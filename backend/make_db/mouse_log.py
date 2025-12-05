import sqlite3
import pandas as pd
import os

# DB파일 저장 경로
DB_DIR = "./DB" #루트폴더(community)
os.makedirs(DB_DIR, exist_ok=True)  # 폴더만 생성

DB_PATH = os.path.join(DB_DIR, "mouse_log.db")  # 파일 경로

def init_db():
    """
    'detections' DB테이블 생성
    """
    #DB 연결
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    #테이블 생성 SQL문
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT,
            end_time TEXT,
            path_log TEXT,
            video_path TEXT
        )
    ''')
    
    #DB연결 해제
    conn.commit()
    conn.close()
    print(f"{DB_PATH}에 DB생성 및 로드 완료")

#마우스 처음 탐지
def insert_event(start_time) -> int: #현재 시간을 입력받음
    """
    마우스를 처음 탐지했을 때 이벤트 생성
    DB에 부여된 'ID'를 반환
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    #datetime 현재시간 객체를 문자열로 변환
    start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    #이벤트의 시작 시점에선 `end_time`, `path_log`, `video_path`가 비어있음
    cursor.execute('''
        INSERT INTO detections (start_time, end_time, path_log, video_path)
        VALUES (?, ?, ?, ?)
    ''', (start_str, None, "", ""))
    event_id = cursor.lastrowid #생성된 행의 ID를 가져온다
    conn.commit()
    conn.close()
    return event_id

#마우스 탐지 종료
def update_event(event_id: int, end_time: str, path_log: str, video_path: str): #이 시점에는 동영상까지 저장되어있음
    """
    마우스 탐지가 종료되었을 때 이벤트 업데이트
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        UPDATE detections
        SET end_time = ?, path_log = ?, video_path = ?
        WHERE id = ?
    ''', (end_str, path_log, video_path, event_id))

    conn.commit()
    conn.close()

def get_recent_events(limit: int = 5) -> pd.DataFrame:
    """
    최근 탐지 이벤트들을 DataFrame 형식으로 반환
    """
    conn = sqlite3.connect(DB_PATH)
    query = f'''
        SELECT * FROM detections
        ORDER BY id DESC
        LIMIT {limit}
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

#파일 실행 또는 import시 DB 생성 및 초기화 실행
if __name__ == "__main__":
    init_db() #DB 생성 및 초기화
else:
    init_db()
