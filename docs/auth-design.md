# A 파트 설계: 프로젝트 골격 + 인증

- 담당: A
- 브랜치: `feature/auth` → `develop` (PR 1개, 작업 내내 같은 PR에 커밋 누적)
- 기준 문서: 팀 개발 계획서(경제 숏폼 트렌드 챗봇), `mission.md`
- 작성일: 2026-10-05

## 1. 목표와 범위

B·C·D가 바로 올라탈 수 있는 FastAPI 골격과, 회원가입·로그인·로그아웃·접근 제어를 만든다.

| 포함 | 제외 (담당) |
|---|---|
| `main.py`, `config.py`, `database.py`, 공통 에러 형식, 공용 테스트 fixture | 트렌드·Q1·Q4 (B) |
| `users` 테이블, 비밀번호 해싱 | `chats` 모델, 챗봇 파이프라인 (C) |
| `POST /api/auth/signup`, `/login`, `/logout` | 화면, `/api/me/chats`, 배포, README 통합 (D) |
| `require_login`, `get_current_user` 의존성 | JWT, 관리자 화면, Alembic 마이그레이션 |
| README 실행·환경 변수 섹션 | |

완료 기준: 계획서의 A 체크리스트 10개 완료, `pytest` 전체 통과, 의미 있는 커밋 10회 이상.

## 2. 디렉터리 구조

```
app/
├── __init__.py
├── main.py           앱 생성, SessionMiddleware, 로깅 설정, 에러 핸들러·라우터 등록, 시작 시 create_all
├── config.py         pydantic-settings 기반 Settings
├── database.py       engine, SessionLocal, Base, get_db
├── dependencies.py   get_current_user, require_login
├── errors.py         APIError, 공통 에러 핸들러
├── security.py       hash_password, verify_password (bcrypt)
├── models/
│   ├── __init__.py   from .user import User   ← 새 모델은 여기에 import 추가
│   └── user.py
└── routers/
    ├── __init__.py
    └── auth.py
tests/
├── conftest.py       임시 SQLite + TestClient fixture (팀 공용)
└── test_*.py
docs/auth-design.md
requirements.txt, .env.example, .gitignore
```

Python 3.10 이상에서 동작하도록 작성한다 (로컬 개발 환경은 3.12).

## 3. 공용 인터페이스 (B·C·D 사용법)

### 3.1 설정 — `app/config.py`

```python
from app.config import settings
settings.SECRET_KEY
```

`.env`에서 읽는다. 앱에 필요한 키는 A가 미리 선언해 두어 `config.py` 충돌을 줄인다. B·C는 필요하면 이름을 바꿔도 된다.

| 변수 | 필수 | 기본값 | 사용처 |
|---|---|---|---|
| `SECRET_KEY` | O | 없음 (없으면 앱 시작 실패) | 세션 쿠키 서명 (A) |
| `DATABASE_URL` | X | `sqlite:///./app.db` | DB 연결 (A) |
| `NAVER_CLIENT_ID` | X | `""` | 네이버 API (B) |
| `NAVER_CLIENT_SECRET` | X | `""` | 네이버 API (B) |
| `LLM_API_KEY` | X | `""` | LLM API (C) |
| `LLM_MODEL` | X | `""` | LLM 모델 이름 (C) |
| `LLM_TIMEOUT_SECONDS` | X | `30` | LLM 호출 타임아웃 (C) |

`SECRET_KEY` 생성: `python -c "import secrets; print(secrets.token_hex(32))"`

### 3.2 DB — `app/database.py`

```python
from app.database import Base, get_db

class Chat(Base):                      # 모델은 Base 상속
    __tablename__ = "chats"
    ...

@router.get("/api/me/chats")
def my_chats(db: Session = Depends(get_db)): ...
```

- SQLAlchemy 2.0 동기 `Session`. `get_db()`는 요청마다 세션을 열고 끝나면 닫는다. `commit()`은 각 라우터에서 명시적으로 호출한다.
- SQLite 연결 시 `check_same_thread=False`, `PRAGMA foreign_keys=ON`을 적용한다.
- 테이블은 앱 시작 시 `Base.metadata.create_all()`로 만든다. 새 모델은 반드시 `app/models/__init__.py`에 import를 추가해야 생성 대상이 된다.
- 시각 컬럼은 DB 기본값 `CURRENT_TIMESTAMP`(UTC)를 사용한다. `chats.created_at`도 같은 기준을 권장한다.
- SQLite는 기본적으로 삭제된 마지막 id를 재사용하므로, 모델에 `__table_args__ = {"sqlite_autoincrement": True}`를 둔다. `users`는 적용되어 있고 `chats`도 같은 설정을 권장한다.

### 3.3 인증 의존성 — `app/dependencies.py`

```python
from app.dependencies import require_login, get_current_user

@router.post("/api/chat")
async def chat(body: ChatRequest,
               user: User = Depends(require_login),
               db: Session = Depends(get_db)): ...
```

| 함수 | 반환 | 비로그인 시 |
|---|---|---|
| `get_current_user` | `User \| None` | `None` (세션의 user_id가 DB에 없으면 세션을 비우고 `None`) |
| `require_login` | `User` | `401 {"error": "LOGIN_REQUIRED", "message": "로그인이 필요해요."}` |

API 라우트는 `require_login`을 쓴다. 화면 라우트(D)는 `get_current_user`를 받아 `None`이면 `RedirectResponse("/login")`으로 보낸다.

### 3.4 에러 응답 형식 — `app/errors.py`

모든 API 에러는 계획서 형식을 따른다.

```json
{"error": "CODE", "message": "사용자에게 보여줄 문구"}
```

```python
from app.errors import APIError
raise APIError(504, "AI_TIMEOUT", "현재 응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요.")
```

- `APIError(status_code, error, message)`를 던지면 위 형식의 JSON으로 응답한다.
- 요청 본문 검증 실패(`RequestValidationError`)는 `422 INVALID_INPUT`으로 바뀐다.
  - Pydantic validator에서 `ValueError("질문은 1~500자로 입력해 주세요.")`를 던지면 그 문구가 그대로 `message`가 된다.
  - 그 밖의 검증 실패(필드 누락, 타입 오류)는 `"입력값이 올바르지 않아요."`로 응답한다.
- `APIError`가 아닌 FastAPI 기본 예외(존재하지 않는 경로의 404 등)는 기본 형식 `{"detail": ...}`를 유지한다.

### 3.5 로깅

- `main.py`에서 `logging.basicConfig(level=INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")`를 한 번만 설정한다.
- 각 모듈은 `logger = logging.getLogger(__name__)`만 사용한다.
- 이벤트는 `이벤트명 key=value` 형태로 남긴다. 예: `login_success user_id=3`

### 3.6 헬스체크

`GET /health` → `200 {"status": "ok"}`. 배포 후 외부 접속 확인용이며 로그인이 필요 없다.

## 4. 인증 API

| 메서드 | 경로 | 로그인 | 성공 | 실패 |
|---|---|---|---|---|
| POST | `/api/auth/signup` | X | `201 {"id", "email"}` | `422 INVALID_INPUT`, `409 EMAIL_TAKEN` |
| POST | `/api/auth/login` | X | `200 {"id", "email"}` + 세션 쿠키 | `422 INVALID_INPUT`, `401 INVALID_CREDENTIALS` |
| POST | `/api/auth/logout` | O | `204` (본문 없음) | `401 LOGIN_REQUIRED` |

요청 본문은 모두 JSON이다.

### 4.1 회원가입

```json
// 요청
{"email": "creator@example.com", "password": "shorts1234"}
// 201
{"id": 1, "email": "creator@example.com"}
// 409
{"error": "EMAIL_TAKEN", "message": "이미 가입된 이메일이에요."}
// 422
{"error": "INVALID_INPUT", "message": "비밀번호는 8자 이상, 72바이트 이하로 입력해 주세요."}
```

- **이메일**: `email-validator`의 `validate_email(..., check_deliverability=False)`로 형식을 검사하고, 실패하면 `"올바른 이메일 형식이 아니에요."`로 응답한다. (`EmailStr`은 영어 메시지를 내므로 쓰지 않는다.) 저장 전에 앞뒤 공백을 지우고 소문자로 바꾼다.
- **비밀번호**: 8자 이상, UTF-8 기준 72바이트 이하. 72바이트는 bcrypt가 처리할 수 있는 상한이다.
- **중복 가입**: 먼저 조회해서 409로 막는다. 동시 요청으로 UNIQUE 제약 위반(`IntegrityError`)이 나도 rollback 후 409로 응답한다.
- 가입 후 자동 로그인은 하지 않는다. 화면(D)은 가입 성공 시 `/login`으로 이동한다.

### 4.2 로그인

```json
// 요청
{"email": "creator@example.com", "password": "shorts1234"}
// 200 (Set-Cookie: session=...)
{"id": 1, "email": "creator@example.com"}
// 401
{"error": "INVALID_CREDENTIALS", "message": "이메일 또는 비밀번호가 올바르지 않아요."}
```

- 이메일은 형식 검사 없이 빈 값만 막는다(422, `"이메일과 비밀번호를 입력해 주세요."`). 형식이 이상하면 일치하는 사용자가 없으므로 401이 된다.
- 이메일은 가입 때와 같이 앞뒤 공백 제거·소문자 변환 후 조회한다.
- 72바이트를 넘는 비밀번호는 가입될 수 없으므로 bcrypt에 넘기지 않고 바로 불일치(401)로 처리한다. bcrypt 5는 72바이트 초과 입력에 `ValueError`를 던지기 때문에, 그대로 넘기면 500이 된다.
- 이메일이 없을 때와 비밀번호가 틀렸을 때 같은 401 메시지를 보낸다. 가입 여부가 노출되지 않게 하기 위해서다.
- 성공하면 기존 세션을 비운 뒤 `session["user_id"] = user.id`만 저장한다.

### 4.3 로그아웃

세션을 비우고 `204`를 반환한다. 로그인하지 않은 상태면 `require_login`에 의해 `401 LOGIN_REQUIRED`가 된다.

### 4.4 서버 로그 이벤트

| 이벤트 | 레벨 | 필드 |
|---|---|---|
| `signup_success` | INFO | `user_id` |
| `signup_duplicate` | INFO | `email` |
| `login_success` | INFO | `user_id` |
| `login_failed` | WARNING | `email` (형식이 올바른 이메일만 기록, 아니면 `<invalid>`) |
| `logout` | INFO | `user_id` |

비밀번호와 해시는 어떤 로그에도 남기지 않는다.

## 5. 데이터 모델 — `users`

| 필드 | 타입 | 제약 | 설명 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 사용자 식별 (삭제된 id는 재사용하지 않음) |
| `email` | VARCHAR(255) | UNIQUE, INDEX, NOT NULL | 로그인 ID (소문자 정규화) |
| `password_hash` | VARCHAR(60) | NOT NULL | bcrypt 해시 (`$2b$12$...`, 60자) |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 가입 시각 (UTC) |

관계: `users` 1 — N `chats` (`chats.user_id` → `users.id`, C 담당)

## 6. 보안 결정

- **bcrypt 직접 사용**: 계획서의 "passlib/bcrypt" 대신 `bcrypt` 라이브러리의 `hashpw`/`checkpw`만 쓴다. passlib는 2020년 이후 관리되지 않고 bcrypt 4.1 이상과 호환되지 않는다. 저장 형식은 계획서대로 bcrypt 해시다.
- **세션 쿠키**: Starlette `SessionMiddleware`. 서명된 쿠키이며 `httponly`, `same_site="lax"`로 설정한다. VM에 HTTP로 배포할 수 있도록 `https_only=False`로 둔다(True면 HTTP에서 쿠키가 전송되지 않는다).
- **비밀 관리**: `.env`는 커밋하지 않는다. `.env.example`에는 변수 이름과 설명만 둔다.

## 7. 테스트

- 도구: `pytest`, FastAPI `TestClient`(Starlette 1.x는 `httpx2`가 필요하다).
- `tests/conftest.py`:
  1. 앱 import 전에 테스트용 `SECRET_KEY` 환경 변수를 설정한다.
  2. 테스트마다 `tmp_path`에 임시 SQLite 파일을 만들고 `create_all`을 실행한다.
  3. `app.dependency_overrides[get_db]`로 임시 DB 세션을 주입한다. 실제 `app.db`는 건드리지 않는다.
  4. `client` fixture를 제공한다. B·C·D도 같은 fixture를 쓴다.
- 기능마다 실패하는 테스트를 먼저 쓰고 구현한다(TDD).
- 검증 항목:
  - 헬스체크, 에러 응답 형식(`APIError`, `INVALID_INPUT` 변환)
  - 비밀번호 해싱·검증
  - 가입 성공, 이메일 소문자 정규화, 중복 409, 이메일 형식 422, 비밀번호 길이 422(8자 미만, 72바이트 초과)
  - 로그인 성공 시 쿠키 발급, 틀린 비밀번호 401, 없는 이메일 401
  - `get_current_user`/`require_login` 함수 단위 동작
  - 로그아웃 204, 로그아웃 후 다시 로그아웃하면 401, 비로그인 로그아웃 401
  - 삭제된 사용자의 세션은 비로그인으로 처리

## 8. Git 진행

- 브랜치: `main`에서 `develop` 생성 → `develop`에서 `feature/auth` 생성.
- PR: `feature/auth` → `develop` 1개. 첫 push 때 Draft PR로 열고, 이후 커밋은 push하면 같은 PR에 쌓인다. 작업이 끝나면 Ready for review로 전환한다.
- 머지: 팀원 1명 이상 승인 후 **Create a merge commit** 방식으로 머지한다(Squash 금지).
- 커밋 컨벤션: `type(scope): 설명`
- 예정 커밋:
  1. `docs(auth): A 파트 설계 문서 추가`
  2. `chore: .gitignore 추가`
  3. `chore: requirements.txt 및 pytest 설정 추가`
  4. `feat(config): 환경 변수 설정 및 .env.example 추가`
  5. `feat(db): SQLite 연결 및 Base, get_db 추가`
  6. `feat(core): 공통 에러 응답 형식 추가`
  7. `feat(core): FastAPI 앱 골격 및 헬스체크 추가`
  8. `test: 임시 DB를 쓰는 공용 테스트 fixture 추가`
  9. `feat(auth): User 모델 추가`
  10. `feat(auth): bcrypt 비밀번호 해싱 추가`
  11. `feat(auth): 회원가입 API 추가`
  12. `feat(auth): 회원가입 입력 검증 추가`
  13. `feat(auth): 로그인 세션 발급 추가`
  14. `feat(auth): get_current_user, require_login 의존성 추가`
  15. `feat(auth): 로그아웃 추가`
  16. `test(auth): 인증 실패 케이스 보강`
  17. `docs: README 실행 및 환경 변수 섹션 추가`
- 기능 커밋에는 그 기능의 테스트를 함께 넣는다. `require_login`은 보호된 라우트가 생기기 전이라 함수 단위 테스트로 검증하고, 로그아웃 커밋부터 API 테스트로 검증한다.
- 커밋 제외: `.env`, `.venv/`, `app.db`, `mission.md`, 팀 계획서 PDF. 파일을 이름으로 지정해 `git add`한다.
- `requirements.txt`는 설치 시점의 버전을 `==`로 고정해 팀원 환경을 맞춘다.
