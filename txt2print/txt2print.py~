import imaplib
import email
import cups#CUPS (Common UNIX PRINTING STANDARD) this is printer driver library.
import os
import time


#login credentials for gmail
GMAIL_USER = 'youremailaddress@gmail.com'#email address
GMAIL_PASS = 'password'#use an application specific password from gmail: https://support.google.com/mail/answer/185833?hl=en
IMAGE_DIR_PATH = '/home/my/photo/directory/'#this is where it will save photos it downloads, LINUX/MAC format, change path style for windows

class text2print:
    def__init__


    


def printer(image):
        conn = cups.Connection()#CUPS (Common UNIX PRINTING STANDARD) this is printer module.
        printers = conn.getPrinters()#list all connected printers
        printer_name = printers.keys()[0]
        printqueuelength = len(conn.getJobs())#used to determine if que still has pending print
        file = IMAGE_DIR_PATH+image#see IMAGE_DIR_PATH above
        if(printqueuelength > 1):
            print "error"
                #FIX.
                #this is only set to check for existing jobs for personal use.  This should be made more robust with waits etc if a job is in que already
        else:
            #print the image
            #DEFINE YOUR PRINTER OPTIONS
            #hard coded to print 4x6 photos at the moment, again just because this was personal project with specific task
            #in the terminal run: lpoptions -l
            #and run: lpoptions()
            #for availible printer options on specific printer
            conn.printFile(printer_name,file,"Optional Title",{'media':'4x6', 'MediaType':'PhotoPlusGloss2', 'fit-to-page':'True'})
            print "print job sent {i}".format(i=file)

inbox = text2print(GMAIL_USER,GMAIL_PASS)#create instance of gmail monitor
counter = 0#just for testing, if this was really going to be live, change to while True: or don't use that at all and simply do some trigger for the sequence of events to check for photos

while counter<=100:#set to while True: and remove counter to run forever
    new_mail = inbox.check_unread()
    if new_mail == False:
        print "no new images"
        time.sleep(15)#try again in 15 seconds
        #it would be better if the mail server could push the new message alert out, not sure if that can be done.  i.e. long polling type connection.
        pass
    else:
        image_file  = inbox.read_email(new_mail)
        printer(image_file)#FIX NEEDED: there is no error handling here.I didn't need for personal use, but it should deal with a pritner issue.  use a Try: Except: 
        time.sleep(5)#give the printer some time before deleting file
        print "delete image file: {i}".format(i=image_file)
        os.remove(image_file)#not needed if you wanted to save all the photos it downloaded
        #could also consider moving emails that had attached photos to a 'printed photo' folder in gmail after they were printed
        #in the text2 print class use something like: self.mail.copy(latest_email_id, 'Printed')
        time.sleep(5)#
        pass
    counter+=1 

