# PULSE 핵심 평가 질문·답안 30선

작성 기준: 2026-10-06, 현재 작업 폴더 코드·README 및 로컬 Git 이력(확인 당시 HEAD `3bd5f57`).

Q001~Q030은 사용자가 제공한 평가 항목 30개(평가 1: 15개, 평가 2: 8개, 평가 3: 7개)에 순서대로 대응합니다. Q031~Q100은 추가 심화·시연·개인 기여 질문입니다. 질문·답안 번호는 두 문서에서 동일합니다.

답변은 구현과 설계 근거를 설명하는 연습용 초안입니다. 실제 기능 동작은 평가 환경에서 시연해야 합니다. 이번 확인에서 `./.venv/Scripts/python.exe -m pytest -q`는 `ModuleNotFoundError: No module named 'requests'`로 conftest import 중 중단되어 테스트 통과를 확인하지 못했습니다. 실제 AI 호출과 배포 서버 외부 접속도 이번 문서 작업에서 실행하지 않았습니다. 코드·테스트 존재를 실행 성공으로 표현하지 마세요.

[예상 질문 100선](EXPECTED_QUESTIONS_100.md) · [답안 100선](EXPECTED_ANSWERS_100.md)

## 먼저 준비할 항목

제공된 평가 기준을 우선하며, 다음 순서는 점수 배점의 추정이 아니라 시연 준비 순서입니다.

1. 실제 앱 기동·비로그인 차단·가입·로그인·질문·AI 응답·DB 저장·본인 기록 조회를 한 흐름으로 준비합니다.
2. 빈 입력·AI 타임아웃·AI 오류·DB 저장 실패를 테스트 환경에서 확인하고 상태코드·실패 저장·다음 요청 처리를 설명합니다.
3. README의 구조도·API 예시·ERD·DB 확인 절차·역할 표와 실제 코드·Git 이력을 연결합니다.
4. DB 접근 분리 수준, 일부 오류 형식, 총 처리 deadline·운영 요청 ID·보관/삭제 정책의 미구현 범위를 미리 설명합니다.

## 평가 기준 대응표

아래의 ‘코드/문서 확인’은 파일·구현이 있다는 의미이며 실제 실행 통과나 평가 충족 판정을 뜻하지 않습니다.

| 번호 | 평가 단계 | 제공 기준 | 준비 상태·추가 확인 | 질문·답안 |
| --- | --- | --- | --- | --- |
| P001 | 1 | 시스템 구조도(인프라 아키텍처·주요 컴포넌트) | 문서 확인 | [바로 보기](#p001) |
| P002 | 1 | API 명세와 요청·응답 예시 | 문서 확인 | [바로 보기](#p002) |
| P003 | 1 | DB 테이블·필드 또는 ERD | 문서 확인 | [바로 보기](#p003) |
| P004 | 1 | DB 확인 방법 안내 | 문서 확인 | [바로 보기](#p004) |
| P005 | 1 | 팀 역할과 개인별 작업 요약 | 문서 확인 | [바로 보기](#p005) |
| P006 | 1 | 회원가입 기능 | 코드 확인 · 현장 시연 필요 | [바로 보기](#p006) |
| P007 | 1 | 로그인 기능 | 코드 확인 · 현장 시연 필요 | [바로 보기](#p007) |
| P008 | 1 | 로그인·비로그인 접근 구분 | 코드 확인 · 현장 시연 필요 | [바로 보기](#p008) |
| P009 | 1 | 웹 UI 질문 입력·응답 출력 | 코드 확인 · 현장 시연 필요 | [바로 보기](#p009) |
| P010 | 1 | 질문→서버→AI API→출력 연결 | 코드 확인 · 현장 시연 필요 | [바로 보기](#p010) |
| P011 | 1 | 사용자·시간·질문·응답 DB 저장 | 코드 확인 · 현장 시연 필요 | [바로 보기](#p011) |
| P012 | 1 | 사용자 기준 로그 조회·추적 | 코드 확인 · 현장 시연 필요 | [바로 보기](#p012) |
| P013 | 1 | AI 실패·타임아웃 시 서비스 처리 | 코드 확인 · 현장 시연 필요 | [바로 보기](#p013) |
| P014 | 1 | 오류 안내와 상태코드 | 코드 확인 · 현장 시연 필요 | [바로 보기](#p014) |
| P015 | 1 | 사용자 입력 검증 | 코드 확인 · 현장 시연 필요 | [바로 보기](#p015) |
| P016 | 2 | 역할 단위 FastAPI 구조 | 코드 확인 | [바로 보기](#p016) |
| P017 | 2 | 목적별 API 라우트 분리 | 코드 확인 | [바로 보기](#p017) |
| P018 | 2 | 요청·응답 스키마 또는 일관된 형식 | 스키마 사용 · 일부 형식 보강 여지 | [바로 보기](#p018) |
| P019 | 2 | 분리·재사용 가능한 인증 | 코드 확인 | [바로 보기](#p019) |
| P020 | 2 | DB 접근 로직 분리 | 엔진·세션·모델 분리 · 라우터 쿼리 잔존 | [바로 보기](#p020) |
| P021 | 2 | 환경 변수 기반 민감정보 | 코드 확인 | [바로 보기](#p021) |
| P022 | 2 | .env 예시·.gitignore | 코드 확인 | [바로 보기](#p022) |
| P023 | 2 | PR 병합 기록·브랜치 흐름 | 로컬 Git 이력 확인 · PR 화면은 별도 | [바로 보기](#p023) |
| P024 | 3 | REST 관점의 목적별 경로·메서드 | 코드 확인 | [바로 보기](#p024) |
| P025 | 3 | 인증·인가의 서비스상 필요성 | 코드 확인 | [바로 보기](#p025) |
| P026 | 3 | 서버 AI 호출·키 비노출 | 코드 확인 | [바로 보기](#p026) |
| P027 | 3 | AI 지연·실패 정책 | 코드 확인 | [바로 보기](#p027) |
| P028 | 3 | 대화 로그 저장 목적과 활용 | 코드 확인 | [바로 보기](#p028) |
| P029 | 3 | 요청·AI·DB 운영 이벤트 추적 | 이벤트 구현 · 요청 ID/시간 지표 미구현 | [바로 보기](#p029) |
| P030 | 3 | 문서 기여와 Git 이력의 일치 | 로컬 Git 이력 확인 · PR 화면은 별도 | [바로 보기](#p030) |

## 평가 1 · 문서와 기본 동작

<a id="p001"></a>

### P001. 시스템 구조도는 어디에 있고 어떤 구성요소를 설명하나요?

평가 1 기준: **시스템 구조도(인프라 아키텍처·주요 컴포넌트)**

**답안:** README의 서비스 아키텍처 이미지에 브라우저, Ubuntu VM 배포 구성, FastAPI, SQLite, 네이버 API, Codyssey LLM 연결을 정리했습니다. 브라우저는 앱 API를 호출하고 외부 데이터와 AI 호출은 서버가 담당합니다. VM 그림은 저장소의 배포 설계이며 현재 서버 가동을 증명하는 자료는 아닙니다.

**근거:** [README.md](../README.md) · [docs/images/diagrams/02-architecture.png](../docs/images/diagrams/02-architecture.png) · [app/main.py](../app/main.py) · [deploy/ai-chatbot.service](../deploy/ai-chatbot.service)

**확인·시연:** README의 아키텍처 이미지를 열고 브라우저→서버→외부 API→DB 순서로 설명합니다.

**100선 연결:** [질문 Q001](EXPECTED_QUESTIONS_100.md#q001) · [답안 Q001](EXPECTED_ANSWERS_100.md#q001)

<a id="p002"></a>

### P002. API 명세와 요청·응답 예시는 어떻게 제공하나요?

평가 1 기준: **API 명세와 요청·응답 예시**

**답안:** README에 메서드, 경로, 로그인 필요 여부, 성공 상태코드와 JSON 예시를 제공합니다. 가입·로그인은 email/password, 채팅은 mode/message/선택 keyword를 받고, 채팅 성공은 chat_id/answer를 반환합니다. 실행 중인 앱의 /docs에서도 등록된 API 스키마를 확인할 수 있습니다.

**근거:** [README.md](../README.md) · [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py)

**확인·시연:** README API 표와 요청·응답 예시를 보여주고 실행 환경에서는 /docs를 엽니다.

**100선 연결:** [질문 Q002](EXPECTED_QUESTIONS_100.md#q002) · [답안 Q002](EXPECTED_ANSWERS_100.md#q002)

<a id="p003"></a>

### P003. DB 구조와 ERD는 실제 코드와 일치하나요?

평가 1 기준: **DB 테이블·필드 또는 ERD**

**답안:** 실제 테이블은 users와 chats입니다. users.id와 chats.user_id가 외래키로 연결되어 사용자 1명이 대화 0개 이상을 소유합니다. ERD에 실제 컬럼·자료형·NULL 허용·키·기본값을 표시했고, mode/status 값 범위는 DB CHECK가 아닌 애플리케이션 규칙임을 구분했습니다.

**근거:** [app/models/user.py](../app/models/user.py) · [app/models/chat.py](../app/models/chat.py) · [docs/images/diagrams/01-db-erd.png](../docs/images/diagrams/01-db-erd.png) · [app/database.py](../app/database.py)

**확인·시연:** ERD의 id/user_id 관계와 answer의 NULL 허용을 모델 선언과 대조합니다.

**100선 연결:** [질문 Q003](EXPECTED_QUESTIONS_100.md#q003) · [답안 Q003](EXPECTED_ANSWERS_100.md#q003)

<a id="p004"></a>

### P004. DB 파일과 저장된 대화는 어떻게 확인하나요?

평가 1 기준: **DB 확인 방법 안내**

**답안:** 기본 DATABASE_URL은 sqlite:///./app.db이며 실행 작업 폴더의 app.db를 사용합니다. scripts/check_logs.py는 지정 DB를 읽기 전용으로 열고 user_id 조건으로 대화 내용을 조회합니다. 화면 /history나 GET /api/me/chats로도 본인 기록을 확인할 수 있습니다.

**근거:** [app/config.py](../app/config.py) · [scripts/check_logs.py](../scripts/check_logs.py) · [scripts/check_logs.sql](../scripts/check_logs.sql) · [README.md](../README.md)

**확인·시연:** 실제 DB 경로와 본인 ID를 확인한 뒤 python scripts/check_logs.py --db app.db --user-id 1 --limit 20을 실행합니다.

**100선 연결:** [질문 Q004](EXPECTED_QUESTIONS_100.md#q004) · [답안 Q004](EXPECTED_ANSWERS_100.md#q004)

<a id="p005"></a>

### P005. 팀 역할과 개인별 기여는 어디에 정리했나요?

평가 1 기준: **팀 역할과 개인별 작업 요약**

**답안:** README에 A 김준택의 기반·인증, B 이지영의 트렌드, C 정지환의 채팅·AI, D 김정현의 UI·기록 조회를 정리했습니다. 역할 이미지와 개인별 표에 파일 책임, 브랜치, PR, 통합 기여를 연결했습니다. 본인이 직접 수행한 작업은 해당 파일과 커밋을 함께 설명합니다.

**근거:** [README.md](../README.md) · [docs/images/diagrams/04-team-roles.png](../docs/images/diagrams/04-team-roles.png) · [docs/D_HANDOFF.md](../docs/D_HANDOFF.md) · [docs/C_AGENT_HANDOFF.md](../docs/C_AGENT_HANDOFF.md)

**확인·시연:** 팀 역할 표에서 본인 담당을 짚고 git log --all --oneline로 대응 커밋을 보여줍니다.

**100선 연결:** [질문 Q005](EXPECTED_QUESTIONS_100.md#q005) · [답안 Q005](EXPECTED_ANSWERS_100.md#q005)

<a id="p006"></a>

### P006. 회원가입은 어떤 절차로 동작하나요?

평가 1 기준: **회원가입 기능**

**답안:** POST /api/auth/signup이 이메일·비밀번호를 검증하고 중복 이메일을 확인한 뒤 bcrypt 해시를 users에 저장합니다. 성공 시 201과 id/email을 반환하고 자동 로그인은 하지 않습니다. 동일 이메일 중복은 UNIQUE 제약과 IntegrityError 처리로도 방어합니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/models/user.py](../app/models/user.py) · [tests/test_auth_signup.py](../tests/test_auth_signup.py) · [tests/test_auth_edge_cases.py](../tests/test_auth_edge_cases.py)

**확인·시연:** 새 이메일로 가입해 201을 확인하고 같은 이메일 재가입의 409를 비교합니다.

**100선 연결:** [질문 Q006](EXPECTED_QUESTIONS_100.md#q006) · [답안 Q006](EXPECTED_ANSWERS_100.md#q006)

<a id="p007"></a>

### P007. 로그인은 어떤 방식으로 동작하나요?

평가 1 기준: **로그인 기능**

**답안:** POST /api/auth/login이 정규화된 이메일로 사용자를 조회하고 bcrypt로 비밀번호를 비교합니다. 성공하면 기존 세션 내용을 비우고 user_id를 서명된 세션 쿠키에 기록하며 200을 반환합니다. 실패는 401 INVALID_CREDENTIALS이고 비밀번호 해시는 응답하지 않습니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/security.py](../app/security.py) · [app/main.py](../app/main.py) · [tests/test_auth_login.py](../tests/test_auth_login.py)

**확인·시연:** 정상 로그인, 잘못된 비밀번호, 로그인 후 /api/me 조회를 순서대로 확인합니다.

**100선 연결:** [질문 Q007](EXPECTED_QUESTIONS_100.md#q007) · [답안 Q007](EXPECTED_ANSWERS_100.md#q007)

<a id="p008"></a>

### P008. 비로그인 사용자는 어떤 기능을 사용할 수 없나요?

평가 1 기준: **로그인·비로그인 접근 구분**

**답안:** 채팅과 내 기록 API는 require_login 의존성으로 보호되어 비로그인 요청에 401 LOGIN_REQUIRED를 반환합니다. 채팅·기록 페이지는 /login으로 303 리다이렉트합니다. 회원가입·로그인 페이지와 /health는 비로그인 상태에서도 접근할 수 있습니다.

**근거:** [app/dependencies.py](../app/dependencies.py) · [app/routers/pages.py](../app/routers/pages.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py)

**확인·시연:** 로그아웃 상태에서 /와 /history의 리다이렉트, /api/chat과 /api/me/chats의 401을 보여줍니다.

**100선 연결:** [질문 Q008](EXPECTED_QUESTIONS_100.md#q008) · [답안 Q008](EXPECTED_ANSWERS_100.md#q008)

<a id="p009"></a>

### P009. 웹 UI에서 질문 입력과 답변 출력이 가능한가요?

평가 1 기준: **웹 UI 질문 입력·응답 출력**

**답안:** 채팅 화면에서 모드와 질문을 입력하면 chat.js가 /api/chat에 JSON을 전송합니다. 성공 응답의 answer를 assistant 메시지로 추가하고 대기 상태를 해제합니다. 답변 표시에는 textContent를 사용하며 실제 AI 응답 시연은 app.main:app에서 별도로 확인해야 합니다.

**근거:** [app/templates/chat.html](../app/templates/chat.html) · [app/static/js/chat.js](../app/static/js/chat.js) · [app/static/js/common.js](../app/static/js/common.js) · [tests/test_ui_auth_integration.py](../tests/test_ui_auth_integration.py)

**확인·시연:** 실제 앱에 로그인해 질문을 전송하고 화면 답변과 네트워크 응답의 answer를 비교합니다.

**100선 연결:** [질문 Q009](EXPECTED_QUESTIONS_100.md#q009) · [답안 Q009](EXPECTED_ANSWERS_100.md#q009)

<a id="p010"></a>

### P010. 질문부터 AI 호출과 출력까지 전체 흐름을 설명해 주세요.

평가 1 기준: **질문→서버→AI API→출력 연결**

**답안:** UI 전송 뒤 서버가 인증·입력을 검증하고 본인의 최근 성공 대화 5쌍과 모드별 참고 자료를 구성합니다. ask_llm이 서버에서 Codyssey API를 한 번 호출하고, 결과·상태를 DB에 commit한 후 응답합니다. UI는 반환된 answer 또는 오류 안내를 표시합니다.

**근거:** [docs/images/diagrams/03-system-flow.png](../docs/images/diagrams/03-system-flow.png) · [app/routers/chat.py](../app/routers/chat.py) · [app/services/llm.py](../app/services/llm.py) · [app/static/js/chat.js](../app/static/js/chat.js)

**확인·시연:** 실제 앱 질문 1건의 UI→POST /api/chat→대화 저장→내 기록 조회를 한 흐름으로 확인합니다.

**100선 연결:** [질문 Q010](EXPECTED_QUESTIONS_100.md#q010) · [답안 Q010](EXPECTED_ANSWERS_100.md#q010)

<a id="p011"></a>

### P011. 사용자·시간·질문·AI 응답이 DB에 저장되나요?

평가 1 기준: **사용자·시간·질문·응답 DB 저장**

**답안:** chats에 user_id, created_at, question, answer를 저장해 사용자와 시각 기준으로 추적합니다. mode, scenario_version, status도 함께 저장합니다. AI 실패는 answer=NULL과 timeout/error 상태로 남기며 DB 저장 자체가 실패한 경우에는 기록 저장을 보장하지 않고 500을 반환합니다.

**근거:** [app/models/chat.py](../app/models/chat.py) · [app/routers/chat.py](../app/routers/chat.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** 채팅 응답 chat_id와 조회된 행의 id·question·answer·status를 대조합니다.

**100선 연결:** [질문 Q011](EXPECTED_QUESTIONS_100.md#q011) · [답안 Q011](EXPECTED_ANSWERS_100.md#q011)

<a id="p012"></a>

### P012. 특정 사용자의 대화 로그만 조회할 수 있나요?

평가 1 기준: **사용자 기준 로그 조회·추적**

**답안:** GET /api/me/chats는 인증 사용자 ID로 WHERE 조건을 만들어 본인 기록만 반환합니다. 요청자가 다른 user_id를 전달해도 조회 대상은 바뀌지 않습니다. 운영용 읽기 전용 스크립트는 명시한 사용자 ID로 조회하지만 웹 인증 API와 같은 권한 경계는 없으므로 DB 파일 접근 권한이 필요합니다.

**근거:** [app/routers/logs.py](../app/routers/logs.py) · [scripts/check_logs.py](../scripts/check_logs.py) · [tests/test_ui.py](../tests/test_ui.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** 두 사용자로 로그인해 각 기록을 확인하고 user_id 쿼리를 추가해도 타인 기록이 나오지 않는지 확인합니다.

**100선 연결:** [질문 Q012](EXPECTED_QUESTIONS_100.md#q012) · [답안 Q012](EXPECTED_ANSWERS_100.md#q012)

<a id="p013"></a>

### P013. AI 실패·타임아웃에도 서비스가 계속 동작하도록 했나요?

평가 1 기준: **AI 실패·타임아웃 시 서비스 처리**

**답안:** LLM 클라이언트는 HTTP 오류를 AIServiceError, 타임아웃을 AITimeoutError로 변환합니다. 채팅 라우터는 두 예외를 처리해 실패 상태를 저장하고 안내 응답을 반환합니다. 이는 알려진 AI 실패 경로에 대한 처리이며 모든 예외·인프라 장애를 처리한다는 의미는 아닙니다.

**근거:** [app/services/llm.py](../app/services/llm.py) · [app/routers/chat.py](../app/routers/chat.py) · [tests/test_llm.py](../tests/test_llm.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** 모의 타임아웃·AI 오류 후 다음 요청을 보내 정상 처리 가능한지 확인합니다.

**100선 연결:** [질문 Q013](EXPECTED_QUESTIONS_100.md#q013) · [답안 Q013](EXPECTED_ANSWERS_100.md#q013)

<a id="p014"></a>

### P014. 오류가 발생하면 사용자는 어떤 안내를 받나요?

평가 1 기준: **오류 안내와 상태코드**

**답안:** 입력 오류 422, 비로그인 401, AI 오류 502, AI 타임아웃 504, 대화 저장 실패 500을 구분합니다. 인증·검증·채팅 오류는 주로 error/message 형식이고 기록 조회 DB 오류는 503과 detail을 반환합니다. UI의 공통 요청 함수는 두 형식 모두 사용자 안내로 바꿉니다.

**근거:** [app/errors.py](../app/errors.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [app/static/js/common.js](../app/static/js/common.js)

**확인·시연:** 빈 질문, 잘못된 로그인, 모의 AI 타임아웃의 상태코드와 화면 문구를 비교합니다.

**100선 연결:** [질문 Q014](EXPECTED_QUESTIONS_100.md#q014) · [답안 Q014](EXPECTED_ANSWERS_100.md#q014)

<a id="p015"></a>

### P015. 어떤 사용자 입력 검증을 구현했나요?

평가 1 기준: **사용자 입력 검증**

**답안:** ChatRequest가 mode와 message의 문자열 여부를 확인하고 공백 제거 후 질문 1~500자, keyword 최대 50자를 검증합니다. 가입은 이메일 형식과 비밀번호 8자 이상·UTF-8 72바이트 이하를 확인합니다. UI 검증을 우회한 직접 API 요청도 서버에서 검사합니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/routers/auth.py](../app/routers/auth.py) · [tests/test_chat.py](../tests/test_chat.py) · [tests/test_auth_signup.py](../tests/test_auth_signup.py)

**확인·시연:** 공백 질문·501자 질문·잘못된 mode·짧은 비밀번호를 직접 API로 전송해 422를 확인합니다.

**100선 연결:** [질문 Q015](EXPECTED_QUESTIONS_100.md#q015) · [답안 Q015](EXPECTED_ANSWERS_100.md#q015)

## 평가 2 · 구조와 협업

<a id="p016"></a>

### P016. 프로젝트 구조를 역할 단위로 어떻게 나눴나요?

평가 2 기준: **역할 단위 FastAPI 구조**

**답안:** app/routers는 HTTP 경계, services는 트렌드·LLM·시나리오, models는 DB 구조를 담당합니다. config/database/dependencies/security/errors는 공통 기반이고 templates/static은 UI입니다. main.py는 이 구성요소를 등록하는 진입점입니다.

**근거:** [README.md](../README.md) · [app/main.py](../app/main.py) · [app/ui.py](../app/ui.py) · [app/database.py](../app/database.py)

**확인·시연:** README 파일 구조와 실제 app/ 폴더를 나란히 보여줍니다.

**100선 연결:** [질문 Q016](EXPECTED_QUESTIONS_100.md#q016) · [답안 Q016](EXPECTED_ANSWERS_100.md#q016)

<a id="p017"></a>

### P017. API 라우트는 목적에 맞게 분리되어 있나요?

평가 2 기준: **목적별 API 라우트 분리**

**답안:** auth.py는 /api/auth의 가입·로그인·로그아웃, chat.py는 채팅과 /api/me, logs.py는 /api/me/chats를 담당합니다. pages.py는 HTML 페이지를 분리하고 /docs 스키마에서 제외합니다. UI 설치 함수는 중복 경로 등록도 검사합니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [app/routers/pages.py](../app/routers/pages.py) · [app/ui.py](../app/ui.py)

**확인·시연:** 각 라우터의 prefix와 decorator를 확인하고 main.py의 등록 지점을 보여줍니다.

**100선 연결:** [질문 Q017](EXPECTED_QUESTIONS_100.md#q017) · [답안 Q017](EXPECTED_ANSWERS_100.md#q017)

<a id="p018"></a>

### P018. 요청·응답 형식의 일관성은 어떻게 관리하나요?

평가 2 기준: **요청·응답 스키마 또는 일관된 형식**

**답안:** 가입·로그인·채팅 요청에는 Pydantic 모델을 쓰고 사용자 응답은 UserResponse, 기록 응답은 ChatLog 목록으로 제한합니다. 채팅 성공은 chat_id/answer 딕셔너리이며 명시적 response_model은 아직 없습니다. 대부분 오류는 error/message로 통일했지만 기록 조회의 detail 형식은 공통 UI에서 함께 처리합니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [app/errors.py](../app/errors.py)

**확인·시연:** UserResponse·ChatLog·ChatRequest를 보여주고 채팅 응답 스키마와 오류 형식의 남은 개선점을 설명합니다.

**100선 연결:** [질문 Q018](EXPECTED_QUESTIONS_100.md#q018) · [답안 Q018](EXPECTED_ANSWERS_100.md#q018)

<a id="p019"></a>

### P019. 인증 로직을 어떻게 재사용하도록 분리했나요?

평가 2 기준: **분리·재사용 가능한 인증**

**답안:** SessionMiddleware가 서명된 쿠키를 처리하고 get_current_user가 세션 user_id로 DB 사용자를 조회합니다. require_login은 로그인 필요 API에 Depends로 재사용합니다. HTML 페이지는 get_current_user 결과가 없을 때 로그인 화면으로 이동합니다.

**근거:** [app/main.py](../app/main.py) · [app/dependencies.py](../app/dependencies.py) · [app/routers/pages.py](../app/routers/pages.py) · [tests/test_dependencies.py](../tests/test_dependencies.py)

**확인·시연:** 채팅·기록·로그아웃에 같은 require_login이 적용되는 코드를 보여줍니다.

**100선 연결:** [질문 Q019](EXPECTED_QUESTIONS_100.md#q019) · [답안 Q019](EXPECTED_ANSWERS_100.md#q019)

<a id="p020"></a>

### P020. DB 접근이 라우터와 충분히 분리되어 있나요?

평가 2 기준: **DB 접근 로직 분리**

**답안:** 엔진 생성, 요청별 세션, ORM 모델은 database.py와 models로 분리했습니다. 다만 사용자 조회·대화 조회·commit 등은 라우터에 남아 있어 별도 CRUD·리포지토리 계층까지 분리된 구조는 아닙니다. 이 기준은 기반 분리는 되어 있으나 쿼리·트랜잭션 경계 분리의 개선 여지가 있다고 답하겠습니다.

**근거:** [app/database.py](../app/database.py) · [app/models/user.py](../app/models/user.py) · [app/models/chat.py](../app/models/chat.py) · [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py)

**확인·시연:** 분리된 엔진·세션·모델과 라우터에 남은 쿼리를 함께 제시합니다.

**100선 연결:** [질문 Q020](EXPECTED_QUESTIONS_100.md#q020) · [답안 Q020](EXPECTED_ANSWERS_100.md#q020)

<a id="p021"></a>

### P021. API 키 같은 민감정보가 코드에 하드코딩되어 있나요?

평가 2 기준: **환경 변수 기반 민감정보**

**답안:** 실제 API 키와 세션 서명 키는 pydantic-settings를 통해 환경 변수 또는 .env에서 읽습니다. 코드에는 키 값 대신 변수 이름과 기본 연결 주소가 있습니다. LLM·네이버 호출은 서버에서 수행하고 /api/me는 설정 여부만 boolean으로 반환합니다.

**근거:** [app/config.py](../app/config.py) · [app/services/llm.py](../app/services/llm.py) · [app/services/trend.py](../app/services/trend.py) · [app/routers/chat.py](../app/routers/chat.py)

**확인·시연:** 설정 필드와 외부 API 헤더 생성 코드를 보여주되 실제 .env 값은 화면에 표시하지 않습니다.

**100선 연결:** [질문 Q021](EXPECTED_QUESTIONS_100.md#q021) · [답안 Q021](EXPECTED_ANSWERS_100.md#q021)

<a id="p022"></a>

### P022. .env 예시와 Git 제외 설정을 어떻게 제공하나요?

평가 2 기준: **.env 예시·.gitignore**

**답안:** .env.example에는 변수 이름·기본값과 빈 비밀 값만 제공합니다. .gitignore는 .env와 .env.*를 제외하고 .env.example만 허용하며 DB 파일과 가상환경도 제외합니다. 이 설정은 현재 파일의 추적 방지이며 과거 Git 이력 전체의 비밀 값 부재를 증명하는 검사와는 구분합니다.

**근거:** [.env.example](../.env.example) · [.gitignore](../.gitignore) · [README.md](../README.md)

**확인·시연:** git ls-files .env .env.example과 git check-ignore -v .env로 추적·제외 상태를 확인합니다.

**100선 연결:** [질문 Q022](EXPECTED_QUESTIONS_100.md#q022) · [답안 Q022](EXPECTED_ANSWERS_100.md#q022)

<a id="p023"></a>

### P023. PR 기반 병합과 브랜치 흐름을 증명할 수 있나요?

평가 2 기준: **PR 병합 기록·브랜치 흐름**

**답안:** 로컬 Git 이력에 PR #2 인증, #4 UI, #5 트렌드, #3 채팅, #6 배포 문서의 병합 커밋이 있습니다. feature/*, develop, main과 관련 원격 추적 브랜치도 확인됩니다. 병합 커밋은 PR 사용 근거이지만 리뷰 승인 내용은 별도 PR 화면에서 확인해야 합니다.

**근거:** [README.md](../README.md) · [docs/D_PR_DRAFTS.md](../docs/D_PR_DRAFTS.md)

**확인·시연:** git log --all --merges --oneline과 git branch -a를 보여주고 각 PR·역할을 대응시킵니다.

**100선 연결:** [질문 Q023](EXPECTED_QUESTIONS_100.md#q023) · [답안 Q023](EXPECTED_ANSWERS_100.md#q023)

## 평가 3 · 설계 이유와 운영 추적

<a id="p024"></a>

### P024. REST 관점에서 엔드포인트와 메서드는 어떤 기준으로 정했나요?

평가 3 기준: **REST 관점의 목적별 경로·메서드**

**답안:** 가입·로그인·로그아웃·AI 대화 생성은 상태 변화나 처리가 있으므로 POST, 내 정보·기록·상태 조회는 GET을 사용했습니다. 본인 자원은 /api/me와 /api/me/chats로 표현했습니다. 로그인 동작은 액션 경로이며 모든 경로가 엄격한 자원 중심 REST라고 주장하지는 않습니다.

**근거:** [app/routers/auth.py](../app/routers/auth.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [README.md](../README.md)

**확인·시연:** API 표에서 조회 GET과 처리 POST, 가입 201·로그아웃 204의 의도를 설명합니다.

**100선 연결:** [질문 Q024](EXPECTED_QUESTIONS_100.md#q024) · [답안 Q024](EXPECTED_ANSWERS_100.md#q024)

<a id="p025"></a>

### P025. 이 서비스에 인증·인가가 왜 필요한가요?

평가 3 기준: **인증·인가의 서비스상 필요성**

**답안:** 대화에는 사용자의 제작 기획과 과거 업로드 맥락이 들어가므로 다른 사용자가 접근하면 안 됩니다. 인증은 요청자의 신원을 확인하고, 인가는 조회·AI 문맥을 그 사용자의 기록으로 제한합니다. 비로그인 AI 호출 제한은 비용 사용의 기본 경계이지만 호출량 제한 기능을 대신하지는 않습니다.

**근거:** [app/dependencies.py](../app/dependencies.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** 비로그인 차단과 두 계정의 문맥·기록 격리를 함께 보여줍니다.

**100선 연결:** [질문 Q025](EXPECTED_QUESTIONS_100.md#q025) · [답안 Q025](EXPECTED_ANSWERS_100.md#q025)

<a id="p026"></a>

### P026. AI 호출을 클라이언트가 아닌 서버에서 하는 이유는 무엇인가요?

평가 3 기준: **서버 AI 호출·키 비노출**

**답안:** 클라이언트에 키를 넣으면 브라우저 소스나 네트워크에서 키를 가져갈 수 있습니다. 서버는 인증·입력 검증·참고 자료·실패 처리·저장을 통합한 뒤 AI를 호출합니다. 브라우저에는 앱 API 결과만 반환하므로 공급자 키를 전달할 필요가 없습니다.

**근거:** [app/services/llm.py](../app/services/llm.py) · [app/routers/chat.py](../app/routers/chat.py) · [app/static/js/chat.js](../app/static/js/chat.js)

**확인·시연:** 브라우저의 /api/chat 요청과 서버 ask_llm의 Authorization 헤더 생성 위치를 비교합니다.

**100선 연결:** [질문 Q026](EXPECTED_QUESTIONS_100.md#q026) · [답안 Q026](EXPECTED_ANSWERS_100.md#q026)

<a id="p027"></a>

### P027. AI 지연·실패 정책은 무엇이며 재시도도 있나요?

평가 3 기준: **AI 지연·실패 정책**

**답안:** LLM HTTP 클라이언트의 기본 timeout은 50초이고 브라우저 채팅 대기는 기본 65초입니다. AI 타임아웃·서비스 오류는 각각 504·502로 안내하고 자동 재시도는 없습니다. 50초는 연결·읽기·쓰기·풀 대기 제한이므로 트렌드 수집부터 DB 저장까지의 총 50초 상한은 아닙니다.

**근거:** [app/config.py](../app/config.py) · [app/services/llm.py](../app/services/llm.py) · [app/static/js/common.js](../app/static/js/common.js) · [tests/test_llm.py](../tests/test_llm.py)

**확인·시연:** 타임아웃 설정과 재시도 없는 단일 API 호출을 보여주고 총 처리 시간 제한과의 차이를 설명합니다.

**100선 연결:** [질문 Q027](EXPECTED_QUESTIONS_100.md#q027) · [답안 Q027](EXPECTED_ANSWERS_100.md#q027)

<a id="p028"></a>

### P028. 대화 로그를 왜 저장하며 실제 기능에 어떻게 사용하나요?

평가 3 기준: **대화 로그 저장 목적과 활용**

**답안:** 사용자가 이전 추천을 다시 확인하고 실패 내역을 추적할 수 있도록 저장합니다. 성공 기록은 다음 질문의 최근 5쌍 문맥으로 재사용하고 /history·조회 API·읽기 전용 스크립트로 확인합니다. 자동 학습이나 모델 재훈련 파이프라인은 구현하지 않았습니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/routers/logs.py](../app/routers/logs.py) · [scripts/check_logs.py](../scripts/check_logs.py) · [app/models/chat.py](../app/models/chat.py)

**확인·시연:** 이전 답변을 기록 화면에서 다시 보고 후속 질문의 문맥 구성 코드를 설명합니다.

**100선 연결:** [질문 Q028](EXPECTED_QUESTIONS_100.md#q028) · [답안 Q028](EXPECTED_ANSWERS_100.md#q028)

<a id="p029"></a>

### P029. 문제 발생 시 요청·AI·DB 단계의 원인을 추적할 수 있나요?

평가 3 기준: **요청·AI·DB 운영 이벤트 추적**

**답안:** 채팅 라우터가 request_received, ai_call_start, ai_call_success 또는 ai_call_fail, db_save_success 또는 db_save_fail을 남깁니다. user_id·mode·저장 성공 시 chat_id와 AI 오류 사유로 실패 단계를 추적합니다. 요청 고유 ID와 처리 시간 지표는 없으므로 같은 사용자의 동시 요청을 완전히 구분하는 기능은 개선 과제입니다.

**근거:** [app/routers/chat.py](../app/routers/chat.py) · [app/main.py](../app/main.py) · [docs/DEPLOY.md](../docs/DEPLOY.md) · [tests/test_chat_api.py](../tests/test_chat_api.py)

**확인·시연:** journalctl -u ai-chatbot -f에서 단계별 이벤트를 확인하고 AI 실패와 DB 실패를 구분합니다.

**100선 연결:** [질문 Q029](EXPECTED_QUESTIONS_100.md#q029) · [답안 Q029](EXPECTED_ANSWERS_100.md#q029)

<a id="p030"></a>

### P030. 문서의 개인별 기여가 Git 이력과 일치하나요?

평가 3 기준: **문서 기여와 Git 이력의 일치**

**답안:** README의 역할 표를 소유 파일과 PR·커밋에 연결해 설명할 수 있습니다. 로컬 이력에서 #2/#4/#5/#3/#6 병합을 확인했고 A의 배포 문서·통합 기여도 표에 반영되어 있습니다. 커밋 작성자 표기와 실제 팀원 이름이 다를 수 있어 계정·작성자·파일을 함께 확인해야 합니다.

**근거:** [README.md](../README.md) · [docs/C_AGENT_HANDOFF.md](../docs/C_AGENT_HANDOFF.md) · [docs/D_HANDOFF.md](../docs/D_HANDOFF.md)

**확인·시연:** git log --all --format=fuller -- app/routers/auth.py 등 담당 파일별 이력을 조회합니다.

**100선 연결:** [질문 Q030](EXPECTED_QUESTIONS_100.md#q030) · [답안 Q030](EXPECTED_ANSWERS_100.md#q030)

## 현장 시연 순서와 준비 명령

아래 명령은 저장소 루트에서 실행합니다. 현재 작업 폴더에 설치된 의존성은 완전하지 않으므로 평가 환경의 설치 상태를 먼저 확인하세요. Windows PowerShell은 `./.venv/Scripts/python.exe`, Linux는 `.venv/bin/python`을 사용합니다.

### 1. 의존성·테스트·실제 앱 기동

```powershell
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m pip check
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

기존 `.env`를 덮어쓰지 말고 `SECRET_KEY` 및 필요한 외부 API 인증을 준비합니다. 위 명령의 성공은 평가 환경에서 확인해야 하며 이번 문서 작업에서는 설치·서버 기동을 실행하지 않았습니다.

### 2. 웹 기능과 기록 확인

1. 비로그인으로 `/`·`/history` 접근 시 로그인 화면 이동, 보호 API 401을 확인합니다.
2. `/signup`에서 새 테스트 계정 가입 후 `/login`에서 로그인합니다. 가입 성공만으로 로그인되지 않는 것을 확인합니다.
3. `/`에서 Q3 등 모드를 선택해 질문하고 화면 답변·네트워크 응답을 확인합니다. Q2는 과거 업로드 주제를 먼저 입력합니다.
4. `/history`와 `GET /api/me/chats?limit=20`에서 같은 질문·답변·상태를 확인합니다.
5. `/api/me`로 확인한 본인 ID와 실제 DB 경로로 아래 조회 명령을 실행합니다. 예시 ID 1을 실제 ID로 바꾸세요.

```powershell
./.venv/Scripts/python.exe scripts/check_logs.py --db app.db --user-id 1 --limit 20
```

### 3. 실패 경로와 회복 확인

- 서버 검증: 공백 질문·501자 질문·지원하지 않는 mode의 422와 AI 호출 차단을 확인합니다.
- 모의 AI 실패: `tests/test_chat_api.py`·`tests/test_llm.py`의 공급자 오류·타임아웃 테스트로 502/504, answer=NULL, error/timeout 저장을 확인합니다.
- DB 저장 실패: `test_db_failure_never_returns_success`에서 500 DB_ERROR·rollback·다음 요청 처리 결과를 확인합니다.
- UI 데모 `[timeout]`·`[error]`는 데모 전용 동작입니다. 실제 앱은 이 문자열을 특별한 실패 명령으로 처리하지 않습니다.

### 4. 실서비스 연결·운영 근거

`scripts.check_connection`은 임시 DB에서 실제 AI를 호출하며 사용량이 발생할 수 있습니다. 평가 환경의 연결 확인을 위한 선택 절차이며 외부 VM 접근 검증과 구분합니다.

```powershell
./.venv/Scripts/python.exe -m scripts.check_connection
git log --all --merges --oneline
git branch -a
```

배포 서버에서는 `systemctl status ai-chatbot`, `journalctl -u ai-chatbot -f`, 서버 내부 `/health`와 평가 PC에서의 공인 주소 접근을 구분해 확인합니다. `GET /health`는 고정 서버 상태 응답으로 DB·네이버·LLM 연결을 모두 검사하는 readiness API가 아닙니다.

## 현장에서 피해야 할 과장

- 데모 고정 응답을 실제 AI 응답으로, 테스트 코드 존재를 이번 실행 통과로 소개하지 않습니다.
- 검색 상대지수를 유튜브 조회수·검색 횟수로, 최신순 일부 뉴스를 인기 순위·전체 언급량으로 소개하지 않습니다.
- 최근 대화 재사용을 모델 학습·재훈련으로, 서명 쿠키를 내용 암호화로 소개하지 않습니다.
- 브라우저 취소를 서버 작업 취소로, 50초 HTTP timeout을 전체 요청 처리 deadline으로 소개하지 않습니다.
- 라우터까지 완전히 분리된 DB 리포지토리·전역 세션 폐기·관리자 기능·대화방·자동 백업·보관/삭제·호출량 제한이 있다고 소개하지 않습니다.
- 운영 로그에는 유효 이메일·사용자 ID가 포함될 수 있습니다. 개인정보가 전혀 남지 않는다고 답하지 않습니다.
