export async function apiRequest(path, {method = 'GET', body, timeoutMs = 65000} = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(path, {
      method, credentials: 'same-origin', signal: controller.signal,
      headers: body === undefined ? {'Accept': 'application/json'} : {'Accept': 'application/json', 'Content-Type': 'application/json'},
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      let message = data.message || (typeof data.detail === 'string' ? data.detail : null);
      if (!message && Array.isArray(data.detail)) message = '입력값을 확인해 주세요.';
      if (!message) message = response.status === 401 ? '로그인이 만료되었습니다. 다시 로그인해 주세요.' : '요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.';
      const error = new Error(message);
      error.status = response.status;
      error.code = data.error;
      throw error;
    }
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('응답 대기 시간이 초과되었습니다. 내 기록에서 저장 여부를 확인한 뒤 다시 시도해 주세요.');
    if (error instanceof TypeError) throw new Error('서버에 연결할 수 없습니다. 네트워크 연결을 확인해 주세요.');
    throw error;
  } finally { clearTimeout(timer); }
}

export function showError(element, message) {
  element.textContent = message;
  element.hidden = !message;
}

document.querySelector('#logout-button')?.addEventListener('click', async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  try { await apiRequest('/api/auth/logout', {method: 'POST'}); location.assign('/login'); }
  catch (error) { showError(document.querySelector('#global-error'), error.message); button.disabled = false; }
});
