# 🚀 Cómo Publicar el Dashboard EAUI 2026

Tu dashboard Streamlit está listo. Aquí tienes 3 opciones para publicarlo:

## Opción 1: Streamlit Cloud ⭐ (Recomendado — Gratis)

**Ventajas:**
- Totalmente gratis
- Publicación en 1 clic
- Ideal para Streamlit
- Actualizaciones automáticas desde GitHub

**Pasos:**

### 1.1 Preparar tu repositorio
```bash
# Asegúrate de que estos archivos estén en GitHub:
- app.py
- requirements.txt
- data/2026_procesado.csv
- .streamlit/config.toml (opcional)
```

### 1.2 Crear cuenta en Streamlit Cloud
1. Ve a [streamlit.io/cloud](https://streamlit.io/cloud)
2. Haz clic en "Sign up"
3. Inicia sesión con tu cuenta de GitHub
4. Autoriza Streamlit a acceder a tus repos

### 1.3 Desplegar tu app
1. Haz clic en "New app"
2. Selecciona:
   - **Repository:** `tu-usuario/eaui_subtel`
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. Haz clic en "Deploy"

¡Listo! Tu dashboard estará disponible en:
```
https://eaui-subtel.streamlit.app/
```

### 1.4 Actualizar el dashboard
Cada vez que hagas push a GitHub, Streamlit automáticamente redespliega tu app.

---

## Opción 2: Heroku (Requiere pago)

Si necesitas control más avanzado, puedes usar Heroku (desde $7/mes).

**Pasos:**
1. Crea una cuenta en [heroku.com](https://heroku.com)
2. Instala Heroku CLI: `brew install heroku` (macOS)
3. Crea un archivo `Procfile`:
```
web: streamlit run --server.port=$PORT --server.address=0.0.0.0 app.py
```
4. Despliega:
```bash
heroku create nombre-app
git push heroku main
```

---

## Opción 3: HTML Estático en Vercel/Netlify

**Si quieres algo realmente estático** para Vercel o Netlify (sin servidor Python):

Puedo convertir el dashboard a un **HTML interactivo autocontenido** que funcione en Vercel/Netlify. 
Ventajas:
- No requiere servidor
- Hosting completamente gratis en Vercel/Netlify
- Puedes comprimir los datos en JSON dentro del HTML

¿Quieres que lo convierta?

---

## Ejecutar Localmente (para probar)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar el app
streamlit run app.py

# 3. Se abrirá en http://localhost:8501
```

---

## Notas Importantes

### 📂 Estructura de carpetas requerida
```
eaui_subtel/
├── app.py                    ← Tu dashboard
├── requirements.txt          ← Dependencias
├── data/
│   └── 2026_procesado.csv   ← Datos OBLIGATORIOS
└── .streamlit/
    └── config.toml          ← Configuración (opcional)
```

### 🔒 Datos Sensibles
- Asegúrate de que `data/2026_procesado.csv` esté en `.gitignore` si contiene datos sensibles
- Streamlit Cloud acepta archivos hasta 100MB

### ⚡ Optimización
Si el dashboard es lento:
1. Añade `@st.cache_data` a funciones de cálculo intenso
2. Usa archivos `.parquet` en lugar de CSV
3. Pre-calcula agregaciones

### 🎨 Personalización
Modifica `.streamlit/config.toml` para cambiar colores, fonts, etc.

---

## ¿Preguntas?

- **Documentación Streamlit:** https://docs.streamlit.io
- **Streamlit Cloud Docs:** https://docs.streamlit.io/deploy/streamlit-cloud
- **Status:** https://status.streamlit.io

---

**¡Felicidades! Tu dashboard está listo para publicarse.** 🎉
