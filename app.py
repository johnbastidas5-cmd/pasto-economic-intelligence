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
# DISEÑO UI/UX - DARK MODE PROFESIONAL CORREGIDO
# --------------------------
st.markdown("""
<style>
    /* Fondo principal y app */
    .stApp, div[data-testid="stAppViewContainer"] {
        background-color: #0B1120 !important;
        color: #F8FAFC !important;
    }
    
    /* BARRA LATERAL (SIDEBAR) - Fondo oscuro unificado */
    section[data-testid="stSidebar"], div[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1E293B !important;
    }
    
    /* Textos, radio buttons y títulos en Sidebar */
    section[data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 {
        color: #F8FAFC !important;
    }
    
    /* Tarjetas de métricas (st.metric) */
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

    /* Banners y Cuadros de alerta (st.warning / st.info / st.success) */
    div.stAlert {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 0.5rem;
    }
    div.stAlert p, div.stAlert div, div.stAlert label {
        color: #F1F5F9 !important;
    }
    
    /* Textos y títulos generales */
    h1, h2, h3, h4 { color: #F8FAFC !important; }
    p, li, span { color: #CBD5E1 !important; }
    hr { border-color: #1E293B !important; }
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

    st.error("⚠️ No se encontraron los archivos CSV principales en la carpeta 'data'.")
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
    st.title("Comparación Territorial de la Inflación en Colombia")
    st.markdown("Análisis espacial y comparado de la variación mensual del IPC entre San Juan de Pasto y las demás capitales del país.")
    
    if datos_ciudades is not None:
        COORDENADAS_CAPITALES = {
            "Bogotá": {"lat": 4.7110, "lon": -74.0721},
            "Medellín": {"lat": 6.2442, "lon": -75.5812},
            "Cali": {"lat": 3.4516, "lon": -76.5320},
            "Barranquilla": {"lat": 10.9685, "lon": -74.7813},
            "Cartagena": {"lat": 10.3997, "lon": -75.5144},
            "Bucaramanga": {"lat": 7.1254, "lon": -73.1198},
            "Pasto": {"lat": 1.2136, "lon": -77.2811},
            "Manizales": {"lat": 5.0689, "lon": -75.5174},
            "Pereira": {"lat": 4.8133, "lon": -75.6961},
            "Armenia": {"lat": 4.5339, "lon": -75.6811},
            "Cúcuta": {"lat": 7.8939, "lon": -72.5078},
            "Ibagué": {"lat": 4.4389, "lon": -75.2322},
            "Ibague": {"lat": 4.4389, "lon": -75.2322},
            "Neiva": {"lat": 2.9273, "lon": -75.2819},
            "Popayán": {"lat": 2.4448, "lon": -76.6147},
            "Montería": {"lat": 8.7479, "lon": -75.8814},
            "Sincelejo": {"lat": 9.3047, "lon": -75.3978},
            "Valledupar": {"lat": 10.4631, "lon": -73.2532},
            "Riohacha": {"lat": 11.5444, "lon": -72.9072},
            "Santa Marta": {"lat": 11.2408, "lon": -74.1990},
            "Villavicencio": {"lat": 4.1420, "lon": -73.6266},
            "Tunja": {"lat": 5.5353, "lon": -73.3678},
            "Florencia": {"lat": 1.6144, "lon": -75.6062},
            "Quibdó": {"lat": 5.6947, "lon": -76.6611},
            "Quibdo": {"lat": 5.6947, "lon": -76.6611},
            "San Andrés": {"lat": 12.5847, "lon": -81.7006}
        }
        
        df_geo = datos_ciudades.copy()
        df_geo['date_str'] = pd.to_datetime(df_geo['date']).dt.strftime('%Y-%m')
        fechas_disponibles = sorted(df_geo['date_str'].unique())
        
        col_sel1, col_sel2 = st.columns([2, 1])
        with col_sel1:
            fecha_seleccionada = st.select_slider(
                "📅 Seleccione el periodo a visualizar en el mapa:",
                options=fechas_disponibles,
                value=fechas_disponibles[-1]
            )
        
        df_mes = df_geo[df_geo['date_str'] == fecha_seleccionada].copy()
        df_mes['lat'] = df_mes['ciudad'].map(lambda x: COORDENADAS_CAPITALES.get(x, {}).get('lat', None))
        df_mes['lon'] = df_mes['ciudad'].map(lambda x: COORDENADAS_CAPITALES.get(x, {}).get('lon', None))
        
        df_mapa = df_mes.dropna(subset=['lat', 'lon']).copy()
        
        with col_sel2:
            var_pasto = df_mes[df_mes['ciudad'] == 'Pasto']['var_mensual'].values
            val_pasto_txt = f"{var_pasto[0]:.2f}%" if len(var_pasto) > 0 else "N/D"
            st.metric(f"Inflación Pasto ({fecha_seleccionada})", val_pasto_txt)

        # Mapa Geográfico Optimizado (Encuadre perfecto de Colombia)
        fig_mapa = px.scatter_geo(
            df_mapa,
            lat='lat',
            lon='lon',
            color='var_mensual',
            size=abs(df_mapa['var_mensual']) + 1.2,
            hover_name='ciudad',
            hover_data={'var_mensual': ':.2f%', 'lat': False, 'lon': False},
            text='ciudad',
            color_continuous_scale="Reds",
            title=f"Distribución Espacial de la Inflación Mensual — Colombia ({fecha_seleccionada})",
            labels={'var_mensual': 'Var. Mensual (%)'}
        )
        
        fig_mapa.update_geos(
            visible=True,
            resolution=50,
            scope="south america",
            showcountries=True, countrycolor="#334155",
            showcoastlines=True, coastlinecolor="#334155",
            showland=True, landcolor="#1E293B",
            showocean=True, oceancolor="#0B1120",
            showlakes=True, lakecolor="#0B1120",
            center=dict(lat=4.5, lon=-73.25),
            lonaxis_range=[-80.0, -66.0],
            lataxis_range=[-4.5, 13.5]
        )
        
        fig_mapa.update_traces(
            textposition='top right',
            textfont=dict(size=10, color="#F8FAFC"),
            marker=dict(line=dict(width=1.5, color='#F8FAFC'), opacity=0.9)
        )
        
        fig_mapa.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=650,
            margin=dict(t=60, b=20, l=20, r=20),
            font=dict(color="#CBD5E1")
        )
        
        st.plotly_chart(fig_mapa, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Ranking de Inflación por Ciudades en el Periodo Seleccionado")
        st.markdown("Comparativa directa ordenada de mayor a menor variación mensual.")
        
        df_ranking = df_mapa.sort_values(by='var_mensual', ascending=True)
        fig_bar = px.bar(
            df_ranking,
            x='var_mensual',
            y='ciudad',
            orientation='h',
            text_auto='.2f',
            color='var_mensual',
            color_continuous_scale="Reds",
            labels={'var_mensual': 'Variación Mensual (%)', 'ciudad': 'Ciudad'}
        )
        fig_bar.update_layout(**PLOTLY_LAYOUT, height=500)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    else:
        st.warning("⚠️ No se encontró la base de datos `data/ipc_ciudades_colombia.csv` en la carpeta data.")
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
