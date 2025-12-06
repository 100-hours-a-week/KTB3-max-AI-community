# `./backend/yolo`
영상분석 탐지 객체를 위한 딥러닝 모델과 이를 활용한 이미지 프레임 편집 함수
- 사용 모델 : `YOLO11n` (출처 : ultralytics)

## I. `detector.py`
- 카메라로 받은 영상을 프레임단위로 분석한다. 
- `YOLO11n` 모델을 사용하여 `mouse` 객체를 탐지하고
- 탐지된 객체에 대해 경고 메세지를 표시한다.
- `ObjectDetector` 클래스는 해당 모델을 기반으로 여러 프레임 분석 메서드를 제공한다.
- 모듈 호출 : 
```python
from backend.yolo import ObjectDetector
```
- 관련 파일 : `./backend/yolo/yolo11n.pt`, `./backend/video/streaming.py`

### I-1. `ObjectDetector.__init__()`
- `YOLO11n` 모델을 `ultralytics` 을 통해 다운받거나 로컬 모델의 파일을 사용한다.  
(저장 경로 : `./backend/yolo/yolo11n.pt`)

### I-2. `ObjectDetector.process_frame()`
- 임력 : 이미지 프레임
- `YOLO11n` 모델로 이미지 프레임을 분석 (신뢰도 45%)
- 객체 탐지 결과가 반영된 프레임을 반환
- `mouse`가 탐지된 경우  
  1. 그 여부(`mouse_detected`)와 
  2. 객체 탐지 박스를 프레임에 추가,  
  3. 해당 박스의 중심 좌표(`center_point`)를 딕셔너리로 반환
- 이때 객체 탐지 박스와 화면 좌상단에 빨간 글씨로 `mouse` 탐지 경고 문구 출력
- 출력 : 편집된 이미지 프레임, DICT{`mouse_detected`, `center_point`}

## II. `yolo11n.pt`
`ultralytics`을 통해 다운받은 `YOLO11n` 모델 파일