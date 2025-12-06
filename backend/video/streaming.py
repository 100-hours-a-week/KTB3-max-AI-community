# streaming.py
# 영상 스트리밍 함수

import cv2
from backend.yolo import ObjectDetector # 분리한 이미지 처리 모듈 import
from .video_recorder import VideoRecorder # VideoRecorder 클래스 import

# 전역 Detector 객체 생성, 서버가 시작될 때 한번만 AI모델이 로드됨
detector = ObjectDetector()
# 전역 레코더 인스턴스 생성
recorder = VideoRecorder()

#영상 스트리밍 함수-------------------------------------------------------------------
#이미지 프레임을 무한 반복 출력한다
def generate_frames(cam_index: int): #카메라 인덱스를 url을 통해 입력받는다
    # 카메라 연결
    cap = cv2.VideoCapture(cam_index)
    # 카메라가 실제로 열렸는지 확인
    if not cap.isOpened(): #카메라 연결 실패 시
        return #스트리밍 중단

    while True: #무한 반복, 영상을 끊임없이 송출
        success, frame = cap.read() #이미지 프레임 한장 불러오기
        if not success: #프레임 추출 실패 시 
            break #종료
        
        # Detector 모듈을 통해 프레임 가공
        processed_frame, info = detector.process_frame(frame)

        # 가공된 프레임을 녹화하여 저장
        recorder.process(processed_frame, info)


        # 가공한 프레임을 JPG 포멧으로 인코딩하여 압축
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        if not ret: #인코딩 실패 시
            continue #건너뛴다
        
        #제네레이터를 이용하여 MJPEG 포멧으로 프레임 전송
        ## MJPEG : Motion JPEG, 사진을 연속 출력하여 동영상처럼 보이게 하는 포멧
        #데이터를 한번에 모두 보내지 않고 조금씩 나누어 보낸다
        yield (b'--frame\r\n' #프레임 구분 (MJPEG 포멧 규격)
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    #서버 종료 시 카메라 해제
    cap.release()
    #이때 스트리밍이 종료가 되었어도 녹화가 진행중이면 이것도 자동 종료되게 하여 안정성을 높인다
    if recorder.is_recording:
        recorder.stop_recording()