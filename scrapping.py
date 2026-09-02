import re
from urllib.parse import urljoin
from wsgiref import headers

from bs4 import BeautifulSoup
import csv   
import requests
from flask import Flask, json, jsonify,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime


# def func(page_num):
#    
#    r=requests.get(url)
#    soup=BeautifulSoup(r.text,'lxml')
#    books= soup.find_all('article',class_='product_pod')
#    with open(f'data/booksproj.csv', 'w', newline='', encoding='utf-8') as f:
#        csv_writer=csv.writer(f, delimiter=',')
#        csv_writer.writerow(['Title','Rating','Price'])
#        for book in books:
#              title=book.h3.a['title']
#              rating=book.find('p',class_='star-rating')['class'][1]#here ratings are stored in the class attribute of the p tag with class 'star-rating'. so we can get the rating by getting the second class of the p tag.
#              #space in class attribute is used to separate multiple classes. so we can get the rating
#              price=book.find('p',class_='price_color').text
             

#              csv_writer.writerow([title,rating,price])
#    data_list=[]
#    with open (f'data/booksproj.csv','r',encoding='utf-8') as f:
#        csv_reader=csv.reader(f)
       
#        next(csv_reader)#skip the header row
#        for row in csv_reader:
#           data_list.append({'title':row[0],'rating':row[1],'price':row[2]})      
#    return data_list
     
   
      

#       data_list.append({'title':title,'rating':rating,'price':price})
#    return data_list
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)
class Books(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(200), nullable=False)
    rating=db.Column(db.String(20), nullable=False)
    price=db.Column(db.Float, nullable=False)
    genre=db.Column(db.String(200), nullable=False)
    image_url=db.Column(db.String(200), nullable=True)
    def __repr__(self):
        return f"Book('{self.title}','{self.rating}','{self.price}','{self.genre}','{self.image_url}')"
with app.app_context():
    db.create_all()
def store_in_db(data_list):
    for book_data in data_list:
        book_entry = Books(title=book_data['title'], rating=book_data['rating'], price=book_data['price'], genre=book_data['genre'], image_url=book_data['image_url'])
        db.session.add(book_entry)
    db.session.commit()
def scrape_page(page):
   data_list=[]
   if page == 1:
    url = "https://books.toscrape.com/"
   else:
        url = f"https://books.toscrape.com/catalogue/page-{page}.html"
   r=requests.get(url)
   sou=BeautifulSoup(r.text,'lxml')
   boks= sou.find_all('article',class_='product_pod')
   for book in boks:
             title=book.h3.a['title']
             rating=book.find('p',class_='star-rating')['class'][1]#here ratings are stored in the class attribute of the p tag with class 'star-rating'. so we can get the rating by getting the second class of the p tag.
             #space in class attribute is used to separate multiple classes. so we can get the rating
             import re
             price_text = book.find('p', class_='price_color').text
             price = float(re.sub(r'[^\d.]', '', price_text))
             image_relative = book.find('img')['src']
             image_url = urljoin("https://books.toscrape.com/", image_relative)
             relative_url=book.find(class_='image_container').a['href']
             book_url = urljoin("https://books.toscrape.com/catalogue/", relative_url)
            #  ---------this works but it still has some issues with the genre extraction, due to lack of stabilty.----------------
            #  j=requests.get(book_url)
            #  soup=BeautifulSoup(j.text,'lxml')
            #  try:
            #      genre = soup.find('ul', class_='breadcrumb').find_all('li')[2].a.text.strip()
            #  except:
            #       genre = "Unknown"
            # --------------the above part ends here-----------------
            #  ---------------this is the  part i have written to extract genre------------------
            # #  book_genre=soup.find('ul',class_='breadcrumb')
            # #  b_genre=book_genre.find_all('li')
            # #  genre=b_genre[2].text.strip()#here we are getting the genre of the book by finding the ul tag with class 'breadcrumb' and then finding the third li tag and getting its text and stripping any whitespace from it.
            # # or
            # # genre = soup.select('ul.breadcrumb li a')[2].text.strip()  # Using CSS selector to get the third <a> tag inside <li> of <ul class="breadcrumb">
            # # or
            # -------------------end of small part-------------------
            #here we are getting the genre of the book by finding the ul tag with class 'breadcrumb' and then finding the third li tag and getting its text and stripping any whitespace from it.
            #  genre = "Unknown"   # temporary
            # --------------------this is the corrected part-------------------
             headers = {"User-Agent": "Mozilla/5.0"}

             j = requests.get(book_url, headers=headers)

             if j.status_code == 200:
                soup = BeautifulSoup(j.text, 'lxml')

                breadcrumb = soup.select("ul.breadcrumb li")

                if len(breadcrumb) > 2:
                     genre = breadcrumb[2].get_text(strip=True)
                else:
                    genre = "Unknown"
             else:
                   genre = "Unknown"
             data_list.append({'title':title,'rating':rating,'price':price,'genre':genre,'image_url':image_url})
   return data_list

@app.route('/search', methods=['GET'])
def search_books():
    search_query = request.args.get('query')
    if search_query:
        books = Books.query.filter(Books.title.ilike(f'%{search_query}%')).all()
    else:
        books = []
    return render_template("base.html", books=books)


@app.route('/')
def home():
    books = Books.query.all()
    return render_template("base.html", books=books)
@app.route('/filter',methods=['GET'])
def filtter_books():
    genre=request.args.get('genre')
    price=request.args.get('price')
    rating=request.args.get('rating')
    query = Books.query
    if genre:
        query=query.filter_by(genre=genre)
    if price:
        query=query.filter(Books.price <= float(price))  #for max price filter
    if rating:
        query=query.filter_by(rating=rating)
    books = query.all()
    return render_template("base.html", books=books)

# def csv_load(data_list):
#     with open(f'booksproj.csv', 'w', newline='', encoding='utf-8') as f:
#         csv_writer=csv.writer(f, delimiter=',')
#         csv_writer.writerow(['Title','Rating','Price','Genre','Image_URL'])
#         for book in data_list:
#             csv_writer.writerow([book['title']+'\t',book['rating']+'\t',book['price']+'\t',book['genre']+'\t',book['image_url']])
# def csv_read():
#     data_list=[]
#     with open (f'booksproj.csv','r',encoding='utf-8') as f:
#         csv_reader=csv.reader(f)
#         next(csv_reader)#skip the header row
#         for row in csv_reader:
#            data_list.append({'title':row[0],'rating':row[1],'price':row[2],'genre':row[3],'image_url':row[4]})      
#     return data_list
# def filter_rating(data_list):
#    mapping={'One':1,'Two':2,'Three':3,'Four':4,'Five':5,'1':1,'2':2,'3':3,'4':4,'5':5}
#    stars = input("Enter rating: ")
#    if stars in mapping:
#       stars = mapping[stars]
#    for book in data_list:
#       if mapping.get(book['rating']) == stars:
#             print(f"Title: {book['title']}, Price: {book['price']}, Rating: {book['rating']}, Genre: {book['genre']}, Image URL: {book['image_url']}")

# def price_range(data_list):
#    min_price=float(input("Enter the minimum price: "))
#    max_price=float(input("Enter the maximum price: "))
#    for book in data_list:
#       price = float(book['price'].replace('£', '').replace('Â', '').strip())#here we are removing the currency symbol and any whitespace from the price string and converting it to a float for comparison.
#       if min_price <= price <= max_price:
#          print(f"Title: {book['title']}, Price: {book['price']}, Rating: {book['rating']}, Genre: {book['genre']}, Image URL: {book['image_url']}")

# def book_search(data_list):
#    search=input("Enter the title of the book you want to search: ")
#    for book in data_list:
#       if search.lower() in book['title'].lower():
#          print(f"Title: {book['title']}, Price: {book['price']}, Rating: {book['rating']}, Genre: {book['genre']}, Image URL: {book['image_url']}")

# if __name__=="__main__":
#     data_list=func()
#     while True:
#         print("1. Filter by rating")
#         print("2. Filter by price range")
#         print("3. Search by title")
#         print("4. Exit")
#         try:
#             choice = int(input("Enter your choice: "))
#         except ValueError:
#              print("Enter a valid number")
#              continue
#         if choice == 1:
#             filter_rating(data_list)
#         elif choice == 2:
#             price_range(data_list)
#         elif choice == 3:
#             book_search(data_list)
#         elif choice == 4:
#             break
#         else:
#             print("Invalid choice")
import os

# if __name__ == "__main__":
#     if not os.path.exists('booksproj.csv'):
#         data_list = scrape_all_pages()
#         csv_load(data_list)
#     else:
#         data_list = csv_read()

#     while True:
#         print("1. Filter by rating")
#         print("2. Filter by price range")
#         print("3. Search by title")
#         print("4. Exit")

#         try:
#             choice = int(input("Enter your choice: "))
#         except ValueError:
#             print("Enter a valid number")
#             continue

#         if choice == 1:
#             filter_rating(data_list)
#         elif choice == 2:
#             price_range(data_list)
#         elif choice == 3:
#             book_search(data_list)
#         elif choice == 4:
#             break
#         else:
#             print("Invalid choice")
# if __name__ == "__main__":
#     with app.app_context():
#         if Books.query.count() == 0:
#             data_list = []
#             for page in range(1, 10):  # Assuming there are 50 pages to scrape
#                 data_list.extend(scrape_page(page))
#             store_in_db(data_list)

#     app.run(debug=True)
def initialize_database():
    with app.app_context():
        db.create_all()

        if Books.query.count() == 0:
            data_list = []

            for page in range(1, 10):
                data_list.extend(scrape_page(page))

            store_in_db(data_list)


initialize_database()