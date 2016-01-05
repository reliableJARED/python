import imaplib
import email
import cups#CUPS (Common UNIX PRINTING STANDARD) this is printer driver library.
import os
import time


#login credentials for gmail
GMAIL_USER = 'youremailaddress@gmail.com'#email address
GMAIL_PASS = 'password'#use an application specific password from gmail: https://support.google.com/mail/answer/185833?hl=en
IMAGE_DIR_PATH = '/home/my/photo/directory/'#this is where it will save photos it downloads, LINUX/MAC format, change path style for windows

 '''
FUTURE EDIT NEEDED:
using str.isdigit() or some other
method need to search email inbox for num@ only email
addresses this way it can pick out messages from a text, and know the phone number
then associate that phone number with an account.

'''
class text2print:
    def __init__(self,GMAIL_USER, GMAIL_PASS):
        self.GMAIL_USER = GMAIL_USER
        self.GMAIL_PASS = GMAIL_PASS
        #setup imap protocal
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        #login
        self.mail.login(GMAIL_USER, GMAIL_PASS)
        
    def check_unread(self):
        self.mail.list()
        #Output: list of "folders" aka lables in gmail

        self.mail.select("inbox")#connect to inbox, could use some other folder
        
        #get uids of all messages
        result, data = self.mail.search(None, 'UNSEEN') 
        uids = data[0].split()#data[0] is a list of all message ID's from search result, ids are separated by a space in one giant long string.  use split() to isolate each one in a list
        
        #set uid to latest message, its the last one in the list
        #if this fails, no unread messages
        try:
            uid = uids[-1]
            return uid#this is the message ID for the latest message.  google and other email servers us unique ID's for every single email
        except:
            return False#if there is no latest image this will return
        
    def read_email(self,uid):
        #read the lastest message
        result, data = self.mail.fetch(uid, '(RFC822)')
        #turn into giant string
        m = email.message_from_string(data[0][1])
        #parse out the message, download the image attachment
        if m.get_content_maintype() == 'multipart': #multipart (photo attached) messages only
            for part in m.walk():#walk()is just an itterator method I think
                if part.get_content_maintype() =='image':
                    filename = part.get_filename()
                    print "downloading image {}".format(filename)
                    fp = open(filename, 'wb')#create a file for the image
                    fp.write(part.get_payload(decode=True))#save the image.  get_payload can do base64 and one other encoding, see python docs on the email library
                    fp.close()
                    
        return filename


def printer(image):
        conn = cups.Connection()#CUPS (Common UNIX PRINTING STANDARD) this is an old printer driver library.
        printers = conn.getPrinters()
        printer_name = printers.keys()[0]
        printqueuelength = len(conn.getJobs())
        file = IMAGE_DIR_PATH+image
        if(printqueuelength > 1):
            print "error"
                #Theres an error or still something in print queue 
        else:
            #print the image
            #YOUR PRINTER OPTIONS
            #in the terminal run: lpoptions -l
            #and run: lpoptions()
            #for availible printer options on specific printer
            conn.printFile(printer_name,file,"Optional Title",{'media':'4x6', 'MediaType':'PhotoPlusGloss2', 'fit-to-page':'True'})
            print "print job sent {i}".format(i=file)

inbox = text2print(GMAIL_USER,GMAIL_PASS)
counter = 0
while counter<=100:#set to while True: and remove counter to run forever
    new_mail = inbox.check_unread()
    if new_mail == False:
        print "no new images"
        time.sleep(15)#try again in 5 seconds
        pass
    else:
        image_file  = inbox.read_email(new_mail)
        printer(image_file)
        time.sleep(5)
        print "delete image file: {i}".format(i=image_file)
        os.remove(image_file)
        time.sleep(5)
        pass
    counter+=1 

