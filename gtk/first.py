#!/usr/bin/python

#self created modules
from generatekey import *
import database

#default modules
import re
import urllib
import random
import sys
import webbrowser
import base64
import pygtk;
pygtk.require('2.0');
import gtk;
from threading import Thread;

class WatchTV:
        def __init__(self):
                print "Generating Key...\n"
                self._key = Key()
     
                self.database = database.DataBase()
                
                
                self.baseLink = 'http://www.letmewatchthis.ch/'
                self.searchLink = '?search_keywords='
                self.keyLink = '&key='
                self.key = self._key.key
                self.sectionLink = '&search_section='
                self.debug = False

        def _GetHost(self):
                t_hosts = []
                for x in self.bs_data.findAll('script',{'type':'text/javascript'}):
                    try:
                        if x.string.startswith('document.writeln'):
                            t_hosts.append(x.string[18:][:-3])
                    except AttributeError:
                        pass
                return t_hosts
        
        def _GetViews(self):
                t_views = []
                for x in self.bs_data.findAll('span',{'class':'version_veiws'}):
                    t_views.append(x.string)
                return t_views
        
        def _GetLinks(self):
                t_links = []
                for x in self.bs_data.findAll('span',{'class':'movie_version_link'}):
                    if 'a href' in unicode(x('a')):
                        t_links.append(unicode(x('a'))[10:].replace('amp;','').split('"')[0])
                return t_links
        
        

        def keyExpirey(self,bsdata):
                regenerate = raw_input("Would you like to get a new key (y/n)?: " )
                if regenerate.lower() == 'y':
                    self._key.getKey()
                    self.key = self._key.key
                    print "Do these two match?"
                    print self.key
                    with open('key.txt','r') as f:
                        print f.readlines()[0]
                    t=raw_input("y/n?: ")
                    if t=='y':
                        print "horrah! returning to main menu, try searching again\n\n\n"
                        return;                

        def search(self,text=True):
                try:
                        self.section = int(raw_input("Movie (1) or TV (2): "))
                except ValueError:
                        print "Program Exiting. Enter a number next time -.- "
                        sys.exit(1)
                        
                #fit the format for website
                self.show = raw_input("What show do you want to search for: ").replace(" ","+")
                print "Searching...\n"
                
                #format URL properly
                self.link = self.baseLink + self.searchLink + self.show + self.keyLink + self.key + self.sectionLink + str(self.section)
                
                #open url
                self.url = urllib.urlopen(self.link).read()
                print 'asdas'
                
                #parse url with BS
                bsdata = BeautifulSoup(self.url)
                
                #check if key has expired (results will be ~50,000
                for x in bsdata.findAll("div", {"class":"number_movies_result"}):
                    digits = re.findall(r'[\d+\,*\d+]+', x.string)
                    if int(''.join(digits).encode('utf-8').replace(',','')) > 1000:
                        print 'We have detected that your key is expired.'
                        self.keyExpirey(bsdata)
                        return
                
                #Finds all shows that have codes
                self.code = re.findall(r'watch-(\d+)([\-*\w+]+)',self.url)
                
                #Displays Search Results
                for x in enumerate(self.code,1):
                        print x[0], x[1]

                #Pick which show you meant to search for
                self.id = raw_input('''\n\nYour query returned the following results above.
                            \nPlease indicate which show you chose with the number on the left: ''')
                                 
                #Sets self.final to the show/code you picked from above.
                for data in enumerate(self.code,1):
                        if int(self.id) == data[0]:
                                self.final = data[1]
         
                #writes the show/code to the database
                if text:
                        self.database.add(self.final[1].lower(), self.final[0])
                        
                #add show to current dictionary        
                self.database.db[self.final[1].lower()]=str(self.final[0])


        def watchShow(self,name, final=True):
            
                #http://www.letmewatchthis.ch/tv-5223-The-Mentalist
                self.tvLink = self.baseLink+'watch-'+str(self.database.db[name])+name
                
                #open link
                self.showData = urllib.urlopen(self.tvLink).read()
                
                #get season/episode
                pattern = re.findall(r'/season-(\d+)-episode-(\d+)',self.showData)
                
                #get episode name
                soup = BeautifulSoup(self.showData)
                
                if final:
                    #iterate through season/episodes & names
                    for x,y in zip(soup.findAll("span",{"class":"tv_episode_name"}),pattern):
                        
                        #print season/episode followed by name, formatted correctly
                        
                        '''
                        Current BUGS:
                        If episode has no name (blank on website), span class tv_episode_name does not exist
                        therefor there is no entry for the name and it skips it.
                        '''
                        print "Season {0} Episode {1} - {2}".format(y[0],y[1],x.string[2:].encode('utf-8').replace("&#039;","'"))
                        
                
                #list for easy access
                specshow = raw_input("Enter Season/Episode (ex: 5 1 for season 5 episode 1): ").split()
                
                #http://www.letmewatchthis.ch/tv-5223-the-mentalist/season-5-episode14
                finalLink = "{0}tv-{1}{2}/season-{3}-episode-{4}".format(self.baseLink,
                                                                        self.database.db[name],
                                                                        name,
                                                                        specshow[0],
                                                                        specshow[1]
                                                                        )
                #open episode to get links
                self.linkData = urllib.urlopen(finalLink).read()
                
                #parse data with BS
                self.bs_data = BeautifulSoup(self.linkData)
                
                #grab hosts
                hosts = self._GetHost()
                
                #grab views per host 
                views = self._GetViews()
                
                #grab links
                links = self._GetLinks()
                
                #print formatted host/views
                for w,x,y,z in zip(range(len(hosts)),hosts, views, links):
                    if x == "HD Sponsor":
                        continue
                    if not final:
                        print "{0}) {1} - {2} -- http://www.letmewatchthis.ch{3}".format(w,x,y,z)                   
                    else:
                        print "{0}) {1} - {2}".format(w,x,y)
                
                                                  
                link_choice = int(raw_input("Enter the number beside the link you want: "))
                directlink = base64.b64decode(links[link_choice].split("&")[2].encode('utf-8')[4:])
                webbrowser.open(directlink)                                              


shows = WatchTV()
print type(shows.database.display())

#create builder, load XML file created with glade
builder = gtk.Builder()
builder.add_from_file("1channel.ui")

#get window object
win = builder.get_object('window')

#list store - left box - contains shows/ids
l_shows = builder.get_object("l_shows")

#treeview1's object is l_shows
treeview1 = builder.get_object("treeview1")

#renders text to columns
render_text=gtk.CellRendererText()

#text=0 is g_chararray name: tv_name
tv_name=gtk.TreeViewColumn("tv name",render_text,text=0);
treeview1.append_column(tv_name);
#text=1 is g_ulong name: tv_id
tv_id=gtk.TreeViewColumn("id",render_text,text=1);
treeview1.append_column(tv_id);

def getItem(x):
    m=x.get_model();
    return (m.get_value( m.get_iter_from_string(str(x.get_cursor()[0][0])),0),
    m.get_value( m.get_iter_from_string(str(x.get_cursor()[0][0])),1))

def cb_shows(x):
    print getItem(x);
    
treeview1.connect("cursor-changed",cb_shows)

'''
with open('../database.txt','r') as f:
    a = f.readlines()

for x in a:
    t = x.split(":")
    l_shows.append((t[0].replace('-',' ').lstrip(),int(t[1].strip())))
'''



win.show_all()
gtk.main()

