# 📑 [종합 엔지니어링 리포트] 스마트 카페 주문 데이터베이스 시스템 (REPORT.md)

> **프로젝트명**: 스마트 카페 주문 및 고객 관리 관계형 데이터베이스 시스템  
> **기준 프레임워크**: `PROJECT_WORKFLOW_PROMPT_TEMPLATE.md` (Step 5)  
> **작성일자**: 2026-10-29  
> **엔지니어링 표준**: Zero-Dependency Python 3.10+ & ANSI 표준 SQL

---

## 1. 핵심 아키텍처 및 모델링 의사결정 (Architecture Decision Record)

### 1.1 다대다(N:M) 관계 해소 및 제3정규형(3NF) 모델링
* **문제 상황**: 
  * "한 번의 주문(Order)은 여러 개의 메뉴(Menu)를 담을 수 있고, 하나의 메뉴(Menu)는 여러 주문에 포함될 수 있다"는 전형적인 N:M 관계가 발생합니다.
* **의사결정**:
  * 주문과 메뉴 사이에 `order_items`라는 매개 엔티티(Intersection Table)를 도입하여 **1:N 관계 2개(`orders -> order_items`, `menus -> order_items`)로 분해**했습니다.
  * 이는 이후 JPA/Hibernate 같은 ORM을 도입할 때 `@OneToMany` - `@ManyToOne` 양방향 연관관계 매핑의 표준 구조가 됩니다.
* **이점**:
  * 과거 결제 당시의 판매 단가(`unit_price`)와 주문 수량(`quantity`)을 스냅샷으로 영구 보존할 수 있습니다. (메뉴판 가격이 인상되어도 과거 결제 영수증 불변성 유지)

### 1.2 자료구조 및 복잡도 분석
* **인덱스 알고리즘**: SQLite B-Tree (Balanced Tree)
* **시간 복잡도**:
  * 기본키(PK) 및 인덱스 단건 조회: $O(\log N)$
  * 외래키(FK) 조인: $O(M \log N)$ (인덱스 기반 Nested Loop Join)
  * 풀 테이블 스캔(인덱스 미사용 시): $O(N)$

---

## 2. 테스트 자동화 결과 통계 (Test Automation Report)

* **테스트 도구**: Python 내장 `unittest` 프레임워크 (무설치 Zero-Cost)
* **실행 모드**: 인메모리 SQLite (`:memory:`) - 디스크 I/O 배제
* **테스트 실행 시간**: **0.032초 (32ms)**
* **테스트 케이스 수**: 총 7개
* **테스트 통과율**: **100% (7/7 PASS)**

```text
test_cascade_delete_order_items (TestCafeDatabase) .......... ok
test_foreign_key_constraint_enforcement (TestCafeDatabase) ... ok
test_minimum_row_count (TestCafeDatabase) ................... ok
test_not_null_constraint_enforcement (TestCafeDatabase) ...... ok
test_q01_to_q15_execution_integrity (TestCafeDatabase) ...... ok
test_tables_created (TestCafeDatabase) ....................... ok
test_unique_constraint_enforcement (TestCafeDatabase) ........ ok

----------------------------------------------------------------------
Ran 7 tests in 0.032s

OK
```

---

## 3. 발견된 엣지 케이스 및 기술적 해결 내역

### 3.1 SQLite 외래키(FK) 기본 비활성화 방어
* **현상**: SQLite는 하위 호환성을 이유로 기본 설정에서 외래키 제약조건(`FOREIGN KEY`) 검사가 꺼져(`OFF`) 있습니다. 이로 인해 부모 테이블에 없는 엉뚱한 ID를 삽입해도 에러 없이 통과되는 치명적인 참조 무결성 훼손이 발생할 수 있습니다.
* **해결**: 모든 DDL 및 세션 연결 시 최우선 순위로 `PRAGMA foreign_keys = ON;` 명령을 강제 실행하여 미아 데이터 삽입을 원천 차단했습니다.

### 3.2 Windows 콘솔 한글/이모지 cp949 인코딩 충돌 방어
* **현상**: Windows PowerShell/CMD 터미널의 기본 코드페이지(cp949) 환경에서 유니코드 이모지(🚀, ✅ 등) 출력 시 `UnicodeEncodeError: 'cp949' codec can't encode character` 예외가 발생하며 프로세스가 비정상 종료되었습니다.
* **해결**: `sys.stdout.reconfigure(encoding='utf-8')`을 선제적으로 구성하고, 터미널 로그에는 `[RUN]`, `[SUCCESS]`와 같은 무결성 보장 텍스트 태그를 적용하여 호환성을 100% 확보했습니다.

### 3.3 화폐 계산 시 부동소수점 누적 오차 방어
* **현상**: 금융/결제 데이터에서 `FLOAT`나 `REAL` 타입을 사용할 경우 $0.1 + 0.2 = 0.30000000000000004$ 와 같은 IEEE 754 부동소수점 오차가 발생하여 매출 합계 불일치가 일어날 수 있습니다.
* **해결**: 대한민국 원화(KRW) 결제 특성에 맞추어 모든 금액(`price`, `total_amount`, `unit_price`, `points`) 컬럼을 정수형(`INTEGER`)으로 통일하여 1원의 오차도 없는 회계 정합성을 달성했습니다.

### 3.4 LEFT JOIN 집계 시 NULL 전파 및 COALESCE 방어
* **현상**: 판매 이력이 없는 신메뉴를 `LEFT JOIN`할 경우 `SUM(quantity)`의 결과가 `0`이 아닌 `NULL`로 반환되어 API 응답이나 UI 화면에 빈칸이 노출되는 결함이 발생합니다.
* **해결**: `COALESCE(SUM(oi.quantity), 0)` 함수를 적용하여 주문 내역이 없는 신메뉴도 정확하게 `0`개로 안전하게 표시되도록 방어했습니다.

### 3.5 B-Tree 복합 인덱스 설계 및 EXPLAIN 실행 계획 증명
* **현상**: 회원별 주문 내역 조회 시 회원이 수십만 명으로 늘어나면 `orders` 테이블 전체를 뒤지는 풀 테이블 스캔(SCAN orders)이 발생하여 지연이 심화됩니다.
* **해결**: `CREATE INDEX idx_orders_member_ordered_at ON orders (member_id, ordered_at DESC);`를 생성했습니다.
* **검증**: `EXPLAIN QUERY PLAN` 결과 `SEARCH orders USING INDEX idx_orders_member_ordered_at (member_id=?)`가 출력됨을 확인하여 $O(\log N)$ 인덱스 탐색이 정상 작동함을 입증했습니다.

---

## 4. 평가자 검증 및 시각화 공간 (Evaluator Verification Guide)

평가자는 터미널에서 아래 단 한 줄의 명령어로 15개 쿼리의 실시간 동작과 포맷팅 테이블을 즉시 확인할 수 있습니다:

```bash
python scripts/verify_requirements.py
```

### [실행 결과 요약]
- **테이블 생성**: 5개 테이블 정상 구축 (`members`, `categories`, `menus`, `orders`, `order_items`)
- **샘플 데이터**: 총 67행 적재 (전 테이블 최소 10행 이상 충족)
- **15개 쿼리**: 기본조회 4개, 조인 4개, 집계 3개, 서브쿼리 1개, 수정 1개, 삭제 1개, 인덱스 1개 전원 정상 통과
- **캡처 저장 위치**: `captures/query_execution_results.md`

