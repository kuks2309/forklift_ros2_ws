#!/bin/bash
# Green Pallet YOLOv8 Segmentation Training Script
# 사용법: ./train.sh [옵션]

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 기본 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="/home/amap/yolov8/yolov8-env"

# 기본 학습 파라미터
MODEL="yolov8n-seg.pt"
EPOCHS=3000
BATCH=16
IMGSZ=640
PATIENCE=50
SAVE_PERIOD=100
NAME="green_pallet"
DEVICE="auto"

# 도움말 출력
show_help() {
    echo -e "${GREEN}Green Pallet YOLOv8 Segmentation Training${NC}"
    echo ""
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  -m, --model       모델 (기본: yolov8n-seg.pt)"
    echo "                    선택: yolov8n-seg.pt, yolov8s-seg.pt, yolov8m-seg.pt, yolov8l-seg.pt"
    echo "  -e, --epochs      에폭 수 (기본: 3000)"
    echo "  -b, --batch       배치 크기 (기본: 16)"
    echo "  -i, --imgsz       이미지 크기 (기본: 640)"
    echo "  -p, --patience    조기종료 patience (기본: 50, 0=비활성화)"
    echo "  -s, --save        체크포인트 저장 주기 (기본: 100)"
    echo "  -n, --name        실험 이름 (기본: green_pallet)"
    echo "  -d, --device      디바이스 (기본: auto)"
    echo "  -h, --help        도움말 출력"
    echo ""
    echo "예시:"
    echo "  $0                              # 기본 설정으로 학습"
    echo "  $0 -m yolov8l-seg.pt -e 5000    # 큰 모델로 5000 에폭 학습"
    echo "  $0 -p 0                         # 조기종료 비활성화"
    echo ""
}

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -e|--epochs)
            EPOCHS="$2"
            shift 2
            ;;
        -b|--batch)
            BATCH="$2"
            shift 2
            ;;
        -i|--imgsz)
            IMGSZ="$2"
            shift 2
            ;;
        -p|--patience)
            PATIENCE="$2"
            shift 2
            ;;
        -s|--save)
            SAVE_PERIOD="$2"
            shift 2
            ;;
        -n|--name)
            NAME="$2"
            shift 2
            ;;
        -d|--device)
            DEVICE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}알 수 없는 옵션: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 가상환경 확인
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}오류: 가상환경을 찾을 수 없습니다: $VENV_PATH${NC}"
    exit 1
fi

# 학습 시작
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Green Pallet Segmentation Training${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}학습 설정:${NC}"
echo "  모델: $MODEL"
echo "  에폭: $EPOCHS"
echo "  배치 크기: $BATCH"
echo "  이미지 크기: $IMGSZ"
echo "  조기종료 patience: $PATIENCE"
echo "  저장 주기: $SAVE_PERIOD 에폭"
echo "  실험 이름: $NAME"
echo "  디바이스: $DEVICE"
echo ""
echo -e "${YELLOW}가상환경 활성화 중...${NC}"

# 가상환경 활성화 및 학습 실행
source "$VENV_PATH/bin/activate"

echo -e "${GREEN}학습 시작!${NC}"
echo ""

cd "$SCRIPT_DIR"
python train.py train \
    --model "$MODEL" \
    --epochs "$EPOCHS" \
    --batch "$BATCH" \
    --imgsz "$IMGSZ" \
    --patience "$PATIENCE" \
    --save_period "$SAVE_PERIOD" \
    --name "$NAME" \
    --device "$DEVICE"

# 종료 상태 확인
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  학습이 완료되었습니다!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  학습 중 오류가 발생했습니다.${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
