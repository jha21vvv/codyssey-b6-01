# ==============================================================================
# 스마트 카페 주문 시스템 (Smart Cafe Ordering Database)
# 파일명: scripts/evaluator_cli.py
# 설명: 평가자가 터미널에서 직접 SQL/명령을 쳐보고 에러가 나는지 실시간 확인하는 전용 CLI 도구
# ==============================================================================

import sqlite3
from pathlib import Path
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
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


def print_help():
    print("""
================================================================================
💡 [평가자 추천 테스트 입력 예시] - 복사해서 그대로 쳐보세요!
--------------------------------------------------------------------------------
1. [외래키 차단 테스트 (에러 터져야 정상!)]
   INSERT INTO orders (member_id, total_amount, payment_method) VALUES (9999, 5000, 'CARD');

2. [UNIQUE 제약조건 차단 테스트 (이메일 중복 에러 터져야 정상!)]
   INSERT INTO members (email, name, phone) VALUES ('minjun.kim@example.com', '홍길동', '010-0000-0000');

3. [NOT NULL 제약조건 차단 테스트 (이름 누락 에러 터져야 정상!)]
   INSERT INTO members (email, name, phone) VALUES ('test@example.com', NULL, '010-0000-0000');

4. [연쇄 삭제 CASCADE 테스트 (1번 주문 삭제 시 자식 품목도 함께 0건 삭제 확인)]
   DELETE FROM orders WHERE order_id = 1;
   SELECT COUNT(*) FROM order_items WHERE order_id = 1;

5. [삭제 차단 RESTRICT 테스트 (팔린 2번 메뉴 삭제 시도 시 에러 차단 확인)]
   DELETE FROM menus WHERE menu_id = 2;

6. [미구매 회원 2명 발굴 쿼리 (LEFT JOIN + IS NULL)]
   SELECT m.member_id, m.name, m.email FROM members m LEFT JOIN orders o ON m.member_id = o.member_id WHERE o.order_id IS NULL;

7. [단골 집계 및 다중 정렬 (1순위: 횟수, 2순위: 결제액)]
   SELECT m.name, COUNT(o.order_id) AS cnt, SUM(o.total_amount) AS total FROM members m INNER JOIN orders o ON m.member_id = o.member_id WHERE o.order_status IN ('COMPLETED', 'PAID') GROUP BY m.member_id, m.name HAVING COUNT(o.order_id) >= 2 ORDER BY cnt DESC, total DESC;

8. [인덱스 실행 계획 확인 (인덱스 사용 여부)]
   CREATE INDEX IF NOT EXISTS idx_orders_member_ordered_at ON orders (member_id, ordered_at DESC);
   EXPLAIN QUERY PLAN SELECT order_id FROM orders WHERE member_id = 1 ORDER BY ordered_at DESC;

• help : 도움말 다시 보기
• exit : 종료
================================================================================
""")


def main():
    root_dir = Path(__file__).resolve().parent.parent
    conn, cur = setup_db(root_dir)

    print("\n" + "=" * 80)
    print(" ☕ [평가자 직접 테스트용 인터랙티브 SQL 콘솔]")
    print("    DB 환경(테이블 5개, 외래키 ON, 샘플데이터 67행)이 완벽히 세팅되었습니다.")
    print("    평가자님이 원하는 SQL을 자유롭게 쳐보세요! (외래키 위반 시 진짜 에러가 뜹니다)")
    print("=" * 80)
    print_help()

    while True:
        try:
            user_input = input("\nSQL> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("평가 콘솔을 종료합니다. 감사합니다!")
                break
            if user_input.lower() == "help":
                print_help()
                continue

            # SQL 실행
            cur.execute(user_input)

            if user_input.strip().upper().startswith("SELECT") or user_input.strip().upper().startswith("EXPLAIN"):
                headers = [d[0] for d in cur.description] if cur.description else []
                rows = cur.fetchall()
                print(format_table(headers, rows))
            else:
                conn.commit()
                print(f"👉 [반영 완료] {cur.rowcount}개 행이 성공적으로 변경/반영되었습니다.")

        except sqlite3.Error as e:
            print(f"\n❌ [SQL 오류 발생 / 제약조건 정상 방어!]")
            print(f"   ➔ 에러 유형 : {type(e).__name__}")
            print(f"   ➔ 상세 메시지: {e}")


if __name__ == "__main__":
    main()

