"""Check real A authentication and D pages against an isolated local test DB."""
import argparse
from pathlib import Path
import uuid

from playwright.sync_api import expect, sync_playwright


def run(base_url: str, *, channel: str | None) -> None:
    output = Path('output/ui')
    output.mkdir(parents=True, exist_ok=True)
    email = f'ui-test-{uuid.uuid4().hex}@example.com'
    password = 'integration-pass-2026'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel=channel)
        page = browser.new_page(viewport={'width': 1440, 'height': 1100})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base_url + '/signup')
        expect(page.locator('.demo-credentials')).to_have_count(0)
        page.locator('#email').fill(email)
        page.locator('#password').fill('가' * 25)
        page.locator('#password-confirm').fill('가' * 25)
        page.locator('#auth-submit').click()
        expect(page.locator('#form-error')).to_contain_text('72바이트')
        page.locator('#password').fill(password)
        page.locator('#password-confirm').fill(password)
        with page.expect_response('**/api/auth/signup') as response:
            page.locator('#auth-submit').click()
        assert response.value.status == 201
        expect(page).to_have_url(base_url + '/login')
        page.locator('#email').fill(email)
        page.locator('#password').fill('wrong-password')
        page.locator('#auth-submit').click()
        expect(page.locator('#form-error')).to_contain_text('올바르지 않아요')
        page.locator('#password').fill(password)
        with page.expect_response('**/api/auth/login') as response:
            page.locator('#auth-submit').click()
        assert response.value.status == 200
        expect(page).to_have_url(base_url + '/')
        expect(page.locator('#send-button')).to_be_disabled()
        expect(page.locator('.demo-banner')).to_contain_text('준비 중')
        page.screenshot(path=str(output / 'auth-connected-desktop.png'), full_page=True)
        page.goto(base_url + '/history')
        expect(page.locator('#history-error')).to_contain_text('대화 기록 기능을 준비 중')
        page.set_viewport_size({'width': 375, 'height': 812})
        page.goto(base_url + '/')
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.screenshot(path=str(output / 'auth-connected-mobile.png'), full_page=True)
        with page.expect_response('**/api/auth/logout') as response:
            page.locator('#logout-button').click()
        assert response.value.status == 204
        expect(page).to_have_url(base_url + '/login')
        page.goto(base_url + '/history')
        expect(page).to_have_url(base_url + '/login')
        assert not errors, errors
        browser.close()
    print('Real auth browser checks passed: signup, byte validation, login, private pages, pending backend, mobile, 204 logout.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8001')
    parser.add_argument('--channel', default=None)
    args = parser.parse_args()
    run(args.base_url.rstrip('/'), channel=args.channel)
