# KTB3-max-AI-community
카테부판교3기 max 인공지능과정 커뮤니티 제작 프로젝트 (프론트+백엔드)

# 목표
1. 영상 스트리밍 중 YOLO모델을 통해 `mouse` 실시간 탐지
2. 탐지된 영상 중 하나를 게시판에 업로드
3. 게시글에 댓글 작성

## 파일 구조
```bash
.
├── DB # 영상, 게시글, 댓글 DB 저장
│   ├── comment.db # 작성된 댓글 DB
│   ├── content.db # 게시된 게시글 DB
│   ├── mouse_log.db # 탐지된 `mouse` 영상 메타데이터 DB
│   └── recorded_videos # # 탐지된 `mouse` 영상 저장폴더
│
├── README.md # 해당 레포지토리 설명
│
├── __init__.py # 패키지화
│
├── backend # 백엔드 관련 폴더
│   │
│   ├── make_db # DB생성 함수 저장
│   │   ├── __init__.py # 패키지화
│   │   ├── comment_db.py # `comment.db` CRUD 기능
│   │   ├── content_db.py # `content.db` CRUD 기능
│   │   └── mouse_log.py # `mouse_log.db` CRUD 기능
│   │
│   ├── server.py # 서버 구동, 라우터 지정
│   │
│   ├── video # 영상 처리 함수 저장
│   │   ├── __init__.py # 패키지화
│   │   ├── streaming.py # 프레임 가공(`mouse` 탐지) 및 스트리밍
│   │   └── video_recorder.py # 영상 녹화(mp4)
│   │
│   └── yolo # YOLO 모델 구동 함수 저장
│       ├── __init__.py # 패키지화
│       ├── detector.py # 프레임 가공(객체 탐지) 함수
│       └── yolo11n.pt # YOLO11n 모델 (없을 경우 자동 다운로드)
│
├── frontend # 프론트엔드 관련 폴더
│   │
│   ├── index.html # 메인 페이지 
│   │
│   └── pages # 기능 페이지
│       ├── board.html # 게시판 페이지
│       └── streaming.html # 영상 스트리밍 페이지
│
└── requirements.txt # 타 로컬환경 구동용 필수 라이브러리 기입
```

## 시험 구동 영상
[![KTB3_max.ji_week12_assignment_community](https://velog.velcdn.com/images/swoo64/post/d90586c6-68d9-441d-b470-75297de0ca11/image.png)](https://youtu.be/0rHqjLoMuDo)  
![youtube](https://img.shields.io/badge/youtube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
[KTB3_max.ji_week12_assignment_community](https://youtu.be/0rHqjLoMuDo)

## 기능 구현
### ① 백엔드 코드
[backend/README 바로가기](https://github.com/100-hours-a-week/KTB3-max-AI-community/tree/main/backend)
### ② 프론트엔드 코드
[frontend 바로가기](https://github.com/100-hours-a-week/KTB3-max-AI-community/tree/main/frontend)  
프론트엔드는 나의 영역이 아니기 때문에 바이브코딩으로 작성 + 코드 설명은 진행하지 않는다

### ③ 서비스 구동
1. 가상환경 생성 및 접속
```bash
python -m venv .venv #가상환경 생성
.venv\Scripts\Activate.ps1 #가상환경 접속 - Windows PowerShell 기준
pip install -r requirements.txt #패키지 설치

deactivate #가상환경 종료
```
2. 서버 구동
```bash
uvicorn backend.server:app --reload --host 127.0.0.1 --port 8000 #윈도우 기준
```
3. `http://127.0.0.1:8000` 로컬 서버 접속

4. 메인 페이지 접속  

|메인 페이지|
|---|
|![메인 페이지](https://velog.velcdn.com/images/swoo64/post/6fcb1b80-ca8c-4881-bce4-f45c962973cf/image.png)|

5. 영상 스트리밍 접속

|스트리밍 페이지 접속|최근 탐지 로그 - 탐지중|최근 탐지 로그 - 탐지 완료|
|---|---|---|
|![](https://velog.velcdn.com/images/swoo64/post/887b0f5f-ae1f-4e65-9be9-e51ca0476c69/image.png)|![](https://velog.velcdn.com/images/swoo64/post/c4a9cf0f-a9c3-4660-8c1d-9a9442a592cb/image.png)|![](https://velog.velcdn.com/images/swoo64/post/1d178753-f413-483f-ac1a-9dcc1eab81d9/image.png)|

6. 영상 게시글 업로드

|비디오 확인 버튼-> 공유|게시판 페이지 접속|게시글 삭제|게시글 삭제 실패|
|---|---|---|---|
|![](https://velog.velcdn.com/images/swoo64/post/d5e799ef-f536-4ff9-846c-6cd62b383711/image.png)|![](https://velog.velcdn.com/images/swoo64/post/77033f04-444a-4ab7-a346-9dd086746a49/image.png)|![](https://velog.velcdn.com/images/swoo64/post/3aa4bcbd-ad97-4d5e-b723-f54df02cf05e/image.png)|![](https://velog.velcdn.com/images/swoo64/post/f1874b53-24b9-41c4-90c2-deca777187a6/image.png)|

7. 댓글 작성

|댓글 작성|작성 결과|댓글 삭제|댓글 삭제 실패|
|---|---|---|---|
|![](https://velog.velcdn.com/images/swoo64/post/0441fac4-1f81-4b6b-8bb0-feea0213db67/image.png)|![](https://velog.velcdn.com/images/swoo64/post/ac6d8450-456d-436e-99fb-46e16ecf8f44/image.png)|![](https://velog.velcdn.com/images/swoo64/post/9159dec0-ee60-4877-90ba-0193d411e019/image.png)|![](https://velog.velcdn.com/images/swoo64/post/fdbd6694-a6f4-4720-85c4-ebcb9f7ae3ad/image.png)|

## 회고