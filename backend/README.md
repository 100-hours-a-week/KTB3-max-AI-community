# `./backend`
영상 처리 및 DB관리 백엔드 코드 저장

## I. `./backend/make_db`
데이터베이스를 생성, 편집에 사용하는 함수  
[make_db/README 바로가기](https://github.com/100-hours-a-week/KTB3-max-AI-community/blob/main/backend/make_db/README.md)

## II. `./backend/video`
카메라를 통한 영상 스트리밍과 이미지 프레임의 영상 파일 저장 함수  
[video/README 바로가기](https://github.com/100-hours-a-week/KTB3-max-AI-community/blob/main/backend/video/README.md)

## III. `./backend/yolo`
영상분석 탐지 객체를 위한 딥러닝 모델과 이를 활용한 이미지 프레임 편집 함수  
[yolo/README 바로가기](https://github.com/100-hours-a-week/KTB3-max-AI-community/blob/main/backend/yolo/README.md)

## IV. `server.py`
FastAPI 기반 백엔드 서버 구동
- 실행 명령어 :
```bash
uvicorn backend.server:app --reload --host 127.0.0.1 --port 8000 # 윈도우
```

## IV-1. FastAPI 스트리밍 라우터
1. `@app.get("/")` : 메인 페이지, `./frontend/index.html` 파일 실행
2. `@app.get("/stream")` : 스트리밍 페이지, `./frontend/pages/streaming.html` 파일 실행
3. `@app.get("/board")` : 게시판 페이지, `./frontend/pages/board.html` 파일 실행  
카메라 인덱스 지정 및 스트리밍 페이지로의 `MJPEG` 이미지 스트리밍 API
4. `@app.get("/api/logs")` : 최근 10개의 `mouse_log` DB 데이터 로그 조회  API
스트리밍 페이지 하단 매 1초마다 자동 갱신 및 영상 존재 시 공유 버튼 활성화
5. `@app.post("/api/share")` : 스트리밍 페이지에서 선택 동영상 게시판 업로드 API

## IV-2. FastAPI 게시판 라우터
1. `@app.get("/api/posts")` : 게시판 페이지에서 각 게시글과 이에 해당하는 댓글들 출력 API
2. `@app.delete("/api/posts/{post_id}")` : 게시글 삭제 API, 비밀번호 일치 시 삭제, 불일치 시 401 에러
3. `@app.post("/api/comments")` : 게시글 댓글 작성 API
4. `@app.delete("/api/comments/{comment_id}")` : 게시글 댓글 삭제 API, 비밀번호 일치 시 삭제, 불일치 시 401 에러