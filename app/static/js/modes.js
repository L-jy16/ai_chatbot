export const MODES = {
  q1: {title: '오늘의 주제', description: '뜨는 이슈에서 다음 콘텐츠 찾기', placeholder: '오늘 올릴 경제 숏폼 주제를 추천해 줘. 최근에는 AI 반도체를 다뤘어.', example: '오늘 올릴 경제 숏폼 주제를 추천해 줘. 최근에는 AI 반도체를 다뤘어.'},
  q4: {title: '타이밍 체크', description: '지금 올릴까, 조금 기다릴까?', placeholder: '금리 인하 주제, 지금 올려도 괜찮을까?', example: '금리 인하 주제, 지금 올려도 괜찮을까?'},
  q5: {title: '새로운 각도', description: '익숙한 주제에 나만의 관점 더하기', placeholder: 'AI 투자 이야기가 너무 흔해. 다른 각도에서 다룰 아이디어를 알려줘.', example: 'AI 투자 이야기가 너무 흔해. 다른 각도에서 다룰 아이디어를 알려줘.'},
  q6: {title: '다음 편 기획', description: '한 편의 이야기를 시리즈로 잇기', placeholder: '어제 환율 상승 영상을 올렸어. 다음 편은 어떻게 이어갈까?', example: '어제 환율 상승 영상을 올렸어. 다음 편은 어떻게 이어갈까?'},
};

export function setupModes(onChoose) {
  const buttons = [...document.querySelectorAll('[data-mode]')];
  const input = document.querySelector('#message');
  const exampleButton = document.querySelector('#example-button');
  let selected = 'q1';
  function select(value) {
    if (!MODES[value]) return;
    selected = value;
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.mode === value)));
    input.placeholder = MODES[value].placeholder;
    document.querySelector('#selected-mode').textContent = MODES[value].title;
    onChoose(value);
  }
  buttons.forEach(button => button.addEventListener('click', () => select(button.dataset.mode)));
  exampleButton.addEventListener('click', () => {
    input.value = MODES[selected].example;
    input.dispatchEvent(new Event('input'));
    input.focus();
  });
  select(selected);
  return {setBusy(busy) {
    buttons.forEach(button => { button.disabled = busy; });
    exampleButton.disabled = busy;
  }};
}
