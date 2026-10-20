from ppgcasp.models import Artigo, Docente, Impacto, LattesInfo
from ppgcasp.render import renderizar_site


def docentes_exemplo():
    a = Docente(
        "Ana Teste", "ana-teste", 1,
        [Artigo(2024, "Título <b>& \"aspas\"", "10.1/a", score=5.0, citacoes=3), Artigo(2023, "Sem doi aqui", None)],
        LattesInfo("Resumo da Ana.", "Panambi", {"trabalhos_tecnicos": 4, "eventos": 0, "cursos": 1,
                                                "material_didatico": 0, "midia": 0, "orientacoes": 0}),
        Impacto(3, 5.0, 1, 0, True),
    )
    b = Docente("Bruno Sem Lattes", "bruno-sem-lattes", 2, [Artigo(2022, "Outro", "10.2/b")], None, None)
    c = Docente("Carla Vazia", "carla-vazia", 2, [], None, None)
    return [a, b, c]


def render(tmp_path, grupo, fotos=None):
    renderizar_site(docentes_exemplo(), grupo, tmp_path, fotos=fotos)
    return tmp_path


def test_index_textos_e_links(tmp_path):
    render(tmp_path, Impacto(0, 0.0, 0, 0, False))
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "Ciências Ambientais e Sistemas Produtivos" in html
    assert "Mestrado Profissional · Instituto Federal Farroupilha" in html
    assert "Biodiversidade, Saúde Ambiental e Conservação" in html
    assert "Inovação, Biotecnologia e Sustentabilidade Produtiva" in html
    assert 'href="docentes/ana-teste.html"' in html
    assert 'href="/' not in html and 'src="/' not in html


def test_impacto_social_condicional(tmp_path):
    render(tmp_path, Impacto(0, 0.0, 0, 0, False))
    assert "Impacto social" not in (tmp_path / "index.html").read_text(encoding="utf-8")
    render(tmp_path, Impacto(3, 5.0, 1, 0, True))
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "Impacto social" in html and "Título &lt;b&gt;" in html


def test_docente_artigo_sem_doi_e_escape(tmp_path):
    render(tmp_path, Impacto(0, 0.0, 0, 0, False))
    html = (tmp_path / "docentes" / "ana-teste.html").read_text(encoding="utf-8")
    assert "sem DOI" in html and "Sem doi aqui" in html
    assert "<b>&" not in html and "&lt;b&gt;&amp;" in html
    assert 'data-doi="10.1/a"' in html
    assert "altmetric-embed" in html and "__dimensions_badge_embed__" in html
    assert "embed.js" in html and "badge.js" in html
    assert 'href="../index.html"' in html


def test_docente_sem_lattes_sem_bloco(tmp_path):
    render(tmp_path, Impacto(0, 0.0, 0, 0, False))
    html = (tmp_path / "docentes" / "bruno-sem-lattes.html").read_text(encoding="utf-8")
    assert "Além dos artigos" not in html


def test_contagem_zero_sem_cartao(tmp_path):
    render(tmp_path, Impacto(0, 0.0, 0, 0, False))
    html = (tmp_path / "docentes" / "ana-teste.html").read_text(encoding="utf-8")
    assert "trabalhos técnicos" in html and "cursos ministrados" in html
    assert "eventos organizados" not in html


def test_docente_sem_artigos_renderiza(tmp_path):
    render(tmp_path, Impacto(0, 0.0, 0, 0, False))
    html = (tmp_path / "docentes" / "carla-vazia.html").read_text(encoding="utf-8")
    assert "Carla Vazia" in html and "<b>0</b>" not in html and ">0<" not in html


def test_foto_ou_iniciais(tmp_path):
    fotos = tmp_path / "fotos_in"
    fotos.mkdir()
    (fotos / "ana-teste.jpg").write_bytes(b"x")
    saida = tmp_path / "out"
    renderizar_site(docentes_exemplo(), Impacto(0, 0.0, 0, 0, False), saida, fotos=fotos)
    ana = (saida / "docentes" / "ana-teste.html").read_text(encoding="utf-8")
    bruno = (saida / "docentes" / "bruno-sem-lattes.html").read_text(encoding="utf-8")
    assert "<img" in ana and "../fotos/ana-teste.jpg" in ana
    assert "<img" not in bruno and ">BL<" in bruno
    assert (saida / "fotos" / "ana-teste.jpg").exists()


def test_static_copiado(tmp_path):
    render(tmp_path, Impacto(0, 0.0, 0, 0, False))
    assert (tmp_path / "static" / "style.css").exists() and (tmp_path / "static" / "app.js").exists()
