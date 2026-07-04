from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil


PACKAGE_DIRS = (
    "config",
    "protocols",
    "apps/vgo-cli",
    "packages/contracts",
    "packages/runtime-core",
    "scripts/common",
    "scripts/runtime",
    "scripts/router",
    "scripts/verify",
)
PACKAGE_EXCLUDED_FILES = {
    "apps/vgo-cli/src/vgo_cli/install_gates.py",
    "apps/vgo-cli/src/vgo_cli/install_support.py",
    "apps/vgo-cli/src/vgo_cli/installer_bridge.py",
    "apps/vgo-cli/src/vgo_cli/upgrade_service.py",
}
RECEIPT_RELPATH = ".vibeskills/install-receipt.json"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _copy_tree(source_root: Path, install_root: Path, relpath: str) -> None:
    source = source_root / relpath
    if not source.exists():
        return
    if source.is_file():
        _copy_file(source, install_root / relpath)
        return
    for file_path in sorted(path for path in source.rglob("*") if path.is_file()):
        installed_relpath = file_path.relative_to(source_root).as_posix()
        if "__pycache__" in file_path.parts or file_path.suffix == ".pyc":
            continue
        if installed_relpath in PACKAGE_EXCLUDED_FILES:
            continue
        _copy_file(file_path, install_root / installed_relpath)


def _installed_files(install_root: Path) -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    for file_path in sorted(path for path in install_root.rglob("*") if path.is_file()):
        relpath = file_path.relative_to(install_root).as_posix()
        if relpath == RECEIPT_RELPATH:
            continue
        files.append({"path": relpath, "sha256": _sha256_file(file_path)})
    return files


def _receipt_path(skills_dir: Path) -> Path:
    return skills_dir.resolve() / "vibe" / RECEIPT_RELPATH


def install_vibe_skill(
    *,
    repo_root: Path,
    skills_dir: Path,
    installed_at_utc: str,
    source_git_commit: str,
    source_git_dirty: bool,
    installer_version: str = "0.1.0",
    package_version: str = "0.1.0",
) -> dict[str, object]:
    source_root = repo_root.resolve()
    resolved_skills_dir = skills_dir.resolve()
    install_root = resolved_skills_dir / "vibe"
    receipt_path = install_root / RECEIPT_RELPATH
    if install_root.exists() and not receipt_path.is_file():
        raise RuntimeError(f"Install root already exists without a Vibe install receipt: {install_root}")

    if install_root.exists():
        shutil.rmtree(install_root)
    install_root.mkdir(parents=True, exist_ok=True)

    _copy_tree(source_root, install_root, "SKILL.md")
    for relpath in PACKAGE_DIRS:
        _copy_tree(source_root, install_root, relpath)

    files = _installed_files(install_root)
    package_digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode("utf-8")).hexdigest()
    receipt: dict[str, object] = {
        "schema_version": 1,
        "receipt_kind": "vibe-skill-install",
        "skill_id": "vibe",
        "skills_dir": str(resolved_skills_dir),
        "install_root": str(install_root.resolve()),
        "installed_at_utc": installed_at_utc,
        "installer_version": installer_version,
        "package_version": package_version,
        "package_digest_sha256": package_digest,
        "source_path": str(source_root),
        "source_git_commit": source_git_commit,
        "source_git_dirty": bool(source_git_dirty),
        "files": files,
    }
    _write_json(receipt_path, receipt)
    return receipt


def check_vibe_skill(*, skills_dir: Path) -> dict[str, object]:
    receipt_path = _receipt_path(skills_dir)
    if not receipt_path.is_file():
        return {"ok": False, "missing_receipt": str(receipt_path)}

    receipt = _read_json(receipt_path)
    install_root = Path(str(receipt["install_root"]))
    missing_files: list[str] = []
    drifted_files: list[str] = []
    for entry in receipt.get("files") or []:
        if not isinstance(entry, dict):
            continue
        relpath = str(entry["path"])
        expected_sha = str(entry["sha256"])
        file_path = install_root / relpath
        if not file_path.is_file():
            missing_files.append(relpath)
            continue
        if _sha256_file(file_path) != expected_sha:
            drifted_files.append(relpath)

    return {
        "ok": not missing_files and not drifted_files,
        "missing_files": missing_files,
        "drifted_files": drifted_files,
    }


def update_vibe_skill(
    *,
    repo_root: Path,
    skills_dir: Path,
    installed_at_utc: str,
    source_git_commit: str,
    source_git_dirty: bool,
    installer_version: str = "0.1.0",
    package_version: str = "0.1.0",
) -> dict[str, object]:
    check_result = check_vibe_skill(skills_dir=skills_dir)
    if not check_result.get("ok"):
        raise RuntimeError(f"Refusing to update drifted Vibe install: {check_result}")
    return install_vibe_skill(
        repo_root=repo_root,
        skills_dir=skills_dir,
        installed_at_utc=installed_at_utc,
        source_git_commit=source_git_commit,
        source_git_dirty=source_git_dirty,
        installer_version=installer_version,
        package_version=package_version,
    )


def uninstall_vibe_skill(*, skills_dir: Path) -> dict[str, object]:
    receipt_path = _receipt_path(skills_dir)
    if not receipt_path.is_file():
        raise RuntimeError(f"Vibe install receipt is missing: {receipt_path}")

    receipt = _read_json(receipt_path)
    install_root = Path(str(receipt["install_root"]))
    removed_files: list[str] = []
    for entry in receipt.get("files") or []:
        if not isinstance(entry, dict):
            continue
        relpath = str(entry["path"])
        file_path = install_root / relpath
        if file_path.is_file():
            file_path.unlink()
            removed_files.append(relpath)

    receipt_path.unlink()
    for directory in sorted((path for path in install_root.rglob("*") if path.is_dir()), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    try:
        install_root.rmdir()
    except OSError:
        pass

    return {"removed_files": sorted(removed_files)}


__all__ = ["check_vibe_skill", "install_vibe_skill", "uninstall_vibe_skill", "update_vibe_skill"]
