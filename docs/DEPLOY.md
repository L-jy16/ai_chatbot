# 배포 가이드 (Ubuntu VM + uvicorn + systemd)

VM 1대에 앱을 올려 외부에서 `http://<서버 공인 IP>:8000`으로 접속할 수 있게 만드는 절차입니다. Ubuntu 22.04(Python 3.10) 또는 24.04(Python 3.12) 기준입니다.

## 0. 준비물

- 공인 IP가 있는 Ubuntu VM과 SSH 접속
- 클라우드 콘솔의 보안 그룹(방화벽)에서 **인바운드 TCP 8000** 허용 (소스 `0.0.0.0/0`)
- 키: `LLM_API_KEY`(Codyssey), `NAVER_CLIENT_ID`·`NAVER_CLIENT_SECRET`(네이버 클라우드 플랫폼 NAVER API HUB Application, 뉴스 검색·검색어 트렌드 API를 켜 둔 것). `SECRET_KEY`는 서버에서 새로 만듭니다.

아래 명령은 사용자 `ubuntu`, 설치 경로 `/home/ubuntu/ai_chatbot` 기준입니다. 다르면 경로를 바꿔 실행하세요.

## 1. 패키지 설치

```bash
sudo apt update
sudo apt install -y git python3 python3-venv
python3 --version   # 3.10 이상이어야 한다
```

## 2. 코드 받기

```bash
cd ~
git clone https://github.com/L-jy16/ai_chatbot.git
cd ai_chatbot
git checkout main   # 배포 브랜치. develop이 main에 머지되기 전이면 develop
```

## 3. 가상환경과 의존성

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

## 4. 환경 변수 (.env)

```bash
cp .env.example .env
.venv/bin/python -c "import secrets; print(secrets.token_hex(32))"   # 출력값을 SECRET_KEY에 넣는다
nano .env
chmod 600 .env   # 소유자만 읽을 수 있게
```

| 변수 | 넣을 값 |
| --- | --- |
| `SECRET_KEY` | 위에서 만든 64자 값 (16자 이상 필수, 비어 있으면 서버가 시작되지 않음) |
| `DATABASE_URL` | `sqlite:////home/ubuntu/ai_chatbot/app.db` (절대 경로 권장, 슬래시 4개) |
| `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` | NAVER API HUB Application의 Client ID(10자)·Client Secret(40자). Application에 **뉴스 검색**과 **검색어 트렌드** API가 켜져 있어야 한다. 사용량 초과 시 과금되므로 [한도 및 알림]을 설정해 둔다 |
| `LLM_API_KEY` | Codyssey AI 키 |
| `LLM_BASE_URL`, `LLM_MODEL` | `.env.example` 값 그대로 (`https://copa.codyssey.kr/v1`, `gpt-5-mini`) |
| `LLM_TIMEOUT_SECONDS` | `50` (추론 모델 응답이 30초를 넘을 수 있음. 브라우저 제한 65초보다 짧게 유지) |

`.env`는 `.gitignore`에 포함되어 있어 커밋되지 않습니다. 서버 밖으로 복사하거나 채팅·문서에 붙여넣지 마세요.

## 5. 직접 실행해서 확인

```bash
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

다른 SSH 창에서:

```bash
curl http://127.0.0.1:8000/health   # {"status":"ok"}
```

확인했으면 `Ctrl+C`로 종료합니다. 첫 실행 때 `users`·`chats` 테이블이 자동으로 만들어집니다.

## 6. systemd 서비스로 등록

SSH를 끊어도 계속 실행되고, 서버가 재부팅되거나 앱이 죽으면 자동으로 다시 시작됩니다.

```bash
sudo cp deploy/ai-chatbot.service /etc/systemd/system/ai-chatbot.service
sudo nano /etc/systemd/system/ai-chatbot.service   # User와 경로가 서버와 맞는지 확인
sudo systemctl daemon-reload
sudo systemctl enable --now ai-chatbot
sudo systemctl status ai-chatbot   # active (running) 확인
```

## 7. 방화벽 열고 외부 접속 확인

1. 클라우드 콘솔 보안 그룹에서 인바운드 TCP 8000을 허용합니다.
2. 서버에서 `ufw`를 쓴다면 SSH를 먼저 허용한 뒤 8000을 엽니다.

   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 8000/tcp
   sudo ufw status
   ```

3. **내 PC**에서 확인합니다.

   ```bash
   curl http://<서버 공인 IP>:8000/health   # {"status":"ok"}
   ```

4. 브라우저에서 `http://<서버 공인 IP>:8000/signup` → 회원가입 → 로그인 → 질문 → `/history`까지 확인합니다.
5. 확인한 주소를 README의 **서비스 URL**에 적습니다.

## 8. 로그와 DB 확인

```bash
journalctl -u ai-chatbot -f                                   # 실시간 로그
journalctl -u ai-chatbot --since "10 min ago" | grep -E "request_received|ai_call|db_save"
.venv/bin/python scripts/check_logs.py --db /home/ubuntu/ai_chatbot/app.db --user-id 1 --limit 20
```

서버 로그에는 요청 수신(`request_received`), AI 호출(`ai_call_start`), AI 응답·실패(`ai_call_success`/`ai_call_fail`), DB 저장(`db_save_success`/`db_save_fail`)이 남습니다. 비밀번호와 키는 남지 않습니다.

## 9. 코드·설정 업데이트

```bash
cd ~/ai_chatbot
git pull
.venv/bin/pip install -r requirements.txt
sudo systemctl restart ai-chatbot
```

`.env`를 고친 뒤에도 `sudo systemctl restart ai-chatbot`으로 다시 시작해야 반영됩니다.

## 10. (선택) 80번 포트로 열기 — nginx

주소에서 `:8000`을 빼고 싶을 때만 합니다.

```bash
sudo apt install -y nginx
sudo tee /etc/nginx/sites-available/ai-chatbot > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 90s;   # AI 응답(최대 50초)과 트렌드 조회 시간을 고려
    }
}
EOF
sudo ln -sf /etc/nginx/sites-available/ai-chatbot /etc/nginx/sites-enabled/ai-chatbot
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

이후 서비스 파일의 `--host 0.0.0.0`을 `--host 127.0.0.1`로 바꾸고(`daemon-reload` 후 재시작), 보안 그룹·ufw에서 8000 대신 80을 엽니다.

## 문제 해결

| 증상 | 확인할 것 |
| --- | --- |
| 서비스가 바로 종료됨 | `journalctl -u ai-chatbot -n 50`. `SECRET_KEY` Field required / at least 16 characters면 `.env`의 `SECRET_KEY` |
| 외부에서 접속 안 됨 | 보안 그룹 8000, `sudo ufw status`, `ss -ltnp \| grep 8000`에서 `0.0.0.0:8000`인지 |
| 채팅이 502 `AI_ERROR` | 로그의 `ai_call_fail ... detail=` 사유. `LLM_API_KEY`·`LLM_MODEL`·`LLM_BASE_URL` |
| 채팅이 504 `AI_TIMEOUT` | `LLM_TIMEOUT_SECONDS`(권장 50, 60 이하) |
| 답변에 트렌드 자료가 없음 | 로그의 `naver_unavailable`(키 없음)·`naver_request_failed`(인증 실패 등). 키가 NAVER API HUB에서 발급한 것(Client ID 10자·Secret 40자)인지, Application에 뉴스 검색·검색어 트렌드 API가 켜져 있는지. 켜지 않은 API는 HUB가 401 "요청한 API는 이 Application에서 활성화되어 있지 않습니다"를 돌려준다 |
| `.env`를 바꿨는데 그대로 | `sudo systemctl restart ai-chatbot` |

## 보안 메모

- 이 절차는 HTTP 배포입니다. 세션 쿠키와 비밀번호가 암호화되지 않은 채 전송되므로, 실제 서비스에서는 도메인을 연결하고 HTTPS(nginx + certbot)를 적용하세요. 앱은 `https_only=False`라 HTTP에서도 로그인이 동작합니다.
- 키가 외부에 노출되면 즉시 재발급하고 `.env`만 바꾼 뒤 재시작합니다.
- SQLite 파일(`app.db`)에 사용자와 대화 기록이 있습니다. 백업은 서비스를 멈춘 뒤 파일을 복사합니다.
