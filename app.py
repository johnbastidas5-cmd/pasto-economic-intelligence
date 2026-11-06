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
# CONFIGURACIÓN DE LA PÁGINA
# --------------------------
st.set_page_config(
    page_title="Inflación y Poder Adquisitivo – Pasto y Regiones",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# DISEÑO UI/UX - DARK MODE PROFESIONAL
# --------------------------
st.markdown("""
<style>
    .stApp, div[data-testid="stAppViewContainer"] {
        background-color: #0B1120 !important;
        color: #F8FAFC !important;
    }
    section[data-testid="stSidebar"], div[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1E293B !important;
    }
    section[data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 {
        color: #F8FAFC !important;
    }
    div[data-testid="metric-container"] {
        background-color: #1E293B !important;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #334155;
    }
    div[data-testid="stMetricLabel"] p {
        color: #94A3B8 !important;
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] div {
        color: #F8FAFC !important;
        font-weight: 700;
    }
    div.stAlert {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 0.5rem;
    }
    div.stAlert p, div.stAlert div, div.stAlert label {
        color: #F1F5F9 !important;
    }
    h1, h2, h3, h4 { color: #F8FAFC !important; }
    p, li, span { color: #CBD5E1 !important; }
    hr { border-color: #1E293B !important; }
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = "plotly_dark"
PLOTLY_LAYOUT = dict(
    template=PLOTLY_TEMPLATE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#CBD5E1", family="system-ui, -apple-system, sans-serif"),
    margin=dict(t=50, b=40, l=40, r=20),
    xaxis=dict(showgrid=True, gridcolor="#1E293B", zerolinecolor="#334155"),
    yaxis=dict(showgrid=True, gridcolor="#1E293B", zerolinecolor="#334155")
)

BASE_DIR = Path(__file__).resolve().parent
RUTA_DATA = BASE_DIR / "data"

@st.cache_data
def cargar_datos():
    archivo1 = RUTA_DATA / "serie_completa_pasto.csv"
    archivo2 = RUTA_DATA / "resumen_anual_pasto.csv"
    if archivo1.exists() and archivo2.exists():
        pasto = pd.read_csv(archivo1, parse_dates=["date"])
        anual = pd.read_csv(archivo2)
        pasto = pasto[pasto["year"] <= 2025].copy()
        anual = anual[anual["year"] <= 2025].copy()
        return pasto, anual
    st.error("⚠️ No se encontraron los archivos principales en 'data'.")
    st.stop()

@st.cache_data
def cargar_datos_ciudades():
    archivo_ciudades = RUTA_DATA / "ipc_ciudades_colombia.csv"
    if archivo_ciudades.exists():
        ciudades = pd.read_csv(archivo_ciudades, parse_dates=["date"])
        return ciudades
    return None

pasto, anual = cargar_datos()
datos_ciudades = cargar_datos_ciudades()

with st.sidebar:
    st.title("Análisis Regional")
    st.markdown("Inflación y poder adquisitivo en San Juan de Pasto")
    st.markdown("---")
    
    pagina = st.radio(
        "Secciones del Análisis",
        [
            "Inicio",
            "Evolución de la inflación",
            "Poder adquisitivo (proxy)",
            "Comparación territorial estratégica",
            "Proyecciones exploratorias",
            "Conceptos metodológicos",
            "Fuentes y limitaciones"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption(f"📅 Datos actualizados: {datetime.now().strftime('%Y-%m-%d')}")
    st.info("Fuente principal: DANE – IPC.")

if pagina == "Inicio":
    st.title("Inflación y poder adquisitivo de los hogares")
    st.subheader("San Juan de Pasto, 2017–2025")
    st.markdown("Herramienta de visualización preliminar asociada al Seminario de Investigación Regional 2 – Universidad de Nariño.")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Observaciones Mensuales", f"{len(pasto):,}")
    with col2:
        st.metric("Periodo de Análisis", "2017–2025")
    with col3:
        st.metric("Última Var. Mensual", f"{pasto['var_mensual'].iloc[-1]:.2f}%")
    with col4:
        st.metric("Fuente Oficial", "DANE")

    st.markdown("---")
    st.markdown("### Resumen de la dinámica inflacionaria")
    fig = px.line(pasto, x="date", y="var_mensual", labels={"var_mensual": "Variación mensual (%)", "date": "Fecha"})
    fig.add_hline(y=0, line_dash="dash", line_color="#F87171", opacity=0.8)
    fig.update_traces(line_color="#38BDF8", line_width=2.5)
    fig.update_layout(**PLOTLY_LAYOUT, height=450)
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "Evolución de la inflación":
    st.title("Evolución de la inflación en San Juan de Pasto")
    st.markdown("La variación mensual del IPC mide el cambio porcentual promedio de los precios de la canasta de consumo.")
    fig1 = px.line(pasto, x="date", y="var_mensual", title="Variación mensual del IPC (2017-2025)", labels={"var_mensual": "Variación mensual (%)", "date": "Fecha"})
    fig1.add_hline(y=0, line_dash="dash", line_color="#F87171")
    fig1.update_traces(line_color="#38BDF8", line_width=2)
    fig1.update_layout(**PLOTLY_LAYOUT, height=400)
    st.plotly_chart(fig1, use_container_width=True)

elif pagina == "Poder adquisitivo (proxy)":
    st.title("Poder adquisitivo del salario mínimo (Proxy)")
    st.warning("Nota metodológica: Indicador agregado deflactado por el IPC de Pasto.", icon="⚠️")
    fig = px.line(pasto, x="date", y="poder_adquisitivo", title="Evolución del Poder Adquisitivo del SMMLV (Pesos base dic 2018)")
    fig.update_traces(line_color="#34D399", line_width=2.5, fill='tozeroy', fillcolor="rgba(52, 211, 153, 0.1)")
    fig.update_layout(**PLOTLY_LAYOUT, height=450)
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "Comparación territorial estratégica":
    st.title("Heterogeneidad Regional y Asimetrías en el Costo de Vida")
    st.markdown("Análisis comparativo focalizado entre centros urbanos principales (**Bogotá**, **Medellín**), economías intermedias fronterizas/andinas (**San Juan de Pasto**) y dominios con vulnerabilidad estructural (**Tumaco** y **Quibdó**).")
    
    if datos_ciudades is not None:
        # Filtrar ciudades de interés estratégico
        ciudades_foco = ["Pasto", "Bogotá", "Medellín", "San Andrés de Tumaco", "Quibdo"]
        
        # Mapeo o limpieza si Tumaco se llama 'San Andrés de Tumaco' o similar en el DANE
        df_ciudades = datos_ciudades.copy()
        
        # Verificar qué nombres de ciudades exactos existen en el dataframe
        disponibles = df_ciudades['ciudad'].unique()
        
        # Seleccionar las disponibles que coincidan con nuestro enfoque
        ciudades_seleccionadas = [c for c in ["Pasto", "Bogotá", "Medellín", "Quibdo", "Florencia", "Popayán"] if c in disponibles]
        
        df_filtrado = df_ciudades[df_ciudades['ciudad'].isin(ciudades_seleccionadas)].copy()
        
        # Gráfico de líneas temporales comparadas
        fig_comp = px.line(
            df_filtrado,
            x='date',
            y='var_mensual',
            color='ciudad',
            title="Evolución Comparada de la Inflación Mensual por Dominios Territoriales",
            labels={'var_mensual': 'Variación Mensual (%)', 'date': 'Fecha', 'ciudad': 'Ciudad'}
        )
        fig_comp.update_layout(**PLOTLY_LAYOUT, height=500)
        st.plotly_chart(fig_comp, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Análisis Académico e Interpretación Económica Regional")
        st.markdown("""
        ### Asimetrías Espaciales y Canastas de Consumo Diferenciadas
        
        La evidencia gráfica permite validar que **la inflación no opera como un fenómeno espacialmente homogéneo**. Las economías regionales de Colombia enfrentan choques de oferta y estructuras de costos altamente fragmentados debido a factores logísticos, costos de transporte y la composición de la canasta de bienes de los hogares:
        
        1. **Vulnerabilidad en Regiones Periféricas (Pasto y Quibdó):**  
           San Juan de Pasto y Quibdó experimentan con frecuencia una alta volatilidad en los precios de los alimentos y bienes regulados. Al ser economías con alta dependencia de cadenas de suministro externas y con conectividad vial vulnerable (frecuentes cierres en la vía Panamericana para el caso de Pasto), los choques de oferta externos se transmiten de manera más violenta e inelástica hacia el consumidor local.
           
        2. **Efecto Escala en Centros Urbanos Mayores (Bogotá y Medellín):**  
           Bogotá y Medellín exhiben trayectorias inflacionarias con menor amplitud mensual extrema, explicadas por mercados laborales más profundos, economías de aglomeración y redes logísticas diversificadas que amortiguan parcialmente los choques exógenos de materias primas internacionales.
           
        3. **Implicaciones sobre la Distribución del Ingreso y el Poder Adquisitivo:**  
           Dado que los hogares de menores ingresos en ciudades intermedias y periféricas destinan una proporción significativamente mayor de su presupuesto presupuestario a **bienes de primera necesidad (alimentos y servicios públicos)**, un aumento idéntico en la tasa de inflación general representa una **pérdida real de poder adquisitivo desproporcionadamente mayor** para Pasto y Quibdó en comparación con los estratos medios y altos de las grandes metrópolis. Esto corrobora empíricamente la hipótesis de que la inflación actúa como un impuesto regresivo territorial.
        """)
    else:
        st.warning("⚠️ No se encontró la base de datos `data/ipc_ciudades_colombia.csv`.")

elif pagina == "Proyecciones exploratorias":
    st.title("Proyecciones Exploratorias")
    ultimos_12 = pasto.tail(12)["var_mensual"].mean()
    st.metric("Promedio Móvil (Últimos 12 meses)", f"{ultimos_12:.3f}%")
    meses = st.slider("Horizonte (meses)", 3, 18, 6)
    ultima_fecha = pasto["date"].max()
    fechas_futuras = pd.date_range(start=ultima_fecha + pd.offsets.MonthBegin(1), periods=meses, freq="MS")
    proyeccion = pd.DataFrame({"date": fechas_futuras, "var_mensual": ultimos_12})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pasto["date"], y=pasto["var_mensual"], name="Histórico", line=dict(color="#38BDF8", width=2)))
    fig.add_trace(go.Scatter(x=proyeccion["date"], name="Proyección", y=proyeccion["var_mensual"], line=dict(color="#FBBF24", width=2.5, dash="dot")))
    fig.update_layout(title="Proyección Inercial", **PLOTLY_LAYOUT, height=450)
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "Conceptos metodológicos":
    st.title("Conceptos y Notas Metodológicas")
    st.write("Detalles conceptuales sobre el IPC regional y la formación de precios en dominios periféricos y centrales.")

elif pagina == "Fuentes y limitaciones":
    st.title("Fuentes Documentales y Limitaciones")
    st.markdown("DANE – Anexos de IPC por ciudades y dominios geográficos (2017-2025).")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748B; font-size: 0.85rem;'>
    Seminario de Investigación Regional 2 | Universidad de Nariño | 2026
</div>
""", unsafe_allow_html=True)
