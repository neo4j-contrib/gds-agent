import re
from pathlib import Path

SKILLS_DIR = Path(__file__).parents[2] / "skills"

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KEY_PATTERN = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)#]+)\)")


def parse_frontmatter(text):
    lines = text.splitlines()
    assert lines[0] == "---", "SKILL.md must start with YAML frontmatter"
    end = lines[1:].index("---") + 1
    fields = {}
    current = None
    for line in lines[1:end]:
        match = KEY_PATTERN.match(line)
        if match:
            current = match.group(1)
            fields[current] = match.group(2).strip()
        elif current and line.startswith(" "):
            fields[current] = f"{fields[current]} {line.strip()}".strip()
    return fields, "\n".join(lines[end + 1 :])


def skill_dirs():
    return sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())


def test_skills_directory_has_skills():
    assert skill_dirs(), f"no skills found in {SKILLS_DIR}"


def test_skill_frontmatter_is_valid():
    for skill in skill_dirs():
        skill_md = skill / "SKILL.md"
        assert skill_md.is_file(), f"{skill.name} is missing SKILL.md"
        fields, _ = parse_frontmatter(skill_md.read_text())

        name = fields.get("name", "")
        assert name == skill.name, f"{skill.name}: frontmatter name '{name}' != dir"
        assert NAME_PATTERN.match(name), f"{skill.name}: invalid name format"
        assert len(name) <= 64, f"{skill.name}: name exceeds 64 chars"
        for reserved in ("anthropic", "claude"):
            assert reserved not in name, f"{skill.name}: reserved word in name"

        description = fields.get("description", "")
        assert description, f"{skill.name}: description is required"
        assert len(description) <= 1024, f"{skill.name}: description exceeds 1024 chars"
        assert "<" not in description and ">" not in description, (
            f"{skill.name}: description must not contain angle brackets"
        )


def test_skill_body_within_limits():
    for skill in skill_dirs():
        _, body = parse_frontmatter((skill / "SKILL.md").read_text())
        assert len(body.splitlines()) < 500, f"{skill.name}: body exceeds 500 lines"


def test_skill_relative_links_resolve():
    for skill in skill_dirs():
        for markdown in skill.rglob("*.md"):
            for link in LINK_PATTERN.findall(markdown.read_text()):
                if "://" in link or link.startswith("mailto:"):
                    continue
                target = (markdown.parent / link).resolve()
                assert target.exists(), (
                    f"{markdown.relative_to(SKILLS_DIR)}: broken link {link}"
                )
