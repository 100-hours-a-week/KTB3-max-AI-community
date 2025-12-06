# `./backend/video`
카메라를 통한 영상 스트리밍과 이미지 프레임의 영상 파일 저장 함수

## I. `video_recorder.py`
- `VideoRecorder` 클래스는 영상 파일 저장 관련 메서드를 제공한다.
- 생성된 영상 파일은 `./DB/recorded_videos`에 저장된다.
- 모듈 호출 : 
```python
from .video_recorder import VideoRecorder  #같은 공간내의 `streaming.py`가 사용
```
- 관련 파일 : `./backend/video/streaming.py`, `./backend/make_db/mouse_log.py`

### I-1. `VideoRecorder.__init__()`
- 2초 쿨다운 (마지막으로 탐지된지 2초가 지나면 해당 탐지 이벤트 종료)
- `mouse`의 이동 경로 저장 ([좌상단, 중상단, 우상단, 좌중단, 중앙, 우중단, 좌하단, 중하단, 우하단])
- 녹화 시작 여부 관리

### I-2. `VideoRecorder.get_zone()`
- 입력 : `x`, `y` (`mouse` 탐지 박스 중앙좌표), `width`, `height` (이미지 프레임의 크기)
- 화면을 9분할로 나눈 다음 입력받은 값을 이용해 `mouse`의 이동 경로를 탐지한다.
- 출력 : `real_zone` (구역 이름)

### I-3. `VideoRecorder.process()`
- 입력 : `ObjectDetector.process_frame()`의 출력값
- `./backend/video/streaming.py`의 `generate_frames()`에 의해 매 이미지 프레임마다 한번씩 작동
- 현재 시간 기록
- `mouse` 탐지 여부를 받고, 탐지되었으면 `mouse` 탐지 이벤트 발생시킴  
  1.  현재 시간을 마지막 탐지 시간으로 갱신
  2.  `VideoRecorder.get_zone()`으로부터 `mouse`의 현재 존재 구역 기록
  3.  가장 최근의 이동구역과 비교하여 달라졌을 경우에만 구역 기록 갱신 (기록 중복 차단)
  4.  녹화중이 아니였으면 녹화 상태로 전환  
  최초로 현재 시간을 녹화 시작 시간으로 기록  
  `mouse_log` 모듈의 `insert_event()` 함수를 통해 시작 시간을 입력하고 `mouse_log` DB로부터 `id`을 반환 받음  
  녹화 파일의 이름을 `mouse_{녹화 시작 시간}`으로 지정  
  웹 브라우저 재생을 위해 코덱을 `avc1(H.264)`로 변환
- 해당 프레임에 `mouse`가 탐지되지 않았지만 녹화 상태일 경우,  
  현재 시간이 녹화 시작시간과 쿨다운 2초 이상 차이가 날 경우 녹화 종료 함수 실행 (`VideoRecorder.stop_recording()`)
- `mouse`의 탐지 여부에 상관없이 영상이 녹화중일 경우 현재 프레임을 기록하여 저장

### I-4. `VideoRecorder.stop_recording()`
- 영상 녹화 종료 함수
- 녹화된 영상의 녹화 종료 시간, `mouse` 이동 경로, 영상 저장 경로를 `mouse_log` DB에 업데이트

## II. `streaming.py`
- 연결된 카메라 장치로부터 영상을 입력받고, 각 이미지프레임을 가공 및 녹화 저장한다.
- 모듈 호출 : 
```python
from backend.video import generate_frames
```
- 관련 파일 : `./backend/server.py`, `./backend/yolo/detector.py`, `./backend/video/video_recorder.py`

## II-1. `generate_frames()`
- 입력 : 카메라 인덱스 (연결된 카메라의 종류)
- 카메라가 연결되면 스트리밍 시작 (모든 이미지 프레임 무한 송출)
- 각각의 이미지 프레임에 대해 `ObjectDetector.process_frame()`으로 이미지 가공 진행
- 가공된 이미지 프레임을 `VideoRecorder.process()`로 영상 녹화 저장
- 가공된 이미지 프레임을 `JPG` 포멧으로 인코딩하여 압축
- 제네레이터를 이용하여 `MJPEG` 포멧으로 규격 변환 후 프레임 전송
- 스트리밍이 종료가 되어있어도 녹화가 진행중이면 `VideoRecorder.stop_recording()`로 녹화 종료
- 출력 : `MJPEG`포멧의 프레임