from pathlib import Path

RAIZ = Path(__file__).parent.parent


def test_workflow_dispara_na_branch_do_repo():
    branch = (RAIZ / ".git" / "HEAD").read_text().strip().split("/")[-1]
    assert f"branches: [{branch}]" in (RAIZ / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
