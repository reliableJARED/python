import sqlite3

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
            print "Error! send column names as list: FAILED SQLtable.CreateTable({t},{c})".format(t=TableName, c=type(columns))
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

        
    def AddRow(self,TableName = 'xyz_default_table',RowData=['data'],duplicate=0):
        #duplicate =0 will NOT enter duplicate row data if RowData is found to exist in the table
        #to enter duplicate data pass 1 after RowData
        
       
        if TableName == 'xyz_default_table':
            print "Error: no table name passed to AddRow"
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
            print RowFind[0]
            for col in range(0,col_count):
                search = search +(str(col_name[col] +" = ?"))#search format: column_name = ?
                find += (RowFind[0],) #match rowfind entries for each column being searched 
                if col_count != (col+1):
                    search = search + (' OR ')#add an AND if there is another column format: column_name1 = ? AND column_name2 = ?
            
            print search #print for TS
            print find
                    
            #check to see if there is a match on a single row in our tabel
            c.execute("SELECT * FROM {tn} WHERE {search}".format(tn=TableName,search=search),find)#RowData will replace ? in search with the input data
            result = c.fetchall()
            return result#result is a tuple, each item is the contents of a row [(matching row1),(matching row2), ...]
        
        print "bad query parameters"
            

if __name__ == '__main__':#test stuff if this module is the main program and not being imported    
    sql = SQLtable('MyDB.sqlite')
    column_names = ['one','two','three']
    sql.CreateTable('My_Table',column_names)
    column_name = ['column1',]
    sql.CreateTable('my_second_table',column_name)
    sql.CreateTable('my_thrid_table','column_name')
    sql.AddRow('My_Table',['apple','pear','banana'])
    sql.AddRow('my_second_table',['peach'])
    sql.AddRow('my_second_table',['berry'])
    result = sql.Query('My_Table',['pear'])
    print result