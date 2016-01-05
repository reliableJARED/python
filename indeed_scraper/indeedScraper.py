from __future__ import print_function #turns print into function print()

import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
import urllib2 # Used to open the html document
from bs4 import BeautifulSoup
import sqlite3
import requests
import random#used in user-agent selection

""" List of Staffing Companies that are filtered out of search """
staffing_companies = ['Foundation Staffing', \
                   'CUE Technoloties',\
                    'Sunrise Systems Inc',\
                   'SNI Financial', \
                   'The Tri-Com Consulting Group', \
                   'United Software group inc',\
                    'Apex Systems Inc', \
                   'Consolidated Health Plans.',\
                    'GENEVA CONSULTING GROUP', \
                    'VLink', \
                   'Aptus IT Solutions Inc.',\
                   'SNI Technology', \
                   'On-3, LLC',\
                    'E*Pro, Inc.', \
                   'Corporate Biz Solutions Inc', \
                   'United Software Group pvt ltd',  \
                   'Robert Half Technology', \
                   'Hobson Associates', \
                   'Sigma Systems, Inc.', \
                   'CyberCoders', \
                   'Skylightsys', \
                   'Fast Switch, Ltd.', \
                   'FIT Solutions', \
                   'L & T Infotech', \
                   'ReqRoute,Inc',  \
                   'CoWorx Staffing',\
                    'IT Solutions Inc', \
                    'Enterprise Solutions Inc.', \
                    'INFICARETECH', \
                    'Kforce', \
                    'Corporate Information Technologies, Inc.',\
                     'Pantar Solutions, Inc.', \
                     'ADPI, LLC..', \
                      'WEX Inc.', \
                      'BCforward', \
                      'Adept Solutions', \
                      'Infogroup Northwest',\
                       'COCC', \
                       'AppLabs', \
                      'Direct Client', \
                      'Project One', \
                      'Virtusa', \
                      'Solution Partners', \
                      'Inc.',\
                       'ePromptus,Inc', \
                       'Spectraforce Technologies Inc', \
                       'ACT-Consulting', \
                       'Albano Systems, Inc',\
                       'The Centrics Group',\
                         'Technosoft Corporation', \
                         'Fours Consulting USA',\
                         'Vertical Talent Solutions', \
                         'Enterprise Solution Inc.', \
                         'Griffin Staffing Network', \
                         'Nigel Frank International Limited', \
                         'Trident Technical Solutions, LLC', \
                         'Sound Business Solutions', \
                         'Talus Partners', \
                         'Staff I.T., Inc', \
                         'E-Business International, Inc.', \
                         'Two95 international Inc', \
                         'Willard Powell', \
                         'iTech Solutions', \
                         '3iPeople Inc.', \
                         'IDC Technologies INC', \
                         'Calsoft Labs',\
                          'Summit Technologies, Inc.', \
                          'Hallmark TotalTech, Inc.', \
                          'L&T Infotech',\
                          'Brine Group Staffing Solutions',\
                          'COOLSOFT']

class SQLtable:
    
    '''
    DATABASE MANAGMENT CLASS
    '''
    
    #This is the SQL database class
    #create by passing a name you want the database file to be called
    def __init__(self,database_file):
        self.database_file = database_file
    
    def CreateTable(self,TableName,columns=['default',]):
        #Creates a table in the database pass column names to column variable as a list
        if type(columns) is not list:
            print("Error! send column names as list: FAILED SQLtable.CreateTable({t},{c})".format(t=TableName, c=type(columns)))
            return
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
        
        
        #print column_names #trouble shoot print
        
        try:
            c.execute('CREATE TABLE {tn}({c})'.format(tn=TableName, c=column_names))
            conn.commit()
        except:
            print("table name: {} exists".format(TableName))
    
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

        
    def AddRow(self,TableName = 'xyz_default_table',RowData=['data'],duplicate=0):
        #duplicate =0 will NOT enter duplicate row data if RowData is found to exist in the table
        #to enter duplicate data pass 1 after RowData
        
       
        if TableName == 'xyz_default_table':
            print("Error: no table name passed to AddRow")
            return
        else:
            TableName = TableName#if a TableName is passed as argument, assign TableName what was passed
        
        #first get data about the table
        table_info = self.TableInfo(TableName)#retuns list of tuples
        if table_info ==[]:#empty list if there is no table
            print("no table named: {}".format(TableName))
            return
     
       
        #first create connection instance to the DB
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        
        if duplicate == 0:#aka don't add RowData to table if RowData already exists
            
            col_count = len(table_info)#each tuple in the list represents a column in the table, get total column count
            if col_count == len(RowData):#check that number of columns matches number of data entries
                pass
            else:
                print("ERROR: RowData has {a} entries and {b} has {c} columns".format(a=len(RowData), b=TableName, c=col_count))
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
            print("{} added to Database".format(RowData))
        else:
            #if result >0 this means contact exists so dont add
            print("Row entry {} Already Exists".format(RowData))


    
    def Query(self, TableName = 'xyz_default_table',RowFind=['xyz_default_row',],columns=['xyz_default_row',],search_type='single_match_any_column'):
        #default implementation will Query the db table for a match to a single RowFind seach term in any column then return that full row of data
        #first create connection instance to the DB
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        
        if search_type=='single_match_any_column':
            #first get data about the table
            table_info = self.TableInfo(TableName)#retuns list of tuples
            col_count = len(table_info)
            col_name = []#container for the column names
            for column in range(0,col_count):
                col_name.append(str(table_info[column][1]))#create list of column names
            #create the search string to check for if RowData already exists in table
            search =''
            find =()#Tuples must be input to values in the sqlite statement
            print(RowFind[0])
            for col in range(0,col_count):
                search = search +(str(col_name[col] +" = ?"))#search format: column_name = ?
                find += (RowFind[0],) #match rowfind entries for each column being searched 
                if col_count != (col+1):
                    search = search + (' OR ')#add an AND if there is another column format: column_name1 = ? AND column_name2 = ?
            
            print(search) #print for TS
            print(find)
                    
            #check to see if there is a match on a single row in our tabel
            c.execute("SELECT * FROM {tn} WHERE {search}".format(tn=TableName,search=search),find)#RowData will replace ? in search with the input data
            result = c.fetchall()
            return result#result is a tuple, each item is the contents of a row [(matching row1),(matching row2), ...]
        
        print("bad query parameters")
     

class WebpageParser:
    # initialization
    def __init__(self):
        pass

    def random_user_agents(self):#opens a txt file with 900 user agents
        user_agent = []
        uafile = 'UserAgent_list.txt'
        with open(uafile, 'rb') as uaf:
            for ua in uaf.readlines():
                if ua:
                    user_agent.append(ua.strip()[1:-1-1])
        random.shuffle(user_agent) #prepare list of user agents.
        return user_agent[0]

    def MKsoup(self,url,payload=None):
        headers = {'User-Agent':self.random_user_agents()}#add random header at some point
        if payload == None:
            link = requests.get(url,headers=headers)
        else:
            link = requests.get(url,params=payload,headers=headers)
            
        page = link.content
        resultURL = link.url
        print(resultURL)
        try:
            return BeautifulSoup(page,"html.parser"), resultURL
        except:
            print("there was a BS parsing error")
            return "ERROR", "ERROR"
            
class Indeed(WebpageParser):
    def __init__(self):
        WebpageParser.__init__(self)

    def search(self,terms,loc,mi='25'):
        #http://www.indeed.com/jobs?q=c%23&l=01002
        key1 = 'q'#search
        key2 = 'l'#location as a zip
        key3 = 'radius'#miles from zip
        
        value1 = terms
        value2 = loc
        value3 = mi#default 25, max is 150
        if int(value3) >150:
            value3 = '150'
        url = 'http://www.indeed.com/jobs'
        payload = {key1:value1,key2:value2,key3:value3}
        INsoup, url = self.MKsoup(url,payload)

        self.MainSearchResultURL = url
        self.MainSearchResultPage = INsoup
        try:
            count = INsoup.find(attrs={'id':'searchCount'}).text
        except AttributeError:
            print(INsoup.content)
        try:    
            self.SearchJobCount = (count.split('of '))[1]# example: "Jobs 1 to 10 of 37" extract the 37
        except UnboundLocalError:
            print("error determining number of posts in the area, set results to 0")
            self.SearchJobCount = str(1)
    def get_all_jobs(self):
        """
        All the jobs returned from the search
        """
        self.all_listings=[]
        try:
            jobPages = int(str(self.SearchJobCount))/10
        except:
            self.SearchJobCount = (str(self.SearchJobCount)).replace(',','') #remove the comma if >999 results
            jobPages = int(self.SearchJobCount)/10
            
        if int(str(self.SearchJobCount)) % 10 != 0:
            jobPages +=1
        for ResultPage in range(0,jobPages):
            searchURL = str(self.MainSearchResultURL) +'&start='+str(ResultPage*10)
            soup, url = self.MKsoup(searchURL)
            posting = soup.find_all(attrs={'data-tn-component':'organicJob'})
            for job in posting:
                title = job.find(attrs={'data-tn-element':'jobTitle'})
                company = job.find(attrs={'itemprop':'hiringOrganization'})
                location = job.find(attrs={'itemprop':'addressLocality'})
                summary = job.find(attrs={'class':'summary'})
                """
                Creat a list with each element as a job post
                """
                try:
                    check = 0
                    for comapny_name in range(len(staffing_companies)): 
                        if ((str(company.text).lstrip()).split('\n'))[0] == staffing_companies[comapny_name]:
                            check = 1
                            #print("staffing company post removed") 
                            
                    if check == 0:
                        self.all_listings.append([((str(company.text).lstrip()).split('\n'))[0], str(title.text), str(location.text),repr(summary.text)])
                    else:
                        pass
                    
                except (UnicodeEncodeError, AttributeError) as e:
                    print("ERROR")
                    print(e)
                    pass
                
        return self.all_listings

              
    def companies_posting(self):
        """
        get the list of companies advertising positions
        """
        try:
            uniqueCompanies = set([self.all_listings[x][0] for x in range(0,len(self.all_listings))])
        except:
            self.get_all_jobs()
            uniqueCompanies = set([self.all_listings[x][0] for x in range(0,len(self.all_listings))])
        return uniqueCompanies
    

    def positions_at_companies(self):
        pass
        
        

        
class YellowPages(WebpageParser):
    
    def __init__(self):
        WebpageParser.__init__(self)
        self.key_1 = 'search_terms'
        self.key_2 = 'geo_location_terms'
 
        
    def address_phone(self):
        payload = {self.key_1:self.company, self.key_2:self.location}
        self.YPsoup, resultURL = self.MKsoup('http://www.yellowpages.com/search',payload)
        if self.YPsoup == "ERROR" or self.location == 'ERROR':
            self.address = "ERROR"
            self.phone = "ERROR"
            return
        try:
            street = self.YPsoup.find(attrs={'class':'street-address'}).text
            city = self.YPsoup.find(attrs={'itemprop':'addressLocality'}).text
            state = self.YPsoup.find(attrs={'itemprop':'addressRegion'}).text
            zip = self.YPsoup.find(attrs={'itemprop':'postalCode'}).text
            phone = self.YPsoup.find(attrs={'class':'phones phone primary'}).text

            self.address = str(street+' '+city+''+state+' '+zip)
            self.phone = phone
        except:
            self.address = "NOT FOUND"
            self.phone = "NOT FOUND"
class JOBError(ValueError): pass#custom ValueError
class JOB(object,YellowPages):
    
    companies_added = []
   
    def __new__(cls,job_list):
        #if the company already exists, dont create new object for it
        if str(job_list[0]) not in cls.companies_added:
            return super(JOB, cls).__new__(cls)#allow the instance to be created
        else:
            #print("{} already has JOB object".format(job_list[0]))
            raise JOBError ("JOB object not created for company because company already has JOB object that was created for it.") 
            
    """Take a job listing and turn into object"""
    def __init__(self,job_list):
        YellowPages.__init__(self)
        self.company = job_list[0]
        self.companies_added.append(str(job_list[0]))
        self.title = job_list[1]
        self.location = job_list[2]
        self.summary = job_list[3]
        self.address_phone()
        

#http://www.phaster.com/zip_code.html
city_zips = {'amherst ma':'01002','boston ma':'02108','wocester':'01601','hartford ct':'06101','providence ri':'02901','manchester nh':'03101',}
"""
              'anchorage ak':'99501',
              'springfield ma':'01101','albany ny':'02210', 
              'providence ri':'02901','charlotte nc':'28201','huntsville al':'35801',
              'phoenix az':'85001','little rock ar':'72201','sacramento ca':'94203',
              'denver co':'80201','dover de':'19901','washington dc':'20001','pensacola fl':'32501',
              'atlanta ga':'30301','honolulu hi':'96801','montpelier id':'83254',
              'chicago il':'60601','indianapolis in':'46201','des moines ia':'52801',
              'wichita ks':'67201','hazard ky':'41701','new orleans la':'70112',
              'freeport me':'04032','baltimore me':'21201','coldwater mi':'49036',
              'duluth mn':'55801','biloxi ms':'39530','st. louis mo':'63101','laurel mt':'59044',
              'hastings ne':'68901','reno nv':'89501','ashland nh':'03217',
              'livingston nj':'07039','santa fe':'87500','new york ny':'10001',
              'walhalla nd':'58282','cleveland oh':'44101','tulsa ok':'74101',
              'portland or':'97201','pittsburgh pa':'15201','newport ri':'02840',
              'camden sc':'29020','aberdeen sd':'57401','nashville tn':'37201',
              'austin tx':'78701','dallas tx':'75201','houston tx':'77001','san antonio tx':'78201',
              'logan ut':'84321','killington vt':'05751','altavista va':'24517',
              'bellevue wa':'98004','beaver wv':'25813','milwaukee wi':'53201',
              'pinedale wy':'82941'}
"""


"""
SINGLE
"""
#i = Indeed()
#print(i.get_all_jobs())
#print("COMPANIES")
#i.companies_posting()

"""
MULTI
"""

zips = [city_zips[key] for key in city_zips]#create a list of zip codes
searchOBJs = [Indeed() for z in zips]#create indeed objects for each zip code 
[searchOBJs[z].search('C# .NET software',zips[z]) for z in range(len(searchOBJs))]#run a search in each zip code 

""" ALL THE COMPANIES IN THE AREA WITH JOBS POSTED """
companies_posting = map(lambda z: z.companies_posting(), searchOBJs)#create a list of all the companies posting in the zipcode, staffing co.'s removed

""" ALL THE LISTINGS """
area_postings = map(lambda z: z.all_listings, searchOBJs)# All_listings has the [company, title, location, summary] for each listed job in the searched zipcode
#print(area_postings)
""" CONTACT INFO FOR JOBs """
""" NOTE: you won't be able to create JOB object more than once for the same company"""
""" DON'T USE LIST COMPREHENSION, IT can't handle an error being thrown, no way to do try/except"""
#job_details =[JOB(area_postings[0][z]) for z in range(len(area_postings[0]))]
job_details = []

#Setup Database
sql = SQLtable('NE_MyStaffingLeads.sqlite')
column_names_leads = ['company','address','phone']
sql.CreateTable('Companies',column_names_leads)

main_count = 0#Total number of companies found
for z in range(len(area_postings)):
        batch_count = 0#number of companies found in a zipcode
        for x in range(len(area_postings[z])):
            try:
                job_details.append(JOB(area_postings[z][x]))
                batch_count += 1
                main_count += 1
            except JOBError:
                #JOBError thrown if a company already has job object
                continue 
        [sql.AddRow('Companies',[job_details[z].company,job_details[z].address,job_details[z].phone])  for z in range((main_count - batch_count),main_count) ]


#create a list of leads that has one entry for each company posting jobs
#Leads = [[job_details[z].company,job_details[z].title,job_details[z].summary,job_details[z].address,job_details[z].phone] for z in range(0,len(job_details))]
#[print(Leads[x]) for x in range(len(Leads))]
#print(job_details)

#[sql.AddRow('Companies',[job_details[z].company,job_details[z].address,job_details[z].phone])  for z in range(0,len(job_details)) ]

#ADD THIS NEXT
#column_names_all = ['company','position','summary','location']
#sql.CreateTable('All_Openings',column_names_all)