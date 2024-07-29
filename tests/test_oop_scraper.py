
#pytest test_oop_scraper.py -v


import pytest
from unittest.mock import Mock, patch
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oop_scraper import QuoteScraper, Quote, Base, get_logger, hash_string
import logging

@pytest.fixture
def mock_scraper():
    with patch('oop_scraper.requests.get'), patch('oop_scraper.BeautifulSoup'):
        scraper = QuoteScraper("https://quotes.toscrape.com/", db_name='test.db')
        yield scraper

@pytest.fixture
def mock_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_setup_database(mock_scraper):
    assert mock_scraper.engine is not None
    assert mock_scraper.Session is not None

def test_scrape_quotes(mock_scraper):
    mock_scraper.scrape_author = Mock(return_value="Mock author description")
    with patch('oop_scraper.BeautifulSoup') as mock_bs:
        mock_quote = Mock()
        mock_quote.find.side_effect = [
            Mock(get_text=Mock(return_value="Quote 1")),
            Mock(get_text=Mock(return_value="Author 1")),
            Mock(__getitem__=Mock(return_value="/author/link"))
        ]
        mock_quote.find_all.return_value = [Mock(get_text=Mock(return_value="tag1")), Mock(get_text=Mock(return_value="tag2"))]
        mock_bs.return_value.find_all.return_value = [mock_quote]
        mock_bs.return_value.find.return_value = None
        
        df = mock_scraper.scrape_quotes()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]['text'] == "Quote 1"
        assert df.iloc[0]['author'] == "Author 1"
        assert df.iloc[0]['tags'] == "tag1, tag2"

def test_scrape_author(mock_scraper):
    with patch('oop_scraper.BeautifulSoup') as mock_bs:
        mock_bs.return_value.find.return_value.get_text.return_value = "Author description"
        result = mock_scraper.scrape_author("https://example.com")
        assert result == "Author description"

def test_store_data(mock_scraper, mock_session):
    df = pd.DataFrame({
        'text': ['Quote 1'],
        'author': ['Author 1'],
        'tags': ['tag1, tag2'],
        'about_author': ['About author 1']
    })
    
    with patch.object(mock_scraper, 'Session', return_value=mock_session):
        mock_scraper.store_data(df)
    
    stored_quote = mock_session.query(Quote).first()
    assert stored_quote.text == 'Quote 1'
    assert stored_quote.author == 'Author 1'

@patch('oop_scraper.pd.DataFrame.to_excel')
def test_run(mock_to_excel, mock_scraper):
    mock_scraper.scrape_quotes = Mock(return_value=pd.DataFrame({
        'text': ['Quote 1'],
        'author': ['Author 1'],
        'tags': ['tag1, tag2'],
        'about_author': ['About author 1']
    }))
    mock_scraper.store_data = Mock()
    
    result_df = mock_scraper.run()
    
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 1
    mock_scraper.scrape_quotes.assert_called_once()
    mock_scraper.store_data.assert_called_once()
    mock_to_excel.assert_called_once()

def test_get_logger():
    logger = get_logger()
    assert logger.level == 20  # INFO level
    assert len(logger.handlers) >= 2  # At least StreamHandler and FileHandler
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)
    assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)

def test_hash_string():
    result = hash_string("test")
    assert result == "098f6bcd4621d373cade4e832627b4f6"

if __name__ == "__main__":
    pytest.main()