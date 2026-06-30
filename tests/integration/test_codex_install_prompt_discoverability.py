from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_codex_install_prompts_default_to_shared_agents_root() -> None:
    zh_prompt = (REPO_ROOT / "docs/install/prompts/full-version-install.md").read_text(encoding="utf-8")
    en_prompt = (REPO_ROOT / "docs/install/prompts/full-version-install.en.md").read_text(encoding="utf-8")
    zh_rules = (REPO_ROOT / "docs/install/installation-rules.md").read_text(encoding="utf-8")
    en_rules = (REPO_ROOT / "docs/install/installation-rules.en.md").read_text(encoding="utf-8")

    assert 'bash ./install.sh --host codex --profile full' in zh_prompt
    assert 'bash ./check.sh --host codex --profile full' in zh_prompt
    assert "~/.agents" in zh_prompt
    assert "$vibe" in zh_prompt

    assert 'bash ./install.sh --host codex --profile full' in en_prompt
    assert 'bash ./check.sh --host codex --profile full' in en_prompt
    assert "~/.agents" in en_prompt
    assert "$vibe" in en_prompt

    assert "~/.agents" in zh_rules
    assert "$vibe" in zh_rules
    assert "~/.agents" in en_rules
    assert "$vibe" in en_rules


def test_codex_reference_docs_prefer_shared_agents_root() -> None:
    zh_recommended = (REPO_ROOT / "docs/install/recommended-full-path.md").read_text(encoding="utf-8")
    en_recommended = (REPO_ROOT / "docs/install/recommended-full-path.en.md").read_text(encoding="utf-8")
    zh_cold_start = (REPO_ROOT / "docs/cold-start-install-paths.md").read_text(encoding="utf-8")
    en_cold_start = (REPO_ROOT / "docs/cold-start-install-paths.en.md").read_text(encoding="utf-8")
    zh_entry = (REPO_ROOT / "docs/install/one-click-install-release-copy.md").read_text(encoding="utf-8")
    en_entry = (REPO_ROOT / "docs/install/one-click-install-release-copy.en.md").read_text(encoding="utf-8")

    assert 'bash ./scripts/bootstrap/one-shot-setup.sh --host codex --profile full' in zh_recommended
    assert 'bash ./check.sh --host codex --profile full --deep' in zh_recommended
    assert "~/.agents" in zh_recommended
    assert "$vibe" in zh_recommended

    assert 'bash ./scripts/bootstrap/one-shot-setup.sh --host codex --profile full' in en_recommended
    assert 'bash ./check.sh --host codex --profile full --deep' in en_recommended
    assert "~/.agents" in en_recommended
    assert "$vibe" in en_recommended

    assert 'bash ./scripts/bootstrap/one-shot-setup.sh --host codex --profile full' in zh_cold_start
    assert "~/.agents" in zh_cold_start
    assert "$vibe" in zh_cold_start

    assert 'bash ./scripts/bootstrap/one-shot-setup.sh --host codex --profile full' in en_cold_start
    assert "~/.agents" in en_cold_start
    assert "$vibe" in en_cold_start

    assert "~/.agents" in zh_entry
    assert "$vibe" in zh_entry
    assert "~/.agents" in en_entry
    assert "$vibe" in en_entry


def test_framework_only_english_prompt_keeps_codex_and_opencode_as_separate_host_cases() -> None:
    framework_prompt = (REPO_ROOT / "docs/install/prompts/framework-only-install.en.md").read_text(encoding="utf-8")

    assert "4. Execute the matching install and check commands for the selected host." in framework_prompt
    assert "For `codex`, default to the shared root `~/.agents`" in framework_prompt
    assert "For `opencode`, prefer the thinner direct install/check path by default:" in framework_prompt
    assert 'bash ./install.sh --host codex --profile minimal' in framework_prompt
    assert 'bash ./install.sh --host opencode --profile minimal' in framework_prompt


def test_framework_only_english_prompt_keeps_codex_outside_opencode_branch() -> None:
    en_prompt = (REPO_ROOT / "docs/install/prompts/framework-only-install.en.md").read_text(encoding="utf-8")

    assert "4. Execute the matching install and check commands for the selected host." in en_prompt
    assert (
        "For `codex`, default to the shared root `~/.agents` so every host can reuse the same install:"
    ) in en_prompt
    assert "For `opencode`, prefer the thinner direct install/check path by default:" in en_prompt
    assert en_prompt.index("For `codex`, default to the shared root `~/.agents` so every host can reuse the same install:") < en_prompt.index(
        "For `opencode`, prefer the thinner direct install/check path by default:"
    )
