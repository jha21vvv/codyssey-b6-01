# 🎧 Google NotebookLM 팟캐스트 기획 안내서 (NOTEBOOKLM_GUIDE.md)

> 본 문서는 Google NotebookLM의 **'Audio Overview(Deep Dive Podcast)'** 기능을 활용하여, 출퇴근이나 이동 중에 귀로 들으며 데이터베이스 모델링과 SQL의 핵심을 완벽히 마스터할 수 있도록 팟캐스트 세션을 기획한 안내서입니다.

---

## 📌 [최우선 확인] NotebookLM 업로드 추천 소스 파일 체크리스트

Google NotebookLM에 새 노트를 만들고 아래 파일들을 순서대로 업로드하세요. (파이썬 `.py` 파일은 업로드가 불가능하므로 사전에 단일 텍스트화된 `NOTEBOOKLM_FULL_SOURCE.txt`를 사용합니다.)

```text
================================================================================
[NotebookLM 업로드 추천 소스 체크리스트]
--------------------------------------------------------------------------------
[x] 1. NOTEBOOKLM_FULL_SOURCE.txt  : SQL 스키마/데이터/15개 쿼리 및 핵심 파이썬 소스 전문
[x] 2. 스터디.md                    : 과제 전문, 1:1 요구사항 매핑, 3개월 차 주니어 일상 비유
[x] 3. REPORT.md                   : 종합 엔지니어링 리포트 (아키텍처 결정, 엣지케이스 방어)
[x] 4. PLAN.md                     : 도메인 선정 이유 및 5개 테이블 스키마 설계 계획서
[x] 5. README.md                   : 프로젝트 종합 소개 및 평가자용 15개 쿼리 실행 결과
================================================================================
```

---

## 🎙️ 1. 팟캐스트 등장인물 (호스트 2인 페르소나)

* **호스트 1 (알렉스 / Alex)**: 
  * 15년 차 시니어 DB 아키텍트이자 백엔드 테크 리드.
  * 성능, 무결성, 정규화, 인덱스 최적화에 진심이며 차분하고 날카로운 통찰력을 제공함.
* **호스트 2 (수민 / Soomin)**: 
  * 호기심 넘치는 3개월 차 주니어 개발자의 멘토.
  * "엑셀이랑 DB가 대체 뭐가 다른가요?", "왜 굳이 중간 테이블을 만들어야 하죠?" 같은 주니어들이 가장 궁금해하는 핵심 질문을 던지고 알기 쉬운 일상 비유로 맞받아침.

---

## 💡 2. 팟캐스트 핵심 토론 주제 및 질문 리스트 (Storyline)

### 세션 1: 엑셀 vs 데이터베이스의 진실
* **수민**: "알렉스, 많은 비전공자나 주니어들이 '엑셀도 행과 열이 있고 필터도 되는데 왜 굳이 복잡한 SQL 데이터베이스를 써야 하나요?'라고 물어봅니다. 한마디로 정리해 주신다면요?"
* **알렉스**: "데이터가 얼마나 많냐가 아니라 **'관계(Relationship)'와 '규칙(Constraint)'**이 있느냐의 차이입니다. 엑셀 시트 하나에 회원 이름, 전화번호, 주문한 커피를 다 넣으면 회원이 전화번호를 바꿀 때마다 10줄, 100줄을 일일이 수정해야 합니다. DB는 회원 서랍장과 영수증 서랍장을 분리하고 외래키(FK)라는 안전한 끈으로 연결하죠."

### 세션 2: N:M 다대다 관계와 `order_items`의 탄생 비화
* **수민**: "이번 프로젝트에서 가장 인상 깊었던 건 '주문'과 '메뉴' 사이에 왜 `order_items`라는 중간 테이블이 들어가야만 했는가예요."
* **알렉스**: "영수증 한 장에 커피 3잔, 케이크 1개가 들어갈 수 있고, 아메리카노라는 메뉴는 수천 명의 영수증에 찍힐 수 있습니다. 이걸 둘이서 직접 연결하려 하면 테이블이 엉망진창이 됩니다. 그래서 '영수증 속 세부 품목 한 줄'이라는 매개체를 만들어 1:N 관계 2개로 우아하게 푼 것이죠. 이것이 바로 이후 JPA/Hibernate를 배울 때 다대다 매핑의 정석입니다."

### 세션 3: INNER JOIN과 LEFT JOIN의 치명적 차이
* **수민**: "신규 회원 중에서 가입만 하고 아직 주문을 한 번도 안 한 손님에게 쿠폰을 보내야 할 때, 왜 INNER JOIN을 쓰면 망하는 건가요?"
* **알렉스**: "INNER JOIN은 양쪽에 모두 도장이 찍힌 사람만 들어오는 파티입니다. 주문 영수증이 없는 신규 회원은 가차 없이 탈락해 버려요! 반면 LEFT JOIN은 왼쪽 회원 명부를 100% 보존하고 영수증 자리를 `NULL`로 비워두기 때문에, `WHERE orders.order_id IS NULL` 조건으로 잠자는 고객을 기가 막히게 건져낼 수 있습니다."

### 세션 4: 인덱스(INDEX)는 공짜 마법인가?
* **수민**: "인덱스를 걸면 검색이 순식간에 빨라지는데, 그럼 모든 컬럼에 다 인덱스를 걸면 안 되나요?"
* **알렉스**: "책 뒷장의 색인표를 생각해 보세요. 단어 하나를 추가할 때마다 색인표를 계속 가나다순으로 다시 정렬해야 합니다. 주문이 쏟아져 들어오는 포스기에서 인덱스가 너무 많으면 INSERT 속도가 처참하게 느려집니다. 조회(SELECT) 빈도와 쓰기(INSERT) 빈도의 완벽한 균형이 필요합니다."

---

## 🎯 3. 3개월 차 주니어가 반드시 얻어가야 할 청취 포인트 3가지

1. **외래키(FK)의 진짜 위치**: 1:N 관계에서 외래키는 무조건 **'N(다)' 쪽 테이블**에 위치해야 한다!
2. **과거 데이터의 불변성**: 메뉴판 가격이 올라도 영수증 상세(`unit_price`)에는 주문 당시의 결제 가격이 스냅샷으로 박제되어야 한다.
3. **WHERE vs HAVING**: 개별 원본 행을 거르는 것은 `WHERE`, 그룹으로 묶어 계산된 합계/평균을 거르는 것은 `HAVING`이다.

---

## 📋 4. Google NotebookLM Customize Audio Overview 전용 프롬프트

Google NotebookLM의 [Customize Audio Overview] 입력창에 아래 프롬프트 중 하나를 복사하여 붙여넣으세요.

### [한국어 버전 프롬프트]
```text
당신은 백엔드 엔지니어링 교육 전문 팟캐스트 호스트 두 사람(시니어 아키텍트 '알렉스'와 주니어 멘토 '수민')입니다.
제공된 스마트 카페 주문 데이터베이스 소스(NOTEBOOKLM_FULL_SOURCE.txt), 스터디 문서(스터디.md), 엔지니어링 리포트(REPORT.md)를 바탕으로 딥다이브 대화를 진행해주세요.

[대화 스타일 및 규칙]
1. 3개월 차 주니어 개발자가 출퇴근길에 편안하게 들으면서도 기술적 핵심을 완벽히 이해할 수 있도록 일상생활 비유(서랍장, 회원 수첩, 영수증 파쇄기, 책 색인표)를 풍부하게 사용하세요.
2. 엑셀과 데이터베이스의 결정적 차이, 다대다(N:M) 관계를 order_items 중간 테이블로 푼 이유, INNER JOIN과 LEFT JOIN의 실무적 차이, 그리고 복합 인덱스(B-Tree)의 원리를 순서대로 자연스럽게 다루어주세요.
3. 한국어로 자연스럽고 에너지 넘치게 대화하며, 주니어 개발자들에게 따뜻한 응원의 메시지로 마무리해주세요.
```

### [English Version Prompt]
```text
You are two podcast hosts—Alex, a 15-year senior database architect, and Soomin, an insightful mentor for junior developers.
Engage in a deep-dive technical yet accessible conversation based on the provided Smart Cafe Ordering Database sources (NOTEBOOKLM_FULL_SOURCE.txt, 스터디.md, REPORT.md).

[Guidelines]
1. Explain relational database fundamentals (Normalization, PK/FK, 1:N relationships, INNER vs LEFT JOIN, GROUP BY/HAVING, and B-Tree indexing) using vivid real-world analogies (receipts, index stickers, file cabinets).
2. Deep dive into why the 'order_items' junction table is essential for decoupling the Many-to-Many relationship between Orders and Menus, and how it prepares developers for JPA/Hibernate.
3. Maintain an engaging, friendly, and intellectually stimulating tone suitable for developers listening during their commute.
```

