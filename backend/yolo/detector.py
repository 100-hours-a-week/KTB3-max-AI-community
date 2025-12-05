# modules/detector.py
import cv2 #OpenCV 라이브러리를 이용하여 이미지의 시각적인 처리를 진행한다
from ultralytics import YOLO #YOLO모델을 불러온다

# 카메라로 받은 이미지를 프레임단위로 분석한다.
# YOLO11n 모델을 사용하여 'mouse' 객체를 탐지하고, 
# 탐지된 객체에 대해 경고 메시지를 표시한다.

class ObjectDetector:
    def __init__(self, model_path="./backend/yolo/yolo11n.pt"): #YOLO모델 다운로드 혹은 로컬파일 로드 경로 지정
        try:
            self.model = YOLO(model_path)
            self.names = self.model.names #모데리 알고 있는 클래스들의 이름을 딕셔너리 형태로 불러온다
            print("Model loaded successfully.")
        except Exception as e: #오류 발생 시
            print(f"Error loading model: {e}")
            self.model = None

    def process_frame(self, frame): # YOLO모델로 프레임 분석
        """
        이미지 프레임을 분석하여 객체 탐지 후 각각의 프레임을 반환
        마우스가 탐지되었을 경우 경고 메시지를 추가

        이때 마우스가 탐지되었는지, 그때의 중심 좌표는 무엇인지 딕셔너리를 추가 반환
        """
        if self.model is None:
            return frame, {"detected": False, "center": None} # 모델 없으면 원본 그대로 반환

        # 프레임 분석
        results = self.model.predict(frame, conf=0.45, verbose=False) #신뢰도 35%, 분석 결과 터미널에 출력하지 않음
        r = results[0] #첫번째 결과만 가져오기
        
        mouse_detected = False #쥐를 탐지했는지 플래그
        center_point = None #마우스 박스의 중심 좌표

        if r.boxes is not None: #탐지된 객체가 있으면 아래 반복문 실행
            for box in r.boxes: #탐지된 각 객체들에 대하여 
                cls_id = int(box.cls[0].item()) #클래스 아이디 추출
                class_name = self.names.get(cls_id, str(cls_id)) #클래스 딕셔너리에서 해당 아이디의 이름을 가져온다, 없으면 그냥 클래스 아이디 반환

                if class_name == 'mouse': #마우스가 탐지된 경우
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist()) #물체의 좌상단, 우하단 위치 좌표를 정수로 가져온다
                    
                    mouse_detected = True #탐지 플래그 세우기

                    # 마우스 박스의 중심좌표 계산
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    center_point = (cx, cy)

                    color = (0, 0, 255) # Red
                    label = f"WARNING: {class_name} detected!" #라벨에 탐지 경고 메세지 출력

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2) #탐지된 객체의 좌표와 색깔로 네모 박스를 두께 2로 그림
                    cv2.putText(frame, label, (x1, y1 - 10),#라벨은 좌상단 좌표 바로 위에 출력
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2) #라벨을 글씨로 작성

        if mouse_detected: #마우스가 탐지된 경우
            cv2.putText(frame, "WARNING: MOUSE DETECTED!", (50, 100), #스트리밍 화면 좌상단에 경고문구 출력
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
        
        #편집된 프레임과 마우스 탐지 여부, 중심 좌표를 딕셔너리로 반환
        return frame, {"detected": mouse_detected, "center": center_point}