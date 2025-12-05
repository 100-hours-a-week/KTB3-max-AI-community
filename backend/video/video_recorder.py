
import cv2
import os
import time
from datetime import datetime #로컬 서버 시간 측정
from backend.make_db import mouse_log #`mouse_log.py` 모듈 import


# 영상 저장 폴더 생성
VIDEO_DIR = './DB/recorded_videos' #현재 backend 작업공간에 생성
os.makedirs(VIDEO_DIR, exist_ok=True)

#영상 저장 클래스-------------------------------------------------------------------
#포함된 함수는 각 프레임마다 동작한다
class VideoRecorder:
    def __init__(self):
        self.cooldown = 2.0 # 2초 쿨다운 (쥐가 사라져도 2초간 녹화 유지)
        self.path_history = [] # 이동 경로 저장 ([좌상단, 중상단, 우상단, 좌중단, 중앙, 우중단, 좌하단, 중하단, 우하단])
        self.last_zone = "" #이전 프레임의 구역 정보
        self.last_detection_time = 0 #마지막 탐지시간
        self.is_recording = False #녹화 시작 여부 관리 (녹화중이 아닐때에만 녹화 시작)
        self.event_id = None # DB의 해당 이벤트의 ID
        self.start_time = None #탐지 시작시간
        self.filename = "" #녹화 파일 이름
        self.out = None # 생성할 비디오 정보 저장
    
    # 마우스 이동경로 구역 계산 함수
    def get_zone(self, x, y, width, height): #마우스 박스의 중앙좌표와 화면 크기
        """
        화면을 3x3 9분할하여 구역 번호(1~9)를 반환합니다.
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        """
        # X축: 0~1/3(좌), 1/3~2/3(중), 2/3~1(우)
        col = 0
        if x < width / 3: col = 0
        elif x < 2 * width / 3: col = 1
        else: col = 2
        
        # Y축: 0~1/3(상), 1/3~2/3(중), 2/3~1(하)
        row = 0
        if y < height / 3: row = 0
        elif y < 2 * height / 3: row = 1
        else: row = 2
        

        # 구역 번호 매핑
        zone_list = ["좌상단", "중상단", "우상단", "좌중단", "중앙", "우중단", "좌하단", "중하단", "우하단"] #구역 이름 매핑
        zone = row * 3 + col + 1 #숫자 매핑 구역
        real_zone = zone_list[zone - 1]
        return real_zone

    # 프레임 처리 및 녹화 관리 함수
    def process(self, frame, detection_info):
        """
        1. 마우스 탐지 이벤트 감지
        2. 이동 경로 기록
        3. 녹화 시작/종료 관리
        """
        current_time = time.time() #현재 시간
        detected = detection_info['detected'] #탐지 여부
        center = detection_info['center'] #마우스 박스 중앙 좌표
        height, width, _ = frame.shape #영상의 크기

        # 1. 마우스 탐지 이벤트 발생
        if detected:
            self.last_detection_time = current_time #마지막 탐지 시간 갱신

            # 이동 경로 기록
            zone = self.get_zone(center[0], center[1], width, height) #해당 프레임에서 박스의 중앙값과 프레임의 크기 입력
            # 각 프레임마다 계산하므로 동일 구역에 계속 존재한다면 기록 중복이 발생한다
            ## 따라서 구역이 바뀌었을때만 기록한다
            if zone != self.last_zone:
                self.path_history.append(zone) #이동 구역 갱신
                self.last_zone = zone #마지막 구역 갱신
        
            # 2. 녹화 시작 관리
            if not self.is_recording:
                self.is_recording = True #녹화 상태로 전환
                self.start_time = datetime.now() #최초로 현재 시간 기록, 다음 탐지된 프레임에선 해당 로직을 거치지 않는다
                # DB에 이벤트 시작시간 기록하고 이벤트 ID를 반환받는다 
                self.event_id = mouse_log.insert_event(self.start_time) #`database.py`의 insert_event 함수 호출
                # 비디오 파일 생성 준비
                self.filename = f"mouse_{self.start_time.strftime('%Y%m%d_%H%M%S')}.mp4" # 파일 이름
                filepath = os.path.join(VIDEO_DIR, self.filename) # 비디오 저장 파일 경로 지정      

                # [수정됨] 웹 브라우저 호환성을 위해 코덱을 mp4v에서 avc1(H.264)로 변경
                # Mac에서는 기본 지원, Windows 등에서는 openh264 dll 필요할 수 있음
                try:
                    fourcc = cv2.VideoWriter_fourcc(*'avc1')
                    self.out = cv2.VideoWriter(filepath, fourcc, 30.0, (width, height))
                except Exception as e:
                    print(f"AVC1 코덱 설정 실패 (mp4v로 폴백): {e}")
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    self.out = cv2.VideoWriter(filepath, fourcc, 30.0, (width, height))

                print(f"마우스 탐지 이벤트 {self.event_id} 시작, {self.filename} 기록중")
        
        # 3. 쥐가 탐지되었지만 녹화중일 경우
        # 아직 쿨다운 2초가 지나지 않았을때이다
        elif self.is_recording:
            if current_time - self.last_detection_time > self.cooldown: # 현재 시간과 비교하여 마지막 탐지시간과의 차이가 쿨다운 2초를 넘긴 경우
                # 녹화를 종료한다
                self.stop_recording() #아래에 정의된 녹화 종료 함수를 호출한다
            # 쿨다운 시간이 지나지 않았다면 녹화를 계속 진행한다
        
        # 4.녹화중일경우
        if self.is_recording and self.out is not None:
            # 현재 프레임을 비디오에 기록하여 저장한다
            self.out.write(frame)
    
    # 녹화 종료 함수
    def stop_recording(self):
        """
        녹화를 종료하고
        DB 업데이트를 진행한다
        """
        if self.out:
            self.out.release() # 파일 저장 완료
            self.out = None
        self.is_recording = False #녹화 상태 해제
        end_time = datetime.now() #마지막 녹화 시간 기록
        
        # 경로 리스트를 문자열로 변환
        path_str = "->".join(self.path_history)
        # 녹화된 비디오 파일 경로 저장
        video_path_full = os.path.abspath(os.path.join(VIDEO_DIR, self.filename))
        
        # DB 업데이트 (종료 시간, 경로, 파일 위치)
        if self.event_id:
            mouse_log.update_event(self.event_id, end_time, path_str, video_path_full)
            print(f"[End] Event {self.event_id} saved. Path: {path_str}")
        
        # 다음 녹화를 위해 변수 초기화
        self.event_id = None
        self.path_history = []
        self.last_zone = ""