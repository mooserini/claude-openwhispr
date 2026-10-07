"""Tests for claude-openwhispr. Stdlib + pytest only, no live network."""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "openwhispr" / "SKILL.md"


def test_manifest_is_valid_and_code_free():
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "openwhispr"
    for key in ("hooks", "mcpServers", "commands", "agents"):
        assert key not in manifest, f"skill-carrier must not declare {key}"
    assert not list(ROOT.glob("**/*.py")) or all(
        p.parent.name == "tests" for p in ROOT.glob("**/*.py")
    ), "no executable code outside tests"


def test_marketplace_points_at_this_plugin():
    mk = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert [p["name"] for p in mk["plugins"]] == ["openwhispr"]
    assert (ROOT / mk["plugins"][0]["source"] / ".claude-plugin" / "plugin.json").is_file()


def test_skill_frontmatter_hardline():
    text = SKILL.read_text()
    assert text.startswith("---")
    assert re.search(r"^name: openwhispr$", text, re.MULTILINE)
    m = re.search(r"^description: (.*)$", text, re.MULTILINE)
    assert m, "description frontmatter missing"
    desc = m.group(1).strip()
    assert len(desc) <= 60, f"description {len(desc)} chars"
    assert desc.endswith(".")


def test_skill_has_no_other_platform_residue():
    text = SKILL.read_text().lower()
    assert "hermes" not in text
    assert "terminal(command" not in text


def test_hooks_and_updaters_absent():
    assert not (ROOT / "hooks").exists()
    assert not (ROOT / ".mcp.json").exists()


def test_readme_discloses_credential_read():
    readme = (ROOT / "README.md").read_text().lower()
    assert "cli-config.json" in readme
    assert "cli-bridge.json" in readme
    assert "never opens credential files" in readme
    assert "0600" in readme


def test_readme_images_exist():
    readme = (ROOT / "README.md").read_text()
    for rel in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme):
        assert (ROOT / rel).is_file(), rel


def test_license_present():
    assert "MIT" in (ROOT / "LICENSE").read_text()
