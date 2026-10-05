# PULSE · 경제 숏폼 트렌드 챗봇

경제·AI 숏폼 제작자를 위한 FastAPI 챗봇입니다. 회원가입·로그인 후 네이버 뉴스·검색 추이를 참고하여 AI와 기획하고, 사용자별 대화 기록을 확인합니다.

## 프로젝트 개요

- **서비스 URL**: 배포 후 기입 (`http://<서버 공인 IP>:8000`, 절차는 [배포 가이드](docs/DEPLOY.md))
- **문제 정의**: AI·경제 정보가 너무 많아, 무엇이 지금 뜨는 주제이고 무엇이 이미 지난 주제인지 구분하기 어렵습니다.
- **타겟 사용자**: 유튜브 경제·AI 숏폼 제작자
- **핵심 원칙**: LLM은 오늘의 이슈를 모르므로, 서버가 네이버 뉴스 검색·데이터랩 검색 추이를 모아 프롬프트에 넣고 답하게 합니다. 자료가 없으면 지어내지 않고 한계를 밝힙니다.

**핵심 흐름**: 로그인한 사용자가 화면에서 모드를 골라 질문 → 서버가 입력을 검증하고 트렌드 자료와 최근 성공 대화 5쌍을 담아 AI를 호출 → 같은 화면에 답변 표시 → 질문·응답·상태를 사용자별 대화 기록으로 저장

**핵심 시나리오**

| 모드 | 사용자 질문 예 | 챗봇이 하는 일 |
| --- | --- | --- |
| Q1 오늘의 주제 | 오늘은 무슨 경제 숏폼을 올려야 해? | 최신 경제 뉴스와 최근/이전 검색 추이를 비교해 추천 주제·내용 정리 |
| Q2 운영 채널 추천 | 기존 영상과 연결해 오늘 올릴 주제를 추천해 줘 | 과거 업로드 주제를 확보한 뒤 관련 자료와 연결한 주제 추천 |
| Q3 타이밍 체크 | 금리 인하 주제, 지금 올려도 괜찮을까? | 검색 관심도를 비교해 지금 올리기 / 기다리기 / 다른 각도 제안 |
| Q4 새로운 각도 | AI 투자 이야기가 너무 흔해. 다른 각도 없을까? | 반전·비교·논쟁·정보·경험형 5~10개 아이디어와 최종 추천 |
| Q5 다음 편 기획 | 어제 환율 상승 영상 다음 편은 어떻게 이어갈까? | 이전 주제에서 1→2→3편 구조와 오늘 올릴 편 제안 |

## 현재 통합 상태

A의 인증·SQLite, B의 트렌드, C의 채팅·AI, D의 PULSE UI를 연결했습니다. 실제 앱은 `app.main:app`이며 다섯 모드 모두 C의 채팅 라우터에서 서버 프롬프트·LLM·대화 저장 경로를 사용합니다. `dev.demo_app:app`은 외부 API를 호출하지 않는 별도의 고정 응답 데모입니다.

뉴스는 최신순 일부 검색 결과이며 인기 순위나 전체 언급량이 아닙니다. 데이터가 없거나 조회에 실패하면 실시간 사실을 지어내지 않고 한계를 알리도록 프롬프트에 명시합니다. 실제 답변 품질과 키 권한은 별도 실서비스 확인이 필요합니다.

## 로컬 실행

Python 3.10 이상. 기존 가상환경과 `.env`가 있으면 그대로 사용하며, 예제 파일로 덮어쓰지 마세요.

macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
# .env가 없을 때만 실행
cp -n .env.example .env
.venv/bin/python -c "import secrets; print(secrets.token_hex(32))"
# 생성한 값을 .env의 SECRET_KEY에 넣고 나머지 API 설정을 채운 뒤 실행
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Windows PowerShell에서는 `.venv/bin/python` 대신 `./.venv/Scripts/python.exe`를 사용합니다. `.env`가 없을 때만 `Copy-Item .env.example .env`로 복사합니다.

1. `http://127.0.0.1:8000/signup`에서 회원가입합니다.
2. `/login`에서 로그인합니다.
3. `/`에서 Q1~Q5 중 하나를 선택해 질문합니다. Q2는 과거 업로드 주제를 먼저 입력합니다.
4. `/history`에서 사용자별 성공·실패 기록을 확인합니다.

상태 확인: `/health`. API 문서: `/docs`. `.env`를 바꾸면 서버를 재시작합니다. 서버는 기본 `app.db`에 users·chats 테이블을 생성합니다.

## 배포

VM 1대에 uvicorn + systemd로 올려 외부에서 `http://<서버 공인 IP>:8000`으로 접속합니다. 전체 절차와 문제 해결은 **[docs/DEPLOY.md](docs/DEPLOY.md)**에 있습니다.

```bash
sudo apt install -y git python3 python3-venv
git clone https://github.com/L-jy16/ai_chatbot.git && cd ai_chatbot
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env && chmod 600 .env        # SECRET_KEY·API 키 입력
sudo cp deploy/ai-chatbot.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now ai-chatbot
curl http://<서버 공인 IP>:8000/health         # 보안 그룹·ufw에서 TCP 8000 허용 후 확인
```

- 서비스 파일: [deploy/ai-chatbot.service](deploy/ai-chatbot.service) (`--host 0.0.0.0 --port 8000 --workers 1`, 앱이 실행 폴더의 `.env`를 읽음)
- 로그: `journalctl -u ai-chatbot -f` (요청 수신·AI 호출·AI 응답/실패·DB 저장 이벤트)
- 업데이트: `git pull` → `pip install -r requirements.txt` → `sudo systemctl restart ai-chatbot`

## 환경 변수와 API 연결

| 변수 | 설명 / 기본값 |
| --- | --- |
| `SECRET_KEY` | 필수 세션 서명 키, 16자 이상 |
| `DATABASE_URL` | `sqlite:///./app.db` |
| `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` | 네이버 뉴스·데이터랩용 인증 쌍 |
| `NAVER_TIMEOUT_SECONDS` | 네이버 개별 요청 제한, 기본 5초 |
| `LLM_API_KEY` | Codyssey에서 발급한 AI 키 |
| `LLM_BASE_URL` | `https://copa.codyssey.kr/v1` |
| `LLM_MODEL` | `.env.example`은 `gpt-5-mini`, 사용 계정의 허용 모델 지정 |
| `LLM_TIMEOUT_SECONDS` | AI 호출 전체 제한, 기본 50초 (gpt-5-mini 추론 응답이 30초를 넘을 수 있어 늘림, 브라우저 제한 65초보다 짧게 유지) |

앱은 실행 폴더의 `.env`를 읽습니다. Codyssey 키로 네이버 API를 조회할 수는 없으며 두 인증은 별개입니다. AI 클라이언트는 [OpenAI Chat Completions 명세](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) 형식으로 설정된 게이트웨이에 요청합니다.

## 민감정보 관리

- **`.env`는 커밋하지 않습니다.** `.gitignore`가 `.env`, `.env.*`(단 `.env.example` 제외), `.venv/`, `*.db`를 제외합니다. 저장소에는 변수 이름과 기본값만 있는 [`.env.example`](.env.example)을 둡니다. 새 키가 생기면 `.env.example`에 이름만 추가합니다.
- **API 키는 서버에서만 씁니다.** LLM·네이버 호출은 모두 서버에서 하고, 브라우저는 같은 출처의 `/api/*`만 호출합니다. `/api/me`는 키 값이 아니라 설정 여부(`true`/`false`)만 알려 줍니다.
- **비밀번호는 bcrypt 해시로만 저장합니다.** 서버 로그에는 비밀번호·해시·API 키·AI 서비스의 원본 오류 본문을 남기지 않고, 로그인 실패 로그에는 형식이 올바른 이메일만 남깁니다.
- **세션 쿠키**는 `SECRET_KEY`로 서명되고 `httponly`·`SameSite=Lax`입니다. `SECRET_KEY`가 없거나 16자 미만이면 서버가 시작되지 않습니다.
- D 페이지는 CSP와 `textContent`로 질문·답변의 HTML 실행을 막습니다.
- 테스트는 외부 API 키를 빈 값으로 고정해 실제 유료 API를 호출하지 않습니다.
- 서버의 `.env`는 `chmod 600`으로 두고, 키가 노출되면 즉시 재발급한 뒤 `.env`만 바꿔 재시작합니다.

## 구조와 연결

```text
app/
├── main.py, config.py, database.py       # 기반·설정·DB
├── dependencies.py, errors.py, security.py
├── models/user.py, chat.py              # 사용자·대화
├── routers/auth.py, chat.py             # 인증·AI 요청
├── routers/pages.py, logs.py            # D 페이지·기록 조회
├── services/trend.py, llm.py            # 네이버·AI
├── services/scenarios/                  # 모드별 프롬프트 (모드↔파일 대응: docs/SCENARIOS.md)
├── ui.py                               # 페이지·static·기록 라우터 등록
├── templates/                          # D Jinja2 템플릿
└── static/css/, static/js/              # D UI
```

`main.py`는 A 인증 라우터와 C의 `create_router(require_login, get_db)`를 등록하고 `install_ui(..., chat_model=Chat)`를 한 번 호출합니다. `/static`, `/`, `/api/me/chats`는 D 등록만 사용하여 중복 경로를 피합니다. 이전 임시 단일 HTML 화면은 제거했습니다.

사용자별 최근 **성공 대화 5개**를 AI에 전달합니다. 외부 동기 HTTP 호출은 스레드로 분리하며 전체 트렌드 준비 시간도 제한합니다. 요청 수신, AI 시작·성공/실패, DB 저장 성공/실패를 기록합니다. 질문·키·AI 서비스의 원본 오류 본문은 로그에 넣지 않습니다.

## API

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| POST | `/api/auth/signup` | 회원가입, 201 |
| POST | `/api/auth/login` | 로그인·세션 쿠키, 200 |
| POST | `/api/auth/logout` | 로그인 필요, 204 |
| GET | `/api/me` | 내 사용자 정보·설정 여부, 키 값 제외 |
| POST | `/api/chat` | 로그인 필요, q1~q5 질문·AI 응답·저장 |
| GET | `/api/me/chats?limit=20` | 내 기록만 최신순, 1~100개, no-store |

```json
{"mode":"q3","message":"금리 인하 주제 지금 올려도 돼?","keyword":"금리 인하"}
```

`keyword`는 API에서 선택적으로 지정할 수 있습니다. UI는 질문에서 키워드를 추출하는 기본 경로를 사용합니다. Q2 UI는 `최근 업로드 주제: ...\n질문: ...`를 한 message로 전송하며 전체 500자 제한을 적용합니다. API에서 맥락 없이 Q2를 호출하면 먼저 과거 업로드 주제를 물어보도록 지시합니다.

성공: `{"chat_id":1,"answer":"..."}`. 비로그인 401, 입력 오류 422, AI 실패 502, 시간 초과 504, 저장 오류 500입니다. 기록 조회 DB 실패는 D 라우터에서 503으로 처리합니다. 시간 초과·AI 오류도 answer=null로 저장합니다.

## 시나리오 번호와 기존 기록

현재 계약은 [docs/SCENARIOS.md](docs/SCENARIOS.md)의 Q1~Q5입니다. **이전 API의 q4 타이밍 호출은 q3로 바꾸세요.** 새 q4는 새로운 각도입니다.

`chats.scenario_version`으로 기록의 번호 체계를 구분합니다. 서버 시작 시 기존 chats 테이블에 해당 열이 없으면 기본 1로 추가하며, 원래 mode·질문·답변은 그대로 보존합니다. 새 기록은 버전 2(화면 Q1~Q5 번호)입니다. 기록 API는 계획서 번호로 저장된 버전 1과 버전 3(C 통합 중 사용)의 q4/q5/q6를 화면 q3/q4/q5로 변환하여 응답합니다. API 응답 필드 수는 기존 계약과 같습니다. SQL에서 원본 mode를 볼 때는 scenario_version도 함께 확인하세요. 스키마 변경은 반복 실행해도 열을 중복 추가하지 않습니다.

users와 chats는 user_id로 연결됩니다. DB 생성 시각은 UTC이며 D 화면은 offset 없는 시각을 `(서버 시각)`으로 표시합니다.

## 트렌드 판정의 한계

한국 시간 어제까지 완료된 14일을 한 번에 조회하여 같은 척도로 비교합니다. 최근 7일 평균이 이전 7일보다 20% 이상 높으면 rising, 20% 이상 낮으면 falling입니다. 그 사이에서 상대지수가 80 이상이면 peak(정점 후보), 나머지는 stable(보합)입니다. 실제 정점을 확정하는 통계 모델은 아닙니다.

빈 응답·14일 데이터 누락·전 기간 0은 unknown, available=false, 평균 null입니다. 검색 상대지수는 조회수나 실제 검색 횟수가 아닙니다.

## 검증과 데모

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
```

테스트는 임시 DB와 모의 외부 응답을 사용하며 실제 유료 API를 호출하지 않습니다. 기존 인증·UI 테스트에 다섯 모드 분기·프롬프트·대화 저장·사용자 격리·오류·구 기록 호환 검사를 포함합니다.

실제 연결 확인은 아래 명령으로 별도 수행할 수 있습니다. **실제 API 사용량이 발생할 수 있습니다.** 임시 DB에서 가입→로그인→Q3 실제 AI 호출→기록을 확인하며 운영 app.db는 수정하지 않습니다.

```bash
.venv/bin/python -m scripts.check_connection
```

UI 전용 데모:

```bash
.venv/bin/python -m pip install -r requirements-ui-dev.txt
.venv/bin/python -m uvicorn dev.demo_app:app --host 127.0.0.1 --port 8001
```

데모 계정은 `demo@example.com` / `demo-pass-2026`입니다. 실제 계정이 아니며 예시 응답과 메모리 DB만 제공합니다. 데모 가입은 503, `[timeout]`·`[error]`는 데모 전용 실패 시뮬레이션입니다. 실제 앱 대신 데모를 운영하지 마세요.

브라우저 검사 도구: `requirements-ui-browser.txt`, `dev/check_ui_browser.py`, `dev/check_auth_browser.py`. 실행법과 D 작업 이력은 [D_HANDOFF.md](docs/D_HANDOFF.md)에 있습니다. 해당 문서의 통합 전 준비 중 상태는 이 README의 현재 상태와 구분합니다.

DB 읽기 전용 검사:

```bash
.venv/bin/python scripts/check_logs.py --db app.db --user-id 1 --limit 20
```

SQLite CLI 예시는 `scripts/check_logs.sql`을 참고하세요. 존재하지 않는 DB는 새로 만들지 않습니다.

## 팀 구성원 역할과 개인별 작업 요약

| 역할 | GitHub (커밋 작성자 이름) | 브랜치 · PR | 개인별 작업 요약 |
| --- | --- | --- | --- |
| A | rlawnsxo8709 | `feature/auth` (#2), 통합 커밋 (#3) | FastAPI 골격(설정·SQLite 연결·공통 에러 형식·로깅), User 모델과 bcrypt 해싱, 회원가입·로그인·로그아웃(세션 쿠키), `require_login`·`get_current_user` 의존성, 가입 입력 검증과 보안 보강(72바이트 비밀번호, 유니코드 이메일 정규화, 로그 마스킹), 인증 테스트와 공용 테스트 fixture. 통합: 화면 Q1~Q5와 시나리오 연결, LLM 응답 토큰·타임아웃 조정, 배포 가이드·README |
| B | L-jy16 | `feature/trend` (#5) | 네이버 API 클라이언트, 뉴스 검색·오늘의 경제 이슈, 데이터랩 검색 추이 조회·최근/과거 비교·상승/하락 판정, Q1 오늘의 주제·Q2 운영 채널 추천·Q3 타이밍 체크 프롬프트, 인증·트렌드·AI·D 화면 1차 연결 |
| C | cds-jihwan (Jipang) | `feature/chat` (#3) | 코디세이 LLM 클라이언트(타임아웃·오류 처리), Chat 모델, `POST /api/chat`(입력 검증·최근 5쌍 문맥·모드 분기), 요청·AI·DB 이벤트 로깅, AI 실패 기록과 DB 롤백, Q4 새로운 각도·Q5 다음 편 프롬프트(`scenarios/q5.py`·`q6.py`), 채팅 API 테스트 |
| D | Kfri-cloud (Kfri) | `feature/ui` (#4) | 공통 템플릿·반응형 스타일, 로그인·회원가입·채팅·내 기록 화면, 모드 선택·예시 질문, 대기·오류·세션 만료 안내, 사용자별 기록 API `GET /api/me/chats`, DB 확인 SQL·스크립트, 독립 데모 앱, 브라우저 검사 |

**통합 과정**: B의 PR #5가 인증·트렌드·AI·D 화면을 처음 연결했습니다. 이후 C의 PR #3에서 채팅 라우터·Chat 모델·LLM 클라이언트를 C의 구현을 기준으로 하나로 합치고, 화면 Q1~Q5 번호와 담당 시나리오를 맞췄습니다(대응표: [docs/SCENARIOS.md](docs/SCENARIOS.md)).

팀 정책은 feature/* → develop → main, PR 리뷰 후 merge commit입니다. 로컬 테스트 성공만으로 완료 표시하지 않고, 실제 API 응답과 배포 후 외부 접속을 따로 확인합니다.
