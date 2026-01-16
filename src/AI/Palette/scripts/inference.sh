#!/bin/bash
# YOLOv8 Segmentation 추론 스크립트
# 사용법: ./inference.sh --weights <모델경로> --source <이미지경로>

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 기본 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="/home/amap/yolov8/yolov8-env"

# 기본 파라미터
WEIGHTS=""
SOURCE=""
OUTPUT="./results"
CONF=0.5
DEVICE="auto"
NO_LABELS=""
SHOW="--show"
SAVE=""

# 도움말
show_help() {
    echo -e "${GREEN}YOLOv8 Segmentation 추론${NC}"
    echo ""
    echo "사용법: $0 --weights <모델> --source <이미지>"
    echo ""
    echo "필수 옵션:"
    echo "  -w, --weights     학습된 모델 경로 (best.pt)"
    echo "  -s, --source      입력 이미지 또는 폴더 경로"
    echo ""
    echo "선택 옵션:"
    echo "  -o, --output      결과 저장 경로 (기본: ./results)"
    echo "  -c, --conf        신뢰도 임계값 (기본: 0.5)"
    echo "  -d, --device      디바이스 (기본: auto)"
    echo "  --no-labels       라벨 표시 안함"
    echo "  --save            결과 파일 저장"
    echo "  --no-show         화면 표시 안함 (저장만)"
    echo "  -h, --help        도움말"
    echo ""
    echo "예시:"
    echo "  $0 -w ./runs/segment/green_pallet/weights/best.pt -s ./test_images/"
    echo "  $0 -w best.pt -s image.png -c 0.3"
    echo ""
}

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--weights)
            WEIGHTS="$2"
            shift 2
            ;;
        -s|--source)
            SOURCE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -c|--conf)
            CONF="$2"
            shift 2
            ;;
        -d|--device)
            DEVICE="$2"
            shift 2
            ;;
        --no-labels)
            NO_LABELS="--no-labels"
            shift
            ;;
        --save)
            SAVE="--save"
            shift
            ;;
        --no-show)
            SHOW=""
            shift
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

# 필수 인자 확인
if [ -z "$WEIGHTS" ]; then
    echo -e "${RED}오류: --weights 옵션이 필요합니다${NC}"
    show_help
    exit 1
fi

if [ -z "$SOURCE" ]; then
    echo -e "${RED}오류: --source 옵션이 필요합니다${NC}"
    show_help
    exit 1
fi

# 가상환경 확인
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}오류: 가상환경을 찾을 수 없습니다: $VENV_PATH${NC}"
    exit 1
fi

# 실행
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  YOLOv8 Segmentation 추론${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}설정:${NC}"
echo "  모델: $WEIGHTS"
echo "  입력: $SOURCE"
echo "  출력: $OUTPUT"
echo "  신뢰도: $CONF"
echo "  디바이스: $DEVICE"
echo ""

# 가상환경 활성화
source "$VENV_PATH/bin/activate"

echo -e "${GREEN}추론 시작...${NC}"
echo ""

cd "$SCRIPT_DIR"
python inference.py \
    --weights "$WEIGHTS" \
    --source "$SOURCE" \
    --output "$OUTPUT" \
    --conf "$CONF" \
    --device "$DEVICE" \
    $NO_LABELS $SHOW $SAVE

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  완료! 결과: $OUTPUT${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo ""
    echo -e "${RED}오류가 발생했습니다${NC}"
    exit 1
fi
