#!/usr/bin/python
 # -*- coding: utf-8 -*-
 
 
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

#third party modules
from BeautifulSoup import BeautifulSoup, SoupStrainer


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
                
#show instance
global shows
shows = WatchTV()


def mainm():
        while True:
                main_menu = int(raw_input('''Choose a category:\n
1)Watch TV!
2)Database Options
3)Key Options
Choice: '''))
                if main_menu == 1:
                        tv_options()
                if main_menu == 2:
                        database_options()
                if main_menu == 3:
                        key_options()
                

def tv_options():
        while True:
                tv_opt = int(raw_input('''What would you like to do:\n
1)Add show to database
2)View TV Shows
3)Watch TV
4)Main Menu
Choice: '''))
                if tv_opt == 1:
                        shows.search()
                if tv_opt == 2:
                        shows.database.display()
                if tv_opt == 3:
                        _show = raw_input("Enter show name: ")
                        _show = '-'+_show.replace(' ','-').strip().lower()
                        if _show in shows.database.db:
                                print _show, shows.database.db[_show]
                                shows.watchShow(_show)
                if tv_opt == 4:
                        return

def database_options():
        while True:
                db_opt = int(raw_input('''What would you like to do:\n
1)Check if a show is in the database
2)Delete show from database
3)View Database
4)Main Menu
Choice: '''))
                if db_opt == 1:
                        if (shows.database.find(raw_input("Enter show: ").lower())):
                                print "Show in database!"
                        else:
                                print "Show not in database!"
                if db_opt == 2:
                        shows.database.delete(raw_input("Enter show: ").lower())
                if db_opt == 3:
                        shows.database.display()
                if db_opt == 4:
                        return
                
def key_options():
        while True:
                key_opt = int(raw_input('''What would you like to do: \n
1)View key
2)Grab new key (expirey)
3)Main Menu
Choice: '''))
                if key_opt == 1:
                        print "Current key: ",shows.key
                if key_opt == 2:
                        shows._key.getKey()
                        shows.key = shows._key.key
                        print "You have successfully gotten a key"
                if key_opt == 3:
                        return
mainm()
