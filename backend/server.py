# server.py
import cv2
import pandas as pd
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

import os
import sys
# [중요] 프로젝트 루트 경로를 파이썬 경로에 추가
# 이 코드가 있어야 'backend' 패키지를 인식할 수 있습니다.
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from backend.make_db import mouse_log #`mouse_log.py` 모듈 import
from backend.video import generate_frames #`streaming.py` 모듈에서 영상 스트리밍 함수 import
from backend.make_db import content_db #`content_db.py` 모듈 import


    
#-------------------------------------------------------------------------------------
app = FastAPI() #FastAPI 서버 인스턴스 생성, uvicorn으로 실행



# 1. 정적 파일 경로 설정 (CSS, JS 등을 위해 필요할 수 있음, 현재는 구조상 크게 필요 없으나 유지)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# 영상 저장 디렉토리 설정 및 생성
VIDEO_DIR = "./DB/recorded_videos"
app.mount("/videos", StaticFiles(directory=VIDEO_DIR), name="videos")

#-------------------------------------------------------------------------------------


# 2. 메인 페이지 (대문)
@app.get("/")
async def read_root():
    return FileResponse("frontend/index.html")

# 3. 스트리밍 페이지
@app.get("/stream")
async def stream_page():
    # 파일 경로가 변경되었으므로 수정
    return FileResponse("frontend/pages/streaming.html")

# [추가] 게시판 페이지 라우터
@app.get("/board")
async def board_page():
    return FileResponse("frontend/pages/board.html")


@app.get("/video_feed") #영상 스트리밍 엔드포인트
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

# 최근 DB 데이터 로그 조회
@app.get("/api/logs")
async def get_logs():
    # 최근 10개 이벤트 가져오기
    df = mouse_log.get_recent_events(limit=10)
    # NaN(빈값)을 None으로 변환 (JSON 표준 호환성 문제 해결)
    df = df.where(pd.notnull(df), None)
    # 데이터프레임을 딕셔너리 리스트로 변환
    data = df.to_dict(orient="records")
    # [중요] DB에는 절대경로가 저장되어 있으므로, 웹에서 접근 가능한 '파일명'만 추출
    for row in data:
        if row['video_path']:
            row['video_filename'] = os.path.basename(row['video_path'])
        else:
            row['video_filename'] = None
    return JSONResponse(content=data)

# [추가] 게시글 데이터 수신을 위한 데이터 모델 정의
class PostModel(BaseModel):
    nickname: str
    password: str
    content: str
    video_filename: str

# [추가] 게시글 삭제 요청용 데이터 모델
class DeleteModel(BaseModel):
    password: str


# [추가] 게시글 저장 API Endpoint
@app.post("/api/share")
async def share_post(post: PostModel):
    try:
        content_db.insert_post(
            nickname=post.nickname,
            password=post.password,
            content=post.content,
            video_filename=post.video_filename
        )
        return {"message": "success"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

# [추가] 게시글 목록 조회 API
@app.get("/api/posts")
async def get_posts():
    posts = content_db.get_all_posts()
    return JSONResponse(content=posts)

# [추가] 게시글 삭제 API
@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: int, body: DeleteModel):
    success = content_db.delete_post(post_id, body.password)
    if success:
        return {"message": "deleted"}
    else:
        # 비밀번호 불일치 또는 게시글 없음 -> 401 Unauthorized 또는 400 Bad Request
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    

if __name__ == "__main__":
    print("서버 시작: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)