import altair as alt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import polars as pl
import streamlit as st

st.set_page_config(
    page_title="ENEM — RS",
    page_icon=":material/bar_chart:",
    layout="wide",
)

st.markdown(
    "<style>"
    "div[data-testid='stCaptionContainer'] p { text-align: justify; }"
    " section[data-testid='stSidebar'] .stMarkdown a { color: #ffffff; }"
    #" [data-testid='stMetricLabel'] * { font-weight: 700 !important; }"
    " .stMainBlockContainer { padding-top: 1rem !important; }"
    "</style>",
    unsafe_allow_html=True,
)

# ============================================================
# CONSTANTES E MAPEAMENTOS
# ============================================================

COLUMNS = [
    "TP_FAIXA_ETARIA", "TP_SEXO", "TP_COR_RACA", "TP_ESCOLA", "IN_TREINEIRO",
    "TP_ST_CONCLUSAO",
    "SG_UF_PROVA", "Q006",
    "NO_MUNICIPIO_PROVA",
    "CO_MUNICIPIO_ESC", "NO_MUNICIPIO_ESC", "SG_UF_ESC",
    "NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO",
    "TP_PRESENCA_CN", "TP_PRESENCA_CH", "TP_PRESENCA_LC", "TP_PRESENCA_MT",
]

NOTAS_COLS    = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
PRESENCA_COLS = ["TP_PRESENCA_CN", "TP_PRESENCA_CH", "TP_PRESENCA_LC", "TP_PRESENCA_MT"]

FAIXA_ETARIA_MAP = {
    1: "Menor de 17 anos", 2: "17 anos", 3: "18 anos", 4: "19 anos", 5: "20 anos",
    6: "21 anos", 7: "22 anos", 8: "23 anos", 9: "24 anos", 10: "25 anos",
    11: "Entre 26 e 30 anos", 12: "Entre 31 e 35 anos", 13: "Entre 36 e 40 anos",
    14: "Entre 41 e 45 anos", 15: "Entre 46 e 50 anos", 16: "Entre 51 e 55 anos",
    17: "Entre 56 e 60 anos", 18: "Entre 61 e 65 anos", 19: "Entre 66 e 70 anos",
    20: "Maior de 70 anos",
}
FAIXA_ORDER = list(FAIXA_ETARIA_MAP.values())

RACA_MAP = {
    0: "Não declarado", 1: "Branca", 2: "Preta", 3: "Parda",
    4: "Amarela", 5: "Indígena", 6: "Não dispõe da informação",
}

ESCOLA_MAP = {1: "Não Respondeu", 2: "Pública", 3: "Privada"}

ST_CONCLUSAO_MAP = {
    1: "Já concluiu o Ensino Médio",
    2: "Concluirá no ano do exame",
    3: "Concluirá após o ano do exame",
    4: "Não concluiu e não está cursando",
}

NOTAS_PROVAS = {
    "NU_NOTA_CN":      "Ciências da Natureza",
    "NU_NOTA_CH":      "Ciências Humanas",
    "NU_NOTA_LC":      "Linguagens",
    "NU_NOTA_MT":      "Matemática",
    "NU_NOTA_REDACAO": "Redação",
}

CORES_AREAS = {
    "Ciências da Natureza": "#D97A5C",
    "Ciências Humanas":     "#E9B44C",
    "Linguagens":           "#47A398",
    "Matemática":           "#7B5EA7",
    "Redação":              "#8BC9D0",
}

MAPA_RENDA_SM = {
    "A": "Sem renda",
    "B": "Até 2 SM", "C": "Até 2 SM", "D": "Até 2 SM",
    "E": "2 a 4 SM",  "F": "2 a 4 SM",  "G": "2 a 4 SM",
    "H": "4 a 8 SM",  "I": "4 a 8 SM",  "J": "4 a 8 SM", "K": "4 a 8 SM",
    "L": "8 a 12 SM", "M": "8 a 12 SM", "N": "8 a 12 SM",
    "O": "Acima de 12 SM", "P": "Acima de 12 SM", "Q": "Acima de 12 SM",
}
SM_POR_ANO = {2021: 1_100, 2022: 1_212, 2023: 1_320}
ORDEM_SM = ["Sem renda", "Até 2 SM", "2 a 4 SM", "4 a 8 SM", "8 a 12 SM", "Acima de 12 SM"]

FAIXA_ETARIA_AGRUPADA = {
    1:  "Até 17 anos",
    2:  "Até 17 anos",
    3:  "18 anos",
    4:  "19 anos",
    5:  "20-24 anos",
    6:  "20-24 anos",
    7:  "20-24 anos",
    8:  "20-24 anos",
    9:  "20-24 anos",
    10: "25-30 anos",
    11: "25-30 anos",
    12: "31-40 anos",
    13: "31-40 anos",
    14: "41-50 anos",
    15: "41-50 anos",
    16: "51-70 anos",
    17: "51-70 anos",
    18: "51-70 anos",
    19: "51-70 anos",
    20: "Mais de 70 anos",
}
ORDEM_FAIXA_AGRUPADA = ["Até 17 anos", "18 anos", "19 anos", "20-24 anos", "25-30 anos", "31-40 anos", "41-50 anos", "51-70 anos", "Mais de 70 anos"]

AREA_OPTIONS = {
    "Ciências da Natureza": "NU_NOTA_CN",
    "Ciências Humanas":     "NU_NOTA_CH",
    "Linguagens":           "NU_NOTA_LC",
    "Matemática":           "NU_NOTA_MT",
    "Redação":              "NU_NOTA_REDACAO",
    "Média Geral":          "MEDIA_GERAL",
}

COR_PUBLICA  = "#4E79D9"
COR_PRIVADA  = "#F28E2B"
COR_NEUTRO   = "#B8C2CC"   # Não informado
COR_NEUTRO2  = "#D6DCE5"   # Sem resposta
COR_OUTROS   = "#94A3B8"   # Outros / residual

CORES_ESCOLA = {
    "Pública":        "#4E79D9",
    "Privada":        "#F28E2B",
    "Não Respondeu":  "#B8C2CC",
}

CORES_SEXO = {
    "Masculino":     "#4E79D9",
    "Feminino":      "#D46A92",
    "Não Informado": "#B8C2CC",
}

CORES_RACA = {
    "Branca":                    "#5D5C86",
    "Parda":                     "#5D5C86",
    "Preta":                     "#5D5C86",
    "Amarela":                   "#5D5C86",
    "Indígena":                  "#5D5C86",
    "Não declarado":             "#B8C2CC",
    "Não dispõe da informação":  "#D6DCE5",
}

CHART_HEIGHT = 550


def _heatmap_annotations(pivot, col_labels, threshold=35):
    """Build Plotly annotation dicts for a heatmap pivot (rows × cols)."""
    anns = []
    for ri, row_label in enumerate(pivot.index.tolist()):
        for ci, col_label in enumerate(col_labels):
            val = pivot.values[ri, ci]
            txt = f"{val:.1f}%" if not np.isnan(val) else "—"
            ink = "#0b0b0b" if (not np.isnan(val) and val < threshold) else "#ffffff"
            anns.append(dict(
                x=col_label, y=row_label,
                text=f"<b>{txt}</b>",
                showarrow=False,
                font=dict(size=12, color=ink),
                xref="x", yref="y",
            ))
    return anns


def _interp_color(v, stops=None):
    """Linearly interpolate a hex colour from a list of (pos, hex) stops."""
    if stops is None:
        stops = [
            (0.0, "#fde8e8"), (0.25, "#f4a9a9"),
            (0.5, "#e86262"), (0.75, "#c93232"), (1.0, "#8b0000"),
        ]
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t0 <= v <= t1:
            f = (v - t0) / (t1 - t0)
            r = int(int(c0[1:3], 16) + f * (int(c1[1:3], 16) - int(c0[1:3], 16)))
            g = int(int(c0[3:5], 16) + f * (int(c1[3:5], 16) - int(c0[3:5], 16)))
            b = int(int(c0[5:7], 16) + f * (int(c1[5:7], 16) - int(c0[5:7], 16)))
            return f"#{r:02x}{g:02x}{b:02x}"
    return stops[-1][1]


# ============================================================
# CARREGAMENTO E PRÉ-PROCESSAMENTO DOS DADOS
# ============================================================

DATA_FILES = {
    2021: "data/MICRODADOS_ENEM_2021.csv",
    2022: "data/MICRODADOS_ENEM_2022.csv",
    2023: "data/MICRODADOS_ENEM_2023.csv",
}

_missing = [p for p in DATA_FILES.values() if not __import__("pathlib").Path(p).exists()]
if _missing:
    st.error(
        "**Arquivo(s) de dados não encontrado(s).**\n\n"
        + "\n".join(f"- `{p}`" for p in _missing) + "\n\n"
        "Consulte o **README** para instruções de como obter os dados antes de executar o dashboard."
    )
    st.stop()


@st.cache_data
def get_enem_dataset(columns: tuple):
    frames = []
    for ano, path in DATA_FILES.items():
        df = pl.read_csv(path, separator=";", encoding="latin1", columns=list(columns))
        frames.append(df.with_columns(pl.lit(ano).alias("ANO")))
    return pl.concat(frames)


PRESENCA_FILTER = pl.all_horizontal([pl.col(c) == 1 for c in PRESENCA_COLS])

_enem_all = get_enem_dataset(tuple(COLUMNS))
_enem_rs  = _enem_all.filter(pl.col("SG_UF_PROVA") == "RS")

# ============================================================
# SIDEBAR — navegação e filtros
# ============================================================
_TODOS = "Todos"
_municipios = sorted(_enem_rs["NO_MUNICIPIO_PROVA"].drop_nulls().unique().to_list())
_anos_disp  = sorted(_enem_rs["ANO"].unique().to_list())

with st.sidebar:
    st.markdown("## Filtros")
    anos_sel = st.selectbox(
        "Edição (ano)",
        options=[_TODOS] + _anos_disp,
        index=0,
        help="Edição do ENEM a analisar.",
    )
    municipio_sel = st.selectbox(
        "Município",
        options=[_TODOS] + _municipios,
        index=0,
        help="Município onde a prova foi realizada.",
    )

# Aplica os filtros; todos os blocos abaixo consomem enem_df / enem_participantes
if anos_sel == _TODOS:
    _enem_rs_filtered = _enem_rs
else:
    _enem_rs_filtered = _enem_rs.filter(pl.col("ANO") == anos_sel)

if municipio_sel == _TODOS:
    enem_df = _enem_rs_filtered
else:
    enem_df = _enem_rs_filtered.filter(pl.col("NO_MUNICIPIO_PROVA") == municipio_sel)

if enem_df.is_empty():
    st.warning(f"Nenhum dado encontrado para o município **{municipio_sel}**.")
    st.stop()

enem_participantes = enem_df.filter(PRESENCA_FILTER)

if enem_participantes.is_empty():
    st.warning(f"Nenhum participante efetivo encontrado para o município **{municipio_sel}**.")
    st.stop()


def get_desempenho_data(participantes: pl.DataFrame):
    return (
        participantes
        .filter(pl.col("Q006").is_not_null())
        .filter(pl.col("TP_ESCOLA").is_in([2, 3]))
        .with_columns([
            pl.col("Q006")
              .replace(MAPA_RENDA_SM).cast(pl.String)
              .alias("FAIXA_RENDA_SM"),
            pl.col("TP_ESCOLA")
              .cast(pl.String)
              .replace({"2": "Pública", "3": "Privada"}).cast(pl.String)
              .alias("TP_ESCOLA_LABEL"),
            pl.mean_horizontal(NOTAS_COLS).alias("MEDIA_GERAL"),
        ])
        .filter(pl.col("FAIXA_RENDA_SM").is_in(ORDEM_SM))
    )


desempenho_df = get_desempenho_data(enem_participantes)


# ============================================================
# CABEÇALHO E INTRODUÇÃO
# ============================================================

st.markdown('<div id="topo"></div>', unsafe_allow_html=True)

_anos_label = "2021, 2022, 2023" if anos_sel == _TODOS else str(anos_sel)
st.title(f":material/bar_chart: Análise de microdados do Exame Nacional do Ensino Médio (ENEM) — {_anos_label}")

tab_visao, tab_perfil, tab_desempenho, tab_ausencia = st.tabs([
    "Visão geral dos dados",
    "Perfil dos Participantes",
    "Desempenho",
    "Ausências",
])


# ============================================================
# ABA 1 — VISÃO GERAL
# ============================================================

def get_enem_kpis(data):
    total_inscritos   = data.height
    participantes_df  = data.filter(PRESENCA_FILTER)
    total_participantes = participantes_df.height

    notas_validas = (
        participantes_df.select(NOTAS_COLS).unpivot().drop_nulls("value")["value"]
    )
    media_geral       = round(notas_validas.mean(), 2) if notas_validas.len() > 0 else 0.0
    taxa_participacao = round(total_participantes / total_inscritos * 100, 1) if total_inscritos > 0 else 0.0

    return {
        "total_inscritos":     total_inscritos,
        "total_participantes": total_participantes,
        "media_geral":         media_geral,
        "taxa_participacao":   taxa_participacao,
    }


enem_kpis = get_enem_kpis(enem_df)

with tab_visao:
    st.markdown(
        "Análise dos microdados do ENEM para o Rio Grande do Sul, cobrindo perfil demográfico, socioeconômico e desempenho acadêmico dos participantes. "
        "O dashboard é organizado em quatro abas: visão geral com indicadores agregados, perfil dos participantes, análise de desempenho por área e ausências. "
        "Use os filtros na barra lateral para recortar os dados por edição e município.  \n"
        f"**Edições analisadas:** {_anos_label}  \n"
        "**Fonte dos dados:** [INEP — Microdados do ENEM](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)  "
    )
    st.divider()
    st.subheader(":material/leaderboard: Indicadores gerais")

    _anos_kpi_disp = sorted(_enem_rs_filtered["ANO"].unique().to_list())
    _CORES_ANOS = {"2021": "#1D9E75", "2022": "#6250D6", "2023": "#e19835"}

    def _kpi_bar_layout(fig):
        fig.update_layout(
            xaxis=dict(title=None, tickfont=dict(size=9), showticklabels=True),
            yaxis=dict(title=None, tickfont=dict(size=10), type="category"),
            margin=dict(t=4, b=4, l=28, r=4),
            height=120,
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)

    def _kpi_line_layout(fig):
        fig.update_layout(
            title=dict(text=None),
            xaxis=dict(title=None, tickfont=dict(size=10), type="category"),
            yaxis=dict(title=None, tickfont=dict(size=9), showticklabels=True),
            margin=dict(t=4, b=28, l=4, r=4),
            height=120,
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container(border=True):
            st.metric("Total de Inscritos", f"{enem_kpis['total_inscritos']:,}")
            if len(_anos_kpi_disp) > 1:
                _inscritos_rows = [
                    {"ano": str(_a), "inscritos": _enem_rs_filtered.filter(pl.col("ANO") == _a).height}
                    for _a in _anos_kpi_disp
                ]
                _inscritos_df = pd.DataFrame(_inscritos_rows)
                _fig_inscritos = go.Figure(go.Bar(
                    x=_inscritos_df["inscritos"],
                    y=_inscritos_df["ano"],
                    orientation="h",
                    marker_color=[_CORES_ANOS.get(a, COR_PUBLICA) for a in _inscritos_df["ano"]],
                    hovertemplate="Ano: %{y}<br>Inscritos: %{x:,}<extra></extra>",
                ))
                _kpi_bar_layout(_fig_inscritos)
                st.markdown("<p style='font-size:12px;color:gray;margin:0 0 2px 0;'>Inscritos por ano</p>", unsafe_allow_html=True)
                st.plotly_chart(_fig_inscritos, use_container_width=True, config={"displayModeBar": False})
    with col2:
        with st.container(border=True):
            st.metric("Total de Participantes", f"{enem_kpis['total_participantes']:,}")
            if len(_anos_kpi_disp) > 1:
                _part_rows = [
                    {"ano": str(_a), "participantes": _enem_rs_filtered.filter(pl.col("ANO") == _a).filter(PRESENCA_FILTER).height}
                    for _a in _anos_kpi_disp
                ]
                _part_df = pd.DataFrame(_part_rows)
                _fig_part_card = go.Figure(go.Bar(
                    x=_part_df["participantes"],
                    y=_part_df["ano"],
                    orientation="h",
                    marker_color=[_CORES_ANOS.get(a, COR_PUBLICA) for a in _part_df["ano"]],
                    hovertemplate="Ano: %{y}<br>Participantes: %{x:,}<extra></extra>",
                ))
                _kpi_bar_layout(_fig_part_card)
                st.markdown("<p style='font-size:12px;color:gray;margin:0 0 2px 0;'>Participantes por ano</p>", unsafe_allow_html=True)
                st.plotly_chart(_fig_part_card, use_container_width=True, config={"displayModeBar": False})
    with col3:
        with st.container(border=True):
            st.metric("Taxa de Participação", f"{enem_kpis['taxa_participacao']:.1f}%")
            if len(_anos_kpi_disp) > 1:
                _taxa_rows = []
                for _a in _anos_kpi_disp:
                    _df_a = _enem_rs_filtered.filter(pl.col("ANO") == _a)
                    _insc = _df_a.height
                    _part = _df_a.filter(PRESENCA_FILTER).height
                    _taxa = round(_part / _insc * 100, 1) if _insc > 0 else 0.0
                    _taxa_rows.append({"ano": str(_a), "taxa": _taxa})
                _taxa_df = pd.DataFrame(_taxa_rows)
                _fig_taxa_card = go.Figure(go.Scatter(
                    x=_taxa_df["ano"],
                    y=_taxa_df["taxa"],
                    mode="lines+markers",
                    line=dict(color=COR_PRIVADA, width=2),
                    marker=dict(size=7, color=COR_PRIVADA, line=dict(color="white", width=1.5)),
                    hovertemplate="Ano: %{x}<br>Taxa: %{y:.1f}%<extra></extra>",
                ))
                _kpi_line_layout(_fig_taxa_card)
                st.markdown("<p style='font-size:12px;color:gray;margin:0 0 2px 0;'>Taxa de participação por ano</p>", unsafe_allow_html=True)
                st.plotly_chart(_fig_taxa_card, use_container_width=True, config={"displayModeBar": False})

    with col4:
        with st.container(border=True):
            st.metric("Média Geral", f"{enem_kpis['media_geral']:.2f}")
            if len(_anos_kpi_disp) > 1:
                _media_rows = []
                for _a in _anos_kpi_disp:
                    _part_a = _enem_rs_filtered.filter(pl.col("ANO") == _a).filter(PRESENCA_FILTER)
                    _m = _part_a.select(pl.mean_horizontal(NOTAS_COLS).mean()).item() if _part_a.height > 0 else None
                    _media_rows.append({"ano": str(_a), "nota_media": round(_m, 1) if _m else None})
                _media_df = pd.DataFrame(_media_rows)
                _fig_media_card = go.Figure(go.Scatter(
                    x=_media_df["ano"],
                    y=_media_df["nota_media"],
                    mode="lines+markers",
                    line=dict(color=COR_PRIVADA, width=2),
                    marker=dict(size=7, color=COR_PRIVADA, line=dict(color="white", width=1.5)),
                    hovertemplate="Ano: %{x}<br>Nota média: %{y:.1f}<extra></extra>",
                ))
                _kpi_line_layout(_fig_media_card)
                st.markdown("<p style='font-size:12px;color:gray;margin:0 0 2px 0;'>Nota média por ano</p>", unsafe_allow_html=True)
                st.plotly_chart(_fig_media_card, use_container_width=True, config={"displayModeBar": False})




# ============================================================
# ABA 2 — PERFIL DOS PARTICIPANTES
# ============================================================

with tab_perfil:

    # --- Seção 1: Distribuição por Faixa Etária e Sexo ---
    st.subheader(":material/person: Distribuição por faixa etária, sexo e cor/raça")

    st.caption(
        "A pirâmide etária compara o volume de participantes femininos e masculinos em cada faixa, "
        "permitindo identificar em quais faixas a diferença entre os sexos é mais acentuada. "
        "O gráfico ao lado mostra o total geral por sexo."
    )

    # --- Pirâmide etária ---
    # Mapeamento final: códigos 1-20 → rótulos da pirâmide (51-70 já mesclados)
    _FAIXA_MAP_PYRAMID = {
        1: "Menor de 17 anos", 2: "17 anos", 3: "18 anos", 4: "19 anos",
        5: "20 anos", 6: "21 anos", 7: "22 anos", 8: "23 anos", 9: "24 anos",
        10: "25 anos", 11: "Entre 26 e 30 anos", 12: "Entre 31 e 35 anos",
        13: "Entre 36 e 40 anos", 14: "Entre 41 e 45 anos", 15: "Entre 46 e 50 anos",
        16: "Entre 51 e 70 anos", 17: "Entre 51 e 70 anos",
        18: "Entre 51 e 70 anos", 19: "Entre 51 e 70 anos",
        20: "Maior de 70 anos",
    }
    _FAIXA_ORDER_PYRAMID = list(dict.fromkeys(_FAIXA_MAP_PYRAMID.values()))

    pyramid_source = (
        enem_participantes
        .filter(pl.col("TP_FAIXA_ETARIA").is_in(list(_FAIXA_MAP_PYRAMID.keys())))
        .with_columns([
            pl.col("TP_FAIXA_ETARIA").cast(pl.String)
              .replace({str(k): v for k, v in _FAIXA_MAP_PYRAMID.items()})
              .alias("faixa_etaria"),
            pl.col("TP_SEXO")
              .replace({"M": "Masculino", "F": "Feminino"}).cast(pl.String)
              .alias("sexo"),
        ])
        .group_by("faixa_etaria", "sexo")
        .agg(pl.len().alias("total"))
    )

    pyramid_df = pyramid_source.to_pandas()
    gender_df  = (
        pyramid_source
        .group_by("sexo")
        .agg(pl.col("total").sum().alias("total"))
        .sort("sexo")
        .to_pandas()
    )

    col_pyramid, col_gender = st.columns([6, 2], gap="large")

    if not pyramid_df.empty:
        color_scale = alt.Scale(
            domain=["Masculino", "Feminino"],
            range=[CORES_SEXO["Masculino"], CORES_SEXO["Feminino"]],
        )

        _max_pyramid = int(pyramid_df["total"].max())
        _x_scale = alt.Scale(domain=[0, _max_pyramid])

        with col_pyramid:
            base = alt.Chart(pyramid_df)

            nearest = alt.selection_point(nearest=True, on="pointerover", fields=["faixa_etaria"], empty=False)

            left = (
                base.transform_filter(alt.datum.sexo == "Feminino")
                .encode(
                    alt.Y("faixa_etaria:O").sort(_FAIXA_ORDER_PYRAMID).axis(None),
                    alt.X("total:Q").title("Quantidade").sort("descending").scale(_x_scale),
                    alt.Color("sexo:N").scale(color_scale).title("Sexo"),
                    alt.Tooltip(["faixa_etaria:N", "sexo:N", "total:Q"]),
                    opacity=alt.condition(nearest, alt.value(1), alt.value(0.8)),
                )
                .mark_bar()
                .add_params(nearest)
                .properties(title="Feminino", height=420)
            )

            middle = (
                base.encode(
                    alt.Y("faixa_etaria:O").sort(_FAIXA_ORDER_PYRAMID).axis(None),
                    alt.Text("faixa_etaria:N"),
                )
                .mark_text(fontSize=10)
                .properties(width=150, height=420)
            )

            nearest_right = alt.selection_point(nearest=True, on="pointerover", fields=["faixa_etaria"], empty=False)

            right = (
                base.transform_filter(alt.datum.sexo == "Masculino")
                .encode(
                    alt.Y("faixa_etaria:O").sort(_FAIXA_ORDER_PYRAMID).axis(None),
                    alt.X("total:Q").title("Quantidade").scale(_x_scale),
                    alt.Color("sexo:N").scale(color_scale).title("Sexo"),
                    alt.Tooltip(["faixa_etaria:N", "sexo:N", "total:Q"]),
                    opacity=alt.condition(nearest_right, alt.value(1), alt.value(0.8)),
                )
                .mark_bar()
                .add_params(nearest_right)
                .properties(title="Masculino", height=420)
            )

            pyramid_chart = (
                alt.hconcat(left, middle, right, spacing=5)
                .resolve_scale(x="independent", color="shared")
                .properties(title="Distribuição por faixa etária e sexo")
                .configure_view(stroke=None)
                .configure_title(fontSize=14, anchor="middle")
                .configure_legend(orient="bottom", title=None, labelFontSize=12)
            )
            st.altair_chart(pyramid_chart, use_container_width=True)

        with col_gender:
            gender_chart = (
                alt.Chart(gender_df)
                .transform_calculate(sexo_abrev="datum.sexo == 'Feminino' ? 'F' : 'M'")
                .mark_bar()
                .encode(
                    alt.X("sexo_abrev:N").title(None).sort(["F", "M"]).axis(labelAngle=0),
                    alt.Y("total:Q").title("Participantes"),
                    alt.Color("sexo:N").scale(color_scale).legend(None),
                    alt.Tooltip(["sexo:N", "total:Q"]),
                )
                .properties(title="Distribuição por sexo", height=540, padding={"top": 40, "left": 5, "right": 5, "bottom": 5})
                .configure_title(fontSize=14, anchor="middle")
            )
            st.altair_chart(gender_chart, use_container_width=True)

    col_raca = st.columns(1)[0]

    with col_raca:
        raca_df = (
            enem_participantes
            .filter(pl.col("TP_COR_RACA").is_not_null())
            .with_columns(
                pl.col("TP_COR_RACA").cast(pl.String)
                  .replace({str(k): v for k, v in RACA_MAP.items()}).alias("raca")
            )
            .group_by("raca").agg(pl.len().alias("total"))
            .to_pandas()
        )
        _total_raca = raca_df["total"].sum()
        raca_df["pct"] = (raca_df["total"] / _total_raca * 100).round(1)
        nearest_raca = alt.selection_point(nearest=True, on="pointerover", fields=["raca"], empty=False)
        st.altair_chart(
            alt.Chart(raca_df).mark_bar().encode(
                alt.X("total:Q").title("Participantes"),
                alt.Y("raca:N").title(None).sort("-x"),
                alt.Color("raca:N").scale(
                    alt.Scale(
                        domain=list(CORES_RACA.keys()),
                        range=list(CORES_RACA.values()),
                    )
                ).legend(None),
                alt.Tooltip(["raca:N", "total:Q", "pct:Q"]),
                opacity=alt.condition(nearest_raca, alt.value(1), alt.value(1)),
            ).add_params(nearest_raca).properties(title="Participantes por cor/raça autoeclarada", height=280),
            use_container_width=True,
        )


    # --- Seção 2: Perfil Escolar ---
    st.divider()
    st.subheader(":material/school: Perfil escolar")
    st.caption(
        "Distribuição dos participantes por tipo de escola (pública ou privada) e por situação de conclusão do Ensino Médio. "
        "Apenas participantes que declararam escola pública ou privada são incluídos no gráfico de tipo de escola."
    )

    col_escola, col_conclusao = st.columns([2,4], gap="large")


    with col_escola:
        escola_df = (
            enem_participantes
            .filter(pl.col("TP_ESCOLA").is_in([2, 3]))
            .with_columns(
                pl.col("TP_ESCOLA")
                  .replace_strict(ESCOLA_MAP, default="Não Respondeu", return_dtype=pl.String)
                  .alias("escola")
            )
            .group_by("escola").agg(pl.len().alias("total"))
            .to_pandas()
        )
        _total_escola = escola_df["total"].sum()
        escola_df["pct"] = (escola_df["total"] / _total_escola * 100).round(1)
        escola_df["_grupo"] = "Participantes"
        _ordem_escola_emp = ["Pública", "Privada"]
        st.altair_chart(
            alt.Chart(escola_df).mark_bar().encode(
                alt.X("total:Q").title("Participantes").stack("normalize"),
                alt.Y("_grupo:N").title(None),
                alt.Color("escola:N").scale(
                    alt.Scale(
                        domain=_ordem_escola_emp,
                        range=[CORES_ESCOLA["Pública"], CORES_ESCOLA["Privada"]],
                    )
                ).legend(orient="bottom", title=None),
                alt.Order("escola:N", sort="ascending"),
                alt.Tooltip(["escola:N", "total:Q", "pct:Q"]),
            ).properties(title="Participantes por tipo de escola", height=250),
            use_container_width=True,
        )

    with col_conclusao:
        conclusao_df = (
            enem_participantes
            .filter(pl.col("TP_ST_CONCLUSAO").is_not_null())
            .with_columns(
                pl.col("TP_ST_CONCLUSAO").cast(pl.String)
                  .replace({str(k): v for k, v in ST_CONCLUSAO_MAP.items()}).alias("situacao")
            )
            .group_by("situacao").agg(pl.len().alias("total"))
            .to_pandas()
        )
        _total_conclusao = conclusao_df["total"].sum()
        conclusao_df["pct"] = (conclusao_df["total"] / _total_conclusao * 100).round(1)
        _ordem_conclusao = list(ST_CONCLUSAO_MAP.values())
        nearest_conclusao = alt.selection_point(nearest=True, on="pointerover", fields=["situacao"], empty=False)
        st.altair_chart(
            alt.Chart(conclusao_df).mark_bar().encode(
                alt.X("total:Q").title("Participantes"),
                alt.Y("situacao:N").title(None).sort(_ordem_conclusao).axis(labelLimit=230, labelFontSize=12),
                alt.Color("situacao:N").scale(
                    alt.Scale(
                        domain=_ordem_conclusao,
                        range=["#0F6E56", "#534AB7", "#D85A30", "#B4B2A9"],
                    )
                ).legend(None),
                alt.Tooltip(["situacao:N", "total:Q", "pct:Q"]),
                opacity=alt.condition(nearest_conclusao, alt.value(1), alt.value(1)),
            ).add_params(nearest_conclusao).properties(title="Situação escolar dos participantes", height=200),
            use_container_width=True,
        )

    # --- Heatmap: distribuição socioeconômica ---
    st.divider()
    st.subheader(":material/groups: Distribuição socioeconômica dos participantes")
    st.caption(
        "Percentual de participantes de cada grupo demográfico em cada faixa de renda familiar. "
        "A soma de cada linha totaliza 100%, permitindo comparar a distribuição de renda entre grupos distintos. "
        "Tons mais escuros indicam maior concentração de participantes naquela faixa."
    )

    _GRUPOS_SOCIO = {
        "Cor/Raça":     "RACA_SOCIO",
        "Sexo":         "SEXO_SOCIO",
        "Faixa Etária": "FAIXA_SOCIO",
    }
    _ORDEM_GRUPOS_SOCIO = {
        "RACA_SOCIO":  ["Branca", "Preta", "Parda", "Amarela", "Indígena"],
        "SEXO_SOCIO":  ["Feminino", "Masculino"],
        "FAIXA_SOCIO": ORDEM_FAIXA_AGRUPADA,
    }

    _grupo_socio_sel = st.selectbox(
        "Agrupar por",
        options=list(_GRUPOS_SOCIO.keys()),
        key="heatmap_socio_grupo",
    )
    _col_grupo_socio = _GRUPOS_SOCIO[_grupo_socio_sel]

    _socio_base = (
        enem_participantes
        .with_columns([
            pl.col("Q006")
              .replace(MAPA_RENDA_SM).cast(pl.String)
              .alias("FAIXA_RENDA_SM"),
            pl.col("TP_COR_RACA").cast(pl.String)
              .replace({str(k): v for k, v in RACA_MAP.items()}).cast(pl.String)
              .alias("RACA_SOCIO"),
            pl.col("TP_SEXO")
              .replace({"M": "Masculino", "F": "Feminino"}).cast(pl.String)
              .alias("SEXO_SOCIO"),
            pl.col("TP_FAIXA_ETARIA").cast(pl.String)
              .replace({str(k): v for k, v in FAIXA_ETARIA_AGRUPADA.items()}).cast(pl.String)
              .alias("FAIXA_SOCIO"),
        ])
        .filter(pl.col("FAIXA_RENDA_SM").is_in(ORDEM_SM))
        .filter(pl.col(_col_grupo_socio).is_not_null())
    )

    _ordem_y_socio = [
        g for g in _ORDEM_GRUPOS_SOCIO[_col_grupo_socio]
        if g in _socio_base[_col_grupo_socio].unique().to_list()
    ]

    _socio_counts = (
        _socio_base
        .filter(pl.col(_col_grupo_socio).is_in(_ordem_y_socio))
        .group_by(_col_grupo_socio, "FAIXA_RENDA_SM")
        .agg(pl.len().alias("n"))
        .to_pandas()
    )

    if _socio_counts.empty:
        st.warning("Nenhum dado disponível para a combinação de filtros selecionada.")
    else:
        _group_totals = _socio_counts.groupby(_col_grupo_socio, observed=True)["n"].transform("sum")
        _socio_counts["pct"] = (_socio_counts["n"] / _group_totals * 100).round(1)

        _socio_pivot = (
            _socio_counts
            .pivot(index=_col_grupo_socio, columns="FAIXA_RENDA_SM", values="pct")
            .reindex(columns=ORDEM_SM)
            .reindex([g for g in _ordem_y_socio if g in _socio_counts[_col_grupo_socio].values])
        )
        _socio_n_pivot = (
            _socio_counts
            .pivot(index=_col_grupo_socio, columns="FAIXA_RENDA_SM", values="n")
            .reindex(index=_socio_pivot.index, columns=ORDEM_SM)
        )
        _socio_total_pivot = _socio_counts.groupby(_col_grupo_socio, observed=True)["n"].sum()
        _total_matrix = np.array([
            [_socio_total_pivot.get(row, 0)] * len(ORDEM_SM)
            for row in _socio_pivot.index
        ])
        _custom_socio = np.stack([_total_matrix, _socio_n_pivot.values], axis=-1)

        _COLORSCALE_SOCIO = [
            [0.0, "#d4edda"], [0.2, "#a3d4ab"], [0.4, "#6db87c"],
            [0.6, "#3a9a52"], [0.8, "#1f7a38"], [1.0, "#0a5220"],
        ]

        fig_socio = go.Figure(go.Heatmap(
            z=_socio_pivot.values,
            x=ORDEM_SM,
            y=_socio_pivot.index.tolist(),
            colorscale=_COLORSCALE_SOCIO,
            zmin=0, zmax=100,
            customdata=_custom_socio,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Faixa de renda: %{x}<br>"
                "Total no grupo: %{customdata[0]:,}<br>"
                "Participantes na faixa: %{customdata[1]:,}<br>"
                "Percentual: %{z:.1f}%"
                "<extra></extra>"
            ),
            colorbar=dict(
                title=dict(text="%", font=dict(size=12)),
                ticksuffix="%", thickness=14, len=0.8,
            ),
            xgap=2, ygap=2,
        ))

        _anns_socio = _heatmap_annotations(_socio_pivot, ORDEM_SM)

        fig_socio.update_layout(
            title=dict(
                text=f"Distribuição de renda por <b>{_grupo_socio_sel}</b>",
                x=0.5, xanchor="center", font=dict(size=15),
            ),
            xaxis=dict(title="Faixa de renda familiar", tickfont=dict(size=11), side="bottom"),
            yaxis=dict(title=None, tickfont=dict(size=12), autorange="reversed"),
            annotations=_anns_socio,
            margin=dict(t=60, b=60, l=160, r=40),
            height=max(280, 60 + len(_ordem_y_socio) * 52),
        )
        st.plotly_chart(fig_socio, use_container_width=True)

        st.caption(
            "Passe o cursor sobre uma célula para ver o total de participantes do grupo e a quantidade naquela faixa de renda. "
            "Apenas participantes com renda declarada e escola pública ou privada são considerados."
        )


# ============================================================
# ABA 3 — ANÁLISE DE DESEMPENHO
# ============================================================

with tab_desempenho:

    # --- Seção 1: Distribuição das Notas ---
    st.subheader(":material/bar_chart: Distribuição das notas por área do conhecimento")
    st.caption(
        "Distribuição das notas dos participantes em cada uma das cinco áreas do ENEM. "
        "A caixa cobre os 50% centrais (Q1–Q3) e a linha central indica a mediana; "
        "valores fora dos limites são considerados outliers e não são exibidos. "
        "Passe o cursor para ver os valores detalhados de cada área."
    )
    enem_df_geral = (
        desempenho_df
        .select(list(NOTAS_PROVAS.keys()))
        .to_pandas()
    )

    fig_box   = go.Figure()
    annotations = []

    for coluna, titulo in NOTAS_PROVAS.items():
        dados   = enem_df_geral[coluna].dropna()
        mediana = round(dados.median(), 0)
        cor     = CORES_AREAS[titulo]
        fig_box.add_trace(go.Box(
            y=dados, name=titulo,
            boxpoints=False,
            marker_color=cor, line_color=cor, fillcolor=cor, opacity=0.8,
            hovertemplate=(
                f"<b>{titulo}</b><br>"
                "Máx (sem outliers): %{upperfence:.0f}<br>"
                "Q3: %{q3:.0f}<br>"
                "Mediana: %{median:.0f}<br>"
                "Q1: %{q1:.0f}<br>"
                "Mín (sem outliers): %{lowerfence:.0f}<extra></extra>"
            ),
        ))
        annotations.append(dict(
            x=titulo, y=mediana,
            text=f"<b>{mediana:.0f}</b>",
            showarrow=False, xanchor="left", xshift=22,
            font=dict(size=10, color=cor),
        ))

    fig_box.update_layout(
        title=dict(text="Distribuição das notas por área do conhecimento", x=0.5, xanchor="center", font=dict(size=15)),
        yaxis=dict(title="Nota", range=[300, 900], tickfont=dict(size=11)),
        xaxis=dict(tickfont=dict(size=11)),
        showlegend=False,
        annotations=annotations,
        margin=dict(t=60, b=40, l=60, r=20),
        height=420,
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # --- Seção 2: Nota Média por Faixa Etária ---
    st.divider()
    st.subheader(":material/timeline: Nota média por faixa etária")
    st.caption(
        f"Nota média por faixa etária e área do conhecimento — ENEM {_anos_label}. "
        "Permite observar se participantes mais jovens ou mais velhos apresentam desempenho distinto em cada área. "
        "Os gráficos individuais abaixo detalham cada área com a média geral como linha de referência."
    )
    colunas_sel = list(NOTAS_PROVAS.keys())

    etaria_base = (
        enem_participantes
        .filter(pl.col("TP_FAIXA_ETARIA").is_in(list(FAIXA_ETARIA_MAP.keys())))
        .with_columns(
            pl.col("TP_FAIXA_ETARIA").cast(pl.String)
              .replace({str(k): v for k, v in FAIXA_ETARIA_MAP.items()})
              .alias("FAIXA_ETARIA_LABEL")
        )
        .filter(pl.all_horizontal([pl.col(c) > 0 for c in colunas_sel]))
        .drop_nulls(colunas_sel)
    )

    faixas_validas = (
        etaria_base
        .group_by("FAIXA_ETARIA_LABEL").agg(pl.len().alias("n"))
        .filter(pl.col("n") >= 30)
        ["FAIXA_ETARIA_LABEL"].to_list()
    )

    medias_etaria = (
        etaria_base
        .filter(pl.col("FAIXA_ETARIA_LABEL").is_in(faixas_validas))
        .group_by("FAIXA_ETARIA_LABEL")
        .agg([pl.col(c).mean().alias(c) for c in colunas_sel])
        .to_pandas()
    )
    medias_etaria["FAIXA_ETARIA_LABEL"] = (
        medias_etaria["FAIXA_ETARIA_LABEL"]
        .astype("category")
        .cat.set_categories([f for f in FAIXA_ORDER if f in faixas_validas], ordered=True)
    )
    medias_etaria = medias_etaria.sort_values("FAIXA_ETARIA_LABEL")

    fig_etaria = go.Figure()
    for col, label in NOTAS_PROVAS.items():
        fig_etaria.add_trace(go.Scatter(
                x=medias_etaria["FAIXA_ETARIA_LABEL"].astype(str).tolist(),
                y=medias_etaria[col].round(1).tolist(),
                mode="lines+markers", name=label,
                line=dict(color=CORES_AREAS[label], width=2),
                marker=dict(size=7, color=CORES_AREAS[label], line=dict(color="white", width=1.5)),
                hovertemplate=f"<b>%{{x}}</b><br>{label}: %{{y:.1f}}<extra></extra>",
            ))

    fig_etaria.update_layout(
        title=dict(text="Nota média por faixa etária e área do conhecimento", x=0.5, xanchor="center", font=dict(size=15)),
        xaxis=dict(
            title="Faixa etária", tickangle=45, tickfont=dict(size=10),
            categoryorder="array", categoryarray=[f for f in FAIXA_ORDER if f in faixas_validas],
        ),
        yaxis=dict(title="Nota média", range=[400, 800], tickfont=dict(size=11)),
        legend=dict(title="Área", orientation="h", y=-0.42, x=0.5, xanchor="center"),
        hovermode="x unified",
        margin=dict(t=60, b=160, l=60, r=20),
        height=480,
    )
    st.plotly_chart(fig_etaria, use_container_width=True)

    # --- Gráficos individuais por área do conhecimento ---
    _faixas_validas_ordered = [f for f in FAIXA_ORDER if f in faixas_validas]
    _areas_list = list(NOTAS_PROVAS.items())

    def _make_area_etaria_fig(col, label, cor, medias_df, faixas_ordered):
        media_geral_area = medias_df[col].mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=medias_df["FAIXA_ETARIA_LABEL"].astype(str).tolist(),
            y=medias_df[col].round(1).tolist(),
            mode="lines+markers",
            name=label,
            line=dict(color=cor, width=2),
            marker=dict(size=7, color=cor, line=dict(color="white", width=1.5)),
            hovertemplate="<b>%{x}</b><br>Nota média: %{y:.1f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=faixas_ordered,
            y=[round(media_geral_area, 1)] * len(faixas_ordered),
            mode="lines",
            name="Média geral",
            line=dict(color=cor, width=1.5, dash="dash"),
            opacity=0.55,
            hovertemplate=f"Média geral {label}: %{{y:.1f}}<extra></extra>",
        ))
        fig.update_layout(
            title=dict(text=label, x=0.5, xanchor="center", font=dict(size=13)),
            xaxis=dict(
                title=None, tickangle=45, tickfont=dict(size=9),
                categoryorder="array", categoryarray=faixas_ordered,
            ),
            yaxis=dict(title="Nota média", tickfont=dict(size=10)),
            legend=dict(orientation="h", y=-0.55, x=0.5, xanchor="center", font=dict(size=10)),
            hovermode="x unified",
            margin=dict(t=50, b=130, l=55, r=15),
            height=380,
        )
        return fig

    # Linha 1: 3 gráficos
    _cols_row1 = st.columns(3, gap="medium")
    for i, (col, label) in enumerate(_areas_list[:3]):
        with _cols_row1[i]:
            st.plotly_chart(
                _make_area_etaria_fig(col, label, CORES_AREAS[label], medias_etaria, _faixas_validas_ordered),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    # Linha 2: 2 gráficos centralizados
    _, _col_l2_a, _col_l2_b, _ = st.columns([0.5, 3, 3, 0.5], gap="medium")
    for i, col_ctx in enumerate([(_col_l2_a, 3), (_col_l2_b, 4)]):
        col_widget, idx = col_ctx
        col, label = _areas_list[idx]
        with col_widget:
            st.plotly_chart(
                _make_area_etaria_fig(col, label, CORES_AREAS[label], medias_etaria, _faixas_validas_ordered),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    # --- Seção 3: Desempenho por Renda e Tipo de Escola ---
    st.divider()
    st.subheader(":material/attach_money: Desempenho e participação por renda familiar e tipo de escola")
    if anos_sel == _TODOS:
        _sm_nota = "  \n".join(f"- {ano}: R$ {sm:,}".replace(",", ".") for ano, sm in SM_POR_ANO.items())
        _sm_caption = f"As faixas de renda são expressas em salários mínimos (SM), cujos valores vigentes foram:\n{_sm_nota}"
    else:
        _sm_valor = SM_POR_ANO.get(anos_sel, "")
        _sm_caption = f"As faixas de renda são expressas em salários mínimos (SM), cujo valor em {anos_sel} era de R$ {_sm_valor:,}.".replace(",", ".")
    st.caption(
        "À esquerda, nota média por faixa de renda comparando escolas públicas e privadas — "
        "evidencia se a diferença de desempenho entre as redes persiste em todas as faixas de renda. "
        "À direita, composição percentual dos participantes de cada rede por faixa de renda. "
        f"{_sm_caption}"
    )

    agg_df = (
        desempenho_df
        .group_by("FAIXA_RENDA_SM", "TP_ESCOLA_LABEL")
        .agg(pl.col("MEDIA_GERAL").drop_nulls().mean().alias("media_nota"))
        .sort("FAIXA_RENDA_SM")
        .to_pandas()
    )

    if agg_df.empty:
        st.warning("Nenhum dado disponível para a combinação de filtros selecionada.")
    else:
        agg_df["FAIXA_RENDA_SM"] = pd.Categorical(agg_df["FAIXA_RENDA_SM"], categories=ORDEM_SM, ordered=True)
        agg_df = agg_df.sort_values("FAIXA_RENDA_SM")

        fig = go.Figure()
        _media_geral_global = agg_df["media_nota"].mean()
        for escola, cor in [("Pública", COR_PUBLICA), ("Privada", COR_PRIVADA)]:
            subset = agg_df[agg_df["TP_ESCOLA_LABEL"] == escola]
            if subset.empty:
                st.warning(f"Sem dados para escola {escola} com os filtros atuais.")
                continue
            fig.add_trace(go.Scatter(
                x=subset["FAIXA_RENDA_SM"].astype(str).tolist(),
                y=subset["media_nota"].round(1).tolist(),
                mode="lines+markers", name=escola,
                line=dict(color=cor, width=2),
                marker=dict(size=9, color=cor, line=dict(color="white", width=2)),
                hovertemplate=(
                    f"<b>{escola}</b><br>"
                    "Faixa de renda: %{x}<br>"
                    "Nota média geral: %{y:.1f}<extra></extra>"
                ),
            ))

        fig.add_trace(go.Scatter(
            x=ORDEM_SM,
            y=[round(_media_geral_global, 1)] * len(ORDEM_SM),
            mode="lines",
            name="Média geral",
            line=dict(color=COR_NEUTRO, width=1.5, dash="dash"),
            hovertemplate=f"Média geral: {_media_geral_global:.1f}<extra></extra>",
        ))

        fig.update_layout(
            title=dict(
                text=f"Nota média por faixa de renda e tipo de escola",
                x=0.5, xanchor="center", font=dict(size=15),
            ),
            xaxis=dict(
                title="Faixa de renda familiar",
                categoryorder="array", categoryarray=ORDEM_SM, tickfont=dict(size=11),
            ),
            yaxis=dict(title="Nota média", tickfont=dict(size=11)),
            legend=dict(title="Tipo de escola", orientation="h", y=-0.30, x=0.5, xanchor="center"),
            hovermode="x unified",
            margin=dict(t=60, b=120, l=60, r=20),
            height=420,
        )

        dist_df = (
            desempenho_df
            .group_by("FAIXA_RENDA_SM", "TP_ESCOLA_LABEL")
            .agg(pl.len().alias("n"))
            .sort("FAIXA_RENDA_SM")
            .to_pandas()
        )

        if not dist_df.empty:
            dist_df["FAIXA_RENDA_SM"] = pd.Categorical(dist_df["FAIXA_RENDA_SM"], categories=ORDEM_SM, ordered=True)
            dist_df = dist_df.sort_values("FAIXA_RENDA_SM")

            total_por_faixa   = dist_df.groupby("FAIXA_RENDA_SM", observed=True)["n"].transform("sum")
            dist_df["pct"]    = dist_df["n"] / total_por_faixa * 100

            fig_dist = go.Figure()
            for escola, cor, rank in [("Pública", COR_PUBLICA, 1), ("Privada", COR_PRIVADA, 2)]:
                subset = dist_df[dist_df["TP_ESCOLA_LABEL"] == escola].copy()
                fig_dist.add_trace(go.Bar(
                    x=subset["FAIXA_RENDA_SM"].astype(str).tolist(),
                    y=subset["pct"].round(1).tolist(),
                    name=escola, marker_color=cor,
                    legendrank=rank,
                    text=subset["pct"].round(1).tolist(),
                    texttemplate="%{text:.1f}%", textposition="inside", insidetextanchor="middle",
                    customdata=list(zip(
                        subset["FAIXA_RENDA_SM"].astype(str).tolist(),
                        subset["n"].tolist(),
                    )),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        f"Tipo de escola: {escola}<br>"
                        "Percentual: %{y:.1f}%<br>"
                        "Participantes: %{customdata[1]:,}<extra></extra>"
                    ),
                ))

            fig_dist.update_layout(
                barmode="stack",
                title=dict(
                    text="Distribuição de participantes por faixa de renda e tipo de escola",
                    x=0.5, xanchor="center", font=dict(size=15),
                ),
                xaxis=dict(
                    title="Faixa de renda familiar",
                    categoryorder="array", categoryarray=ORDEM_SM, tickfont=dict(size=11),
                ),
                yaxis=dict(title="Participantes (%)", ticksuffix="%", range=[0, 100], tickfont=dict(size=11)),
                legend=dict(title="Tipo de escola", orientation="h", y=-0.30, x=0.5, xanchor="center", traceorder="normal"),
                margin=dict(t=60, b=120, l=60, r=20),
                height=420,
            )

            _col_nota_renda, _col_dist_renda = st.columns(2, gap="medium")
            with _col_nota_renda:
                st.plotly_chart(fig, use_container_width=True)
            with _col_dist_renda:
                st.plotly_chart(fig_dist, use_container_width=True)

    # --- Seção 4: Proporção acima dos cortes de desempenho ---
    st.divider()
    st.subheader(":material/filter_alt: Proporção de participantes acima dos cortes de desempenho")
    st.caption(
        "Percentual de participantes de cada grupo que obteve nota acima dos cortes indicados (600, 700, 800, 900). "
        "Cortes mais altos representam níveis de exigência maiores, típicos de cursos mais competitivos. "
        "Use os seletores abaixo para explorar diferentes grupos demográficos e áreas do conhecimento."
    )

    _CORTES = [600, 700, 800, 900]

    _GRUPOS = {
        "Tipo de escola":  "TP_ESCOLA_LABEL",
        "Faixa de renda":  "FAIXA_RENDA_SM",
        "Cor/Raça":        "RACA_LABEL",
        "Sexo":            "SEXO_LABEL",
    }

    _NOTAS_HEATMAP = {
        "Nota Geral":            "MEDIA_GERAL",
        "Matemática":            "NU_NOTA_MT",
        "Ciências da Natureza":  "NU_NOTA_CN",
        "Ciências Humanas":      "NU_NOTA_CH",
        "Linguagens e Códigos":  "NU_NOTA_LC",
        "Redação":               "NU_NOTA_REDACAO",
    }

    col_grupo_sel, col_nota_sel = st.columns(2)
    with col_grupo_sel:
        _grupo_sel = st.selectbox("Grupo demográfico", options=list(_GRUPOS.keys()), key="heatmap_grupo")
    with col_nota_sel:
        _nota_sel  = st.selectbox("Área da nota", options=list(_NOTAS_HEATMAP.keys()), key="heatmap_nota")

    _col_grupo = _GRUPOS[_grupo_sel]
    _col_nota  = _NOTAS_HEATMAP[_nota_sel]

    _hm_base = (
        enem_participantes
        .with_columns([
            pl.col("TP_SEXO")
              .replace({"M": "Masculino", "F": "Feminino"}).cast(pl.String)
              .alias("SEXO_LABEL"),
            pl.col("TP_COR_RACA").cast(pl.String)
              .replace({str(k): v for k, v in RACA_MAP.items()}).cast(pl.String)
              .alias("RACA_LABEL"),
            pl.col("TP_ESCOLA").cast(pl.String)
              .replace({"1": "Não Respondeu", "2": "Pública", "3": "Privada"}).cast(pl.String)
              .alias("TP_ESCOLA_LABEL"),
            pl.col("Q006")
              .replace(MAPA_RENDA_SM).cast(pl.String)
              .alias("FAIXA_RENDA_SM"),
            pl.mean_horizontal(NOTAS_COLS).alias("MEDIA_GERAL"),
        ])
        .filter(pl.col(_col_grupo).is_not_null())
        .filter(pl.col(_col_nota).is_not_null())
    )

    _ORDEM_GRUPOS = {
        "TP_ESCOLA_LABEL": ["Pública", "Privada"],
        "FAIXA_RENDA_SM":  ORDEM_SM,
        "RACA_LABEL":      ["Branca", "Parda", "Preta", "Amarela", "Indígena", "Não declarado", "Não dispõe da informação"],
        "SEXO_LABEL":      ["Feminino", "Masculino"],
    }
    _ordem_y = [g for g in _ORDEM_GRUPOS[_col_grupo] if g in _hm_base[_col_grupo].unique().to_list()]

    _hm_rows = []
    for _grupo_val in _ordem_y:
        _sub = _hm_base.filter(pl.col(_col_grupo) == _grupo_val)
        _total = _sub.height
        if _total == 0:
            continue
        for _corte in _CORTES:
            _acima = _sub.filter(pl.col(_col_nota) > _corte).height
            _pct   = round(_acima / _total * 100, 1)
            _hm_rows.append({
                "grupo": _grupo_val,
                "corte": f"> {_corte}",
                "pct":   _pct,
                "total": _total,
                "acima": _acima,
            })

    _hm_df = pd.DataFrame(_hm_rows)

    if _hm_df.empty:
        st.warning("Nenhum dado disponível para a combinação de filtros selecionada.")
    else:
        _hm_pivot = _hm_df.pivot(index="grupo", columns="corte", values="pct")
        _corte_cols = [f"> {c}" for c in _CORTES]
        _hm_pivot   = _hm_pivot.reindex(columns=_corte_cols)
        _hm_pivot   = _hm_pivot.reindex([g for g in _ordem_y if g in _hm_pivot.index])

        _hm_total = _hm_df.pivot(index="grupo", columns="corte", values="total").reindex(
            index=_hm_pivot.index, columns=_corte_cols
        )
        _hm_acima = _hm_df.pivot(index="grupo", columns="corte", values="acima").reindex(
            index=_hm_pivot.index, columns=_corte_cols
        )
        _custom = np.stack([_hm_total.values, _hm_acima.values], axis=-1)

        _COLORSCALE = [
            [0.0, "#cde2fb"], [0.2, "#9ec5f4"], [0.4, "#6da7ec"],
            [0.6, "#3987e5"], [0.8, "#256abf"], [1.0, "#104281"],
        ]

        fig_hm = go.Figure(go.Heatmap(
            z=_hm_pivot.values,
            x=_corte_cols,
            y=_hm_pivot.index.tolist(),
            colorscale=_COLORSCALE,
            zmin=0, zmax=100,
            customdata=_custom,
            texttemplate="%{text}",
            textfont=dict(size=12, color="white"),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Corte: %{x}<br>"
                "Total no grupo: %{customdata[0]:,}<br>"
                "Acima do corte: %{customdata[1]:,}<br>"
                "Percentual: %{z:.1f}%"
                "<extra></extra>"
            ),
            colorbar=dict(
                title=dict(text="%", font=dict(size=12)),
                ticksuffix="%", thickness=14, len=0.8,
            ),
            xgap=2, ygap=2,
        ))

        fig_hm.update_layout(
            title=dict(
                text=f"Proporção acima do corte — <b>{_nota_sel}</b> por <b>{_grupo_sel}</b>",
                x=0.5, xanchor="center", font=dict(size=15),
            ),
            xaxis=dict(title="Corte de nota", tickfont=dict(size=12), side="bottom"),
            yaxis=dict(title=None, tickfont=dict(size=12), autorange="reversed"),
            margin=dict(t=60, b=60, l=180, r=40),
            height=max(280, 60 + len(_ordem_y) * 52),
        )

        fig_hm.update_traces(texttemplate=None)
        fig_hm.update_layout(annotations=_heatmap_annotations(_hm_pivot, _corte_cols))
        st.plotly_chart(fig_hm, use_container_width=True)

        st.caption(
            "Passe o cursor sobre uma célula para ver o total de participantes do grupo e a quantidade acima do corte. "
            "Tons de azul mais escuros representam proporções maiores."
        )


# ============================================================
# ABA 4 — AUSÊNCIAS
# ============================================================

with tab_ausencia:
    st.subheader(":material/event_busy: Distribuição de ausências por dia de prova")
    st.caption(
        "O 1º dia de provas contempla Linguagens e Ciências Humanas; o 2º dia, Ciências da Natureza e Matemática. "
        "A análise classifica cada inscrito em uma das quatro situações possíveis e identifica "
        "em qual dia ocorre maior evasão e quantos candidatos abandonam o exame após o primeiro dia."
    )

    # Classifica cada inscrito em uma das quatro situações
    _DIA1_COLS = ["TP_PRESENCA_LC", "TP_PRESENCA_CH"]
    _DIA2_COLS = ["TP_PRESENCA_CN", "TP_PRESENCA_MT"]

    _ausencia_base = enem_df.with_columns([
        pl.all_horizontal([pl.col(c) == 1 for c in _DIA1_COLS]).alias("_presente_d1"),
        pl.all_horizontal([pl.col(c) == 1 for c in _DIA2_COLS]).alias("_presente_d2"),
    ]).with_columns(
        pl.when(pl.col("_presente_d1") & pl.col("_presente_d2"))
          .then(pl.lit("Presente nos dois dias"))
          .when(~pl.col("_presente_d1") & ~pl.col("_presente_d2"))
          .then(pl.lit("Ausente nos dois dias"))
          .when(~pl.col("_presente_d1") & pl.col("_presente_d2"))
          .then(pl.lit("Ausente no 1º dia"))
          .otherwise(pl.lit("Ausente no 2º dia"))
          .alias("situacao")
    )

    _situacao_counts = (
        _ausencia_base
        .group_by("situacao")
        .agg(pl.len().alias("n"))
        .to_pandas()
    )

    _total_inscritos = _situacao_counts["n"].sum()
    _situacao_counts["pct"] = (_situacao_counts["n"] / _total_inscritos * 100).round(1)

    _ORDEM_SITUACAO = [
        "Presente nos dois dias",
        "Ausente no 2º dia",
        "Ausente nos dois dias",
        "Ausente no 1º dia",
    ]
    _situacao_counts["situacao"] = (
        _situacao_counts["situacao"]
        .astype("category")
        .cat.set_categories(
            [s for s in _ORDEM_SITUACAO if s in _situacao_counts["situacao"].values],
            ordered=True,
        )
    )
    _situacao_counts = _situacao_counts.sort_values("n", ascending=False).reset_index(drop=True)

    _CORES_SITUACAO = {
        "Presente nos dois dias": "#2E9E6B",
        "Ausente no 1º dia":      "#D95F5F",
        "Ausente no 2º dia":      "#D95F5F",
        "Ausente nos dois dias":  "#D95F5F",
    }

    fig_aus = go.Figure()
    for _, row in _situacao_counts.iterrows():
        sit  = row["situacao"]
        cor  = _CORES_SITUACAO.get(sit, "#94A3B8")
        fig_aus.add_trace(go.Bar(
            y=[sit],
            x=[row["n"]],
            name=sit,
            orientation="h",
            marker_color=cor,
            text=f"<b>{row['n']:,}</b>  {row['pct']:.1f}%",
            textposition="outside",
            textfont=dict(size=12),
            hovertemplate=(
                f"<b>{sit}</b><br>"
                f"Participantes: {row['n']:,}<br>"
                f"Percentual: {row['pct']:.1f}%"
                "<extra></extra>"
            ),
        ))

    fig_aus.update_layout(
        title=dict(
            text=(
                "Distribuição de ausências dos participantes"
            ),
            x=0.5, xanchor="center", font=dict(size=15),
        ),
        yaxis=dict(title=None, tickfont=dict(size=12), categoryorder="total ascending"),
        xaxis=dict(title="Quantidade de participantes", tickfont=dict(size=11)),
        showlegend=False,
        margin=dict(t=80, b=40, l=180, r=120),
        height=320,
    )

    st.plotly_chart(fig_aus, use_container_width=True)
    st.caption(
        "Valores sobre cada barra indicam a quantidade absoluta e o percentual em relação ao total de inscritos. "
        "A diferença entre ausentes no 1º e no 2º dia revela quantos candidatos desistiram após a primeira jornada."
    )

    # --- Seção: Perfil dos Faltosos ---
    st.divider()
    st.subheader(":material/person_search: Perfil dos candidatos com maior propensão à ausência")
    st.caption(
        "Taxa de falta (faltosos / inscritos × 100) segmentada por faixa etária, raça/cor e renda familiar. "
        "Permite identificar quais perfis têm maior propensão à ausência e se esse padrão varia entre os dias de prova. "
        "Selecione o período para considerar ausência no 1º dia, no 2º dia ou em ambos."
    )

    _periodo_sel = st.radio(
        "Período de ausência",
        options=["Dia 1", "Dia 2", "Ambos os dias"],
        horizontal=True,
        key="abs_periodo",
    )

    if _periodo_sel == "Dia 1":
        _faltou_expr = ~pl.all_horizontal([pl.col(c) == 1 for c in _DIA1_COLS])
    elif _periodo_sel == "Dia 2":
        _faltou_expr = ~pl.all_horizontal([pl.col(c) == 1 for c in _DIA2_COLS])
    else:
        _faltou_expr = (
            ~pl.all_horizontal([pl.col(c) == 1 for c in _DIA1_COLS]) &
            ~pl.all_horizontal([pl.col(c) == 1 for c in _DIA2_COLS])
        )

    # Calcula x_max global para manter eixo fixo entre os 3 períodos
    _EXPRS_PERIODOS = {
        "Dia 1":        ~pl.all_horizontal([pl.col(c) == 1 for c in _DIA1_COLS]),
        "Dia 2":        ~pl.all_horizontal([pl.col(c) == 1 for c in _DIA2_COLS]),
        "Ambos os dias": (
            ~pl.all_horizontal([pl.col(c) == 1 for c in _DIA1_COLS]) &
            ~pl.all_horizontal([pl.col(c) == 1 for c in _DIA2_COLS])
        ),
    }
    _RACAS_VALIDAS = ["Branca", "Parda", "Preta", "Amarela", "Indígena"]
    _x_max_global = 0.0
    for _expr in _EXPRS_PERIODOS.values():
        _tmp = enem_df.with_columns([
            pl.col("TP_FAIXA_ETARIA").cast(pl.String)
              .replace({str(k): v for k, v in FAIXA_ETARIA_AGRUPADA.items()})
              .alias("FAIXA_ETARIA_G"),
            pl.col("TP_COR_RACA").cast(pl.String)
              .replace({str(k): v for k, v in RACA_MAP.items()})
              .alias("RACA"),
            pl.col("Q006")
              .replace(MAPA_RENDA_SM).cast(pl.String)
              .alias("RENDA"),
            _expr.alias("FALTOU"),
        ])
        _tmp_tot = _tmp.filter(pl.col("FALTOU")).height
        if _tmp_tot == 0:
            continue
        for _col, _filtro in [
            ("FAIXA_ETARIA_G", pl.col("FAIXA_ETARIA_G").is_in(ORDEM_FAIXA_AGRUPADA)),
            ("RACA",            pl.col("RACA").is_in(_RACAS_VALIDAS)),
            ("RENDA",           pl.col("RENDA").is_in(ORDEM_SM)),
        ]:
            _t = (
                _tmp.filter(_filtro)
                .group_by(_col)
                .agg([pl.len().alias("inscritos"), pl.col("FALTOU").sum().alias("faltosos")])
                .with_columns((pl.col("faltosos") / pl.col("inscritos") * 100).alias("taxa"))
                .select(pl.col("taxa").max())
                .item()
            )
            if _t and _t > _x_max_global:
                _x_max_global = _t

    _abs_base = enem_df.with_columns([
        pl.col("TP_FAIXA_ETARIA").cast(pl.String)
          .replace({str(k): v for k, v in FAIXA_ETARIA_AGRUPADA.items()})
          .alias("FAIXA_ETARIA_G"),
        pl.col("TP_COR_RACA").cast(pl.String)
          .replace({str(k): v for k, v in RACA_MAP.items()})
          .alias("RACA"),
        pl.col("Q006")
          .replace(MAPA_RENDA_SM).cast(pl.String)
          .alias("RENDA"),
        _faltou_expr.alias("FALTOU"),
    ])

    _total_faltosos = _abs_base.filter(pl.col("FALTOU")).height

    def _make_abs_bar(df, grupo_col, ordem=None, sort_by_taxa=True):
        _grp = (
            df.group_by(grupo_col)
            .agg([
                pl.len().alias("inscritos"),
                pl.col("FALTOU").sum().alias("faltosos"),
            ])
            .with_columns([
                (pl.col("faltosos") / pl.col("inscritos") * 100).round(1).alias("taxa"),
                (pl.col("faltosos") / (_total_faltosos or 1) * 100).round(1).alias("pct_faltosos"),
            ])
            .to_pandas()
        )
        if ordem:
            _grp = _grp[_grp[grupo_col].isin(ordem)].copy()
            _grp[grupo_col] = pd.Categorical(_grp[grupo_col], categories=ordem, ordered=True)
            if sort_by_taxa:
                _grp = _grp.sort_values("taxa", ascending=True)
            else:
                _grp = _grp.sort_values(grupo_col, ascending=True)
        else:
            _grp = _grp.sort_values("taxa", ascending=True)
        return _grp

    def _plot_abs_bar(df_grp, grupo_col, title, x_max=None):
        _max_taxa = df_grp["taxa"].max() if not df_grp.empty else 100
        _norm = df_grp["taxa"] / (_max_taxa if _max_taxa > 0 else 1)

        colors = [_interp_color(v) for v in _norm]
        _x_range = [0, (x_max if x_max else _max_taxa) / 0.70]

        fig = go.Figure(go.Bar(
            x=df_grp["taxa"],
            y=df_grp[grupo_col].astype(str),
            orientation="h",
            marker_color=colors,
            customdata=df_grp[["inscritos", "faltosos", "taxa", "pct_faltosos"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Inscritos: %{customdata[0]:,}<br>"
                "Faltosos: %{customdata[1]:,}<br>"
                "Taxa de falta: %{customdata[2]:.1f}%<br>"
                "% do total de faltosos: %{customdata[3]:.1f}%"
                "<extra></extra>"
            ),
        ))
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor="center", font=dict(size=14)),
            xaxis=dict(title="Taxa de falta (%)", tickfont=dict(size=10), ticksuffix="%", range=_x_range),
            yaxis=dict(title=None, tickfont=dict(size=11)),
            showlegend=False,
            margin=dict(t=50, b=40, l=140, r=10),
            height=CHART_HEIGHT,
            bargap=0.3,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(showgrid=True, gridcolor="#eeeeee")
        fig.update_yaxes(showgrid=False)
        return fig

    # Gráfico 1 — Faixa Etária
    _abs_etaria = _make_abs_bar(
        _abs_base.filter(pl.col("FAIXA_ETARIA_G").is_in(ORDEM_FAIXA_AGRUPADA)),
        "FAIXA_ETARIA_G",
        ordem=ORDEM_FAIXA_AGRUPADA,
        sort_by_taxa=False,
    )

    # Gráfico 2 — Raça/Cor
    _abs_raca = _make_abs_bar(
        _abs_base.filter(pl.col("RACA").is_in(_RACAS_VALIDAS)),
        "RACA",
    )

    # Gráfico 3 — Renda
    _abs_renda = _make_abs_bar(
        _abs_base.filter(pl.col("RENDA").is_in(ORDEM_SM)),
        "RENDA",
        ordem=ORDEM_SM,
    )

    _col_abs1, _col_abs2, _col_abs3 = st.columns(3, gap="small")
    with _col_abs1:
        st.plotly_chart(
            _plot_abs_bar(_abs_etaria, "FAIXA_ETARIA_G", "Taxa de falta por faixa etária", x_max=_x_max_global),
            use_container_width=True, config={"displayModeBar": False},
        )
    with _col_abs2:
        st.plotly_chart(
            _plot_abs_bar(_abs_raca, "RACA", "Taxa de falta por raça/cor", x_max=_x_max_global),
            use_container_width=True, config={"displayModeBar": False},
        )
    with _col_abs3:
        st.plotly_chart(
            _plot_abs_bar(_abs_renda, "RENDA", "Taxa de falta por faixa de renda", x_max=_x_max_global),
            use_container_width=True, config={"displayModeBar": False},
        )

