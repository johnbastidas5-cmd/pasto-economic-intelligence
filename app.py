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
        border: 1px solid #38BDF8 !important;
        border-radius: 0.5rem;
        color: #F8FAFC !important;
    }
    div.stAlert p, div.stAlert div, div.stAlert label, div.stAlert span {
        color: #F8FAFC !important;
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
    st.error("⚠️ No se encontraron los archivos principales en la carpeta 'data'.")
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

    with st.expander("📖 Interpretación Académica de la Serie Global"):
        st.write("""
        La serie histórica de la variación mensual del IPC en San Juan de Pasto evidencia un régimen de baja inflación y estabilidad relativa entre 2017 y 2019, seguido por un periodo de alta perturbación a partir de 2021-2022. 
        Este comportamiento responde a choques combinados de oferta global (crisis de contenedores postpandemia) y choques de oferta locales (restricciones logísticas y bloqueos viales en el sur del país), evidenciando la fragilidad estructural de las cadenas de abastecimiento regionales.
        """)

elif pagina == "Evolución de la inflación":
    st.title("Evolución de la inflación en San Juan de Pasto")
    st.markdown("Análisis desagregado de la variación mensual y la acumulación anual por *compounding*.")
    
    fig1 = px.line(pasto, x="date", y="var_mensual", title="Variación mensual del IPC (2017-2025)", labels={"var_mensual": "Variación mensual (%)", "date": "Fecha"})
    fig1.add_hline(y=0, line_dash="dash", line_color="#F87171")
    fig1.update_traces(line_color="#38BDF8", line_width=2)
    fig1.update_layout(**PLOTLY_LAYOUT, height=400)
    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("🔬 Lectura Teórica: Dinámica Mensual y Estacionalidad"):
        st.write("""
        * **Puntos de inflexión:** Los picos más altos de la serie mensual suelen coincidir con principios de año (ajustes de tarifas reguladas, salarios y matrículas) y con coyunturas de escasez de alimentos en plazas de mercado locales.
        * **Rigidez a la baja:** Se observa que los precios presentan resistencia a disminuir en los periodos de desaceleración económica, lo que consolida una pérdida permanente del poder de compra si los ingresos nominales no se ajustan de manera sincrónica.
        """)

    st.markdown("---")
    st.markdown("### Inflación anual aproximada (Compounding)")
    st.caption("Calculada mediante composición de las variaciones mensuales oficiales del DANE (años con cobertura ≥11 meses).")

    datos_anuales_validos = anual[anual["n_meses"] >= 11]
    fig2 = px.bar(
        datos_anuales_validos,
        x="year", y="inflacion_comp",
        title="Impacto inflacionario anualizado",
        text_auto=".2f",
        labels={"year": "Año", "inflacion_comp": "Inflación Compuesta (%)"}
    )
    fig2.update_traces(marker_color="#60A5FA", textposition="outside", textfont=dict(color="#F8FAFC"))
    fig2.update_layout(**PLOTLY_LAYOUT, height=400)
    fig2.update_xaxes(dtick=1) 
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("🔬 Lectura Teórica: Acumulación Anual y Pérdida de Poder de Compra"):
        st.write("""
        La agregación anual por *compounding* refleja la verdadera magnitud del choque inflacionario sobre el presupuesto de los hogares de Pasto en el periodo postpandemia. 
        Tasas de inflación compuesta superiores al 8% o 10ual anual significan que el poder adquisitivo del dinero se reduce a un ritmo acelerado, castigando severamente a los hogares perceptores de ingresos fijos o salarios mínimos que no logran indexar sus ingresos al mismo ritmo.
        """)

elif pagina == "Poder adquisitivo (proxy)":
    st.title("Poder adquisitivo del salario mínimo (Proxy)")
    
    st.warning("""
    **Nota metodológica de rigor:**  
    Este indicador utiliza el Salario Mínimo Mensual Legal Vigente (SMMLV) deflactado por el IPC de Pasto (base diciembre 2018). Constituye un **proxy agregado** y no representa la distribución real de micro-ingresos de los hogares, existiendo una covarianza mecánica por el uso del IPC como deflactor.
    """, icon="⚠️")

    st.markdown("<br>", unsafe_allow_html=True)
    fig = px.line(pasto, x="date", y="poder_adquisitivo", title="Evolución del Poder Adquisitivo del SMMLV (Pesos constantes - base dic 2018)")
    fig.update_traces(line_color="#34D399", line_width=2.5, fill='tozeroy', fillcolor="rgba(52, 211, 153, 0.1)")
    fig.update_layout(**PLOTLY_LAYOUT, height=450)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("🔬 Análisis Económico del Ingreso Real y el Salario Mínimo"):
        st.write("""
        * **Efecto Decreto vs. Inflación Local:** Cada mes de enero, el Gobierno nacional decreta un incremento nominal del SMMLV; sin embargo, debido a la inflación acumulada a lo largo del año en Pasto, el poder adquisitivo real (línea verde) experimenta una erosión continua y progresiva hasta el siguiente ajuste.
        * **Implicación distributiva:** Esto demuestra que los incrementos nominales del salario mínimo pierden efectividad real rápidamente cuando las presiones inflacionarias locales superan las expectativas macroeconómicas nacionales.
        """)

elif pagina == "Comparación territorial estratégica":
    st.title("Heterogeneidad Regional y Asimetrías en el Costo de Vida")
    st.markdown("Análisis comparativo focalizado entre centros urbanos principales (**Bogotá**, **Medellín**) y economías regionales con alta vulnerabilidad estructural.")
    
    if datos_ciudades is not None:
        df_ciudades = datos_ciudades.copy()
        disponibles = df_ciudades['ciudad'].unique()
        ciudades_seleccionadas = [c for c in ["Pasto", "Bogotá", "Medellín", "Quibdo", "Florencia", "Popayán"] if c in disponibles]
        df_filtrado = df_ciudades[df_ciudades['ciudad'].isin(ciudades_seleccionadas)].copy()
        
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
        
        with st.expander("🔬 Interpretación Económica de la Asimetría Regional"):
            st.write("""
            * **Fricciones Logísticas y Geográficas:** San Juan de Pasto y Quibdó exhiben mayor sensibilidad ante choques de oferta que las grandes metrópolis (Bogotá y Medellín). La dependencia de corredores viales únicos incrementa los costos de transporte y margina a los consumidores locales.
            * **Inflación como Impuesto Regresivo:** Al tener una canasta donde el gasto en alimentos posee mayor ponderación relativa, los hogares de Pasto resienten con mayor intensidad los episodios inflacionarios frente a ciudades con estructuras de consumo más diversificadas.
            """)
    else:
        st.warning("⚠️ No se encontró la base de datos `data/ipc_ciudades_colombia.csv`.")

elif pagina == "Conceptos metodológicos":
    st.title("Conceptos y Notas Metodológicas")
    st.markdown("Precisiones teóricas y operativas para la correcta lectura de la investigación.")

    with st.expander("📌 Índice de Precios al Consumidor (IPC)", expanded=True):
        st.write("Indicador estadístico que mide la variación porcentual promedio de los precios de una canasta representativa de bienes y servicios de consumo de los hogares. En Colombia es elaborado mensualmente por el DANE. La segmentación por dominio geográfico (Pasto) permite aislar las dinámicas locales.")

    with st.expander("📌 Poder adquisitivo y salarios reales"):
        st.write("Representa la cantidad de bienes y servicios que un flujo de ingresos nominales permite adquirir. Si la inflación crece por encima de los ajustes nominales salariales, el ingreso real disminuye y se deteriora el bienestar.")

    with st.expander("📌 Limitación mecánica del Proxy"):
        st.write("Al construir el indicador dividiendo el SMMLV entre el IPC regional, se introduce una covarianza puramente matemática. Esto restringe la interpretación causal directa a partir de este indicador agregado.")

elif pagina == "Fuentes y limitaciones":
    st.title("Fuentes Documentales y Limitaciones")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📚 Fuentes Oficiales")
        st.markdown("""
        * **Fuente Primaria:** Departamento Administrativo Nacional de Estadística (DANE).
        * **Módulo:** Anexos de variación mensual del IPC por ciudades y dominios geográficos.
        * **Proxy Salarial:** Salario Mínimo Mensual Legal Vigente (SMMLV) deflactado (Base Dic. 2018).
        * **Periodo de Estudio:** 2017 – 2025.
        """)
    with col2:
        st.markdown("### ⚠️ Limitaciones Metodológicas")
        st.markdown("""
        * El análisis empírico actual utiliza series agregadas; **no incorpora microdatos** de ingresos a nivel de hogar (GEIH).
        * El alcance es de carácter descriptivo-correlacional, **no establece efectos causales** paramétricos directos.
        """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748B; font-size: 0.85rem;'>
    Seminario de Investigación Regional 2 | Universidad de Nariño | 2026<br>
    Desarrollado para el análisis reproducible con Streamlit y Plotly.
</div>
""", unsafe_allow_html=True)
