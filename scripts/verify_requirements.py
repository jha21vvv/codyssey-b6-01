# ==============================================================================
# 스마트 카페 주문 시스템 (Smart Cafe Ordering Database)
# 파일명: scripts/verify_requirements.py
# 설명: 평가자용 15개 쿼리 시각적 러너 및 결과 캡처 자동 생성 스크립트
#       (터미널 포맷팅 테이블 및 captures/query_execution_results.md 생성)
# ==============================================================================

# [1차]: 파이썬 내장 sqlite3 모듈과 경로 처리를 위한 pathlib 모듈을 임포트합니다.
# [2차]: 가벼운 미니 DB 엔진과 파일 보관함 위치를 찾는 나침반을 준비합니다.
import sqlite3
from pathlib import Path
import json
import sys

# [1차]: Windows 콘솔(cmd/powershell)의 기본 인코딩(cp949) 한계로 인한 유니코드 출력 오류를 방지하기 위해 stdout을 utf-8로 재구성합니다.
# [2차]: 윈도우 터미널 창에서 한글이나 특수 기호가 깨지거나 에러를 뿜지 않도록 전용 번역 통역관을 배치합니다.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def setup_in_memory_db(root_dir: Path) -> sqlite3.Connection:
    # [1차]: 인메모리 SQLite 연결을 생성하고 스키마와 샘플 데이터를 로드합니다.
    # [2차]: 평가자가 기다릴 필요 없이 RAM 메모리에서 즉시 0.01초 만에 테스트용 카페 DB를 가동합니다.
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    schema_file = root_dir / "sql" / "01_schema.sql"
    with open(schema_file, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    data_file = root_dir / "sql" / "02_sample_data.sql"
    with open(data_file, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    return conn


def format_table(headers: list, rows: list) -> str:
    # [1차]: 결과 집합을 깔끔한 아스키 테이블 문자열로 포맷팅합니다.
    # [2차]: 표 형태로 데이터를 예쁘게 줄 맞춰서 콘솔에 보여주는 자동 줄맞춤 자입니다.
    if not rows:
        return "(조회된 결과가 없습니다 / 0 rows)"

    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    header_str = " | ".join(f"{str(headers[i]).ljust(col_widths[i])}" for i in range(len(headers)))
    sep_str = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    
    row_lines = []
    for row in rows:
        row_lines.append(" | ".join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(headers))))

    return f"{header_str}\n{sep_str}\n" + "\n".join(row_lines)


def format_markdown_table(headers: list, rows: list) -> str:
    # [1차]: 마크다운 문서용 테이블 문자열을 생성합니다.
    # [2차]: 마크다운 문서에 바로 붙여넣을 수 있는 표를 만듭니다.
    if not rows:
        return "*결과 없음 (0 rows)*"

    header_str = "| " + " | ".join(headers) + " |"
    sep_str = "| " + " | ".join(["---"] * len(headers)) + " |"
    row_strs = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return f"{header_str}\n{sep_str}\n" + "\n".join(row_strs)


def main():
    root_dir = Path(__file__).resolve().parent.parent
    captures_dir = root_dir / "captures"
    captures_dir.mkdir(parents=True, exist_ok=True)
    capture_file = captures_dir / "query_execution_results.md"

    conn = setup_in_memory_db(root_dir)
    cursor = conn.cursor()

    queries = [
        {
            "id": "Q01",
            "category": "기본 조회 1 (WHERE, ORDER BY, LIMIT)",
            "title": "판매 중인 메뉴 상위 5개 (가격 내림차순)",
            "purpose": "현재 판매 활성화된 프리미엄 메뉴 TOP 5를 확인하여 매장 주력 상품 파악",
            "sql": "SELECT menu_id, menu_name, price FROM menus WHERE is_available = 1 ORDER BY price DESC LIMIT 5;"
        },
        {
            "id": "Q02",
            "category": "기본 조회 2 (WHERE, IN)",
            "title": "VIP 및 VVIP 우수 회원 목록 조회",
            "purpose": "로열티 프로그램 우대 대상자(VIP 이상)를 필터링하여 특별 프로모션 명단 확보",
            "sql": "SELECT member_id, name, email, grade, points FROM members WHERE grade IN ('VIP', 'VVIP') ORDER BY points DESC;"
        },
        {
            "id": "Q03",
            "category": "기본 조회 3 (WHERE, AND, 부등호)",
            "title": "15,000원 이상 고액 결제 완료 주문 조회",
            "purpose": "매출 기여도가 높은 단체/대량 결제 패턴 분석을 위한 15,000원 이상 주문 조회",
            "sql": "SELECT order_id, member_id, order_status, total_amount, payment_method, ordered_at FROM orders WHERE order_status IN ('COMPLETED', 'PAID') AND total_amount >= 15000 ORDER BY ordered_at DESC;"
        },
        {
            "id": "Q04",
            "category": "기본 조회 4 (LIMIT, OFFSET 페이징)",
            "title": "카드 결제 건 최신순 3건 페이징 조회",
            "purpose": "카드 매출 전표 대조를 위한 3건 단위 페이징(Paging) 조회",
            "sql": "SELECT order_id, member_id, total_amount, payment_method, ordered_at FROM orders WHERE payment_method = 'CARD' ORDER BY ordered_at DESC LIMIT 3 OFFSET 0;"
        },
        {
            "id": "Q05",
            "category": "조인 1 (INNER JOIN)",
            "title": "주문 내역과 고객 인적사항 매칭 조회",
            "purpose": "영수증에 적힌 고객 번호를 회원 테이블과 연결하여 주문자 실명 및 등급 확인",
            "sql": "SELECT o.order_id, m.name AS member_name, m.grade, m.phone, o.total_amount, o.order_status FROM orders o INNER JOIN members m ON o.member_id = m.member_id ORDER BY o.order_id ASC;"
        },
        {
            "id": "Q06",
            "category": "조인 2 (INNER JOIN 3개 테이블 다중 조인)",
            "title": "주문 상세 품목 + 메뉴명 + 카테고리명 결합 조회",
            "purpose": "주방 바리스타 조리를 위한 주문서 상세(품목, 메뉴명, 카테고리, 주문금액) 확인",
            "sql": "SELECT oi.order_item_id, oi.order_id, c.category_name, m.menu_name, oi.quantity, oi.unit_price, (oi.quantity * oi.unit_price) AS line_total FROM order_items oi INNER JOIN menus m ON oi.menu_id = m.menu_id INNER JOIN categories c ON m.category_id = c.category_id ORDER BY oi.order_id ASC, oi.order_item_id ASC;"
        },
        {
            "id": "Q07",
            "category": "조인 3 (LEFT JOIN + IS NULL)",
            "title": "한 번도 주문하지 않은 미구매 신규 회원 발굴",
            "purpose": "회원가입 후 아직 첫 결제를 하지 않은 고객을 선별하여 웰컴 쿠폰 발송",
            "sql": "SELECT m.member_id, m.name, m.email, m.created_at FROM members m LEFT JOIN orders o ON m.member_id = o.member_id WHERE o.order_id IS NULL;"
        },
        {
            "id": "Q08",
            "category": "조인 4 (LEFT JOIN + COALESCE)",
            "title": "전체 메뉴별 누적 판매 수량 집계 (미판매 메뉴 0건 표시)",
            "purpose": "메뉴판의 모든 메뉴 판매량을 전수 조사하여 비인기 단종 후보 및 베스트셀러 파악",
            "sql": "SELECT m.menu_id, m.menu_name, m.price, COALESCE(SUM(oi.quantity), 0) AS total_sold_quantity FROM menus m LEFT JOIN order_items oi ON m.menu_id = oi.menu_id GROUP BY m.menu_id, m.menu_name, m.price ORDER BY total_sold_quantity DESC;"
        },
        {
            "id": "Q09",
            "category": "집계 1 (COUNT, AVG, MAX + GROUP BY)",
            "title": "카테고리별 등록 메뉴 수, 평균 가격, 최고 가격 집계",
            "purpose": "카테고리별 가격대 분포와 구색 현황을 분석하여 메뉴 포트폴리오 관리",
            "sql": "SELECT c.category_id, c.category_name, COUNT(m.menu_id) AS menu_count, ROUND(AVG(m.price), 0) AS avg_price, MAX(m.price) AS max_price FROM categories c INNER JOIN menus m ON c.category_id = m.category_id GROUP BY c.category_id, c.category_name ORDER BY c.category_id ASC;"
        },
        {
            "id": "Q10",
            "category": "집계 2 (COUNT, SUM + GROUP BY)",
            "title": "고객별 총 주문 횟수 및 누적 구매 금액 랭킹",
            "purpose": "고객 생애 가치(LTV)를 산출하여 충성 고객 순위 산정",
            "sql": "SELECT m.member_id, m.name AS member_name, m.grade, COUNT(o.order_id) AS order_count, SUM(o.total_amount) AS total_spent FROM members m INNER JOIN orders o ON m.member_id = o.member_id WHERE o.order_status IN ('COMPLETED', 'PAID') GROUP BY m.member_id, m.name, m.grade ORDER BY total_spent DESC;"
        },
        {
            "id": "Q11",
            "category": "집계 3 (GROUP BY + HAVING)",
            "title": "2회 이상 재주문한 단골 고객 및 총 결제액 필터링",
            "purpose": "단순 일회성 방문 고객을 제외하고 재방문 단골만 선별",
            "sql": "SELECT m.member_id, m.name AS member_name, COUNT(o.order_id) AS repeat_orders, SUM(o.total_amount) AS total_spent FROM members m INNER JOIN orders o ON m.member_id = o.member_id WHERE o.order_status IN ('COMPLETED', 'PAID') GROUP BY m.member_id, m.name HAVING COUNT(o.order_id) >= 2 ORDER BY repeat_orders DESC, total_spent DESC;"
        },
        {
            "id": "Q12",
            "category": "서브쿼리 1 (중첩 Scalar Subquery)",
            "title": "전체 메뉴 평균 가격보다 비싼 고급 메뉴 목록 조회",
            "purpose": "메뉴 전체 평균 단가를 자동 계산하여 그보다 높은 프리미엄 메뉴 필터링",
            "sql": "SELECT menu_id, menu_name, price FROM menus WHERE price > (SELECT AVG(price) FROM menus) ORDER BY price DESC;"
        },
        {
            "id": "Q13",
            "category": "데이터 수정 (UPDATE + Subquery)",
            "title": "누적 주문 30,000원 이상 일반 회원을 VIP로 승급 및 포인트 부여",
            "purpose": "실적 기준에 도달한 일반 고객의 등급을 자동으로 상향 조정하고 감사 리워드 지급",
            "sql": "UPDATE members SET grade = 'VIP', points = points + 2000 WHERE member_id IN (SELECT o.member_id FROM orders o WHERE o.order_status IN ('COMPLETED', 'PAID') GROUP BY o.member_id HAVING SUM(o.total_amount) >= 30000) AND grade = 'NORMAL';"
        },
        {
            "id": "Q14",
            "category": "데이터 삭제 (DELETE + CASCADE)",
            "title": "주문 취소(CANCELLED)된 주문 레코드 정리",
            "purpose": "취소된 거래 내역을 안전하게 삭제하여 DB 리소스 최적화",
            "sql": "DELETE FROM orders WHERE order_status = 'CANCELLED';"
        },
        {
            "id": "Q15",
            "category": "인덱스 (CREATE INDEX + EXPLAIN QUERY PLAN)",
            "title": "주문 조회 최적화 인덱스 생성 및 실행 계획 분석",
            "purpose": "자주 조회되는 (member_id, ordered_at) 복합 B-Tree 인덱스로 인덱스 스캔 성능 확보",
            "sql": "EXPLAIN QUERY PLAN SELECT order_id, total_amount, ordered_at FROM orders WHERE member_id = 1 ORDER BY ordered_at DESC;"
        }
    ]

    # Q15 인덱스 선행 생성
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_member_ordered_at ON orders (member_id, ordered_at DESC);")

    print("\n" + "=" * 80)
    print("[RUN] [스마트 카페 주문 DB] 평가자용 15개 핵심 비즈니스 SQL 쿼리 검증 러너")
    print("=" * 80 + "\n")

    md_content = [
        "# [캡처] 핵심 SQL 쿼리 15개 실행 결과 캡처 문서 (captures/query_execution_results.md)",
        "",
        "> 본 문서는 `scripts/verify_requirements.py`에 의해 실시간으로 실행된 15개 핵심 쿼리의 입출력 결과 텍스트 캡처본입니다.",
        ""
    ]

    for q in queries:
        qid = q["id"]
        title = q["title"]
        cat = q["category"]
        purpose = q["purpose"]
        sql_text = q["sql"]

        print(f"▶ [{qid}] {title}")
        print(f"   - 범주: {cat}")
        print(f"   - 목적: {purpose}")
        print(f"   - SQL : {sql_text}")

        # 실행
        if sql_text.startswith("UPDATE") or sql_text.startswith("DELETE"):
            cursor.execute(sql_text)
            affected = cursor.rowcount
            result_str = f"영향을 받은 행 수 (Affected Rows): {affected}건"
            headers = ["결과 메시지"]
            rows = [[result_str]]
            print(f"   - 결과: {result_str}\n")
        else:
            cursor.execute(sql_text)
            headers = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            print(format_table(headers, rows))
            print()

        # 마크다운 캡처 기록
        md_content.append(f"## {qid}. {title}")
        md_content.append(f"- **범주**: `{cat}`")
        md_content.append(f"- **실행 목적**: {purpose}")
        md_content.append("```sql")
        md_content.append(sql_text)
        md_content.append("```")
        md_content.append("### [실행 결과]")
        if sql_text.startswith("UPDATE") or sql_text.startswith("DELETE"):
            md_content.append(f"> **반영 결과**: {affected}개 행이 성공적으로 변경/삭제되었습니다.\n")
        else:
            md_content.append(format_markdown_table(headers, rows))
            md_content.append("")
        md_content.append("---\n")

    with open(capture_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))

    print("=" * 80)
    print(f"[SUCCESS] 15개 쿼리 실행 검증 완료!")
    print(f"[SAVED] 결과 캡처 파일 생성됨: {capture_file}")
    print("=" * 80 + "\n")

    conn.close()


if __name__ == "__main__":
    main()
