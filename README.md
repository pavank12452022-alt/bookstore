# Bookstore (Book Scraper & Web App)

A Flask web application that scrapes book data from [Books to Scrape](https://books.toscrape.com/), stores it in an SQLite database, and provides a web interface to search and filter books.

## Features

- **Web Scraping**: Scrapes title, star rating, price, genre, and cover image URL using BeautifulSoup and Requests.
- **Database**: Automatically populates and manages book records in an SQLite database via Flask-SQLAlchemy.
- **Search & Filter**: 
  - Search books by title keyword.
  - Filter by genre, maximum price, and star rating.

## Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy, SQLite
- **Scraper**: BeautifulSoup4, Requests
- **Frontend**: HTML5, Bootstrap 5

## Project Structure

```
bookstore/
├── scrapping.py        # Flask app & scraper logic
├── templates/
│   └── base.html       # Web UI layout & filter forms
└── instance/
    └── books.db        # SQLite database
```

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pavank12452022-alt/bookstore.git
   cd bookstore
   ```

2. **Install dependencies**:
   ```bash
   pip install Flask Flask-SQLAlchemy beautifulsoup4 requests lxml
   ```

3. **Run the application**:
   ```bash
   python scrapping.py
   ```

4. **Access in browser**:
   Open `http://127.0.0.1:5000/`
