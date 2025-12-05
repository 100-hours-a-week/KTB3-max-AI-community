import sqlite3
import os
from datetime import datetime

# DB 파일 저장 경로
DB_DIR = "./DB"
os.makedirs(DB_DIR, exist_ok=True)

# 댓글용 별도 DB 파일
DB_PATH = os.path.join(DB_DIR, "comment.db")

def init_db():
    """
    댓글(comments) 테이블 생성 (nickname 컬럼 추가됨)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 기존 DB파일이 있을 경우 호환성 문제가 생길 수 있으므로
    # nickname 컬럼이 포함된 새로운 스키마로 생성합니다.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            nickname TEXT NOT NULL,  -- [추가] 닉네임
            content TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"{DB_PATH}에 댓글 DB 로드 완료")

def insert_comment(post_id, nickname, content, password):
    """
    댓글 저장 (nickname 인자 추가)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO comments (post_id, nickname, content, password, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (post_id, nickname, content, password, created_at))
    
    conn.commit()
    conn.close()

def get_comments_by_post_id(post_id):
    """
    특정 게시글의 댓글 목록 조회
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM comments WHERE post_id = ? ORDER BY id ASC', (post_id,))
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in rows]

def delete_comment(comment_id, password):
    """
    비밀번호 일치 시 댓글 삭제
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT password FROM comments WHERE id = ?', (comment_id,))
    result = cursor.fetchone()

    if result and result[0] == password:
        cursor.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

if __name__ == "__main__":
    init_db()
else:
    init_db()