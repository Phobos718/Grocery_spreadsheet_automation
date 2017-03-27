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
DB_item_count = int(DB.cell(2, 8).value)

def refresh_prices():
    print '\nLoading pages...'
    links = [urllib2.urlopen(DB.cell(i + 2, 2).value) for i in range(DB_item_count)]
    price_list = []
    promo_list = []

    print '\nFetching prices'
    for link in links:
        page = BeautifulSoup(link, 'html.parser')
        price_list.append( page.find('meta', itemprop='price')['content'].replace('.',',') )
        if page.find('div', class_='onOffer') is not None:
            promo_details = page.find('div', class_='onOffer').span.text
            promo_list.append( promo_details.partition('.')[0] ) 

        else: 
            promo_list.append( '-' )

    print promo_list

    print '\nUpdating spreadsheet...'
    for i in range(DB_item_count):
        DB.update_cell(2 + i, 3, price_list[i])
        DB.update_cell(2 + i, 9, promo_list[i])
    

def update_order(sheet_option):
    sheet_list = [Erik_N, Les, Erik_S]
    log = open('log.csv','w+')
    for sheet in sheet_list:
        log.write(sheet.export())
    log.close()

    if sheet_option == '':
        for i in range(DB_item_count):
            value = (int(Erik_N.cell( i + 2, 2).value) +
                    int(Erik_S.cell( i + 2, 2).value) +
                    int(Les.cell( i + 2, 2).value) +
                    int(DB.cell( i + 2, 4).value))
            DB.update_cell( i + 2, 4, value)
            for sheet in sheet_list:
                sheet.update_cell( i + 2, 2, 0)

    else:
        for i in range(DB_item_count):
            value = int(DB.cell( i + 2, 4).value)
            for opt in sheet_option:
                opt = int(opt) - 1
                value += int(sheet_list[opt].cell( i + 2, 2).value)
            DB.update_cell( 2 + i, 4, value)

def log_and_reset():
    sheet_list = [Erik_N, Les, Erik_S]
    log = open('log.csv','w+')
    for sheet in sheet_list:
        log.write(sheet.export())
    log.close()
    for sheet in sheet_list:
        sheet.update_cell( i + 2, 2, 0)




option = ''
while option != 'y' and option != 'n':
    option = raw_input('Would you like to refresh prices? [y/n]\n')
    if option == 'y':
        refresh_prices()
    elif option == 'n':
        break

option = raw_input( 'Select sheet to add to orders (enter digits in any order)'
                    ' or press "Enter" to save logs and reset sheet.'
                    '\n[1]Mucsu\n[2]Nardu\n[3]Suplu\n' )


update_order(option)
