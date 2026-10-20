from build import main


def test_build_cache_apenas(tmp_path):
    saida = tmp_path / "site"
    assert main(["--saida", str(saida), "--cache", str(tmp_path / "c.json")]) == 0
    assert (saida / "index.html").exists()
    assert len(list((saida / "docentes").glob("*.html"))) == 17


def test_build_cache_apenas_nao_faz_requisicao(tmp_path, monkeypatch):
    import requests

    def proibido(*a, **k):
        raise AssertionError("rede usada")

    monkeypatch.setattr(requests, "get", proibido)
    assert main(["--saida", str(tmp_path / "s"), "--cache", str(tmp_path / "c.json")]) == 0


def test_lattes_aplicado(tmp_path):
    saida = tmp_path / "site"
    main(["--saida", str(saida), "--cache", str(tmp_path / "c.json")])
    html = (saida / "docentes" / "anderson-saldanha-bueno.html").read_text(encoding="utf-8")
    assert "Além dos artigos" in html and "Júlio de Castilhos" in html
