import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Análisis de Ventas 2025", page_icon="📊", layout="wide")

# 2. CARGA MANUAL DE DATOS
st.sidebar.header("Carga de Archivos")
# Permitimos subir varios archivos a la vez
uploaded_files = st.sidebar.file_uploader(
    "Sube los archivos 'parte_1.csv' y 'parte_2.csv'", 
    type="csv", 
    accept_multiple_files=True
)

# Lógica de validación y concatenación
if len(uploaded_files) == 2:
    # Leemos ambos archivos subidos
    df_list = [pd.read_csv(file) for file in uploaded_files]
    
    # Concatenamos en un solo DataFrame principal
    df = pd.concat(df_list, ignore_index=True)
    
    st.sidebar.success("✅ Datos combinados correctamente")
    
   
    # --- BIENVENIDA INSTITUCIONAL ---
    st.title("🏆 Corporate Performance Dashboard: Cierre de Ejercicio")
    
    st.markdown(f"""
    ### Informe Estratégico para la Alta Dirección
    **Atención:** CEO y Dirección de Ventas.
    
    Este dashboard consolida los indicadores clave de rendimiento (KPIs) del área de alimentación, permitiendo evaluar el desempeño anual y facilitar la toma de decisiones críticas.
    
    **Autor:** Javier Martínez Montelongo  
    
    ---
    """)
    
    st.info("💡 **Instrucciones:** Navegue por las pestañas para explorar los niveles de análisis global, regional y por unidad de negocio.")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Visualización Global", "Información por Tienda", "Información por Estado", "Análisis Avanzado"])
    
    # --- TAB 1: VISUALIZACIÓN GLOBAL ---
    with tab1:
        st.header("🌎 Resumen Ejecutivo Global")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tiendas Activas", value=df["store_nbr"].nunique())
        with col2:
            st.metric("Productos Vendidos (Volumen)", value=f"{df.shape[0]:,}")
        with col3:
            st.metric("Presencia Geográfica", f"{df['state'].nunique()} Estados")
        with col4:
            st.metric("Periodo Analizado", f"{df['month'].nunique()} Meses")
    
        st.write("---")
    
        # Top Categorías
        st.subheader("🔝 10 Categorías de Productos Más Vendidas")
        top_productos = df.groupby("family")["sales"].sum().nlargest(10).reset_index()
        fig = px.bar(top_productos, x='sales', y='family', orientation='h', color='sales', color_continuous_scale='Purples')
        fig.update_layout(xaxis_tickformat='.2s', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        st.info("**Conclusión:** Identificamos las familias de productos que motorizan el flujo de caja. Es vital asegurar el stock de estas categorías líderes.")
    
        # Ventas por Tienda
        st.subheader("🏢 Distribución de Ventas por Punto de Venta")
        ventas_por_tienda = df.groupby('store_nbr')['sales'].sum().reset_index().sort_values(by="sales", ascending=False)
        fig_barras = px.bar(ventas_por_tienda, x='store_nbr', y='sales', color='sales', color_continuous_scale='Purples')
        fig_barras.update_layout(xaxis_type='category')
        fig_barras.update_yaxes(tickformat=".2s")
        st.plotly_chart(fig_barras, use_container_width=True)
        st.caption("**Aporte:** Permite detectar disparidades de rendimiento entre tiendas para replicar mejores prácticas de las líderes en las rezagadas.")
    
        # Ventas en Promoción
        st.subheader("🔥 Top 10 Tiendas: Efectividad en Promociones")
        df_promos = df[df["onpromotion"] > 0]
        top_tiendas_promo = df_promos.groupby('store_nbr')['sales'].sum().nlargest(10).reset_index()
        fig_promo = px.bar(top_tiendas_promo, x='store_nbr', y='sales', color='sales', color_continuous_scale='Blues')
        fig_promo.update_layout(xaxis_type='category')
        fig_promo.update_yaxes(tickformat=".2s")
        st.plotly_chart(fig_promo, use_container_width=True)
        st.info("**Análisis:** Estas tiendas muestran la mayor sensibilidad al precio. Son los puntos ideales para campañas de liquidación de inventario.")
    
        # Estacionalidad
        st.header("📅 Análisis de Estacionalidad y Tendencias")
        tab21, tab22, tab23 = st.tabs(["Día de la Semana", "Semanas del Año", "Meses del Año"])
    
        with tab21:
            df_dia = df.groupby('day_of_week')['sales'].mean().reset_index()
            orden_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            fig1 = px.bar(df_dia, x='day_of_week', y='sales', color='sales', color_continuous_scale='Purples', category_orders={"day_of_week": orden_dias})
            st.plotly_chart(fig1, use_container_width=True)
            st.caption("**Conclusión:** Determina los días de mayor afluencia para optimizar la asignación de personal y logística de recepción.")
    
        with tab22:
            df_semana = df.groupby('week')['sales'].mean().reset_index()
            fig2 = px.line(df_semana, x='week', y='sales', template="plotly_dark")
            fig2.update_traces(fill='tozeroy')
            st.plotly_chart(fig2, use_container_width=True)
            st.caption("**Análisis:** Visualización de picos anuales (festividades) y valles, permitiendo la planificación de compras estacionales.")
    
        with tab23:
            df_mes = df.groupby('month')['sales'].mean().reset_index()
            meses_nombres = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
            df_mes['month_name'] = df_mes['month'].map(meses_nombres)
            fig3 = px.bar(df_mes, x='month_name', y='sales', color='sales', color_continuous_scale='Viridis')
            st.plotly_chart(fig3, use_container_width=True)
    
    # --- TAB 2: INFORMACIÓN POR TIENDA ---
    with tab2:
        st.header("🏪 Detalle Operativo por Unidad")
        with st.expander("Seleccione la Tienda a Auditar"):
            tienda_sel = st.selectbox("Número de tienda:", sorted(df['store_nbr'].unique()))
        
        df_t = df[df["store_nbr"] == tienda_sel]
        m1, m2, m3 = st.columns(3)
        t_sales = df_t['sales'].sum()
        t_promo = df_t[df_t['onpromotion'] > 0]['sales'].sum()
        m1.metric("Ventas Totales Tienda", f"{t_sales:,.0f}")
        m2.metric("Venta bajo Promoción", f"{t_promo:,.0f}")
        m3.metric("% Dependencia Promo", f"{(t_promo/t_sales*100):,.1f}%" if t_sales>0 else "0%")
    
        st.subheader("📅 Evolución Anual de Ventas")
        ventas_anuales = df_t.groupby('year')['sales'].sum().reset_index().sort_values('year')
        fig_anual = px.bar(ventas_anuales, x='year', y='sales', color='sales', color_continuous_scale='Purples')
        fig_anual.update_layout(xaxis_type='category')
        st.plotly_chart(fig_anual, use_container_width=True)
        st.info(f"**Insight:** Esta gráfica muestra el crecimiento orgánico de la Tienda {tienda_sel} año tras año.")
    
    # --- TAB 3: INFORMACIÓN POR ESTADO ---
    with tab3:
        st.header("📍 Análisis de Desempeño Regional")
        estado_sel = st.selectbox("Seleccionar un Estado:", df["state"].unique())
        df_est = df[df['state'] == estado_sel]
    
        st.subheader(f"📈 Volumen de Transacciones Anuales - {estado_sel}")
        trans_anuales = df_est.groupby('year')['transactions'].sum().reset_index().sort_values('year')
        fig_trans = px.line(trans_anuales, x='year', y='transactions', markers=True, color_discrete_sequence=['#7d33ff'])
        fig_trans.update_layout(xaxis_type='category')
        st.plotly_chart(fig_trans, use_container_width=True)
        st.caption("**Aporte:** Mide la fidelidad y frecuencia del cliente en la región, más allá del monto monetario.")
    
        col_ranking, col_producto = st.columns(2)
        with col_ranking:
            st.subheader("🏆 Ranking de Tiendas en el Estado")
            ranking_tiendas = df_est.groupby('store_nbr')['sales'].sum().nlargest(10).reset_index()
            fig_tiendas = px.bar(ranking_tiendas, x='sales', y=ranking_tiendas['store_nbr'].astype(str), orientation='h', color='sales', color_continuous_scale='Purples')
            st.plotly_chart(fig_tiendas, use_container_width=True)
        
        with col_producto:
            st.subheader("🔝 Mix de Productos Líder")
            top_prod = df_est.groupby('family')['sales'].sum().idxmax()
            st.metric("Categoría Más Vendida", top_prod)
            pie_data = df_est.groupby('family')['sales'].sum().nlargest(5).reset_index()
            fig_pie = px.pie(pie_data, values='sales', names='family', hole=0.4, color_discrete_sequence=px.colors.sequential.Purples_r)
            st.plotly_chart(fig_pie, use_container_width=True)
        st.info(f"**Conclusión Regional:** En {estado_sel}, la categoría {top_prod} domina el mercado. El Top 5 representa la mayor parte de los ingresos locales.")
    
    # --- TAB 4: ANÁLISIS AVANZADO ---
    with tab4:
        st.header("🚀 Strategic Insights (Nivel Dirección)")
        
        st.subheader("Análisis de Eficiencia: Ventas vs. Intensidad Promocional")
        df_matrix = df.groupby('family').agg({'sales': 'sum', 'onpromotion': 'mean'}).reset_index()
        fig_matrix = px.scatter(df_matrix, x='onpromotion', y='sales', text='family', size='sales', color='sales', color_continuous_scale='RdPu')
        st.plotly_chart(fig_matrix, use_container_width=True)
        st.warning("**Nota Estratégica:** Los productos en la parte superior izquierda son 'Estrellas' (venden mucho sin descuentos). Los de la derecha dependen demasiado de promociones para generar volumen.")
    
        st.subheader("Mapa de Calor: Concentración de Ventas por Cluster")
        heatmap_data = df.groupby(['day_of_week', 'cluster'])['sales'].mean().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='cluster', values='sales').reindex(orden_dias)
        fig_heat = px.imshow(heatmap_pivot, color_continuous_scale='Purples')
        st.plotly_chart(fig_heat, use_container_width=True)
    
        st.info("**Conclusión:** Este mapa revela patrones ocultos: qué grupos de tiendas (clusters) tienen picos de demanda en días específicos, permitiendo una distribución logística inteligente.")
    
elif len(uploaded_files) == 1:
    st.warning("⚠️ Se detectó solo un archivo. Por favor, sube ambas partes para completar el dataset.")
    st.stop()
else:
    st.info("👋 Bienvenida/o. Por favor, sube las dos partes del dataset en el menú lateral para activar el análisis.")
    # Imagen que ilustra cómo funciona la concatenación de datos en Pandas
    
    st.stop()

