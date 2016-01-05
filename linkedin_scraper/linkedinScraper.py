import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
import urllib2 # Used to open the html document
from bs4 import BeautifulSoup
import sqlite3
import requests
import random
import time

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
        """ DEAL WITH GOOGLE Captcha """
        if link.status_code == 503:#response is 503 when you get a captcha
            print "********Original URL*************"
            print url
            print "**********************"
            captcha_image_id = str(link.content)
            captcha_image_id = captcha_image_id.split("/sorry/image?")
            captcha_image_id = captcha_image_id[1]
            captcha_image_id = captcha_image_id.split("&")
            captcha_image_id = captcha_image_id[0]
            '''
                https://ipv4.google.com/sorry/image?id=4909973586317130873&hl=en
                to get the image alone, replace id
            '''
            print " "
            print "*********  ATTENTION REQUIRED!   **********"
            print "please follow the link below, then enter the captcha answer"
            print 'https://ipv4.google.com/sorry/image?{captcha}&hl=en'.format(captcha=captcha_image_id)
            print ''
            captcha_answer = raw_input('Enter Captcha: ')
            url = url+'&{id}&captcha={ans}&submit=Submit'.format(id=captcha_image_id,ans=captcha_answer)
            print 'New URL:'
            #change the url to go to the CaptchaRedirect
            url = url.replace("IndexRedirect", "CaptchaRedirect",1)#replaces first instance
            print url
            print "**********************"
            link = requests.get(url,headers=headers,allow_redirects=True)
            print link.status_code
            print link.cookies

        resultURL = link.url#used to cycle through pages of google results
        try:
            return BeautifulSoup(page,"html.parser"), resultURL
        except:
            return "ERROR"
            
class LinkedinProfileDataExtractor(WebpageParser):

    def __init__(self,url):
        WebpageParser.__init__(self)
        self.LIsoup, resultURL = self.MKsoup(url)
        self.profile = url
        try:
            self.name()
            self.job()
            self.company()
            self.location()
        except:
            self.location = 'ERROR'#used so YP search knows not to search
            self.name = 'ERROR'#used so YP search knows not to search
            self.company = 'ERROR'#used so YP search knows not to search
    def name(self):
        name = self.LIsoup.find(attrs={'class':'fn'}).text
        self.name = name
        
    def job(self):
        job = self.LIsoup.find(attrs={'class':'position'})#find all the jobs
        job = job.find(attrs={'class':'item-title'}).text#get latest
        self.job = job
    
    def company(self):
        company = self.LIsoup.find(attrs={'class':'position'})
        company = company.find(attrs={'class':'item-subtitle'}).text#get latest company
        self.company = company
    
    def location(self):
        try:
            loc = self.LIsoup.find(attrs={'class':'locality'}).text
        except:
            loc = "NO LOCACTION"
            print self.profile
        self.location = loc
                
class Extract(LinkedinProfileDataExtractor):
    
    def __init__(self,url):
        LinkedinProfileDataExtractor.__init__(self,url)
        self.key_1 = 'search_terms'
        self.key_2 = 'geo_location_terms'
        self.address_phone()
        
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
   
class google(WebpageParser):
    
    def __init__(self,hit_count):
        self.hit_count = hit_count
        WebpageParser.__init__(self)
        self.urls = []    #this variable will hold a list of the url's returned from the search

    def search(self,terms,page=0):
        #keys for google
        key1 = 'start'
        key2 = 'num'
        key3 = 'client'
        key4 = 'channel'
        key5 = 'q' #search terms
        key6 = 'ie'
        key7 = 'oe'
        key8 = 'as_q'#https://developers.google.com/custom-search/docs/xml_results?hl=en#Advanced_Search_Query_Parameters
        
        #value2 is special
        #max hits per page is 100
        if (int(self.hit_count)>=100):
            #RUN THE MULTIPAGE PROCESS FUNCTION ONCE BUILT
            value2 = 100
        else:
            value2 = self.hit_count
            
        value1 = page*self.hit_count
        value3 = 'ubuntu'
        value4 = 'fs'
        value5_a= terms
        value5_b= ' site:linkedin.com/pub'
        value6 = 'utf-8'
        value7 = 'utf-8'
        value8 = 'Springfield, Massachusetts'#value for sub-search of results if needed
           
        #setup the payload for the google search   
        payload = {key1:value1,key2:value2,key3:value3,key4:value4,key5:value5_a+value5_b,key6:value6, key7:value7}
        self.Gsoup, self.searchURL = self.MKsoup('https://google.com/search',payload)
        #self.resultURLs(Gsoup)
    
    def resultURLs(self,Gsoup):
        #print Gsoup
        #extract the urls of search results from a google page
        for result in Gsoup.find_all("h3","r",'a'):
            #go to <h3 class='r"><a> tag where href is stored pull out the link
            name = result.find('a',href=True)
            #grab the link from a tag, and prettify it with 2 string splits
            #to isolate the true url link 
            link = name['href']
            link = ((link.split("rl?q=")[1]).split("&sa"))[0]#extract the actual URL from the href
            self.urls.append(link)
        print self.urls
        self.remove_badURLS()

    def remove_badURLS(self):
        #function takes linkedin search result urls
        #and removes and directory or potential duplicaate /in links
        url_list = self.urls
        url_list2=[]
        url_list3=[]
        url_list4=[]

        directory = "/dir/"
        in_profile = "/in/"
        percent = "%"
        
        for x in range(0,len(url_list)):
            #remove links that are directory
            if url_list[x].find(directory) == -1:
                url_list2.append(url_list[x])
        for x in range(0,len(url_list2)):
            #remove links that are "/in/" to prevent dup with /pub/
            if url_list2[x].find(in_profile) == -1:
                url_list3.append(url_list2[x])        
        
        for x in range(0,len(url_list3)):
            #remove links that contain "%" they are almost always bad
            if url_list3[x].find(percent) == -1:
                url_list4.append(url_list3[x])   
        #return a list of urls
        self.urls = url_list4


class SQLtable:
    def __init__(self,database_file):
        self.database_file = database_file
    
    def create_table(self,TN):#Create the contact table in the database
        conn = sqlite3.connect(self.database_file)
        #create instance of the cursor
        c = conn.cursor()
        #create a name for the table
        TableName = TN
        #setup the column names and data type for the table
        type = 'TEXT'
        name ='Name'
        job ='Job'
        company ='Company'
        location ='Address'
        phone = 'Phone Number'
        linkedin = 'LinkedIn'
        try:
            c.execute('CREATE TABLE {tn}({c1} {t},{c2} {t},{c3} {t},{c4} {t},{c5} {t},{c6} {t})'.format(tn=TableName,c1=name,c2=job,c3=company,c4=location,c5=phone,c6=linkedin, t=type))
            conn.commit()
        except:
            print "table name: %s exists" % TableName
            
    def AddContact(self,TN,ContactInfo_object):
        #this method requires an object from the linkedin scrape
        #it then writes the atributes of the persons contact info
        #to the database.
        TableName = TN
        name = ContactInfo_object.name
        if name == 'ERROR':
            print "appears this record had an error when linkedin profile was extracted"
            return
        job = ContactInfo_object.job
        company = ContactInfo_object.company
        location = ContactInfo_object.address
        phone = ContactInfo_object.phone
        linkedinURL =  ContactInfo_object.profile
        #first create connection instance to the DB
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        
        # check if contact exists in database already.  check to see if there is a match on a single row
        #of the same name and company, if so its probably the same person so skip
        search = 'Name = ? AND Company = ?'
        data = (name,company)#must be tuple when replacing ?'s with data
        c.execute("SELECT * FROM {tn} WHERE {s}".format(tn=TableName,s=search),data)
        result = c.fetchall()
        #result will retun 0 if no match found
        if len(result)==0:
            #put all of the contacts info in a single variable
            #these are defined at the begining of this method
            input = (name, job, company, location,phone,linkedinURL)
            
            #next create a place holder for each value going to each column
            qmark = "?,?,?,?,?,?"
            
            #update the table with the info from the ContactInfo_object
            c.execute('''INSERT INTO {tn} VALUES ({q})'''.format(tn=TableName, q=qmark),input)
            #save changes to database
            conn.commit()
            conn.close()
            #notify user of update
            print "{} added to Database".format(name)
        else:
            #if result >0 this means contact exists so dont add
            print "{} Already Exists in Database".format(name)


if __name__ == '__main__':#test stuff if this module is the main program and not being imported    
    g = google(100)#hits per page
    database = SQLtable('HR_ContactList.sqlite')
    database.create_table('CONTACTS')
    pages = 4
    """
    AROUND(x) is used for word proxmity where x is the max number of words separating the search terms on the page.
    using AROUND() helps prevent the 'people also viewed' section of a linkedin page causing false hits.
    -*/dir/* is used to remove linkedin directory results
    
    """
    print "finding linkedin profiles"
    g.search('software "hr manager"  AND ", massachusetts" -*/dir/*')
    g.resultURLs(g.Gsoup)#extract page 1 of results

    #extract additional pages
    for page in range(1,pages):#start at 1 which is really page 2.  page 1 is automatical done in g.search() call
        Gsoup, url = g.MKsoup(g.searchURL+"&start="+str(g.hit_count*page))
        g.resultURLs(Gsoup)
        print "page {} done".format(page+1)
    print "total urls {}".format(len(g.urls))
    
    for p in range(0,len(g.urls)):
        try:
            profile = Extract(str(g.urls[p]))
        except:
            continue
            print "error with profile = Extract(str(g.urls[p]))"

        try:
            print profile.name
            print profile.job
            print str(profile.company)
            print profile.phone
            print profile.address
            print profile.profile#linkedin profile url
            database.AddContact('CONTACTS',profile)
        except:
            print "error printing data, could be due to strange characters"
        print "********************"

    