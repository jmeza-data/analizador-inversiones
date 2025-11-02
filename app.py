import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="📈 Analizador de Inversiones",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .category-badge {
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .add-stock-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px dashed #dee2e6;
        margin: 1rem 0;
    }
    .category-section {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 3px solid #ff9800;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado de sesión
if 'custom_stocks' not in st.session_state:
    st.session_state.custom_stocks = {}

if 'removed_default_stocks' not in st.session_state:
    st.session_state.removed_default_stocks = set()

if 'stock_categories' not in st.session_state:
    st.session_state.stock_categories = {}

if 'custom_categories' not in st.session_state:
    st.session_state.custom_categories = set()

# Título principal
st.markdown('<h1 class="main-header">📈 Analizador de Inversiones</h1>', unsafe_allow_html=True)
st.markdown("### 💡 Descubre cuánto habrías ganado (o perdido) invirtiendo en tus acciones favoritas")

# Diccionario de acciones populares por defecto con sus categorías
DEFAULT_STOCKS = {
    "NU Holdings (Nu Bank)": {"symbol": "NU", "category": "🏦 Fintech"},
    "NVIDIA Corporation": {"symbol": "NVDA", "category": "💻 Tecnología"}, 
    "Apple Inc.": {"symbol": "AAPL", "category": "💻 Tecnología"},
    "Alphabet Inc. (Google)": {"symbol": "GOOGL", "category": "💻 Tecnología"},
    "Meta Platforms (Facebook)": {"symbol": "META", "category": "💻 Tecnología"},
    "Microsoft Corporation": {"symbol": "MSFT", "category": "💻 Tecnología"},
    "Amazon.com Inc.": {"symbol": "AMZN", "category": "🛒 E-commerce"},
    "Tesla Inc.": {"symbol": "TSLA", "category": "🚗 Automotriz"},
    "Netflix Inc.": {"symbol": "NFLX", "category": "🎬 Entretenimiento"},
    "PayPal Holdings": {"symbol": "PYPL", "category": "🏦 Fintech"},
    "Coca-Cola Company": {"symbol": "KO", "category": "🥤 Consumo"},
    "Johnson & Johnson": {"symbol": "JNJ", "category": "💊 Salud"}
}

# Categorías predefinidas disponibles
PREDEFINED_CATEGORIES = [
    "💻 Tecnología",
    "🏦 Fintech", 
    "🪙 Criptomonedas",
    "📈 ETFs",
    "🚗 Automotriz",
    "💊 Salud",
    "🥤 Consumo",
    "🎬 Entretenimiento",
    "🛒 E-commerce",
    "🏭 Industrial",
    "🏠 Inmobiliario",
    "⚡ Energía",
    "📊 Índices",
    "💎 Materias Primas",
    "🌿 ESG/Sustentable"
]

# Función para validar símbolo de acción
@st.cache_data(ttl=3600)
def validate_stock_symbol(symbol):
    try:
        stock = yf.Ticker(symbol.upper())
        info = stock.info
        if 'symbol' in info or 'shortName' in info:
            return True, info.get('shortName', symbol.upper())
        return False, None
    except Exception as e:
        st.error(f"Error validando {symbol}: {str(e)}")
        return False, None

# Función para limpiar el estado de widgets removidos
def clean_removed_widget_states():
    keys_to_remove = []
    for key in st.session_state.keys():
        if key.startswith('investment_'):
            symbol = key.replace('investment_', '')
            if symbol in st.session_state.removed_default_stocks:
                keys_to_remove.append(key)
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

# Limpiar estados al inicio si es necesario
clean_removed_widget_states()

# Sidebar para configuración
st.sidebar.header("🎯 Configuración de Análisis")

# ============= SECCIÓN: GESTIÓN DE ACCIONES Y CATEGORÍAS =============
st.sidebar.markdown("---")
st.sidebar.subheader("📋 Gestión de Acciones")

# Expandir sección de agregar acciones
with st.sidebar.expander("➕ Agregar Nueva Acción", expanded=False):
    # Input para símbolo
    new_symbol = st.text_input(
        "🎯 Símbolo de la acción:",
        placeholder="Ej: TSLA, BTC-USD, SPY",
        key="new_symbol_input",
        help="Ingresa el símbolo de cualquier acción disponible en Yahoo Finance"
    ).upper()
    
    # Selector de categoría
    st.markdown("📂 **Categoría:**")
    
    # Combinar categorías predefinidas con personalizadas
    all_categories = sorted(list(set(PREDEFINED_CATEGORIES + list(st.session_state.custom_categories))))
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        category_option = st.selectbox(
            "Selecciona una categoría:",
            ["Crear nueva categoría..."] + all_categories,
            key="category_selector"
        )
    
    with col2:
        st.markdown("") # Espacio
        st.markdown("") # Espacio
        validate_button = st.button("🔍 Validar", key="validate_button")
    
    # Si selecciona crear nueva categoría
    selected_category = category_option
    if category_option == "Crear nueva categoría...":
        new_category = st.text_input(
            "✨ Nombre de la nueva categoría:",
            placeholder="Ej: 🎮 Gaming, 🌍 Internacionales",
            key="new_category_input",
            help="Usa emojis para hacer más visual tu categoría"
        )
        if new_category.strip():
            selected_category = new_category.strip()
    
    # Validar y agregar acción
    if validate_button and new_symbol:
        if not selected_category or selected_category == "Crear nueva categoría...":
            st.error("❌ Por favor selecciona o crea una categoría")
        else:
            try:
                with st.spinner(f"Validando {new_symbol}..."):
                    is_valid, company_name = validate_stock_symbol(new_symbol)
                    
                    if is_valid:
                        # Verificar si ya existe
                        existing_symbols = [data["symbol"] for data in DEFAULT_STOCKS.values()] + list(st.session_state.custom_stocks.keys())
                        
                        if new_symbol not in existing_symbols:
                            # Agregar acción
                            st.session_state.custom_stocks[new_symbol] = {
                                "name": company_name,
                                "category": selected_category
                            }
                            
                            # Agregar categoría a personalizadas si es nueva
                            if selected_category not in PREDEFINED_CATEGORIES:
                                st.session_state.custom_categories.add(selected_category)
                            
                            st.success(f"✅ {new_symbol} agregado en {selected_category}!")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ {new_symbol} ya está en la lista")
                    else:
                        st.error(f"❌ {new_symbol} no es un símbolo válido")
            except Exception as e:
                st.error(f"❌ Error al validar {new_symbol}: {str(e)}")
    
    # Mostrar instrucciones
    st.markdown("""
    **💡 Consejos:**
    - Usa símbolos de Yahoo Finance
    - Ejemplos por categoría:
      - 🪙 Crypto: BTC-USD, ETH-USD
      - 📈 ETFs: SPY, QQQ, VTI
      - 💻 Tech: SHOP, SQ, ROKU
    """)

# Mostrar acciones personalizadas agrupadas por categoría
if st.session_state.custom_stocks:
    st.sidebar.markdown("**🎯 Tus Acciones Personalizadas:**")
    
    # Agrupar por categorías
    custom_by_category = {}
    for symbol, data in st.session_state.custom_stocks.items():
        category = data["category"]
        if category not in custom_by_category:
            custom_by_category[category] = []
        custom_by_category[category].append((symbol, data["name"]))
    
    # Mostrar cada categoría
    for category, stocks in custom_by_category.items():
        st.sidebar.markdown(f"**{category}:**")
        for symbol, name in stocks:
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                display_name = name[:15] + "..." if len(name) > 15 else name
                st.markdown(f"  • **{symbol}** ({display_name})")
            with col2:
                if st.button("🗑️", key=f"remove_custom_{symbol}", help=f"Eliminar {symbol}"):
                    # Limpiar estado del widget antes de eliminar
                    widget_key = f"investment_{symbol}"
                    if widget_key in st.session_state:
                        del st.session_state[widget_key]
                    del st.session_state.custom_stocks[symbol]
                    if symbol in st.session_state.stock_categories:
                        del st.session_state.stock_categories[symbol]
                    st.rerun()

# Gestión de categorías personalizadas
if st.session_state.custom_categories:
    with st.sidebar.expander("🏷️ Gestionar Categorías Personalizadas"):
        st.markdown("**Tus categorías:**")
        for category in list(st.session_state.custom_categories):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"• {category}")
            with col2:
                # Solo permitir eliminar si no hay acciones en esa categoría
                stocks_in_category = [s for s, d in st.session_state.custom_stocks.items() if d["category"] == category]
                if not stocks_in_category:
                    if st.button("🗑️", key=f"remove_cat_{category}", help=f"Eliminar categoría"):
                        st.session_state.custom_categories.remove(category)
                        st.rerun()
                else:
                    st.markdown("🔒")

st.sidebar.markdown("---")

# Combinar todas las acciones
ALL_STOCKS = {}

# Agregar acciones por defecto (excluyendo las removidas)
for name, data in DEFAULT_STOCKS.items():
    symbol = data["symbol"]
    if symbol not in st.session_state.removed_default_stocks:
        ALL_STOCKS[name] = {
            "symbol": symbol,
            "category": data["category"]
        }

# Agregar acciones personalizadas
for symbol, data in st.session_state.custom_stocks.items():
    ALL_STOCKS[data["name"]] = {
        "symbol": symbol,
        "category": data["category"]
    }

# Selector de fechas
st.sidebar.subheader("📅 Período de Análisis")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Fecha inicio",
        value=datetime.now() - timedelta(days=365),
        max_value=datetime.now() - timedelta(days=1),
        help="Fecha de inicio de la inversión"
    )
with col2:
    end_date = st.date_input(
        "Fecha final",
        value=datetime.now() - timedelta(days=1),
        max_value=datetime.now(),
        help="Fecha final de la inversión"
    )

st.sidebar.markdown("---")

# ============= SECCIÓN: INPUTS DE INVERSIÓN =============
st.sidebar.subheader("💵 Monto de Inversión (USD)")

# Botones de acciones rápidas
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    if st.button("💯 $100 Todo", help="Poner $100 en todas las acciones visibles"):
        for data in ALL_STOCKS.values():
            st.session_state[f"investment_{data['symbol']}"] = 100.0
        st.rerun()
        
with col2:
    if st.button("🔄 Reset", help="Poner $0 en todas las acciones"):
        for data in ALL_STOCKS.values():
            st.session_state[f"investment_{data['symbol']}"] = 0.0
        st.rerun()

with col3:
    if st.button("🎲 Random", help="Cantidades aleatorias"):
        import random
        for data in ALL_STOCKS.values():
            st.session_state[f"investment_{data['symbol']}"] = float(random.randint(0, 20) * 50)
        st.rerun()

# Selector de categoría para filtrar
if ALL_STOCKS:
    all_categories_in_use = sorted(list(set(data["category"] for data in ALL_STOCKS.values())))
    
    category_filter = st.sidebar.selectbox(
        "🏷️ Filtrar por categoría:",
        ["Todas las categorías"] + all_categories_in_use,
        key="category_filter",
        help="Filtra las acciones por categoría para análisis específicos"
    )

investments = {}

# Agrupar acciones por categoría para mostrar
stocks_by_category = {}
for name, data in ALL_STOCKS.items():
    category = data["category"]
    symbol = data["symbol"]
    
    # Aplicar filtro de categoría
    if category_filter != "Todas las categorías" and category != category_filter:
        continue
        
    if category not in stocks_by_category:
        stocks_by_category[category] = []
    stocks_by_category[category].append((name, symbol))

# Mostrar acciones agrupadas por categoría
for category, stocks in stocks_by_category.items():
    st.sidebar.markdown(f"**{category}:**")
    
    for stock_name, symbol in stocks:
        # Verificar si es acción por defecto o personalizada
        is_default = symbol in [data["symbol"] for data in DEFAULT_STOCKS.values()]
        
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            current_value = st.session_state.get(f"investment_{symbol}", 0.0)
            icon = "💰" if is_default else "🌟"
            
            investments[symbol] = st.number_input(
                f"{icon} {symbol}",
                min_value=0.0,
                value=current_value,
                step=50.0,
                format="%.2f",
                key=f"investment_{symbol}",
                help=stock_name
            )
        with col2:
            if is_default:
                # Botón para ocultar acciones por defecto
                if st.button("❌", key=f"hide_{symbol}", help=f"Ocultar {symbol}"):
                    st.session_state.removed_default_stocks.add(symbol)
                    widget_key = f"investment_{symbol}"
                    if widget_key in st.session_state:
                        del st.session_state[widget_key]
                    st.rerun()
            else:
                # Las acciones personalizadas ya tienen botón de eliminar arriba
                st.markdown("🌟")

# Mostrar acciones ocultas (para poder restaurarlas)
if st.session_state.removed_default_stocks:
    with st.sidebar.expander("👁️ Mostrar Acciones Ocultas"):
        st.markdown("**Acciones ocultas (click para restaurar):**")
        for symbol in list(st.session_state.removed_default_stocks):
            # Buscar info de la acción
            stock_info = None
            for name, data in DEFAULT_STOCKS.items():
                if data["symbol"] == symbol:
                    stock_info = (name, data["category"])
                    break
            
            if stock_info:
                name, category = stock_info
                if st.button(f"🔄 {symbol} ({category})", key=f"restore_{symbol}"):
                    st.session_state.removed_default_stocks.remove(symbol)
                    st.rerun()

st.sidebar.markdown("---")

# Resumen rápido de inversión
total_investment_preview = sum(investments.values())
if total_investment_preview > 0:
    st.sidebar.success(f"💰 **Inversión Total:** ${total_investment_preview:,.2f}")
    st.sidebar.markdown(f"📊 **Acciones con inversión:** {sum(1 for v in investments.values() if v > 0)}")
    
    # Resumen por categorías
    investment_by_category = {}
    for name, data in ALL_STOCKS.items():
        symbol = data["symbol"]
        category = data["category"]
        if symbol in investments and investments[symbol] > 0:
            if category not in investment_by_category:
                investment_by_category[category] = 0
            investment_by_category[category] += investments[symbol]
    
    if investment_by_category:
        st.sidebar.markdown("**💼 Por categoría:**")
        for category, amount in investment_by_category.items():
            percentage = (amount / total_investment_preview) * 100
            st.sidebar.markdown(f"  • {category}: ${amount:,.0f} ({percentage:.1f}%)")

# Botón para calcular
calculate_button = st.sidebar.button("🚀 CALCULAR INVERSIONES", type="primary", use_container_width=True)

# Función para obtener datos de acciones con manejo de errores mejorado
@st.cache_data(ttl=3600)
def get_stock_data(symbol, start, end):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(start=start, end=end, interval="1d")
        if len(data) == 0:
            return None
        return data
    except Exception as e:
        st.error(f"❌ Error obteniendo datos para {symbol}: {str(e)}")
        return None

# Función para obtener información de la empresa
@st.cache_data(ttl=3600)
def get_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            'name': info.get('shortName', symbol),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'currency': info.get('currency', 'USD')
        }
    except:
        return {
            'name': symbol,
            'sector': 'N/A',
            'industry': 'N/A',
            'currency': 'USD'
        }

# Función para calcular métricas de inversión
def calculate_investment_metrics(data, investment_amount):
    if data is None or len(data) == 0 or investment_amount <= 0:
        return None
    
    start_price = data['Close'].iloc[0]
    end_price = data['Close'].iloc[-1]
    
    shares = investment_amount / start_price
    final_value = shares * end_price
    profit_loss = final_value - investment_amount
    profit_loss_pct = (profit_loss / investment_amount) * 100
    
    # Calcular máximo y mínimo durante el período
    max_price = data['Close'].max()
    min_price = data['Close'].min()
    max_value = shares * max_price
    min_value = shares * min_price
    
    # Calcular volatilidad (desviación estándar de retornos diarios)
    daily_returns = data['Close'].pct_change().dropna()
    volatility = daily_returns.std() * (252 ** 0.5) * 100 if len(daily_returns) > 0 else 0  # Anualizada
    
    return {
        'investment': investment_amount,
        'start_price': start_price,
        'end_price': end_price,
        'shares': shares,
        'final_value': final_value,
        'profit_loss': profit_loss,
        'profit_loss_pct': profit_loss_pct,
        'max_value': max_value,
        'min_value': min_value,
        'max_price': max_price,
        'min_price': min_price,
        'volatility': volatility,
        'data': data
    }

# Función para obtener categoría de una acción
def get_stock_category(symbol):
    # Buscar en acciones por defecto
    for name, data in DEFAULT_STOCKS.items():
        if data["symbol"] == symbol:
            return data["category"]
    
    # Buscar en acciones personalizadas
    for sym, data in st.session_state.custom_stocks.items():
        if sym == symbol:
            return data["category"]
    
    return "🔹 Otros"

# Procesamiento principal
if calculate_button:
    if start_date >= end_date:
        st.error("❌ La fecha de inicio debe ser anterior a la fecha final")
    else:
        active_investments = {k: v for k, v in investments.items() if v > 0}
        
        if not active_investments:
            st.warning("⚠️ Por favor, ingresa al menos una inversión mayor a $0")
        else:
            st.success(f"🎯 Analizando {len(active_investments)} inversiones desde {start_date.strftime('%d/%m/%Y')} hasta {end_date.strftime('%d/%m/%Y')}")
            
            # Obtener datos y calcular métricas
            results = {}
            total_investment = 0
            total_final_value = 0
            stock_infos = {}
            
            # Barra de progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, (symbol, amount) in enumerate(active_investments.items()):
                status_text.text(f"📊 Obteniendo datos para {symbol}... ({i+1}/{len(active_investments)})")
                progress_bar.progress((i + 1) / len(active_investments))
                
                data = get_stock_data(symbol, start_date, end_date)
                
                if data is not None:
                    stock_info = get_stock_info(symbol)
                    stock_infos[symbol] = stock_info
                    
                    metrics = calculate_investment_metrics(data, amount)
                    
                    if metrics:
                        # Agregar información de categoría
                        metrics['category'] = get_stock_category(symbol)
                        results[symbol] = metrics
                        total_investment += amount
                        total_final_value += metrics['final_value']
                else:
                    st.warning(f"⚠️ No se encontraron datos para {symbol} en el período seleccionado")
            
            progress_bar.empty()
            status_text.empty()
            
            if results:
                total_profit_loss = total_final_value - total_investment
                total_profit_loss_pct = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
                
                # ============= SECCIÓN: MÉTRICAS PRINCIPALES =============
                st.markdown("## 📊 Resumen General")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="💰 Inversión Total", 
                        value=f"${total_investment:,.2f}"
                    )
                
                with col2:
                    st.metric(
                        label="💎 Valor Final", 
                        value=f"${total_final_value:,.2f}"
                    )
                
                with col3:
                    st.metric(
                        label="📈 Ganancia/Pérdida", 
                        value=f"${total_profit_loss:,.2f}",
                        delta=f"{total_profit_loss_pct:+.2f}%"
                    )
                
                with col4:
                    roi_emoji = "🟢" if total_profit_loss_pct >= 0 else "🔴"
                    st.metric(
                        label=f"{roi_emoji} ROI Total", 
                        value=f"{total_profit_loss_pct:+.2f}%"
                    )
                
                st.markdown("---")
                
                # ============= SECCIÓN: ANÁLISIS POR CATEGORÍAS =============
                st.markdown("## 🏷️ Análisis por Categorías Personalizadas")
                
                # Agrupar resultados por categorías
                category_analysis = {}
                for symbol, metrics in results.items():
                    category = metrics['category']
                    if category not in category_analysis:
                        category_analysis[category] = {
                            'investment': 0,
                            'final_value': 0,
                            'profit_loss': 0,
                            'count': 0,
                            'stocks': []
                        }
                    category_analysis[category]['investment'] += metrics['investment']
                    category_analysis[category]['final_value'] += metrics['final_value']
                    category_analysis[category]['profit_loss'] += metrics['profit_loss']
                    category_analysis[category]['count'] += 1
                    category_analysis[category]['stocks'].append(symbol)
                
                # Crear tabla de análisis por categorías
                category_table = []
                for category, data in category_analysis.items():
                    roi = (data['profit_loss'] / data['investment']) * 100 if data['investment'] > 0 else 0
                    profit_emoji = "🟢" if data['profit_loss'] >= 0 else "🔴"
                    
                    category_table.append({
                        '🏷️ Categoría': category,
                        '📊 # Acciones': data['count'],
                        '💵 Inversión': f"${data['investment']:,.2f}",
                        '💎 Valor Final': f"${data['final_value']:,.2f}",
                        f'{profit_emoji} Ganancia/Pérdida': f"${data['profit_loss']:,.2f}",
                        '📈 ROI (%)': f"{roi:+.2f}%",
                        '📋 Acciones': ", ".join(data['stocks'])
                    })
                
                df_categories = pd.DataFrame(category_table)
                st.dataframe(df_categories, use_container_width=True, hide_index=True)
                
                # Gráfico de barras por categorías
                fig_cat = go.Figure()
                
                categories = list(category_analysis.keys())
                cat_profits = [category_analysis[c]['profit_loss'] for c in categories]
                cat_colors = ['#00cc44' if p >= 0 else '#ff4444' for p in cat_profits]
                
                fig_cat.add_trace(go.Bar(
                    x=categories,
                    y=cat_profits,
                    marker_color=cat_colors,
                    text=[f"${p:,.0f}" for p in cat_profits],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Ganancia/Pérdida: $%{y:,.2f}<extra></extra>'
                ))
                
                fig_cat.update_layout(
                    title="💰 Ganancia/Pérdida por Categoría",
                    xaxis_title="Categoría",
                    yaxis_title="Ganancia/Pérdida (USD)",
                    template="plotly_white",
                    height=500
                )
                
                st.plotly_chart(fig_cat, use_container_width=True)
                
                st.markdown("---")
                
                # ============= SECCIÓN: TABLA DETALLADA =============
                st.markdown("## 📋 Análisis Detallado por Acción")
                
                # Preparar datos para la tabla
                table_data = []
                for symbol, metrics in results.items():
                    # Buscar nombre de la empresa
                    stock_name = stock_infos.get(symbol, {}).get('name', symbol)
                    if symbol in [data["symbol"] for data in DEFAULT_STOCKS.values()]:
                        for name, data in DEFAULT_STOCKS.items():
                            if data["symbol"] == symbol:
                                stock_name = name.split(' ')[0]
                                break
                    elif symbol in st.session_state.custom_stocks:
                        stock_name = st.session_state.custom_stocks[symbol]["name"].split(' ')[0]
                    
                    profit_emoji = "🟢" if metrics['profit_loss'] >= 0 else "🔴"
                    
                    table_data.append({
                        '🏢 Empresa': f"{stock_name} ({symbol})",
                        '🏷️ Categoría': metrics['category'],
                        '💵 Inversión': f"${metrics['investment']:,.2f}",
                        '📈 Precio Inicial': f"${metrics['start_price']:.2f}",
                        '📉 Precio Final': f"${metrics['end_price']:.2f}",
                        '📊 Acciones': f"{metrics['shares']:.2f}",
                        '💎 Valor Final': f"${metrics['final_value']:,.2f}",
                        f'{profit_emoji} Ganancia/Pérdida': f"${metrics['profit_loss']:,.2f}",
                        '📈 ROI (%)': f"{metrics['profit_loss_pct']:+.2f}%",
                        '📊 Volatilidad': f"{metrics['volatility']:.1f}%"
                    })
                
                df_results = pd.DataFrame(table_data)
                st.dataframe(df_results, use_container_width=True, hide_index=True)
                
                # ============= SECCIÓN: GRÁFICOS ADICIONALES =============
                
                # Gráfico de barras - Ganancia/Pérdida por acción
                st.markdown("## 📊 Ganancia/Pérdida por Acción")
                
                fig_bar = go.Figure()
                
                symbols = list(results.keys())
                profits = [results[s]['profit_loss'] for s in symbols]
                colors = ['#00cc44' if p >= 0 else '#ff4444' for p in profits]
                
                fig_bar.add_trace(go.Bar(
                    x=symbols,
                    y=profits,
                    marker_color=colors,
                    text=[f"${p:,.0f}" for p in profits],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Ganancia/Pérdida: $%{y:,.2f}<extra></extra>'
                ))
                
                fig_bar.update_layout(
                    title="💰 Ganancia/Pérdida por Acción Individual",
                    xaxis_title="Acción",
                    yaxis_title="Ganancia/Pérdida (USD)",
                    template="plotly_white",
                    height=500
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Gráfico de evolución de precios normalizados
                st.markdown("## 📈 Evolución de Precios (Base 100)")
                
                fig_lines = go.Figure()
                
                colors_line = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#ff9999', '#66b3ff']
                
                for i, (symbol, metrics) in enumerate(results.items()):
                    data = metrics['data']
                    normalized_prices = (data['Close'] / data['Close'].iloc[0]) * 100
                    
                    fig_lines.add_trace(go.Scatter(
                        x=data.index,
                        y=normalized_prices,
                        mode='lines',
                        name=f"{symbol} ({metrics['category']})",
                        line=dict(width=3, color=colors_line[i % len(colors_line)]),
                        hovertemplate=f'<b>{symbol}</b><br>Fecha: %{{x}}<br>Precio normalizado: %{{y:.1f}}<extra></extra>'
                    ))
                
                fig_lines.update_layout(
                    title="📈 Evolución de Precios Normalizados por Categoría",
                    xaxis_title="Fecha",
                    yaxis_title="Precio Normalizado (Base 100)",
                    template="plotly_white",
                    hovermode='x unified',
                    height=600,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.02
                    )
                )
                
                st.plotly_chart(fig_lines, use_container_width=True)
                
                # Gráficos de pie - Distribución por categorías
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🥧 Inversión por Categoría")
                    
                    fig_pie_cat = go.Figure(data=[go.Pie(
                        labels=list(category_analysis.keys()),
                        values=[category_analysis[c]['investment'] for c in category_analysis.keys()],
                        hole=.4,
                        textinfo='label+percent',
                        textposition='auto'
                    )])
                    
                    fig_pie_cat.update_layout(
                        title="Capital por Categoría",
                        template="plotly_white",
                        height=400,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_pie_cat, use_container_width=True)
                
                with col2:
                    st.markdown("### 💎 Valor Final por Categoría")
                    
                    fig_pie_cat2 = go.Figure(data=[go.Pie(
                        labels=list(category_analysis.keys()),
                        values=[category_analysis[c]['final_value'] for c in category_analysis.keys()],
                        hole=.4,
                        textinfo='label+percent',
                        textposition='auto'
                    )])
                    
                    fig_pie_cat2.update_layout(
                        title="Valor Final por Categoría",
                        template="plotly_white",
                        height=400,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_pie_cat2, use_container_width=True)
                
                # ============= SECCIÓN: ESTADÍSTICAS ADICIONALES =============
                st.markdown("## 📊 Estadísticas Adicionales")
                
                # Top performers
                sorted_by_roi = sorted(results.items(), key=lambda x: x[1]['profit_loss_pct'], reverse=True)
                best_performer = sorted_by_roi[0]
                worst_performer = sorted_by_roi[-1]
                
                # Top categoría
                sorted_categories = sorted(category_analysis.items(), key=lambda x: (x[1]['profit_loss'] / x[1]['investment']) * 100, reverse=True)
                best_category = sorted_categories[0] if sorted_categories else None
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.success(f"""
                    **🏆 Mejor Inversión**
                    
                    **{best_performer[0]}**
                    
                    Categoría: **{best_performer[1]['category']}**
                    
                    ROI: **{best_performer[1]['profit_loss_pct']:+.2f}%**
                    
                    Ganancia: **${best_performer[1]['profit_loss']:,.2f}**
                    """)
                
                with col2:
                    st.error(f"""
                    **📉 Peor Inversión**
                    
                    **{worst_performer[0]}**
                    
                    Categoría: **{worst_performer[1]['category']}**
                    
                    ROI: **{worst_performer[1]['profit_loss_pct']:+.2f}%**
                    
                    Pérdida: **${worst_performer[1]['profit_loss']:,.2f}**
                    """)
                
                with col3:
                    if best_category:
                        best_cat_roi = (best_category[1]['profit_loss'] / best_category[1]['investment']) * 100
                        st.info(f"""
                        **🏷️ Mejor Categoría**
                        
                        **{best_category[0]}**
                        
                        ROI: **{best_cat_roi:+.2f}%**
                        
                        Acciones: **{best_category[1]['count']}**
                        
                        Ganancia: **${best_category[1]['profit_loss']:,.2f}**
                        """)
                
                # Información adicional
                st.markdown("---")
                st.markdown("### ℹ️ Información del Análisis")
                
                st.info(f"""
                **📅 Período analizado:** {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')} ({(end_date - start_date).days} días)
                
                **🎯 Acciones analizadas:** {len(results)} inversiones activas
                
                **🏷️ Categorías únicas:** {len(category_analysis)} categorías diferentes
                
                **📊 Acciones personalizadas:** {len(st.session_state.custom_stocks)} agregadas por ti
                
                **🎨 Categorías personalizadas:** {len(st.session_state.custom_categories)} creadas por ti
                
                **💡 Metodología:** Se asume inversión completa en fecha de inicio y mantenimiento hasta fecha final.
                
                **📊 Fuente de datos:** Yahoo Finance
                
                **⚠️ Disclaimer:** Solo para fines educativos. No constituye asesoría financiera.
                """)
                
            else:
                st.error("❌ No se pudieron obtener datos para ninguna de las acciones seleccionadas.")

# Instrucciones iniciales
else:
    st.markdown("""
    ## 🚀 ¿Cómo usar esta aplicación?
    
    Esta herramienta te permite simular inversiones con **sistema completo de categorías personalizables**.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📝 Pasos para usar:
        
        1. **➕ Agrega acciones** con categorías personalizadas
        
        2. **🏷️ Crea categorías** como "🎮 Gaming", "🌍 Internacionales"
        
        3. **🔍 Filtra por categoría** para análisis específicos
        
        4. **📅 Selecciona fechas** y **💵 montos de inversión**
        
        5. **🚀 Calcula** y obtén análisis por categorías
        """)
    
    with col2:
        st.markdown("""
        ### ✨ Sistema de Categorías:
        
        - **🏷️ 15 categorías predefinidas** listas para usar
        - **➕ Crear categorías personalizadas** ilimitadas
        - **🔍 Filtros por categoría** en sidebar
        - **📊 Análisis detallado** por cada categoría
        - **📈 Gráficos específicos** de rendimiento por categoría
        """)
    
    # Mostrar categorías predefinidas
    st.markdown("### 🏷️ Categorías Predefinidas Disponibles:")
    
    # Mostrar en columnas
    cols = st.columns(3)
    for i, category in enumerate(PREDEFINED_CATEGORIES):
        col = cols[i % 3]
        with col:
            st.markdown(f"• {category}")
    
    # Mostrar acciones por defecto agrupadas por categoría
    st.markdown("### 📊 Acciones Populares por Categoría:")
    
    default_by_category = {}
    for name, data in DEFAULT_STOCKS.items():
        category = data["category"]
        if category not in default_by_category:
            default_by_category[category] = []
        default_by_category[category].append((name, data["symbol"]))
    
    for category, stocks in default_by_category.items():
        with st.expander(f"{category} ({len(stocks)} acciones)"):
            for name, symbol in stocks:
                st.markdown(f"• **{symbol}** - {name}")
    
    # Ejemplos de uso con categorías
    st.markdown("""
    ### 💡 Ejemplos con Categorías Personalizadas:
    
    **Ejemplo 1: Portfolio Gaming**
    - Crea categoría: "🎮 Gaming"
    - Agrega: RBLX (Roblox), EA (Electronic Arts), TTWO (Take-Two)
    - Analiza: NVDA vs acciones gaming
    
    **Ejemplo 2: Sostenible vs Tech**
    - Crea categoría: "🌿 ESG/Sustentable"
    - Agrega: TSLA, NEE, ESG
    - Compara: Sustentables vs Tecnología tradicional
    
    **Ejemplo 3: Internacional**
    - Crea categoría: "🌍 Internacionales"
    - Agrega: BABA, TSM, ASML
    - Analiza: Performance global vs US
    """)

# Footer personalizado
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 10px; margin-top: 2rem;'>
    <h4>📈 Analizador de Inversiones v3.0 - Streamlit Cloud</h4>
    <p style='color: #666; margin: 0;'>
        🏷️ Sistema completo de categorías | ✨ Acciones personalizables | 📊 Análisis avanzado
    </p>
    <p style='color: #888; font-size: 0.8rem; margin: 0.5rem 0 0 0;'>
        Desarrollado con ❤️ usando Streamlit | Solo fines educativos | Datos de Yahoo Finance
    </p>
</div>
""", unsafe_allow_html=True)