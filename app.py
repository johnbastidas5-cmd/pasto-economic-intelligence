import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# --------------------------
# CONFIGURACIÓN
# --------------------------
st.set_page_config(
    page_title="Inflación y Poder Adquisitivo – San Juan de Pasto",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo profesional de alto contraste
st.markdown("""
<style>
    .stApp {
        background-color: #0F172A;
        color: #F1F5F9;
    }
    h1, h2, h3, h4 {
        color: #F8FAFC !important;
        font-weight: 600;
    }
    div[data-testid="stSidebar"] {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }
    .stMetric {
        background: #1E293B;
        padding: 16px 20px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .stAlert {
        border-radius: 8px;
    }
    .stRadio > label {
        color: #E2E8F0 !important;
    }
    div[data-testid="stSidebar"] .stRadio label {
        color: #E2E8F0 !important;
    }
    .stCaption, .stMarkdown p, .stMarkdown li {
        color: #CBD5E1 !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# CARGA DE DATOS
# --------------------------
@st.cache_data
def cargar_datos():
    ruta_data = Path("data")
    archivo1 = ruta_data / "serie_completa_pasto.csv"
    archivo2 = ruta_data / "resumen_anual_pasto.csv"

    if archivo1.exists() and archivo2.exists():
        pasto = pd.read_csv(archivo1, parse_dates=["date"])
        anual = pd.read_csv(archivo2)
        pasto = pasto[pasto["year"] <= 2025].copy()
        anual = anual[anual["year"] <= 2025].copy()
        return pasto, anual

    st.error("No se encontraron los archivos CSV en la carpeta 'data'. Verifique que los archivos estén disponibles.")
    st.stop()

pasto, anual = cargar_datos()

# --------------------------
# SIDEBAR
# --------------------------
st.sidebar.title("Navegación")
st.sidebar.markdown("Análisis de inflación y poder adquisitivo en San Juan de Pasto")

pagina = st.sidebar.radio(
    "Secciones",
    [
        "Inicio",
        "Evolución de la inflación",
        "Poder adquisitivo (proxy)",
        "Proyecciones exploratorias",
        "Conceptos y notas metodológicas",
        "Fuentes y limitaciones"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Datos actualizados: {datetime.now().strftime('%Y-%m-%d')}")
st.sidebar.info("Fuente principal: DANE – Índice de Precios al Consumidor (dominio Pasto).")

# --------------------------
# PÁGINAS
# --------------------------
if pagina == "Inicio":
    st.title("Inflación y poder adquisitivo de los hogares")
    st.markdown("### San Juan de Pasto, 2017–2025")
    st.markdown("Herramienta de visualización preliminar asociada al Seminario de Investigación Regional 2 – Universidad de Nariño.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Observaciones", f"{len(pasto):,}")
    with col2:
        st.metric("Periodo", "2017–2025")
    with col3:
        st.metric("Última var. mensual", f"{pasto['var_mensual'].iloc[-1]:.2f}%")
    with col4:
        st.metric("Fuente", "DANE")

    st.markdown("---")
    st.subheader("Resumen del periodo")
    st.markdown("Variación mensual del Índice de Precios al Consumidor en San Juan de Pasto.")

    fig = px.line(
        pasto, x="date", y="var_mensual",
        labels={"var_mensual": "Variación mensual (%)", "date": "Fecha"}
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#64748B")
    fig.update_layout(
        template="plotly_dark",
        height=420,
        margin=dict(t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0")
    )
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "Evolución de la inflación":
    st.header("Evolución de la inflación en San Juan de Pasto")
    st.markdown("""
    La variación mensual del IPC mide el cambio porcentual promedio de los precios de la canasta de consumo de los hogares.  
    Valores positivos indican aumento de precios; valores cercanos a cero o negativos reflejan estabilidad o deflación puntual.
    """)

    fig1 = px.line(
        pasto, x="date", y="var_mensual",
        title="Variación mensual del IPC — San Juan de Pasto (2017-2025)",
        labels={"var_mensual": "Variación mensual (%)", "date": "Fecha"}
    )
    fig1.add_hline(y=0, line_dash="dash", line_color="#64748B")
    fig1.update_layout(
        template="plotly_dark",
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0")
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### Inflación anual aproximada")
    st.caption("Calculada mediante compounding de las variaciones mensuales oficiales del DANE. Se incluyen solo años con cobertura casi completa (≥11 meses).")

    fig2 = px.bar(
        anual[anual["n_meses"] >= 11],
        x="year", y="inflacion_comp",
        title="Inflación anual aproximada — San Juan de Pasto",
        text_auto=".1f",
        color_discrete_sequence=["#3B82F6"]
    )
    fig2.update_layout(
        template="plotly_dark",
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0")
    )
    st.plotly_chart(fig2, use_container_width=True)

elif pagina == "Poder adquisitivo (proxy)":
    st.header("Poder adquisitivo del salario mínimo (proxy)")
    st.warning("""
    **Nota metodológica importante**  
    Este indicador utiliza el Salario Mínimo Mensual Legal Vigente (SMMLV) deflactado por el IPC de Pasto.  
    Constituye un **proxy agregado** y no representa el ingreso real de los hogares.  
    Para un análisis adecuado de poder adquisitivo a nivel de hogar se requieren microdatos de la GEIH.  
    Existe una relación mecánica porque el mismo IPC se emplea como deflactor.
    """)

    fig = px.line(
        pasto, x="date", y="poder_adquisitivo",
        title="Poder adquisitivo del SMMLV (pesos de diciembre 2018)",
        labels={"poder_adquisitivo": "Poder adquisitivo", "date": "Fecha"}
    )
    fig.update_layout(
        template="plotly_dark",
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0")
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **Interpretación**  
    - Ascenso de la serie: el salario mínimo alcanza para adquirir una mayor cantidad de bienes y servicios valorados a precios de Pasto.  
    - Descenso de la serie: el aumento de precios supera el ajuste del salario mínimo, reduciendo la capacidad de compra.
    """)

elif pagina == "Proyecciones exploratorias":
    st.header("Proyecciones exploratorias")
    st.info("""
    Estas proyecciones se basan en el promedio simple de las variaciones mensuales de los últimos 12 meses.  
    Son ejercicios exploratorios y **no constituyen pronósticos oficiales** ni modelos econométricos.
    """)

    ultimos_12 = pasto.tail(12)["var_mensual"].mean()
    st.metric("Promedio de los últimos 12 meses", f"{ultimos_12:.2f}%")

    meses = st.slider("Número de meses a proyectar", 3, 18, 6)
    ultima_fecha = pasto["date"].max()
    fechas_futuras = pd.date_range(
        start=ultima_fecha + pd.offsets.MonthBegin(1),
        periods=meses,
        freq="MS"
    )
    proyeccion = pd.DataFrame({
        "date": fechas_futuras,
        "var_mensual": ultimos_12
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pasto["date"], y=pasto["var_mensual"],
        name="Serie histórica",
        line=dict(color="#3B82F6", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=proyeccion["date"], y=proyeccion["var_mensual"],
        name="Proyección (promedio reciente)",
        line=dict(color="#F59E0B", width=2, dash="dot")
    ))
    fig.update_layout(
        title="Proyección exploratoria de la variación mensual del IPC",
        template="plotly_dark",
        height=460,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0")
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Supuesto: el promedio de los últimos 12 meses se mantiene constante. La dinámica real de precios suele presentar mayor variabilidad.")

elif pagina == "Conceptos y notas metodológicas":
    st.header("Conceptos y notas metodológicas")

    with st.expander("Índice de Precios al Consumidor (IPC)"):
        st.write("Indicador que mide la variación porcentual promedio de los precios de una canasta representativa de bienes y servicios consumidos por los hogares. En Colombia es elaborado mensualmente por el DANE. El dominio geográfico de Pasto permite análisis territoriales específicos.")

    with st.expander("Poder adquisitivo"):
        st.write("Cantidad de bienes y servicios que un ingreso determinado permite adquirir. Cuando los precios crecen más rápido que los ingresos nominales, el ingreso real y el poder adquisitivo disminuyen.")

    with st.expander("Uso del salario mínimo como proxy"):
        st.write("Se emplea el SMMLV deflactado por el IPC de Pasto por disponibilidad y comparabilidad temporal. No representa la distribución de ingresos de los hogares. El análisis riguroso de poder adquisitivo requiere microdatos de ingresos (GEIH).")

    with st.expander("Relación mecánica"):
        st.write("Al construir el indicador de poder adquisitivo dividiendo el salario mínimo por el IPC, parte de la covarianza observada con la inflación es matemática. Esto limita la interpretación causal a partir de este proxy.")

    with st.expander("Alcance causal"):
        st.write("Con la información agregada aquí presentada solo es posible hablar de asociación y evolución conjunta. La identificación de impactos causales requiere diseños metodológicos más robustos (por ejemplo, con microdatos, controles y estrategias de identificación).")

elif pagina == "Fuentes y limitaciones":
    st.header("Fuentes y limitaciones")

    st.markdown("""
    **Fuente principal de datos**  
    Departamento Administrativo Nacional de Estadística (DANE) – Anexos de variación mensual del IPC por ciudades.

    **Proxy utilizado**  
    Salario Mínimo Mensual Legal Vigente deflactado por el IPC de San Juan de Pasto (base diciembre 2018).

    **Periodo de análisis**  
    2017 – 2025

    **Limitaciones**  
    - No se utilizan microdatos de ingresos de hogares (GEIH o ECV).  
    - Existe relación mecánica en el proxy de poder adquisitivo.  
    - Las proyecciones son exploratorias y no constituyen pronósticos oficiales.  
    - No se dispone de IPC por divisiones de gasto para el dominio Pasto en esta versión.  
    - El análisis es descriptivo y no estima efectos causales.

    **Autores**  
    John Alexander Bastidas Morales · Jhonatan Stiven Melo Yela  
    Universidad de Nariño – Seminario de Investigación Regional 2  
    Docente: Julio Riascos
    """)

st.markdown("---")
st.caption("Universidad de Nariño · Seminario de Investigación Regional 2 · Datos oficiales del DANE")
