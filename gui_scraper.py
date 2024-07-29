import os
import re
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy import exc
from oop_scraper import *  # Contiene la clase QuoteScraper y funcines auxiliares
from ai_recommender import *
from autogen_agents import *

def load_quotes_from_db(engine):
    query = "SELECT * FROM quotes"
    df = pd.read_sql_query(query, engine)
    return df


def main():

    # Load environment variables
    load_dotenv()
    users = {
    "admin": os.getenv("ADMIN_PASSWORD"),
    }

    st.markdown("""
        <style>
            .quote-box {
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
                background-color: #f9f9f9;
            }
        </style>
        """, unsafe_allow_html=True)


    st.title("App de Frases Célebres")

    # Session state to keep track of login status
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Login Form
    if not st.session_state.logged_in:
        with st.form("login_form"):
            st.subheader("Autenticación")
            username = st.text_input("Usuario")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")

            if submit_button:
                
                if username in users  and users["admin"] == hash_string(password):
                    st.session_state.logged_in = True
                    st.success("Autenticación realizada con éxito")
                    st.rerun()
                else:
                    st.error("Usuario o password incorrectos")

    # Interfaz de Scraping
    if st.session_state.logged_in:
        st.sidebar.title("Opciones de Scraping")
        option = st.sidebar.radio("Elige una opción: ", ("Scraping Básico", "Recomendador - IA",  "Búsqueda Global - IA"))

        if option == "Scraping Básico":
            st.subheader("Scraper Básico de: https://quotes.toscrape.com")

            with st.form("scraper_form"):
                st.write("Pulsa el botón para realizar el Scraping.")
                start_scraping = st.form_submit_button("Iniciar Scraping")

            if start_scraping:
                db_path = "sqlite:///quotes.db"
                engine = create_engine(db_path)

                if os.path.exists("quotes.db"):
                    st.info("BBDD existente. Cargando quotes.")
                    result_df = load_quotes_from_db(engine)
                else:
                    st.info("No hay BBDD. Iniciando scraping.")
                    # Crea una barra de progreso
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Ejecutar el scraper
                    scraper = QuoteScraper("https://quotes.toscrape.com/")

                    # Actualizar la barra de progreso (simplificada)
                    status_text.text("Scraping en proceso...")
                    progress_bar.progress(50)

                    result_df = scraper.run()

                    # Actualizar progreso
                    progress_bar.progress(100)
                    status_text.text("Scraping completado!")

                    
                # Mostrar las frases
                st.subheader("Frases Disponibles")
                st.dataframe(result_df, hide_index=True)

                # Descarga en csv de las frases encontradas
                st.download_button(
                    label="Descargar en .CSV",
                    data=result_df.to_csv(index=False).encode('utf-8'),
                    file_name="scraped_quotes.csv",
                    mime="text/csv",
                )

        elif option == "Recomendador - IA":
            st.subheader("Recomendador de Frases")
            with st.form("advanced_scraper_form"):
                user_query = st.text_area("**Introduzca la impresión a dar o sentimiento:**", height=50)
                n_quotes = st.number_input("Número de Frases", min_value=1, step=1)
                start_advanced_scraping = st.form_submit_button("Lanzar Recomendador")

            if start_advanced_scraping:
                db_path = "sqlite:///quotes.db"
                engine = create_engine(db_path)

                if os.path.exists("quotes.db"):
                    result_df = load_quotes_from_db(engine)
                else:
                    st.error("Database file not found. Please run the basic scraper first.")
                    return
                
                df_selected = result_df[['text', 'tags', 'author']].copy()
                df_selected['text'] = df_selected['text'].str.slice(0, 80)

                response = dame_quotes(user_query, n_quotes, df_selected)

                # Muestra los resultados
                st.subheader("Frases Seleccionadas:")
                with st.container():
                    # Parsing
                    split_response = re.split(r'(\d+\.\s*")', response)
                    
                    
                    if split_response[0] == '':
                        split_response.pop(0)
                    
                    formatted_response = []
                    for i in range(0, len(split_response), 2):
                        if i+1 < len(split_response):
                            formatted_response.append(split_response[i] + split_response[i+1])
                        else:
                            formatted_response.append(split_response[i])
                    
                    # Construye la respuesta en el formato adecuado
                    final_response = "<br><br>".join(formatted_response)
                    
                    st.markdown(f"""
                    <div class="quote-box">
                        {final_response}
                    </div>
                    """, unsafe_allow_html=True)
                                


        elif option == "Búsqueda Global - IA":

            DB_PATH = "quotes_internet.db"
            DB_URL = f"sqlite:///{DB_PATH}"

            st.subheader("Búsqueda Global en Internet")
            with st.form("internet_search_form"):
                user_query = st.text_area("**Introduzca el tema o sentimiento:**", height=50)
                t_query = user_query[:50]
                n_quotes = st.number_input("Número de frases", min_value=1, max_value=10, step=1)
                if n_quotes > 10:
                    n_quotes=10
                    st.warning("El número máximo de frases es 10.")
                start_advanced_search = st.form_submit_button("Lanzar Buscador")

            if start_advanced_search:

                
                
                # Nos aseguramos que exista la base de datos de búsquedas en Internet
                if not os.path.exists(DB_PATH):
                    temp_engine = create_engine(DB_URL)
                    Base.metadata.create_all(temp_engine)
                    temp_engine.dispose()

                # Create engine and session
                engine1 = create_engine(DB_URL)
                Base.metadata.create_all(engine1)
                Session = sessionmaker(bind=engine1)
                session = Session()

                try:

                    quotes = get_quotes(t_query)
                    parsed_quotes = parse_quotes(quotes)

                    # Crear y mostrar la df de quotes . 
                    quotes_df = create_quotes_dataframe(parsed_quotes)

                    st.dataframe(quotes_df.head(n_quotes), hide_index=True)
                    
                    # Almacenar las frases
                    for _, row in quotes_df.iterrows():
                        quote = Quote_internet(
                            text=row['text'],
                            author=row['author'],
                            tags=row['tag'],
                            source=row['source']
                        )
                        session.add(quote)
                    
        
                    session.commit()
                    st.success("Quotes successfully stored in the database.")
                
                except exc.SQLAlchemyError as e:
                    st.error(f"Error de Base de datos: {str(e)}")
                    session.rollback()
                except Exception as e:
                    st.error(f"Error inesperado: {str(e)}")
                    session.rollback()
                finally:
                    session.close()
                    engine1.dispose()

            
            if st.button("Mostrar la Base de Datos"):
                engine = create_engine(DB_URL)
                try:
                    with engine.connect() as connection:
                        df = pd.read_sql_table("quotes_internet", connection)
                    st.dataframe(df, hide_index=True)
                except Exception as e:
                    st.error(f"Error cargando contenido de la BBDD: {str(e)}")
                finally:
                    engine.dispose()


if __name__ == "__main__":
    main()

