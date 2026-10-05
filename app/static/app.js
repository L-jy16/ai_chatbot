'use strict';
const $ = id => document.getElementById(id);
let authMode = 'login', mode = 'q1', busy = false;
async function api(path, options = {}) {
  const response = await fetch(path, {credentials:'same-origin', ...options,
    headers: {'Content-Type':'application/json', ...(options.headers || {})}});
  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith('/api/auth/')) showAuth();
    throw new Error(data?.message || '요청을 처리하지 못했어요. 잠시 후 다시 시도해 주세요.');
  }
  return data;
}
function showAuth() {
  $('auth').hidden=false; $('studio').hidden=true; $('account').hidden=true;
  $('conversation').replaceChildren(); $('history-list').replaceChildren(); $('history-panel').hidden=true;
}
async function showStudio() {
  const user=await api('/api/me');
  $('auth').hidden=true; $('studio').hidden=false; $('account').hidden=false;
  $('email').textContent=user.email;
  const ready=user.trend_configured && user.llm_configured;
  $('data-status').classList.toggle('ready',ready);
  $('data-status').textContent=!user.llm_configured ? 'AI 연결 설정이 필요합니다. 서버의 API 키와 모델 설정을 확인해 주세요.' : user.trend_configured
    ? '뉴스·검색 추이 연결이 설정되어 있습니다. 조회 결과와 데이터의 한계를 답변에 함께 표시합니다.'
    : '네이버 연결 전입니다. AI와 기획 대화는 가능하지만 실시간 이슈·검색 추이는 확인할 수 없습니다.';
}
function selectAuth(next) {
  authMode=next; $('auth-error').textContent='';
  $('login-tab').setAttribute('aria-pressed',next==='login');
  $('signup-tab').setAttribute('aria-pressed',next==='signup');
  $('auth-submit').textContent=next==='login'?'로그인':'회원가입';
  $('auth-password').autocomplete=next==='login'?'current-password':'new-password';
}
$('login-tab').onclick=()=>selectAuth('login'); $('signup-tab').onclick=()=>selectAuth('signup');
$('auth-form').onsubmit=async e=>{
  e.preventDefault(); $('auth-submit').disabled=true; $('auth-error').textContent='';
  const payload={email:$('auth-email').value,password:$('auth-password').value};
  try {
    await api('/api/auth/'+authMode,{method:'POST',body:JSON.stringify(payload)});
    if(authMode==='signup') {
      selectAuth('login'); $('auth-error').textContent='회원가입이 완료되었습니다. 로그인해 주세요.';
    } else { $('auth-password').value=''; await showStudio(); }
  } catch(err) { $('auth-error').textContent=err.message; }
  finally { $('auth-submit').disabled=false; }
};
$('logout').onclick=async()=>{
  try{await api('/api/auth/logout',{method:'POST'});showAuth();}
  catch(err){$('chat-error').textContent=err.message;}
};
function selectMode(next) {
  mode=next; $('q1').setAttribute('aria-pressed',next==='q1'); $('q4').setAttribute('aria-pressed',next==='q4');
  $('keyword-field').hidden=next!=='q4';
  $('send').textContent=next==='q1'?'주제 추천받기 →':'타이밍 분석하기 →';
  $('message').placeholder=next==='q1'?'오늘 만들 경제 숏폼 주제 3개를 추천해 줘.':'금리 인하 주제 지금 올려도 돼?';
}
$('q1').onclick=()=>selectMode('q1'); $('q4').onclick=()=>selectMode('q4');
$('message').oninput=()=>$('counter').textContent=`${$('message').value.length} / 500`;
function bubble(role, text) {
  const empty=$('conversation').querySelector('.empty'); if(empty) empty.remove();
  const div=document.createElement('div'); div.className='bubble '+role;
  const label=document.createElement('strong'); label.textContent=role==='user'?'나':'숏폼 스튜디오';
  const content=document.createElement('div');content.textContent=text;
  div.append(label,content);$('conversation').append(div);return content;
}
$('chat-form').onsubmit=async e=>{
  e.preventDefault(); if(busy) return;
  const message=$('message').value.trim(); if(!message) return;
  const payload={mode,message,keyword:mode==='q4'?$('keyword').value.trim()||null:null};
  busy=true; ['send','logout','q1','q4'].forEach(id=>$(id).disabled=true); $('chat-error').textContent='';
  bubble('user',message); const output=bubble('assistant','자료를 확인하고 답변을 작성하고 있어요…');
  try {
    const data=await api('/api/chat',{method:'POST',body:JSON.stringify(payload)});
    output.textContent=data.answer;
    if($('message').value.trim()===message){$('message').value='';$('counter').textContent='0 / 500';}
  } catch(err){output.textContent='답변을 받지 못했습니다.';$('chat-error').textContent=err.message;}
  finally{busy=false;['send','logout','q1','q4'].forEach(id=>$(id).disabled=false);}
};
$('history-toggle').onclick=async()=>{
  $('history-panel').hidden=!$('history-panel').hidden;
  if($('history-panel').hidden)return;
  $('history-list').textContent='기록을 불러오고 있어요…';
  try{
    const rows=await api('/api/me/chats');$('history-list').replaceChildren();
    if(!rows.length)$('history-list').textContent='아직 저장된 대화가 없습니다.';
    for(const row of rows){
      const details=document.createElement('details');details.className='history-item';
      const summary=document.createElement('summary');summary.textContent=`${row.mode.toUpperCase()} · ${new Date(row.created_at+'Z').toLocaleString('ko-KR')} · ${row.question}`;
      const answer=document.createElement('p');answer.textContent=row.answer || (row.status==='timeout'?'응답 시간 초과':'AI 연결 실패');
      details.append(summary,answer);$('history-list').append(details);
    }
  }catch(err){$('history-list').textContent=err.message;}
};
showStudio().catch(showAuth);
