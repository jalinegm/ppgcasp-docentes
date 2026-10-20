import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from .models import LattesInfo
from .planilha import ANO_MAX, ANO_MIN, slugify, titulo_nome

CATEGORIAS = [
    ("trabalhos_tecnicos", "trabalhos técnicos"),
    ("eventos", "eventos organizados"),
    ("cursos", "cursos ministrados"),
    ("material_didatico", "materiais didáticos"),
    ("midia", "programas de rádio/TV e mídia"),
    ("orientacoes", "orientações de pós-graduação"),
]

TAGS = {
    "trabalhos_tecnicos": ["TRABALHO-TECNICO"],
    "eventos": ["ORGANIZACAO-DE-EVENTO"],
    "cursos": ["CURSO-DE-CURTA-DURACAO-MINISTRADO"],
    "material_didatico": ["DESENVOLVIMENTO-DE-MATERIAL-DIDATICO-OU-INSTRUCIONAL"],
    "midia": [
        "PROGRAMA-DE-RADIO-OU-TV",
        "ENTREVISTAS-MESAS-REDONDAS-PROGRAMAS-E-COMENTARIOS-NA-MIDIA",
    ],
    "orientacoes": [
        "ORIENTACOES-CONCLUIDAS-PARA-MESTRADO",
        "ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO",
    ],
}


def _ler_bytes(caminho: Path) -> bytes | None:
    try:
        if caminho.suffix == ".zip":
            with zipfile.ZipFile(caminho) as z:
                xmls = [n for n in z.namelist() if n.endswith(".xml")]
                return z.read(xmls[0]) if xmls else None
        return caminho.read_bytes()
    except (zipfile.BadZipFile, OSError):
        return None


def _no_periodo(elemento: ET.Element) -> bool:
    for filho in elemento:
        ano = filho.attrib.get("ANO") or filho.attrib.get("ANO-DE-CONCLUSAO")
        if ano and ano.isdigit():
            return ANO_MIN <= int(ano) <= ANO_MAX
    return False


def _resumo(raiz: ET.Element) -> str:
    resumo = raiz.find("DADOS-GERAIS/RESUMO-CV")
    texto = resumo.attrib.get("TEXTO-RESUMO-CV-RH", "").strip() if resumo is not None else ""
    if len(texto) <= 220:
        return texto
    corte = texto[:220]
    ponto = corte.rfind(". ")
    return corte[: ponto + 1] if ponto > 60 else corte.rstrip() + "…"


def _campus(raiz: ET.Element) -> str:
    end = raiz.find("DADOS-GERAIS/ENDERECO/ENDERECO-PROFISSIONAL")
    if end is None or "farroupilha" not in end.attrib.get("NOME-INSTITUICAO-EMPRESA", "").lower():
        return ""
    return end.attrib.get("CIDADE", "")


def _info(dados: bytes) -> tuple[str, LattesInfo] | None:
    try:
        raiz = ET.fromstring(dados)
    except ET.ParseError:
        return None
    gerais = raiz.find("DADOS-GERAIS")
    nome = gerais.attrib.get("NOME-COMPLETO") if gerais is not None else None
    if not nome:
        return None
    contagens = {
        chave: sum(1 for tag in tags for e in raiz.iter(tag) if _no_periodo(e))
        for chave, tags in TAGS.items()
    }
    return slugify(titulo_nome(nome)), LattesInfo(_resumo(raiz), _campus(raiz), contagens)


def carregar_lattes(pasta: Path) -> dict[str, LattesInfo]:
    saida: dict[str, LattesInfo] = {}
    for arquivo in sorted(pasta.iterdir()):
        if arquivo.suffix not in (".xml", ".zip"):
            continue
        dados = _ler_bytes(arquivo)
        resultado = _info(dados) if dados else None
        if resultado:
            saida[resultado[0]] = resultado[1]
    return saida
