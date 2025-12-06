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
[![KTB3_max.ji_week12_assignment_community](https://i9.ytimg.com/vi/0rHqjLoMuDo/mqdefault.jpg?sqp=COCMz8kG-oaymwEmCMACELQB8quKqQMa8AEB-AGECYAC0AWKAgwIABABGGEgYShhMA8=&rs=AOn4CLDPz1BbhAa_i6HE-S4YYL4G_aK56Q)](https://youtu.be/0rHqjLoMuDo)  
![youtube](https://img.shields.io/badge/youtube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
[KTB3_max.ji_week12_assignment_community](https://youtu.be/0rHqjLoMuDo)

## 기능 구현


## 회고