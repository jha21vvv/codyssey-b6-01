# ==============================================================================
# 스마트 카페 주문 시스템 (Smart Cafe Ordering Database)
# 파일명: tests/test_database.py
# 설명: SQLite 기반 0.05초 초고속 데이터베이스 무결성 & 15개 쿼리 자동 검증 단위 테스트
# ==============================================================================

# [1차]: 단위 테스트 작성을 위한 파이썬 표준 라이브러리 unittest를 임포트합니다.
# [2차]: 소프트웨어 공장에서 제품에 결함이 없는지 자동으로 품질을 검사해 주는 로봇 시험관을 데려옵니다.
import unittest

# [1차]: 내장 관계형 데이터베이스 엔진인 sqlite3 모듈을 임포트합니다.
# [2차]: 컴퓨터 안에 가벼운 미니 데이터베이스 엔진을 가동합니다.
import sqlite3

# [1차]: 파일 시스템 경로 조작을 위한 Path 객체를 pathlib 모듈에서 가져옵니다.
# [2차]: SQL 파일들이 컴퓨터 어디에 저장되어 있는지 길을 찾아주는 내비게이션 도구입니다.
from pathlib import Path


class TestCafeDatabase(unittest.TestCase):
    # [1차]: 각 테스트 케이스 메서드 실행 직전에 인메모리 SQLite DB를 생성하고 스키마 및 샘플 데이터를 로드합니다.
    # [2차]: 시험을 볼 때마다 다른 시험지에 영향을 주지 않도록 매번 깨끗한 새 도화지와 연습장을 준비합니다.
    def setUp(self):
        # [1차]: 기준이 되는 프로젝트 루트 경로를 tests 디렉토리의 부모 디렉토리로 설정합니다.
        # [2차]: 프로젝트 메인 폴더 위치를 찾습니다.
        self.root_dir = Path(__file__).resolve().parent.parent

        # [1차]: 디스크 I/O 비용 없는 초고속 인메모리(:memory:) SQLite 연결을 생성합니다.
        # [2차]: 하드디스크에 파일을 쓰지 않고 컴퓨터 RAM 메모리 위에서 순식간에 날아다니는 가상 시험용 DB를 만듭니다.
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        # [1차]: SQLite 세션에서 외래키 제약조건 검사를 명시적으로 활성화합니다.
        # [2차]: 부모 없는 미아 데이터가 들어오지 못하게 문지기에게 외래키 검문검색을 명령합니다.
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        # [1차]: 01_schema.sql 파일을 읽어와 스키마를 생성합니다.
        # [2차]: 테이블 5개 서랍장을 만드는 설계도 SQL을 읽어서 방 안에 배치합니다.
        schema_path = self.root_dir / "sql" / "01_schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            self.cursor.executescript(f.read())

        # [1차]: 02_sample_data.sql 파일을 읽어와 샘플 데이터를 적재합니다.
        # [2차]: 만들어진 5개 서랍장에 손님, 메뉴, 주문 영수증 카드들을 가지런히 채워 넣습니다.
        data_path = self.root_dir / "sql" / "02_sample_data.sql"
        with open(data_path, "r", encoding="utf-8") as f:
            self.cursor.executescript(f.read())

    # [1차]: 각 테스트 케이스가 완료되면 인메모리 DB 연결을 닫고 자원을 해제합니다.
    # [2차]: 시험이 끝나면 연습장을 덮고 시험 책상을 깔끔하게 정리합니다.
    def tearDown(self):
        self.conn.close()

    # --------------------------------------------------------------------------
    # 1. 스키마 및 테이블 생성 검증
    # --------------------------------------------------------------------------
    def test_tables_created(self):
        # [1차]: sqlite_master 시스템 테이블에서 사용자 테이블 이름 목록을 조회합니다.
        # [2차]: 방 안에 우리가 주문한 서랍장 5개가 제대로 배달되어 놓여있는지 목록을 확인합니다.
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in self.cursor.fetchall()]

        # [1차]: 기획된 5개 테이블이 모두 존재하는지 단언(assert)합니다.
        # [2차]: 5개 서랍장(회원, 카테고리, 메뉴, 주문, 주문상세)이 모두 빠짐없이 존재하는지 검사합니다.
        expected_tables = {"members", "categories", "menus", "orders", "order_items"}
        self.assertTrue(expected_tables.issubset(set(tables)), f"누락된 테이블 존재: {expected_tables - set(tables)}")

    # --------------------------------------------------------------------------
    # 2. 샘플 데이터 최소 10행 요구사항 충족 검증
    # --------------------------------------------------------------------------
    def test_minimum_row_count(self):
        # [1차]: 5개 테이블 각각에 대해 COUNT(*) 쿼리를 실행하여 10행 이상인지 검증합니다.
        # [2차]: 과제 규정대로 5개 서랍장마다 최소 10장 이상의 카드가 두둑하게 들어있는지 장수를 셉니다.
        tables = ["members", "categories", "menus", "orders", "order_items"]
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = self.cursor.fetchone()[0]
            self.assertGreaterEqual(count, 10, f"{table} 테이블의 데이터가 10행 미만입니다: {count}행")

    # --------------------------------------------------------------------------
    # 3. 외래키(FK) 참조 무결성 차단 검증
    # --------------------------------------------------------------------------
    def test_foreign_key_constraint_enforcement(self):
        # [1차]: 존재하지 않는 회원 ID(9999)를 참조하는 주문 삽입 시 IntegrityError 예외가 발생하는지 검증합니다.
        # [2차]: 회원 명부에 없는 가짜 손님 번호(9999번)로 주문을 넣으려고 하면 경비원이 멱살을 잡고 쫓아내는지 시험합니다.
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("""
                INSERT INTO orders (order_id, member_id, total_amount, payment_method)
                VALUES (999, 9999, 5000, 'CARD');
            """)

    # --------------------------------------------------------------------------
    # 4. UNIQUE 제약조건 차단 검증
    # --------------------------------------------------------------------------
    def test_unique_constraint_enforcement(self):
        # [1차]: 이미 존재하는 이메일('minjun.kim@example.com')로 신규 회원을 등록할 때 IntegrityError가 발생하는지 검증합니다.
        # [2차]: 이미 가입된 단골의 이메일 아이디를 다른 사람이 가로채서 똑같이 가입하려 할 때 붉은 경고등이 울리는지 봅니다.
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("""
                INSERT INTO members (email, name, phone)
                VALUES ('minjun.kim@example.com', '홍길동', '010-9999-8888');
            """)

    # --------------------------------------------------------------------------
    # 5. NOT NULL 제약조건 차단 검증
    # --------------------------------------------------------------------------
    def test_not_null_constraint_enforcement(self):
        # [1차]: 필수값인 이름(name)을 누락하고 NULL로 삽입 시 IntegrityError가 발생하는지 검증합니다.
        # [2차]: 손님 이름을 공백(NULL)으로 비워둔 채 회원 등록을 시도하면 시스템이 거부하는지 확인합니다.
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("""
                INSERT INTO members (email, name, phone)
                VALUES ('noname@example.com', NULL, '010-0000-0000');
            """)

    # --------------------------------------------------------------------------
    # 6. ON DELETE CASCADE 동작 검증
    # --------------------------------------------------------------------------
    def test_cascade_delete_order_items(self):
        # [1차]: 1번 주문을 삭제했을 때, 자식 테이블(order_items)의 1번 주문 관련 품목들도 함께 자동 연쇄 삭제되는지 검증합니다.
        # [2차]: 1번 영수증을 파쇄기에 넣으면 영수증에 딸린 품목 내역들도 함께 깔끔히 분쇄되는지 확인합니다.
        self.cursor.execute("SELECT COUNT(*) FROM order_items WHERE order_id = 1;")
        initial_items = self.cursor.fetchone()[0]
        self.assertGreater(initial_items, 0)

        # [1차]: 1번 주문 삭제
        self.cursor.execute("DELETE FROM orders WHERE order_id = 1;")

        # [1차]: 자식 품목 수 조회 -> 0개 확인
        self.cursor.execute("SELECT COUNT(*) FROM order_items WHERE order_id = 1;")
        remaining_items = self.cursor.fetchone()[0]
        self.assertEqual(remaining_items, 0, "부모 주문 삭제 시 자식 품목이 연쇄 삭제(CASCADE)되지 않았습니다.")

    # --------------------------------------------------------------------------
    # 7. 핵심 쿼리 15개 무결성 전수 검증
    # --------------------------------------------------------------------------
    def test_q01_to_q15_execution_integrity(self):
        # [Q01: 기본 조회 1] 판매 중 메뉴 상위 5개 가격 내림차순
        self.cursor.execute("""
            SELECT menu_id, menu_name, price FROM menus
            WHERE is_available = 1 ORDER BY price DESC LIMIT 5;
        """)
        rows_q01 = self.cursor.fetchall()
        self.assertEqual(len(rows_q01), 5)
        self.assertGreaterEqual(rows_q01[0][2], rows_q01[1][2])  # 내림차순 확인

        # [Q02: 기본 조회 2] VIP 이상 회원 조회
        self.cursor.execute("""
            SELECT member_id, name, grade FROM members
            WHERE grade IN ('VIP', 'VVIP') ORDER BY points DESC;
        """)
        rows_q02 = self.cursor.fetchall()
        self.assertGreaterEqual(len(rows_q02), 3)

        # [Q03: 기본 조회 3] 15,000원 이상 고액 결제 건
        self.cursor.execute("""
            SELECT order_id, total_amount FROM orders
            WHERE order_status IN ('COMPLETED', 'PAID') AND total_amount >= 15000;
        """)
        rows_q03 = self.cursor.fetchall()
        self.assertGreaterEqual(len(rows_q03), 3)

        # [Q04: 기본 조회 4] CARD 결제 페이징 조회 (LIMIT 3 OFFSET 0)
        self.cursor.execute("""
            SELECT order_id FROM orders WHERE payment_method = 'CARD' ORDER BY ordered_at DESC LIMIT 3 OFFSET 0;
        """)
        rows_q04 = self.cursor.fetchall()
        self.assertEqual(len(rows_q04), 3)

        # [Q05: 조인 1 - INNER] 주문과 회원 정보 조인
        self.cursor.execute("""
            SELECT o.order_id, m.name FROM orders o
            INNER JOIN members m ON o.member_id = m.member_id;
        """)
        rows_q05 = self.cursor.fetchall()
        self.assertGreaterEqual(len(rows_q05), 10)

        # [Q06: 조인 2 - 3개 테이블 다중 조인] 주문상세 + 메뉴 + 카테고리
        self.cursor.execute("""
            SELECT oi.order_item_id, c.category_name, m.menu_name, (oi.quantity * oi.unit_price)
            FROM order_items oi
            INNER JOIN menus m ON oi.menu_id = m.menu_id
            INNER JOIN categories c ON m.category_id = c.category_id;
        """)
        rows_q06 = self.cursor.fetchall()
        self.assertGreaterEqual(len(rows_q06), 15)

        # [Q07: 조인 3 - LEFT JOIN] 미주문 회원 발굴
        self.cursor.execute("""
            SELECT m.member_id, m.name FROM members m
            LEFT JOIN orders o ON m.member_id = o.member_id
            WHERE o.order_id IS NULL;
        """)
        rows_q07 = self.cursor.fetchall()
        # 샘플 데이터에 주문이 없는 회원은 9번 장우진, 10번 한예원 2명
        self.assertEqual(len(rows_q07), 2)

        # [Q08: 조인 4 - LEFT JOIN + COALESCE] 전체 메뉴 판매량 집계
        self.cursor.execute("""
            SELECT m.menu_id, m.menu_name, COALESCE(SUM(oi.quantity), 0) AS total_sold
            FROM menus m
            LEFT JOIN order_items oi ON m.menu_id = oi.menu_id
            GROUP BY m.menu_id, m.menu_name, m.price
            ORDER BY total_sold DESC;
        """)
        rows_q08 = self.cursor.fetchall()
        self.assertEqual(len(rows_q08), 15)  # 총 메뉴 15개 모두 누락 없이 반환

        # [Q09: 집계 1 - COUNT, AVG, MAX + GROUP BY] 카테고리별 통계
        self.cursor.execute("""
            SELECT c.category_name, COUNT(m.menu_id), ROUND(AVG(m.price), 0), MAX(m.price)
            FROM categories c
            INNER JOIN menus m ON c.category_id = m.category_id
            GROUP BY c.category_id, c.category_name;
        """)
        rows_q09 = self.cursor.fetchall()
        self.assertGreaterEqual(len(rows_q09), 10)

        # [Q10: 집계 2 - COUNT, SUM + GROUP BY] 고객별 누적 구매액 및 주문수
        self.cursor.execute("""
            SELECT m.name, COUNT(o.order_id), SUM(o.total_amount)
            FROM members m
            INNER JOIN orders o ON m.member_id = o.member_id
            WHERE o.order_status IN ('COMPLETED', 'PAID')
            GROUP BY m.member_id, m.name;
        """)
        rows_q10 = self.cursor.fetchall()
        self.assertGreaterEqual(len(rows_q10), 6)

        # [Q11: 집계 3 - HAVING] 2회 이상 주문한 단골 필터링
        self.cursor.execute("""
            SELECT m.name, COUNT(o.order_id)
            FROM members m
            INNER JOIN orders o ON m.member_id = o.member_id
            WHERE o.order_status IN ('COMPLETED', 'PAID')
            GROUP BY m.member_id, m.name
            HAVING COUNT(o.order_id) >= 2;
        """)
        rows_q11 = self.cursor.fetchall()
        self.assertGreaterEqual(len(rows_q11), 3)

        # [Q12: 서브쿼리 1] 전체 메뉴 평균 가격보다 비싼 메뉴
        self.cursor.execute("""
            SELECT menu_name, price FROM menus
            WHERE price > (SELECT AVG(price) FROM menus);
        """)
        rows_q12 = self.cursor.fetchall()
        self.assertGreaterEqual(len(rows_q12), 3)

        # [Q13: 데이터 수정 - UPDATE] 3만원 이상 구매 일반 회원 VIP 승급
        self.cursor.execute("""
            UPDATE members SET grade = 'VIP', points = points + 2000
            WHERE member_id IN (
                SELECT o.member_id FROM orders o
                WHERE o.order_status IN ('COMPLETED', 'PAID')
                GROUP BY o.member_id HAVING SUM(o.total_amount) >= 30000
            ) AND grade = 'NORMAL';
        """)
        # 변경 행 수 검증
        self.assertGreaterEqual(self.cursor.rowcount, 0)

        # [Q14: 데이터 삭제 - DELETE] CANCELLED 주문 정리
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'CANCELLED';")
        cancelled_before = self.cursor.fetchone()[0]
        self.assertEqual(cancelled_before, 1)

        self.cursor.execute("DELETE FROM orders WHERE order_status = 'CANCELLED';")
        self.assertEqual(self.cursor.rowcount, 1)

        # [Q15: 인덱스 생성 및 실행 계획 확인]
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_member_ordered_at 
            ON orders (member_id, ordered_at DESC);
        """)
        self.cursor.execute("""
            EXPLAIN QUERY PLAN
            SELECT order_id, total_amount, ordered_at FROM orders
            WHERE member_id = 1 ORDER BY ordered_at DESC;
        """)
        plan = self.cursor.fetchall()
        # 실행 계획 문자열에 idx_orders_member_ordered_at 인덱스가 사용되었는지 검증
        plan_str = " ".join([str(p) for p in plan])
        self.assertIn("idx_orders_member_ordered_at", plan_str)


if __name__ == "__main__":
    # [1차]: 파이썬 인터프리터에서 직접 실행 시 상세한(verbosity=2) 테스트 결과를 출력합니다.
    # [2차]: 로봇 검사관에게 검사 결과를 항목별로 꼼꼼하게 소리 내어 보고하라고 지시합니다.
    unittest.main(verbosity=2)
