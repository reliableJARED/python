An example of a simple scraper for python.  There are many ways to do this, this is our way.

Target: http://pc104.org/products/

Information needs to be added to a spread sheet consisting of a variety of categories such as:
Company Name
Product Name
Image of the product
Type of Product
Description
Technical Details
Specification
PC Bus
Technology

code imports required:

import BeautifulSoup

http://www.python-excel.org/
  import xlwt: https://pypi.python.org/pypi/xlwt 
  import xlrd: https://pypi.python.org/pypi/xlrd
  import xlutils: https://pypi.python.org/pypi/xlutils

import requests: http://www.python-requests.org/en/latest/
