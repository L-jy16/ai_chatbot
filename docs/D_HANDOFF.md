# D 작업 전달서

브랜치: `feature/ui`. 배포는 사용자 요청으로 제외했습니다.

## 구현된 내용

- 로그인·회원가입·채팅·내 기록, 공통 템플릿·반응형 CSS.
- Q1/Q4/Q5/Q6·예시 질문, 대기·오류, 입력 유지·중복 전송 방지.
- `create_logs_router()` 사용자별 조회, `install_ui()` 일괄 등록.
- 읽기 전용 SQLite SQL·Python CLI.
- 실제 앱과 분리한 데모·검증. 실제 회원가입·LLM은 대체하지 않습니다.

## A와 연결

1. `requirements-ui.txt`를 팀 의존성에 반영합니다.
2. SessionMiddleware를 설정하고 세션 `user_id`에 양의 정수를 저장합니다.
3. `require_login`이 사용자·인증 유효성을 검사하고 int/User/`{"id": int}`를 반환하게 합니다.
4. 동기 SQLAlchemy Session을 yield하는 `get_db`를 연결합니다.
5. `main.py`에서 README의 `install_ui()`를 한 번 호출합니다. 페이지·static·로그를 중복 등록하지 않습니다.
6. JSON `{email, password}`와 비밀번호 정책을 맞춥니다.
7. `.env.example`은 제안 이름입니다. 실제 config와 맞추고 데모의 임시 세션 키는 사용하지 않습니다.

## C와 연결

1. Chat의 계획서 필드를 구현하고 실패 시 nullable `answer`를 허용합니다.
2. `/api/chat`의 `{mode, message}` → `{chat_id, answer}` 계약을 맞춥니다.
3. 실패 상태·DB 저장을 유지합니다. 화면은 `message`/문자열 `detail`을 표시합니다.
4. 실제 Chat을 `install_ui()`에 주입합니다. 데모 모델을 import하지 않습니다.
5. AI timeout은 65초 미만으로 설정하고 DB timestamp 시간대를 A와 합의합니다.

## 검증 근거

- pytest 36개 통과: 인증 차단·사용자 분리·limit·null·DB 실패·모드·SQL.
- 별도 headless Chrome: 인증 화면·모드 payload·실패 복구·HTML 비실행·기록 상태·모바일·로그아웃.
- `output/ui/`: 로컬 캡처. Git에는 포함하지 않습니다.

## 통합 후 확인

- [ ] 실제 회원가입·로그인과 두 실제 계정의 기록 분리.
- [ ] 네이버·LLM 연결 후 네 시나리오 실제 응답.
- [ ] 성공/timeout/error를 영구 DB·API·화면·SQL에서 대조.
- [ ] 최근 대화 컨텍스트·서버 핵심 로그 확인.
- [ ] develop PR·리뷰·merge commit, 개인별 커밋·실제 작업자 확인.

A/B/C 코드가 없어 위 항목은 대기 상태입니다. 배포·URL 검증은 범위에서 제외했습니다.
