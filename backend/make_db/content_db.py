import sqlite3
import os
from datetime import datetime

# DB 파일 저장 경로 (기존 DB 폴더 사용)
DB_DIR = "./DB"
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "content.db") # 게시글용 별도 DB 파일

def init_db():
    """
    게시글(posts) 테이블 생성
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 테이블 생성 SQL
    # video_filename은 mouse_log.db의 파일명과 연결되는 외래키 개념
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            password TEXT NOT NULL,
            content TEXT,
            video_filename TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"{DB_PATH}에 게시판 DB 생성 및 로드 완료")

def insert_post(nickname, password, content, video_filename):
    """
    `posts` DB에 게시글 저장 함수
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO posts (nickname, password, content, video_filename, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (nickname, password, content, video_filename, created_at))
    
    conn.commit()
    conn.close()
    print(f"게시글 저장 완료: {nickname} - {video_filename}")

def get_all_posts():
    """
    모든 게시글을 최신순(id 내림차순)으로 조회
    """
    conn = sqlite3.connect(DB_PATH)
    # 딕셔너리 형태로 가져오기 위해 row_factory 설정
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM posts ORDER BY id DESC')
    rows = cursor.fetchall()
    
    conn.close()
    # sqlite3.Row 객체를 dict로 변환하여 리스트 반환
    return [dict(row) for row in rows]

def delete_post(post_id, password):
    """
    비밀번호가 일치하면 게시글 삭제
    성공 시 True, 실패(비번 불일치 등) 시 False 반환
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 해당 게시글의 비밀번호 조회
    cursor.execute('SELECT password FROM posts WHERE id = ?', (post_id,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        return False # 게시글이 없음

    db_password = result[0]

    # 2. 비밀번호 비교
    if db_password == password:
        cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        return True # 삭제 성공
    else:
        conn.close()
        return False # 비밀번호 불일치
    
    
# 모듈 import 시 DB 초기화
if __name__ == "__main__":
    init_db()
else:
    init_db()