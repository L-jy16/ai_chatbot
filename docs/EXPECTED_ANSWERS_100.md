# PULSE 답안 100선

작성 기준: 2026-10-06, 현재 작업 폴더 코드·README 및 로컬 Git 이력(확인 당시 HEAD `3bd5f57`).

Q001~Q030은 사용자가 제공한 평가 항목 30개(평가 1: 15개, 평가 2: 8개, 평가 3: 7개)에 순서대로 대응합니다. Q031~Q100은 추가 심화·시연·개인 기여 질문입니다. 질문·답안 번호는 두 문서에서 동일합니다.

답변은 구현과 설계 근거를 설명하는 연습용 초안입니다. 실제 기능 동작은 평가 환경에서 시연해야 합니다. 이번 확인에서 `./.venv/Scripts/python.exe -m pytest -q`는 `ModuleNotFoundError: No module named 'requests'`로 conftest import 중 중단되어 테스트 통과를 확인하지 못했습니다. 실제 AI 호출과 배포 서버 외부 접속도 이번 문서 작업에서 실행하지 않았습니다. 코드·테스트 존재를 실행 성공으로 표현하지 마세요.

[핵심 평가 질문·답안 30선](EVALUATION_PRIORITY_QA.md) · [예상 질문 100선](EXPECTED_QUESTIONS_100.md)

각 답안은 바로 말할 수 있는 설명과 근거·시연 방법을 함께 제공합니다. 개인 기여 답변은 본인 담당에 맞춰 선택하고, 개선 제안은 구현 완료와 구분하세요.

## 평가 1 · 문서와 기본 동작 · Q001~Q015

<a id="q001"></a>

### Q001. 시스템 구조도는 어디에 있고 어떤 구성요소를 설명하나요?

**답안:** README의 서비스 아키텍처 이미지에 브라우저, Ubuntu VM 배포 구성, FastAPI, SQLite, 네이버 API, Codyssey LLM 연결을 정리했습니다. 브라우저는 앱 API를 호출하고 외부 데이터와 AI 호출은 서버가 담당합니다. VM 그림은 저장소의 배포 설계이며 현재 서버 가동을 증명하는 자료는 아닙니다.

**근거:** [README.md](../README.md) · [docs/images/diagrams/02-architecture.png](../docs/images/diagrams/02-architecture.png) · [app/main.py](../app/main.py) · [deploy/ai-chatbot.service](../deploy/ai-chatbot.service)

**확인·시연:** README의 아키텍처 이미지를 열고 브라우저→서버→외부 API→DB 순서로 설명합니다.

<a id="q002"></a>

### Q002. API 명세와 요청·응답 예시는 어떻게 제공하나요?

**답안:** README에 메서드, 경로, 로그인 필요 여부, 성공 상태코드와 JSON 예시를 제공합니다. 가입·로그인은 email/password, 채팅은 mode/message/선택 keyword를 받고, 채팅 성공은 chat_id/answer를 반환합니다. 실행 중인 앱의 /docs에서도 등록된 API 스키마를 확인할 수 있습니다.

**근거:** [README.md](../README.md) · [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py)

**확인·시연:** README API 표와 요청·응답 예시를 보여주고 실행 환경에서는 /docs를 엽니다.

<a id="q003"></a>

### Q003. DB 구조와 ERD는 실제 코드와 일치하나요?

**답안:** 실제 테이블은 users와 chats입니다. users.id와 chats.user_id가 외래키로 연결되어 사용자 1명이 대화 0개 이상을 소유합니다. ERD에 실제 컬럼·자료형·NULL 허용·키·기본값을 표시했고, mode/status 값 범위는 DB CHECK가 아닌 애플리케이션 규칙임을 구분했습니다.

**근거:** [app/models/user.py](../app/models/user.py) · [app/models/chat.py](../app/models/chat.py) · [docs/images/diagrams/01-db-erd.png](../docs/images/diagrams/01-db-erd.png) · [app/database.py](../app/database.py)

**확인·시연:** ERD의 id/user_id 관계와 answer의 NULL 허용을 모델 선언과 대조합니다.

<a id="q004"></a>

### Q004. DB 파일과 저장된 대화는 어떻게 확인하나요?

**답안:** 기본 DATABASE_URL은 sqlite:///./app.db이며 실행 작업 폴더의 app.db를 사용합니다. scripts/check_logs.py는 지정 DB를 읽기 전용으로 열고 user_id 조건으로 대화 내용을 조회합니다. 화면 /history나 GET /api/me/chats로도 본인 기록을 확인할 수 있습니다.

**근거:** [app/config.py](../app/config.py) · [scripts/check_logs.py](../scripts/check_logs.py) · [scripts/check_logs.sql](../scripts/check_logs.sql) · [README.md](../README.md)

**확인·시연:** 실제 DB 경로와 본인 ID를 확인한 뒤 python scripts/check_logs.py --db app.db --user-id 1 --limit 20을 실행합니다.

<a id="q005"></a>

### Q005. 팀 역할과 개인별 기여는 어디에 정리했나요?

**답안:** README에 A 김준택의 기반·인증, B 이지영의 트렌드, C 정지환의 채팅·AI, D 김정현의 UI·기록 조회를 정리했습니다. 역할 이미지와 개인별 표에 파일 책임, 브랜치, PR, 통합 기여를 연결했습니다. 본인이 직접 수행한 작업은 해당 파일과 커밋을 함께 설명합니다.

**근거:** [README.md](../README.md) · [docs/images/diagrams/04-team-roles.png](../docs/images/diagrams/04-team-roles.png) · [docs/D_HANDOFF.md](../docs/D_HANDOFF.md) · [docs/C_AGENT_HANDOFF.md](../docs/C_AGENT_HANDOFF.md)

**확인·시연:** 팀 역할 표에서 본인 담당을 짚고 git log --all --oneline로 대응 커밋을 보여줍니다.

<a id="q006"></a>

### Q006. 회원가입은 어떤 절차로 동작하나요?

**답안:** POST /api/auth/signup이 이메일·비밀번호를 검증하고 중복 이메일을 확인한 뒤 bcrypt 해시를 users에 저장합니다. 성공 시 201과 id/email을 반환하고 자동 로그인은 하지 않습니다. 동일 이메일 중복은 UNIQUE 제약과 IntegrityError 처리로도 방어합니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/models/user.py](../app/models/user.py) · [tests/test_auth_signup.py](../tests/test_auth_signup.py) · [tests/test_auth_edge_cases.py](../tests/test_auth_edge_cases.py)

**확인·시연:** 새 이메일로 가입해 201을 확인하고 같은 이메일 재가입의 409를 비교합니다.

<a id="q007"></a>

### Q007. 로그인은 어떤 방식으로 동작하나요?

**답안:** POST /api/auth/login이 정규화된 이메일로 사용자를 조회하고 bcrypt로 비밀번호를 비교합니다. 성공하면 기존 세션 내용을 비우고 user_id를 서명된 세션 쿠키에 기록하며 200을 반환합니다. 실패는 401 INVALID_CREDENTIALS이고 비밀번호 해시는 응답하지 않습니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/security.py](../app/security.py) · [app/main.py](../app/main.py) · [tests/test_auth_login.py](../tests/test_auth_login.py)

**확인·시연:** 정상 로그인, 잘못된 비밀번호, 로그인 후 /api/me 조회를 순서대로 확인합니다.

<a id="q008"></a>

### Q008. 비로그인 사용자는 어떤 기능을 사용할 수 없나요?

**답안:** 채팅과 내 기록 API는 require_login 의존성으로 보호되어 비로그인 요청에 401 LOGIN_REQUIRED를 반환합니다. 채팅·기록 페이지는 /login으로 303 리다이렉트합니다. 회원가입·로그인 페이지와 /health는 비로그인 상태에서도 접근할 수 있습니다.

**근거:** [app/dependencies.py](../app/dependencies.py) · [app/routers/pages.py](../app/routers/pages.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py)

**확인·시연:** 로그아웃 상태에서 /와 /history의 리다이렉트, /api/chat과 /api/me/chats의 401을 보여줍니다.

<a id="q009"></a>

### Q009. 웹 UI에서 질문 입력과 답변 출력이 가능한가요?

**답안:** 채팅 화면에서 모드와 질문을 입력하면 chat.js가 /api/chat에 JSON을 전송합니다. 성공 응답의 answer를 assistant 메시지로 추가하고 대기 상태를 해제합니다. 답변 표시에는 textContent를 사용하며 실제 AI 응답 시연은 app.main:app에서 별도로 확인해야 합니다.

**근거:** [app/templates/chat.html](../app/templates/chat.html) · [app/static/js/chat.js](../app/static/js/chat.js) · [app/static/js/common.js](../app/static/js/common.js) · [tests/test_ui_auth_integration.py](../tests/test_ui_auth_integration.py)

**확인·시연:** 실제 앱에 로그인해 질문을 전송하고 화면 답변과 네트워크 응답의 answer를 비교합니다.

<a id="q010"></a>

### Q010. 질문부터 AI 호출과 출력까지 전체 흐름을 설명해 주세요.

**답안:** UI 전송 뒤 서버가 인증·입력을 검증하고 본인의 최근 성공 대화 5쌍과 모드별 참고 자료를 구성합니다. ask_llm이 서버에서 Codyssey API를 한 번 호출하고, 결과·상태를 DB에 commit한 후 응답합니다. UI는 반환된 answer 또는 오류 안내를 표시합니다.

**근거:** [docs/images/diagrams/03-system-flow.png](../docs/images/diagrams/03-system-flow.png) · [app/routers/chat.py](../app/routers/chat.py) · [app/services/llm.py](../app/services/llm.py) · [app/static/js/chat.js](../app/static/js/chat.js)

**확인·시연:** 실제 앱 질문 1건의 UI→POST /api/chat→대화 저장→내 기록 조회를 한 흐름으로 확인합니다.

<a id="q011"></a>

### Q011. 사용자·시간·질문·AI 응답이 DB에 저장되나요?

**답안:** chats에 user_id, created_at, question, answer를 저장해 사용자와 시각 기준으로 추적합니다. mode, scenario_version, status도 함께 저장합니다. AI 실패는 answer=NULL과 timeout/error 상태로 남기며 DB 저장 자체가 실패한 경우에는 기록 저장을 보장하지 않고 500을 반환합니다.

**근거:** [app/models/chat.py](../app/models/chat.py) · [app/routers/chat.py](../app/routers/chat.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** 채팅 응답 chat_id와 조회된 행의 id·question·answer·status를 대조합니다.

<a id="q012"></a>

### Q012. 특정 사용자의 대화 로그만 조회할 수 있나요?

**답안:** GET /api/me/chats는 인증 사용자 ID로 WHERE 조건을 만들어 본인 기록만 반환합니다. 요청자가 다른 user_id를 전달해도 조회 대상은 바뀌지 않습니다. 운영용 읽기 전용 스크립트는 명시한 사용자 ID로 조회하지만 웹 인증 API와 같은 권한 경계는 없으므로 DB 파일 접근 권한이 필요합니다.

**근거:** [app/routers/logs.py](../app/routers/logs.py) · [scripts/check_logs.py](../scripts/check_logs.py) · [tests/test_ui.py](../tests/test_ui.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** 두 사용자로 로그인해 각 기록을 확인하고 user_id 쿼리를 추가해도 타인 기록이 나오지 않는지 확인합니다.

<a id="q013"></a>

### Q013. AI 실패·타임아웃에도 서비스가 계속 동작하도록 했나요?

**답안:** LLM 클라이언트는 HTTP 오류를 AIServiceError, 타임아웃을 AITimeoutError로 변환합니다. 채팅 라우터는 두 예외를 처리해 실패 상태를 저장하고 안내 응답을 반환합니다. 이는 알려진 AI 실패 경로에 대한 처리이며 모든 예외·인프라 장애를 처리한다는 의미는 아닙니다.

**근거:** [app/services/llm.py](../app/services/llm.py) · [app/routers/chat.py](../app/routers/chat.py) · [tests/test_llm.py](../tests/test_llm.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** 모의 타임아웃·AI 오류 후 다음 요청을 보내 정상 처리 가능한지 확인합니다.

<a id="q014"></a>

### Q014. 오류가 발생하면 사용자는 어떤 안내를 받나요?

**답안:** 입력 오류 422, 비로그인 401, AI 오류 502, AI 타임아웃 504, 대화 저장 실패 500을 구분합니다. 인증·검증·채팅 오류는 주로 error/message 형식이고 기록 조회 DB 오류는 503과 detail을 반환합니다. UI의 공통 요청 함수는 두 형식 모두 사용자 안내로 바꿉니다.

**근거:** [app/errors.py](../app/errors.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [app/static/js/common.js](../app/static/js/common.js)

**확인·시연:** 빈 질문, 잘못된 로그인, 모의 AI 타임아웃의 상태코드와 화면 문구를 비교합니다.

<a id="q015"></a>

### Q015. 어떤 사용자 입력 검증을 구현했나요?

**답안:** ChatRequest가 mode와 message의 문자열 여부를 확인하고 공백 제거 후 질문 1~500자, keyword 최대 50자를 검증합니다. 가입은 이메일 형식과 비밀번호 8자 이상·UTF-8 72바이트 이하를 확인합니다. UI 검증을 우회한 직접 API 요청도 서버에서 검사합니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/routers/auth.py](../app/routers/auth.py) · [tests/test_chat.py](../tests/test_chat.py) · [tests/test_auth_signup.py](../tests/test_auth_signup.py)

**확인·시연:** 공백 질문·501자 질문·잘못된 mode·짧은 비밀번호를 직접 API로 전송해 422를 확인합니다.

## 평가 2 · 구조와 협업 · Q016~Q023

<a id="q016"></a>

### Q016. 프로젝트 구조를 역할 단위로 어떻게 나눴나요?

**답안:** app/routers는 HTTP 경계, services는 트렌드·LLM·시나리오, models는 DB 구조를 담당합니다. config/database/dependencies/security/errors는 공통 기반이고 templates/static은 UI입니다. main.py는 이 구성요소를 등록하는 진입점입니다.

**근거:** [README.md](../README.md) · [app/main.py](../app/main.py) · [app/ui.py](../app/ui.py) · [app/database.py](../app/database.py)

**확인·시연:** README 파일 구조와 실제 app/ 폴더를 나란히 보여줍니다.

<a id="q017"></a>

### Q017. API 라우트는 목적에 맞게 분리되어 있나요?

**답안:** auth.py는 /api/auth의 가입·로그인·로그아웃, chat.py는 채팅과 /api/me, logs.py는 /api/me/chats를 담당합니다. pages.py는 HTML 페이지를 분리하고 /docs 스키마에서 제외합니다. UI 설치 함수는 중복 경로 등록도 검사합니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [app/routers/pages.py](../app/routers/pages.py) · [app/ui.py](../app/ui.py)

**확인·시연:** 각 라우터의 prefix와 decorator를 확인하고 main.py의 등록 지점을 보여줍니다.

<a id="q018"></a>

### Q018. 요청·응답 형식의 일관성은 어떻게 관리하나요?

**답안:** 가입·로그인·채팅 요청에는 Pydantic 모델을 쓰고 사용자 응답은 UserResponse, 기록 응답은 ChatLog 목록으로 제한합니다. 채팅 성공은 chat_id/answer 딕셔너리이며 명시적 response_model은 아직 없습니다. 대부분 오류는 error/message로 통일했지만 기록 조회의 detail 형식은 공통 UI에서 함께 처리합니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [app/errors.py](../app/errors.py)

**확인·시연:** UserResponse·ChatLog·ChatRequest를 보여주고 채팅 응답 스키마와 오류 형식의 남은 개선점을 설명합니다.

<a id="q019"></a>

### Q019. 인증 로직을 어떻게 재사용하도록 분리했나요?

**답안:** SessionMiddleware가 서명된 쿠키를 처리하고 get_current_user가 세션 user_id로 DB 사용자를 조회합니다. require_login은 로그인 필요 API에 Depends로 재사용합니다. HTML 페이지는 get_current_user 결과가 없을 때 로그인 화면으로 이동합니다.

**근거:** [app/main.py](../app/main.py) · [app/dependencies.py](../app/dependencies.py) · [app/routers/pages.py](../app/routers/pages.py) · [tests/test_dependencies.py](../tests/test_dependencies.py)

**확인·시연:** 채팅·기록·로그아웃에 같은 require_login이 적용되는 코드를 보여줍니다.

<a id="q020"></a>

### Q020. DB 접근이 라우터와 충분히 분리되어 있나요?

**답안:** 엔진 생성, 요청별 세션, ORM 모델은 database.py와 models로 분리했습니다. 다만 사용자 조회·대화 조회·commit 등은 라우터에 남아 있어 별도 CRUD·리포지토리 계층까지 분리된 구조는 아닙니다. 이 기준은 기반 분리는 되어 있으나 쿼리·트랜잭션 경계 분리의 개선 여지가 있다고 답하겠습니다.

**근거:** [app/database.py](../app/database.py) · [app/models/user.py](../app/models/user.py) · [app/models/chat.py](../app/models/chat.py) · [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py)

**확인·시연:** 분리된 엔진·세션·모델과 라우터에 남은 쿼리를 함께 제시합니다.

<a id="q021"></a>

### Q021. API 키 같은 민감정보가 코드에 하드코딩되어 있나요?

**답안:** 실제 API 키와 세션 서명 키는 pydantic-settings를 통해 환경 변수 또는 .env에서 읽습니다. 코드에는 키 값 대신 변수 이름과 기본 연결 주소가 있습니다. LLM·네이버 호출은 서버에서 수행하고 /api/me는 설정 여부만 boolean으로 반환합니다.

**근거:** [app/config.py](../app/config.py) · [app/services/llm.py](../app/services/llm.py) · [app/services/trend.py](../app/services/trend.py) · [app/routers/chat.py](../app/routers/chat.py)

**확인·시연:** 설정 필드와 외부 API 헤더 생성 코드를 보여주되 실제 .env 값은 화면에 표시하지 않습니다.

<a id="q022"></a>

### Q022. .env 예시와 Git 제외 설정을 어떻게 제공하나요?

**답안:** .env.example에는 변수 이름·기본값과 빈 비밀 값만 제공합니다. .gitignore는 .env와 .env.*를 제외하고 .env.example만 허용하며 DB 파일과 가상환경도 제외합니다. 이 설정은 현재 파일의 추적 방지이며 과거 Git 이력 전체의 비밀 값 부재를 증명하는 검사와는 구분합니다.

**근거:** [.env.example](../.env.example) · [.gitignore](../.gitignore) · [README.md](../README.md)

**확인·시연:** git ls-files .env .env.example과 git check-ignore -v .env로 추적·제외 상태를 확인합니다.

<a id="q023"></a>

### Q023. PR 기반 병합과 브랜치 흐름을 증명할 수 있나요?

**답안:** 로컬 Git 이력에 PR #2 인증, #4 UI, #5 트렌드, #3 채팅, #6 배포 문서의 병합 커밋이 있습니다. feature/*, develop, main과 관련 원격 추적 브랜치도 확인됩니다. 병합 커밋은 PR 사용 근거이지만 리뷰 승인 내용은 별도 PR 화면에서 확인해야 합니다.

**근거:** [README.md](../README.md) · [docs/D_PR_DRAFTS.md](../docs/D_PR_DRAFTS.md)

**확인·시연:** git log --all --merges --oneline과 git branch -a를 보여주고 각 PR·역할을 대응시킵니다.

## 평가 3 · 설계 이유와 운영 추적 · Q024~Q030

<a id="q024"></a>

### Q024. REST 관점에서 엔드포인트와 메서드는 어떤 기준으로 정했나요?

**답안:** 가입·로그인·로그아웃·AI 대화 생성은 상태 변화나 처리가 있으므로 POST, 내 정보·기록·상태 조회는 GET을 사용했습니다. 본인 자원은 /api/me와 /api/me/chats로 표현했습니다. 로그인 동작은 액션 경로이며 모든 경로가 엄격한 자원 중심 REST라고 주장하지는 않습니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [README.md](../README.md)

**확인·시연:** API 표에서 조회 GET과 처리 POST, 가입 201·로그아웃 204의 의도를 설명합니다.

<a id="q025"></a>

### Q025. 이 서비스에 인증·인가가 왜 필요한가요?

**답안:** 대화에는 사용자의 제작 기획과 과거 업로드 맥락이 들어가므로 다른 사용자가 접근하면 안 됩니다. 인증은 요청자의 신원을 확인하고, 인가는 조회·AI 문맥을 그 사용자의 기록으로 제한합니다. 비로그인 AI 호출 제한은 비용 사용의 기본 경계이지만 호출량 제한 기능을 대신하지는 않습니다.

**근거:** [app/dependencies.py](../app/dependencies.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** 비로그인 차단과 두 계정의 문맥·기록 격리를 함께 보여줍니다.

<a id="q026"></a>

### Q026. AI 호출을 클라이언트가 아닌 서버에서 하는 이유는 무엇인가요?

**답안:** 클라이언트에 키를 넣으면 브라우저 소스나 네트워크에서 키를 가져갈 수 있습니다. 서버는 인증·입력 검증·참고 자료·실패 처리·저장을 통합한 뒤 AI를 호출합니다. 브라우저에는 앱 API 결과만 반환하므로 공급자 키를 전달할 필요가 없습니다.

**근거:** [app/services/llm.py](../app/services/llm.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/static/js/chat.js](../app/static/js/chat.js)

**확인·시연:** 브라우저의 /api/chat 요청과 서버 ask_llm의 Authorization 헤더 생성 위치를 비교합니다.

<a id="q027"></a>

### Q027. AI 지연·실패 정책은 무엇이며 재시도도 있나요?

**답안:** LLM HTTP 클라이언트의 기본 timeout은 50초이고 브라우저 채팅 대기는 기본 65초입니다. AI 타임아웃·서비스 오류는 각각 504·502로 안내하고 자동 재시도는 없습니다. 50초는 연결·읽기·쓰기·풀 대기 제한이므로 트렌드 수집부터 DB 저장까지의 총 50초 상한은 아닙니다.

**근거:** [app/config.py](../app/config.py) · [app/services/llm.py](../app/services/llm.py) · [app/static/js/common.js](../app/static/js/common.js) · [tests/test_llm.py](../tests/test_llm.py)

**확인·시연:** 타임아웃 설정과 재시도 없는 단일 API 호출을 보여주고 총 처리 시간 제한과의 차이를 설명합니다.

<a id="q028"></a>

### Q028. 대화 로그를 왜 저장하며 실제 기능에 어떻게 사용하나요?

**답안:** 사용자가 이전 추천을 다시 확인하고 실패 내역을 추적할 수 있도록 저장합니다. 성공 기록은 다음 질문의 최근 5쌍 문맥으로 재사용하고 /history·조회 API·읽기 전용 스크립트로 확인합니다. 자동 학습이나 모델 재훈련 파이프라인은 구현하지 않았습니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [scripts/check_logs.py](../scripts/check_logs.py) · [app/models/chat.py](../app/models/chat.py)

**확인·시연:** 이전 답변을 기록 화면에서 다시 보고 후속 질문의 문맥 구성 코드를 설명합니다.

<a id="q029"></a>

### Q029. 문제 발생 시 요청·AI·DB 단계의 원인을 추적할 수 있나요?

**답안:** 채팅 라우터가 request_received, ai_call_start, ai_call_success 또는 ai_call_fail, db_save_success 또는 db_save_fail을 남깁니다. user_id·mode·저장 성공 시 chat_id와 AI 오류 사유로 실패 단계를 추적합니다. 요청 고유 ID와 처리 시간 지표는 없으므로 같은 사용자의 동시 요청을 완전히 구분하는 기능은 개선 과제입니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/main.py](../app/main.py) · [docs/DEPLOY.md](../docs/DEPLOY.md) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** journalctl -u ai-chatbot -f에서 단계별 이벤트를 확인하고 AI 실패와 DB 실패를 구분합니다.

<a id="q030"></a>

### Q030. 문서의 개인별 기여가 Git 이력과 일치하나요?

**답안:** README의 역할 표를 소유 파일과 PR·커밋에 연결해 설명할 수 있습니다. 로컬 이력에서 #2/#4/#5/#3/#6 병합을 확인했고 A의 배포 문서·통합 기여도 표에 반영되어 있습니다. 커밋 작성자 표기와 실제 팀원 이름이 다를 수 있어 계정·작성자·파일을 함께 확인해야 합니다.

**근거:** [README.md](../README.md) · [docs/C_AGENT_HANDOFF.md](../docs/C_AGENT_HANDOFF.md) · [docs/D_HANDOFF.md](../docs/D_HANDOFF.md)

**확인·시연:** git log --all --format=fuller -- app/routers/auth.py 등 담당 파일별 이력을 조회합니다.

## 서비스 목적과 시나리오 · Q031~Q040

<a id="q031"></a>

### Q031. PULSE가 해결하려는 사용자 문제는 무엇인가요?

**답안:** 경제·AI 숏폼 제작자가 최신 이슈를 기획 주제로 바꾸고 이전 영상과 연결하기 어려운 문제를 다룹니다. 뉴스와 검색 추이를 참고해 주제·게시 타이밍·새 관점·후속 편을 제안합니다. 실제 인기나 조회수 향상을 검증한 서비스라고 말하지 않고 기획 의사결정을 돕는 도구로 설명합니다.

**근거:** [README.md](../README.md) · [docs/SCENARIOS.md](../docs/SCENARIOS.md)

**확인·시연:** 타겟 사용자와 Q1~Q5의 질문 예시를 연결해 설명합니다.

<a id="q032"></a>

### Q032. 일반적인 자유 대화 챗봇과의 차이는 무엇인가요?

**답안:** UI가 Q1~Q5 기획 목적을 중심으로 질문을 안내하고 서버가 모드별 참고 자료와 출력 규칙을 구성합니다. 본인의 최근 대화와 과거 업로드 주제를 활용해 후속 기획을 돕습니다. 기반 LLM 자체를 새로 학습한 것이 아니라 데이터 수집과 프롬프트·UI 흐름을 결합한 서비스입니다.

**근거:** [app/services/scenarios/q1.py](../app/services/scenarios/q1.py) · [app/services/scenarios/q2.py](../app/services/scenarios/q2.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/static/js/modes.js](../app/static/js/modes.js)

**확인·시연:** 같은 주제를 Q3 타이밍과 Q4 새로운 각도로 질문해 기대 출력 형식의 차이를 설명합니다.

<a id="q033"></a>

### Q033. Q1 오늘의 주제는 어떻게 생성하나요?

**답안:** 경제 최신 뉴스에서 키워드를 고르고 각 키워드의 최근·이전 검색 추이를 비교합니다. 그 자료를 system 프롬프트에 넣어 주제 3개와 최종 추천 1개, 제목·훅·핵심 내용을 요청합니다. 자료가 부족하면 최신 수치나 이슈를 지어내지 않도록 명시합니다.

**근거:** [app/services/scenarios/q1.py](../app/services/scenarios/q1.py) · [app/services/trend.py](../app/services/trend.py)

**확인·시연:** Q1의 news/comparisons 자료 구조와 답변 항목을 코드에서 보여줍니다.

<a id="q034"></a>

### Q034. Q2가 과거 업로드 주제를 먼저 묻는 이유는 무엇인가요?

**답안:** 운영 중인 채널과 연결된 추천을 하려면 기존 주제가 필요합니다. UI는 업로드 주제를 질문 문자열에 포함하고 서버는 현재 질문이나 이전 질문에서 해당 맥락을 찾습니다. 맥락이 없으면 채널 이력을 임의로 만들지 않고 먼저 주제를 묻게 합니다.

**근거:** [app/static/js/chat.js](../app/static/js/chat.js) · [app/services/scenarios/q2.py](../app/services/scenarios/q2.py) · [docs/SCENARIOS.md](../docs/SCENARIOS.md)

**확인·시연:** Q2 주제 입력이 비어 있을 때의 안내와 최근 업로드 주제가 포함된 요청 JSON을 비교합니다.

<a id="q035"></a>

### Q035. Q3 타이밍 체크는 무엇을 근거로 판단하나요?

**답안:** 지정 keyword 또는 질문에서 추출한 키워드의 데이터랩 추이와 관련 뉴스 일부를 참고합니다. 프롬프트는 지금 올리기·기다리기·각도 바꾸기의 이유를 제시하도록 합니다. 데이터 부족은 관심 없음으로 처리하지 않고 판단을 보류하도록 안내합니다.

**근거:** [app/services/scenarios/q3.py](../app/services/scenarios/q3.py) · [app/services/trend.py](../app/services/trend.py)

**확인·시연:** keyword와 comparison·news를 확인하고 unknown일 때의 프롬프트 규칙을 설명합니다.

<a id="q036"></a>

### Q036. Q4 새로운 각도는 어떤 결과를 목표로 하나요?

**답안:** 같은 주제를 반전·비교·논쟁·정보·경험의 다섯 관점으로 재해석합니다. 최신 뉴스 제목 일부를 참고해 전체 5~10개 아이디어와 최종 추천 1개 및 이유를 요청합니다. 프롬프트 요구사항이지 모든 실제 답변의 형식을 강제로 검사하는 로직은 아닙니다.

**근거:** [app/services/scenarios/q5.py](../app/services/scenarios/q5.py) · [tests/test_scenarios.py](../tests/test_scenarios.py)

**확인·시연:** 화면 q4가 scenarios/q5.py로 연결되는 지점과 다섯 관점 규칙을 보여줍니다.

<a id="q037"></a>

### Q037. Q5 다음 편 기획은 어떤 흐름인가요?

**답안:** 현재 질문이나 이전 대화에서 기존 영상 주제를 찾고 1편→2편→3편의 연결 구조와 오늘 올릴 편을 제안합니다. 주제가 없으면 임의로 정하지 않고 먼저 물어보도록 합니다. q5 화면 요청은 내부 scenarios/q6.py로 전달됩니다.

**근거:** [app/services/scenarios/q6.py](../app/services/scenarios/q6.py) · [app/routers/chat.py](../app/routers/chat.py) · [docs/SCENARIOS.md](../docs/SCENARIOS.md)

**확인·시연:** 이전 영상 주제를 담은 질문과 후속 질문을 보내 연결된 답변 여부를 확인합니다.

<a id="q038"></a>

### Q038. 화면 번호와 시나리오 파일 번호가 다른 이유는 무엇인가요?

**답안:** 기존 계획의 Q4/Q5/Q6 기능이 현재 화면에서는 Q3/Q4/Q5로 정리된 이력이 있습니다. 라우터가 q4→q5.py, q5→q6.py로 명시적으로 대응하므로 파일명만 보고 기능을 판단하면 안 됩니다. 신규 요청·저장은 현재 화면 번호를 기준으로 합니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [docs/SCENARIOS.md](../docs/SCENARIOS.md) · [tests/test_mode_integration.py](../tests/test_mode_integration.py)

**확인·시연:** ALLOWED_MODES와 모드 분기, 문서의 대응표를 함께 보여줍니다.

<a id="q039"></a>

### Q039. free 모드는 UI에서도 선택할 수 있나요?

**답안:** 서버 API는 q1~q5 외에 free를 허용하지만 UI에는 자유 질문 버튼이 없습니다. free는 외부 트렌드 조회 없이 기본 system 프롬프트와 최근 성공 대화를 사용합니다. API 지원 범위와 화면 제공 범위를 구분해서 설명해야 합니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/static/js/modes.js](../app/static/js/modes.js) · [README.md](../README.md)

**확인·시연:** UI의 다섯 모드와 서버 ALLOWED_MODES의 free를 비교합니다.

<a id="q040"></a>

### Q040. 이 서비스가 조회수나 투자 성과를 보장하나요?

**답안:** 보장하지 않습니다. 네이버 검색 상대지수와 일부 뉴스는 기획 참고자료이며 유튜브 조회수·전체 언급량·투자 수익의 측정값이 아닙니다. 추천은 그 자료와 질문을 바탕으로 한 아이디어이고 결과는 별도 검증이 필요합니다.

**근거:** [README.md](../README.md) · [app/services/scenarios/q1.py](../app/services/scenarios/q1.py) · [app/services/scenarios/q3.py](../app/services/scenarios/q3.py) · [docs/SCENARIOS.md](../docs/SCENARIOS.md)

**확인·시연:** 검색 관심도와 조회수의 차이, 뉴스 수집 범위를 설명합니다.

## 인증·인가와 보안 · Q041~Q050

<a id="q041"></a>

### Q041. 세션 쿠키에는 무엇이 들어가며 암호화되나요?

**답안:** 앱은 세션에 user_id를 기록하고 SessionMiddleware가 내용을 서명합니다. 서명은 변조 확인을 위한 것이며 내용을 비밀로 숨기는 암호화로 설명하면 안 됩니다. API 키·비밀번호·해시는 세션에 저장하지 않습니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/main.py](../app/main.py) · [tests/test_auth_edge_cases.py](../tests/test_auth_edge_cases.py)

**확인·시연:** 세션에 user_id만 넣는 코드와 쿠키 변조 거절 테스트를 보여줍니다.

<a id="q042"></a>

### Q042. HttpOnly·SameSite·Secure 설정은 어떻게 되어 있나요?

**답안:** 세션 쿠키는 HttpOnly와 SameSite=Lax를 사용합니다. 현재 main.py는 HTTP VM 배포를 고려해 https_only=False이므로 Secure 쿠키를 강제하지 않습니다. 운영 HTTPS 전환 시 https_only=True 적용이 개선 과제입니다.

**근거:** [app/main.py](../app/main.py) · [tests/test_auth_edge_cases.py](../tests/test_auth_edge_cases.py) · [docs/DEPLOY.md](../docs/DEPLOY.md)

**확인·시연:** 쿠키 속성 확인 코드·테스트와 현재 https_only 값을 보여줍니다.

<a id="q043"></a>

### Q043. 비밀번호를 평문으로 저장하지 않는 이유와 방법은 무엇인가요?

**답안:** DB 유출 시 원문 비밀번호 노출을 줄이기 위해 bcrypt 해시만 저장합니다. 가입 시 gensalt와 hashpw를 쓰고 로그인 시 checkpw로 비교합니다. users에는 password_hash가 있고 응답에는 id/email만 포함됩니다.

**근거:** [app/security.py](../app/security.py) · [app/models/user.py](../app/models/user.py) · [app/routers/auth.py](../app/routers/auth.py) · [tests/test_security.py](../tests/test_security.py)

**확인·시연:** User 모델과 해싱 함수를 보여주되 실제 사용자 해시는 표시하지 않습니다.

<a id="q044"></a>

### Q044. 비밀번호 72바이트 제한은 글자 수 제한과 같은가요?

**답안:** 다릅니다. 최소 길이는 8자이지만 최대는 UTF-8 인코딩 기준 72바이트라 한글·이모지는 문자 수보다 더 많은 바이트를 사용합니다. bcrypt가 처리 가능한 한도를 넘기지 않도록 가입 전에 검증하고 로그인도 72바이트 초과를 불일치로 처리합니다.

**근거:** [app/security.py](../app/security.py) · [app/routers/auth.py](../app/routers/auth.py) · [tests/test_auth_signup.py](../tests/test_auth_signup.py) · [tests/test_security.py](../tests/test_security.py)

**확인·시연:** len(password)와 len(password.encode('utf-8'))의 차이를 예시로 설명합니다.

<a id="q045"></a>

### Q045. 이메일 대소문자·공백·유니코드 중복은 어떻게 처리하나요?

**답안:** NFKC 정규화 후 앞뒤 공백을 제거하고 소문자로 저장·조회합니다. 가입 시 이메일 형식을 검증하고 DB UNIQUE 제약으로 같은 정규화 이메일의 중복을 막습니다. 메일 발송이나 주소 소유 확인은 구현하지 않았습니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/models/user.py](../app/models/user.py) · [tests/test_auth_signup.py](../tests/test_auth_signup.py)

**확인·시연:** 같은 이메일의 대문자·공백 변형으로 가입과 로그인을 비교합니다.

<a id="q046"></a>

### Q046. 탈퇴·삭제된 사용자나 변조 쿠키는 어떻게 처리하나요?

**답안:** get_current_user가 세션 user_id에 해당하는 DB 사용자를 찾지 못하면 세션을 비우고 비로그인으로 처리합니다. User의 AUTOINCREMENT는 삭제된 ID가 새 사용자에게 재사용되는 위험을 줄입니다. 변조 서명 쿠키를 로그인으로 인정하지 않는 테스트도 있습니다. 사용자 삭제 API 자체는 없습니다.

**근거:** [app/dependencies.py](../app/dependencies.py) · [app/models/user.py](../app/models/user.py) · [tests/test_auth_edge_cases.py](../tests/test_auth_edge_cases.py)

**확인·시연:** 삭제 사용자 세션·다음 가입 ID·변조 쿠키 테스트의 기대 결과를 설명합니다.

<a id="q047"></a>

### Q047. 로그아웃은 기존 쿠키의 재사용까지 차단하나요?

**답안:** 로그아웃 요청은 현재 클라이언트 세션을 비우고 204를 반환합니다. 다만 서버 저장형 세션 목록이나 토큰 폐기 목록은 없어 과거에 복사한 유효 서명 쿠키를 즉시 무효화하는 기능까지 구현한 것은 아닙니다. 전역 세션 폐기·기기별 세션 관리는 운영 보강 과제입니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/main.py](../app/main.py) · [tests/test_auth_logout.py](../tests/test_auth_logout.py)

**확인·시연:** 정상 로그아웃 뒤 현재 브라우저의 보호 API 접근이 401인지 확인하고 전역 폐기 미구현을 구분합니다.

<a id="q048"></a>

### Q048. 사용자 ID를 요청에 넣어 타인의 기록을 볼 수 있나요?

**답안:** 웹 API는 본문·쿼리의 user_id를 인가 근거로 쓰지 않습니다. require_login으로 확인된 사용자 ID가 기록 조회와 AI 문맥 조회의 필터가 됩니다. DB 파일을 직접 읽는 운영 스크립트는 별도 파일 접근 권한에 의존합니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [tests/test_chat_api.py](../tests/test_chat_api.py) · [tests/test_ui.py](../tests/test_ui.py)

**확인·시연:** 타인 ID를 쿼리에 넣어도 결과가 본인 기록에 고정되는지 확인합니다.

<a id="q049"></a>

### Q049. 질문이나 AI 답변에 HTML이 들어오면 어떻게 되나요?

**답안:** UI는 질문·답변·오류를 textContent로 넣어 HTML 문자열을 실행하지 않습니다. 페이지에는 script-src 'self' 등의 CSP와 nosniff 헤더도 설정합니다. 이 방어는 표시 경로에 대한 것이며 모든 종류의 웹 공격을 해결한다는 의미는 아닙니다.

**근거:** [app/static/js/chat.js](../app/static/js/chat.js) · [app/static/js/history.js](../app/static/js/history.js) · [app/routers/pages.py](../app/routers/pages.py)

**확인·시연:** script 태그 같은 문자열이 화면에서 텍스트로 보이는지 테스트 환경에서 확인합니다.

<a id="q050"></a>

### Q050. 로그에 민감한 내용을 남기지 않으려면 무엇을 했나요?

**답안:** 채팅 이벤트에는 질문·답변 원문과 API 키를 넣지 않고 단계·사용자·상태를 기록합니다. 로그인 실패의 이메일 입력은 형식 검증을 거쳐 잘못된 값·줄바꿈 등은 <invalid>로 마스킹하지만 올바른 이메일은 로그에 남습니다. 따라서 개인정보가 전혀 없다고 말하지 않고 운영 로그의 보관·접근 관리도 필요하다고 설명합니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py) · [tests/test_auth_edge_cases.py](../tests/test_auth_edge_cases.py)

**확인·시연:** 비밀번호 미기록·이메일 오입력 마스킹·AI 실패 사유 로그 테스트를 확인합니다.

## API 계약과 오류 · Q051~Q060

<a id="q051"></a>

### Q051. 회원가입·로그인·로그아웃의 요청·응답 예시를 말해 주세요.

**답안:** 가입과 로그인은 {"email":"creator@example.com","password":"shorts1234"}를 보내고 {"id":1,"email":"creator@example.com"} 같은 사용자 응답을 받습니다. 가입은 201, 로그인은 200이며 로그인 성공으로 세션 쿠키가 설정됩니다. 로그아웃은 로그인 쿠키를 포함한 POST이고 204·빈 본문입니다. 값은 설명용 예시입니다.

**근거:** [README.md](../README.md) · [app/routers/auth.py](../app/routers/auth.py)

**확인·시연:** /docs의 auth 항목과 브라우저 네트워크 응답을 확인합니다.

<a id="q052"></a>

### Q052. 채팅 API의 최소 요청과 정상 응답은 무엇인가요?

**답안:** 최소 요청은 {"mode":"q3","message":"금리 인하 주제 지금 올려도 돼?"}이며 keyword는 선택입니다. 성공 응답은 {"chat_id":1,"answer":"추천 내용"} 형식으로 DB 저장 후 200을 반환합니다. 로그인 쿠키가 필요하며 answer 문구는 모델 응답에 따라 달라집니다.

**근거:** [README.md](../README.md) · [app/routers/chat.py](../app/routers/chat.py)

**확인·시연:** 실제 요청 JSON과 반환된 chat_id/answer를 저장 기록과 대조합니다.

<a id="q053"></a>

### Q053. 기록 API 응답에는 어떤 필드가 포함되나요?

**답안:** id, mode, question, answer, status, created_at의 6개 필드를 반환합니다. user_id, scenario_version, password_hash는 공개 기록 응답에 포함하지 않습니다. 응답 목록은 최신순이며 기록이 없으면 빈 배열입니다.

**근거:** [app/routers/logs.py](../app/routers/logs.py) · [tests/test_ui.py](../tests/test_ui.py) · [README.md](../README.md)

**확인·시연:** GET /api/me/chats의 응답 키 집합과 [] 사례를 확인합니다.

<a id="q054"></a>

### Q054. 왜 401·409·422를 구분하나요?

**답안:** 401은 로그인 필요나 인증정보 불일치, 409는 중복 이메일로 자원 생성이 충돌하는 경우, 422는 요청 입력 검증 실패에 사용합니다. 상태코드를 구분하면 UI와 평가자가 실패 원인을 예측할 수 있습니다. 본문 error 코드와 한국어 message도 함께 확인합니다.

**근거:** [app/errors.py](../app/errors.py) · [app/routers/auth.py](../app/routers/auth.py) · [app/dependencies.py](../app/dependencies.py)

**확인·시연:** 비로그인·중복가입·빈 질문의 응답을 나란히 비교합니다.

<a id="q055"></a>

### Q055. AI 오류는 왜 502나 504이고 DB 오류는 500인가요?

**답안:** AI 공급자 오류는 upstream 사용 실패로 502 AI_ERROR, 타임아웃은 504 AI_TIMEOUT으로 응답합니다. 대화 저장 SQLAlchemy 오류는 우리 저장 경계의 실패로 500 DB_ERROR입니다. 단 기록 조회 DB 오류는 현재 503과 detail로 구현되어 있어 저장 오류와 구분합니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** 모의 AI 실패·타임아웃·DB commit 실패의 상태코드를 확인합니다.

<a id="q056"></a>

### Q056. Swagger 문서에는 화면 페이지도 표시되나요?

**답안:** /docs에는 등록된 API 라우트와 Pydantic 기반 스키마가 표시됩니다. HTML 페이지 라우터는 include_in_schema=False라 페이지 경로를 API 명세에 포함하지 않습니다. 채팅 성공 응답은 명시적 response_model이 없어 상세 출력 스키마 보강 여지가 있습니다.

**근거:** [app/routers/pages.py](../app/routers/pages.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/main.py](../app/main.py)

**확인·시연:** 실행 중 /docs의 API 목록과 실제 HTML 페이지 경로를 비교합니다.

<a id="q057"></a>

### Q057. 왜 내 기록 API에는 user_id 경로가 없나요?

**답안:** 조회 대상을 현재 로그인 사용자로 한정해 호출자가 다른 사용자의 ID를 선택할 필요를 없앴습니다. /api/me/chats라는 경로는 본인 자원이라는 의미도 드러냅니다. 관리자용 타인 기록 조회 API와 관리자 역할 모델은 구현되어 있지 않습니다.

**근거:** [app/routers/logs.py](../app/routers/logs.py) · [app/dependencies.py](../app/dependencies.py) · [README.md](../README.md)

**확인·시연:** 라우터 입력에는 limit만 있고 사용자 ID는 인증에서 얻는 것을 확인합니다.

<a id="q058"></a>

### Q058. 기록 limit과 정렬 방식은 어떻게 정했나요?

**답안:** limit은 기본 20, 최소 1, 최대 100으로 응답 크기를 제한합니다. created_at DESC 다음 id DESC로 정렬해 같은 시각에도 순서를 정합니다. offset·cursor 페이지네이션과 전체 건수 조회는 아직 없습니다.

**근거:** [app/routers/logs.py](../app/routers/logs.py) · [scripts/check_logs.sql](../scripts/check_logs.sql) · [tests/test_ui.py](../tests/test_ui.py)

**확인·시연:** limit=0·101의 422와 정상 limit=1 응답을 비교합니다.

<a id="q059"></a>

### Q059. 클라이언트 검증이 있는데 서버 검증이 또 필요한가요?

**답안:** UI는 즉시 안내를 위한 것이고 직접 HTTP 호출로 우회할 수 있습니다. 서버의 Pydantic 검증이 빈 질문·잘못된 타입·허용되지 않은 mode를 차단해야 AI 비용과 잘못된 저장을 막을 수 있습니다. 실패 입력에서 AI 호출과 대화 저장이 일어나지 않는 테스트가 있습니다.

**근거:** [app/static/js/chat.js](../app/static/js/chat.js) · [app/routers/chat.py](../app/routers/chat.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** 브라우저를 거치지 않은 API 요청으로 빈 message를 보내 확인합니다.

<a id="q060"></a>

### Q060. 오류 응답 형식이 완전히 통일되어 있나요?

**답안:** 완전히 통일되어 있지는 않습니다. 인증·입력·채팅의 주요 오류는 error/message지만 기록 조회의 HTTPException은 detail이고 일부 기본 HTTP 오류도 FastAPI 형식을 유지합니다. common.js가 이를 함께 처리하며 앞으로 공통 응답 계약으로 정리할 수 있습니다.

**근거:** [app/errors.py](../app/errors.py) · [app/routers/logs.py](../app/routers/logs.py) · [app/static/js/common.js](../app/static/js/common.js)

**확인·시연:** 기록 조회 503 detail과 채팅 500 error/message를 비교해 차이를 설명합니다.

## DB 설계와 저장 · Q061~Q070

<a id="q061"></a>

### Q061. 왜 SQLite와 SQLAlchemy를 선택했나요?

**답안:** 이 규모의 과제에서 별도 DB 서버 없이 사용자·대화 저장을 시연하기 쉬운 구조입니다. SQLAlchemy는 모델·세션·외래키를 코드로 관리해 테이블 구조와 사용 경계를 명확히 합니다. 대규모 동시 쓰기를 해결한 설계로 설명하지 않으며 트래픽 증가 시 DB 전환과 측정이 필요합니다.

**근거:** [app/database.py](../app/database.py) · [app/models/user.py](../app/models/user.py) · [app/models/chat.py](../app/models/chat.py) · [deploy/ai-chatbot.service](../deploy/ai-chatbot.service)

**확인·시연:** 기본 DB URL과 worker 1 설정을 연결해 선택의 범위를 설명합니다.

<a id="q062"></a>

### Q062. users와 chats를 따로 둔 이유는 무엇인가요?

**답안:** 사용자 정보는 한 계정당 하나이고 대화는 사용자마다 여러 건 생기므로 수명이 다른 데이터를 분리했습니다. chats.user_id 외래키로 소유자를 연결하면 사용자별 조회 조건을 만들 수 있습니다. 별도 대화방 테이블은 없어 현재 문맥은 같은 사용자의 최근 기록을 기준으로 합니다.

**근거:** [app/models/user.py](../app/models/user.py) · [app/models/chat.py](../app/models/chat.py) · [app/routers/chat.py](../app/routers/chat.py)

**확인·시연:** ERD의 1:N 관계와 문맥 조회 필터를 보여줍니다.

<a id="q063"></a>

### Q063. 주요 DB 필드의 자료형과 NULL 조건을 설명해 주세요.

**답안:** id/user_id/scenario_version은 정수, email/password_hash/mode/status는 길이를 선언한 문자열, question/answer는 Text입니다. 생성 시각은 DateTime과 DB 기본 CURRENT_TIMESTAMP를 씁니다. answer만 AI 실패를 표현하도록 NULL을 허용하고 다른 주요 필드는 NOT NULL입니다. SQLite의 VARCHAR 길이 선언만으로 입력 길이가 강제된다고 말하면 안 됩니다.

**근거:** [app/models/user.py](../app/models/user.py) · [app/models/chat.py](../app/models/chat.py) · [app/routers/chat.py](../app/routers/chat.py)

**확인·시연:** 모델 타입과 입력 validator를 나누어 설명합니다.

<a id="q064"></a>

### Q064. 외래키 제약은 SQLite에서도 실제로 적용하나요?

**답안:** create_db_engine의 connect 이벤트가 연결마다 PRAGMA foreign_keys=ON을 실행합니다. 그 상태에서 chats.user_id는 존재하는 users.id를 참조해야 합니다. 웹 API도 세션 사용자를 확인하지만 애플리케이션 확인과 DB 무결성 제약은 서로 다른 방어입니다.

**근거:** [app/database.py](../app/database.py) · [app/models/chat.py](../app/models/chat.py) · [tests/test_database.py](../tests/test_database.py)

**확인·시연:** DB 엔진의 connect 이벤트와 외래키 관련 테스트를 보여줍니다.

<a id="q065"></a>

### Q065. 인덱스와 유일키는 어디에 적용했나요?

**답안:** users.email은 unique=True와 index=True로 이메일 중복 방지 및 조회를 지원합니다. chats.user_id는 사용자별 조회에 맞춰 index=True입니다. created_at/id를 포함한 복합 인덱스나 실행 계획 기반 최적화는 아직 없어 데이터가 커지면 측정 후 검토합니다.

**근거:** [app/models/user.py](../app/models/user.py) · [app/models/chat.py](../app/models/chat.py) · [app/routers/logs.py](../app/routers/logs.py)

**확인·시연:** 모델 인덱스 선언과 실제 WHERE·ORDER BY 조건을 연결합니다.

<a id="q066"></a>

### Q066. AI 실패 기록에서 answer가 NULL인 이유는 무엇인가요?

**답안:** AI가 유효한 답변을 주지 못했음을 성공 답변과 구분하려고 NULL로 저장합니다. status를 timeout 또는 error로 함께 기록해 기록 화면에서 실패 종류를 표시합니다. 오류 안내 문구를 AI 답변으로 저장하면 이후 성공 문맥에 잘못 섞일 수 있어 경계를 유지합니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/models/chat.py](../app/models/chat.py) · [app/static/js/history.js](../app/static/js/history.js)

**확인·시연:** 실패 행의 answer/status와 문맥 조회 success 조건을 확인합니다.

<a id="q067"></a>

### Q067. 왜 DB commit 뒤에만 채팅 성공을 반환하나요?

**답안:** 사용자에게 성공이라고 알린 답변이 기록에도 남는다는 계약을 지키기 위해서입니다. add·flush로 chat_id를 얻고 commit을 마친 뒤 200을 반환합니다. commit 실패 시 rollback과 500을 반환하며 AI 답변이 이미 생성됐더라도 저장 성공으로 처리하지 않습니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** commit 실패 테스트의 500·행 미저장·다음 요청 회복을 보여줍니다.

<a id="q068"></a>

### Q068. scenario_version은 왜 필요하며 구 기록은 어떻게 처리하나요?

**답안:** 같은 q4/q5 값의 기능 의미가 과거와 현재 번호 체계에서 달라 구분 값이 필요합니다. 새 기록은 버전 2이고 구 테이블에 열이 없으면 기본 1로 추가합니다. 기록 API는 버전 1·3의 q4/q5/q6를 현재 q3/q4/q5로 변환해 보여주며 원본 mode를 덮어쓰지 않습니다.

**근거:** [app/database.py](../app/database.py) · [app/models/chat.py](../app/models/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [tests/test_mode_integration.py](../tests/test_mode_integration.py)

**확인·시연:** 스키마 열 추가와 조회 시 번호 변환 코드를 구분해 보여줍니다.

<a id="q069"></a>

### Q069. DB 생성 시각과 화면 시각은 어떤 시간대를 사용하나요?

**답안:** 모델은 DB CURRENT_TIMESTAMP로 UTC 시각을 저장합니다. SQLite에서 반환된 offset 없는 시각은 화면에서 서버 시각 표시로 안내하며 한국 시간 변환이 완전히 통일된 구조는 아닙니다. 데이터랩 비교의 날짜는 별도로 Asia/Seoul을 사용합니다.

**근거:** [app/models/chat.py](../app/models/chat.py) · [app/static/js/history.js](../app/static/js/history.js) · [app/services/trend.py](../app/services/trend.py) · [README.md](../README.md)

**확인·시연:** DB 시각, 기록 API 문자열, 화면의 서버 시각 표시를 비교합니다.

<a id="q070"></a>

### Q070. DB 확인 스크립트는 데이터를 변경하거나 새 파일을 만들 수 있나요?

**답안:** check_logs.py는 mode=ro URI로 기존 DB를 읽기 전용 연결합니다. 조회 SQL은 user_id/limit 바인딩을 사용하고 존재하지 않는 DB는 오류로 처리합니다. 이 도구는 대화 내용 원문을 출력하므로 시연에는 본인 테스트 데이터와 적절한 파일 접근 권한을 사용합니다.

**근거:** [scripts/check_logs.py](../scripts/check_logs.py) · [scripts/check_logs.sql](../scripts/check_logs.sql) · [tests/test_ui.py](../tests/test_ui.py)

**확인·시연:** 존재하는 테스트 DB 조회와 없는 DB 경로의 실패를 비교합니다.

## LLM·트렌드·비동기 처리 · Q071~Q080

<a id="q071"></a>

### Q071. LLM에는 어떤 메시지 묶음을 보내나요?

**답안:** system 프롬프트 뒤에 본인 최근 성공 대화 최대 5쌍을 user/assistant 순서로 넣고 현재 user 질문을 마지막에 붙입니다. 과거 기록은 최신 5건을 조회한 후 시간순으로 역전해 메시지를 구성합니다. 실패 기록과 타인 기록은 제외합니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/services/llm.py](../app/services/llm.py) · [tests/test_chat.py](../tests/test_chat.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** build_messages의 순서와 최대 11개 대화 메시지에 system 1개가 추가되는 payload를 설명합니다.

<a id="q072"></a>

### Q072. 왜 최근 성공 대화 5쌍만 사용하나요?

**답안:** 전체 기록을 전송하면 입력 크기·비용·지연이 커지므로 제한된 최근 맥락을 사용하도록 설계했습니다. 성공하고 답변이 있는 기록만 넣어 실패 안내가 대화 문맥에 섞이지 않게 합니다. 5쌍은 구현상의 제한이며 최적 성능을 실험으로 증명한 수치는 아닙니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [tests/test_chat.py](../tests/test_chat.py)

**확인·시연:** limit(5)와 success·answer 조건, 오래된 기록 제외 테스트를 확인합니다.

<a id="q073"></a>

### Q073. AI 호출은 스트리밍인가요, 자동 재시도는 있나요?

**답안:** 현재는 한 번의 비스트리밍 HTTP 요청으로 전체 답변을 받은 후 저장·응답합니다. 자동 재시도, 작업 큐, SSE 토큰 스트리밍은 구현하지 않았습니다. 이를 추가한다면 비용 중복·취소·저장 완료 시점·실패 기록 계약을 함께 설계해야 합니다.

**근거:** [app/services/llm.py](../app/services/llm.py) · [app/routers/chat.py](../app/routers/chat.py) · [tests/test_llm.py](../tests/test_llm.py)

**확인·시연:** client.post 1회와 stream 옵션·재시도 루프가 없는 코드를 보여줍니다.

<a id="q074"></a>

### Q074. 빈 AI 답변이나 잘못된 응답 형식은 어떻게 처리하나요?

**답안:** HTTP 성공이라도 choices[0].message.content를 읽을 수 없거나 문자열이 비면 AIServiceError로 처리합니다. 정상으로 저장·반환하지 않고 error/NULL 기록과 502 안내로 연결됩니다. max_completion_tokens는 4000으로 설정되어 있지만 항상 답변 품질이나 길이가 보장되는 것은 아닙니다.

**근거:** [app/services/llm.py](../app/services/llm.py) · [tests/test_llm.py](../tests/test_llm.py) · [app/routers/chat.py](../app/routers/chat.py)

**확인·시연:** 빈 content·비정상 JSON 구조의 모의 공급자 응답 테스트를 확인합니다.

<a id="q075"></a>

### Q075. 네이버 API 키가 없거나 조회에 실패하면 어떻게 되나요?

**답안:** 트렌드 서비스는 빈 결과를 반환하고 정해진 사유·예외 유형을 로그로 남깁니다. 뉴스가 없거나 비교가 unknown이면 프롬프트는 데이터 부족을 알리도록 합니다. 이것은 LLM 키 부재와 다르며 LLM 키가 없으면 AIServiceError로 실패합니다.

**근거:** [app/services/trend.py](../app/services/trend.py) · [app/services/llm.py](../app/services/llm.py) · [app/services/scenarios/q1.py](../app/services/scenarios/q1.py) · [app/services/scenarios/q3.py](../app/services/scenarios/q3.py)

**확인·시연:** 네이버 미설정과 LLM 미설정의 서로 다른 동작을 모의 환경에서 비교합니다.

<a id="q076"></a>

### Q076. 뉴스 목록을 인기 순위나 전체 언급량으로 볼 수 있나요?

**답안:** 볼 수 없습니다. search_news는 sort=date와 제한된 display 수로 최신순 일부 검색 결과를 가져옵니다. get_hot_issues라는 이름도 실제 인기 순위를 측정했다는 뜻은 아니며 프롬프트에서 그 한계를 명시합니다.

**근거:** [app/services/trend.py](../app/services/trend.py) · [app/services/scenarios/q1.py](../app/services/scenarios/q1.py) · [app/services/scenarios/q3.py](../app/services/scenarios/q3.py)

**확인·시연:** 검색 파라미터와 프롬프트의 인기·언급량 제한 문구를 확인합니다.

<a id="q077"></a>

### Q077. 검색 추이를 왜 14일 한 번의 요청으로 비교하나요?

**답안:** 한국 시간 어제까지 완료된 14일을 같은 데이터랩 요청으로 받아 동일 척도에서 최근 7일과 이전 7일 평균을 비교합니다. 오늘은 아직 완료되지 않아 제외합니다. 두 구간을 각각 정규화한 별도 요청으로 비교하는 문제를 줄이는 구현이며 장기간 계절성 분석은 아닙니다.

**근거:** [app/services/trend.py](../app/services/trend.py) · [tests/test_trend.py](../tests/test_trend.py)

**확인·시연:** compare_periods의 start/end와 단일 _request_datalab 호출을 설명합니다.

<a id="q078"></a>

### Q078. rising·falling·peak·stable·unknown의 차이는 무엇인가요?

**답안:** 최근 평균이 이전 평균의 1.2배 이상이면 rising, 0.8배 이하이면 falling입니다. 그 사이에서 최근 평균 80 이상이면 peak 후보, 그 외는 stable이며 이전 평균이 0이고 최근이 양수면 rising입니다. 14일 누락·잘못된 값·모든 값 0 등은 unknown으로 처리하며 실제 정점을 확정하는 통계 모델은 아닙니다.

**근거:** [app/services/trend.py](../app/services/trend.py) · [tests/test_trend.py](../tests/test_trend.py)

**확인·시연:** 경계값·누락 데이터·전 기간 0의 테스트 사례를 확인합니다.

<a id="q079"></a>

### Q079. 뉴스의 악성 지시문이나 모델의 사실 지어내기를 어떻게 줄이나요?

**답안:** 외부 자료를 reference_data 등으로 분리하고 자료 속 문장을 지시로 따르지 말라고 system에 명시합니다. 자료 부재·상대지수·일부 뉴스라는 한계를 설명하고 출처·수치를 지어내지 않도록 합니다. 이는 프롬프트 수준의 완화이며 공격 방어나 사실 정확성을 보장하는 별도 검증기는 없습니다.

**근거:** [app/services/scenarios/q1.py](../app/services/scenarios/q1.py) · [app/services/scenarios/q2.py](../app/services/scenarios/q2.py) · [app/services/scenarios/q3.py](../app/services/scenarios/q3.py) · [app/services/scenarios/common.py](../app/services/scenarios/common.py)

**확인·시연:** 외부 자료 경계와 자료 부족 규칙을 보여주고 실제 출력의 근거 확인 필요성을 설명합니다.

<a id="q080"></a>

### Q080. 동기 네이버 요청이 async 채팅 처리에 미치는 영향은 어떻게 줄였나요?

**답안:** requests 기반 조회는 시나리오에서 asyncio.to_thread로 실행하고 독립 조회를 asyncio.gather로 묶습니다. 동기 네트워크 호출이 이벤트 루프를 직접 막는 문제를 줄이려는 구현입니다. 동기 SQLAlchemy 조회·저장은 async 라우터 안에 남아 있어 모든 블로킹 작업이 제거된 구조는 아닙니다.

**근거:** [app/services/scenarios/q1.py](../app/services/scenarios/q1.py) · [app/services/scenarios/q2.py](../app/services/scenarios/q2.py) · [app/services/scenarios/q3.py](../app/services/scenarios/q3.py) · [app/routers/chat.py](../app/routers/chat.py)

**확인·시연:** to_thread/gather 호출과 동기 DB 사용의 남은 경계를 함께 설명합니다.

## 시연·테스트·배포·운영 · Q081~Q090

<a id="q081"></a>

### Q081. 평가 때 가장 먼저 어떤 순서로 시연하나요?

**답안:** 실제 app.main:app의 /health 확인 뒤 비로그인 차단→새 계정 가입→로그인→질문→화면 답변→내 기록 조회를 보여줍니다. 마지막으로 입력 오류와 모의 AI 실패 처리, README 구조·API·ERD·팀 역할, Git PR 이력을 제시합니다. 실제 키·배포 주소·DB 경로는 준비된 평가 환경에서 확인합니다.

**근거:** [README.md](../README.md) · [docs/DEPLOY.md](../docs/DEPLOY.md) · [scripts/check_connection.py](../scripts/check_connection.py)

**확인·시연:** 우선순위 문서의 시연 순서를 따라 성공 흐름부터 확인합니다.

<a id="q082"></a>

### Q082. 실제 앱과 UI 데모는 어떻게 구분하나요?

**답안:** 실제 진입점은 app.main:app으로 인증·LLM·SQLite 경로를 사용합니다. dev.demo_app:app은 고정 예시 답변과 메모리 DB를 쓰는 UI 점검용 앱입니다. 데모는 화면·오류 안내를 보여줄 수 있지만 실제 AI 연결·분석 품질·운영 저장의 증거로 대신할 수 없습니다.

**근거:** [app/main.py](../app/main.py) · [dev/demo_app.py](../dev/demo_app.py) · [README.md](../README.md)

**확인·시연:** 시작 명령의 모듈 경로와 화면 데모 표시를 확인합니다.

<a id="q083"></a>

### Q083. 실제 AI 연결은 어떤 도구로 확인하나요?

**답안:** scripts.check_connection은 임시 DB로 가입·로그인·Q3 AI 호출·기록 일치 검증을 수행합니다. 실제 네이버·LLM 키를 사용하는 호출이라 사용량이 발생할 수 있고 일반 pytest와 구분합니다. TestClient 기반이므로 외부 VM 네트워크 접속 검증은 별도로 필요합니다.

**근거:** [scripts/check_connection.py](../scripts/check_connection.py) · [docs/DEPLOY.md](../docs/DEPLOY.md)

**확인·시연:** 평가 환경의 키 설정을 확인한 뒤 python -m scripts.check_connection을 실행하고 외부 브라우저 시연도 합니다.

<a id="q084"></a>

### Q084. 단위·통합 테스트는 어떤 중요한 경계를 다루나요?

**답안:** 인증·입력·쿠키·모델·트렌드·LLM 응답 정규화와 UI 연동 테스트가 있습니다. 채팅 테스트는 사용자 격리·5쌍 문맥·실패 저장·DB rollback·모드 연결을 확인합니다. 브라우저 화면 검사는 별도 도구이며 테스트가 있다는 사실과 이번 실행 성공 여부는 구분합니다.

**근거:** [tests/test_chat_api.py](../tests/test_chat_api.py) · [tests/test_llm.py](../tests/test_llm.py) · [tests/test_auth_edge_cases.py](../tests/test_auth_edge_cases.py) · [tests/test_mode_integration.py](../tests/test_mode_integration.py) · [dev/check_ui_browser.py](../dev/check_ui_browser.py)

**확인·시연:** 핵심 테스트 이름·assert를 보여주고 평가 환경에서 pytest -q 결과를 확인합니다.

<a id="q085"></a>

### Q085. 테스트 실행이 실제 DB와 유료 API를 건드리지 않게 했나요?

**답안:** conftest가 앱 import 전에 테스트 SECRET_KEY·메모리 DB 설정을 적용하고 네이버·LLM 키를 빈 값으로 고정합니다. 각 테스트의 DB 세션은 임시 파일로 override하며 외부 성공 응답은 모의 처리합니다. 따라서 일반 pytest 결과는 실제 공급자 응답 품질을 증명하지 않습니다.

**근거:** [tests/conftest.py](../tests/conftest.py) · [tests/test_chat_api.py](../tests/test_chat_api.py) · [tests/test_llm.py](../tests/test_llm.py)

**확인·시연:** 환경 초기화와 override_get_db·monkeypatch 사용 지점을 확인합니다.

<a id="q086"></a>

### Q086. 현재 확인 환경에서 테스트가 통과했나요?

**답안:** 이번 문서 작성 중 pytest -q를 실행했지만 requests 미설치로 conftest import 단계에서 중단되었습니다. 테스트는 수집되지 않아 통과 건수나 기능 정상 동작을 확인했다고 답할 수 없습니다. 평가 환경에서 requirements 설치·의존성 점검 뒤 재실행하고 결과를 제시해야 합니다.

**근거:** [requirements.txt](../requirements.txt) · [tests/conftest.py](../tests/conftest.py) · [app/services/trend.py](../app/services/trend.py)

**확인·시연:** python -m pip install -r requirements.txt, python -m pip check, python -m pytest -q 순서로 평가 환경을 점검합니다.

<a id="q087"></a>

### Q087. 프로세스 재시작과 서버 재부팅에는 어떻게 대응하나요?

**답안:** 제공된 systemd 서비스는 Uvicorn을 worker 1로 실행하고 Restart=always, RestartSec=3으로 재시작합니다. enable 설정으로 부팅 시 서비스 시작을 구성할 수 있습니다. 이는 배포 파일의 정책이며 실제 설치·가동 여부는 systemctl status로 확인해야 합니다.

**근거:** [deploy/ai-chatbot.service](../deploy/ai-chatbot.service) · [docs/DEPLOY.md](../docs/DEPLOY.md)

**확인·시연:** 배포 서버에서 systemctl status ai-chatbot과 /health 응답을 확인합니다.

<a id="q088"></a>

### Q088. VM 서비스가 외부에서 안 열리면 무엇부터 확인하나요?

**답안:** 프로세스 상태·journal 로그·서버 내부 /health를 먼저 확인합니다. 다음으로 0.0.0.0 바인딩, 포트 8000, 클라우드 보안 그룹과 서버 방화벽, 실제 공인 IP를 확인합니다. 내부 TestClient 성공만으로 외부 접속까지 성공했다고 결론내리지 않습니다.

**근거:** [deploy/ai-chatbot.service](../deploy/ai-chatbot.service) · [docs/DEPLOY.md](../docs/DEPLOY.md)

**확인·시연:** 서버 내부 curl과 평가 PC의 외부 curl·브라우저 결과를 구분해 비교합니다.

<a id="q089"></a>

### Q089. 브라우저 대기 시간이 끝나면 서버 처리도 취소되나요?

**답안:** 현재 AbortController는 브라우저 fetch 대기를 중단하지만 서버 작업 취소·DB 저장 중단을 보장하지 않습니다. 이미 진행 중인 작업이 나중에 저장될 수 있어 UI는 내 기록 확인 후 재시도를 안내합니다. 요청 중복 방지용 idempotency key는 아직 없습니다.

**근거:** [app/static/js/common.js](../app/static/js/common.js) · [app/routers/chat.py](../app/routers/chat.py)

**확인·시연:** 브라우저 시간 초과 안내와 이후 내 기록 확인 절차를 설명합니다.

<a id="q090"></a>

### Q090. 동시 요청·처리시간·비용에는 어떤 한계가 있나요?

**답안:** UI는 응답 대기 중 전송을 막지만 다른 탭·직접 API의 동시 호출까지 제한하지 않습니다. 최근 5쌍·일부 뉴스·토큰 한도는 크기 제한이고 사용자별 요청 제한·총 처리 deadline·정밀 비용 집계는 없습니다. worker 1과 SQLite 구성에서 실제 부하 측정 없이 확장성을 보장할 수 없습니다.

**근거:** [app/static/js/chat.js](../app/static/js/chat.js) · [app/services/llm.py](../app/services/llm.py) · [app/services/scenarios/q2.py](../app/services/scenarios/q2.py) · [deploy/ai-chatbot.service](../deploy/ai-chatbot.service)

**확인·시연:** 현재 크기·대기 제한과 미구현된 서버 동시성·비용 정책을 나누어 설명합니다.

## 개인 기여·협업·개선·마무리 · Q091~Q100

<a id="q091"></a>

### Q091. A 담당자의 핵심 기여는 무엇인가요?

**답안:** README 기준 A 김준택은 설정·DB 기반, User·bcrypt, 가입·로그인·로그아웃과 인증 의존성을 담당했습니다. 모드 통합 및 배포 서비스·가이드·README 기여도 포함되어 있습니다. 발표자는 본인 작업과 팀 전체 기여를 구분하고 파일별 이력으로 근거를 보완합니다.

**근거:** [README.md](../README.md) · [app/routers/auth.py](../app/routers/auth.py) · [app/security.py](../app/security.py) · [app/dependencies.py](../app/dependencies.py) · [deploy/ai-chatbot.service](../deploy/ai-chatbot.service)

**확인·시연:** feature/auth와 PR #2, 배포 문서 PR #6 관련 이력을 보여줍니다.

<a id="q092"></a>

### Q092. B 담당자의 핵심 기여는 무엇인가요?

**답안:** README 기준 B 이지영은 네이버 뉴스·데이터랩 수집, 추이 비교, Q1~Q3 프롬프트를 담당했습니다. PR #5의 1차 통합 기여도 정리되어 있습니다. 수집값은 검색 상대지수·최신순 일부 뉴스라는 한계를 함께 설명합니다.

**근거:** [README.md](../README.md) · [app/services/trend.py](../app/services/trend.py) · [app/services/scenarios/q1.py](../app/services/scenarios/q1.py) · [app/services/scenarios/q2.py](../app/services/scenarios/q2.py) · [app/services/scenarios/q3.py](../app/services/scenarios/q3.py)

**확인·시연:** feature/trend와 PR #5, 관련 서비스 파일 이력을 확인합니다.

<a id="q093"></a>

### Q093. C 담당자의 핵심 기여는 무엇인가요?

**답안:** README 기준 C 정지환은 Chat 모델, 채팅 라우터, LLM 클라이언트, 최근 대화 문맥과 실패 저장·rollback을 담당했습니다. 현재 화면 Q4·Q5의 프롬프트 파일은 q5.py·q6.py입니다. PR #3과 대응 파일로 통합 결과를 설명합니다.

**근거:** [README.md](../README.md) · [app/models/chat.py](../app/models/chat.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/services/llm.py](../app/services/llm.py) · [docs/C_AGENT_HANDOFF.md](../docs/C_AGENT_HANDOFF.md)

**확인·시연:** feature/chat과 PR #3, 빈 AI 응답·실패 저장 관련 커밋을 확인합니다.

<a id="q094"></a>

### Q094. D 담당자의 핵심 기여는 무엇인가요?

**답안:** README 기준 D 김정현은 Jinja2·반응형 UI, 인증·채팅·내 기록 화면, 기록 조회 API와 DB 확인 도구를 담당했습니다. UI 데모·브라우저 검사와 공통 API 오류 안내도 포함됩니다. 화면은 A 인증·C 채팅·D 기록 API와 연결되고 UI 데모는 실제 AI 증거와 구분합니다.

**근거:** [README.md](../README.md) · [app/ui.py](../app/ui.py) · [app/routers/logs.py](../app/routers/logs.py) · [app/static/js/chat.js](../app/static/js/chat.js) · [scripts/check_logs.py](../scripts/check_logs.py) · [docs/D_HANDOFF.md](../docs/D_HANDOFF.md)

**확인·시연:** feature/ui와 PR #4, 본인 담당 화면·조회·검증 파일을 보여줍니다.

<a id="q095"></a>

### Q095. 팀 간 인터페이스와 통합은 어떻게 맞췄나요?

**답안:** A의 require_login/get_db를 C 채팅과 D 기록 조회에 주입하고 B의 자료·프롬프트를 C의 LLM 호출과 연결했습니다. D UI는 같은 출처의 A/C/D API를 호출하고 main.py가 실제 Chat 모델로 install_ui를 한 번 등록합니다. 모드 번호와 API 계약은 SCENARIOS 문서·통합 테스트로 맞춥니다.

**근거:** [app/main.py](../app/main.py) · [app/ui.py](../app/ui.py) · [app/routers/chat.py](../app/routers/chat.py) · [docs/SCENARIOS.md](../docs/SCENARIOS.md) · [tests/test_mode_integration.py](../tests/test_mode_integration.py)

**확인·시연:** 의존성 주입·모드 대응·중복 라우터 검사 지점을 순서대로 설명합니다.

<a id="q096"></a>

### Q096. 평가 기준 중 가장 설명을 조심해야 할 부분은 무엇인가요?

**답안:** DB 엔진·모델은 분리했지만 라우터 쿼리까지 분리한 리포지토리 구조는 아닙니다. 오류 형식 일부, 총 처리 deadline, 요청 ID, 페이지네이션·보관·삭제·호출량 제한도 미구현입니다. 테스트·실제 API·외부 배포의 이번 검증 상태를 나누어 말하고 개선 과제를 구현 완료로 표현하지 않아야 합니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [app/database.py](../app/database.py) · [app/services/llm.py](../app/services/llm.py) · [README.md](../README.md)

**확인·시연:** Q020·Q060·Q086·Q090의 답변과 현재 코드를 함께 확인합니다.

<a id="q097"></a>

### Q097. 운영 환경으로 확장한다면 무엇을 먼저 개선하나요?

**답안:** 우선 HTTPS·Secure 쿠키와 세션 폐기·추가 CSRF 방어·호출량 제한을 검토하겠습니다. 이어 DB 접근 계층, 오류/응답 스키마 통일, request_id·처리시간·비용 지표, 전체 deadline과 중복 요청 정책을 보강합니다. 이는 제안 순서이며 실제 운영 요구·부하·위협에 따라 결정할 미구현 과제입니다.

**근거:** [app/main.py](../app/main.py) · [app/dependencies.py](../app/dependencies.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/errors.py](../app/errors.py) · [app/services/llm.py](../app/services/llm.py)

**확인·시연:** 현재 코드에서 적용되지 않은 지점을 짚고 개선 목표와 확인 기준을 설명합니다.

<a id="q098"></a>

### Q098. DB 백업·개인정보 보관·삭제 정책은 구현되어 있나요?

**답안:** 자동 백업·복원 검증·보관기간·사용자 삭제 API·대화 삭제 API는 현재 제공하지 않습니다. 대화 원문과 유효 이메일 로그가 남으므로 운영에서는 접근 권한과 보관·삭제 정책을 추가해야 합니다. live SQLite 백업은 일관성 있는 방법을 설계해야 하며 일반 파일 복사만으로 복원 가능성을 보장한다고 답하지 않습니다.

**근거:** [app/models/chat.py](../app/models/chat.py) · [app/routers/auth.py](../app/routers/auth.py) · [app/routers/logs.py](../app/routers/logs.py) · [docs/DEPLOY.md](../docs/DEPLOY.md)

**확인·시연:** 현재 저장·조회 기능과 미구현된 관리 정책을 명확히 구분합니다.

<a id="q099"></a>

### Q099. 대화방·문맥 선택·확장 가능한 DB 구조는 어떻게 개선할 수 있나요?

**답안:** 현재는 대화방 구분 없이 같은 사용자의 최근 성공 기록을 문맥으로 사용합니다. 여러 기획을 독립적으로 이어가려면 conversation 테이블과 소유권·문맥 선택 규칙, 마이그레이션·페이지네이션을 설계할 수 있습니다. 트래픽 증가 시 PostgreSQL·비동기 DB·큐 도입은 측정 근거에 따라 검토할 계획입니다.

**근거:** [app/models/chat.py](../app/models/chat.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [app/database.py](../app/database.py)

**확인·시연:** 현 구조의 user_id 필터를 보여주고 대화방 분리 시 변경할 모델·조회·인가를 설명합니다.

<a id="q100"></a>

### Q100. 평가 마지막에 이 프로젝트를 어떻게 요약하겠습니까?

**답안:** PULSE는 로그인 사용자의 경제·AI 숏폼 기획을 네이버 자료와 최근 대화 맥락으로 돕는 FastAPI 서비스입니다. 사용자별 저장·조회, 입력 검증, 알려진 AI 실패 안내와 역할별 코드·문서를 갖췄습니다. 실제 AI·배포 시연과 테스트 결과는 확인된 범위로 제시하고 DB 접근 분리·운영 관측·보안·확장 과제를 다음 단계로 설명하겠습니다.

**근거:** [README.md](../README.md) · [docs/images/diagrams/00-overview.png](../docs/images/diagrams/00-overview.png) · [app/main.py](../app/main.py)

**확인·시연:** 문제→전체 흐름→개인 기여→검증 근거→남은 과제의 순서로 1분 요약합니다.

