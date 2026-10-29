# ==============================================================================
# 스마트 카페 주문 시스템 (Smart Cafe Ordering Database)
# 파일명: scripts/build_notebooklm_source.py
# 설명: NotebookLM 업로드용 순수 소스 코드 단일 텍스트 파일(NOTEBOOKLM_FULL_SOURCE.txt) 생성기
# ==============================================================================

# [1차]: 파일 시스템 탐색을 위한 pathlib 모듈과 시스템 모듈을 임포트합니다.
# [2차]: 여러 폴더에 흩어져 있는 소스 코드 파일들을 한 권의 책으로 묶어줄 제본 도구를 준비합니다.
from pathlib import Path
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def build_source_text():
    root_dir = Path(__file__).resolve().parent.parent
    output_file = root_dir / "NOTEBOOKLM_FULL_SOURCE.txt"

    # NotebookLM에 통합할 순수 핵심 소스 파일 목록
    source_files = [
        root_dir / "sql" / "01_schema.sql",
        root_dir / "sql" / "02_sample_data.sql",
        root_dir / "sql" / "03_queries.sql",
        root_dir / "tests" / "test_database.py",
        root_dir / "scripts" / "verify_requirements.py",
        root_dir / "scripts" / "generate_diagrams_matplotlib.py"
    ]

    lines = []
    lines.append("=" * 80)
    lines.append("스마트 카페 주문 시스템 (Cafe Order DB) - 전체 핵심 소스 코드 통합집")
    lines.append("NotebookLM 딥다이브 오디오 팟캐스트 및 학습 전용 단일 텍스트 소스")
    lines.append("=" * 80)
    lines.append("")

    for filepath in source_files:
        if not filepath.exists():
            print(f"[경고] 파일을 찾을 수 없습니다: {filepath}")
            continue

        rel_path = filepath.relative_to(root_dir)
        lines.append("\n" + "#" * 80)
        lines.append(f"# [SOURCE FILE]: {rel_path.as_posix()}")
        lines.append("#" * 80 + "\n")

        with open(filepath, "r", encoding="utf-8") as f:
            lines.append(f.read())
        lines.append("\n")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[빌드 성공] NOTEBOOKLM_FULL_SOURCE.txt 생성 완료 ({output_file})")


if __name__ == "__main__":
    build_source_text()

