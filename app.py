"""
site-poema — uma galeria de poemas feita com Streamlit.

Os poemas ficam em arquivos .md dentro da pasta `poemas/`.
Para publicar um poema novo, basta criar um arquivo lá e dar push.
"""

from __future__ import annotations

import html
import random
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import streamlit as st

# --------------------------------------------------------------------------
# Configuração
# --------------------------------------------------------------------------

TITULO_DO_SITE = "site-poema"
AUTOR = "Gabriel Andrade Ackermann"
PASTA_POEMAS = Path(__file__).parent / "poemas"
PASTA_FOTOS = Path(__file__).parent / "fotos"

st.set_page_config(
    page_title=TITULO_DO_SITE,
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------
# Modelo e leitura dos arquivos
# --------------------------------------------------------------------------


@dataclass
class Poema:
    slug: str
    titulo: str
    corpo: str
    data: str = ""
    epigrafe: str = ""
    nota: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def primeiro_verso(self) -> str:
        for linha in self.corpo.splitlines():
            if linha.strip():
                return linha.strip()
        return ""


RE_FOTO = re.compile(r"^\[foto:\s*([^\]|]+?)\s*(?:\|\s*(.*?))?\s*\]$")


def partir_em_blocos(corpo: str) -> list[tuple[str, object]]:
    """Separa o poema em blocos de texto e marcações de foto.

    Uma linha no formato `[foto: arquivo.jpg]` (ou `[foto: arquivo.jpg |
    legenda]`) vira uma imagem naquele ponto exato do poema.
    """
    blocos: list[tuple[str, object]] = []
    acumulado: list[str] = []

    def despejar() -> None:
        texto = "\n".join(acumulado).strip("\n")
        if texto.strip():
            blocos.append(("texto", texto))
        acumulado.clear()

    for linha in corpo.split("\n"):
        achado = RE_FOTO.match(linha.strip())
        if achado:
            despejar()
            blocos.append(("foto", (achado.group(1), achado.group(2) or "")))
        else:
            acumulado.append(linha)
    despejar()
    return blocos


def para_html(texto: str) -> str:
    """Converte o texto do poema em HTML preservando versos, estrofes e recuos.

    O markdown do Streamlit colapsa linhas em branco e espaços; por isso
    escapamos o texto e montamos as quebras à mão.
    """
    linhas = html.escape(texto).split("\n")
    saida = []
    for linha in linhas:
        recuo = len(linha) - len(linha.lstrip(" "))
        saida.append("&nbsp;" * recuo + linha.strip())
    return "<br>".join(saida)


def _slugificar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    return re.sub(r"[-\s]+", "-", texto) or "poema"


def _ler_frontmatter(bruto: str) -> tuple[dict[str, str], str]:
    """Lê um cabeçalho simples entre --- e --- no topo do arquivo."""
    if not bruto.lstrip().startswith("---"):
        return {}, bruto

    bruto = bruto.lstrip()
    partes = bruto.split("---", 2)
    if len(partes) < 3:
        return {}, bruto

    cabecalho, corpo = partes[1], partes[2]
    meta: dict[str, str] = {}
    for linha in cabecalho.splitlines():
        if ":" not in linha:
            continue
        chave, _, valor = linha.partition(":")
        meta[chave.strip().lower()] = valor.strip().strip('"').strip("'")
    return meta, corpo.lstrip("\n")


@st.cache_data(show_spinner=False)
def carregar_poemas() -> list[Poema]:
    poemas: list[Poema] = []
    if not PASTA_POEMAS.exists():
        return poemas

    for arquivo in sorted(PASTA_POEMAS.glob("*.md")):
        bruto = arquivo.read_text(encoding="utf-8")
        meta, corpo = _ler_frontmatter(bruto)

        titulo = meta.get("titulo") or meta.get("title") or arquivo.stem
        tags_bruto = meta.get("tags", "")
        tags = [
            t.strip()
            for t in tags_bruto.strip("[]").split(",")
            if t.strip()
        ]

        poemas.append(
            Poema(
                slug=meta.get("slug") or _slugificar(titulo),
                titulo=titulo,
                corpo=corpo.strip("\n"),
                data=meta.get("data", ""),
                epigrafe=meta.get("epigrafe", ""),
                nota=meta.get("nota", ""),
                tags=tags,
            )
        )

    # mais recentes primeiro; sem data, ordem alfabética no fim
    poemas.sort(key=lambda p: (p.data == "", p.data), reverse=False)
    poemas.sort(key=lambda p: p.data, reverse=True)
    return poemas


# --------------------------------------------------------------------------
# Tipografia
# --------------------------------------------------------------------------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400&display=swap');

:root {
    --tinta: #1d1b18;
    --tinta-fraca: #6f6a62;
    --papel: #faf8f4;
    --fio: #e3ded4;
}

.stApp { background: var(--papel); }

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 44rem;
    padding-top: 4rem;
    padding-bottom: 6rem;
}

.poema-titulo {
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 2.1rem;
    font-weight: 500;
    line-height: 1.2;
    color: var(--tinta);
    margin: 0 0 .35rem 0;
}

.poema-data {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .72rem;
    letter-spacing: .09em;
    text-transform: uppercase;
    color: var(--tinta-fraca);
    margin-bottom: 2.4rem;
}

.poema-epigrafe {
    font-family: 'EB Garamond', Georgia, serif;
    font-style: italic;
    font-size: 1rem;
    color: var(--tinta-fraca);
    border-left: 1px solid var(--fio);
    padding-left: 1rem;
    margin: 0 0 2.2rem 0;
}

.poema-corpo {
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 1.25rem;
    line-height: 1.85;
    color: var(--tinta);
    hyphens: none;
}

.poema-respiro { height: 2.2rem; }

.poema-foto { margin: 2.4rem 0 2.4rem 0; }
div[data-testid="stImage"] {
    display: flex;
    justify-content: center;
    margin: 2.6rem 0;
}
div[data-testid="stImage"] img {
    border-radius: 2px;
    filter: saturate(.92);
    max-height: 60vh;
    width: auto !important;
    max-width: 100%;
    object-fit: contain;
}
.poema-legenda {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .68rem;
    letter-spacing: .06em;
    color: var(--tinta-fraca);
    margin-top: .55rem;
}

.poema-nota {
    font-family: 'EB Garamond', Georgia, serif;
    font-size: .95rem;
    font-style: italic;
    color: var(--tinta-fraca);
    margin-top: 3rem;
    padding-top: 1.2rem;
    border-top: 1px solid var(--fio);
}

.poema-tags {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .7rem;
    letter-spacing: .08em;
    color: var(--tinta-fraca);
    margin-top: 1.6rem;
}

.marca {
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 1.45rem;
    color: var(--tinta);
    margin-bottom: .1rem;
}

.marca-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .68rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--tinta-fraca);
    margin-bottom: 1.6rem;
}

.indice-verso {
    font-family: 'EB Garamond', Georgia, serif;
    font-style: italic;
    color: var(--tinta-fraca);
    font-size: 1rem;
    margin: -.4rem 0 1.6rem 0;
}

section[data-testid="stSidebar"] { background: #f4f1ea; }
section[data-testid="stSidebar"] .stRadio label p {
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 1.02rem;
}

.stButton button {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .72rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    border-radius: 2px;
    border: 1px solid var(--fio);
    background: transparent;
    color: var(--tinta-fraca);
}
.stButton button:hover {
    border-color: var(--tinta-fraca);
    color: var(--tinta);
    background: transparent;
}

@media (prefers-color-scheme: dark) {
    :root {
        --tinta: #ece7dd;
        --tinta-fraca: #9a938a;
        --papel: #14130f;
        --fio: #2c2a25;
    }
    section[data-testid="stSidebar"] { background: #1a1815; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Estado e navegação
# --------------------------------------------------------------------------

poemas = carregar_poemas()

if not poemas:
    st.markdown(f'<div class="marca">{TITULO_DO_SITE}</div>', unsafe_allow_html=True)
    st.info(
        "Nenhum poema ainda. Crie um arquivo `.md` dentro da pasta `poemas/` "
        "e ele aparece aqui."
    )
    st.stop()

por_slug = {p.slug: p for p in poemas}

# link compartilhável: ?poema=slug
slug_url = st.query_params.get("poema")
if slug_url in por_slug:
    st.session_state.setdefault("slug", slug_url)
st.session_state.setdefault("slug", poemas[0].slug)


def ir_para(slug: str) -> None:
    st.session_state.slug = slug
    st.query_params["poema"] = slug


# --- barra lateral -------------------------------------------------------

with st.sidebar:
    st.markdown(f'<div class="marca">{TITULO_DO_SITE}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="marca-sub">{AUTOR}</div>', unsafe_allow_html=True)

    busca = st.text_input("Buscar", placeholder="palavra, verso, título…", label_visibility="collapsed")

    todas_tags = sorted({t for p in poemas for t in p.tags})
    tags_escolhidas: list[str] = []
    if todas_tags:
        tags_escolhidas = st.multiselect("Temas", todas_tags, label_visibility="collapsed", placeholder="Temas")

    def filtra(p: Poema) -> bool:
        if tags_escolhidas and not set(tags_escolhidas) & set(p.tags):
            return False
        if busca:
            alvo = f"{p.titulo}\n{p.corpo}\n{' '.join(p.tags)}".lower()
            if busca.lower() not in alvo:
                return False
        return True

    visiveis = [p for p in poemas if filtra(p)]

    st.markdown("---")

    if not visiveis:
        st.caption("Nada encontrado.")
    else:
        indices = [p.slug for p in visiveis]
        atual = st.session_state.slug if st.session_state.slug in indices else indices[0]
        escolha = st.radio(
            "Poemas",
            indices,
            index=indices.index(atual),
            format_func=lambda s: por_slug[s].titulo,
            label_visibility="collapsed",
        )
        if escolha != st.session_state.slug:
            ir_para(escolha)

    st.markdown("---")
    if st.button("Ao acaso", use_container_width=True):
        ir_para(random.choice([p.slug for p in poemas]))
        st.rerun()

    st.caption("1 poema" if len(poemas) == 1 else f"{len(poemas)} poemas")


# --------------------------------------------------------------------------
# Página do poema
# --------------------------------------------------------------------------

poema = por_slug.get(st.session_state.slug, poemas[0])

st.markdown(
    f'<h1 class="poema-titulo">{html.escape(poema.titulo)}</h1>',
    unsafe_allow_html=True,
)
if poema.data:
    st.markdown(
        f'<div class="poema-data">{html.escape(poema.data)}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div class="poema-respiro"></div>', unsafe_allow_html=True)
if poema.epigrafe:
    st.markdown(
        f'<div class="poema-epigrafe">{para_html(poema.epigrafe)}</div>',
        unsafe_allow_html=True,
    )

for tipo, conteudo in partir_em_blocos(poema.corpo):
    if tipo == "texto":
        st.markdown(
            f'<div class="poema-corpo">{para_html(conteudo)}</div>',
            unsafe_allow_html=True,
        )
    else:
        arquivo, legenda = conteudo
        caminho = PASTA_FOTOS / arquivo
        st.markdown('<div class="poema-foto">', unsafe_allow_html=True)
        if caminho.exists():
            st.image(str(caminho))
            if legenda:
                st.markdown(
                    f'<div class="poema-legenda">{html.escape(legenda)}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.warning(f"Foto não encontrada: fotos/{arquivo}")
        st.markdown("</div>", unsafe_allow_html=True)

if poema.tags:
    st.markdown(
        '<div class="poema-tags">' + " · ".join(poema.tags) + "</div>",
        unsafe_allow_html=True,
    )
if poema.nota:
    st.markdown(
        f'<div class="poema-nota">{para_html(poema.nota)}</div>',
        unsafe_allow_html=True,
    )

# --- anterior / próximo ---------------------------------------------------

st.markdown("<div style='height:3.5rem'></div>", unsafe_allow_html=True)
pos = [p.slug for p in poemas].index(poema.slug)
esq, _, dir_ = st.columns([1, 2, 1])
with esq:
    if pos > 0 and st.button("← anterior", use_container_width=True):
        ir_para(poemas[pos - 1].slug)
        st.rerun()
with dir_:
    if pos < len(poemas) - 1 and st.button("próximo →", use_container_width=True):
        ir_para(poemas[pos + 1].slug)
        st.rerun()
