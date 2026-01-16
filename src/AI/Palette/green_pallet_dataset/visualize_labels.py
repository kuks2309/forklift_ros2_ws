#!/usr/bin/env python3
"""
Green Pallet Dataset Label Visualizer
RGB 이미지에 YOLO Segmentation 라벨을 시각화하는 스크립트
"""

import cv2
import numpy as np
import os
from pathlib import Path
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


def load_yolo_polygon(label_path, img_width, img_height):
    """YOLO 폴리곤 라벨 파일 로드 및 픽셀 좌표로 변환"""
    polygons = []

    if not os.path.exists(label_path):
        return polygons

    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue

            class_id = int(parts[0])
            coords = list(map(float, parts[1:]))

            # 정규화된 좌표를 픽셀 좌표로 변환
            points = []
            for i in range(0, len(coords), 2):
                x = int(coords[i] * img_width)
                y = int(coords[i + 1] * img_height)
                points.append([x, y])

            polygons.append({
                'class_id': class_id,
                'points': np.array(points, dtype=np.int32)
            })

    return polygons


def extract_rgb_index(label_filename):
    """라벨 파일명에서 RGB 이미지 인덱스 추출
    예: '0287fa2d-19.txt' -> '19'
    """
    stem = Path(label_filename).stem
    match = re.search(r'-(\d+)$', stem)
    if match:
        return match.group(1)
    return None


def build_label_mapping(labels_dir):
    """라벨 파일과 RGB 이미지 인덱스 매핑 생성"""
    mapping = {}
    labels_path = Path(labels_dir)

    if not labels_path.exists():
        return mapping

    for label_file in labels_path.glob('*.txt'):
        rgb_idx = extract_rgb_index(label_file.name)
        if rgb_idx:
            mapping[rgb_idx] = label_file

    return mapping


def draw_visualization_cv2(img, polygons):
    """OpenCV로 이미지에 폴리곤 시각화"""
    vis_img = img.copy()
    overlay = vis_img.copy()

    fill_color = (0, 255, 0)  # 녹색 채우기
    line_color = (0, 200, 0)  # 진한 녹색 테두리
    point_colors = [(0, 0, 255), (0, 128, 255), (0, 255, 255), (255, 255, 0)]  # P1, P2, P3, P4 색상 (BGR)

    for poly in polygons:
        points = poly['points']
        cv2.fillPoly(overlay, [points], fill_color)
        cv2.polylines(vis_img, [points], True, line_color, 2)

        # 꼭지점 표시 (P1, P2, P3, P4 번호 포함)
        for i, point in enumerate(points):
            color = point_colors[i % len(point_colors)]
            cv2.circle(vis_img, tuple(point), 10, color, -1)
            cv2.circle(vis_img, tuple(point), 10, (255, 255, 255), 2)
            cv2.putText(vis_img, f'P{i+1}', (point[0]+12, point[1]+5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(vis_img, f'P{i+1}', (point[0]+12, point[1]+5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

    cv2.addWeighted(overlay, 0.3, vis_img, 0.7, 0, vis_img)
    return vis_img


def visualize_rgb_with_labels(dataset_dir, split='train', output_dir=None):
    """RGB 이미지에 라벨 시각화 (matplotlib 사용)"""
    base_dir = Path(dataset_dir)
    rgb_dir = base_dir / 'rgb'
    labels_dir = base_dir / 'green_pallet_yolo_label' / 'labels' / split

    if not rgb_dir.exists():
        print(f"RGB 디렉토리가 없습니다: {rgb_dir}")
        return

    label_mapping = build_label_mapping(labels_dir)

    if not label_mapping:
        print(f"라벨 파일이 없습니다: {labels_dir}")
        return

    rgb_indices = sorted(label_mapping.keys(), key=lambda x: int(x))

    print(f"\n=== RGB 이미지 라벨 시각화 ({split}) ===")
    print(f"라벨이 있는 이미지: {len(rgb_indices)}개")
    print("조작: 좌/우 화살표 또는 A/D 키로 이동, Q로 종료\n")

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    idx = [0]  # mutable for callback

    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    plt.subplots_adjust(bottom=0.15)

    def update_display():
        ax.clear()
        rgb_idx = rgb_indices[idx[0]]
        rgb_path = rgb_dir / f"{rgb_idx}.png"
        label_path = label_mapping[rgb_idx]

        if not rgb_path.exists():
            ax.set_title(f"RGB 이미지 없음: {rgb_idx}.png")
            fig.canvas.draw()
            return

        img = cv2.imread(str(rgb_path))
        if img is None:
            ax.set_title(f"이미지 로드 실패: {rgb_idx}.png")
            fig.canvas.draw()
            return

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img.shape[:2]
        polygons = load_yolo_polygon(str(label_path), w, h)

        ax.imshow(img_rgb)

        # 폴리곤 그리기
        patches = []
        point_colors = ['red', 'orange', 'yellow', 'cyan']  # P1, P2, P3, P4 색상
        for poly in polygons:
            points = poly['points']
            polygon = Polygon(points, closed=True)
            patches.append(polygon)

            # 꼭지점 표시 (P1, P2, P3, P4 번호 포함)
            for i, pt in enumerate(points):
                color = point_colors[i % len(point_colors)]
                ax.scatter(pt[0], pt[1], c=color, s=100, zorder=5, edgecolors='white', linewidths=1)
                ax.annotate(f'P{i+1}', (pt[0]+10, pt[1]-10), fontsize=10, fontweight='bold',
                           color='white', bbox=dict(boxstyle='round,pad=0.2', facecolor=color, alpha=0.8))

            # 테두리 그리기
            points_closed = np.vstack([points, points[0]])
            ax.plot(points_closed[:, 0], points_closed[:, 1], 'g-', linewidth=2)

        if patches:
            p = PatchCollection(patches, alpha=0.3, facecolors='lime', edgecolors='green')
            ax.add_collection(p)

        title = f"[{idx[0] + 1}/{len(rgb_indices)}] RGB: {rgb_idx}.png | Pallets: {len(polygons)}"
        ax.set_title(title, fontsize=12)
        ax.set_xlabel(f"Label: {label_path.name}", fontsize=10)
        ax.axis('off')

        fig.canvas.draw()

    def on_key(event):
        if event.key in ['right', 'd', 'n']:
            idx[0] = (idx[0] + 1) % len(rgb_indices)
            update_display()
        elif event.key in ['left', 'a', 'p']:
            idx[0] = (idx[0] - 1) % len(rgb_indices)
            update_display()
        elif event.key == 's':
            if output_dir:
                rgb_idx = rgb_indices[idx[0]]
                save_path = os.path.join(output_dir, f"vis_rgb_{rgb_idx}.png")
                fig.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"저장됨: {save_path}")
        elif event.key == 'q':
            plt.close(fig)

    fig.canvas.mpl_connect('key_press_event', on_key)

    update_display()
    plt.show()


def save_all_rgb_visualizations(dataset_dir, output_dir, split='train'):
    """모든 RGB 이미지 시각화 결과 저장"""
    base_dir = Path(dataset_dir)
    rgb_dir = base_dir / 'rgb'
    labels_dir = base_dir / 'green_pallet_yolo_label' / 'labels' / split

    os.makedirs(output_dir, exist_ok=True)

    label_mapping = build_label_mapping(labels_dir)
    rgb_indices = sorted(label_mapping.keys(), key=lambda x: int(x))

    print(f"\n=== RGB 이미지 시각화 저장 ({split}) ===")
    print(f"총 {len(rgb_indices)}개 이미지 처리 중...")

    for i, rgb_idx in enumerate(rgb_indices):
        rgb_path = rgb_dir / f"{rgb_idx}.png"
        label_path = label_mapping[rgb_idx]

        if not rgb_path.exists():
            print(f"[{i + 1}/{len(rgb_indices)}] 건너뜀 (RGB 없음): {rgb_idx}.png")
            continue

        img = cv2.imread(str(rgb_path))
        if img is None:
            continue

        h, w = img.shape[:2]
        polygons = load_yolo_polygon(str(label_path), w, h)

        vis_img = draw_visualization_cv2(img, polygons)

        # 정보 표시
        info_text = f"RGB: {rgb_idx}.png | Pallets: {len(polygons)}"
        cv2.putText(vis_img, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (255, 255, 255), 2)
        cv2.putText(vis_img, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 200, 0), 1)

        output_path = os.path.join(output_dir, f"vis_rgb_{rgb_idx}.png")
        cv2.imwrite(output_path, vis_img)
        print(f"[{i + 1}/{len(rgb_indices)}] 저장: {output_path}")

    print(f"\n완료! 저장 위치: {output_dir}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Green Pallet RGB Label Visualizer')
    parser.add_argument('--mode', type=str, default='browse',
                        choices=['browse', 'save_all'],
                        help='실행 모드: browse(탐색), save_all(전체저장)')
    parser.add_argument('--split', type=str, default='train',
                        choices=['train', 'val'],
                        help='데이터셋 분할: train 또는 val')
    parser.add_argument('--output', type=str, default='./visualized',
                        help='시각화 결과 저장 디렉토리')

    args = parser.parse_args()

    dataset_dir = os.path.dirname(os.path.abspath(__file__))

    if args.mode == 'browse':
        visualize_rgb_with_labels(dataset_dir, split=args.split, output_dir=args.output)

    elif args.mode == 'save_all':
        output_dir = os.path.join(dataset_dir, args.output, args.split)
        save_all_rgb_visualizations(dataset_dir, output_dir, split=args.split)
