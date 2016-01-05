'''
Simple chatroom


Reference
https://gist.github.com/tyt2y3/90ad9c8ed8409e08185e

additional references
https://docs.python.org/2/library/threading.html
http://blog.oddbit.com/2013/11/23/long-polling-with-ja/
http://zulko.github.io/blog/2013/09/19/a-basic-example-of-threads-synchronization-in-python/
http://www.laurentluce.com/posts/python-threads-synchronization-locks-rlocks-semaphores-conditions-events-and-queues/
'''

import time
import threading
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import sqlite3

#Global variable setup
message = None
sql = None
# HOSTING SETUP
HOST = '192.168.1.105'
PORT = 8000

class Chat_server(BaseHTTPRequestHandler):
    def log_message(self, *args):#https://docs.python.org/2/library/basehttpserver.html#BaseHTTPServer.BaseHTTPRequestHandler.log_message
        #standard function in BaseHTTPRequestHandler use for error handling
        pass
    '''
    To add support for an HTTP method in your request handler class, 
    implement the method do_METHOD(), replacing METHOD with the name of the HTTP method. 
    For example, do_GET(), do_POST(), etc. For consistency, the method takes no arguments. 
    All of the parameters for the request are parsed by BaseHTTPRequestHandler and stored as instance attributes of the request instance.
    '''

        
    def do_POST(self):#https://pymotw.com/2/BaseHTTPServer/
        print self.headers
        length = int(self.headers['Content-Length'])#this is just an interger represenation of total number of characters/data
        body = self.rfile.read(length)#rfile will start at the first piece of data in the post, you then want to read(length) pieces of data
        #for example if the post coming in is 'Hello' rfile starts at 'H' and you tell it to read 5 bytes and stop. so you get 'Hello'
        
        path = self.path#path is a method in BaseHTTPRequestHandler, it contains the request url path
        client_ip = self.client_address#get tuple in the form of: ('Client IP',port)
        print
        print "do_POST called by "  +str(client_ip)#for troubleshooting and learning
        
        if path.startswith('/'):#it will always start with '/'.  typical path format is: baseURL/home or baseURL/?parameter=value&other=some
            path = path[1:]#chops the '/ ' off of the path
            
        #    
        res = self.perform_operation(path, body, client_ip)
        if res:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            print "sending: " + str(res)
            self.wfile.write(res)#this ends up sending the response to all clients
        else:
            self.send_response(404)

    def do_GET(self):
        path = self.path#path is a method in BaseHTTPRequestHandler, it contains the request path
        client_ip = self.client_address
        sql.AddContact(client_ip)#add the IP address to DB
        
        print "do_GET called by "  +str(client_ip)
        if path.startswith('/'):#it always will.  typical path format: /?parameter=value&other=some
            path = path[1:]#chops the '/ ' off of the path
            print path
        res = self.get_html(path)#serve up the webpage
        if res:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(res)
        else:
            self.send_response(404)

    def perform_operation(self, path, body, client_ip):
        if path=='poll':
            print "perform_operation: POLL, by" +str(client_ip)
            return message.wait(body)
        elif path=='post':
            print "perform_operation: POST, by" +str(client_ip)
            return message.post(body,client_ip)
            

    def get_html(self, path):#called when visitor first goes to site or does refresh
        if path=='' or path=='index.html':#if you just go to the Host:Port for the server it will be path =='', not sure when 'index.html' would naturally come up
            print "returning index.html"
            return '''
           <body>
           
            <style>
            iframe {
                width: 400px;
                height: 600px;
            }
            </style>
            <iframe src="room.html"></iframe> <!--basically this is a webpage in a webpage tag-->
            
          
            <p>Test</p>
            
            
            </body>
             
            '''
        elif path=='room.html':#see that src="room.html", as soon as the homepage is rendered there is another request for room.html from inside the <iframe>, thats how this elif becomes true, the following javascript is then put in that <iframe>
            print "returning room.html"
            return '''
   <html>
   
             <body>
            
             <p><b>Press ENTER to send</b></p>
             
             <p>ChatBox</p>
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>
            <input id="input" type="text"/>
            <div id="nav" class="chatbox"></div>
            
            
            <script>
            $('#input').keypress(function(press_enter){
            if (press_enter.keyCode ==13){
                $.ajax('/post', {
                    method: 'POST',
                    timeout: 1000,
                    data: $('#input').val()
                    }); 
                    $('#input').val('');
                }
            });
            var last_message = '';
            
            var audio = new Audio('https://0.s3.envato.com/files/140747660/preview.mp3'); // this is used for the beep when a message is sent 
            
            (function poll() {
                $.ajax('/poll', {
                    method: 'POST',
                    timeout: 1000*60*10, //10 minutes
                    success: function(data){
                        $("<p "+data+"</p>").prependTo($("div"));//create new <p> tag on page with message inside
                        last_message = data;
                        audio.play(); // play the audio 'beep'
                        
                        
                        poll();
                    },
                    error: function(){
                        setTimeout(poll, 1000);
                    },
                    data: last_message
                });
            }());
            
            
            </script>
            </body>

</html>
   
  
            '''


class Message():
    def __init__(self):
        self.data = ''
        self.client_ip = ''
        self.time = 0
        self.event = threading.Event()
        self.lock = threading.Lock()
        self.event.clear()
        print "Message() called"

    def wait(self, last_mess=''):
        print "Message().wait called"
        if message.data != last_mess and time.time()-message.time < 60:
            # resend the previous message if it is within 1 min
            return message.data
        self.event.wait()
        
        print "Message().wait returned: " +message.data
        return message.data#, message.client_ip

    def post(self, data, client_ip):
        #when a post comes in check if the client_ip is in the database,
        #if not add them.  Then add the associated color to that persons text post
        
        print "Message().post called by " +str(client_ip)#for trouble shoot
        print "post data received was:" +data#for trouble shoot
        
     
        text_color = sql.color(client_ip)#get the associated text color choice, comes back as tuple
        text_color = text_color[0][0]#results from SQL return as tuple
        
        data = "style=color:"+text_color+">"+data
        
        
        with self.lock:# WITH statements explained: http://effbot.org/zone/python-with-statement.htm
            self.data = data
            self.client_ip = client_ip
            self.time = time.time()
            self.event.set()
            self.event.clear()
        return 'ok'


ThreadingMixIn.daemon_threads = True
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def start_server(handler, host, port):
    global message
    global sql
    sql = SQLtable('chatDB.sqlite')
    sql.create_table()
    message = Message()
    try:
        server = ThreadedHTTPServer((host, port), handler)
        print 'Serving at http://%s:%s' % (host, port)
        print 'created: '
        print server
        print ' '
        server.serve_forever()
   
    except KeyboardInterrupt:
        server.server_close()
        print time.asctime(), " Server Stopped %s:%s" % (host, port)


class SQLtable:
    #pass a db name and new database with a table named 'Contacts' with name/type of columns
    #will be created
    def __init__(self,database_file):
        self.database_file = database_file
        self.create_table()
    
    def create_table(self):
        #first create connection instance to the DB
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        #setup the string that will feed into the new column creation
        #colname type, colname type,
        type = 'BLOB'
        self.TableName = 'users'
        IP ='IP'
        COLOR ='COLOR'
        
        try:
            c.execute('CREATE TABLE {tn}({c1} {t} PRIMARY KEY,{c2} {t})'.format(tn=self.TableName,c1=IP,c2=COLOR, t=type))
            conn.commit()
        except:
            print "table name: %s exists" %self.TableName
            
    def AddContact(self,address_string,):
        #this method takes an IP address for a user and puts it in the database
        
        #Table is allways
        TableName = self.TableName
        IP = 'IP'
        userIP = repr(address_string[0])#convert to a string, using str() will NOT WORK, must use repr()
        
        print userIP
        print type(userIP)
        # create connection instance to the DB
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        
        searchIP = (userIP,)#the seach input MUST be a tuple
        
        # check if contact exists check to see if there is a match on a single row
        #of the same name and company, if so its probably the same person so skip
        c.execute("SELECT * FROM {} WHERE {} = ?".format(TableName,IP),searchIP)
        result = c.fetchall()
        print result
        #result will retun 0 if no match found
        if len(result)==0:
            #update with new contact info 
            COLOR = 'blue'
            
            #setup the contact info to write to database
            #these are defined at the begining of 'AddContact' method
            input = (userIP, COLOR)
            
            #next create a place holder for each value going to each column
            qmark = "?,?"
            
            #update the table with the info from the ContactInfo_object
            c.execute('''INSERT INTO {tn} VALUES ({q})'''.format(tn=TableName, q=qmark),input)
            #save changes to database
            conn.commit()
            conn.close()
            #notify user of update
            print "New IP address added to Database"
        else:
            #if result >0 this means contact exists so dont add
            print "IP Already Exists"
            
    def color(self, address_string):
        #Table is allways
        TableName = self.TableName
        IP = 'IP'
        COLOR = 'COLOR'
        
        # create connection instance to the DB
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        userIP = repr(address_string[0])#convert to a string, using str() will NOT WORK, must use repr()
        
        searchIP = (userIP,)#the seach input MUST be a tuple
        
        #database search for IP addresses text color choice
        c.execute('SELECT {c} FROM {tn} WHERE {ip} = ?'.format(c=COLOR,tn=TableName,ip=IP),searchIP) 
        result = c.fetchall()
        
        print result
        return result
        

if __name__ == '__main__':
    start_server(Chat_server, HOST, PORT)
    
    '''
    By doing the __main__ check, you can have the code only execute when you want to run the module as a program and not have it execute when someone just wants to import the module and call your functions themselves.
    '''