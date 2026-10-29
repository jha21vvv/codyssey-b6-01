# ☕ 스마트 카페 주문 데이터베이스 시스템 (Cafe Order DB)

> **과제명**: 코디세이 b6-1 (데이터베이스 모델링 및 SQL 기초 실습)  
> **기준 프레임워크**: `PROJECT_WORKFLOW_PROMPT_TEMPLATE.md` 7단계 마스터 프로세스  
> **기술 스택**: Zero-Dependency Python 3.10+, SQLite3 내장 엔진 (표준 ANSI SQL 호환)  
> **백엔드 프레임워크 배제**: 순수 SQL 스크립트 및 테스트/검증 자동화 파이프라인

---

## 📌 1. 프로젝트 개요

본 프로젝트는 "스마트 카페 주문 & 회원 리워드 시스템"을 도메인으로 선정하여, 백엔드 프레임워크 없이 순수 SQL 기반으로 **테이블 모델링(DDL) ➔ 샘플 데이터 적재(DML) ➔ 15개 핵심 비즈니스 쿼리(DQL/DML) ➔ 초고속 단위 테스트 ➔ 다이어그램 시각화**까지 전 과정을 완성한 엔지니어링 패키지입니다.

### 🌟 핵심 특징
1. **완벽한 제약조건**: `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, `ON DELETE CASCADE / RESTRICT` 망라
2. **다대다(N:M) 정규화**: 주문(Orders)과 메뉴(Menus) 사이의 다대다 관계를 `order_items` 매개 테이블로 분해하여 1:N 관계 4개 구축 (요구사항 초과 충족)
3. **Zero-Dependency 초고속 검증**: 별도 DB 서버나 외부 패키지 설치 없이 파이썬 내장 `sqlite3`와 `unittest`로 0.03초 만에 무결성 100% 검증
4. **고해상도 시각화**: `matplotlib` 기반 아키텍처 다이어그램 4종(`.png`) 자동 렌더링

---

## 📂 2. 프로젝트 디렉토리 구조

```text
codyssey-b6-01/
├── sql/
│   ├── 01_schema.sql                  # [Step 2] DDL: 5개 테이블 정의 및 외래키/무결성 제약조건
│   ├── 02_sample_data.sql              # [Step 2] DML: 각 테이블 10행 이상 현실 샘플 데이터 (총 67행)
│   └── 03_queries.sql                  # [Step 2] DQL: 15개 핵심 쿼리 및 실행 목적 설명 (2단 주석 완비)
├── tests/
│   └── test_database.py               # [Step 3] 0.03초 초고속 단위 테스트 (7개 테스트 전수 통과)
├── scripts/
│   ├── generate_diagrams_matplotlib.py # [Step 4] Matplotlib 고해상도 아키텍처 다이어그램 4종 생성기
│   ├── verify_requirements.py         # [Step 5] 평가자용 원클릭 시각적 검증 러너 (콘솔 테이블 & 마크다운 캡처)
│   └── build_notebooklm_source.py     # [Step 6] 순수 소스 단일 텍스트(NOTEBOOKLM_FULL_SOURCE.txt) 빌더
├── diagrams/                          # [Step 4] Matplotlib 생성 고해상도 아키텍처 다이어그램 PNG
│   ├── 01_erd_diagram.png
│   ├── 02_one_to_many_relation.png
│   ├── 03_sql_join_principles.png
│   └── 04_query_pipeline_flow.png
├── captures/                          # [Step 5] 15개 쿼리 실행 결과 캡처 마크다운
│   └── query_execution_results.md
├── PLAN.md                            # [Step 1] 요구사항 분해 및 설계 계획서
├── 스터디.md                           # [Step 4] 과제 전문 수록, 요구사항 1:1 대조, 주니어 일상 비유
├── REPORT.md                          # [Step 5] 아키텍처 결정, 엣지케이스 방어, 벤치마크 리포트
├── NOTEBOOKLM_GUIDE.md                # [Step 6] 팟캐스트 기획서 (업로드 소스 체크리스트 박스 최상단 수록)
├── NOTEBOOKLM_FULL_SOURCE.txt         # [Step 6] NotebookLM 업로드용 단일 소스 텍스트
└── README.md                          # 본 종합 가이드 문서
```

---

## 🚀 3. 빠른 시작 및 원클릭 실행 가이드

### 3.1 단위 테스트 실행 (초고속 0.03초 무결성 검증)
```bash
python tests/test_database.py
```

### 3.2 고해상도 다이어그램 생성
```bash
python scripts/generate_diagrams_matplotlib.py
```

### 3.3 평가자용 15개 쿼리 시각적 러너 실행
```bash
python scripts/verify_requirements.py
```

---

## 📊 4. 핵심 엔티티 관계도 (ERD)

![스마트 카페 ERD](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b6-01/diagrams/01_erd_diagram.png)

---

## 🔍 5. [평가자 시각적 검증 공간] 15개 쿼리 실행 입출력 예시

평가자분이 직접 `python scripts/verify_requirements.py`를 실행했을 때 터미널에 표시되는 실제 출력 결과 샘플입니다:

```text
================================================================================
[RUN] [스마트 카페 주문 DB] 평가자용 15개 핵심 비즈니스 SQL 쿼리 검증 러너
================================================================================

▶ [Q01] 판매 중인 메뉴 상위 5개 (가격 내림차순)
   - 범주: 기본 조회 1 (WHERE, ORDER BY, LIMIT)
   - 목적: 현재 판매 활성화된 프리미엄 메뉴 TOP 5를 확인하여 매장 주력 상품 파악
   - SQL : SELECT menu_id, menu_name, price FROM menus WHERE is_available = 1 ORDER BY price DESC LIMIT 5;
menu_id | menu_name       | price
--------+-----------------+------
13      | 시그니처 텀블러 500ml  | 18000
14      | 에티오피아 예가체프 200g | 16000
12      | 치킨 클럽 샌드위치      | 7500 
11      | 바스크 치즈케이크       | 6800 
9       | 딸기 요거트 스무디      | 6500 

▶ [Q05] 주문 내역과 고객 인적사항 매칭 조회
   - 범주: 조인 1 (INNER JOIN)
   - 목적: 영수증에 적힌 고객 번호를 회원 테이블과 연결하여 주문자 실명 및 등급 확인
   - SQL : SELECT o.order_id, m.name AS member_name, m.grade, m.phone, o.total_amount, o.order_status FROM orders o INNER JOIN members m ON o.member_id = m.member_id ORDER BY o.order_id ASC;
order_id | member_name | grade  | phone         | total_amount | order_status
---------+-------------+--------+---------------+--------------+-------------
1        | 김민준         | VVIP   | 010-1234-5678 | 13800        | COMPLETED   
2        | 이지은         | VIP    | 010-2345-6789 | 12300        | COMPLETED   
3        | 박서준         | NORMAL | 010-3456-7890 | 4500         | COMPLETED   
...

▶ [Q07] 한 번도 주문하지 않은 미구매 신규 회원 발굴
   - 범주: 조인 3 (LEFT JOIN + IS NULL)
   - 목적: 회원가입 후 아직 첫 결제를 하지 않은 고객을 선별하여 웰컴 쿠폰 발송
   - SQL : SELECT m.member_id, m.name, m.email, m.created_at FROM members m LEFT JOIN orders o ON m.member_id = o.member_id WHERE o.order_id IS NULL;
member_id | name | email                 | created_at         
----------+------+-----------------------+--------------------
9         | 장우진  | woojin.jang@example.com | 2026-03-01 10:00:00
10        | 한예원  | yewon.han@example.com   | 2026-03-02 18:40:00

▶ [Q10] 고객별 총 주문 횟수 및 누적 구매 금액 랭킹
   - 범주: 집계 2 (COUNT, SUM + GROUP BY)
   - 목적: 고객 생애 가치(LTV)를 산출하여 충성 고객 순위 산정
   - SQL : SELECT m.member_id, m.name AS member_name, m.grade, COUNT(o.order_id) AS order_count, SUM(o.total_amount) AS total_spent FROM members m INNER JOIN orders o ON m.member_id = o.member_id WHERE o.order_status IN ('COMPLETED', 'PAID') GROUP BY m.member_id, m.name, m.grade ORDER BY total_spent DESC;
member_id | member_name | grade  | order_count | total_spent
----------+-------------+--------+-------------+------------
6         | 강하은         | VVIP   | 2           | 67800      
1         | 김민준         | VVIP   | 3           | 34800      
2         | 이지은         | VIP    | 2           | 30300      
...

▶ [Q15] 주문 조회 최적화 인덱스 생성 및 실행 계획 분석
   - 범주: 인덱스 (CREATE INDEX + EXPLAIN QUERY PLAN)
   - 목적: 자주 조회되는 (member_id, ordered_at) 복합 B-Tree 인덱스로 인덱스 스캔 성능 확보
   - SQL : EXPLAIN QUERY PLAN SELECT order_id, total_amount, ordered_at FROM orders WHERE member_id = 1 ORDER BY ordered_at DESC;
id | parent | notused | detail                                                              
---+--------+---------+---------------------------------------------------------------------
4  | 0      | 0       | SEARCH orders USING INDEX idx_orders_member_ordered_at (member_id=?)

================================================================================
[SUCCESS] 15개 쿼리 실행 검증 완료!
[SAVED] 결과 캡처 파일 생성됨: captures/query_execution_results.md
================================================================================
```

