# autogen_web_scraper

## Descripción
Este proyecto es un scraper de frases célebres que extrae información de la web https://quotes.toscrape.com. Utiliza Beautifulsoup para navegar por el sitio web y recopila frases, autores, etiquetas y descripciones de autores, almacenándolos en una base de datos SQLite y un archivo Excel.
Proporciona recomendaciones sobre las frases del scraping básico mediante IA
Añade nuevas frases mediante búsqueda global en Internet usando Agentes (Autogen de Microsoft)
Front End basado en Streamlit
La aplicación ha sido dockerizada (Dockerfile) y desplegada en Azure mediante servicio de contenedores.

## Características Principales
- Scraping automatizado de frases célebres.
- Almacenamiento de datos en SQLite y Excel.
- Manejo de múltiples páginas y navegación automática.
- Registro de actividades mediante logging.
- Tests del scraper realizados con pytest disponibles

## Requisitos
- Python 3.11
- Beautifulsoup
- SQLAlchemy
- Pandas
- Streamlit
- Docker
- Pyautogen
- Langchain

## Instalación
1. Clona este repositorio:
   ```
   git clone https://github.com/joserodr68/autogen_web_scraper

    ```
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso
Para ejecutar el scraper:

```
streamlit run gui_scraper.py
```

## Estructura del Proyecto
- `QuoteScraper`: Clase principal que maneja el proceso de scraping.
- `Quote` y `Quote_internet`: Modelos de datos para SQLAlchemy.
- `get_logger()`: Función para configurar el sistema de logging.
- `hash_string()`: Función de utilidad para hashear strings.

## Funcionalidades Detalladas
1. **Scraping de Frases**
   - Extrae texto de la frase, autor, etiquetas y descripción del autor.
   - Navega automáticamente por todas las páginas disponibles.

2. **Almacenamiento de Datos**
   - Guarda los datos en una base de datos SQLite.
   - Exporta los datos a un archivo Excel.

3. **Logging**
   - Registra eventos importantes durante el proceso de scraping.

## Notas de Desarrollo
- El scraper utiliza BeautifulSoup.
- Se implementa un manejo básico de errores y logging para facilitar el debug.
- La clase `QuoteScraper` está diseñada para ser fácilmente extensible.


# Interfaz Gráfico

## Descripción
Esta aplicación es un scraper de frases célebres con funcionalidades avanzadas de búsqueda y recomendación utilizando inteligencia artificial. Está diseñada para recopilar, almacenar y presentar frases inspiradoras de diversas fuentes.

## Funcionalidades

### 1. Autenticación
- La aplicación requiere autenticación para acceder a sus funciones.
- Los usuarios deben introducir un nombre de usuario (admin)  y contraseña válidos.

### 2. Scraping Básico
- Extrae frases de la web https://quotes.toscrape.com
- Almacena las frases en una base de datos SQLite local.
- Permite descargar las frases en formato CSV.

### 3. Recomendador de Frases con IA
- Utiliza inteligencia artificial para recomendar frases basadas en la entrada del usuario.
- El usuario puede especificar una impresión o sentimiento deseado.
- Permite seleccionar el número de frases a recomendar.

### 4. Búsqueda Global en Internet con IA
- Realiza búsquedas de frases en internet basadas en un tema o sentimiento proporcionado por el usuario.
- Utiliza Agentes Inteligentes Autogen.
- Almacena las frases encontradas en una base de datos SQLite.
- Ofrece la opción de visualizar el contenido de la base de datos.

## Cómo Utilizar

1. **Inicio de Sesión**
   - Introduce tu nombre de usuario y contraseña en la pantalla de inicio.

2. **Navegación**
   - Utiliza la barra lateral para seleccionar entre las diferentes funcionalidades:
     - Scraping Básico
     - Recomendador - IA
     - Búsqueda Global - IA

3. **Scraping Básico**
   - Pulsa el botón "Iniciar Scraping" para comenzar la extracción de frases.
   - Visualiza las frases extraídas y descárgalas en formato CSV si lo deseas.

4. **Recomendador de Frases**
   - Introduce la impresión o sentimiento deseado en el campo de texto.
   - Selecciona el número de frases que quieres obtener.
   - Pulsa "Lanzar Recomendador" para ver las frases recomendadas.

5. **Búsqueda Global en Internet**
   - Introduce el tema o sentimiento sobre el que quieres buscar frases.
   - Indica el número de frases que deseas obtener (máximo 10).
   - Pulsa "Lanzar Buscador" para iniciar la búsqueda.
   - Opcionalmente, puedes visualizar el contenido de la base de datos pulsando el botón correspondiente.


## Notas
- Asegúrate de tener una conexión a internet estable para las funciones de búsqueda global y recomendación.
- La aplicación utiliza bases de datos SQLite locales para almacenar las frases.
