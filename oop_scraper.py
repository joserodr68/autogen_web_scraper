import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import logging
import hashlib
import os

Base = declarative_base()

class Quote(Base):
    __tablename__ = 'quotes'

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    author = Column(String(100))
    tags = Column(String(200))
    about_author = Column(Text)

class Quote_internet(Base):
    __tablename__ = 'quotes_internet'

    id = Column(Integer, primary_key=True)
    text = Column(Text,  unique=True)
    author = Column(String(100))
    tags = Column(String(200))
    source =  Column(String(300))

class QuoteScraper:
    def __init__(self, url, db_name='quotes.db'):
        self.url = url
        self.db_name = db_name
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.script_dir, db_name)
        self.excel_path = os.path.join(self.script_dir, "quotes_db.xlsx")
        self.setup_database()
        self.logger = get_logger()

    def setup_database(self):
        db_path = os.path.abspath(self.db_name)
        self.engine = create_engine(f'sqlite:///{db_path}', echo=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def scrape_quotes(self):
        quotes_data = []
        next_url = self.url

        while next_url:
            response = requests.get(next_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            quote_elements = soup.find_all(class_='quote')
            for quote in quote_elements:
                text = quote.find(class_='text').get_text()
                author = quote.find(class_='author').get_text()
                tags = ", ".join([tag.get_text() for tag in quote.find_all(class_='tag')])

                author_link = quote.find('a')['href']
                author_url = f"http://quotes.toscrape.com{author_link}"
                about_author = self.scrape_author(author_url)

                quotes_data.append({
                    "text": text,
                    "author": author,
                    "tags": tags,
                    "about_author": about_author
                })

            next_button = soup.find(class_='next')
            next_url = f"http://quotes.toscrape.com{next_button.find('a')['href']}" if next_button else None

        return pd.DataFrame(quotes_data)

    def scrape_author(self, author_url):
        response = requests.get(author_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        about_author = soup.find(class_='author-description').get_text()
        return about_author

    def store_data(self, df):
        session = self.Session()
        try:
            for _, row in df.iterrows():
                quote = Quote(
                    text=row['text'],
                    author=row['author'],
                    tags=row['tags'],
                    about_author=row['about_author']
                )
                session.add(quote)
            session.commit()
        except Exception as e:
            print(f"An error occurred while storing data: {e}")
            session.rollback()
        finally:
            session.close()

    def run(self):
        print("Comenzando scraping...")
        self.logger.info ("Scraping iniciado.")
        df = self.scrape_quotes()
        print(f"Scraping completado. Citas totales recopiladas: {len(df)}")
        self.logger.info (f"Scraping completado. Citas totales recopiladas: {len(df)}")

        print("Almacenando datos en BBDD...")
        self.logger.info ("Almacenando datos en BBDD.")
        self.store_data(df)
        print("Almacenamiento de datos finalizado.")
        self.logger.info ("Almacenamiento de datos finalizado.")

        df.to_excel(self.excel_path, index=False)
        print(f"Datos almacenados en Excel: {self.excel_path}")
        self.logger.info (f"Datos almacenados en Excel: {self.excel_path}")

        print("Proceso de Scraping finalizado.")
        self.logger.info ("Proceso de Scraping finalizado.")

        return df

def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler('scraper.log')
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger

def hash_string(input_string):
    return hashlib.md5(input_string.encode()).hexdigest()

if __name__ == "__main__":
    scraper = QuoteScraper("https://quotes.toscrape.com/")
    result_df = scraper.run()

    print("\nDataset Statistics:")
    print(f"Total Quotes: {len(result_df)}")
    print(f"Unique Authors: {result_df['author'].nunique()}")
    print(f"Total Tags: {result_df['tags'].str.split(', ').explode().nunique()}")

    db_path = os.path.abspath(scraper.db_name)
    if os.path.exists(db_path):
        print(f"\nBase de datos creada en: {db_path}")
        print(f"Tamaño de la Base de Datos: {os.path.getsize(db_path)} bytes")
    else:
        print("\nWarning: Database file was not created successfully.")
