from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
README_PATHS = (ROOT / "README.md", ROOT / "README.zh.md")
ASSET_PATHS = (
    ROOT / "docs" / "assets" / "star-history-light.svg",
    ROOT / "docs" / "assets" / "star-history-dark.svg",
)


def test_readmes_use_local_star_history_assets() -> None:
    for readme_path in README_PATHS:
        readme = readme_path.read_text(encoding="utf-8")

        assert "https://api.star-history.com" not in readme
        assert "./docs/assets/star-history-light.svg" in readme
        assert "./docs/assets/star-history-dark.svg" in readme
        assert "https://www.star-history.com/" in readme


def test_star_history_assets_are_valid_svg() -> None:
    for asset_path in ASSET_PATHS:
        root = ET.parse(asset_path).getroot()

        assert root.tag == "{http://www.w3.org/2000/svg}svg"
