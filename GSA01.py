import gspread
import urllib2
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

Erik_N = client.open('vasarlas').worksheet('Nardu')
Erik_S = client.open('vasarlas').worksheet('Suplu')
Les = client.open('vasarlas').worksheet('Mucsu')
Order = client.open('vasarlas').worksheet('Order')
DB = client.open('vasarlas').worksheet('DB')
DB_item_count = int(DB.cell(2, 5).value)

def refresh_prices():
    print '\nLoading pages...'
    links = [urllib2.urlopen(DB.cell(i + 2, 2).value) for i in range(DB_item_count)]
    #maybe if page comes here as a list comprehension it'd be faster... maybe
    price_list = []

    print '\nFetching prices data...'
    for link in links:
        page = BeautifulSoup(link, 'html.parser')
        price_list.append( page.find('meta', itemprop='price')['content'].replace('.',',') )

    print '\nUpdating spreadsheet...'
    for i in range(DB_item_count):
        DB.update_cell(2 + i, 3, price_list[i])

def update_order(sheet_option):
    if sheet_option == '':
        for i in range(DB_item_count):
            value = (int(Erik_N.cell( i + 2, 2).value) +
                    int(Erik_S.cell( i + 2, 2).value) +
                    int(Les.cell( i + 2, 2).value) +
                    int(Order.cell( i + 2, 2).value))
            Order.update_cell( 2 + i, 2, value)

    else:
        sheet_list = [Erik_N, Erik_S, Les]
        for i in range(DB_item_count):
            value = int(Order.cell( i + 2, 2).value)
            for opt in sheet_option:
                opt = int(opt) - 1
                value += int(sheet_list[opt].cell( i + 2, 2).value)
            Order.update_cell( 2 + i, 2, value)



option = ''
while option != 'y' and option != 'n':
    option = raw_input('Would you like to refresh prices? [y/n]\n')
    if option == 'y':
        refresh_prices()
    elif option == 'n':
        print 'whatever man'
        break

option = raw_input('Select sheet to add to orders or press "Enter" to add all.\n[1]Mucsu\n[2]Nardu\n[3]Suplu\n')
