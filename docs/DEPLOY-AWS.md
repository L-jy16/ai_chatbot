# AWS EC2 배포 가이드 (Nginx + uvicorn + systemd)

AWS 서울 리전(`ap-northeast-2`)의 EC2 1대에 이 앱을 올려 `http://<퍼블릭 IP>/`로 접속하게 만드는 절차입니다. 일반 VM용 절차는 [DEPLOY.md](DEPLOY.md)에 있습니다. 이 문서는 AWS에 맞춘 구성으로 두 가지가 다릅니다.

- **Nginx(80)가 앞에서 받고 uvicorn은 `127.0.0.1:8000`에만 엽니다.** 보안 그룹은 80과 22만 열고 8000은 열지 않습니다.
- **비밀값(`.env`)은 SSH로 서버에 직접 복사합니다.** EC2 user-data에는 넣지 않습니다. user-data는 인스턴스 메타데이터와 콘솔에서 다시 볼 수 있기 때문입니다.

이 구성으로 실제 배포해 검증했습니다(2026-10, Ubuntu 24.04, t3.micro).

## 목차

1. [구성](#1-구성)
2. [비용](#2-비용)
3. [준비물](#3-준비물)
4. [방법 A — 자동 배포 스크립트](#4-방법-a--자동-배포-스크립트)
5. [방법 B — 직접 배포](#5-방법-b--직접-배포)
6. [확인](#6-확인)
7. [운영과 업데이트](#7-운영과-업데이트)
8. [정리 — 과금 방지](#8-정리--과금-방지)
9. [문제 해결](#9-문제-해결)

## 1. 구성

```
사용자 브라우저 ──HTTP 80──▶ Internet Gateway ──▶ Public Subnet (10.0.1.0/24)
                                                   └─ EC2 t3.micro (Ubuntu 24.04)
                                                        ├─ Nginx :80  ──proxy──▶ uvicorn 127.0.0.1:8000 (FastAPI, systemd)
                                                        └─ SQLite /home/ubuntu/ai_chatbot/app.db
EC2 ──아웃바운드 443──▶ copa.codyssey.kr (LLM), naverapihub.apigw.ntruss.com (네이버 검색·검색어 트렌드)
```

| 항목 | 값 |
| --- | --- |
| 네트워크 | VPC `10.0.0.0/16`, 퍼블릭 서브넷 `10.0.1.0/24`(퍼블릭 IP 자동 할당), 라우트 `0.0.0.0/0 → IGW` |
| 보안 그룹 인바운드 | TCP 80 ← `0.0.0.0/0`, TCP 22 ← **내 IP/32만**. 8000은 열지 않음 |
| 인스턴스 | t3.micro, Ubuntu 24.04 LTS, gp3 8GiB, IMDSv2 필수 |
| 앱 | systemd 서비스 `ai-chatbot`, 워커 1개(SQLite), 사용자 `ubuntu` |
| 데이터 | EC2 디스크의 SQLite 파일. 인스턴스를 지우면 가입자·대화 기록도 함께 지워진다 |

실제 배포 때 서버 사용량은 메모리 909MiB 중 약 400MiB, 디스크 6.8G 중 2.4G였습니다. uvicorn 프로세스가 약 84MiB를 씁니다.

## 2. 비용

서울 리전 온디맨드 단가입니다(2026-10, AWS 가격표 API 조회).

| 리소스 | 단가 |
| --- | --- |
| EC2 t3.micro | $0.013/시간 |
| EBS gp3 | $0.0912/GB-월 (8GiB ≈ $0.001/시간) |
| 퍼블릭 IPv4 | $0.005/시간 |
| **합계** | **약 $0.019/시간, 하루 약 $0.46, 30일 약 $13.7** |

데이터 전송과 LLM API 사용량은 포함하지 않았습니다. 프리 티어·크레딧 적용 여부는 계정마다 다르니 `aws ec2 describe-instance-types --region ap-northeast-2 --filters Name=free-tier-eligible,Values=true --query 'InstanceTypes[].InstanceType' --output text`로 확인하세요. 다 쓰면 [8. 정리](#8-정리--과금-방지)를 반드시 합니다.

## 3. 준비물

- **AWS IAM 사용자**와 액세스 키. 루트 계정 키는 쓰지 않습니다. 필요한 권한은 서울 리전의 EC2·VPC·보안 그룹·키페어 생성·삭제와 `ec2:Describe*`입니다.
- **로컬 PC**: Linux 또는 WSL2(bash 4 이상), `curl`, `unzip`, `ssh`/`scp`, `git`. AWS CLI v2는 방법 A라면 자동 설치됩니다.
- **이 저장소의 체크아웃**: 배포할 코드가 있는 브랜치(`main`에 아직 머지되지 않았다면 `develop`).
- **앱 `.env`**(로컬, 커밋하지 않음):

| 변수 | 값 |
| --- | --- |
| `SECRET_KEY` | 16자 이상. 비워 두면 서버에서 만든다(방법 A) |
| `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` | Codyssey AI 키와 `.env.example` 기본값 |
| `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` | **네이버 클라우드 플랫폼 NAVER API HUB** Application의 Client ID(10자)·Client Secret(40자). Application에 **뉴스 검색**과 **검색어 트렌드** API를 켜 둔다. 기존 네이버 개발자센터 키(20자·10자)는 HUB 주소에서 쓸 수 없다 |
| `DATABASE_URL` | 서버에서 `sqlite:////home/ubuntu/ai_chatbot/app.db`(절대 경로)로 맞춘다 |

NAVER API HUB는 사용량을 넘으면 과금되므로, 콘솔 Application 목록의 **[한도 및 알림]**에서 한도와 알림을 설정해 두세요.

## 4. 방법 A — 자동 배포 스크립트

[rlawnsxo8709/b3-1](https://github.com/rlawnsxo8709/b3-1)의 Bash 스크립트가 아래 [방법 B](#5-방법-b--직접-배포)의 모든 단계를 자동으로 합니다. 순서는 네트워크 → 보안 그룹 → 키페어 → EC2 → 앱 전송·설치 → 외부 검증입니다.

```bash
git clone https://github.com/rlawnsxo8709/b3-1.git
cd b3-1
cp .env.example .env      # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, APP_SRC를 채운다
```

| `.env` 항목 | 설명 |
| --- | --- |
| `APP_SRC` | 이 앱 저장소 경로(상대 경로는 스크립트 폴더 기준). 두 저장소를 같은 폴더에 나란히 받았다면 `APP_SRC=../ai_chatbot` |
| `APP_ENV_FILE` | 서버로 보낼 앱 `.env`. 비우면 `APP_SRC/.env` |
| `APP_REF` | 배포할 브랜치·커밋. 기본 `HEAD`(지금 체크아웃된 커밋). **커밋된 코드만 올라간다**(`git archive`) |

```bash
./deploy.sh --preflight-only   # 리소스를 만들지 않고 키·IP·앱 코드·.env만 점검
./deploy.sh                    # 생성·설치·검증 (약 3~6분)
./verify.sh                    # 다시 검증
./cleanup.sh                   # 모두 삭제하고 잔여 0건 확인
```

`deploy.sh`를 다시 실행하면 이미 만든 리소스는 건너뜁니다. 앱 커밋이나 `.env`가 바뀌었으면 앱만 다시 설치합니다. DB와 서버의 `SECRET_KEY`는 유지되므로 로그인 세션도 그대로입니다.

## 5. 방법 B — 직접 배포

AWS 콘솔이나 CLI로 직접 만듭니다. 아래 CLI 예시는 서울 리전 기준입니다.

### 5-1. 네트워크와 보안 그룹

1. VPC `10.0.0.0/16`을 만듭니다. 콘솔의 기본 VPC를 써도 됩니다.
2. 퍼블릭 서브넷 `10.0.1.0/24`을 만들고 **퍼블릭 IPv4 자동 할당**을 켭니다.
3. Internet Gateway를 만들어 VPC에 연결합니다. 라우트 테이블에 `0.0.0.0/0 → IGW`를 추가하고 서브넷에 연결합니다.
4. 보안 그룹을 만들고 인바운드 규칙 두 개만 넣습니다.

```bash
aws ec2 authorize-security-group-ingress --group-id <sg-id> --ip-permissions \
  'IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges=[{CidrIp=0.0.0.0/0,Description=HTTP}]' \
  "IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=$(curl -s https://checkip.amazonaws.com)/32,Description=SSH-my-ip}]"
```

### 5-2. EC2

- AMI: Ubuntu 24.04 LTS (x86_64), 유형: t3.micro, 스토리지: gp3 8GiB
- 서브넷·보안 그룹: 위에서 만든 것. 키페어: 새로 만들어 `.pem`을 보관(`chmod 400`)
- 메타데이터: IMDSv2 필수(`HttpTokens=required`)

### 5-3. 서버 기본 설치 (SSH 접속 후)

```bash
ssh -i <키>.pem ubuntu@<퍼블릭 IP>
sudo apt-get update && sudo apt-get install -y nginx python3-venv
```

### 5-4. 앱 코드와 `.env` 올리기 (로컬에서)

커밋된 코드를 묶어 보냅니다. 서버에서 `git clone`해도 되지만, 이 방법은 서버에 git 자격 증명이 필요 없습니다.

```bash
git -C <앱 저장소> archive --format=tar.gz -o /tmp/app.tgz develop
scp -i <키>.pem /tmp/app.tgz ubuntu@<퍼블릭 IP>:/tmp/app.tgz
scp -i <키>.pem <앱 저장소>/.env ubuntu@<퍼블릭 IP>:/tmp/app.env
```

### 5-5. 앱 설치 (서버에서)

```bash
mkdir -p ~/ai_chatbot && tar -xzf /tmp/app.tgz -C ~/ai_chatbot && rm /tmp/app.tgz
cd ~/ai_chatbot
install -m 600 /tmp/app.env .env && rm /tmp/app.env
# DATABASE_URL을 절대 경로로 (없으면 추가)
grep -q '^DATABASE_URL=' .env && sed -i 's#^DATABASE_URL=.*#DATABASE_URL=sqlite:////home/ubuntu/ai_chatbot/app.db#' .env \
  || echo 'DATABASE_URL=sqlite:////home/ubuntu/ai_chatbot/app.db' >> .env
python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip && .venv/bin/pip install -q -r requirements.txt
```

`SECRET_KEY`가 비어 있으면 `.venv/bin/python -c "import secrets; print(secrets.token_hex(32))"`로 만들어 `.env`에 넣습니다.

### 5-6. systemd 서비스

```bash
sudo tee /etc/systemd/system/ai-chatbot.service > /dev/null <<'EOF'
[Unit]
Description=PULSE economy short-form trend chatbot (FastAPI)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ai_chatbot
# 127.0.0.1에만 바인딩한다. 바깥 요청은 Nginx(80)가 넘겨주고, 보안 그룹은 8000을 열지 않는다
ExecStart=/home/ubuntu/ai_chatbot/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now ai-chatbot
curl -s http://127.0.0.1:8000/health    # {"status":"ok"}
```

### 5-7. Nginx 리버스 프록시

LLM 응답이 최대 50초(`LLM_TIMEOUT_SECONDS`)까지 걸릴 수 있어 읽기 시간 제한을 90초로 둡니다.

```bash
sudo tee /etc/nginx/sites-available/default > /dev/null <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    client_max_body_size 1m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_send_timeout 90s;
        proxy_read_timeout 90s;
    }
}
EOF
sudo nginx -t && sudo systemctl reload nginx
```

## 6. 확인

```bash
curl -i http://<퍼블릭 IP>/health                 # 200 {"status":"ok"}
curl -s -o /dev/null -w '%{http_code}\n' http://<퍼블릭 IP>/      # 303 (비로그인 → /login)
curl -sL -o /dev/null -w '%{http_code}\n' http://<퍼블릭 IP>/     # 200 (로그인 화면)
```

브라우저에서 `http://<퍼블릭 IP>/signup`으로 가입하고 로그인한 뒤 질문을 보냅니다. `/history`에서 기록을 확인합니다. HTTP 배포라 비밀번호가 암호화되지 않은 채 전송되므로 테스트 계정만 씁니다.

서버 안 점검:

```bash
systemctl is-active nginx ai-chatbot                                # active active
ss -ltn | grep -E ':80 |:8000 '                                     # 0.0.0.0:80, 127.0.0.1:8000
sudo journalctl -u ai-chatbot --since "10 min ago" | grep -E "ai_call|naver|db_save"
```

## 7. 운영과 업데이트

- **코드 업데이트**: 방법 A는 새 커밋을 체크아웃한 뒤 `./deploy.sh`를 실행합니다. 방법 B는 5-4·5-5의 코드 부분을 반복한 뒤 `sudo systemctl restart ai-chatbot`을 실행합니다.
- **`.env` 변경**: 서버 `.env`를 고치고 `sudo systemctl restart ai-chatbot`을 실행합니다. 방법 A는 로컬 `.env`를 고치고 `./deploy.sh`를 실행하면 다시 올라갑니다.
- **로그**: `sudo journalctl -u ai-chatbot -f`. 요청·AI 호출·DB 저장·네이버 실패가 남고 키와 비밀번호는 남지 않습니다.
- **백업**: 서비스를 멈춘 뒤 `app.db`를 복사합니다.

## 8. 정리 — 과금 방지

방법 A는 `./cleanup.sh` 한 번으로 끝납니다. 직접 만들었다면 아래 순서로 지웁니다. 의존 관계 때문에 순서가 중요합니다.

1. EC2 인스턴스 종료(Terminate). 루트 EBS는 함께 삭제되는지 확인합니다.
2. 남은 EBS 볼륨과 탄력적 IP(만들었다면)를 삭제·해제합니다.
3. 보안 그룹을 삭제합니다.
4. 라우트 테이블 연결을 해제하고 삭제합니다.
5. Internet Gateway를 분리하고 삭제합니다.
6. 서브넷 → VPC 순서로 삭제합니다.
7. 키페어를 삭제하고 로컬 `.pem`도 지웁니다.

다음 날 Billing 화면에서 새 요금이 없는지 확인합니다. 정리하면 SQLite의 가입자·대화 기록도 함께 사라집니다.

## 9. 문제 해결

| 증상 | 원인과 조치 |
| --- | --- |
| 브라우저가 `502 Bad Gateway` | Nginx는 떴지만 앱이 안 떴다. `sudo journalctl -u ai-chatbot -n 50`. `SECRET_KEY` 누락·16자 미만이 흔한 원인 |
| 외부에서 접속 안 됨(시간 초과) | 라우트 `0.0.0.0/0 → IGW` → 보안 그룹 80 → 퍼블릭 IP → `ss -ltn`에서 `0.0.0.0:80` 순서로 확인 |
| SSH가 시간 초과 | 네트워크가 바뀌어 내 IP가 달라졌다. 보안 그룹 22번 소스를 지금 IP/32로 바꾼다 |
| 트렌드 자료 없음, 로그에 `naver_request_failed` | 키가 NAVER API HUB 키인지 확인한다(개발자센터 키는 HUB에서 401). HUB가 401 "요청한 API는 이 Application에서 활성화되어 있지 않습니다"를 돌려주면 그 API(뉴스 검색 또는 검색어 트렌드)를 Application에 켠다 |
| 검색어 트렌드가 새벽에만 비교 불가 | 데이터랩은 전날 수치를 다음 날 늦게 반영한다. 앱은 어제 값이 없으면 하루 앞당긴 14일로 비교한다 |
| 채팅이 502 `AI_ERROR` / 504 `AI_TIMEOUT` | 로그의 `ai_call_fail` 사유. `LLM_API_KEY`·`LLM_MODEL`·`LLM_BASE_URL`, `LLM_TIMEOUT_SECONDS`(50 권장) |
