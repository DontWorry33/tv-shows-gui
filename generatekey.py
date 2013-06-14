import re
import urllib
import os

class Key:
    def __init__(self):
        self.key = ''
        self.valid = False
        self.isValid()
        #self.getKey()

        
    def isValid(self):
        if os.path.isfile('key.txt'):
            with open('key.txt','r') as f:
                t_key = f.readlines()[0]
                
            if len(t_key) >= 1:
                self.valid = True
                self.key = t_key
                #print self.key
                return self.valid
                
            else:
                self.valid = False
                self.getKey()
                
        if len(self.key) <= 0:
            self.valid = False
            self.getKey()


    def getKey(self):
        source = 'http://www.letmewatchthis.ch'
        data = urllib.urlopen(source).read()
        keyL = re.findall(r'name="key" value="([\d+\w+]+)',data)
        self.key = ''.join(keyL)
        self.valid = True
        self.writeKey()

    def writeKey(self):
        if self.valid==True:
            with open("key.txt","w") as f:
                f.write(self.key)


if __name__ == "__main__":
    key = Key()
    print key.key
