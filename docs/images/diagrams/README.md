# PULSE 다이어그램 이미지

현재 코드와 README를 기준으로 2026-10-06 작성했습니다.

- 01-db-erd.png: 실제 users / chats 테이블, 자료형·제약·1:N 관계
- 02-architecture.png: 저장소의 배포 구성, FastAPI·SQLite·외부 API 구성
- 03-system-flow.png: 인증부터 AI 호출·기록 저장·내 기록 조회까지의 처리 흐름
- 04-team-roles.png: README에 기재된 A~D 담당자와 모듈 간 책임 연결
- 00-overview.png: 네 이미지를 모은 미리보기

개별 PNG는 3000×1950 픽셀입니다. SVG는 같은 내용의 확대 가능한 원본입니다.
팀 역할은 실제 DB 테이블이 아닌 개념 관계도입니다.
아키텍처의 Ubuntu VM은 저장소의 배포 구성이며 실제 배포 상태를 뜻하지 않습니다.
DB의 mode/status 값 범위와 질문 길이는 애플리케이션 검증·처리 규칙입니다.
새 대화의 scenario_version 기본값은 2이며 구 스키마에 열 추가 시 기본값은 1입니다.
이미지는 AI 이미지 생성 없이 SVG를 코드로 작성해 Microsoft Edge에서 PNG로 렌더링했습니다.

근거: README.md, app/models/user.py, app/models/chat.py, app/database.py,
app/main.py, app/routers/chat.py, app/routers/logs.py, app/services/scenarios/,
deploy/ai-chatbot.service.

재생성: ./.venv/Scripts/python.exe scripts/render_project_diagrams.py
