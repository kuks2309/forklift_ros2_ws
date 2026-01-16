#!/usr/bin/env python3
"""
YOLOv8 Segmentation Inference and Result Visualization
Display segmentation results on images using trained model
"""

from ultralytics import YOLO
import cv2
import numpy as np
import os
import argparse
from pathlib import Path
import torch
from pose_estimation import draw_pose_axes, refine_pose_by_quad_perturbation


def check_device(device_arg):
    """Check GPU/CPU device"""
    if torch.cuda.is_available():
        print(f"CUDA available: {torch.cuda.get_device_name(0)}")
        if device_arg == 'auto':
            return 0
        return device_arg
    print("Using CPU")
    return 'cpu'


def get_quadrilateral_from_mask(mask_binary):
    """
    Extract quadrilateral vertices from mask
    Get 4 points using minAreaRect, then separate by Y coordinate into top/bottom

    Returns:
        contour: original contour
        ordered_pts: 4 points in order P1(top-left), P2(top-right), P3(bottom-right), P4(bottom-left)
    """
    contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, None

    # Select largest contour
    contour = max(contours, key=cv2.contourArea)

    # Extract 4 points using minAreaRect
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    pts = box.astype(np.float32)

    # Separate top 2 and bottom 2 by Y coordinate
    sorted_by_y = pts[np.argsort(pts[:, 1])]
    top_pts = sorted_by_y[:2]
    bottom_pts = sorted_by_y[2:]

    # Sort by X
    top_pts = top_pts[np.argsort(top_pts[:, 0])]
    bottom_pts = bottom_pts[np.argsort(bottom_pts[:, 0])]

    ordered = np.array([
        top_pts[0],      # P1: top-left
        top_pts[1],      # P2: top-right
        bottom_pts[1],   # P3: bottom-right
        bottom_pts[0]    # P4: bottom-left
    ], dtype=np.int32)

    return contour, ordered


def draw_segmentation(img, result, show_labels=True):
    """Draw segmentation result on image"""
    h, w = img.shape[:2]
    vis_img = img.copy()
    overlay = img.copy()

    # Color settings
    fill_color = (0, 255, 0)  # green
    line_color = (0, 200, 0)
    point_colors = [(0, 0, 255), (0, 128, 255), (0, 255, 255), (255, 255, 0)]  # P1~P4 (BGR)

    if result.masks is None:
        return vis_img

    masks = result.masks.data.cpu().numpy()
    boxes = result.boxes

    for i, (mask, box) in enumerate(zip(masks, boxes)):
        # Resize mask
        mask_resized = cv2.resize(mask, (w, h))
        mask_binary = (mask_resized > 0.5).astype(np.uint8)

        # Fill mask area
        colored_mask = np.zeros_like(img)
        colored_mask[mask_binary == 1] = fill_color
        overlay = cv2.addWeighted(overlay, 1, colored_mask, 0.4, 0)

        # Extract quadrilateral vertices (minAreaRect based)
        contour, quad_pts = get_quadrilateral_from_mask(mask_binary)

        if contour is not None:
            # Draw mask outline
            cv2.drawContours(vis_img, [contour], -1, line_color, 2)

            # Draw quadrilateral
            if quad_pts is not None:
                cv2.polylines(vis_img, [quad_pts], True, (255, 0, 255), 3)  # magenta quadrilateral

                # Mark vertices (P1, P2, P3, P4)
                for j, pt in enumerate(quad_pts):
                    x, y = pt
                    color = point_colors[j % len(point_colors)]
                    cv2.circle(vis_img, (x, y), 10, color, -1)
                    cv2.circle(vis_img, (x, y), 10, (255, 255, 255), 2)
                    # Display P number next to point
                    cv2.putText(vis_img, f'P{j+1}', (x+12, y+5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
                    cv2.putText(vis_img, f'P{j+1}', (x+12, y+5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                # Display coordinate info (top-left)
                if show_labels:
                    coord_y = 30
                    for j, pt in enumerate(quad_pts):
                        x, y = pt
                        color = point_colors[j % len(point_colors)]
                        coord_text = f'P{j+1}: [{x}, {y}]'
                        cv2.putText(vis_img, coord_text, (10, coord_y),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
                        cv2.putText(vis_img, coord_text, (10, coord_y),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        coord_y += 25

                # Fixed pallet size: 1200x1000x150mm pallet, front face (forklift entry side)
                # Width: 1200mm, Height: 150mm
                pallet_w = 1200.0
                pallet_h = 150.0

                # 6DoF pose estimation using quad perturbation refinement
                pose_pnp = refine_pose_by_quad_perturbation(quad_pts, (w, h), pallet_width=pallet_w, pallet_height=pallet_h)

                if pose_pnp['success']:
                    # Draw 3D coordinate axes using refined pose
                    vis_img = draw_pose_axes(vis_img, quad_pts, pose_pnp)

                    # Draw projected quad (cyan) to show fit quality
                    if 'projected_quad' in pose_pnp and pose_pnp['projected_quad'] is not None:
                        proj_pts = pose_pnp['projected_quad'].astype(np.int32)
                        cv2.polylines(vis_img, [proj_pts], True, (255, 255, 0), 1)

                    # Pose info text (top-right)
                    if show_labels:
                        pose_lines = [
                            ("Roll:", f"{pose_pnp['roll']:.1f} deg", (0, 0, 255)),    # X-axis - red
                            ("Pitch:", f"{pose_pnp['pitch']:.1f} deg", (0, 255, 0)),  # Y-axis - green
                            ("Yaw:", f"{pose_pnp['yaw']:.1f} deg", (255, 0, 0)),      # Z-axis - blue
                            ("Z:", f"{pose_pnp['tvec'][2]/1000:.2f}m", (255, 255, 255))  # distance
                        ]
                        text_x = w - 180
                        for k, (label, value, color) in enumerate(pose_lines):
                            y_pos = 30 + k * 25
                            text = f"{label} {value}"
                            cv2.putText(vis_img, text, (text_x, y_pos),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3)
                            cv2.putText(vis_img, text, (text_x, y_pos),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1)

        # Display class label and confidence
        if show_labels:
            conf_score = box.conf[0].item()
            label = f"Pallet {conf_score:.2f}"
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(vis_img, (x1, y1-th-10), (x1+tw+10, y1), (0, 150, 0), -1)
            cv2.putText(vis_img, label, (x1+5, y1-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Composite overlay
    vis_img = cv2.addWeighted(overlay, 0.4, vis_img, 0.6, 0)
    return vis_img


def run_inference(args):
    """Run inference"""
    device = check_device(args.device)

    # Load model
    print(f"Loading model: {args.weights}")
    model = YOLO(args.weights)

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process input path
    source_path = Path(args.source)

    if source_path.is_file():
        image_paths = [source_path]
    elif source_path.is_dir():
        image_paths = sorted(
            list(source_path.glob('*.png')) +
            list(source_path.glob('*.jpg')) +
            list(source_path.glob('*.jpeg'))
        )
    else:
        print(f"Invalid path: {args.source}")
        return

    print(f"Images to process: {len(image_paths)}")
    print(f"Confidence threshold: {args.conf}")
    if args.show:
        print("Display: ON (Left/Right=prev/next, S=save, ESC=exit)")
    if args.save:
        print(f"Save results: {output_dir}")
    print("")

    if args.show:
        # Interactive mode: navigate with arrow keys
        idx = 0
        vis_images = {}  # cache

        while True:
            img_path = image_paths[idx]
            print(f"\r[{idx+1}/{len(image_paths)}] {img_path.name}", end="          ")

            # Check cache
            if idx not in vis_images:
                img = cv2.imread(str(img_path))
                if img is not None:
                    results = model.predict(source=str(img_path), conf=args.conf, device=device, verbose=False)
                    vis_images[idx] = draw_segmentation(img, results[0], show_labels=not args.no_labels)
                else:
                    vis_images[idx] = None

            vis_img = vis_images[idx]
            if vis_img is not None:
                cv2.imshow("Segmentation Result", vis_img)

            key = cv2.waitKey(0) & 0xFF

            if key == 27:  # ESC - exit
                break
            elif key == 83 or key == ord('d'):  # Right or D - next
                idx = (idx + 1) % len(image_paths)
            elif key == 81 or key == ord('a'):  # Left or A - previous
                idx = (idx - 1) % len(image_paths)
            elif key == ord('s'):  # S - save
                if vis_img is not None:
                    output_path = output_dir / f"result_{img_path.name}"
                    cv2.imwrite(str(output_path), vis_img)
                    print(f" -> Saved: {output_path}", end="")

        cv2.destroyAllWindows()
        print("\nDone!")
    else:
        # Batch mode: save all
        for i, img_path in enumerate(image_paths):
            print(f"[{i+1}/{len(image_paths)}] {img_path.name}...", end=" ")

            img = cv2.imread(str(img_path))
            if img is None:
                print("Failed")
                continue

            results = model.predict(source=str(img_path), conf=args.conf, device=device, verbose=False)
            vis_img = draw_segmentation(img, results[0], show_labels=not args.no_labels)

            if args.save:
                output_path = output_dir / f"result_{img_path.name}"
                cv2.imwrite(str(output_path), vis_img)
                print("Saved")
            else:
                print("Done")

        print("\nDone!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YOLOv8 Segmentation Inference')
    parser.add_argument('--weights', type=str, required=True,
                        help='Trained model path (best.pt)')
    parser.add_argument('--source', type=str, required=True,
                        help='Input image or folder path')
    parser.add_argument('--output', type=str, default='./results',
                        help='Result save path')
    parser.add_argument('--conf', type=float, default=0.5,
                        help='Confidence threshold (default: 0.5)')
    parser.add_argument('--device', type=str, default='auto',
                        help='Device (auto, 0, cpu)')
    parser.add_argument('--no-labels', action='store_true',
                        help='Hide labels')
    parser.add_argument('--show', action='store_true',
                        help='Display results on screen')
    parser.add_argument('--save', action='store_true',
                        help='Save result files')

    args = parser.parse_args()
    run_inference(args)
