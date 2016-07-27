#ONLY NEEDED ON MY UBUNTU
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

from bs4 import BeautifulSoup
import sqlite3
import requests
import random
import time
import random
import xlwt
import sys


FILE = "linkedIn_profile_urls.txt"


def random_user_agents():#opens a txt file with 900 user agents
        user_agent = []
        uafile = 'UserAgent_list.txt'
        with open(uafile, 'rb') as uaf:
            for ua in uaf.readlines():
                if ua:
                    user_agent.append(ua.strip()[1:-1-1])
        random.shuffle(user_agent) #prepare list of user agents.
        return user_agent[0]

def resultURLs(Gsoup):
        googleResulteURLS = []
        #extract the urls of search results from a google page
        for result in Gsoup.find_all("h3","r",'a'):
            #go to <h3 class='r"><a> HTML location where url is found
            name = result.find('a',href=True)
   
            #pull out the 'href' property of the HTML tag, this is the actual link
            link = name['href']
            
            #prettify the link it with 2 string splits, google adds tracking data not part of
            #the real url that we must remove
            #to isolate the true url link
            link = ((link.split("rl?q=")[1]).split("&sa"))[0]
            
            #add the resulting URL to our list of URLs.  Each URL should lead
            #to a linkedIn profile
            googleResulteURLS.append(repr(link))
     
        return googleResulteURLS
   
def googleResultPagesURLs(url):
        TenPages =[]
        TenPages.append(url)
        #after page 1, start is increment of 100, because we are
        #using num=100 in our search to get 100 results per page
        url = url.replace('start=1','start=100')
        
        TenPages.append(url)

        #now loop through for 10 pages.  by default google typically won't actually
        #return more than 1000 results even if it says '22,000 results' for example
        #from a search
        #for x in range(2,10):
                #url = url.replace('start='+str(x-1)+'00','start='+str(x)+'00')
                #TenPages.append(url)
        
        return TenPages


def getSearchResults(urlList):
        allContent =[]
        file = open(FILE, "w")
        for x in range(0,len(urlList)):
                print "google result page "+str(x+1)+" being scraped"
                #random sleep time to slow things down and not make google mad
                time.sleep(random.randint(2,5))
                try:
                        #get the google result page
                        link = requests.get(urlList[x])

                        #parse the result page
                        Gsoup = BeautifulSoup(link.content,"html.parser")

                        #extract the result urls from the parsed page
                        profileURLs = resultURLs(Gsoup)

                        #should be 100 results in profileURLs
                        for result in profileURLs:
                                #don't add duplicates
                                if result not in allContent:
                                        #use str() strip unicode
                                        #save to txt file
                                        file.write(result)
                                        file.write('\n')
                                        #add to our master list
                                        allContent.append(result)
                except:
                        print "bad google result page"
        file.close()             
        return allContent

class LinkedinProfileObject:
    def __init__(self,name, job,company,loc,url) :
        self.name = name
        self.job = job
        self.company = company
        self.location = loc
        self.url = url

def LinkedinProfileDataExtractor(url):
        #the urls all come in as 'u'https we want that as https
        url = url.replace('u\'https','https')
        #also want to remove the trailing '
        url = url[:-1]

        #spoof header, linkedin won't allow python
        headers = {'User-Agent':random_user_agents()}#add random header at some point
        
        error_msg = 'ERROR'
        #get the linkedin profile page
        try:
                link = requests.get(url,headers=headers)
        except:
                print "linkedin seems to be blocking you now"
                return 'blocked','blocked','blocked','blocked',url

        #parse the result page
        LIsoup = BeautifulSoup(link.content,"html.parser")

        try:
                name = LIsoup.find(attrs={'class':'fn'}).text
        except:
                name = error_msg
        try:
                job = LIsoup.find(attrs={'class':'position'})#find all the jobs
                job = job.find(attrs={'class':'item-title'}).text#get latest
        except:
                job = error_msg
        try:
                company = LIsoup.find(attrs={'class':'position'})
                company = company.find(attrs={'class':'item-subtitle'}).text#get latest company
        except:
                company = error_msg
        try:
                loc = LIsoup.find(attrs={'class':'locality'}).text
        except:
                loc = error_msg
                return name, job,company,loc,url

class SQLtable:
    
    '''
    DATABASE MANAGMENT CLASS
    '''
    
    #This is the SQL database class
    #create by passing a name you want the database file to be called
    def __init__(self,database_file):
        self.database_file = database_file+'.sqlite'
    
    def CreateTable(self,TableName,columns=['default',]):
        #Creates a table in the database pass column names to column variable as a list
        
        #first create connection instance to the Database
        conn = sqlite3.connect(self.database_file)
        #create instance of the cursor
        c = conn.cursor()
        
        #setup the column data type affinity for the table
        #for now all are text, see this: https://www.sqlite.org/datatype3.html?#affinity
        affinity = "TEXT"
        
        #create input string. format is (column_name1 type, column_name2 type,...)
        column_names = ','.join('{column_name} {afn}'.format(column_name = c,afn=affinity)for c in (columns))
        #https://docs.python.org/2/tutorial/datastructures.html#list-comprehensions
        #see that link on how single line for loops (list comprehensions) work
        
        try:
            c.execute('CREATE TABLE {tn}({c})'.format(tn=TableName, c=column_names))
            conn.commit()
        except:
            print "table name: %s exists" %TableName
    
    def TableInfo(self, TableName):
        #This PRAGMA returns one row for each column in the named table: TableName
        #see: https://www.sqlite.org/pragma.html#pragma_table_info
        info = "PRAGMA table_info(%s)" % TableName
        #create a connection to the database
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute(info)
        #use fetchall() to get all the  rows returned from the PRAGMA
        #Note each row has info about a single column.  ColInfo will be list of tuples for each column in table
        ColInfo = c.fetchall()
        #Columns in the result set include the column name, data type, whether or not the column can be NULL, and the default value for the column.
        
        #ColInfo has the format:
        #(col#, colName,colType,bool4NULL(0 or 1),defaultValue,PrimaryKey index(0 for non PK))
        #so each column returns a tuple of 6 items if for example the table had 3 columns
        # then ColInfo would have format [(col_1 6item list),(col_2 6item list),(col_3 6item list)]
        return ColInfo

        
    def AddRow(self,RowData=['data'],TableName = None,duplicate=0):
        #duplicate =0 will NOT enter duplicate row data if RowData is found to exist in the table
        #to enter duplicate data pass 1 after RowData
        
       
        if TableName is None:
            print "Error: no table name passed to AddRow([data],tableName)"
            return
        else:
            TableName = TableName#if a TableName is passed as argument, assign TableName what was passed
        
        #first get data about the table
        table_info = self.TableInfo(TableName)#retuns list of tuples
        if table_info ==[]:#empty list if there is no table
            print "no table named: {}".format(TableName)
            return
     
       
        #first create connection instance to the DB
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        
        if duplicate == 0:#aka don't add RowData to table if RowData already exists
            
            col_count = len(table_info)#each tuple in the list represents a column in the table, get total column count
            if col_count == len(RowData):#check that number of columns matches number of data entries
                pass
            else:
                print "ERROR: RowData has {a} entries and {b} has {c} columns".format(a=len(RowData), b=TableName, c=col_count)
                return
            
            col_name = []#container for the column names
            for column in range(0,col_count):
                col_name.append(str(table_info[column][1]))#create list of column names
           
            
            #create the search string to check for if RowData already exists in table
            search =''
            for col in range(0,col_count):
                search = search +(str(col_name[col] +" = ?"))#search format: column_name = ?
                if col_count != (col+1):
                    search = search + (' AND ')#add an AND if there is another column format: column_name1 = ? AND column_name2 = ?
            
            #print search #print for TS
                
            #check to see if there is a match on a single row in our tabel for RowData
            c.execute("SELECT * FROM {tn} WHERE {search}".format(tn=TableName,search=search),RowData)#RowData will replace ? in search with the input data
            result = c.fetchall()
            
            #len(result) will = 0 if no match found
        if duplicate == 1 or len(result)==0:#duplicate entry OK or no existing match, note len(result) MUST come second as it will not exist if duplicate ==1 
            
            #create a place holder ? for each value going to each column in our table
            qmark = "?"
            qmark = ','.join('?' for count in range (len(RowData)))
            
            #print qmark #print for TS
            
            #update the table with the info from the RowData list
            c.execute('''INSERT INTO {tn} VALUES ({q})'''.format(tn=TableName, q=qmark),RowData)
            #save changes to database
            conn.commit()
            conn.close()
            #notify user of update
            print "{} added to Database".format(RowData)
        else:
            #if result >0 this means contact exists so dont add
            print "Row entry {} Already Exists".format(RowData)


def writeToExcel(allLinkedInProfileURLs):
    #setup excel sheet
    wb = xlwt.Workbook()
    ws = wb.add_sheet('results')
    for url in range(0,len(allLinkedInProfileURLs)):
        name, job,company,loc,profile = LinkedinProfileDataExtractor(allLinkedInProfileURLs[url])
       
        #ws.write(row, column, data)
        print "profile "+str(url+1)+" of "+str(len(allLinkedInProfileURLs))+ " done"
        ws.write(url,0,name)
        ws.write(url,1,job)
        ws.write(url,2,company)
        ws.write(url,3,loc)
        ws.write(url,4,profile)
        
    wb.save('LinkedInScrapeResults.xls')

def googleSearch(position,company):
    #need to add the google search operator AROUND() to our search terms
    #the reason is false positive search results form the right hand side
    #where it shows 'people also viewed'  we dont want those terms triggering 
    #a google result, we only want the persons profile content to trigger a result
    position_prox = position.replace(' ', ' AROUND(3) ')#2 indicantes number of words separating these terms
    
    #now we want to make sure our position is showing up near our company, first split position
    #term on whitespaces, if any
    position_terms = position.split()
    
    #next for each term in position make sure it's near our company
    pos_comp_proxy = " "
    for x in range(0,len(position_terms)):
        pos_comp_proxy = pos_comp_proxy +" "+ position_terms[x] + " AROUND(7) " +company
    
    #finally put it all together to get our search term
    searchTerm = position_prox + pos_comp_proxy
    print searchTerm
                            
    #keys for google
    key1 = 'start'
    key2 = 'num'
    key3 = 'client'
    key4 = 'channel'
    key5 = 'q' #search terms
    key6 = 'ie'
    key7 = 'oe'

    value1 = 1
    value2 = 100#hits per page
    value3 = 'ubuntu'
    value4 = 'fs'
    value5_a= searchTerm #'research AROUND(2) scientist scientist AROUND(5) biogen AROUND(5) present '
    value5_b= ' -*/dir/* -*/title/* -*/jobs/* site:linkedin.com/*'
    value6 = 'utf-8'
    value7 = 'utf-8'
            
    headers = {'User-Agent':random_user_agents()}#add random header at some point
    payload = {key1:value1,key2:value2,key3:value3,key4:value4,key5:value5_a+value5_b,key6:value6, key7:value7}
    link = requests.get('https://google.com/search',params=payload,headers=headers)
    #print link.url
    return link.url


position = raw_input("job or position: ") 
company = raw_input("company: ") 
#run google search
searchURL = googleSearch(position,company)

#use the search result url to generate pages of hits
allGoogleResultURLs = googleResultPagesURLs(searchURL)

#extract the urls from the search result pages
allLinkedInProfileURLs = getSearchResults(allGoogleResultURLs)
print allLinkedInProfileURLs[0]

#Now we have a list of linkedin profiles that match criteria of what
#we are looking for.  Next go to the profiles and extract data


#NOTE:
#could write direct to excel using writeToExcel(allLinkedInProfileURLs) 
#but database is better long term


#setup our database to hold the results
#SQLtable class is created by passing a name for our db
myDB = SQLtable('LinkedIN_scrape')

#creat a name for a table in our db, and columns in that table
tablename = 'results'
column_names =['name','job','company','location','linkedin_URL']

#create our table in our database
myDB.CreateTable(tablename,column_names)

#scraped data holder
profileObjectList =[]

#for each profile url, extract our data and create a data object then append to our list
for LIprofile in range(0,len(allLinkedInProfileURLs)):
    #random sleep time to slow things down and not make linkedin mad
    time.sleep(random.randint(2,5))
    
    #extract data from a linkedin Profile
    try:
        name, job,company,loc,profile = LinkedinProfileDataExtractor(allLinkedInProfileURLs[LIprofile])
        #create an object for the extracted data and put the object in a list
        profileObjectList.append(LinkedinProfileObject(name, job,company,loc,profile))
    except:
        print "error making profile object for: " + allLinkedInProfileURLs[LIprofile]
    
    
    #update progress to user
    b = str(LIprofile)+" of "+ str(len(allLinkedInProfileURLs))+ " complete\r" 
    print b
    sys.stdout.write("\033[F") # Cursor up one line
    #sys.stdout.write(str(LIprofile)+" of "+ str(len(allLinkedInProfileURLs))+ " complete" )
    #sys.stdout.flush()
    
  

#now every object in our profileObjectList has properties .name,.job,.company,.location,.url
#write data to our database
for obj in range(0,len(profileObjectList)):
    myDB.AddRow([profileObjectList[obj].name,\
                 profileObjectList[obj].job,\
                 profileObjectList[obj].company,\
                 profileObjectList[obj].location,\
                 profileObjectList[obj].url],tablename )
    print str(obj+1) + " of "+str(len(profileObjectList))+" written to database"