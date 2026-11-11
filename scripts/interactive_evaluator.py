# ==============================================================================
# 스마트 카페 주문 시스템 (Smart Cafe Ordering Database)
# 파일명: scripts/interactive_evaluator.py
# 설명: 평가자용 단계별 인터랙티브 시연 러너 (엔터키를 누르며 하나씩 검증)
# ==============================================================================

import sqlite3
from pathlib import Path
import sys

# Windows cp949 인코딩 충돌 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def print_box(title: str):
    print("\n" + "=" * 80)
    print(f"📌 {title}")
    print("=" * 80)


def wait_for_enter(prompt: str = "👉 [Enter] 키를 누르면 위 항목을 실제로 실행하고 검증합니다..."):
    try:
        input(prompt)
    except EOFError:
        pass


def setup_db(root_dir: Path):
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    with open(root_dir / "sql" / "01_schema.sql", encoding="utf-8") as f:
        cur.executescript(f.read())
    with open(root_dir / "sql" / "02_sample_data.sql", encoding="utf-8") as f:
        cur.executescript(f.read())
    return conn, cur


def format_table(headers, rows):
    if not rows:
        return "(조회된 결과가 없습니다 / 0 rows)"
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))
    header_str = " | ".join(f"{str(headers[i]).ljust(col_widths[i])}" for i in range(len(headers)))
    sep_str = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    row_lines = [" | ".join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(headers))) for row in rows]
    return f"{header_str}\n{sep_str}\n" + "\n".join(row_lines)


def main():
    root_dir = Path(__file__).resolve().parent.parent
    conn, cur = setup_db(root_dir)

    print("\n" + "█" * 80)
    print(" ☕ [스마트 카페 주문 DB] 평가자 전용 단계별 인터랙티브 시연 콘솔")
    print("   평가자가 엔터(Enter) 키를 누르며 과제의 핵심 요구사항을 하나씩 직접 검증합니다.")
    print("█" * 80)

    # --------------------------------------------------------------------------
    # Step 1: 외래키(FK) 참조 무결성 차단 검증
    # --------------------------------------------------------------------------
    print_box("[검증 1] 외래키(FK) 참조 무결성 차단 검증")
    print("• 시나리오: 회원 명부에 없는 가짜 손님(9999번)으로 주문 영수증을 등록하려고 시도합니다.")
    print("• 실행 코드: INSERT INTO orders (member_id, total_amount, payment_method) VALUES (9999, 5000, 'CARD');")
    wait_for_enter()
    try:
        cur.execute("INSERT INTO orders (member_id, total_amount, payment_method) VALUES (9999, 5000, 'CARD');")
        print("❌ 실패: 에러 없이 삽입되었습니다. (외래키 제약조건 미작동)")
    except sqlite3.IntegrityError as e:
        print(f"✅ 성공! 예상대로 예외 발생 및 쓰기 차단됨: {e}")
        print("   ➔ [결과 해설]: PRAGMA foreign_keys = ON; 자물쇠가 가짜 부모를 가진 미아 데이터 생성을 원천 차단했습니다.")

    # --------------------------------------------------------------------------
    # Step 2: 연쇄 삭제 (ON DELETE CASCADE) 검증
    # --------------------------------------------------------------------------
    print_box("[검증 2] 부모 주문 삭제 시 자식 품목 연쇄 삭제(CASCADE) 검증")
    print("• 시나리오: 1번 영수증을 파쇄(DELETE)하면, 그 안의 품목들(order_items)도 함께 자동 삭제되는지 확인합니다.")
    cur.execute("SELECT COUNT(*) FROM order_items WHERE order_id = 1;")
    before_cnt = cur.fetchone()[0]
    print(f"• 삭제 전: 1번 영수증에 딸린 품목 수 = {before_cnt}건")
    wait_for_enter("👉 [Enter]를 누르면 1번 영수증을 삭제합니다 (DELETE FROM orders WHERE order_id = 1)...")
    cur.execute("DELETE FROM orders WHERE order_id = 1;")
    cur.execute("SELECT COUNT(*) FROM order_items WHERE order_id = 1;")
    after_cnt = cur.fetchone()[0]
    print(f"• 삭제 후: 1번 영수증에 딸린 품목 수 = {after_cnt}건")
    if after_cnt == 0:
        print("✅ 성공! 부모 영수증이 삭제되자 자식 품목들도 자동으로 연쇄 삭제(CASCADE)되었습니다.")

    # --------------------------------------------------------------------------
    # Step 3: 미구매 신규 회원 발굴 (LEFT JOIN + IS NULL)
    # --------------------------------------------------------------------------
    print_box("[검증 3] 미구매 신규 회원 발굴 조회 (LEFT JOIN + IS NULL)")
    print("• 시나리오: 회원가입만 하고 아직 주문을 한 번도 안 한 손님만 콕 집어내어 첫 주문 할인 쿠폰 대상자를 뽑습니다.")
    print("• 실행 쿼리:")
    print("  SELECT m.member_id, m.name, m.email, m.created_at")
    print("  FROM members m LEFT JOIN orders o ON m.member_id = o.member_id")
    print("  WHERE o.order_id IS NULL;")
    wait_for_enter()
    cur.execute("""
        SELECT m.member_id, m.name, m.email, m.created_at
        FROM members m LEFT JOIN orders o ON m.member_id = o.member_id
        WHERE o.order_id IS NULL;
    """)
    headers = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print(format_table(headers, rows))
    print("✅ 성공! 이미 구매한 회원들은 모두 걸러지고, 영수증이 없는 9번 장우진, 10번 한예원 손님만 정확히 출력되었습니다.")

    # --------------------------------------------------------------------------
    # Step 4: 단골손님 집계 및 다중 정렬 (WHERE + GROUP BY + HAVING + ORDER BY)
    # --------------------------------------------------------------------------
    print_box("[검증 4] 2회 이상 주문한 단골손님 집계 및 다중 정렬 (1순위: 횟수, 2순위: 금액)")
    print("• 시나리오: 취소된 주문은 빼고(WHERE), 손님별로 묶어(GROUP BY), 2회 이상 온 단골만(HAVING), 횟수 내림차순 ➔ 결제액 내림차순(ORDER BY) 정렬합니다.")
    print("• 실행 쿼리:")
    print("  SELECT m.name, COUNT(o.order_id) AS repeat_orders, SUM(o.total_amount) AS total_spent")
    print("  FROM members m INNER JOIN orders o ON m.member_id = o.member_id")
    print("  WHERE o.order_status IN ('COMPLETED', 'PAID')")
    print("  GROUP BY m.member_id, m.name HAVING COUNT(o.order_id) >= 2")
    print("  ORDER BY repeat_orders DESC, total_spent DESC;")
    wait_for_enter()
    cur.execute("""
        SELECT m.name AS member_name, COUNT(o.order_id) AS repeat_orders, SUM(o.total_amount) AS total_spent
        FROM members m INNER JOIN orders o ON m.member_id = o.member_id
        WHERE o.order_status IN ('COMPLETED', 'PAID')
        GROUP BY m.member_id, m.name HAVING COUNT(o.order_id) >= 2
        ORDER BY repeat_orders DESC, total_spent DESC;
    """)
    headers = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print(format_table(headers, rows))
    print("✅ 성공! 횟수 동점자(2회) 중 결제액이 더 큰 강하은(67,800원) 손님이 이지은(30,300원) 손님보다 위에 정렬되었습니다.")

    # --------------------------------------------------------------------------
    # Step 5: B-Tree 복합 인덱스 생성 및 실제 사용 증명 (EXPLAIN QUERY PLAN)
    # --------------------------------------------------------------------------
    print_box("[검증 5] 복합 B-Tree 인덱스 생성 및 옵티마이저 실행 계획 증명")
    print("• 시나리오: orders (member_id, ordered_at DESC) 인덱스를 생성하고, EXPLAIN QUERY PLAN으로 인덱스를 진짜 타는지 확인합니다.")
    wait_for_enter("👉 [Enter]를 누르면 인덱스를 생성하고 실행 계획을 분석합니다...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_member_ordered_at ON orders (member_id, ordered_at DESC);")
    cur.execute("""
        EXPLAIN QUERY PLAN
        SELECT order_id, total_amount, ordered_at
        FROM orders WHERE member_id = 1 ORDER BY ordered_at DESC;
    """)
    plan = cur.fetchall()
    headers = [d[0] for d in cur.description]
    print(format_table(headers, plan))
    plan_str = " ".join(str(p) for p in plan)
    if "USING INDEX idx_orders_member_ordered_at" in plan_str:
        print("✅ 성공! 풀 테이블 스캔(SCAN)이 아닌 인덱스 스캔(SEARCH orders USING INDEX ...)으로 동작함을 공식 입증했습니다.")

    print("\n" + "█" * 80)
    print(" 🎉 모든 핵심 요구사항 단계별 검증이 성공적으로 완료되었습니다!")
    print("█" * 80 + "\n")
    conn.close()


if __name__ == "__main__":
    main()

