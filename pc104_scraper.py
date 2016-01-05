'''
https://www.elance.com/j/scrape-data-add-spreasheet/76522376/?backurl=aHR0cHM6Ly93d3cuZWxhbmNlLmNvbS9yL2pvYnMvcS13ZWIlMjBzY3JhcGluZw%3D%3D
'''
# Chris Made This Edit! :)
#Jared made this edit, woot!
#but it didnt make it


import requests
from bs4 import BeautifulSoup
import urllib2 # Used to read the html document
import urlparse
import xlwt #This works with LibreOffice
import xlrd #This works with LibreOffice
import xlutils
from xlutils.copy import copy #used to edit existing excel sheets

# Create opener with friendly user agent
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

def workbook():
    #create workbook
    book =xlwt.Workbook()
    '''TO WRITE TO BOOK USE THIS FORMAT:
        sheet = book.add_sheet('Example_Sheet')#create sheet
        row = 0#first row
        column =0#first column
        val = 5#enter a value
        sheet.write(row,col,val)
        when writing strings \n will carrige return same cell
        example "john \nSmint"
        book.save('Example_Book.xls')

        workbook saves in same folder where this
        py code is saved
    '''
    return book

def webpage_to_soup():
    open_page = requests.get('http://pc104.org/products/')
    #open web page
    page = opener.open(open_page.url)
    #turn HTML to soup
    soup = BeautifulSoup(page)
    

    #pull all the links from the page
    url_list =[]
    for link in soup.find_all('a', href=True):
       url_list.append(link['href'])
    
    return url_list

def product_links(url_list=[]):
    #this function take all the urls found on the page and extracts only those of interest
    product = '/product_type/'
    ProductList =[]
    spec = '/specifications/'
    SpecList =[]
    #extract only links of product pages
    for x in range(0,len(url_list)):
        # The find == -1 if not found, so != -1 equals found
        if url_list[x].find(product) != -1:
            ProductList.append(url_list[x])

    for x in range(0,len(url_list)):
        if url_list[x].find(spec) != -1:
            SpecList.append(url_list[x])

    return ProductList, SpecList

def write_to_excel(ProductList=[], SpecList=[]):
    #create excel sheet
    excel = workbook()
    ProductPage = excel.add_sheet('product')
    SpecPage = excel.add_sheet('specification')
    #create column header in excel sheet
    SpecPage.write(0,0,"Specification Page")
    ProductPage.write(0,0,"Product Page")
    for product in range(0,len(ProductList)):
        ProductPage.write(product+1,0,ProductList[product])

    for spec in range(0,len(SpecList)):
        SpecPage.write(spec+1,0,SpecList[spec])

    product_url_count = len(ProductList)
    spec_url_count = len(SpecList)
    #save the excel sheet, will be saved to the same directory as this code
    print "file created"
    excel.save('elance_work.xls')
    #return count of urls for each page
    return product_url_count, spec_url_count
    
    
def find_number_of_pages(url):
    #called from product_page_extract
    #used to determine number of product pages in catagroy
    open_page = requests.get(url)
    #open web page
    page = opener.open(open_page.url)
    #turn HTML to soup
    soup = BeautifulSoup(page)
    
#navigate to the buttom of page to find what Page 1 of x is, we want x
#if there is only one page of results there will be no <span class=pages'>
    try:
        count = str(soup.find('span','pages').text)
    except AttributeError:
        #str(soup.find('span','pages').text) throws error when only 1 page
        count = 1
    
    # string split the text of the <span class='pages'>
    if count ==1:
        num_of_pages = 1
    else:
        #string split to isolate num_of_pages, count will look like:
        #[<span class="pages">Page 1 of 2</span>]
        count2 = count.split("Page 1 of ")
        count3 = count2[1].split("</span")
        num_of_pages = int(count3[0])
        
    #below is used for user to see progress
    print "pages= " + str(num_of_pages) + ", type= " + str(type(num_of_pages))
    #finally after all that retrun total pages for the product catagory
    return num_of_pages

    
def product_page_extract(product_url_count,spec_url_count):
    #open the previously created workbook with company data
    book = xlrd.open_workbook(('elance_work.xls'), formatting_info=True, on_demand=True)
    #open specific sheets
    ProductSheet = book.sheet_by_name('product')
    SpecSheet = book.sheet_by_name('specification')
    
    #copy() is from xlutils lets you write to existing workbook
    edit = copy(book)
    #create instance of excel sheets that can be edited
    product_edit_sheet = edit.get_sheet(0)#first sheet, product
    spec_edit_sheet = edit.get_sheet(1)#second sheet, specification
    #create headers for column 2
    product_edit_sheet.write(0,1,"Num of Pages")
    spec_edit_sheet.write(0,1,"Num of Pages")
    #Product pages
    for x in range(0,product_url_count):
        #go down each row in excel,(remember row 1 is header) pass url to determine num of pages in that catagory
        page_count = find_number_of_pages(ProductSheet.cell_value(x+1,0))
        #write the page count in column 2 or our 'elance_work.xls'
        product_edit_sheet.write(x+1,1,page_count)
        
    #specification pages
    for x in range(0,spec_url_count):
        #go down each row in excel,(remember row 1 is header) pass url to determine num of pages in that catagory
        page_count = find_number_of_pages(SpecSheet.cell_value(x+1,0))
        #write the page count in column 2 or our 'elance_work.xls'
        product_edit_sheet.write(x+1,1,page_count)
    
    edit.save('elance_work.xls')
        
        

    
       
       
#the main sequence
step1 = webpage_to_soup()
step2,step3 = product_links(step1)
step4,step5 = write_to_excel(step2,step3)
product_page_extract(step4,step5)
