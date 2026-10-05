export const MODES = {
  q1: {title: '오늘의 주제', description: '최근·과거 트렌드와 오늘의 핫이슈', guide: '최근·과거 트렌드를 비교하고 최신 토픽과 오늘의 핫이슈를 반영해, 오늘 만들 숏폼의 주제와 내용을 정리합니다.', placeholder: '오늘은 무슨 경제 숏폼을 올려야 해?', example: '오늘은 무슨 경제 숏폼을 올려야 해? 요즘과 과거 트렌드를 비교하고 오늘 핫한 이슈도 알려줘.'},
  q2: {title: '운영 채널 추천', description: '과거 업로드와 연결한 오늘의 주제', guide: '먼저 과거 업로드 주제를 알려주세요. 연결된 주제의 최신 내용을 분석해 오늘 올릴 주제와 내용을 정리합니다.', placeholder: '경제 숏폼 채널을 운영 중이야. 기존 영상과 연결해 오늘 올릴 주제를 추천해 줘.', example: '기존 영상과 연결된 요즘 이슈를 업데이트해서 오늘 올릴 숏폼의 주제와 내용을 정리해 줘.', previousTopics: 'AI 반도체 투자, 환율 상승'},
  q3: {title: '타이밍 체크', description: '지금 / 기다리기 / 다른 각도', guide: '만들고 싶은 주제의 검색량·이슈성·최근 언급량과 과거 유사 트렌드를 비교해, 지금 올리기 / 조금 기다리기 / 다른 각도로 바꾸기를 제안합니다.', placeholder: '금리 인하 주제, 지금 올려도 괜찮을까?', example: '금리 인하 주제, 지금 올려도 괜찮을까? 이미 많이 소비됐는지 아직 상승 중인지 분석해 줘.'},
  q4: {title: '새로운 각도', description: '다섯 가지 관점으로 5~10개 아이디어', guide: '흔히 다룬 관점을 피해 반전형·비교형·논쟁형·정보형·경험형으로 주제 5~10개를 만들고, 조회 가능성이 높은 방향을 추천합니다.', placeholder: 'AI 투자 이야기가 너무 흔해. 다른 각도에서 다룰 아이디어를 알려줘.', example: 'AI 투자 이야기가 너무 흔해. 다섯 가지 관점으로 숏폼 주제 5~10개를 만들고 가장 유망한 방향을 추천해 줘.'},
  q5: {title: '다음 편 기획', description: '이전 영상에서 1→2→3편 시리즈로', guide: '이전 영상의 주제를 입력해 주세요. 관련 키워드와 파생 이슈에서 후속 후보를 찾고 1편 → 2편 → 3편 구조와 오늘 올릴 다음 편을 추천합니다.', placeholder: '어제 환율 상승 영상을 올렸어. 다음 편은 어떻게 이어갈까?', example: '어제 환율 상승 영상을 올렸어. 관련 키워드와 파생 이슈로 1편 → 2편 → 3편을 기획하고 오늘 올릴 다음 편을 추천해 줘.'},
};

export function setupModes(onChoose) {
  const buttons = [...document.querySelectorAll('[data-mode]')];
  const input = document.querySelector('#message');
  const exampleButton = document.querySelector('#example-button');
  const topics = document.querySelector('#previous-topics');
  let selected = 'q1';
  function select(value) {
    if (!MODES[value]) return;
    selected = value;
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.mode === value)));
    input.placeholder = MODES[value].placeholder;
    document.querySelector('#selected-mode').textContent = MODES[value].title;
    document.querySelector('#mode-guide').textContent = MODES[value].guide;
    document.querySelector('#channel-context').hidden = value !== 'q2';
    topics.disabled = value !== 'q2';
    topics.required = value === 'q2';
    onChoose(value);
  }
  buttons.forEach(button => button.addEventListener('click', () => select(button.dataset.mode)));
  exampleButton.addEventListener('click', () => {
    input.value = MODES[selected].example;
    if (selected === 'q2') topics.value = MODES[selected].previousTopics;
    input.dispatchEvent(new Event('input'));
    input.focus();
  });
  select(selected);
  return {setBusy(busy) {
    buttons.forEach(button => { button.disabled = busy; });
    exampleButton.disabled = busy;
    topics.disabled = busy || selected !== 'q2';
  }};
}
