# ==============================================================================
# 스마트 카페 주문 시스템 (Smart Cafe Ordering Database)
# 파일명: scripts/generate_diagrams_matplotlib.py
# 설명: Matplotlib을 활용한 고해상도 아키텍처 다이어그램 4종 자동 생성기
# ==============================================================================

# [1차]: 고해상도 그래픽 차트 및 도면 생성을 위한 matplotlib 라이브러리를 임포트합니다.
# [2차]: 컴퓨터 화면 위에 예쁜 아키텍처 다이어그램을 그려줄 전용 제도판과 색연필 세트를 꺼냅니다.
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
import sys

# [1차]: 윈도우 한글 폰트(맑은 고딕) 및 마이너스 부호 깨짐 방지 설정을 적용합니다.
# [2차]: 한국어 글자가 네모 모양(□□)으로 깨져서 못생기게 나오지 않도록 맑은 고딕 명찰 폰트를 지정합니다.
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


def create_erd_diagram(output_path: Path):
    # [1차]: 전체 5개 테이블과 PK/FK 연결 관계를 표현하는 ERD 다이어그램을 생성합니다.
    # [2차]: 카페 데이터베이스의 5개 서랍장 구조와 끈으로 이어진 연결 고리를 한눈에 볼 수 있는 청사진을 그립니다.
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_facecolor("#F8F9FA")
    fig.patch.set_facecolor("#FFFFFF")

    # 테이블 박스 정보: (이름, x, y, 너비, 높이, 배경색, 테두리색, 컬럼목록)
    tables = [
        ("categories (대분류)", 0.5, 5.0, 3.2, 2.4, "#E3F2FD", "#1976D2", [
            "PK: category_id (INT)",
            "UK: category_name (TEXT)",
            "description (TEXT)"
        ]),
        ("menus (판매 메뉴)", 4.8, 5.0, 3.5, 2.7, "#E8F5E9", "#388E3C", [
            "PK: menu_id (INT)",
            "FK: category_id (INT)",
            "menu_name (TEXT)",
            "price (INT)",
            "is_available (INT)"
        ]),
        ("members (고객 회원)", 0.5, 1.0, 3.2, 2.7, "#FFF3E0", "#F57C00", [
            "PK: member_id (INT)",
            "UK: email (TEXT)",
            "name (TEXT)",
            "grade (TEXT)",
            "points (INT)"
        ]),
        ("orders (주문 영수증)", 4.8, 1.0, 3.5, 2.7, "#F3E5F5", "#7B1FA2", [
            "PK: order_id (INT)",
            "FK: member_id (INT)",
            "order_status (TEXT)",
            "total_amount (INT)",
            "payment_method (TEXT)"
        ]),
        ("order_items (주문 품목)", 9.3, 3.0, 3.8, 2.9, "#FFEBEE", "#D32F2F", [
            "PK: order_item_id (INT)",
            "FK: order_id (INT)",
            "FK: menu_id (INT)",
            "quantity (INT)",
            "unit_price (INT)"
        ])
    ]

    for name, x, y, w, h, bg_color, border_color, cols in tables:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                      facecolor=bg_color, edgecolor=border_color, linewidth=2)
        ax.add_patch(rect)
        # 테이블 헤더
        ax.text(x + w / 2, y + h - 0.35, name, ha="center", va="center", fontsize=11, fontweight="bold", color=border_color)
        ax.plot([x + 0.1, x + w - 0.1], [y + h - 0.6, y + h - 0.6], color=border_color, lw=1)
        # 컬럼 텍스트
        col_y = y + h - 0.95
        for col in cols:
            col_color = "#D32F2F" if "PK" in col else ("#1976D2" if "FK" in col else "#333333")
            font_weight = "bold" if ("PK" in col or "FK" in col or "UK" in col) else "normal"
            ax.text(x + 0.25, col_y, col, ha="left", va="center", fontsize=9, color=col_color, fontweight=font_weight)
            col_y -= 0.35

    # 1:N 관계 화살표 그리기
    # 1. categories -> menus (1:N)
    ax.annotate("", xy=(4.8, 6.2), xytext=(3.7, 6.2),
                arrowprops=dict(arrowstyle="->", color="#1976D2", lw=2, mutation_scale=15))
    ax.text(4.25, 6.35, "1 : N", ha="center", fontsize=9, fontweight="bold", color="#1976D2")

    # 2. members -> orders (1:N)
    ax.annotate("", xy=(4.8, 2.3), xytext=(3.7, 2.3),
                arrowprops=dict(arrowstyle="->", color="#F57C00", lw=2, mutation_scale=15))
    ax.text(4.25, 2.45, "1 : N", ha="center", fontsize=9, fontweight="bold", color="#F57C00")

    # 3. orders -> order_items (1:N)
    ax.annotate("", xy=(9.3, 4.0), xytext=(8.3, 2.8),
                arrowprops=dict(arrowstyle="->", color="#7B1FA2", lw=2, mutation_scale=15))
    ax.text(8.7, 3.2, "1 : N", ha="center", fontsize=9, fontweight="bold", color="#7B1FA2")

    # 4. menus -> order_items (1:N)
    ax.annotate("", xy=(9.3, 4.8), xytext=(8.3, 5.8),
                arrowprops=dict(arrowstyle="->", color="#388E3C", lw=2, mutation_scale=15))
    ax.text(8.7, 5.5, "1 : N", ha="center", fontsize=9, fontweight="bold", color="#388E3C")

    ax.set_xlim(0, 13.5)
    ax.set_ylim(0.5, 8.2)
    ax.axis("off")
    ax.set_title("스마트 카페 주문 데이터베이스 종합 엔티티 관계도 (ERD)", fontsize=16, fontweight="bold", pad=20)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"[생성 완료] {output_path}")


def create_relation_diagram(output_path: Path):
    # [1차]: 1:N 관계의 핵심 메커니즘과 부모-자식 테이블 참조 관계를 설명하는 다이어그램을 생성합니다.
    # [2차]: "왜 부모 번호를 자식이 들고 있어야 하는가?"를 한눈에 보여주는 1:N 관계 설명 그림입니다.
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("#FFFFFF")

    # 부모 테이블 (members)
    rect1 = patches.FancyBboxPatch((0.8, 1.5), 4.2, 3.5, boxstyle="round,pad=0.1",
                                  facecolor="#E8EAF6", edgecolor="#3F51B5", linewidth=2)
    ax.add_patch(rect1)
    ax.text(2.9, 4.6, "[부모 1] members (회원 테이블)", ha="center", fontsize=11, fontweight="bold", color="#3F51B5")
    parent_data = [
        "member_id (PK) | 이름   | 등급",
        "------------------------------",
        "  1 (김민준)    | 김민준 | VVIP",
        "  2 (이지은)    | 이지은 | VIP ",
        "  3 (박서준)    | 박서준 | NORMAL"
    ]
    y_pos = 4.0
    for line in parent_data:
        ax.text(1.1, y_pos, line, fontsize=9.5)
        y_pos -= 0.5

    # 자식 테이블 (orders)
    rect2 = patches.FancyBboxPatch((6.8, 1.0), 4.5, 4.2, boxstyle="round,pad=0.1",
                                  facecolor="#FBE9E7", edgecolor="#D84315", linewidth=2)
    ax.add_patch(rect2)
    ax.text(9.05, 4.8, "[자식 N] orders (주문 테이블)", ha="center", fontsize=11, fontweight="bold", color="#D84315")
    child_data = [
        "order_id (PK) | member_id (FK) | 금액",
        "--------------------------------------",
        "  101         | 1 (김민준 참조) | 13,800",
        "  102         | 2 (이지은 참조) | 12,300",
        "  103         | 1 (김민준 참조) |  5,000",
        "  104         | 1 (김민준 참조) | 16,000",
        "  105         | 3 (박서준 참조) |  4,500"
    ]
    y_pos = 4.3
    for line in child_data:
        ax.text(7.0, y_pos, line, fontsize=9)
        y_pos -= 0.45

    # 참조 화살표 연결
    ax.annotate("", xy=(7.0, 3.85), xytext=(5.0, 3.0),
                arrowprops=dict(arrowstyle="->", color="#D84315", lw=2, mutation_scale=15))
    ax.text(6.0, 3.6, "김민준 1:N 복수 주문", ha="center", fontsize=9, fontweight="bold", color="#D84315")

    # 핵심 해설 텍스트 박스
    rect_box = patches.FancyBboxPatch((1.5, 0.2), 9.0, 0.6, boxstyle="square,pad=0.05",
                                     facecolor="#ECEFF1", edgecolor="#90A4AE", linewidth=1)
    ax.add_patch(rect_box)
    ax.text(6.0, 0.5, "핵심 규칙: 1:N 관계에서 외래키(FK)는 무조건 'N(다)' 쪽 테이블에 위치해야 중복 없이 연결됩니다!",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#37474F")

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.5)
    ax.axis("off")
    ax.set_title("1:N (일대다) 관계 및 외래키(FK) 참조 원리", fontsize=15, fontweight="bold", pad=15)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"[생성 완료] {output_path}")


def create_join_diagram(output_path: Path):
    # [1차]: INNER JOIN과 LEFT JOIN의 결과 집합 차이를 명확히 시각화하는 다이어그램을 생성합니다.
    # [2차]: 교집합만 건지는 INNER JOIN과, 왼쪽 손님을 다 살리는 LEFT JOIN의 차이를 그림으로 보여줍니다.
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")

    # [좌측] INNER JOIN (교집합)
    ax1.set_facecolor("#F9FBE7")
    circle1 = patches.Circle((2.5, 3.0), 1.8, facecolor="#81C784", alpha=0.5, edgecolor="#2E7D32", lw=2)
    circle2 = patches.Circle((4.5, 3.0), 1.8, facecolor="#64B5F6", alpha=0.5, edgecolor="#1565C0", lw=2)
    ax1.add_patch(circle1)
    ax1.add_patch(circle2)
    ax1.text(1.8, 3.0, "회원 명부\n(members)", ha="center", va="center", fontsize=10, fontweight="bold")
    ax1.text(5.2, 3.0, "주문 내역\n(orders)", ha="center", va="center", fontsize=10, fontweight="bold")
    ax1.text(3.5, 3.0, "★ 양쪽 모두\n존재하는\n구매 회원\n(INNER)", ha="center", va="center", fontsize=10, fontweight="bold", color="#B71C1C")
    ax1.text(3.5, 0.8, "주문 이력이 있는 활성 고객만 조회\n(미구매 신규 회원은 탈락)", ha="center", fontsize=9.5, color="#333333")
    ax1.set_xlim(0, 7)
    ax1.set_ylim(0, 5.5)
    ax1.axis("off")
    ax1.set_title("[1] INNER JOIN (내부 조인 - 교집합)", fontsize=13, fontweight="bold", pad=10)

    # [우측] LEFT JOIN (왼쪽 기준 + 빈자리 NULL)
    ax2.set_facecolor("#FFFDE7")
    circle3 = patches.Circle((2.5, 3.0), 1.8, facecolor="#FFB74D", alpha=0.8, edgecolor="#E65100", lw=2)
    circle4 = patches.Circle((4.5, 3.0), 1.8, facecolor="#E0E0E0", alpha=0.4, edgecolor="#757575", lw=1.5, ls="--")
    ax2.add_patch(circle3)
    ax2.add_patch(circle4)
    ax2.text(1.8, 3.0, "전체 회원\n(누락 없음)", ha="center", va="center", fontsize=10, fontweight="bold", color="#BF360C")
    ax2.text(5.2, 3.0, "주문 내역\n(orders)", ha="center", va="center", fontsize=9.5, color="#757575")
    ax2.text(3.5, 3.0, "구매 이력\n매칭", ha="center", va="center", fontsize=9.5, fontweight="bold")
    ax2.text(3.5, 0.8, "주문 없는 신규 회원도 NULL로 모두 보존!\n(WHERE orders.id IS NULL로 미구매자 발굴)", ha="center", fontsize=9.5, color="#333333")
    ax2.set_xlim(0, 7)
    ax2.set_ylim(0, 5.5)
    ax2.axis("off")
    ax2.set_title("[2] LEFT JOIN (외부 조인 - 왼쪽 전체 보존)", fontsize=13, fontweight="bold", pad=10)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"[생성 완료] {output_path}")


def create_pipeline_diagram(output_path: Path):
    # [1차]: SQL 구문의 물리적 실제 실행 순서(파이프라인)를 보여주는 플로우차트를 생성합니다.
    # [2차]: SQL이 머릿속에서 어떤 순서로 데이터를 요리해 나가는지 요리 레시피 순서도를 그립니다.
    fig, ax = plt.subplots(figsize=(13, 5), dpi=300)
    ax.set_facecolor("#F5F5F5")
    fig.patch.set_facecolor("#FFFFFF")

    steps = [
        ("1. FROM / JOIN", "조회 대상 테이블 준비 & 결합", "#E1F5FE", "#0288D1"),
        ("2. WHERE", "행 단위 개별 조건 필터링", "#E8F5E9", "#2E7D32"),
        ("3. GROUP BY", "공통 컬럼 기준 그룹 묶기", "#FFF8E1", "#F57F17"),
        ("4. HAVING", "집계 결과 그룹 조건 필터링", "#FBE9E7", "#D84315"),
        ("5. SELECT", "최종 출력 컬럼 프로젝션", "#EDE7F6", "#512DA8"),
        ("6. ORDER BY", "지정 기준 오름/내림차순 정렬", "#F3E5F5", "#8E24AA"),
        ("7. LIMIT", "최종 출력 행 개수 제한", "#ECEFF1", "#37474F")
    ]

    x_start = 0.5
    box_w = 1.45
    box_h = 2.2

    for i, (title, desc, bg, border) in enumerate(steps):
        rect = patches.FancyBboxPatch((x_start, 1.2), box_w, box_h, boxstyle="round,pad=0.08",
                                      facecolor=bg, edgecolor=border, linewidth=2)
        ax.add_patch(rect)
        ax.text(x_start + box_w / 2, 2.7, title, ha="center", va="center", fontsize=10, fontweight="bold", color=border)
        ax.text(x_start + box_w / 2, 1.9, desc, ha="center", va="center", fontsize=8.5, color="#333333", wrap=True)

        if i < len(steps) - 1:
            ax.annotate("", xy=(x_start + box_w + 0.3, 2.3), xytext=(x_start + box_w + 0.05, 2.3),
                        arrowprops=dict(arrowstyle="->", color="#455A64", lw=2, mutation_scale=12))

        x_start += box_w + 0.32

    ax.set_xlim(0, 13.0)
    ax.set_ylim(0.5, 4.2)
    ax.axis("off")
    ax.set_title("SQL 엔진의 실제 내부 쿼리 실행 파이프라인 (Execution Flow)", fontsize=15, fontweight="bold", pad=15)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"[생성 완료] {output_path}")


def main():
    root_dir = Path(__file__).resolve().parent.parent
    diagrams_dir = root_dir / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    create_erd_diagram(diagrams_dir / "01_erd_diagram.png")
    create_relation_diagram(diagrams_dir / "02_one_to_many_relation.png")
    create_join_diagram(diagrams_dir / "03_sql_join_principles.png")
    create_pipeline_diagram(diagrams_dir / "04_query_pipeline_flow.png")
    print("모든 다이어그램 이미지가 diagrams/ 폴더에 성공적으로 생성되었습니다.")


if __name__ == "__main__":
    main()
