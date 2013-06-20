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
import threading
from BeautifulSoup import BeautifulSoup

class WatchTV:
        def __init__(self):
                print "Generating Key...\n"
                self._key = Key()
     
                self.database = database.DataBase()
                
                
                self.baseLink = 'http://www.primewire.ag/'
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
        
        
        def keyExpirey(self):
                bsdata = BeautifulSoup(self.url)
                
                #check if key has expired (results will be ~50,000)
                for x in bsdata.findAll("div", {"class":"number_movies_result"}):
                    digits = re.findall(r'[\d+\,*\d+]+', x.string)
                    if int(''.join(digits).encode('utf-8').replace(',','')) > 1000:
                        return True
                return False
                
        
        def search(self,show,text=True):
                #format show name
                show = show.replace(" ","+")
                #format URL properly
                self.link = self.baseLink + self.searchLink + show + self.keyLink + self.key + self.sectionLink + '2'
                
                #open url
                self.url = urllib.urlopen(self.link).read()
                
                #Finds all shows that have codes
                self.code = re.findall(r'watch-(\d+)([\-*\w+]+)',self.url)
                
                #Displays Search Results
                for x in self.code:
                        yield x

                #Pick which show you meant to search for
                #self.id = raw_input('''\n\nYour query returned the following results above.
                            #\nPlease indicate which show you chose with the number on the left: ''')
                                 
                #Sets self.final to the show/code you picked from above.
                '''
                for data in enumerate(self.code,1):
                        if int(self.id) == data[0]:
                                self.final = data[1]
                '''
                #writes the show/code to the database
                '''
                if text:
                        self.database.add(self.final[1].lower(), self.final[0])
                        
                #add show to current dictionary        
                self.database.db[self.final[1].lower()]=str(self.final[0])
                '''

        def e_request(self,name):
                #http://www.primewire.ag/tv-5223-The-Mentalist
                self.tvLink = self.baseLink+'watch-'+str(self.database.db[name])+name
                
                #open link
                self.showData = urllib.urlopen(self.tvLink).read()
                
                #get season/episode
                pattern = re.findall(r'/season-(\d+)-episode-(\d+)',self.showData)
                
                #get episode name
                soup = BeautifulSoup(self.showData)
                
                #iterate through season/episodes & names
                for x,y in zip(soup.findAll("span",{"class":"tv_episode_name"}),pattern):
                    
                    #print season/episode followed by name, formatted correctly
                    
                    '''
                    Current BUGS:
                    If episode has no name (blank on website), span class tv_episode_name does not exist
                    therefor there is no entry for the name and it skips it.
                    '''
                    #print "Season {0} Episode {1} - {2}".format(y[0],y[1],x.string[2:].encode('utf-8').replace("&#039;","'"))
                    yield (y[0],y[1],x.string[2:].encode('utf-8').replace("&#039;","'"))

        def watchShow(self, name, specshow):
            

                
                #list for easy access
                #specshow = raw_input("Enter Season/Episode (ex: 5 1 for season 5 episode 1): ").split()
                
                #http://www.primewire.ag/tv-5223-the-mentalist/season-5-episode14
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
                    '''
                    if not final:
                        print "{0}) {1} - {2} -- http://www.primewire.ag{3}".format(w,x,y,z)  
                    '''
                    
                    #print "{0}) {1} - {2}".format(w,x,y)
                    yield (w,x,y,z)
                                                  
                #link_choice = int(raw_input("Enter the number beside the link you want: "))
                #directlink = base64.b64decode(links[link_choice].split("&")[2].encode('utf-8')[4:])
                #webbrowser.open(directlink)                                              


shows = WatchTV()


#create builder, load XML file created with glade
builder = gtk.Builder()
builder.add_from_file("gtk/1channel.ui")

#get window object
win = builder.get_object('window')
win.maximize()

#get window1 object
win2 = builder.get_object("window1")
win2.set_position(gtk.WIN_POS_CENTER)


#renders text to columns
render_text=gtk.CellRendererText()



#list store - left box - contains shows/ids
l_shows = builder.get_object("l_shows")
#list store - second box - seasons
l_seasons = builder.get_object("l_seasons")
#list store - third box - episode/episode names
l_episodes = builder.get_object("l_episodes")
#list store - last box - links
l_links = builder.get_object("l_links")



#object l_shows
treeview1 = builder.get_object("treeview1")
#object l_seasons
treeview2 = builder.get_object("treeview2")
#object l_episodes
treeview3 = builder.get_object("treeview3")
#object l_links
treeview4 = builder.get_object("treeview4")
#object l_options
treeview5 = builder.get_object("treeview5")



#button b_add
b_add = builder.get_object("b_add")
#button b_search
b_search = builder.get_object("b_search")
#button option_add in win1
option_add = builder.get_object("option_add")


#entry t_search
t_search = builder.get_object("t_search")


#text=0 is gchararray tv_name
tv_name=gtk.TreeViewColumn("tv name",render_text,text=0)
treeview1.append_column(tv_name)
#text=1 is gulong tv_id
tv_id=gtk.TreeViewColumn("id",render_text,text=1)
treeview1.append_column(tv_id)


#text=0 is gchararray s_name
tv_season = gtk.TreeViewColumn("season",render_text, text=0)
treeview2.append_column(tv_season)


#text=0 is gchararary e_name
tv_episode = gtk.TreeViewColumn("episode",render_text,text=0)
treeview3.append_column(tv_episode)


#text=0 is gchararray l_name
tv_links = gtk.TreeViewColumn("links",render_text,text=0)
treeview4.append_column(tv_links)

#text=0 is gchararray o_name
tv_options = gtk.TreeViewColumn("results",render_text,text=0)
treeview5.append_column(tv_options)

def getItem(x):
    m_shows=x.get_model();
    return (m_shows.get_value( m_shows.get_iter_from_string(str(x.get_cursor()[0][0])),0),
    m_shows.get_value( m_shows.get_iter_from_string(str(x.get_cursor()[0][0])),1))
def getItem2(x,i):
    m=x.get_model();
    return m.get_value( m.get_iter_from_string(str(x.get_cursor()[0][0])),i)
    
def thread_e(x):
    m_season = treeview2.get_model()
    m_season.clear()
    treeview3.get_model().clear()
    treeview4.get_model().clear()
    
    repeat=''
    #SeasonEpisodeName
    global sen
    sen=[]
    #iterate over values, add seasons to liststore, episodes to other liststore
    show=getItem(x)[0];
    
    for a,b,c in shows.e_request(show.replace(' ','-')):
        #grab GTK lock
        gtk.gdk.threads_enter()
        
        
        if(show!=getItem(x)[0]):
            #unlocks (due to clicking more than 1 show)
            gtk.gdk.threads_leave();
            break
            
        #multiple repeats due to 2 for loops
        if(repeat=='' or repeat!=a):
            m_season.append(("Season {0}".format(a),int(a)))
            repeat=a
        
        #add data to list so no more request
        sen.append((a,b,c))
        
        #unlocks
        gtk.gdk.threads_leave();

def thread_l():
    m_links = treeview4.get_model()
    m_links.clear()
    s_id = getItem(treeview2)[1]
    e_id = getItem(treeview3)[1]
    
    #HostLinksViews
    global hlv
    hlv=[]
    
    for a,b,c,d in shows.watchShow(getItem(treeview1)[0].replace(' ','-'),(s_id,e_id)):
        gtk.gdk.threads_enter()
        m_links.append(("Host: {0} - {1}".format(b,c),int(a)))
        hlv.append((a,b,c,d))
        gtk.gdk.threads_leave()
    
def thread_o():
    m_options = treeview5.get_model()
    for x in shows.search(t_search.get_text()):
        gtk.gdk.threads_enter()
        print type(x),x
        #print t_search.get_text().replace(" ",'+')
        m_options.append((x[1],int(x[0])))
        gtk.gdk.threads_leave()
        
    
def cb_shows(x):
    #starts thread_e function in a new thread
    threading.Thread(target=thread_e,args=(x,)).start();
    
def cb_seasons(x):
    m_episode = treeview3.get_model()
    m_episode.clear()
    treeview4.get_model().clear()
    for x in sen:
        if int(x[0])==getItem2(treeview2,1):
            m_episode.append(("Episode {0} - {1}".format(x[1],x[2][1:].encode('utf-8').replace("&#039;","'")),int(x[1])))
    
def cb_episodes(x):
    threading.Thread(target=thread_l).start()
    

def cb_links(x):
    for y in hlv:
        if getItem(treeview4)[1] in y:
            webbrowser.open(base64.b64decode(y[3].split("&")[2].encode('utf-8')[4:]))



def cb_error(x):
    test = gtk.MessageDialog(win);
    test.set_markup("Please enter text in the search box");
    test_ok = test.add_button("ok",gtk.RESPONSE_CLOSE)
    test_ok.connect("clicked",lambda x: test.hide())
    if len(t_search.get_text()) <= 0:
        test.run()
        return True
    
def cb_add(x):
    if (cb_error(x)):
        return
    win2.show_all()
    threading.Thread(target=thread_o).start()
    



treeview1.connect("cursor-changed",cb_shows)
treeview2.connect("cursor-changed",cb_seasons)
treeview3.connect("cursor-changed",cb_episodes)
treeview4.connect("cursor-changed",cb_links)
b_add.connect("clicked",cb_add)
b_search.connect("clicked",cb_error)

for x in shows.database.yieldDB():
    l_shows.append((x[0].replace('-',' '), x[1]))



win.show_all()
gtk.gdk.threads_init()
gtk.main()

