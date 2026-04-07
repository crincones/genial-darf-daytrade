"""
Calculadora de DARF - Notas de Corretagem
Desenvolvido para operações de Day Trade no mercado futuro (WIN, WDO, etc.)
Corretora: Genial CCTVM

Legislação aplicável:
- Day Trade: alíquota de 20% sobre o lucro líquido (IN RFB 1.585/2015)
- IRRF retido na fonte: 1% sobre o lucro do day trade (dedutível da DARF)
- DARF vence no último dia útil do mês seguinte ao das operações
- Não há compensação de prejuízos entre meses diferentes para cálculo da DARF
  (mas prejuízos acumulados podem compensar lucros futuros - implementação simplificada)
"""

import streamlit as st
import pdfplumber
import pandas as pd
import re
import io
import calendar
from datetime import date, timedelta
import plotly.graph_objects as go
from collections import defaultdict

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Calculadora DARF · Day Trade",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Sora:wght@300;400;600;700&display=swap');

:root {
    --bg: #0d1117;
    --surface: #161b22;
    --surface2: #1c2128;
    --border: #30363d;
    --accent: #58a6ff;
    --accent2: #3fb950;
    --danger: #f85149;
    --warning: #d29922;
    --text: #e6edf3;
    --muted: #8b949e;
    --mono: 'JetBrains Mono', monospace;
    --sans: 'Sora', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--sans) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background-color: var(--bg) !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 16px !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #0d1117 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--sans) !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #79c0ff !important;
    transform: translateY(-1px) !important;
}

/* Download button */
.stDownloadButton > button {
    background: var(--surface2) !important;
    color: var(--accent2) !important;
    border: 1px solid var(--accent2) !important;
    border-radius: 8px !important;
    font-family: var(--sans) !important;
    font-weight: 600 !important;
}

/* Progress bar */
.stProgress > div > div { background-color: var(--accent) !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden; }

/* Alert boxes */
.alert-warning {
    background: rgba(210, 153, 34, 0.12) !important;
    border: 1px solid var(--warning) !important;
    border-radius: 10px !important;
    padding: 16px 20px !important;
    margin: 16px 0 !important;
    font-size: 0.9rem;
}
.alert-danger {
    background: rgba(248, 81, 73, 0.12) !important;
    border: 1px solid var(--danger) !important;
    border-radius: 10px !important;
    padding: 16px 20px !important;
    margin: 16px 0 !important;
    font-size: 0.9rem;
}
.alert-info {
    background: rgba(88, 166, 255, 0.10) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 10px !important;
    padding: 16px 20px !important;
    margin: 16px 0 !important;
    font-size: 0.9rem;
}

/* Note card */
.note-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 18px;
    margin: 8px 0;
    font-family: var(--mono);
    font-size: 0.82rem;
}
.note-card .nota-header { color: var(--accent); font-weight: 700; margin-bottom: 6px; }
.note-card .lucro { color: var(--accent2); }
.note-card .prejuizo { color: var(--danger); }

/* Tag pills */
.pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 2px;
}
.pill-green { background: rgba(63,185,80,0.2); color: var(--accent2); border: 1px solid var(--accent2); }
.pill-red   { background: rgba(248,81,73,0.2); color: var(--danger);  border: 1px solid var(--danger); }
.pill-blue  { background: rgba(88,166,255,0.2); color: var(--accent); border: 1px solid var(--accent); }

h1, h2, h3 { font-family: var(--sans) !important; }
h1 { font-size: 1.8rem !important; font-weight: 700 !important; }
h2 { font-size: 1.2rem !important; font-weight: 600 !important; color: var(--muted) !important; }

.divider { border-top: 1px solid var(--border); margin: 24px 0; }

/* Expander */
details { 
    background: var(--surface2) !important; 
    border: 1px solid var(--border) !important; 
    border-radius: 10px !important; 
    padding: 4px 12px !important;
    margin: 8px 0 !important;
}

/* Selectbox / inputs */
.stSelectbox > div > div, .stTextInput > div > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Constants ─────────────────────────────────────────────────────────────────
ALIQUOTA_DAYTRADE = 0.20   # 20% sobre lucro day trade
IRRF_SOURCE_RATE  = 0.01   # 1% retido na fonte (dedo-duro)
DARF_MINIMA       = 10.00  # DARF mínima R$ 10,00


# ── Utility: last business day of a month ─────────────────────────────────────
def ultimo_dia_util(ano: int, mes: int) -> date:
    """Returns the last business day (Mon-Fri) of the given year/month."""
    ultimo = calendar.monthrange(ano, mes)[1]
    d = date(ano, mes, ultimo)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def vencimento_darf(ano_ref: int, mes_ref: int) -> date:
    """DARF vence no último dia útil do mês SEGUINTE às operações."""
    if mes_ref == 12:
        return ultimo_dia_util(ano_ref + 1, 1)
    return ultimo_dia_util(ano_ref, mes_ref + 1)


# ── PDF Parsing ───────────────────────────────────────────────────────────────
def parse_valor(texto: str) -> float:
    """Convert Brazilian number string like '1.234,56' to float."""
    texto = texto.strip().replace('.', '').replace(',', '.')
    try:
        return float(texto)
    except ValueError:
        return 0.0


def extrair_notas_pdf(pdf_bytes: bytes) -> tuple[list[dict], list[dict]]:
    """
    Extract unique brokerage notes from a PDF file (Genial CCTVM format).

    Returns a tuple:
      - list of successfully extracted notes
      - list of failure dicts: {page, nr_nota, arquivo, problema}

    Supports multi-page notes: when a note spans 2+ pages, page 1 shows
    "CONTINUA" instead of totals. Page 2+ repeats the header with Folha=2,3...
    and contains the final totals. Data is merged across pages by nr_nota.
    """
    notes_by_id: dict[str, dict] = {}

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

            if not any("NOTA DE CORRETAGEM" in ln for ln in lines):
                continue

            nr_nota     = None
            folha       = None
            data_pregao = None
            total_liq   = None
            total_dc    = None
            irrf_dt     = 0.0

            for i, line in enumerate(lines):
                # ── Nota number + folha + date ──────────────────────────────
                if re.match(r'Nr\.\s*nota\s+Folha\s+Data\s+preg', line, re.I):
                    if i + 1 < len(lines):
                        m = re.match(r'(\d{1,7})\s+(\d+)\s+(\d{2}/\d{2}/\d{4})', lines[i + 1])
                        if m:
                            nr_nota     = m.group(1)
                            folha       = int(m.group(2))
                            data_pregao = m.group(3)

                # ── IRRF Day Trade (Projeção) ────────────────────────────────
                if re.match(r'IRRF\s+IRRF\s+Day\s+Trade', line, re.I):
                    if i + 1 < len(lines):
                        vals = lines[i + 1].split()
                        if len(vals) >= 2:
                            irrf_dt = parse_valor(vals[1])

                # ── Total líquido da nota ────────────────────────────────────
                if re.search(r'Total\s+l[ií]quido\s+da\s+nota', line, re.I):
                    if i + 1 < len(lines):
                        val_line = lines[i + 1]
                        # "CONTINUA" means this page has no totals — skip silently
                        if re.search(r'CONTINUA', val_line, re.I):
                            pass
                        else:
                            matches = re.findall(r'([\d\.]+,\d+)\s*([DC])', val_line)
                            if matches:
                                val_str, dc = matches[-1]
                                total_liq = parse_valor(val_str)
                                total_dc  = dc.upper()

            if nr_nota is None:
                # Can't even identify which note this page belongs to
                continue  # silent skip — not a parseable nota page

            # ── Merge into notes_by_id ───────────────────────────────────────
            if nr_nota not in notes_by_id:
                notes_by_id[nr_nota] = {
                    "nr_nota":     nr_nota,
                    "data_pregao": data_pregao,
                    "total_liq":   total_liq,
                    "total_dc":    total_dc,
                    "irrf_dt":     irrf_dt,
                    "page":        page_num + 1,
                }
            else:
                existing = notes_by_id[nr_nota]
                # Later pages (folha 2+) fill in whatever is still missing
                if existing["total_liq"] is None and total_liq is not None:
                    existing["total_liq"] = total_liq
                    existing["total_dc"]  = total_dc
                if existing["irrf_dt"] == 0.0 and irrf_dt > 0:
                    existing["irrf_dt"] = irrf_dt
                if existing["data_pregao"] is None and data_pregao:
                    existing["data_pregao"] = data_pregao

    # ── Post-processing: detect truly incomplete notes ───────────────────────
    failed_pages = []
    complete_notes = []
    for nr, nota in notes_by_id.items():
        missing = []
        if nota["data_pregao"] is None:
            missing.append("data de pregão não encontrada")
        if nota["total_liq"] is None:
            missing.append("total líquido não encontrado")
        if missing:
            failed_pages.append({
                "page":     nota["page"],
                "nr_nota":  nr,
                "problema": "; ".join(missing),
            })
        else:
            complete_notes.append(nota)

    return complete_notes, failed_pages

def resultado_financeiro(total_liq: float, total_dc: str) -> float:
    if total_dc == "C":
        return total_liq
    elif total_dc == "D":
        return -total_liq
    return 0.0


# ── DARF Calculation ──────────────────────────────────────────────────────────
def calcular_darf_mensal(notas: list[dict]) -> list[dict]:
    """
    Group notes by month and calculate DARF for day trade operations.
    """
    by_month: dict[str, dict] = defaultdict(lambda: {
        "notas": [], "lucro_bruto": 0.0, "irrf_total": 0.0,
        "ano": None, "mes": None
    })

    for nota in notas:
        dp = nota.get("data_pregao")
        if not dp:
            continue
        try:
            dia, mes, ano = dp.split("/")
            mes, ano = int(mes), int(ano)
        except Exception:
            continue

        chave = f"{ano:04d}-{mes:02d}"
        grp   = by_month[chave]
        grp["ano"] = ano
        grp["mes"] = mes

        resultado = 0.0
        if nota["total_liq"] is not None and nota["total_dc"]:
            resultado = resultado_financeiro(nota["total_liq"], nota["total_dc"])

        grp["lucro_bruto"] += resultado
        grp["irrf_total"]  += nota.get("irrf_dt", 0.0)
        grp["notas"].append(nota)

    resultado_list     = []
    prejuizo_acumulado = 0.0
    darf_abaixo_min    = 0.0

    for chave in sorted(by_month.keys()):
        grp = by_month[chave]
        ano, mes = grp["ano"], grp["mes"]

        lucro_bruto = grp["lucro_bruto"]
        irrf_total  = grp["irrf_total"]

        base_calculo = lucro_bruto + prejuizo_acumulado

        if base_calculo <= 0:
            prejuizo_acumulado = base_calculo
            darf_calc = 0.0
        else:
            prejuizo_acumulado = 0.0
            darf_calc = base_calculo * ALIQUOTA_DAYTRADE

        darf_acum_entrada = darf_abaixo_min
        darf_total = darf_calc + darf_abaixo_min

        irrf_a_deduzir = min(irrf_total, darf_total)
        darf_devida    = max(0.0, darf_total - irrf_a_deduzir)
        darf_bruta     = darf_calc

        obs = ""
        if darf_devida >= DARF_MINIMA:
            darf_pagar      = darf_devida
            darf_abaixo_min = 0.0
        elif darf_devida > 0:
            darf_pagar      = 0.0
            darf_abaixo_min = darf_devida
            obs = (f"DARF R$ {darf_devida:.2f} < mínimo R$ {DARF_MINIMA:.2f} "
                   f"— acumula (inclui R$ {darf_abaixo_min:.2f} de meses anteriores)"
                   if darf_abaixo_min > darf_devida
                   else f"DARF R$ {darf_devida:.2f} < mínimo R$ {DARF_MINIMA:.2f} — acumula pro próximo mês")
        else:
            darf_pagar      = 0.0

        venc      = vencimento_darf(ano, mes)
        notas_mes = grp["notas"]

        resultado_list.append({
            "Mês/Ano":              f"{mes:02d}/{ano}",
            "Nº Notas":             len(notas_mes),
            "Notas":                ", ".join(n["nr_nota"] for n in notas_mes),
            "Resultado Bruto (R$)":  lucro_bruto,
            "Base de Cálculo (R$)":  base_calculo,
            "Alíquota":              f"{ALIQUOTA_DAYTRADE*100:.0f}%",
            "IRRF Retido (R$)":      irrf_total,
            "DARF Bruta (R$)":       darf_bruta,
            "DARF Acum Entrada":     darf_acum_entrada,
            "DARF Total Bruta":      darf_total,
            "DARF Acumulada <mín":   darf_abaixo_min,
            "DARF a Pagar (R$)":     darf_pagar,
            "Vencimento DARF":       venc.strftime("%d/%m/%Y"),
            "Prejuízo Acumulado":    prejuizo_acumulado,
            "Observação":            obs,
            "_ano": ano,
            "_mes": mes,
            "_lucro": lucro_bruto,
        })

    return resultado_list


# ── Streamlit UI ───────────────────────────────────────────────────────────────
def main():
    # ── Header ──
    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        st.markdown("<div style='font-size:2.8rem;margin-top:8px'>📊</div>", unsafe_allow_html=True)
    with col_title:
        st.markdown("<h1>Calculadora DARF · Day Trade</h1>", unsafe_allow_html=True)
        st.markdown("<h2>Notas de Corretagem — Mercado Futuro (WIN / WDO)</h2>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-warning">
    ⚠️ <strong>ATENÇÃO — Leia antes de usar:</strong><br>
    Os arquivos PDF carregados devem corresponder ao <strong>mês completo</strong> de operações.
    Caso alguma nota esteja faltando ou o arquivo seja parcial, o cálculo da DARF será
    <strong>incorreto</strong> e pode gerar inconsistências com a Receita Federal.<br><br>
    Verifique sempre junto à sua corretora se todos os pregões do mês estão incluídos.
    Este sistema é uma ferramenta auxiliar e <strong>não substitui a orientação de um contador</strong>.
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⚙️ Parâmetros Legais")
        st.markdown(f"""
        <div class='note-card'>
        <div class='nota-header'>Day Trade (IN RFB 1.585/2015)</div>
        • Alíquota IRPF: <strong>20%</strong> sobre lucro líquido<br>
        • IRRF (dedo-duro): <strong>1%</strong> — dedutível<br>
        • DARF mínima: <strong>R$ 10,00</strong><br>
        • Vencimento: último dia útil do mês seguinte<br>
        • Prejuízos compensáveis com lucros futuros (mesma modalidade)
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📋 Como usar")
        st.markdown("""
        1. Carregue os PDFs de notas de corretagem (um por mês ou múltiplos)
        2. Aguarde o processamento
        3. Revise os resultados e o gráfico
        4. Baixe o CSV para seu controle
        """)

        st.markdown("---")
        st.markdown(
            "<div style='font-size:0.75rem;color:var(--muted)'>Desenvolvido para uso com Genial CCTVM.<br>"
            "Consulte sempre um contador para validação.</div>",
            unsafe_allow_html=True
        )

    st.markdown("### 📂 Upload das Notas de Corretagem")
    uploaded_files = st.file_uploader(
        "Selecione um ou mais arquivos PDF de notas de corretagem",
        type=["pdf"],
        accept_multiple_files=True,
        help="Carregue os PDFs mensais gerados pela corretora. Podem conter múltiplas notas."
    )

    if not uploaded_files:
        st.markdown("""
        <div class="alert-info">
        💡 Carregue os PDFs das notas de corretagem para iniciar o processamento.
        Múltiplos arquivos são suportados — cada arquivo pode conter várias notas do período.
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("---")
    st.markdown("### ⚙️ Processando Arquivos")

    all_notes = []
    all_failures: list[dict] = []   # NEW: aggregate failures across all files
    progress_bar = st.progress(0)
    status_text  = st.empty()
    detail_log   = st.expander("🔍 Log de processamento", expanded=False)

    log_lines = []

    for i, uploaded_file in enumerate(uploaded_files):
        progress_bar.progress(i / len(uploaded_files))
        status_text.markdown(
            f"<span style='color:var(--accent)'>Processando:</span> **{uploaded_file.name}** "
            f"({i+1}/{len(uploaded_files)})",
            unsafe_allow_html=True
        )

        pdf_bytes = uploaded_file.read()
        # NEW: extrair_notas_pdf now returns (notes, failures)
        notas, failures = extrair_notas_pdf(pdf_bytes)
        all_notes.extend(notas)

        # Tag each failure with the source filename
        for f in failures:
            f["arquivo"] = uploaded_file.name
        all_failures.extend(failures)

        log_lines.append(f"✅ **{uploaded_file.name}** → {len(notas)} nota(s) extraída(s)" +
                         (f", ⚠️ {len(failures)} página(s) com falha" if failures else ""))
        for n in notas:
            sinal = "🟢" if n.get("total_dc") == "C" else "🔴"
            liq_str = f"R$ {n['total_liq']:.2f}" if n['total_liq'] is not None else "R$ ?"
            dc_str  = n['total_dc'] or '?'
            dp_str  = n['data_pregao'] or '?'
            log_lines.append(
                f"   {sinal} Nota {n['nr_nota']} | {dp_str} | "
                f"{liq_str} {dc_str} | "
                f"IRRF: R$ {n['irrf_dt']:.2f}"
            )
        for f in failures:
            log_lines.append(f"   🚨 Página {f['page']}: {f['problema']}")

    progress_bar.progress(1.0)
    status_text.markdown(
        f"<span style='color:var(--accent2)'>✅ Concluído!</span> "
        f"**{len(all_notes)} nota(s)** extraída(s) de **{len(uploaded_files)} arquivo(s)**"
        + (f" · <span style='color:var(--danger)'>⚠️ {len(all_failures)} página(s) com falha</span>"
           if all_failures else ""),
        unsafe_allow_html=True
    )

    with detail_log:
        for line in log_lines:
            st.markdown(line)

    # ── NEW: Explicit alert block for extraction failures ──────────────────
    if all_failures:
        falhas_html = "".join(
            f"<li><strong>{f['arquivo']}</strong> — Página {f['page']} "
            f"(Nota {f['nr_nota']}): {f['problema']}</li>"
            for f in all_failures
        )
        st.markdown(f"""
        <div class="alert-danger">
        🚨 <strong>ATENÇÃO: {len(all_failures)} página(s) não puderam ser lidas corretamente e foram IGNORADAS.</strong><br>
        Isso significa que os dados abaixo podem estar <strong>incompletos</strong> — 
        o cálculo da DARF pode estar errado se as notas abaixo corresponderem a operações reais.<br><br>
        <strong>Páginas com falha:</strong>
        <ul style="margin:8px 0 0 0;padding-left:20px">{falhas_html}</ul>
        <br>
        <strong>Possíveis causas:</strong> PDF com formato diferente do padrão Genial CCTVM, arquivo corrompido, 
        página de rodapé/capa sem nota, ou nota com número de identificação fora do padrão esperado.<br>
        Verifique o arquivo manualmente e, se necessário, contate o suporte da corretora.
        </div>
        """, unsafe_allow_html=True)

    if not all_notes:
        st.error("Nenhuma nota válida encontrada nos PDFs. Verifique se os arquivos são notas de corretagem no formato Genial CCTVM.")
        return

    # ── Remove duplicates across files ──
    seen = set()
    unique_notes = []
    for n in all_notes:
        if n["nr_nota"] not in seen:
            seen.add(n["nr_nota"])
            unique_notes.append(n)

    if len(unique_notes) < len(all_notes):
        st.warning(
            f"⚠️ {len(all_notes) - len(unique_notes)} nota(s) duplicada(s) removida(s) "
            f"(mesma nota presente em múltiplos arquivos)."
        )

    # ── Calculate DARF ──
    resultados = calcular_darf_mensal(unique_notes)

    st.markdown("---")

    # ── Summary Metrics ──
    st.markdown("### 📈 Resumo Geral")

    total_resultado = sum(r["Resultado Bruto (R$)"] for r in resultados)
    total_darf      = sum(r["DARF a Pagar (R$)"] for r in resultados)
    total_irrf      = sum(r["IRRF Retido (R$)"] for r in resultados)
    meses_lucro     = sum(1 for r in resultados if r["Resultado Bruto (R$)"] > 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "Resultado Total",
            f"R$ {total_resultado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
    with c2:
        st.metric(
            "Total DARF a Pagar",
            f"R$ {total_darf:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
    with c3:
        st.metric(
            "Total IRRF Retido",
            f"R$ {total_irrf:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )
    with c4:
        st.metric(
            "Meses com Lucro",
            f"{meses_lucro} / {len(resultados)}"
        )

    # ── Monthly Results Table ──
    st.markdown("---")
    st.markdown("### 📋 Resumo Mensal por DARF")

    for r in resultados:
        lucro        = r["Resultado Bruto (R$)"]
        base         = r["Base de Cálculo (R$)"]
        darf         = r["DARF a Pagar (R$)"]
        irrf         = r["IRRF Retido (R$)"]
        obs          = r["Observação"]
        venc         = r["Vencimento DARF"]
        aliq         = r["Alíquota"]
        notas_s      = r["Notas"]
        n_notas      = r["Nº Notas"]
        mes_ano      = r["Mês/Ano"]

        lucro_color  = "accent2" if lucro >= 0 else "danger"
        lucro_sinal  = "+" if lucro >= 0 else ""
        darf_color   = "danger" if darf > 0 else "muted"

        with st.expander(
            f"📅 {mes_ano}  ·  Resultado: R$ {lucro_sinal}{lucro:,.2f}  ·  "
            f"DARF: R$ {darf:,.2f}",
            expanded=True
        ):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class='note-card'>
                <div class='nota-header'>💰 Resultado do Mês</div>
                Resultado bruto:&nbsp;&nbsp;<strong class='{lucro_color}'>{lucro_sinal}R$ {lucro:,.2f}</strong><br>
                Prejuízo acumulado: R$ {r['Prejuízo Acumulado']:,.2f}<br>
                Base de cálculo: <strong>R$ {base:,.2f}</strong>
                </div>
                """.replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)

            with col2:
                darf_este_mes  = r['DARF Bruta (R$)']
                darf_acum_ent  = r.get('DARF Acum Entrada', 0.0)
                darf_total_b   = r.get('DARF Total Bruta', darf_este_mes)

                def brl(v):
                    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

                linhas = f"Base × 20%: {brl(darf_este_mes)}"
                if darf_acum_ent > 0:
                    linhas += (f"<br><span style='color:var(--warning)'>+ Acúmulo meses ant.: "
                               f"{brl(darf_acum_ent)}</span>"
                               f"<br><span style='border-top:1px solid var(--border);display:block;padding-top:2px'>"
                               f"= Subtotal: {brl(darf_total_b)}</span>")
                linhas += f"<br>− IRRF retido: {brl(irrf)}"

                darf_color_val = "var(--accent2)" if darf > 0 else "var(--muted)"
                st.markdown(f"""
                <div class='note-card'>
                <div class='nota-header'>🏛️ Cálculo DARF</div>
                Alíquota: <strong>{aliq}</strong><br>
                {linhas}<br>
                <strong style='color:{darf_color_val}'>= DARF a pagar: {brl(darf)}</strong>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class='note-card'>
                <div class='nota-header'>📆 Vencimento & Notas</div>
                Vencimento DARF: <strong>{venc}</strong><br>
                Notas processadas: <strong>{n_notas}</strong><br>
                Nºs: <span style='font-size:0.78rem;color:var(--muted)'>{notas_s}</span>
                </div>
                """, unsafe_allow_html=True)

            if obs:
                st.markdown(f"""
                <div class="alert-warning">⚠️ {obs}</div>
                """, unsafe_allow_html=True)

    # ── Histogram Chart ──
    st.markdown("---")
    st.markdown("### 📊 Resultado Mensal (Histograma)")

    meses  = [r["Mês/Ano"] for r in resultados]
    lucros = [r["Resultado Bruto (R$)"] for r in resultados]
    cores  = ["#3fb950" if v >= 0 else "#f85149" for v in lucros]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=meses,
        y=lucros,
        marker_color=cores,
        marker_line_color=["#2ea043" if v >= 0 else "#da3633" for v in lucros],
        marker_line_width=1.5,
        text=[
            f"R$ {v:+,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            for v in lucros
        ],
        textposition="outside",
        textfont=dict(color="#e6edf3", size=11, family="JetBrains Mono"),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Resultado: R$ %{y:,.2f}<br>"
            "<extra></extra>"
        ),
    ))

    fig.add_hline(y=0, line_color="#30363d", line_width=1.5)

    fig.update_layout(
        paper_bgcolor="#0d1117",
        plot_bgcolor="#161b22",
        font=dict(family="Sora, sans-serif", color="#e6edf3"),
        margin=dict(t=20, b=40, l=60, r=20),
        height=380,
        bargap=0.3,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=12, color="#8b949e"),
            linecolor="#30363d",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1c2128",
            tickprefix="R$ ",
            tickfont=dict(size=11, color="#8b949e"),
            linecolor="#30363d",
            zeroline=False,
        ),
        hoverlabel=dict(
            bgcolor="#161b22",
            bordercolor="#30363d",
            font=dict(family="Sora", color="#e6edf3"),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Detailed Notes Table ──
    st.markdown("---")
    st.markdown("### 🗒️ Detalhamento das Notas")

    df_notas = pd.DataFrame([{
        "Nr. Nota":      n["nr_nota"],
        "Data Pregão":   n["data_pregao"],
        "Resultado (R$)": resultado_financeiro(n["total_liq"] or 0, n["total_dc"] or "D"),
        "D/C":           n["total_dc"],
        "IRRF DT (R$)":  n["irrf_dt"],
    } for n in unique_notes])

    df_notas = df_notas.sort_values("Data Pregão", key=lambda s: pd.to_datetime(s, format="%d/%m/%Y", errors="coerce"))
    st.dataframe(df_notas, use_container_width=True, hide_index=True)

    # ── CSV Export ──
    st.markdown("---")
    st.markdown("### 💾 Exportar CSV")

    df_export = pd.DataFrame([{
        "Mês/Ano":              r["Mês/Ano"],
        "Nº de Notas":          r["Nº Notas"],
        "Números das Notas":    r["Notas"],
        "Resultado Bruto (R$)": f"{r['Resultado Bruto (R$)']:.2f}",
        "Base de Cálculo (R$)": f"{r['Base de Cálculo (R$)']:.2f}",
        "Alíquota Day Trade":   r["Alíquota"],
        "IRRF Retido (R$)":     f"{r['IRRF Retido (R$)']:.2f}",
        "DARF Bruta (R$)":      f"{r['DARF Bruta (R$)']:.2f}",
        "DARF a Pagar (R$)":    f"{r['DARF a Pagar (R$)']:.2f}",
        "Vencimento DARF":      r["Vencimento DARF"],
        "Observação":           r["Observação"],
    } for r in resultados])

    csv_buffer = io.StringIO()
    df_export.to_csv(csv_buffer, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    csv_bytes = csv_buffer.getvalue().encode("utf-8-sig")

    col_dl1, col_dl2 = st.columns([2, 6])
    with col_dl1:
        st.download_button(
            label="⬇️ Baixar CSV — Resumo DARF",
            data=csv_bytes,
            file_name="darf_daytrade_resumo.csv",
            mime="text/csv",
        )

    st.markdown("""
    <div class="alert-info" style="margin-top:24px">
    📌 <strong>Lembre-se:</strong> O arquivo CSV exportado é para controle pessoal.
    Para emissão da DARF, acesse o <a href="https://www.gov.br/receitafederal/pt-br" 
    target="_blank" style="color:var(--accent)">site da Receita Federal</a> e utilize o
    <strong>Sicalc</strong> (código DARF: <strong>6015</strong> para Day Trade — Renda Variável).
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
