from pathlib import Path


def test_canonical_entry_does_not_rebuild_runtime_packet_in_place() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    text = (repo_root / "packages" / "runtime-core" / "src" / "vgo_runtime" / "canonical_entry.py").read_text(
        encoding="utf-8"
    )
    assert "runtime_packet_path.write_text(" not in text
    assert "build_runtime_truth_packet(" not in text
