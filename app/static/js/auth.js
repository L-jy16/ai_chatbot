import {apiRequest, showError} from './common.js';

const form = document.querySelector('#auth-form');
const button = document.querySelector('#auth-submit');
const errorBox = document.querySelector('#form-error');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (button.disabled || !form.reportValidity()) return;
  showError(errorBox, '');
  const email = form.elements.email.value.trim();
  const password = form.elements.password.value;
  if (form.dataset.action === 'signup' && password !== document.querySelector('#password-confirm').value) {
    showError(errorBox, '비밀번호 확인이 일치하지 않습니다.');
    return;
  }
  if (form.dataset.action === 'signup' && new TextEncoder().encode(password).length > 72) {
    showError(errorBox, '비밀번호는 8자 이상, 72바이트 이하로 입력해 주세요.');
    return;
  }
  button.disabled = true;
  const label = button.textContent;
  button.textContent = '잠시만 기다려 주세요…';
  try {
    await apiRequest(`/api/auth/${form.dataset.action}`, {method: 'POST', body: {email, password}, timeoutMs: 15000});
    location.assign(form.dataset.action === 'signup' ? '/login' : '/');
  } catch (error) { showError(errorBox, error.message); }
  finally { button.disabled = false; button.textContent = label; }
});
