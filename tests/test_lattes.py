import zipfile
from pathlib import Path

from ppgcasp.lattes import CATEGORIAS, carregar_lattes

PASTA = Path(__file__).parent.parent / "dados" / "lattes"


def test_anderson():
    info = carregar_lattes(PASTA)["anderson-saldanha-bueno"]
    assert 0 < info.contagens["trabalhos_tecnicos"] <= 35
    assert info.resumo
    assert "Júlio de Castilhos" in info.campus


def test_le_zip_e_xml():
    assert len(carregar_lattes(PASTA)) >= 12


def test_zip_corrompido_ignorado(tmp_path):
    (tmp_path / "ruim.zip").write_bytes(b"nao e zip")
    (tmp_path / "ruim.xml").write_text("<nao fechado")
    assert carregar_lattes(tmp_path) == {}


def test_zip_sem_xml_ignorado(tmp_path):
    with zipfile.ZipFile(tmp_path / "vazio.zip", "w") as z:
        z.writestr("leia.txt", "oi")
    assert carregar_lattes(tmp_path) == {}


def test_categorias_ordem():
    assert [c for c, _ in CATEGORIAS][0] == "trabalhos_tecnicos"
    assert dict(CATEGORIAS)["orientacoes"] == "orientações de pós-graduação"


def test_campus_so_farroupilha():
    # Geruza consta com instituição de outro estado no Lattes
    info = carregar_lattes(PASTA)["geruza-leal-melo"]
    assert info.campus == ""
