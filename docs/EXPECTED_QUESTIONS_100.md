# PULSE 예상 질문 100선

작성 기준: 2026-10-06, 현재 작업 폴더 코드·README 및 로컬 Git 이력(확인 당시 HEAD `3bd5f57`).

Q001~Q030은 사용자가 제공한 평가 항목 30개(평가 1: 15개, 평가 2: 8개, 평가 3: 7개)에 순서대로 대응합니다. Q031~Q100은 추가 심화·시연·개인 기여 질문입니다. 질문·답안 번호는 두 문서에서 동일합니다.

답변은 구현과 설계 근거를 설명하는 연습용 초안입니다. 실제 기능 동작은 평가 환경에서 시연해야 합니다. 이번 확인에서 `./.venv/Scripts/python.exe -m pytest -q`는 `ModuleNotFoundError: No module named 'requests'`로 conftest import 중 중단되어 테스트 통과를 확인하지 못했습니다. 실제 AI 호출과 배포 서버 외부 접속도 이번 문서 작업에서 실행하지 않았습니다. 코드·테스트 존재를 실행 성공으로 표현하지 마세요.

[핵심 평가 질문·답안 30선](EVALUATION_PRIORITY_QA.md) · [답안 100선](EXPECTED_ANSWERS_100.md)

질문지만 보고 먼저 답한 뒤 같은 번호의 답안과 코드 근거를 확인하세요.

## 평가 1 · 문서와 기본 동작 · Q001~Q015

<a id="q001"></a>

### Q001. 시스템 구조도는 어디에 있고 어떤 구성요소를 설명하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q001)

<a id="q002"></a>

### Q002. API 명세와 요청·응답 예시는 어떻게 제공하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q002)

<a id="q003"></a>

### Q003. DB 구조와 ERD는 실제 코드와 일치하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q003)

<a id="q004"></a>

### Q004. DB 파일과 저장된 대화는 어떻게 확인하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q004)

<a id="q005"></a>

### Q005. 팀 역할과 개인별 기여는 어디에 정리했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q005)

<a id="q006"></a>

### Q006. 회원가입은 어떤 절차로 동작하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q006)

<a id="q007"></a>

### Q007. 로그인은 어떤 방식으로 동작하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q007)

<a id="q008"></a>

### Q008. 비로그인 사용자는 어떤 기능을 사용할 수 없나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q008)

<a id="q009"></a>

### Q009. 웹 UI에서 질문 입력과 답변 출력이 가능한가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q009)

<a id="q010"></a>

### Q010. 질문부터 AI 호출과 출력까지 전체 흐름을 설명해 주세요.

[답안 보기](EXPECTED_ANSWERS_100.md#q010)

<a id="q011"></a>

### Q011. 사용자·시간·질문·AI 응답이 DB에 저장되나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q011)

<a id="q012"></a>

### Q012. 특정 사용자의 대화 로그만 조회할 수 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q012)

<a id="q013"></a>

### Q013. AI 실패·타임아웃에도 서비스가 계속 동작하도록 했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q013)

<a id="q014"></a>

### Q014. 오류가 발생하면 사용자는 어떤 안내를 받나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q014)

<a id="q015"></a>

### Q015. 어떤 사용자 입력 검증을 구현했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q015)

## 평가 2 · 구조와 협업 · Q016~Q023

<a id="q016"></a>

### Q016. 프로젝트 구조를 역할 단위로 어떻게 나눴나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q016)

<a id="q017"></a>

### Q017. API 라우트는 목적에 맞게 분리되어 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q017)

<a id="q018"></a>

### Q018. 요청·응답 형식의 일관성은 어떻게 관리하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q018)

<a id="q019"></a>

### Q019. 인증 로직을 어떻게 재사용하도록 분리했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q019)

<a id="q020"></a>

### Q020. DB 접근이 라우터와 충분히 분리되어 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q020)

<a id="q021"></a>

### Q021. API 키 같은 민감정보가 코드에 하드코딩되어 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q021)

<a id="q022"></a>

### Q022. .env 예시와 Git 제외 설정을 어떻게 제공하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q022)

<a id="q023"></a>

### Q023. PR 기반 병합과 브랜치 흐름을 증명할 수 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q023)

## 평가 3 · 설계 이유와 운영 추적 · Q024~Q030

<a id="q024"></a>

### Q024. REST 관점에서 엔드포인트와 메서드는 어떤 기준으로 정했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q024)

<a id="q025"></a>

### Q025. 이 서비스에 인증·인가가 왜 필요한가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q025)

<a id="q026"></a>

### Q026. AI 호출을 클라이언트가 아닌 서버에서 하는 이유는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q026)

<a id="q027"></a>

### Q027. AI 지연·실패 정책은 무엇이며 재시도도 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q027)

<a id="q028"></a>

### Q028. 대화 로그를 왜 저장하며 실제 기능에 어떻게 사용하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q028)

<a id="q029"></a>

### Q029. 문제 발생 시 요청·AI·DB 단계의 원인을 추적할 수 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q029)

<a id="q030"></a>

### Q030. 문서의 개인별 기여가 Git 이력과 일치하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q030)

## 서비스 목적과 시나리오 · Q031~Q040

<a id="q031"></a>

### Q031. PULSE가 해결하려는 사용자 문제는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q031)

<a id="q032"></a>

### Q032. 일반적인 자유 대화 챗봇과의 차이는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q032)

<a id="q033"></a>

### Q033. Q1 오늘의 주제는 어떻게 생성하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q033)

<a id="q034"></a>

### Q034. Q2가 과거 업로드 주제를 먼저 묻는 이유는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q034)

<a id="q035"></a>

### Q035. Q3 타이밍 체크는 무엇을 근거로 판단하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q035)

<a id="q036"></a>

### Q036. Q4 새로운 각도는 어떤 결과를 목표로 하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q036)

<a id="q037"></a>

### Q037. Q5 다음 편 기획은 어떤 흐름인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q037)

<a id="q038"></a>

### Q038. 화면 번호와 시나리오 파일 번호가 다른 이유는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q038)

<a id="q039"></a>

### Q039. free 모드는 UI에서도 선택할 수 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q039)

<a id="q040"></a>

### Q040. 이 서비스가 조회수나 투자 성과를 보장하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q040)

## 인증·인가와 보안 · Q041~Q050

<a id="q041"></a>

### Q041. 세션 쿠키에는 무엇이 들어가며 암호화되나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q041)

<a id="q042"></a>

### Q042. HttpOnly·SameSite·Secure 설정은 어떻게 되어 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q042)

<a id="q043"></a>

### Q043. 비밀번호를 평문으로 저장하지 않는 이유와 방법은 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q043)

<a id="q044"></a>

### Q044. 비밀번호 72바이트 제한은 글자 수 제한과 같은가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q044)

<a id="q045"></a>

### Q045. 이메일 대소문자·공백·유니코드 중복은 어떻게 처리하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q045)

<a id="q046"></a>

### Q046. 탈퇴·삭제된 사용자나 변조 쿠키는 어떻게 처리하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q046)

<a id="q047"></a>

### Q047. 로그아웃은 기존 쿠키의 재사용까지 차단하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q047)

<a id="q048"></a>

### Q048. 사용자 ID를 요청에 넣어 타인의 기록을 볼 수 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q048)

<a id="q049"></a>

### Q049. 질문이나 AI 답변에 HTML이 들어오면 어떻게 되나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q049)

<a id="q050"></a>

### Q050. 로그에 민감한 내용을 남기지 않으려면 무엇을 했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q050)

## API 계약과 오류 · Q051~Q060

<a id="q051"></a>

### Q051. 회원가입·로그인·로그아웃의 요청·응답 예시를 말해 주세요.

[답안 보기](EXPECTED_ANSWERS_100.md#q051)

<a id="q052"></a>

### Q052. 채팅 API의 최소 요청과 정상 응답은 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q052)

<a id="q053"></a>

### Q053. 기록 API 응답에는 어떤 필드가 포함되나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q053)

<a id="q054"></a>

### Q054. 왜 401·409·422를 구분하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q054)

<a id="q055"></a>

### Q055. AI 오류는 왜 502나 504이고 DB 오류는 500인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q055)

<a id="q056"></a>

### Q056. Swagger 문서에는 화면 페이지도 표시되나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q056)

<a id="q057"></a>

### Q057. 왜 내 기록 API에는 user_id 경로가 없나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q057)

<a id="q058"></a>

### Q058. 기록 limit과 정렬 방식은 어떻게 정했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q058)

<a id="q059"></a>

### Q059. 클라이언트 검증이 있는데 서버 검증이 또 필요한가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q059)

<a id="q060"></a>

### Q060. 오류 응답 형식이 완전히 통일되어 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q060)

## DB 설계와 저장 · Q061~Q070

<a id="q061"></a>

### Q061. 왜 SQLite와 SQLAlchemy를 선택했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q061)

<a id="q062"></a>

### Q062. users와 chats를 따로 둔 이유는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q062)

<a id="q063"></a>

### Q063. 주요 DB 필드의 자료형과 NULL 조건을 설명해 주세요.

[답안 보기](EXPECTED_ANSWERS_100.md#q063)

<a id="q064"></a>

### Q064. 외래키 제약은 SQLite에서도 실제로 적용하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q064)

<a id="q065"></a>

### Q065. 인덱스와 유일키는 어디에 적용했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q065)

<a id="q066"></a>

### Q066. AI 실패 기록에서 answer가 NULL인 이유는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q066)

<a id="q067"></a>

### Q067. 왜 DB commit 뒤에만 채팅 성공을 반환하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q067)

<a id="q068"></a>

### Q068. scenario_version은 왜 필요하며 구 기록은 어떻게 처리하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q068)

<a id="q069"></a>

### Q069. DB 생성 시각과 화면 시각은 어떤 시간대를 사용하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q069)

<a id="q070"></a>

### Q070. DB 확인 스크립트는 데이터를 변경하거나 새 파일을 만들 수 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q070)

## LLM·트렌드·비동기 처리 · Q071~Q080

<a id="q071"></a>

### Q071. LLM에는 어떤 메시지 묶음을 보내나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q071)

<a id="q072"></a>

### Q072. 왜 최근 성공 대화 5쌍만 사용하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q072)

<a id="q073"></a>

### Q073. AI 호출은 스트리밍인가요, 자동 재시도는 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q073)

<a id="q074"></a>

### Q074. 빈 AI 답변이나 잘못된 응답 형식은 어떻게 처리하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q074)

<a id="q075"></a>

### Q075. 네이버 API 키가 없거나 조회에 실패하면 어떻게 되나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q075)

<a id="q076"></a>

### Q076. 뉴스 목록을 인기 순위나 전체 언급량으로 볼 수 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q076)

<a id="q077"></a>

### Q077. 검색 추이를 왜 14일 한 번의 요청으로 비교하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q077)

<a id="q078"></a>

### Q078. rising·falling·peak·stable·unknown의 차이는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q078)

<a id="q079"></a>

### Q079. 뉴스의 악성 지시문이나 모델의 사실 지어내기를 어떻게 줄이나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q079)

<a id="q080"></a>

### Q080. 동기 네이버 요청이 async 채팅 처리에 미치는 영향은 어떻게 줄였나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q080)

## 시연·테스트·배포·운영 · Q081~Q090

<a id="q081"></a>

### Q081. 평가 때 가장 먼저 어떤 순서로 시연하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q081)

<a id="q082"></a>

### Q082. 실제 앱과 UI 데모는 어떻게 구분하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q082)

<a id="q083"></a>

### Q083. 실제 AI 연결은 어떤 도구로 확인하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q083)

<a id="q084"></a>

### Q084. 단위·통합 테스트는 어떤 중요한 경계를 다루나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q084)

<a id="q085"></a>

### Q085. 테스트 실행이 실제 DB와 유료 API를 건드리지 않게 했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q085)

<a id="q086"></a>

### Q086. 현재 확인 환경에서 테스트가 통과했나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q086)

<a id="q087"></a>

### Q087. 프로세스 재시작과 서버 재부팅에는 어떻게 대응하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q087)

<a id="q088"></a>

### Q088. VM 서비스가 외부에서 안 열리면 무엇부터 확인하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q088)

<a id="q089"></a>

### Q089. 브라우저 대기 시간이 끝나면 서버 처리도 취소되나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q089)

<a id="q090"></a>

### Q090. 동시 요청·처리시간·비용에는 어떤 한계가 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q090)

## 개인 기여·협업·개선·마무리 · Q091~Q100

<a id="q091"></a>

### Q091. A 담당자의 핵심 기여는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q091)

<a id="q092"></a>

### Q092. B 담당자의 핵심 기여는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q092)

<a id="q093"></a>

### Q093. C 담당자의 핵심 기여는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q093)

<a id="q094"></a>

### Q094. D 담당자의 핵심 기여는 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q094)

<a id="q095"></a>

### Q095. 팀 간 인터페이스와 통합은 어떻게 맞췄나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q095)

<a id="q096"></a>

### Q096. 평가 기준 중 가장 설명을 조심해야 할 부분은 무엇인가요?

[답안 보기](EXPECTED_ANSWERS_100.md#q096)

<a id="q097"></a>

### Q097. 운영 환경으로 확장한다면 무엇을 먼저 개선하나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q097)

<a id="q098"></a>

### Q098. DB 백업·개인정보 보관·삭제 정책은 구현되어 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q098)

<a id="q099"></a>

### Q099. 대화방·문맥 선택·확장 가능한 DB 구조는 어떻게 개선할 수 있나요?

[답안 보기](EXPECTED_ANSWERS_100.md#q099)

<a id="q100"></a>

### Q100. 평가 마지막에 이 프로젝트를 어떻게 요약하겠습니까?

[답안 보기](EXPECTED_ANSWERS_100.md#q100)

