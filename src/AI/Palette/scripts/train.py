#!/usr/bin/env python3
"""
Green Pallet YOLOv8 Segmentation Training Script
"""

from ultralytics import YOLO
import torch
import os
import argparse


def check_device(device_arg):
    """GPU/CPU 장치 확인 및 설정"""
    print(f"PyTorch 버전: {torch.__version__}")
    print(f"CUDA 사용 가능: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"CUDA 장치 수: {torch.cuda.device_count()}")
        print(f"현재 CUDA 장치: {torch.cuda.current_device()}")
        print(f"CUDA 장치 이름: {torch.cuda.get_device_name(0)}")
        if device_arg == 'auto':
            return 0  # GPU 사용
        return device_arg
    else:
        print("GPU를 찾을 수 없습니다. CPU를 사용합니다.")
        return 'cpu'


def train(args):
    """YOLOv8 Segmentation 학습 실행"""

    # 장치 확인
    device = check_device(args.device)
    print(f"\n사용 장치: {device}")
    print("="*50)

    # 데이터셋 경로
    data_yaml = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.yaml')

    # 모델 로드 (pretrained segmentation model)
    model = YOLO(args.model)

    # 학습 실행
    results = model.train(
        data=data_yaml,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        workers=args.workers,
        project=args.project,
        name=args.name,
        exist_ok=True,
        pretrained=True,
        optimizer='auto',
        verbose=True,
        seed=42,
        deterministic=True,
        # Early Stopping 설정
        patience=args.patience,  # N 에폭 동안 개선 없으면 조기 종료 (0=비활성화)
        save=True,
        save_period=args.save_period,  # N 에폭마다 체크포인트 저장
        val=True,
        plots=True,
        task='segment',  # 세그멘테이션 작업 지정
    )

    # 학습된 모델로 검증
    model.val()

    print("\n" + "="*50)
    print("학습 완료!")
    print(f"결과 저장 위치: {results.save_dir}")
    print(f"Best 모델: {results.save_dir}/weights/best.pt")
    print(f"Last 모델: {results.save_dir}/weights/last.pt")
    print("="*50)

    return results


def validate(args):
    """학습된 모델 검증"""
    device = check_device(args.device)
    model = YOLO(args.weights)
    data_yaml = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.yaml')

    results = model.val(
        data=data_yaml,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
    )

    return results


def predict(args):
    """이미지 예측 테스트"""
    device = check_device(args.device)
    model = YOLO(args.weights)

    results = model.predict(
        source=args.source,
        imgsz=args.imgsz,
        conf=args.conf,
        device=device,
        save=True,
        save_txt=True,
        project=args.project,
        name='predict',
        exist_ok=True,
    )

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Green Pallet YOLOv8 Segmentation')
    subparsers = parser.add_subparsers(dest='mode', help='실행 모드')

    # Train parser
    train_parser = subparsers.add_parser('train', help='모델 학습')
    train_parser.add_argument('--model', type=str, default='yolov8n-seg.pt',
                              help='기본 모델 (yolov8n-seg.pt, yolov8s-seg.pt, yolov8m-seg.pt, yolov8l-seg.pt)')
    train_parser.add_argument('--epochs', type=int, default=100, help='학습 에폭 수')
    train_parser.add_argument('--imgsz', type=int, default=640, help='입력 이미지 크기')
    train_parser.add_argument('--batch', type=int, default=16, help='배치 크기')
    train_parser.add_argument('--device', type=str, default='auto', help='학습 디바이스 (auto, 0, 1, cpu)')
    train_parser.add_argument('--workers', type=int, default=8, help='데이터 로더 워커 수')
    train_parser.add_argument('--project', type=str, default='./runs/segment', help='결과 저장 경로')
    train_parser.add_argument('--name', type=str, default='green_pallet', help='실험 이름')
    train_parser.add_argument('--patience', type=int, default=20,
                              help='조기종료 patience (N 에폭 동안 개선 없으면 종료, 0=비활성화)')
    train_parser.add_argument('--save_period', type=int, default=10, help='체크포인트 저장 주기 (에폭)')

    # Validate parser
    val_parser = subparsers.add_parser('val', help='모델 검증')
    val_parser.add_argument('--weights', type=str, required=True, help='학습된 모델 경로')
    val_parser.add_argument('--imgsz', type=int, default=640, help='입력 이미지 크기')
    val_parser.add_argument('--batch', type=int, default=16, help='배치 크기')
    val_parser.add_argument('--device', type=str, default='auto', help='디바이스')

    # Predict parser
    pred_parser = subparsers.add_parser('predict', help='이미지 예측')
    pred_parser.add_argument('--weights', type=str, required=True, help='학습된 모델 경로')
    pred_parser.add_argument('--source', type=str, required=True, help='입력 이미지/폴더 경로')
    pred_parser.add_argument('--imgsz', type=int, default=640, help='입력 이미지 크기')
    pred_parser.add_argument('--conf', type=float, default=0.5, help='신뢰도 임계값')
    pred_parser.add_argument('--device', type=str, default='auto', help='디바이스')
    pred_parser.add_argument('--project', type=str, default='./runs/segment', help='결과 저장 경로')

    args = parser.parse_args()

    if args.mode == 'train':
        train(args)
    elif args.mode == 'val':
        validate(args)
    elif args.mode == 'predict':
        predict(args)
    else:
        parser.print_help()
