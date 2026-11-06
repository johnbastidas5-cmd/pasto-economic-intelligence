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
    page_title="Inflación y Poder Adquisitivo – Pasto",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# DISEÑO UI/UX - DARK MODE PROFESIONAL
# --------------------------
# Soluciona el problema de contraste en tarjetas, métricas y textos
st.markdown("""
<style>
    /* Fondo principal y textos base */
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    /* Barra lateral */
    div[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1E293B;
    }
    div[data-testid="stSidebar"] * {
        color: #CBD5E1 !important;
    }
    div[data-testid="stSidebar"] h1 {
        color: #F8FAFC !important;
    }
    /* Tarjetas de métricas (st.metric) */
    div[data-testid="metric-container"] {
        background-color: #1E293B;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    /* CORRECCIÓN DE CONTRASTE: Títulos y valores de las métricas */
    div[data-testid="stMetricLabel"] label, div[data-testid="stMetricLabel"] p {
        color: #94A3B8 !important;
        font-size: 0.9rem !important;
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] div {
        color: #F8FAFC !important;
        font-weight: 700;
    }
    /* Alertas y banners */
    div.stAlert {
        border-radius: 0.5rem;
        border: 1px solid #334155;
    }
    /* Párrafos, listas y captions */
    p, li, .stCaption {
        color: #CBD5E1 !important;
    }
    /* Líneas separadoras */
    hr {
        border-color: #1E293B !important;
    }
    /* Selectores y radio buttons */
    .stRadio > div > label > div {
        color: #F8FAFC !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# CONFIGURACIÓN PLOTLY HOMOGÉNEA
# --------------------------
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

    st.error("⚠️ No se encontraron los archivos CSV en la carpeta 'data'. Verifique que los archivos estén disponibles.")
    st.stop()

# Intento de cargar datos de múltiples ciudades (para mapa de calor)
@st.cache_data
def cargar_datos_ciudades():
    ruta_data = Path("data")
    archivo_ciudades = ruta_data / "ipc_ciudades_colombia.csv"
    if archivo_ciudades.exists():
        ciudades = pd.read_csv(archivo_ciudades, parse_dates=["date"])
        return ciudades
    return None

pasto, anual = cargar_datos()
datos_ciudades = cargar_datos_ciudades()

# --------------------------
# SIDEBAR / NAVEGACIÓN
# --------------------------
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
            "Comparación territorial",
            "Proyecciones exploratorias",
            "Conceptos metodológicos",
            "Fuentes y limitaciones"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption(f"📅 Datos actualizados: {datetime.now().strftime('%Y-%m-%d')}")
    st.info("Fuente principal: DANE – Índice de Precios al Consumidor (IPC).")

# --------------------------
# RENDERIZADO DE PÁGINAS
# --------------------------

if pagina == "Inicio":
    st.title("Inflación y poder adquisitivo de los hogares")
    st.subheader("San Juan de Pasto, 2017–2025")
    st.markdown("Herramienta de visualización preliminar asociada al Seminario de Investigación Regional 2 – Universidad de Nariño.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Tarjetas de métricas principales
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
    st.markdown("Evolución de la variación mensual del Índice de Precios al Consumidor (IPC) en el dominio geográfico de Pasto.")

    fig = px.line(
        pasto, x="date", y="var_mensual",
        labels={"var_mensual": "Variación mensual (%)", "date": "Fecha"}
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#F87171", opacity=0.8)
    fig.update_traces(line_color="#38BDF8", line_width=2.5)
    fig.update_layout(**PLOTLY_LAYOUT, height=450)
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "Evolución de la inflación":
    st.title("Evolución de la inflación en San Juan de Pasto")
    st.markdown("""
    La variación mensual del IPC mide el cambio porcentual promedio de los precios de la canasta de consumo de los hogares.  
    Valores positivos indican aumento generalizado de precios; valores cercanos a cero o negativos reflejan estabilidad o deflación coyuntural.
    """)
    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfica 1: Mensual
    fig1 = px.line(
        pasto, x="date", y="var_mensual",
        title="Variación mensual del IPC (2017-2025)",
        labels={"var_mensual": "Variación mensual (%)", "date": "Fecha"}
    )
    fig1.add_hline(y=0, line_dash="dash", line_color="#F87171")
    fig1.update_traces(line_color="#38BDF8", line_width=2)
    fig1.update_layout(**PLOTLY_LAYOUT, height=400)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")
    
    # Gráfica 2: Anual Compuesta
    st.markdown("### Inflación anual aproximada (Compounding)")
    st.caption("Calculada mediante composición (compounding) de las variaciones mensuales oficiales del DANE. Se incluyen solo años con cobertura casi completa (≥11 meses).")

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
    # Asegurar que el eje X muestre los años como enteros
    fig2.update_xaxes(dtick=1) 
    st.plotly_chart(fig2, use_container_width=True)

elif pagina == "Poder adquisitivo (proxy)":
    st.title("Poder adquisitivo del salario mínimo (Proxy)")
    
    st.warning("""
    **Nota metodológica de rigor:**  
    Este indicador utiliza el Salario Mínimo Mensual Legal Vigente (SMMLV) deflactado por el IPC específico de Pasto.  
    Constituye un **proxy agregado** y no representa la distribución real de ingresos de los hogares. Existe una relación estadística mecánica debido a que el mismo IPC se emplea como deflactor. Para estimaciones causales precisas se requiere el uso de microdatos de la GEIH.
    """, icon="⚠️")

    st.markdown("<br>", unsafe_allow_html=True)

    fig = px.line(
        pasto, x="date", y="poder_adquisitivo",
        title="Evolución del Poder Adquisitivo del SMMLV (Pesos constantes - base dic 2018)",
        labels={"poder_adquisitivo": "Poder adquisitivo real (COP)", "date": "Fecha"}
    )
    fig.update_traces(line_color="#34D399", line_width=2.5, fill='tozeroy', fillcolor="rgba(52, 211, 153, 0.1)")
    fig.update_layout(**PLOTLY_LAYOUT, height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Interpretación Económica:**  
    - **Ascenso de la serie:** El ajuste nominal del salario mínimo supera la inflación acumulada, permitiendo adquirir una mayor cantidad de bienes valorados a precios de Pasto.  
    - **Descenso de la serie:** El aumento sostenido de precios (inflación) erosiona el ajuste nominal previo, reduciendo la capacidad real de compra del hogar representativo.
    """)

elif pagina == "Comparación territorial":
    st.title("Comparación Territorial de la Inflación")
    st.markdown("Análisis comparado de la variación de precios entre San Juan de Pasto y otras ciudades capitales de Colombia.")
    
    if datos_ciudades is not None:
        # LÓGICA SI EL USUARIO PROPORCIONA EL ARCHIVO DE CIUDADES
        st.success("Base de datos territorial cargada correctamente.")
        
        # Crear tabla pivote para el mapa de calor (Ciudad vs Fecha)
        pivot_ciudades = datos_ciudades.pivot_table(
            values='var_mensual', 
            index='ciudad', 
            columns='date', 
            aggfunc='mean'
        )
        
        fig = px.imshow(
            pivot_ciudades,
            color_continuous_scale="RdYlBu_r", # Rojo para alta inflación, Azul para baja/deflación
            aspect="auto",
            title="Mapa de Calor: Variación Mensual del IPC por Ciudades",
            labels=dict(x="Fecha", y="Dominio Geográfico (Ciudad)", color="Var. Mensual (%)")
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("Los tonos más rojizos indican presiones inflacionarias más fuertes en ese mes específico para la ciudad correspondiente.")
    else:
        # LÓGICA SI NO HAY DATOS TERRITORIALES (Cumpliendo la directriz de NO inventar datos)
        st.warning("""
        **Limitación de Datos: Comparación territorial no disponible.**
        
        Actualmente, la base de datos cargada (`serie_completa_pasto.csv`) únicamente contiene observaciones para el dominio geográfico de San Juan de Pasto. Para realizar un análisis comparado espacialmente válido frente a otros dominios, es necesario contar con información cruzada oficial.
        
        *No se han imputado ni estimado valores territoriales artificiales para preservar el rigor académico exigido.*
        """, icon="🛑")
        
        st.markdown("### ¿Cómo activar este módulo?")
        st.markdown("""
        Para activar el Mapa de Calor territorial, incluya un archivo llamado `ipc_ciudades_colombia.csv` en la carpeta `data/` con la siguiente estructura proveniente de los anexos del DANE:
        """)
        
        df_ejemplo = pd.DataFrame({
            "date": ["2023-01-01", "2023-01-01", "2023-01-01"],
            "ciudad": ["Pasto", "Bogotá", "Cali"],
            "var_mensual": [1.12, 1.05, 1.15]
        })
        st.dataframe(df_ejemplo, use_container_width=True)
        st.caption("Una vez el archivo esté en la carpeta, el sistema generará automáticamente el mapa de calor económico.")

elif pagina == "Proyecciones exploratorias":
    st.title("Proyecciones Exploratorias")
    st.info("""
    Estas proyecciones utilizan un modelo estático basado en el promedio simple de las variaciones mensuales recientes (últimos 12 meses).  
    **Advertencia:** Son ejercicios descriptivos exploratorios. No constituyen pronósticos oficiales ni reemplazan modelos econométricos de series de tiempo (ARIMA/SARIMA).
    """, icon="ℹ️")

    ultimos_12 = pasto.tail(12)["var_mensual"].mean()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Promedio Móvil (Últimos 12 meses)", f"{ultimos_12:.3f}%")
        meses = st.slider("Horizonte de proyección (meses)", min_value=3, max_value=18, value=6)
    
    ultima_fecha = pasto["date"].max()
    fechas_futuras = pd.date_range(start=ultima_fecha + pd.offsets.MonthBegin(1), periods=meses, freq="MS")
    proyeccion = pd.DataFrame({"date": fechas_futuras, "var_mensual": ultimos_12})

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pasto["date"], y=pasto["var_mensual"],
        name="Serie Histórica Observada",
        line=dict(color="#38BDF8", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=proyeccion["date"], y=proyeccion["var_mensual"],
        name="Proyección (Inercia 12M)",
        line=dict(color="#FBBF24", width=2.5, dash="dot")
    ))
    fig.update_layout(
        title=f"Proyección Inercial de la Variación Mensual del IPC ({meses} meses)",
        **PLOTLY_LAYOUT,
        height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Supuesto metodológico: La inercia inflacionaria reciente se mantiene constante. En la práctica empírica, la dinámica de precios presenta estacionalidad y choques exógenos.")

elif pagina == "Conceptos metodológicos":
    st.title("Conceptos y Notas Metodológicas")
    st.markdown("Glosario y precisiones analíticas para la correcta interpretación de los resultados.")

    with st.expander("📌 Índice de Precios al Consumidor (IPC)", expanded=True):
        st.write("Indicador estadístico que mide la variación porcentual promedio de los precios al por menor de una canasta representativa de bienes y servicios consumidos por los hogares. En Colombia, es elaborado mensualmente por el DANE. La segmentación territorial (dominio geográfico de Pasto) permite aislar la dinámica de precios regional de los promedios nacionales.")

    with st.expander("📌 Poder adquisitivo y salarios reales"):
        st.write("Representa la cantidad física de bienes y servicios que un flujo de ingreso nominal permite adquirir. Si el nivel general de precios (inflación) crece a una tasa superior al crecimiento de los ingresos nominales (ej. incrementos salariales), el ingreso real se contrae, deteriorando el bienestar económico del hogar.")

    with st.expander("📌 Limitación mecánica del Proxy utilizado"):
        st.write("Al construir el proxy dividiendo el SMMLV entre el IPC regional, se introduce una covarianza puramente matemática. Esto significa que, por diseño de la ecuación, subidas en el IPC fuerzan caídas en la métrica. Por ende, la causalidad estricta no puede derivarse únicamente de esta visualización descriptiva.")

    with st.expander("📌 Implicaciones de Causalidad"):
        st.write("Los datos agregados presentados evidencian asociación cronológica y evolución conjunta. La inferencia causal rigurosa (ej. impacto heterogéneo por quintiles de ingreso) exigiría estrategias de identificación microeconométricas aplicadas a las bases de microdatos de la Gran Encuesta Integrada de Hogares (GEIH).")

elif pagina == "Fuentes y limitaciones":
    st.title("Fuentes Documentales y Limitaciones")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📚 Fuentes de Información")
        st.markdown("""
        * **Fuente Primaria:** Departamento Administrativo Nacional de Estadística (DANE).
        * **Módulo:** Anexos de variación mensual histórica del IPC por ciudades y dominios geográficos.
        * **Proxy de Ingreso:** Salario Mínimo Mensual Legal Vigente histórico deflactado (Base Dic. 2018).
        * **Cobertura Temporal:** 2017 – 2025.
        * **Cobertura Espacial:** San Juan de Pasto (Área Urbana).
        """)

    with col2:
        st.markdown("### ⚠️ Limitaciones del Estudio")
        st.markdown("""
        * Análisis fundamentado en series agregadas; **no incorpora microdatos** de la GEIH ni ECV.
        * El análisis es estrictamente descriptivo-correlacional, **no establece efectos causales** paramétricos.
        * Desagregación por divisiones de gasto (alimentos, vivienda, transporte) no incluida en esta versión.
        * Las proyecciones mostradas carecen de validación econométrica formal.
        """)

    st.markdown("---")
    st.markdown("""
    **Créditos de Investigación:**  
    👨‍🎓 John Alexander Bastidas Morales · Jhonatan Stiven Melo Yela  
    🏛️ Universidad de Nariño – Seminario de Investigación Regional 2  
    👨‍🏫 Docente supervisor: Julio Riascos
    """)

# Footer universal
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748B; font-size: 0.85rem;'>
    Desarrollado para el Seminario de Investigación Regional 2 | Universidad de Nariño | 2026<br>
    Renderizado con Streamlit y Plotly.
</div>
""", unsafe_allow_html=True)
