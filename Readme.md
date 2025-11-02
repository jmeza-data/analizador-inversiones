# 📈 Analizador de Inversiones

Una aplicación web interactiva para analizar inversiones en acciones con sistema de categorías personalizables.

## 🚀 Características

- **Sistema de categorías personalizables**: Organiza tus acciones por sectores, tipos de inversión, o categorías personalizadas
- **15 categorías predefinidas**: Tecnología, Fintech, Criptomonedas, ETFs, y más
- **Acciones personalizables**: Agrega cualquier acción disponible en Yahoo Finance
- **Análisis completo**: Gráficos interactivos, métricas de rendimiento, y estadísticas detalladas
- **Filtros inteligentes**: Analiza por categoría específica o todas juntas

## 📊 Funcionalidades

### ✨ Gestión de Inversiones
- Agregar acciones personalizadas con validación automática
- Asignar categorías predefinidas o crear nuevas categorías
- Filtrar acciones por categoría para análisis específicos
- Botones de acción rápida ($100 Todo, Reset, Random)

### 📈 Análisis Avanzado
- **Resumen general**: Inversión total, valor final, ROI
- **Análisis por categorías**: Rendimiento de cada categoría
- **Tabla detallada**: Métricas individuales por acción
- **Gráficos interactivos**: Evolución de precios, distribución, comparativas
- **Estadísticas**: Mejor/peor inversión, mejor categoría, volatilidad

### 🎯 Acciones Incluidas por Defecto
- **💻 Tecnología**: AAPL, GOOGL, META, MSFT, NVDA
- **🏦 Fintech**: NU, PYPL
- **🛒 E-commerce**: AMZN
- **🚗 Automotriz**: TSLA
- **🎬 Entretenimiento**: NFLX
- **🥤 Consumo**: KO
- **💊 Salud**: JNJ

## 🛠️ Instalación Local

```bash
# Clonar repositorio
git clone [tu-repositorio]
cd analizador-inversiones

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

## ☁️ Deploy en Streamlit Cloud

### Paso 1: Preparar Repositorio
1. Sube `app.py` y `requirements.txt` a tu repositorio de GitHub
2. Asegúrate de que el archivo principal se llame `app.py`

### Paso 2: Deploy en Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona tu repositorio
4. Especifica el archivo principal: `app.py`
5. ¡Deploy automático!

## 📁 Estructura del Proyecto

```
analizador-inversiones/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
└── README.md          # Documentación
```

## 🔧 Dependencias

- `streamlit`: Framework de la aplicación web
- `yfinance`: Obtención de datos financieros
- `pandas`: Manipulación de datos
- `plotly`: Gráficos interactivos
- `numpy`: Operaciones numéricas

## 💡 Ejemplos de Uso

### Portfolio Tech Diversificado
```
💻 Tecnología: AAPL $1000, MSFT $800
🏦 Fintech: NU $500, PYPL $400  
🪙 Crypto: BTC-USD $600, ETH-USD $400
```

### Portfolio por Sectores
```
🎮 Gaming: RBLX $500, EA $300
🌿 ESG: TSLA $800, NEE $600
🏠 REITs: VNQ $400, SPG $300
```

### Portfolio Global
```
🌍 Internacionales: BABA $700, TSM $500
💻 US Tech: GOOGL $800, META $600
📈 ETFs: SPY $1000, QQQ $800
```

## 🏷️ Categorías Predefinidas

- 💻 Tecnología
- 🏦 Fintech
- 🪙 Criptomonedas
- 📈 ETFs
- 🚗 Automotriz
- 💊 Salud
- 🥤 Consumo
- 🎬 Entretenimiento
- 🛒 E-commerce
- 🏭 Industrial
- 🏠 Inmobiliario
- ⚡ Energía
- 📊 Índices
- 💎 Materias Primas
- 🌿 ESG/Sustentable

## ⚠️ Disclaimer

Esta aplicación es solo para fines educativos y de análisis. No constituye asesoría financiera. Las inversiones conllevan riesgos y los rendimientos pasados no garantizan resultados futuros.

## 📞 Soporte

Los datos son obtenidos de Yahoo Finance y pueden tener un retraso de hasta 15 minutos. Para soporte técnico, revisa la documentación de Streamlit.

---

Desarrollado con ❤️ usando Streamlit | Datos en tiempo real de Yahoo Finance