# server.py
from typing import List, Dict, Any, Union
import cv2
import pandas as pd
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os

import sys
# 프로젝트 루트 경로 추가 - 'backend' 패키지 인식
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from backend.make_db import mouse_log #`mouse_log.py` 모듈 import
from backend.make_db import content_db #`content_db.py` 모듈 import
from backend.make_db import comment_db #`comment_db.py` 모듈 import
from backend.video import generate_frames #`streaming.py` 모듈에서 영상 스트리밍 함수 import


    
#-------------------------------------------------------------------------------------
app = FastAPI() #FastAPI 서버 인스턴스 생성, uvicorn으로 실행

# 영상 저장 디렉토리 설정 및 생성
VIDEO_DIR = "./DB/recorded_videos"
app.mount("/videos", StaticFiles(directory=VIDEO_DIR), name="videos")
#-------------------------------------------------------------------------------------
# 페이지 라우터

# 1. 메인 페이지 라우터
@app.get("/")
async def read_root() -> FileResponse:
    return FileResponse("frontend/index.html")

# 2. 스트리밍 페이지 라우터
@app.get("/stream")
async def stream_page() -> FileResponse:
    # 파일 경로가 변경되었으므로 수정
    return FileResponse("frontend/pages/streaming.html")

# 3. 게시판 페이지 라우터
@app.get("/board")
async def board_page() -> FileResponse:
    return FileResponse("frontend/pages/board.html")

#-------------------------------------------------------------------------------------
# 영상 스트리밍 엔드포인트

@app.get("/video_feed")
### OpenCV는 동기 작업이므로 async를 사용하지 않는다
def video_feed(cam_index: int = 0): #Streamlit에서 ?cam_index=1 처럼 카메라 인덱스를 파라미터로 보낼 수 있게 설정
    # 1. 카메라 연결 테스트
    test_cap = cv2.VideoCapture(cam_index)
    if not test_cap.isOpened(): #카메라 연결 실패시
        # 연결이 안되었으면 503 에러
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, #503 : 서비스 불가
            content={"detail": f"Camera {cam_index} not found or unavailable."} #해당 카메라 인덱스를 포함한 에러문 출력
        )
        #계속 연결이 안되면 503에러를 무한 반복하여 출력함
    test_cap.release() # 테스트가 끝났으니 카메라 연결을 해제하고 스트리밍 함수에 넘김

    # 2. 스트리밍 시작
    return StreamingResponse(
        generate_frames(cam_index), #영상 스트리밍 함수 실행
        media_type="multipart/x-mixed-replace; boundary=frame" #HTTP를 이용하여 브라우저에게 MJPEG 포멧임을 알림
    )

#-------------------------------------------------------------------------------------
# API 엔드포인트

# 1. `mouse` 탐지 로그 조회 API
@app.get("/api/logs")
async def get_logs() -> JSONResponse:
    df = mouse_log.get_recent_events(limit=10) # 최근 10개 이벤트 가져오기
    df = df.where(pd.notnull(df), None) # 결측값인 것은 None으로 변환 (JSON 직렬화를 위해)
    data = df.to_dict(orient="records") # 데이터프레임을 딕셔너리 리스트로 변환

    # 동영상의 절대경로중 파일명만 추출
    # 상단에 /videos 라는 주소로 비디오 폴더를 연결했었다
    for row in data:
        if row['video_path']:
            row['video_filename'] = os.path.basename(row['video_path'])
        else:
            row['video_filename'] = None
    return JSONResponse(content=data)

# 2-1. 게시글 데이터 수신을 위한 데이터 모델
class PostModel(BaseModel):
    nickname: str
    password: str
    content: str
    video_filename: str



# 2-2. 게시글 저장 API
@app.post("/api/share")
async def share_post(post: PostModel):
    try:
        #DB에 게시글 저장
        content_db.insert_post(
            nickname=post.nickname,
            password=post.password,
            content=post.content,
            video_filename=post.video_filename
        )
        return {"message": "success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

# 3. 게시글 + 댓글 병합 조회 API
@app.get("/api/posts")
async def get_posts() -> JSONResponse:
    posts: List[Dict[str, Any]] = content_db.get_all_posts() #모든 게시물 가져오기
    
    for post in posts: # 각 게시글에 해당하는 댓글 가져와서 합치기
        comments: List[Dict[str, Any]] = comment_db.get_comments_by_post_id(post['id'])
        post['comments'] = comments # 'comments' 키에 리스트 저장
        
    return JSONResponse(content=posts)

# 4-1. 게시글 삭제 요청용 데이터 모델
class DeleteModel(BaseModel):
    password: str

# 4-2. 게시글 삭제 API
@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: int, body: DeleteModel) -> Dict[str, str]:
    success: bool = content_db.delete_post(post_id, body.password)
    if success: #삭제 성공 시
        return {"message": "deleted"}
    else:
        # 비밀번호 불일치 또는 게시글 없음 -> 401 Unauthorized 또는 400 Bad Request
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    


# 5-1. 댓글 작성용 데이터 모델
class CommentModel(BaseModel):
    post_id: int
    nickname: str
    content: str
    password: str

# 5-2. 댓글 작성 API
@app.post("/api/comments")
async def add_comment(comment: CommentModel):
    try:
        #DB에 댓글 저장
        comment_db.insert_comment(comment.post_id, comment.nickname, comment.content, comment.password)
        return {"message": "success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

# 6. 댓글 삭제 API
@app.delete("/api/comments/{comment_id}")
async def delete_comment(comment_id: int, body: DeleteModel) -> Dict[str, str]:
    success = comment_db.delete_comment(comment_id, body.password)
    if success:
        return {"message": "deleted"}
    else:
        raise HTTPException(status_code=401, detail="비밀번호 불일치")

#-------------------------------------------------------------------------------------
# 서버가 구동되면 로컬 접속주소 출력
if __name__ == "__main__":
    print("서버 시작: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)