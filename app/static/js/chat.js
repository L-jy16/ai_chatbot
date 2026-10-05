import {apiRequest, showError} from './common.js';
import {setupModes} from './modes.js';

const form = document.querySelector('#chat-form');
const input = document.querySelector('#message');
const send = document.querySelector('#send-button');
const errorBox = document.querySelector('#chat-error');
const conversation = document.querySelector('#conversation');
const waiting = document.querySelector('#waiting-status');
const loginAgain = document.querySelector('#login-again');
const topics = document.querySelector('#previous-topics');
let mode = 'q1';

function requestMessage() {
  const question = input.value.trim();
  return mode === 'q6' && question && topics.value.trim()
    ? `최근 업로드 주제: ${topics.value.trim()}\n질문: ${question}` : question;
}
function updateCount() {
  document.querySelector('#char-count').textContent = `${requestMessage().length} / 500`;
}
export function chooseMode(value) { mode = value; updateCount(); }
const modes = setupModes(chooseMode);

function appendMessage(kind, text) {
  document.querySelector('#welcome')?.remove();
  const article = document.createElement('article');
  article.className = `message message-${kind}`;
  const label = document.createElement('p');
  label.className = 'message-label';
  label.textContent = kind === 'user' ? '나의 질문' : 'PULSE · 아이디어';
  const content = document.createElement('div');
  content.className = 'message-content';
  content.textContent = text;
  article.append(label, content);
  conversation.append(article);
  conversation.scrollTop = conversation.scrollHeight;
  return article;
}

input.addEventListener('input', updateCount);
topics.addEventListener('input', updateCount);
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    form.requestSubmit();
  }
});
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (send.disabled) return;
  const message = requestMessage();
  if (!message || message.length > 500) {
    showError(errorBox, '질문은 1~500자로 입력해 주세요.');
    input.focus();
    return;
  }
  showError(errorBox, '');
  loginAgain.hidden = true;
  send.disabled = true;
  input.disabled = true;
  modes.setBusy(true);
  waiting.hidden = false;
  form.setAttribute('aria-busy', 'true');
  send.textContent = '응답 기다리는 중…';
  const pendingQuestion = appendMessage('user', message);
  try {
    const data = await apiRequest('/api/chat', {method: 'POST', body: {mode, message}});
    if (typeof data.answer !== 'string' || !data.answer.trim()) throw new Error('응답 내용이 비어 있습니다. 잠시 후 다시 시도해 주세요.');
    appendMessage('assistant', data.answer);
    input.value = '';
    document.querySelector('#char-count').textContent = '0 / 500';
  } catch (error) {
    pendingQuestion.remove();
    showError(errorBox, error.message);
    loginAgain.hidden = error.status !== 401;
  } finally {
    waiting.hidden = true;
    form.setAttribute('aria-busy', 'false');
    send.textContent = '질문 보내기 ↗';
    send.disabled = false;
    input.disabled = false;
    modes.setBusy(false);
    input.focus();
  }
});
