    #!/usr/bin/python2.6
import sqlite3 as sql
import glob

class DataBase:
        def __init__(self):
                self.database = "keys.db"
                self.db={}
                self.connection = sql.connect(self.database)
                self.cursor = self.connection.cursor()
                self.initialize()
                
        def initialize(self):
                for x in self.cursor.execute('SELECT * FROM shows'):
                        self.db[x[0]]=int(x[1])
                print "Database is ready!\n"
                #print self.db
                
        def display(self):
                print '---------------------------------------------'
                #print self.db
                for x in self.cursor.execute('SELECT * FROM shows'):
                        yield "Show: {0} - ID: {1}".format(x[0].replace('-',' ').strip(), x[1])
                print '---------------------------------------------'
                
        def yieldDB(self):
                for x in self.cursor.execute('SELECT * FROM shows'):
                        yield x

        #formatted name, formatted id
        def add(self, f_name, f_id):
                try:
                        self.db[f_name]
                        print "Show in database!"
                        return
                except:
                        pass #show not in database
                        
                self.cursor.execute('INSERT INTO shows (names, ids)VALUES(?,?)',(f_name,f_id))
                print "Show had been added!"
                self.db[f_name]=f_id
                self.commit()
        
        #deletion name
        def delete(self,d_name):
                if self.find(d_name):
                        d_name = '-'+d_name.replace(" ",'-')
                        print d_name
                        self.cursor.execute('DELETE FROM shows WHERE names = {0}'.format('"'+d_name+'"'))
                        self.cursor.execute('DELETE FROM shows WHERE ids = {0}'.format('"'+self.db[d_name]+'"'))
                        del(self.db[d_name])
                        print "Show has been deleted!"
                        self.commit()
                else:
                        print "Show does not exist in database"
        #nametofind
        def find(self, ntf):
                t_shows = [] #temporary show list
                for x in self.yieldDB():
                        if ntf == x[0].replace('-',' ').strip():
                                return True
                return False
        
        def commit(self):
                self.connection.commit()
                print "Database has been modified"
                
if __name__ == "__main__":
        tvshows = DataBase()        
        while True:
                c=raw_input("1)ADD\n2)DEL\n3)DP\nCHOICE: ")
                if int(c) == 1:
                        tvshows.add('-'+raw_input("NAME: ").replace(' ','-'),'5206')
                if int(c) == 2:
                        tvshows.delete(raw_input("NAME: "))
                if int(c) == 3:
                        tvshows.display()


