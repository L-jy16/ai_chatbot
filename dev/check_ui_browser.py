"""Browser smoke checks against a running local demo; screenshots in output/ui."""
import argparse
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def run(base_url: str, *, channel: str | None) -> None:
    output = Path("output/ui")
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel=channel)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(base_url + "/signup")
        page.locator('#email').fill('creator@example.com')
        page.locator('#password').fill('example-pass-2026')
        page.locator('#password-confirm').fill('different-pass')
        page.locator('#auth-submit').click()
        expect(page.locator('#form-error')).to_have_text('비밀번호 확인이 일치하지 않습니다.')
        page.screenshot(path=str(output / 'signup-desktop.png'), full_page=True)
        page.goto(base_url + '/login')
        page.locator('#email').fill('demo@example.com')
        page.locator('#password').fill('wrong-password')
        page.locator('#auth-submit').click()
        expect(page.locator('#form-error')).to_contain_text('확인해 주세요')
        page.locator('#password').fill('demo-pass-2026')
        page.locator('#auth-submit').click()
        expect(page).to_have_url(base_url + '/')
        page.screenshot(path=str(output / 'chat-desktop.png'), full_page=True)

        for index, mode in enumerate(['q1', 'q4', 'q5', 'q6']):
            page.locator(f'[data-mode="{mode}"]').click()
            expect(page.locator(f'[data-mode="{mode}"]')).to_have_attribute('aria-pressed', 'true')
            page.locator('#example-button').click()
            assert page.locator('#message').input_value()
            with page.expect_request('**/api/chat') as request:
                page.locator('#send-button').click()
            assert request.value.post_data_json['mode'] == mode
            expect(page.locator('.message-assistant')).to_have_count(index + 1)
            expect(page.locator('#message')).to_have_value('')

        page.locator('#message').fill('   ')
        page.locator('#send-button').click()
        expect(page.locator('#chat-error')).to_contain_text('1~500자')
        page.locator('#message').fill('[timeout]')
        page.locator('#send-button').click()
        expect(page.locator('#chat-error')).to_contain_text('지연')
        expect(page.locator('#message')).to_have_value('[timeout]')
        expect(page.locator('#send-button')).to_be_enabled()

        # Verify AI text is not interpreted as executable HTML.
        unsafe = '<img src=x onerror="window.__xss=1">'
        page.route('**/api/chat', lambda route: route.fulfill(json={'chat_id': 999, 'answer': unsafe}))
        page.locator('#message').fill('응답 표시 검사')
        page.locator('#send-button').click()
        expect(page.locator('.message-assistant').last).to_contain_text(unsafe)
        assert page.locator('#conversation img').count() == 0
        page.unroute('**/api/chat')
        page.goto(base_url + '/history')
        expect(page.locator('.history-record').first).to_be_visible()
        assert 'PRIVATE USER TWO' not in page.locator('#history-list').inner_text()
        page.locator('.history-record details').first.locator('summary').click()
        page.screenshot(path=str(output / 'history-desktop.png'), full_page=True)
        page.route('**/api/me/chats?*', lambda route: route.fulfill(json=[]))
        page.locator('#refresh-history').click()
        expect(page.locator('#history-empty')).to_be_visible()
        page.unroute('**/api/me/chats?*')
        page.route('**/api/me/chats?*', lambda route: route.fulfill(status=503, json={'detail': '기록 조회 실패 예시'}))
        page.locator('#refresh-history').click()
        expect(page.locator('#history-error')).to_have_text('기록 조회 실패 예시')
        expect(page.locator('#refresh-history')).to_be_enabled()
        page.unroute('**/api/me/chats?*')

        page.set_viewport_size({'width': 375, 'height': 812})
        for path, name in [('/', 'chat-mobile'), ('/history', 'history-mobile')]:
            page.goto(base_url + path)
            if path == '/history':
                expect(page.locator('.history-record').first).to_be_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), f'horizontal overflow: {path}'
            page.screenshot(path=str(output / f'{name}.png'), full_page=True)
        page.locator('#logout-button').click()
        expect(page).to_have_url(base_url + '/login')
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.screenshot(path=str(output / 'login-mobile.png'), full_page=True)
        assert not errors, errors
        browser.close()
    print('Browser checks passed: auth, four modes, timeout recovery, safe text, history states, mobile, logout.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--channel', default=None, help='Use chrome or msedge, or omit for Playwright Chromium')
    args = parser.parse_args()
    run(args.base_url.rstrip('/'), channel=args.channel)
