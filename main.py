from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import requests

# Rquesting Response:
try:
 html_request = requests.get('https://books.toscrape.com/').text
except:
  print("No response") 
  
# Initializing Soup:
soup = BeautifulSoup(html_request, "html.parser")
books = soup.find_all('li', class_= "col-xs-6 col-sm-4 col-md-3 col-lg-3")

# Initializing SQL Table:
conn = sqlite3.connect("library.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS library
            (index_book int PRIMARY KEY, book_udp int , book_name text, book_price int, book_stock text, book_description text)''')

# Initializing Outside "for" Variables:
books_dict = {}
book_names_list = []
book_prices_list = []
book_stocks_list = []
book_udp_list = []

for index,book in enumerate(books):
    book_url = book.find('a')['href']
    book_url = "https://books.toscrape.com/" + book_url
    book_response = requests.get(book_url).text
    soup2 = BeautifulSoup(book_response,"html.parser")
    # Getting Values:
    book_names = soup2.find('h1').text
    book_price = soup2.find('p').text.replace("Â","")
    book_stock = soup2.find('p', class_= "instock availability").text.replace("  ","").replace("\n","") 
    book_desciption = soup2.select('p')[3].text
    book_table= soup2.select('th')[0].text +" : "+ soup2.select('td')[0].text
    book_table2 = soup2.select('td')[0].text
    
    # Creating ListS for Dict:
    book_names_list.append(book_names)
    book_prices_list.append(book_price)
    book_stocks_list.append(book_stock)
    book_udp_list.append(book_table2)
    
    # Updating Dict:
    books_dict.update({
       'UDP': book_udp_list,
       'Name': book_names_list,
       'Price': book_prices_list,
       'Srock': book_stocks_list,
       }) 
    
    #Inserting Values of Tuple into the SQL table:
    book_tuple = [(index,book_table,book_names,book_price,book_stock,book_desciption)]
    c.executemany("INSERT INTO library VALUES (?,?,?,?,?,?)", book_tuple)
    
    
    # Writing Txt file:
    with open (f'./{index}.txt', 'w', encoding="utf-8") as f:   
        f.write(f"""\n Book Name: {book_names}
          \n {book_table}
          \n Book Price: {book_price}
          \n Book Stock: {book_stock}
          \n Book Description : \n {book_desciption}       
          """)  
        print(f"File Saved {index}") 

#Commiting and Closing SQL Table:  
conn.commit()
conn.close()

# Creating Excel File From Dataframe: 
df = pd.DataFrame(books_dict)
df.to_excel("Library_Excel.xlsx",sheet_name="library01")
df.to_csv("Library_csv.csv", index= False, encoding= "utf-8")
    
  