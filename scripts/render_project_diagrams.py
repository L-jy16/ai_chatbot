"""Render repository-grounded Korean diagrams as SVG and high-resolution PNG."""
from pathlib import Path
from html import escape
import json
import shutil
import zipfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'diagrams'
DOCS = ROOT / 'docs' / 'images' / 'diagrams'
W, H = 2000, 1300
NAVY = '#15263f'
INK = '#22354f'
MUTED = '#63758a'
BLUE = '#3067d7'
TEAL = '#098875'
PURPLE = '#7956bd'
ORANGE = '#bd6a20'
COLORS = [BLUE, TEAL, PURPLE, ORANGE]


class Diagram:
    def __init__(self, number, title, subtitle):
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
                      '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#63758a"/></marker></defs>']
        self.rect(0, 0, W, H, '#f5f8fc', radius=0)
        self.rect(0, 0, W, 205, NAVY, radius=0)
        self.text(80, 56, f'PULSE  /  PROJECT DIAGRAMS  /  {number:02}', 21, '#a8c6ff', True)
        self.text(80, 118, title, 46, '#ffffff', True)
        self.text(80, 166, subtitle, 23, '#c7d5e8')
        self.line([(80, 1220), (1920, 1220)], '#d9e3ef', 2)
        self.text(80, 1260, '기준: 현재 저장소 코드·README  |  2026.10.06', 20, MUTED)
        self.text(1920, 1260, f'PULSE  ·  {number:02} / 04', 20, MUTED, anchor='end')

    def rect(self, x, y, w, h, fill='white', stroke=None, radius=18, dash=None):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="2"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')

    def text(self, x, y, value, size=25, fill=INK, bold=False, anchor='start', mono=False):
        family = 'Consolas, monospace' if mono else 'Malgun Gothic, sans-serif'
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}" text-anchor="{anchor}">{escape(str(value))}</text>')

    def lines(self, x, y, values, size=24, fill=MUTED, gap=39):
        for i, value in enumerate(values):
            self.text(x, y + i * gap, value, size, fill)

    def line(self, points, color=MUTED, width=3, arrow=False, dash=None):
        data = ' '.join(f'{x},{y}' for x, y in points)
        self.parts.append(f'<polyline points="{data}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"' + (' marker-end="url(#arrow)"' if arrow else '') + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')

    def label(self, x, y, value, color=MUTED, size=21):
        self.text(x, y, value, size, color, anchor='middle')

    def card(self, x, y, w, h, title, lines, color=BLUE, tag=None, size=24):
        self.rect(x, y, w, h, 'white', '#d7e2ef')
        self.rect(x, y, 7, h, color, radius=3)
        self.text(x + 25, y + 49, title, 29, color, True)
        if tag:
            self.text(x + w - 22, y + 44, tag, 19, MUTED, anchor='end')
        self.lines(x + 25, y + 94, lines, size, INK, 38)

    def finish(self):
        return ''.join(self.parts) + '</svg>'


def erd():
    d = Diagram(1, 'DB 구조 · ERD', 'SQLite / SQLAlchemy  ·  users 1명은 chats 0개 이상을 소유합니다.')
    rows_u = [('PK', 'id', 'INTEGER', 'NOT NULL · AUTOINCREMENT'),
              ('UK', 'email', 'VARCHAR(255)', 'NOT NULL · UNIQUE · INDEX'),
              ('', 'password_hash', 'VARCHAR(60)', 'NOT NULL · bcrypt'),
              ('', 'created_at', 'DATETIME', 'NOT NULL · CURRENT_TIMESTAMP')]
    rows_c = [('PK', 'id', 'INTEGER', 'NOT NULL · AUTOINCREMENT'),
              ('FK', 'user_id', 'INTEGER', 'NOT NULL · INDEX → users.id'),
              ('', 'mode', 'VARCHAR(10)', 'NOT NULL'),
              ('', 'scenario_version', 'INTEGER', 'NOT NULL · DEFAULT 2'),
              ('', 'question', 'TEXT', 'NOT NULL'),
              ('', 'answer', 'TEXT', 'NULL 허용'),
              ('', 'status', 'VARCHAR(10)', 'NOT NULL'),
              ('', 'created_at', 'DATETIME', 'NOT NULL · CURRENT_TIMESTAMP')]
    def table(x, y, w, rows, title, color, owner):
        h = 140 + 72 * len(rows)
        d.rect(x, y, w, h, 'white', '#d7e2ef')
        d.rect(x, y, w, 82, color)
        d.rect(x, y + 50, w, 32, color, radius=0)
        d.text(x + 28, y + 53, title, 34, 'white', True)
        d.text(x + w - 28, y + 51, owner, 21, '#ffffff', anchor='end')
        d.text(x + 28, y + 120, 'KEY', 19, MUTED, True)
        d.text(x + 96, y + 120, 'COLUMN', 19, MUTED, True)
        d.text(x + 398, y + 120, 'TYPE / CONSTRAINT', 19, MUTED, True)
        for i, (key, field, typ, constraint) in enumerate(rows):
            yy = y + 140 + 72 * i
            if i % 2 == 0:
                d.rect(x + 1, yy, w - 2, 72, '#f4f7fc', radius=0)
            d.text(x + 28, yy + 42, key, 22, color, True)
            d.text(x + 96, yy + 42, field, 25, INK, True, mono=True)
            d.text(x + 398, yy + 29, typ, 23, INK, mono=True)
            d.text(x + 398, yy + 57, constraint, 17, MUTED)
    table(80, 270, 760, rows_u, 'users  ·  사용자', BLUE, 'A 김준택')
    table(1160, 270, 760, rows_c, 'chats  ·  대화 기록', PURPLE, 'C 정지환')
    # Crow's foot: exactly one user and zero-to-many chat rows.
    d.line([(840, 540), (1160, 540)], MUTED, 4)
    d.line([(868, 522), (868, 558)], MUTED, 4)
    d.line([(882, 522), (882, 558)], MUTED, 4)
    d.parts.append('<circle cx="1115" cy="540" r="10" fill="#f5f8fc" stroke="#63758a" stroke-width="3"/>')
    d.line([(1137, 540), (1160, 520)], MUTED, 3)
    d.line([(1137, 540), (1160, 560)], MUTED, 3)
    d.label(1000, 486, '소유 · 1 : 0..N', INK, 25)
    d.label(1000, 591, 'users.id = chats.user_id', MUTED, 18)
    d.card(80, 755, 760, 177, '관계와 무결성', ['대화 1개는 반드시 사용자 1명에 속함', '모든 SQLite 연결에서 foreign_keys=ON'], BLUE)
    d.card(80, 1010, 590, 170, 'PK / FK / UK', ['PK 기본키 · FK 외래키 · UK 유일키', '생성 시각은 DB 기본값으로 UTC 저장'], BLUE, size=22)
    d.card(705, 1010, 590, 170, '애플리케이션 검증', ['mode: q1~q5 / free · 질문: 1~500자', 'mode·status 값에는 DB CHECK 제약 없음'], TEAL, size=22)
    d.card(1330, 1010, 590, 170, '실패와 기존 기록', ['status: success / timeout / error', 'AI 실패: answer=NULL · 새 기록 버전=2'], PURPLE, size=22)
    return d.finish()


def architecture():
    d = Diagram(2, '아키텍처 · 서비스 구성', '브라우저 → FastAPI → 시나리오·AI → SQLite  ·  외부 API는 서버에서 호출합니다.')
    d.rect(450, 230, 1110, 832, '#edf3fc', '#b8cee9', 24)
    d.text(480, 273, 'Ubuntu VM  ·  배포 구성', 28, NAVY, True)
    d.text(480, 318, 'systemd → Uvicorn  |  0.0.0.0:8000  |  worker 1', 23, MUTED)
    d.card(80, 425, 310, 230, '사용자 브라우저', ['PULSE · 반응형 화면', 'Jinja2 / HTML / CSS / JS', '로그인 · 채팅 · 내 기록'], ORANGE, size=21)
    d.card(480, 425, 285, 230, 'FastAPI · A', ['app.main:app', 'SessionMiddleware', '세션 인증 · 입력 검증'], BLUE, size=22)
    d.card(830, 375, 310, 362, '라우터 · A / C / D', ['A  /api/auth/*', 'C  POST /api/chat', 'D  GET /api/me/chats', 'users 생성·조회', 'chats 문맥·저장·조회', 'SQLAlchemy ORM'], BLUE, size=23)
    d.card(1200, 365, 330, 210, '시나리오·트렌드', ['B  Q1~Q3 · 뉴스·검색 추이', 'C  Q4~Q5 프롬프트', 'system 프롬프트 구성'], TEAL, size=21)
    d.card(1200, 630, 330, 170, 'LLM 클라이언트 · C', ['httpx · ask_llm()', '타임아웃 · 오류 처리'], PURPLE, size=23)
    d.card(1600, 365, 320, 210, '네이버 API', ['뉴스 검색', '데이터랩 검색 추이', '최근 7일 / 이전 7일 비교'], TEAL, size=21)
    d.card(1600, 630, 320, 170, 'Codyssey LLM API', ['chat/completions', '질문·문맥 → AI 답변'], PURPLE, size=23)
    d.card(830, 895, 470, 135, 'SQLite · app.db', ['users [A]  ·  chats [C]'], BLUE, size=24)
    d.line([(390, 540), (480, 540)], arrow=True)
    d.label(435, 522, 'HTTP', size=20)
    d.line([(765, 540), (830, 540)], arrow=True)
    d.line([(1140, 463), (1200, 463)], arrow=True)
    d.line([(1530, 463), (1600, 463)], arrow=True)
    d.line([(1140, 705), (1200, 705)], arrow=True)
    d.line([(1530, 705), (1600, 705)], arrow=True)
    d.line([(985, 737), (985, 895)], arrow=True)
    d.label(1094, 833, '요청별 DB 세션', size=20)
    d.text(480, 855, '서버 설정 · A', 24, BLUE, True)
    d.lines(480, 895, ['config.py / .env', '세션 키 · DB URL', '네이버·LLM 인증 키'], 21)
    d.text(1600, 891, '외부 서비스', 25, MUTED, True)
    d.lines(1600, 934, ['연결 화살표는 요청 방향', '응답은 같은 경로로 반환'], 22)
    d.card(80, 1100, 1840, 96, '통합', [], NAVY)
    d.text(235, 1159, 'main.py에서 인증·채팅·UI·기록 API를 등록  /  API 키는 서버 설정에서만 사용  /  VM은 저장소의 배포 구성 기준', 24, INK)
    return d.finish()


def system_flow():
    d = Diagram(3, '시스템 구조 · 채팅 처리 흐름', '로그인 사용자 기준  ·  최근 성공 대화 5쌍과 외부 자료를 함께 AI에 전달합니다.')
    steps = [
        (80, 260, '01  질문 전송 · D UI', ['Q1~Q5 모드 선택 · 질문 입력', 'POST /api/chat + 세션 쿠키', 'Q2는 과거 업로드 주제를 함께 전송'], ORANGE),
        (740, 260, '02  인증·입력 검증 · A / C', ['세션 user_id → 실제 사용자 확인', 'mode · 질문 길이 1~500자 검증', '인증 실패 401 · 입력 오류 422'], BLUE),
        (1400, 260, '03  대화 문맥 조회 · C', ['SQLite에서 본인 기록만 조회', '성공·답변 있는 최근 5쌍', '시간순 user / assistant 메시지 구성'], PURPLE),
        (1400, 560, '04  시나리오 자료 구성 · B / C', ['모드별 system 프롬프트 생성', '필요한 뉴스·검색 추이 조회', '자료 부족·조회 실패 한계를 명시'], TEAL),
        (740, 560, '05  AI 호출 · C', ['system + 이전 대화 + 현재 질문', 'Codyssey LLM API 1회 호출', 'success / timeout / error 결정'], PURPLE),
        (80, 560, '06  대화 기록 저장 · C', ['user_id · mode · 질문 · 답변 · 상태', 'AI 실패도 answer=NULL로 저장', 'DB 저장 실패: rollback → 500'], BLUE),
        (80, 860, '07  결과 표시 · D UI', ['DB commit 후 응답 반환', '성공 200 · AI timeout 504 · error 502', '같은 화면에 답변·오류 표시'], ORANGE),
        (740, 860, '08  내 기록 조회 · D', ['GET /api/me/chats?limit=20', '인증된 본인 기록만 최신순 반환', '기본 20개 · 최대 100개'], ORANGE),
    ]
    for x, y, title, lines, color in steps:
        d.card(x, y, 520, 218, title, lines, color, size=23)
    d.line([(600, 370), (740, 370)], arrow=True)
    d.line([(1260, 370), (1400, 370)], arrow=True)
    d.line([(1660, 478), (1660, 560)], arrow=True)
    d.line([(1400, 670), (1260, 670)], arrow=True)
    d.line([(740, 670), (600, 670)], arrow=True)
    d.line([(340, 778), (340, 860)], arrow=True)
    d.line([(600, 970), (740, 970)], arrow=True)
    d.label(670, 951, '별도 요청', size=21)
    d.card(1400, 860, 520, 218, 'DB에서 지키는 경계', ['모든 대화는 users.id와 FK로 연결', '사용자 ID는 세션 인증 결과 사용', '기록 조회·문맥 조회 모두 본인으로 제한'], NAVY, size=22)
    d.text(80, 1150, '현재 화면 번호: Q1 오늘의 주제  ·  Q2 운영 채널 추천  ·  Q3 타이밍 체크  ·  Q4 새로운 각도  ·  Q5 다음 편 기획', 26, INK, True)
    return d.finish()


def team():
    d = Diagram(4, '팀 역할 · 책임 관계도', 'README의 확인된 담당 정보 기준  ·  프로젝트·담당자 관계를 표현한 개념도입니다.')
    d.rect(680, 250, 640, 135, NAVY)
    d.text(1000, 303, 'PULSE', 36, 'white', True, anchor='middle')
    d.text(1000, 350, '경제 숏폼 트렌드 챗봇 · FastAPI 통합 서비스', 25, '#c7d5e8', anchor='middle')
    d.line([(1000, 385), (1000, 435)], width=3)
    d.line([(280, 435), (1720, 435)], width=3)
    owners = [
        ('A', '김준택', 'rlawnsxo8709', 'feature/auth', '기반 · 인증 · 통합', ['FastAPI 설정 · SQLite 연결', 'User 모델 · bcrypt 해싱', '회원가입·로그인·로그아웃', '세션 쿠키 · 인증 의존성', '모드 통합 · 배포 구성·문서']),
        ('B', '이지영', 'L-jy16', 'feature/trend', '트렌드 · 시나리오', ['네이버 뉴스 · 데이터랩', '최근·과거 검색 추이 비교', '상승·하락·보합 판정', 'Q1 오늘의 주제 · Q2 채널', 'Q3 타이밍 체크']),
        ('C', '정지환', 'cds-jihwan', 'feature/chat', '채팅 · AI · 대화 저장', ['Chat 모델 · /api/chat', 'LLM 클라이언트 · 오류 처리', '최근 성공 대화 5쌍 문맥', 'AI 실패 기록 · DB 롤백', 'Q4 새로운 각도 · Q5 다음 편']),
        ('D', '김정현', 'Kfri-cloud', 'feature/ui', '화면 · 기록 조회 · 검증', ['Jinja2 · 반응형 UI', '로그인·채팅·내 기록 화면', 'GET /api/me/chats', 'DB 확인 SQL·스크립트', 'UI 데모 · 브라우저 검사']),
    ]
    for i, (role, name, github, branch, responsibility, items) in enumerate(owners):
        x = 80 + i * 480
        color = COLORS[i]
        d.line([(x + 200, 435), (x + 200, 505)], arrow=True)
        d.rect(x, 505, 400, 442, 'white', '#d7e2ef')
        d.rect(x, 505, 400, 85, color)
        d.rect(x, 560, 400, 30, color, radius=0)
        d.text(x + 25, 560, f'{role}  {name}', 34, 'white', True)
        d.text(x + 25, 627, github, 23, MUTED)
        d.text(x + 25, 671, responsibility, 25, color, True)
        d.lines(x + 25, 720, items, 22, INK, 39)
        d.text(x + 25, 921, branch, 22, MUTED, mono=True)
    d.rect(80, 1000, 1840, 188, '#eaf0fa', '#d7e2ef')
    d.text(110, 1046, '모듈 간 연결', 28, NAVY, True)
    d.text(110, 1093, 'A → C / D    인증·DB 의존성 제공', 25, BLUE, True)
    d.text(1010, 1093, 'B → C    트렌드 자료·프롬프트 제공', 25, TEAL, True)
    d.text(110, 1147, 'C → D    Chat 모델·대화 기록 제공', 25, PURPLE, True)
    d.text(1010, 1147, 'D → A / C / D API    UI에서 기능 호출', 25, ORANGE, True)
    return d.finish()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    diagrams = [('01-db-erd', erd()), ('02-architecture', architecture()),
                ('03-system-flow', system_flow()), ('04-team-roles', team())]
    for name, svg in diagrams:
        (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel='msedge')
        page = browser.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1.5)
        for name, svg in diagrams:
            page.set_content('<html><head><meta charset="utf-8"><style>body{margin:0}svg{display:block}</style></head><body>' + svg + '</body></html>')
            page.evaluate('document.fonts.ready')
            page.screenshot(path=str(OUT / f'{name}.png'))
            print(f'{name}.png: 3000 x 1950')
        # Compact overview retains the original SVG text and routes.
        content = '<html><head><meta charset="utf-8"><style>body{margin:0;background:#e2e8f0;display:grid;grid-template-columns:1000px 1000px;gap:12px;padding:12px}svg{width:1000px;height:650px;display:block}</style></head><body>' + ''.join(svg for _, svg in diagrams) + '</body></html>'
        page.set_viewport_size({'width': 2036, 'height': 1336})
        page.set_content(content)
        page.screenshot(path=str(OUT / '00-overview.png'), full_page=True)
        browser.close()
    notes = '''# PULSE 다이어그램 이미지

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
'''
    (OUT / 'README.md').write_text(notes, encoding='utf-8')
    DOCS.mkdir(parents=True, exist_ok=True)
    for file in sorted(OUT.iterdir()):
        if file.suffix in {'.png', '.svg', '.md'}:
            shutil.copy2(file, DOCS / file.name)
    with zipfile.ZipFile(OUT / 'pulse-diagrams.zip', 'w', zipfile.ZIP_DEFLATED) as bundle:
        for file in sorted(OUT.iterdir()):
            if file.suffix in {'.png', '.svg', '.md'}:
                bundle.write(file, file.name)
    print(json.dumps({'output': str(OUT), 'images': len(diagrams) + 1}, ensure_ascii=False))


if __name__ == '__main__':
    main()
