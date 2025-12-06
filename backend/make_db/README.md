# `./backend/make_db`
데이터베이스를 생성, 편집에 사용하는 함수를 모아두었다.
- `SQLite3`를 이용
- 저장 경로 : `./DB`

## I. `mouse_log.py`
- 모듈 호출 : 
```python
from backend.make_db import mouse_log
```
- 관련 파일 : `./DB/mouse_log.db`, `./backend/video/video_recorder.py`, `./backend/server.py`

### I-1) `init_db()`
- `mouse_log` 테이블 생성 (`mouse`탐지 기록 저장 DB)  
- 해당 파일 실행 또는 import시 `init_db()`함수 자동 실행
- 이미 `mouse_log` DB가 존재한다면 초기화를 진행하지 않음

|컬럼|타입|설명|
|---|---|---|
|id (PRIMARY KEY)|int|영상 식별 부호|
|start_time|text|녹화 시작 시간|
|end_time|text|녹화 종료 시간|
|path_log|text|`mouse`의 화면상 이동 경로|
|video_path|text|녹화 영상 저장 경로|

### I-2) `insert_event()`
- 입력 : 현재 시간 (탐지 시작 시간)
- `mouse`를 처음 탐지하였을 때 탐지 이벤트를 생성
- 탐지 시작 시간을 `start_time`으로 문자열 변환, 이 값을 통해 `mouse_log` DB에 새로운 인스턴스 추가 후 `id`를 반환
- 출력 : `id`

### I-3) `update_event()`
- 입력 : `event_id`, 현재 시간 (탐지 종료 시간), `path_log`, `video_path`
- `mouse`탐지가 종료되었을 때 해당 탐지 이벤트를 종료
- 탐지 종료 시간을 `end_time`으로 문자열 변환
- 탐지 이벤트의 `id`를 가지는 인스턴스에 해당 값 업데이트

### I-4) `get_recent_events()`
- 입력 : `limit` (최대 출력 인스턴수 수)
- 최근 탐지한 이벤트들을 DB에서 출력 후 데이터프레임으로 변환
- 출력 : `df`

## II. `content_db.py`
- 관련 파일 : `./DB/content.db`, `./backend/server.py`
- 모듈 호출 : 
```python
from backend.make_db import content_db
```

### II-1) `init_db()`
- `posts` 테이블 생성 (게시글 저장 DB)  
- 해당 파일 실행 또는 import시 `init_db()`함수 자동 실행
- 이미 `posts` DB가 존재한다면 초기화를 진행하지 않음

|컬럼|타입|설명|
|---|---|---|
|id (PRIMARY KEY)|int|게시글 식별 부호|
|nickname|text|게시글 작성 닉네임|
|password|text|게시글 작성 비밀번호|
|content|text|게시글 작성 내용|
|video_filename|text|업로드된 녹화 영상 이름|
|created_at|text|게시글 업로드 시간|

### II-2) `insert_post()`
- 입력 : `nickanme`, `password`, `content`, `video_filename`
- `posts` DB에 게시글 저장 함수
- 현재 시간으로 `created_at`생성 및 문자열 변환

### II-3) `get_all_posts()`
- `posts` DB에서 모든 게시글을 `id`를 기준으로 최신순으로 조회
- 조회된 데이터를 `DICT`형태로 변환 후 리스트로 반환
- 출력 : `LIST[DICT]`

### II-4) `delete_post()`
- 입력 : `id`, `password`
- 비밀번호가 일치하면 해당 게시글을 `posts` DB에서 삭제
- 출력 : `True` (삭제 성공 - 비밀번호 일치), `False` (삭제 실패 - 게시글 존재하지 않음 또는 비밀번호 불일치)


## III. `comment_db.py`
- 관련 파일 : `./DB/comment.db`, `./backend/server.py`
- 모듈 호출 : 
```python
from backend.make_db import comment_db
```

### III-1) `init_db()`
- `comments` 테이블 생성 (댓글 저장 DB)  
- 해당 파일 실행 또는 import시 `init_db()`함수 자동 실행
- 이미 `comments` DB가 존재한다면 초기화를 진행하지 않음

|컬럼|타입|설명|
|---|---|---|
|id (PRIMARY KEY)|int|댓글 식별 부호|
|post_id|int|댓글을 단 게시글 식별 부호|
|nickname|text|댓글 작성 닉네임|
|content|text|댓글 작성 내용|
|password|text|댓글 작성 비밀번호|
|created_at|text|댓글 업로드 시간|

### III-2) `insert_post()`
- 입력 : `post_id`, `nickanme`, `content`, `password`
- `comments` DB에 댓글 저장 함수
- 현재 시간으로 `created_at`생성 및 문자열 변환

### III-3) `get_comments_by_post_id()`
- 입력 : `post_id`
- 특정 게시글의 모든 댓글 목록 조회
- 조회된 데이터를 `DICT`형태로 변환 후 리스트로 반환
- 출력 : `LIST[DICT]`

### III-4) `delete_comment()`
- 입력 : `id`, `password`
- 비밀번호가 일치하면 해당 게시글을 `comments` DB에서 삭제
- 출력 : `True` (삭제 성공 - 비밀번호 일치), `False` (삭제 실패 - 댓글 존재하지 않음 또는 비밀번호 불일치)