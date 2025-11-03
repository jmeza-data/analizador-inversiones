import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# ============= CONFIGURACIÓN DE LA PÁGINA =============
st.set_page_config(
    page_title="📈 Analizador de Inversiones Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============= CSS MEJORADO =============
st.markdown("""
<style>
    /* Estilo principal */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    /* Tarjetas de métricas mejoradas */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .metric-positive {
        border-left: 5px solid #00c851;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    }
    
    .metric-negative {
        border-left: 5px solid #ff4444;
        background: linear-gradient(135deg, #f8d7da 0%, #f1b0b7 100%);
    }
    
    /* Sidebar mejorado */
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    /* Botones de acción rápida */
    .quick-action-btn {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        border: none;
        font-weight: bold;
        cursor: pointer;
        margin: 0.2rem;
        transition: all 0.3s ease;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Categorías con colores */
    .category-tech { background: linear-gradient(45deg, #4285f4, #34a853); }
    .category-fintech { background: linear-gradient(45deg, #ff6b35, #f7931e); }
    .category-crypto { background: linear-gradient(45deg, #f7931e, #ffcd02); }
    .category-health { background: linear-gradient(45deg, #ea4335, #fbbc04); }
    .category-consumer { background: linear-gradient(45deg, #34a853, #0f9d58); }
    .category-auto { background: linear-gradient(45deg, #4285f4, #0066cc); }
    
    /* Alertas mejoradas */
    .success-alert {
        background: linear-gradient(90deg, #d4edda, #c3e6cb);
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        color: #155724;
    }
    
    .warning-alert {
        background: linear-gradient(90deg, #fff3cd, #ffeaa7);
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        color: #856404;
    }
    
    .error-alert {
        background: linear-gradient(90deg, #f8d7da, #f5c6cb);
        border: 1px solid #f5c6cb;
        border-radius: 10px;
        padding: 1rem;
        color: #721c24;
    }
    
    /* Tablas mejoradas */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Loading spinner personalizado */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Tooltips mejorados */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Navegación por tabs */
    .tab-nav {
        display: flex;
        background: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem;
        margin: 1rem 0;
    }
    
    .tab-item {
        flex: 1;
        text-align: center;
        padding: 0.8rem;
        background: transparent;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .tab-item.active {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
    }
    
    /* Animaciones sutiles */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header { font-size: 2rem; }
        .metric-card { padding: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# ============= FUNCIONES DE UTILIDAD MEJORADAS =============

def show_notification(message, type="info"):
    """Muestra notificaciones estilizadas"""
    if type == "success":
        st.markdown(f'<div class="success-alert">✅ {message}</div>', unsafe_allow_html=True)
    elif type == "warning":
        st.markdown(f'<div class="warning-alert">⚠️ {message}</div>', unsafe_allow_html=True)
    elif type == "error":
        st.markdown(f'<div class="error-alert">❌ {message}</div>', unsafe_allow_html=True)
    else:
        st.info(f"ℹ️ {message}")

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Crea tarjetas de métricas personalizadas"""
    card_class = "metric-card"
    if delta:
        if "+" in str(delta):
            card_class += " metric-positive"
        elif "-" in str(delta):
            card_class += " metric-negative"
    
    delta_html = f"<small style='color: {'green' if '+' in str(delta) else 'red'}'>{delta}</small>" if delta else ""
    
    return f"""
    <div class="{card_class}">
        <h4 style="margin: 0; color: #333;">{title}</h4>
        <h2 style="margin: 0.5rem 0; color: #2c3e50;">{value}</h2>
        {delta_html}
    </div>
    """

# ============= INICIALIZACIÓN DEL ESTADO =============
def initialize_session_state():
    """Inicializa todas las variables de estado de sesión"""
    defaults = {
        'custom_stocks': {},
        'removed_default_stocks': set(),
        'stock_categories': {},
        'custom_categories': set(),
        'current_view': 'portfolio',  # portfolio, analysis, settings
        'show_tutorial': True,
        'last_calculation': None,
        'favorite_stocks': set(),
        'investment_presets': {}
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

initialize_session_state()

# ============= DATOS Y CONFIGURACIÓN =============
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

PREDEFINED_CATEGORIES = [
    "💻 Tecnología", "🏦 Fintech", "🪙 Criptomonedas", "📈 ETFs",
    "🚗 Automotriz", "💊 Salud", "🥤 Consumo", "🎬 Entretenimiento",
    "🛒 E-commerce", "🏭 Industrial", "🏠 Inmobiliario", "⚡ Energía",
    "📊 Índices", "💎 Materias Primas", "🌿 ESG/Sustentable"
]

# ============= FUNCIONES PRINCIPALES =============

@st.cache_data(ttl=3600)
def validate_stock_symbol(symbol):
    """Valida símbolo de acción con mejor manejo de errores"""
    try:
        stock = yf.Ticker(symbol.upper())
        info = stock.info
        if 'symbol' in info or 'shortName' in info:
            return True, info.get('shortName', symbol.upper())
        return False, None
    except Exception as e:
        return False, str(e)

@st.cache_data(ttl=3600)
def get_stock_data(symbol, start, end):
    """Obtiene datos históricos con manejo mejorado de errores"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(start=start, end=end, interval="1d")
        if len(data) == 0:
            return None
        return data
    except Exception as e:
        st.error(f"❌ Error obteniendo datos para {symbol}: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def get_stock_info(symbol):
    """Obtiene información de la empresa"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            'name': info.get('shortName', symbol),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'currency': info.get('currency', 'USD'),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 'N/A')
        }
    except:
        return {
            'name': symbol, 'sector': 'N/A', 'industry': 'N/A', 
            'currency': 'USD', 'market_cap': 0, 'pe_ratio': 'N/A'
        }

def calculate_investment_metrics(data, investment_amount):
    """Calcula métricas de inversión con análisis adicional"""
    if data is None or len(data) == 0 or investment_amount <= 0:
        return None
    
    start_price = data['Close'].iloc[0]
    end_price = data['Close'].iloc[-1]
    
    shares = investment_amount / start_price
    final_value = shares * end_price
    profit_loss = final_value - investment_amount
    profit_loss_pct = (profit_loss / investment_amount) * 100
    
    # Análisis adicional
    max_price = data['Close'].max()
    min_price = data['Close'].min()
    max_value = shares * max_price
    min_value = shares * min_price
    
    # Volatilidad y otros indicadores
    daily_returns = data['Close'].pct_change().dropna()
    volatility = daily_returns.std() * (252 ** 0.5) * 100 if len(daily_returns) > 0 else 0
    
    # Drawdown máximo
    rolling_max = data['Close'].expanding().max()
    drawdown = (data['Close'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100
    
    # Sharpe ratio simplificado (asumiendo risk-free rate = 0)
    sharpe_ratio = daily_returns.mean() / daily_returns.std() * (252 ** 0.5) if daily_returns.std() > 0 else 0
    
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
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'data': data
    }

def get_stock_category(symbol):
    """Obtiene categoría de una acción"""
    for name, data in DEFAULT_STOCKS.items():
        if data["symbol"] == symbol:
            return data["category"]
    
    for sym, data in st.session_state.custom_stocks.items():
        if sym == symbol:
            return data["category"]
    
    return "🔹 Otros"

# ============= INTERFAZ PRINCIPAL =============

# Header principal con estilo mejorado
st.markdown('<h1 class="main-header">📈 Analizador de Inversiones Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">🚀 Descubre el potencial de tus inversiones con análisis profesional y categorías personalizables</p>', unsafe_allow_html=True)

# ============= NAVEGACIÓN POR TABS =============
# Verificar si hay análisis completado para mostrar indicador
has_analysis = 'analysis_results' in st.session_state and st.session_state.analysis_results

# Crear títulos de tabs con indicadores
portfolio_tab = "🏠 Portfolio"
analysis_tab = "📊 Análisis" + (" ✅" if has_analysis else "")
config_tab = "⚙️ Configuración"
help_tab = "❓ Ayuda"

tab1, tab2, tab3, tab4 = st.tabs([portfolio_tab, analysis_tab, config_tab, help_tab])

with tab1:
    st.markdown("### 💼 Gestión de Portfolio")
    
    # Métricas rápidas del portfolio
    if st.session_state.custom_stocks or any(st.session_state.get(f"investment_{data['symbol']}", 0) > 0 for data in DEFAULT_STOCKS.values()):
        col1, col2, col3, col4 = st.columns(4)
        
        # Calcular totales rápidos
        total_stocks = len(st.session_state.custom_stocks) + len([s for s in DEFAULT_STOCKS.values() if s["symbol"] not in st.session_state.removed_default_stocks])
        custom_categories = len(st.session_state.custom_categories)
        
        with col1:
            st.markdown(create_metric_card("📊 Total Acciones", str(total_stocks)), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("🏷️ Categorías", str(custom_categories + len(set(data["category"] for data in DEFAULT_STOCKS.values())))), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("🌟 Personalizadas", str(len(st.session_state.custom_stocks))), unsafe_allow_html=True)
        with col4:
            # Calcular correctamente las inversiones activas incluyendo personalizadas
            active_investments = 0
            # Contar acciones por defecto con inversión
            for name, data in DEFAULT_STOCKS.items():
                if data["symbol"] not in st.session_state.removed_default_stocks:
                    if st.session_state.get(f"investment_{data['symbol']}", 0) > 0:
                        active_investments += 1
            
            # Contar acciones personalizadas con inversión  
            for symbol in st.session_state.custom_stocks.keys():
                if st.session_state.get(f"investment_{symbol}", 0) > 0:
                    active_investments += 1
                    
            st.markdown(create_metric_card("💰 Con Inversión", str(active_investments)), unsafe_allow_html=True)

with tab2:
    st.markdown("### 📈 Centro de Análisis")
    
    # Verificar si hay datos calculados
    if 'analysis_results' in st.session_state and st.session_state.analysis_results:
        results = st.session_state.analysis_results
        stock_infos = st.session_state.get('stock_infos', {})
        
        # Calcular totales
        total_investment = sum(metrics['investment'] for metrics in results.values())
        total_final_value = sum(metrics['final_value'] for metrics in results.values())
        total_profit_loss = total_final_value - total_investment
        total_profit_loss_pct = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
        
        # ============= MÉTRICAS PRINCIPALES =============
        st.markdown("## 📊 Resumen General")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card("💰 Inversión Total", f"${total_investment:,.2f}"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card("💎 Valor Final", f"${total_final_value:,.2f}"), unsafe_allow_html=True)
        
        with col3:
            delta_str = f"{total_profit_loss_pct:+.2f}%"
            st.markdown(create_metric_card("📈 Ganancia/Pérdida", f"${total_profit_loss:,.2f}", delta_str), unsafe_allow_html=True)
        
        with col4:
            roi_emoji = "🟢" if total_profit_loss_pct >= 0 else "🔴"
            st.markdown(create_metric_card(f"{roi_emoji} ROI Total", f"{total_profit_loss_pct:+.2f}%"), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ============= ANÁLISIS POR CATEGORÍAS =============
        st.markdown("## 🏷️ Análisis por Categorías")
        
        # Agrupar por categorías
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
        
        # Tabla de categorías
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
        
        # ============= TABLA DETALLADA =============
        st.markdown("## 📋 Análisis Detallado por Acción")
        
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
        
        # ============= GRÁFICOS =============
        
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
        
        # ============= ESTADÍSTICAS ADICIONALES =============
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
        
        analysis_start = st.session_state.get('analysis_start_date', 'N/A')
        analysis_end = st.session_state.get('analysis_end_date', 'N/A')
        
        st.info(f"""
        **📅 Período analizado:** {analysis_start} a {analysis_end}
        
        **🎯 Acciones analizadas:** {len(results)} inversiones activas
        
        **🏷️ Categorías únicas:** {len(category_analysis)} categorías diferentes
        
        **📊 Acciones personalizadas:** {len(st.session_state.custom_stocks)} agregadas por ti
        
        **🎨 Categorías personalizadas:** {len(st.session_state.custom_categories)} creadas por ti
        
        **💡 Metodología:** Se asume inversión completa en fecha de inicio y mantenimiento hasta fecha final.
        
        **📊 Fuente de datos:** Yahoo Finance
        
        **⚠️ Disclaimer:** Solo para fines educativos. No constituye asesoría financiera.
        """)
        
    else:
        # Vista cuando no hay análisis
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; margin: 2rem 0;'>
            <h2>📊 Listo para Analizar</h2>
            <p style='font-size: 1.2rem; color: #666; margin: 1rem 0;'>
                Configura tu portfolio y presiona el botón "🚀 CALCULAR ANÁLISIS" para ver resultados detallados aquí.
            </p>
            <div style='margin: 2rem 0;'>
                <div style='display: inline-block; margin: 0.5rem; padding: 1rem; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <h4>📈 Gráficos Interactivos</h4>
                    <p>Evolución de precios y comparativas</p>
                </div>
                <div style='display: inline-block; margin: 0.5rem; padding: 1rem; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <h4>📊 Métricas Avanzadas</h4>
                    <p>ROI, volatilidad, Sharpe ratio</p>
                </div>
                <div style='display: inline-block; margin: 0.5rem; padding: 1rem; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <h4>🏷️ Análisis por Categorías</h4>
                    <p>Rendimiento por sector</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Guía rápida
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🚀 Para empezar:
            
            1. **Ve a la pestaña "Portfolio"**
            2. **Configura tus inversiones** en el sidebar
            3. **Selecciona período de tiempo**
            4. **Presiona "🚀 CALCULAR ANÁLISIS"**
            5. **¡Los resultados aparecerán aquí!**
            """)
        
        with col2:
            st.markdown("""
            ### 💡 Consejos:
            
            - **Usa acciones variadas** para mejor análisis
            - **Prueba diferentes categorías** 
            - **Experimenta con períodos** de tiempo
            - **Guarda configuraciones** útiles como presets
            - **Compara resultados** entre categorías
            """)
    

with tab3:
    st.markdown("### ⚙️ Configuración Avanzada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Presets de Inversión")
        
        # Crear presets personalizados
        preset_name = st.text_input("Nombre del preset:", placeholder="Ej: Portfolio Conservador")
        if st.button("💾 Guardar Preset Actual") and preset_name:
            current_investments = {}
            for data in DEFAULT_STOCKS.values():
                if data["symbol"] not in st.session_state.removed_default_stocks:
                    amount = st.session_state.get(f"investment_{data['symbol']}", 0)
                    if amount > 0:
                        current_investments[data["symbol"]] = amount
            
            for symbol in st.session_state.custom_stocks.keys():
                amount = st.session_state.get(f"investment_{symbol}", 0)
                if amount > 0:
                    current_investments[symbol] = amount
            
            st.session_state.investment_presets[preset_name] = current_investments
            show_notification(f"Preset '{preset_name}' guardado exitosamente!", "success")
        
        # Mostrar presets guardados
        if st.session_state.investment_presets:
            st.markdown("**Presets guardados:**")
            for preset_name, investments in st.session_state.investment_presets.items():
                col_preset1, col_preset2 = st.columns([3, 1])
                with col_preset1:
                    st.write(f"📁 {preset_name} ({len(investments)} acciones)")
                with col_preset2:
                    if st.button("🔄", key=f"load_preset_{preset_name}", help="Cargar preset"):
                        # Limpiar inversiones actuales
                        for data in DEFAULT_STOCKS.values():
                            st.session_state[f"investment_{data['symbol']}"] = 0.0
                        for symbol in st.session_state.custom_stocks.keys():
                            st.session_state[f"investment_{symbol}"] = 0.0
                        
                        # Cargar preset
                        for symbol, amount in investments.items():
                            st.session_state[f"investment_{symbol}"] = amount
                        
                        show_notification(f"Preset '{preset_name}' cargado!", "success")
                        st.rerun()
    
    with col2:
        st.markdown("#### 🔧 Herramientas")
        
        col_clean1, col_clean2 = st.columns(2)
        with col_clean1:
            if st.button("🗑️ Limpiar Todo"):
                st.session_state.show_confirm_clean = True
        
        with col_clean2:
            if st.session_state.get('show_confirm_clean', False):
                if st.button("⚠️ Confirmar", type="secondary"):
                    # Limpiar todo
                    st.session_state.custom_stocks = {}
                    st.session_state.removed_default_stocks = set()
                    st.session_state.custom_categories = set()
                    st.session_state.investment_presets = {}
                    st.session_state.analysis_results = None
                    st.session_state.show_confirm_clean = False
                    
                    # Limpiar inversiones
                    for key in list(st.session_state.keys()):
                        if key.startswith('investment_'):
                            del st.session_state[key]
                    
                    show_notification("🗑️ Todo limpiado exitosamente!", "success")
                    st.rerun()
        
        if st.button("📤 Exportar Configuración"):
            config_data = {
                'custom_stocks': dict(st.session_state.custom_stocks),
                'custom_categories': list(st.session_state.custom_categories),
                'investment_presets': dict(st.session_state.investment_presets),
                'removed_default_stocks': list(st.session_state.removed_default_stocks)
            }
            import json
            config_json = json.dumps(config_data, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="💾 Descargar Configuración",
                data=config_json,
                file_name=f"portfolio_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

with tab4:
    st.markdown("### ❓ Centro de Ayuda")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🚀 Guía Rápida
        
        **1. Configurar Portfolio:**
        - Agrega acciones personalizadas
        - Crea categorías únicas
        - Establece montos de inversión
        
        **2. Análisis:**
        - Selecciona período de tiempo
        - Presiona "Calcular Inversiones"
        - Revisa resultados en "Análisis"
        
        **3. Gestión Avanzada:**
        - Crea presets de inversión
        - Exporta/importa configuraciones
        - Usa filtros por categoría
        """)
    
    with col2:
        st.markdown("""
        #### 💡 Tips y Trucos
        
        **🎯 Categorías Efectivas:**
        - Usa emojis para identificación rápida
        - Agrupa por sector o estrategia
        - Crea categorías por riesgo
        
        **📊 Análisis Profundo:**
        - Compara períodos diferentes
        - Usa métricas avanzadas
        - Analiza por categorías
        
        **⚙️ Productividad:**
        - Guarda presets frecuentes
        - Usa botones de acción rápida
        - Filtra por categorías
        """)
    
    # FAQ expandible
    with st.expander("❓ Preguntas Frecuentes"):
        st.markdown("""
        **¿Qué símbolos puedo usar?**
        Cualquier símbolo disponible en Yahoo Finance (acciones, ETFs, criptomonedas con -USD)
        
        **¿Cómo funcionan las categorías?**
        Las categorías te permiten agrupar y analizar acciones por temas específicos
        
        **¿Puedo guardar mi configuración?**
        Sí, usa los presets en la pestaña Configuración
        
        **¿Los datos son en tiempo real?**
        Los datos tienen un retraso de ~15 minutos, actualización automática cada hora
        """)

# ============= SIDEBAR MEJORADO =============
with st.sidebar:
    st.markdown("### 🎯 Panel de Control")
    
    # Navegación rápida
    st.markdown("#### 🚀 Acciones Rápidas")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💯 $100 Todo", use_container_width=True, help="Poner $100 en todas las acciones"):
            # Aplicar $100 a todas las acciones disponibles
            for name, data in DEFAULT_STOCKS.items():
                symbol = data["symbol"]
                if symbol not in st.session_state.removed_default_stocks:
                    st.session_state[f"investment_{symbol}"] = 100.0
            
            for symbol in st.session_state.custom_stocks.keys():
                st.session_state[f"investment_{symbol}"] = 100.0
            
            show_notification("💯 $100 aplicado a todas las acciones!", "success")
            st.rerun()
            
    with col2:
        if st.button("🔄 Reset", use_container_width=True, help="Limpiar todas las inversiones"):
            # Resetear todas las inversiones a $0
            for name, data in DEFAULT_STOCKS.items():
                symbol = data["symbol"]
                st.session_state[f"investment_{symbol}"] = 0.0
            
            for symbol in st.session_state.custom_stocks.keys():
                st.session_state[f"investment_{symbol}"] = 0.0
            
            show_notification("🔄 Todas las inversiones reseteadas!", "success")
            st.rerun()
    
    # Acción adicional centrada
    if st.button("🎲 Random", use_container_width=True, help="Montos aleatorios"):
        import random
        for name, data in DEFAULT_STOCKS.items():
            symbol = data["symbol"]
            if symbol not in st.session_state.removed_default_stocks:
                st.session_state[f"investment_{symbol}"] = float(random.randint(0, 20) * 50)
        
        for symbol in st.session_state.custom_stocks.keys():
            st.session_state[f"investment_{symbol}"] = float(random.randint(0, 20) * 50)
        
        show_notification("🎲 Montos aleatorios aplicados!", "success")
        st.rerun()
    
    st.markdown("---")
    
    # Selector de fechas mejorado
    st.markdown("#### 📅 Período de Análisis")
    
    # Presets de fechas
    date_preset = st.selectbox(
        "⚡ Presets rápidos:",
        ["Personalizado", "Último año", "Últimos 6 meses", "Últimos 3 meses", "YTD", "Últimos 5 años"]
    )
    
    if date_preset == "Último año":
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now() - timedelta(days=1)
    elif date_preset == "Últimos 6 meses":
        start_date = datetime.now() - timedelta(days=180)
        end_date = datetime.now() - timedelta(days=1)
    elif date_preset == "Últimos 3 meses":
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now() - timedelta(days=1)
    elif date_preset == "YTD":
        start_date = datetime(datetime.now().year, 1, 1)
        end_date = datetime.now() - timedelta(days=1)
    elif date_preset == "Últimos 5 años":
        start_date = datetime.now() - timedelta(days=365*5)
        end_date = datetime.now() - timedelta(days=1)
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Inicio",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now() - timedelta(days=1)
            )
        with col2:
            end_date = st.date_input(
                "Final",
                value=datetime.now() - timedelta(days=1),
                max_value=datetime.now()
            )
    
    st.markdown("---")
    
    # Gestión de acciones con interfaz mejorada
    st.markdown("#### ➕ Agregar Acción")
    
    with st.expander("🎯 Nueva Acción", expanded=False):
        new_symbol = st.text_input(
            "Símbolo:",
            placeholder="Ej: TSLA, BTC-USD",
            key="new_symbol_sidebar"
        ).upper()
        
        # Categorías en un selector más limpio
        all_categories = sorted(list(set(PREDEFINED_CATEGORIES + list(st.session_state.custom_categories))))
        selected_category = st.selectbox(
            "Categoría:",
            ["Seleccionar..."] + all_categories + ["➕ Crear nueva..."],
            key="category_sidebar"
        )
        
        if selected_category == "➕ Crear nueva...":
            new_category = st.text_input(
                "Nueva categoría:",
                placeholder="🎮 Gaming, 🌍 Global",
                key="new_category_sidebar"
            )
            if new_category:
                selected_category = new_category
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Validar", key="validate_sidebar"):
                if new_symbol and selected_category and selected_category not in ["Seleccionar...", "➕ Crear nueva..."]:
                    is_valid, name_or_error = validate_stock_symbol(new_symbol)
                    if is_valid:
                        st.session_state.custom_stocks[new_symbol] = {
                            "name": name_or_error,
                            "category": selected_category
                        }
                        if selected_category not in PREDEFINED_CATEGORIES:
                            st.session_state.custom_categories.add(selected_category)
                        show_notification(f"✅ {new_symbol} agregado!", "success")
                        st.rerun()
                    else:
                        show_notification(f"❌ {new_symbol} no válido", "error")
                else:
                    show_notification("⚠️ Completa todos los campos", "warning")
    
    # Mostrar resumen del portfolio
    if st.session_state.custom_stocks:
        st.markdown("#### 🌟 Acciones Personalizadas")
        for symbol, data in st.session_state.custom_stocks.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{symbol}**")
                st.caption(f"{data['category']}")
            with col2:
                if st.button("🗑️", key=f"del_{symbol}", help="Eliminar"):
                    del st.session_state.custom_stocks[symbol]
                    if f"investment_{symbol}" in st.session_state:
                        del st.session_state[f"investment_{symbol}"]
                    st.rerun()
    
    st.markdown("---")
    
    # Configuración de inversiones con interface mejorada
    st.markdown("#### 💰 Configurar Inversiones")
    
    # Combinar todas las acciones
    ALL_STOCKS = {}
    for name, data in DEFAULT_STOCKS.items():
        symbol = data["symbol"]
        if symbol not in st.session_state.removed_default_stocks:
            ALL_STOCKS[name] = data
    
    for symbol, data in st.session_state.custom_stocks.items():
        ALL_STOCKS[data["name"]] = {
            "symbol": symbol,
            "category": data["category"]
        }
    
    # Filtro por categoría
    if ALL_STOCKS:
        categories_in_use = sorted(list(set(data["category"] for data in ALL_STOCKS.values())))
        category_filter = st.selectbox(
            "🏷️ Filtrar por:",
            ["Todas"] + categories_in_use,
            key="category_filter_sidebar"
        )
        
        investments = {}
        
        # Mostrar acciones filtradas
        for name, data in ALL_STOCKS.items():
            symbol = data["symbol"]
            category = data["category"]
            
            if category_filter != "Todas" and category != category_filter:
                continue
            
            current_value = st.session_state.get(f"investment_{symbol}", 0.0)
            
            # Input de inversión más compacto
            investments[symbol] = st.number_input(
                f"💰 {symbol}",
                min_value=0.0,
                value=current_value,
                step=50.0,
                key=f"investment_{symbol}",
                help=f"{name} | {category}"
            )
    
    # Resumen de inversión
    if 'investments' in locals():
        total_investment = sum(investments.values())
        if total_investment > 0:
            st.markdown("#### 📊 Resumen")
            st.success(f"💰 Total: ${total_investment:,.2f}")
            active_count = sum(1 for v in investments.values() if v > 0)
            st.info(f"📈 Activas: {active_count}")
    
    st.markdown("---")
    
    # Botón de cálculo mejorado
    if st.button("🚀 CALCULAR ANÁLISIS", type="primary", use_container_width=True):
        if 'investments' in locals() and any(v > 0 for v in investments.values()):
            active_investments = {k: v for k, v in investments.items() if v > 0}
            
            if start_date >= end_date:
                show_notification("❌ La fecha de inicio debe ser anterior a la fecha final", "error")
            else:
                try:
                    # Mostrar progreso inmediatamente
                    progress_placeholder = st.empty()
                    with progress_placeholder.container():
                        with st.spinner("🔄 Analizando inversiones..."):
                            st.write(f"📊 Procesando {len(active_investments)} inversiones...")
                            
                            # Obtener datos y calcular métricas
                            results = {}
                            stock_infos = {}
                            
                            for i, (symbol, amount) in enumerate(active_investments.items()):
                                st.write(f"📈 Analizando {symbol}... ({i+1}/{len(active_investments)})")
                                
                                data = get_stock_data(symbol, start_date, end_date)
                                
                                if data is not None:
                                    stock_info = get_stock_info(symbol)
                                    stock_infos[symbol] = stock_info
                                    
                                    metrics = calculate_investment_metrics(data, amount)
                                    
                                    if metrics:
                                        # Agregar información de categoría
                                        metrics['category'] = get_stock_category(symbol)
                                        results[symbol] = metrics
                                else:
                                    st.warning(f"⚠️ No se encontraron datos para {symbol}")
                    
                    # Limpiar el placeholder de progreso
                    progress_placeholder.empty()
                    
                    if results:
                        # Guardar resultados inmediatamente en session state
                        st.session_state.analysis_results = results
                        st.session_state.stock_infos = stock_infos
                        st.session_state.analysis_start_date = start_date.strftime('%d/%m/%Y')
                        st.session_state.analysis_end_date = end_date.strftime('%d/%m/%Y')
                        st.session_state.last_calculation = "completed"
                        
                        # Mostrar notificación de éxito
                        show_notification("✅ Análisis completado exitosamente!", "success")
                        
                        # Forzar actualización inmediata
                        st.rerun()
                        
                    else:
                        show_notification("❌ No se pudieron obtener datos para ninguna acción", "error")
                        
                except Exception as e:
                    show_notification(f"❌ Error durante el análisis: {str(e)}", "error")
        else:
            show_notification("⚠️ Configura al menos una inversión mayor a $0", "warning")

# ============= FOOTER MEJORADO =============
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-top: 2rem;'>
    <h4>📈 Analizador de Inversiones Pro v4.0</h4>
    <p style='margin: 0.5rem 0;'>
        🎯 Interfaz mejorada | ⚡ Navegación intuitiva | 📊 Análisis profesional
    </p>
    <p style='opacity: 0.8; font-size: 0.9rem; margin: 0;'>
        Desarrollado con ❤️ usando Streamlit | Datos de Yahoo Finance | Solo fines educativos
    </p>
</div>
""", unsafe_allow_html=True)