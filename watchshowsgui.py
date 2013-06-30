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
        
        
        
        def genKey(self):
                self._key.getKey()
                self.key = self._key.key
                return True               
        
        
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
                
                #Yields Search Results
                for x in self.code:
                        yield x


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
                    yield (w,x,y,z)
                                                

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
#button option_close in win1
option_close = builder.get_object("option_close")
#button b_delete
b_delete = builder.get_object("b_delete")

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

window_2_model = treeview5.get_model()


#RELOAD SHOWS
def refresh_db():
    l_shows.clear()
    for x in shows.database.yieldDB():
        l_shows.append((x[0].replace('-',' '),x[1]))    

#GET ITEMS IN TREEVIEWS
def getItem(x):
    m_shows=x.get_model();
    return (m_shows.get_value( m_shows.get_iter_from_string(str(x.get_cursor()[0][0])),0),
    m_shows.get_value( m_shows.get_iter_from_string(str(x.get_cursor()[0][0])),1))
def getItem2(x,i):
    m=x.get_model();
    return m.get_value( m.get_iter_from_string(str(x.get_cursor()[0][0])),i)



#KEY VERIFICATION
def thread_k():
    if shows.genKey() == True:
        gtk.gdk.threads_enter()
        keyd_ok = keyd.add_button("ok",gtk.RESPONSE_CLOSE)
        keyd_ok.connect("clicked",lambda x: keyd.hide())
        keyd.set_markup("Verified!")
        gtk.gdk.threads_leave()
def key_start():
    global keyd
    keyd = gtk.MessageDialog(win);
    keyd.set_markup("Please wait while we get your key from the website.")
    
    threading.Thread(target=thread_k).start()
    keyd.run()


#DELETE SHOWS
def delshow(x):
    print getItem(treeview1)
    shows.database.delete(getItem(treeview1)[0])
    conf.hide()
def cb_delete(x):
    global conf
    conf = gtk.MessageDialog(win)
    conf.set_markup("Are you sure you want to delete this show?")
    conf.add_button("yes",gtk.RESPONSE_CLOSE).connect("clicked", delshow)
    conf.add_button("no",gtk.RESPONSE_CLOSE).connect("clicked", lambda x: conf.hide())
    conf.run()
    refresh_db()
    

#HIDE WIN2 (needed so win2 doesn't destruct everything in it)        
def cb_close_win1(x):
    win2.hide()


#WRITE SEARCHED SHOWS TO DB
def cb_write(x):
    showcode = getItem(treeview5)
    shows.database.add(showcode[0].lower(), int(showcode[1]))
    shows.database.db[showcode[0].lower()]=int(showcode[1])
    suc = gtk.MessageDialog(win)
    suc.set_markup("Show has been successfully added!")
    suc.add_button("ok",gtk.RESPONSE_CLOSE).connect("clicked",lambda x: suc.hide())
    refresh_db()
    suc.run()


#ERROR DIALOG
def cb_error(x):
    er = gtk.MessageDialog(win);
    er.set_markup("Please enter text in the search box");
    er_ok = er.add_button("ok",gtk.RESPONSE_CLOSE)
    er_ok.connect("clicked",lambda x: er.hide())
    if len(t_search.get_text()) <= 0:
        er.run()
        return True


#SEARCH FOR SHOWS TO ADD
m_options = treeview5.get_model()
def thread_o():
    m_options = window_2_model
    m_options.clear()
    print m_options
    for x in shows.search(t_search.get_text()):
        gtk.gdk.threads_enter()
        m_options.append((x[1],int(x[0])))
        gtk.gdk.threads_leave()
def cb_add(x):
    if (cb_error(x)):
        return
    threading.Thread(target=thread_o).start()
    win2.show_all()


#WHEN LINK IS CLICKED OPEN IN WEB BROWSER
def cb_links(x):
    for y in hlv:
        if getItem(treeview4)[1] in y:
            webbrowser.open(base64.b64decode(y[3].split("&")[2].encode('utf-8')[4:]))



#WHEN EPISODE IS CLICKED LOAD LINKS
def thread_l():
    m_links = treeview4.get_model()
    m_links.clear()
    s_id = getItem(treeview2)[1]
    e_id = getItem(treeview3)[1]
    
    
    
    
    #HostLinksViews
    global hlv
    hlv=[]
    show = getItem(treeview1)[0]
    for a,b,c,d in shows.watchShow(getItem(treeview1)[0].replace(' ','-'),(s_id,e_id)):
        gtk.gdk.threads_enter()
        if show!=getItem(treeview1)[0]:
            gtk.gdk.threads_leave()
            break
        if e_id != getItem(treeview3)[1]:
            gtk.gdk.threads_leave()
            break
        m_links.append(("Host: {0} - {1}".format(b,c),int(a)))
        hlv.append((a,b,c,d))
        gtk.gdk.threads_leave()
def cb_episodes(x):
    threading.Thread(target=thread_l).start()



#WHEN SEASON IS CLICKED LOAD EPISODES
def cb_seasons(x):
    m_episode = treeview3.get_model()
    m_episode.clear()
    treeview4.get_model().clear()
    for x in sen:
        if int(x[0])==getItem2(treeview2,1):
            m_episode.append(("Episode {0} - {1}".format(x[1],x[2][1:].encode('utf-8').replace("&#039;","'")),int(x[1])))




        
#WHEN SHOW IS CLICKED LOAD SEASONS
def thread_e(x):
    #get listshow for treeview2 and clear
    m_season = treeview2.get_model()
    m_season.clear()
    
    #clear other liststores when switching shows
    treeview3.get_model().clear()
    treeview4.get_model().clear()
    
    #variable for nulling double repeat
    repeat=''
    
    #SeasonEpisodeName
    global sen
    sen=[]
    
    #sets current show to the
    show=getItem(treeview1)[0];
    
    #a = season number
    #b = episode number
    #c = episode title
    for a,b,c in shows.e_request(show.replace(' ','-')):
        #grab GTK lock
        gtk.gdk.threads_enter()
        
        #if the show dodes not match the current show (clicked more than once)
        if(show!=getItem(treeview1)[0]):
            #unlocks thread and breaks
            gtk.gdk.threads_leave();
            break
            
        #multiple repeats due to 2 for loops
        if(repeat=='' or repeat!=a):
            m_season.append(("Season {0}".format(a),int(a)))
            repeat=a
        
        #add data to list to minimize number of requests
        sen.append((a,b,c))
        
        #unlocks thread
        gtk.gdk.threads_leave();
def cb_shows(x):
    threading.Thread(target=thread_e,args=(x,)).start();

treeview1.connect("cursor-changed",cb_shows)
treeview2.connect("cursor-changed",cb_seasons)
treeview3.connect("cursor-changed",cb_episodes)
treeview4.connect("cursor-changed",cb_links)
b_add.connect("clicked",cb_add)
b_search.connect("clicked",cb_error)
option_add.connect("clicked",cb_write)
option_close.connect("clicked",cb_close_win1)
b_delete.connect("clicked",cb_delete)


for x in shows.database.yieldDB():
    l_shows.append((x[0].replace('-',' '), x[1]))



win.show_all()
gtk.gdk.threads_init()
key_start()

gtk.main()


