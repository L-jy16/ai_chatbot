import {apiRequest, showError} from './common.js';
import {MODES} from './modes.js';

const list = document.querySelector('#history-list');
const limit = document.querySelector('#history-limit');
const refresh = document.querySelector('#refresh-history');
const loading = document.querySelector('#history-loading');
const empty = document.querySelector('#history-empty');
const count = document.querySelector('#history-count');
const statuses = {success: '응답 완료', timeout: '응답 시간 초과', error: '응답 실패'};

function textNode(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  node.textContent = text;
  return node;
}
function displayTime(value) {
  if (!value) return '시각 미상';
  // Offset-less DB timestamps have no declared timezone; do not invent one.
  if (!/(Z|[+-]\d{2}:\d{2})$/.test(value)) return `${value.replace('T', ' ').slice(0, 19)} (서버 시각)`;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : `${new Intl.DateTimeFormat('ko-KR', {timeZone: 'Asia/Seoul', dateStyle: 'medium', timeStyle: 'short'}).format(date)} KST`;
}
function renderRecord(record) {
  const article = document.createElement('article');
  article.className = 'card history-record';
  const meta = document.createElement('div');
  meta.className = 'history-meta';
  const time = textNode('time', 'tiny muted', displayTime(record.created_at));
  time.dateTime = record.created_at;
  const status = ['success', 'timeout', 'error'].includes(record.status) ? record.status : 'unknown';
  meta.append(textNode('span', 'mode-tag', MODES[record.mode]?.title || '자유 질문'), time, textNode('span', `status-tag status-${status}`, statuses[record.status] || '상태 확인 필요'));
  article.append(meta, textNode('h3', 'history-question', record.question));
  const details = document.createElement('details');
  details.open = record.status !== 'success';
  details.append(textNode('summary', '', record.answer ? '응답 펼쳐보기' : '처리 결과 확인'));
  details.append(textNode('div', 'message-content history-answer', record.answer ?? 'AI 응답이 저장되지 않았습니다. 주제 찾기에서 다시 질문해 주세요.'));
  article.append(details);
  return article;
}
async function loadHistory() {
  if (refresh.disabled) return;
  refresh.disabled = true;
  limit.disabled = true;
  list.replaceChildren();
  empty.hidden = true;
  loading.hidden = false;
  count.textContent = '기록을 불러오는 중…';
  showError(document.querySelector('#history-error'), '');
  document.querySelector('#history-login').hidden = true;
  try {
    const records = await apiRequest(`/api/me/chats?limit=${encodeURIComponent(limit.value)}`, {timeoutMs: 15000});
    if (!Array.isArray(records)) throw new Error('기록 응답 형식이 올바르지 않습니다.');
    records.forEach(record => list.append(renderRecord(record)));
    empty.hidden = records.length !== 0;
    count.textContent = `최근 대화 ${records.length}개 · 최신순`;
  } catch (error) {
    showError(document.querySelector('#history-error'), error.message);
    document.querySelector('#history-login').hidden = error.status !== 401;
    count.textContent = '조회 실패 · 새로고침으로 다시 시도하세요.';
  } finally { refresh.disabled = false; limit.disabled = false; loading.hidden = true; }
}
refresh.addEventListener('click', loadHistory);
limit.addEventListener('change', loadHistory);
loadHistory();
