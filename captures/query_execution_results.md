# [캡처] 핵심 SQL 쿼리 15개 실행 결과 캡처 문서 (captures/query_execution_results.md)

> 본 문서는 `scripts/verify_requirements.py`에 의해 실시간으로 실행된 15개 핵심 쿼리의 입출력 결과 텍스트 캡처본입니다.

## Q01. 판매 중인 메뉴 상위 5개 (가격 내림차순)
- **범주**: `기본 조회 1 (WHERE, ORDER BY, LIMIT)`
- **실행 목적**: 현재 판매 활성화된 프리미엄 메뉴 TOP 5를 확인하여 매장 주력 상품 파악
```sql
SELECT menu_id, menu_name, price FROM menus WHERE is_available = 1 ORDER BY price DESC LIMIT 5;
```
### [실행 결과]
| menu_id | menu_name | price |
| --- | --- | --- |
| 13 | 시그니처 텀블러 500ml | 18000 |
| 14 | 에티오피아 예가체프 200g | 16000 |
| 12 | 치킨 클럽 샌드위치 | 7500 |
| 11 | 바스크 치즈케이크 | 6800 |
| 9 | 딸기 요거트 스무디 | 6500 |

---

## Q02. VIP 및 VVIP 우수 회원 목록 조회
- **범주**: `기본 조회 2 (WHERE, IN)`
- **실행 목적**: 로열티 프로그램 우대 대상자(VIP 이상)를 필터링하여 특별 프로모션 명단 확보
```sql
SELECT member_id, name, email, grade, points FROM members WHERE grade IN ('VIP', 'VVIP') ORDER BY points DESC;
```
### [실행 결과]
| member_id | name | email | grade | points |
| --- | --- | --- | --- | --- |
| 6 | 강하은 | haeun.kang@example.com | VVIP | 15800 |
| 1 | 김민준 | minjun.kim@example.com | VVIP | 12500 |
| 2 | 이지은 | jieun.lee@example.com | VIP | 6800 |
| 4 | 최수아 | sua.choi@example.com | VIP | 5400 |

---

## Q03. 15,000원 이상 고액 결제 완료 주문 조회
- **범주**: `기본 조회 3 (WHERE, AND, 부등호)`
- **실행 목적**: 매출 기여도가 높은 단체/대량 결제 패턴 분석을 위한 15,000원 이상 주문 조회
```sql
SELECT order_id, member_id, order_status, total_amount, payment_method, ordered_at FROM orders WHERE order_status IN ('COMPLETED', 'PAID') AND total_amount >= 15000 ORDER BY ordered_at DESC;
```
### [실행 결과]
| order_id | member_id | order_status | total_amount | payment_method | ordered_at |
| --- | --- | --- | --- | --- | --- |
| 12 | 1 | PAID | 16000 | CARD | 2026-02-19 18:30:00 |
| 9 | 6 | COMPLETED | 22800 | KAKAO_PAY | 2026-02-16 12:20:00 |
| 7 | 2 | COMPLETED | 18000 | CARD | 2026-02-14 14:10:00 |
| 5 | 6 | COMPLETED | 45000 | CARD | 2026-02-12 11:50:00 |

---

## Q04. 카드 결제 건 최신순 3건 페이징 조회
- **범주**: `기본 조회 4 (LIMIT, OFFSET 페이징)`
- **실행 목적**: 카드 매출 전표 대조를 위한 3건 단위 페이징(Paging) 조회
```sql
SELECT order_id, member_id, total_amount, payment_method, ordered_at FROM orders WHERE payment_method = 'CARD' ORDER BY ordered_at DESC LIMIT 3 OFFSET 0;
```
### [실행 결과]
| order_id | member_id | total_amount | payment_method | ordered_at |
| --- | --- | --- | --- | --- |
| 12 | 1 | 16000 | CARD | 2026-02-19 18:30:00 |
| 11 | 8 | 11800 | CARD | 2026-02-18 10:15:00 |
| 10 | 7 | 6500 | CARD | 2026-02-17 16:00:00 |

---

## Q05. 주문 내역과 고객 인적사항 매칭 조회
- **범주**: `조인 1 (INNER JOIN)`
- **실행 목적**: 영수증에 적힌 고객 번호를 회원 테이블과 연결하여 주문자 실명 및 등급 확인
```sql
SELECT o.order_id, m.name AS member_name, m.grade, m.phone, o.total_amount, o.order_status FROM orders o INNER JOIN members m ON o.member_id = m.member_id ORDER BY o.order_id ASC;
```
### [실행 결과]
| order_id | member_name | grade | phone | total_amount | order_status |
| --- | --- | --- | --- | --- | --- |
| 1 | 김민준 | VVIP | 010-1234-5678 | 13800 | COMPLETED |
| 2 | 이지은 | VIP | 010-2345-6789 | 12300 | COMPLETED |
| 3 | 박서준 | NORMAL | 010-3456-7890 | 4500 | COMPLETED |
| 4 | 최수아 | VIP | 010-4567-8901 | 12600 | COMPLETED |
| 5 | 강하은 | VVIP | 010-6789-0123 | 45000 | COMPLETED |
| 6 | 김민준 | VVIP | 010-1234-5678 | 5000 | COMPLETED |
| 7 | 이지은 | VIP | 010-2345-6789 | 18000 | COMPLETED |
| 8 | 정도윤 | NORMAL | 010-5678-9012 | 9500 | COMPLETED |
| 9 | 강하은 | VVIP | 010-6789-0123 | 22800 | COMPLETED |
| 10 | 조시우 | NORMAL | 010-7890-1234 | 6500 | COMPLETED |
| 11 | 윤아린 | NORMAL | 010-8901-2345 | 11800 | CANCELLED |
| 12 | 김민준 | VVIP | 010-1234-5678 | 16000 | PAID |

---

## Q06. 주문 상세 품목 + 메뉴명 + 카테고리명 결합 조회
- **범주**: `조인 2 (INNER JOIN 3개 테이블 다중 조인)`
- **실행 목적**: 주방 바리스타 조리를 위한 주문서 상세(품목, 메뉴명, 카테고리, 주문금액) 확인
```sql
SELECT oi.order_item_id, oi.order_id, c.category_name, m.menu_name, oi.quantity, oi.unit_price, (oi.quantity * oi.unit_price) AS line_total FROM order_items oi INNER JOIN menus m ON oi.menu_id = m.menu_id INNER JOIN categories c ON m.category_id = c.category_id ORDER BY oi.order_id ASC, oi.order_item_id ASC;
```
### [실행 결과]
| order_item_id | order_id | category_name | menu_name | quantity | unit_price | line_total |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | Espresso Coffee | 아이스 아메리카노 | 2 | 4500 | 9000 |
| 2 | 1 | Espresso Coffee | 바닐라빈 라떼 | 1 | 4800 | 4800 |
| 3 | 2 | Fresh Ade | 생자몽 에이드 | 1 | 6200 | 6200 |
| 4 | 2 | Non-Coffee Latte | 제주 말차 라떼 | 1 | 6100 | 6100 |
| 20 | 2 | Bakery | 플레인 크루아상 | 1 | 3800 | 3800 |
| 5 | 3 | Espresso Coffee | 아이스 아메리카노 | 1 | 4500 | 4500 |
| 6 | 4 | Sweet Dessert | 바스크 치즈케이크 | 1 | 6800 | 6800 |
| 7 | 4 | Espresso Coffee | 바닐라빈 라떼 | 1 | 5800 | 5800 |
| 8 | 5 | Espresso Coffee | 아이스 아메리카노 | 10 | 4500 | 45000 |
| 9 | 6 | Espresso Coffee | 카페라떼 | 1 | 5000 | 5000 |
| 10 | 7 | Merchandise Goods | 시그니처 텀블러 500ml | 1 | 18000 | 18000 |
| 11 | 8 | Espresso Coffee | 아이스 아메리카노 | 1 | 4500 | 4500 |
| 12 | 8 | Espresso Coffee | 카페라떼 | 1 | 5000 | 5000 |
| 13 | 9 | Meal Sandwich | 치킨 클럽 샌드위치 | 2 | 7500 | 15000 |
| 14 | 9 | Bakery | 플레인 크루아상 | 1 | 3800 | 3800 |
| 15 | 9 | Tea & Herb | 캐모마일 허브 | 1 | 4000 | 4000 |
| 16 | 10 | Blended Smoothie | 딸기 요거트 스무디 | 1 | 6500 | 6500 |
| 17 | 11 | Non-Coffee Latte | 초코라떼 | 1 | 5500 | 5500 |
| 18 | 11 | Tea & Herb | 얼그레이 클래식 | 1 | 6300 | 6300 |
| 19 | 12 | Specialty Beans | 에티오피아 예가체프 200g | 1 | 16000 | 16000 |

---

## Q07. 한 번도 주문하지 않은 미구매 신규 회원 발굴
- **범주**: `조인 3 (LEFT JOIN + IS NULL)`
- **실행 목적**: 회원가입 후 아직 첫 결제를 하지 않은 고객을 선별하여 웰컴 쿠폰 발송
```sql
SELECT m.member_id, m.name, m.email, m.created_at FROM members m LEFT JOIN orders o ON m.member_id = o.member_id WHERE o.order_id IS NULL;
```
### [실행 결과]
| member_id | name | email | created_at |
| --- | --- | --- | --- |
| 9 | 장우진 | woojin.jang@example.com | 2026-03-01 10:00:00 |
| 10 | 한예원 | yewon.han@example.com | 2026-03-02 18:40:00 |

---

## Q08. 전체 메뉴별 누적 판매 수량 집계 (미판매 메뉴 0건 표시)
- **범주**: `조인 4 (LEFT JOIN + COALESCE)`
- **실행 목적**: 메뉴판의 모든 메뉴 판매량을 전수 조사하여 비인기 단종 후보 및 베스트셀러 파악
```sql
SELECT m.menu_id, m.menu_name, m.price, COALESCE(SUM(oi.quantity), 0) AS total_sold_quantity FROM menus m LEFT JOIN order_items oi ON m.menu_id = oi.menu_id GROUP BY m.menu_id, m.menu_name, m.price ORDER BY total_sold_quantity DESC;
```
### [실행 결과]
| menu_id | menu_name | price | total_sold_quantity |
| --- | --- | --- | --- |
| 1 | 아이스 아메리카노 | 4500 | 14 |
| 2 | 카페라떼 | 5000 | 2 |
| 3 | 바닐라빈 라떼 | 5800 | 2 |
| 10 | 플레인 크루아상 | 3800 | 2 |
| 12 | 치킨 클럽 샌드위치 | 7500 | 2 |
| 4 | 초코라떼 | 5500 | 1 |
| 5 | 제주 말차 라떼 | 6000 | 1 |
| 6 | 얼그레이 클래식 | 5000 | 1 |
| 7 | 캐모마일 허브 | 5000 | 1 |
| 8 | 생자몽 에이드 | 6200 | 1 |
| 9 | 딸기 요거트 스무디 | 6500 | 1 |
| 11 | 바스크 치즈케이크 | 6800 | 1 |
| 13 | 시그니처 텀블러 500ml | 18000 | 1 |
| 14 | 에티오피아 예가체프 200g | 16000 | 1 |
| 15 | 시즌 콜드브루 라떼 | 6000 | 0 |

---

## Q09. 카테고리별 등록 메뉴 수, 평균 가격, 최고 가격 집계
- **범주**: `집계 1 (COUNT, AVG, MAX + GROUP BY)`
- **실행 목적**: 카테고리별 가격대 분포와 구색 현황을 분석하여 메뉴 포트폴리오 관리
```sql
SELECT c.category_id, c.category_name, COUNT(m.menu_id) AS menu_count, ROUND(AVG(m.price), 0) AS avg_price, MAX(m.price) AS max_price FROM categories c INNER JOIN menus m ON c.category_id = m.category_id GROUP BY c.category_id, c.category_name ORDER BY c.category_id ASC;
```
### [실행 결과]
| category_id | category_name | menu_count | avg_price | max_price |
| --- | --- | --- | --- | --- |
| 1 | Espresso Coffee | 4 | 5325.0 | 6000 |
| 2 | Non-Coffee Latte | 2 | 5750.0 | 6000 |
| 3 | Tea & Herb | 2 | 5000.0 | 5000 |
| 4 | Fresh Ade | 1 | 6200.0 | 6200 |
| 5 | Blended Smoothie | 1 | 6500.0 | 6500 |
| 6 | Bakery | 1 | 3800.0 | 3800 |
| 7 | Sweet Dessert | 1 | 6800.0 | 6800 |
| 8 | Meal Sandwich | 1 | 7500.0 | 7500 |
| 9 | Merchandise Goods | 1 | 18000.0 | 18000 |
| 10 | Specialty Beans | 1 | 16000.0 | 16000 |

---

## Q10. 고객별 총 주문 횟수 및 누적 구매 금액 랭킹
- **범주**: `집계 2 (COUNT, SUM + GROUP BY)`
- **실행 목적**: 고객 생애 가치(LTV)를 산출하여 충성 고객 순위 산정
```sql
SELECT m.member_id, m.name AS member_name, m.grade, COUNT(o.order_id) AS order_count, SUM(o.total_amount) AS total_spent FROM members m INNER JOIN orders o ON m.member_id = o.member_id WHERE o.order_status IN ('COMPLETED', 'PAID') GROUP BY m.member_id, m.name, m.grade ORDER BY total_spent DESC;
```
### [실행 결과]
| member_id | member_name | grade | order_count | total_spent |
| --- | --- | --- | --- | --- |
| 6 | 강하은 | VVIP | 2 | 67800 |
| 1 | 김민준 | VVIP | 3 | 34800 |
| 2 | 이지은 | VIP | 2 | 30300 |
| 4 | 최수아 | VIP | 1 | 12600 |
| 5 | 정도윤 | NORMAL | 1 | 9500 |
| 7 | 조시우 | NORMAL | 1 | 6500 |
| 3 | 박서준 | NORMAL | 1 | 4500 |

---

## Q11. 2회 이상 재주문한 단골 고객 및 총 결제액 필터링
- **범주**: `집계 3 (GROUP BY + HAVING)`
- **실행 목적**: 단순 일회성 방문 고객을 제외하고 재방문 단골만 선별
```sql
SELECT m.member_id, m.name AS member_name, COUNT(o.order_id) AS repeat_orders, SUM(o.total_amount) AS total_spent FROM members m INNER JOIN orders o ON m.member_id = o.member_id WHERE o.order_status IN ('COMPLETED', 'PAID') GROUP BY m.member_id, m.name HAVING COUNT(o.order_id) >= 2 ORDER BY repeat_orders DESC, total_spent DESC;
```
### [실행 결과]
| member_id | member_name | repeat_orders | total_spent |
| --- | --- | --- | --- |
| 1 | 김민준 | 3 | 34800 |
| 6 | 강하은 | 2 | 67800 |
| 2 | 이지은 | 2 | 30300 |

---

## Q12. 전체 메뉴 평균 가격보다 비싼 고급 메뉴 목록 조회
- **범주**: `서브쿼리 1 (중첩 Scalar Subquery)`
- **실행 목적**: 메뉴 전체 평균 단가를 자동 계산하여 그보다 높은 프리미엄 메뉴 필터링
```sql
SELECT menu_id, menu_name, price FROM menus WHERE price > (SELECT AVG(price) FROM menus) ORDER BY price DESC;
```
### [실행 결과]
| menu_id | menu_name | price |
| --- | --- | --- |
| 13 | 시그니처 텀블러 500ml | 18000 |
| 14 | 에티오피아 예가체프 200g | 16000 |
| 12 | 치킨 클럽 샌드위치 | 7500 |

---

## Q13. 누적 주문 30,000원 이상 일반 회원을 VIP로 승급 및 포인트 부여
- **범주**: `데이터 수정 (UPDATE + Subquery)`
- **실행 목적**: 실적 기준에 도달한 일반 고객의 등급을 자동으로 상향 조정하고 감사 리워드 지급
```sql
UPDATE members SET grade = 'VIP', points = points + 2000 WHERE member_id IN (SELECT o.member_id FROM orders o WHERE o.order_status IN ('COMPLETED', 'PAID') GROUP BY o.member_id HAVING SUM(o.total_amount) >= 30000) AND grade = 'NORMAL';
```
### [실행 결과]
> **반영 결과**: 0개 행이 성공적으로 변경/삭제되었습니다.

---

## Q14. 주문 취소(CANCELLED)된 주문 레코드 정리
- **범주**: `데이터 삭제 (DELETE + CASCADE)`
- **실행 목적**: 취소된 거래 내역을 안전하게 삭제하여 DB 리소스 최적화
```sql
DELETE FROM orders WHERE order_status = 'CANCELLED';
```
### [실행 결과]
> **반영 결과**: 1개 행이 성공적으로 변경/삭제되었습니다.

---

## Q15. 주문 조회 최적화 인덱스 생성 및 실행 계획 분석
- **범주**: `인덱스 (CREATE INDEX + EXPLAIN QUERY PLAN)`
- **실행 목적**: 자주 조회되는 (member_id, ordered_at) 복합 B-Tree 인덱스로 인덱스 스캔 성능 확보
```sql
EXPLAIN QUERY PLAN SELECT order_id, total_amount, ordered_at FROM orders WHERE member_id = 1 ORDER BY ordered_at DESC;
```
### [실행 결과]
| id | parent | notused | detail |
| --- | --- | --- | --- |
| 4 | 0 | 0 | SEARCH orders USING INDEX idx_orders_member_ordered_at (member_id=?) |

---
