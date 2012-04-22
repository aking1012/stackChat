'''
parsing hell
find new messages and possibly edits eventually
'''
import difflib

'''
so we can choose to deepcopy newlist = list[:] has produced mixed results
'''
import copy

'''
selenium stuff for scraping
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from time import sleep

'''
the xvfb stuff so we can run selenium headless
'''
from pyvirtualdisplay import Display

#set this to true for debugging
#debug = True
debug = False
def log(whatever):
    if debug:
        print whatever

#debugscraper = True
debugscraper = False
def logscraper(whatever):
    if debugscraper:
        print whatever

class scrapeSend():
    def __init__(self):
        #comment the next two lines out if you want a browser window
        display = Display(visible=0, size=(800, 600))
        display.start()
        self.sleep = 20
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(self.sleep)
        self.base_url = "https://accounts.google.com/"
        self.verificationErrors = []
    
    def login(self, login, passwd):
        driver = self.driver
        driver.get("http://stackexchange.com/users/login?returnurl=%2fusers%2fchat-login")
        driver.find_element_by_css_selector("a.google.openid_large_btn").click()
        driver.find_element_by_id("Email").clear()
        driver.find_element_by_id("Email").send_keys(login)
        driver.find_element_by_id("Passwd").clear()
        driver.find_element_by_id("Passwd").send_keys(passwd)
        driver.find_element_by_id("signIn").click()
        sleep(self.sleep)

    def logout(self):
        driver = self.driver
        driver.get("http://chat.stackexchange.com/logout")
        driver.find_element_by_css_selector("input.button").click()
        driver.get("http://mail.google.com/mail?logout")

    def post(self, message, room = 'rooms/201/ask-ubuntu-general-room'):
        driver = self.driver
        driver.get("http://chat.stackexchange.com/" + room)
        driver.find_element_by_id("input").clear()
        driver.find_element_by_id("input").send_keys(message)
        driver.find_element_by_id("sayit-button").click()

    def getCurrentPosts(self, room = 'rooms/201/ask-ubuntu-general-room'):
        '''
        Get posts.  It defaults to the askubuntu-general room, just supply a room argument.
        '''
        driver = self.driver
        html = []
        driver.get("http://chat.stackexchange.com/" + room)
        sleep(self.sleep/5)
        elements = driver.find_elements_by_class_name('user-container')
        for element in elements:
            print '--------------------------'
            print self.driver.execute_script("return arguments[0].innerHTML;", element)
            html.append(self.driver.execute_script("return arguments[0].innerHTML;", element))
        return html
            
    def is_element_present(self, how, what):
        '''
        Put here by the Selenium IDE...so I left it
        '''
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def quit(self):
        '''
        quit the browser
        '''
        self.driver.quit()

class stackChatParser():
    def __init__(self):
        '''
        self.url is the page we browse to get to the room
        self.speakers is the thread separated out by who said it in order
            this is so we can simply find the last speaker that matches and
            start checking for edits or new messages
        self.newmessages is an array of messages with who said it
        '''
        self.url = 'http://chat.stackexchange.com/rooms/201/ask-ubuntu-general-room'

        self.oldspeakers = []
        self.speakers = []
        self.newmessages = []
        self.userlist = []
                
    def processText(self, text):
        '''
        First we split the text out to speakers and get our userlist
        '''
        speakers=[]
        split=[]
        usersplit=0
        inuserlist = False
        
        userlist=[]
        #find user list
        i=0
        
        #I need to change this part to parse bottom up to get the end
        #user list so some less than happy person doesn't think it's funny
        #to type 'leave (all) | ' as a message
        #atext = text.reverse()
        
        #we can find the userlist
        for line in text:
            if line=='\n' and 'leave (all) | ' in text[i-1]: 
                log('found start of the userlist')
                inuserlist=True
                usersplit = i+1
            elif inuserlist == True:
                if line == '\n':
                    inuserlist=False
                    log('found end of the userlist')
                    self.userlist = userlist
                    print "Current users: "
                    for user in userlist:
                        print user.rstrip()
                    break
                else:
                    userlist.append(line.lstrip())
            i+=1
        #find message splits
        i=0
        endchat = usersplit-12
        for line in text:
            if i>endchat:break
            if line==' \n' and text[i+2]==text[i+1]: split.append(i+2)
            i+=1
        #populate speakers
        i=0
        for index in split:
            try:
                speakers.append(text[index:split[i+1]-2])
            except:
                speakers.append(text[index:endchat])
            i+=1
        self.speakers = speakers
    
    def findLast(self):
        '''
        '''
        splits = self.flattenSpeakers()
        thediff = []
        for line in difflib.context_diff(self.flatoldspeak, self.flatspeak):
            thediff.append(line)
        log(thediff)
        edits = []
        '''
        #in case I try to support edits, it would be like user: X edited this: Y to this: Z
        i=0
        sections = []
        for item in thediff:
            if item=='***************\n':
                sections.append(i)
            i+=1
        #find line numbers here
        #then search for what !'s happen in what user posts
        print sections
        last = sections[-1]
        i=0
        for line in thediff:
            if i<=last:
                pass
                i+=1
            else:
                print line.rstrip()
                i+=1
        '''
        dontStop = True
        i=1
        addlines = 0
        addstuff = []
        while(dontStop):
            if thediff[-i][0] == '+':
                log(thediff[-i].rstrip())
                addstuff.insert(0, thediff[-i][2:])
                addlines = i
                i+=1
            else:
                break
        return edits, addlines, splits, addstuff
        
        
    def flattenSpeakers(self):
        '''
        '''
        self.flatspeak = []
        self.flatoldspeak = []
        speakers = copy.deepcopy(self.speakers)
        oldspeakers = copy.deepcopy(self.oldspeakers)
        splits = []
        i=0
        for alist in speakers:
            splits.append(len(alist))
            for item in alist:
                self.flatspeak.append(item)
        for alist in oldspeakers:
            for item in alist:
                self.flatoldspeak.append(item)
        return splits

    def splitsSumReverse(self, splits, entries):
        '''
        #TODO HERE
        '''
        splits.reverse()
        length = 0
        i=0
        while(i < entries):
            length += splits[i]
            i+=1
        return length
        
    def diffSpeakers(self):
        '''
        I could do away with almost all this if I made every 
        statement singular instead of a conversation...
        '''
        edits, addlines, splits, addstuff = self.findLast()
        try:
            log(splits)
            entries = 0
            tempint = 0
            newsize = addlines
            self.newmessages = []
            while (tempint < newsize):
                tempint += splits[-entries]
                entries+=1
            if tempint == newsize:
                allnew = True
            else:
                allnew = False
            toadd = len(self.speakers)-entries
            if allnew:
                #add just edit parsing up here
                #adding lines
                if addlines < splits[-1] and len(addstuff)==0:
                    pass
                elif addlines < splits[-1]:
                    log('notreally')
                    oldspeakernum = splits[-1] - addlines - 1 
                    message = []
                    #temp = self.speakers[-1][0]
                    message.append(self.speakers[-1][0])
                    i=1
                    log("add: " + str(oldspeakernum) + " items from: " + str(addstuff))
                    for item in addstuff:
                        message.append(copy.deepcopy(item))
                    self.newmessages.append(copy.deepcopy(message))
                #just messages
                else:
                    log('really')
                    log(entries)
                    log(addlines)
                    i=0
                    while (i<entries):
                        self.newmessages.append(self.speakers[toadd+i])
                        i+=1
            else:
                log('--------!!!')
                #added a line and speakers
                if addlines < self.splitsSumReverse(splits, entries):
                    log('yay')
                    log(addstuff)
                    message = []
                    message.append(self.speakers[-entries][0])
                    oldstuff = self.splitsSumReverse(splits, entries) - addlines
                    i=0
                    for item in addstuff:
                        if i<oldstuff:
                            message.append(addstuff[i])
                            i+=1
                        else:
                            break
                    self.newmessages.append(message)
                    speakers = -(entries-1)
                    while(speakers!=0):
                        self.newmessages.append(self.speakers[speakers])
                        speakers+=1                    
                else:
                    log('WAT!')
            log(self.newmessages)
            log(len(self.newmessages))
            log('------------')
            return True
        except:
            self.newmessages = []
            return False
    
    def test(self):
        with open('./scrapedemo.txt', 'r') as speakers:
            self.processText(speakers.readlines())
        print '\n???????????????\n'
        print 'test for added messages'
        print '\n???????????????\n'
        self.oldspeakers = copy.deepcopy(self.speakers)
        self.speakers.append(['testuser\n','message\n'])
        self.speakers.append(['anothertestuser\n','anothermessage\n','butthisone is longer\n'])
        self.diffSpeakers()
        print self.newmessages
        print '\n???????????????\n'
        print 'test for added a bit from the last poster'
        print '\n???????????????\n'
        self.speakers = copy.deepcopy(self.oldspeakers)
        this = self.speakers.pop()
        this.append('changed\n')
        this.append('more\n')
        self.speakers.append(this)
        self.diffSpeakers()
        print self.newmessages
        print '\n???????????????\n'
        print "test for added a bit from the last poster and a new message"
        print '\n???????????????\n'
        self.speakers = copy.deepcopy(self.oldspeakers)
        this = self.speakers.pop()
        this.append('changed\n')
        self.speakers.append(this)
        self.speakers.append(['testuser\n','message\n'])
        self.diffSpeakers()
        print self.newmessages
        print '\n???????????????\n'
        print "test for edits ... not implemented, but it should be pretty straightforward.  you're grepping for ^!"
        print '\n???????????????\n'
        self.speakers = copy.deepcopy(self.oldspeakers)
        thisa = self.speakers.pop()
        this = self.speakers.pop()
        this[1] = 'changed'
        self.speakers.append(this)
        self.speakers.append(thisa)
        self.diffSpeakers()
        print self.newmessages
        print '\n???????????????\n'

import subprocess, sys, fcntl, select

class clientCommunication():
    '''
    Still have to shim in the xtalk XMPP bot.
    I've got some XMPP sending code laying around, but it doesn't listen...so...
    '''
    def __init__(self, chatbridge, server, contact, sendscrape):
        '''
        '''
        self.bot = chatbridge
        self.user = contact
        self.server = server
        self.tostack = sendscrape
        
    def runService(self):
        '''
        '''
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        fcntl.fcntl(proc.stdout.fileno(), fcntl.F_SETFL, fcntl.fcntl(proc.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK)
        while proc.poll() == None:
            readable = select.select([proc.stdout.fileno()], [], [])[0]
            if readable:
                self.listenToUser(proc.stdout.read())
            self.sendToUser(self.tostack.poll())
            
    
    def sendToUser(self):
        '''
        '''
        
    def listenToUser(self, message):
        '''
        optionally insert commands here, like search for @me or translate /me
        '''
        self.tostack.post(message)



if __name__=='__main__':
    '''
    chat = stackChatParser()
    chat.test()
    '''
    #Tested login/logout it works
    #chatint.login('gmail-login','gmail-password')
    #sleep(15)
    chatint = scrapeSend()
    html = chatint.getCurrentPosts()
    #chatint.post('Just a test')
    #TODO add html parsing...I checked raw-text parsing.
    #It worked fine once I got it into a list of lists.
    #if 'a' message else user
    #there are some 'still loading issues',
    #but i can just grab their name from their profile and keep an index
    
    
    #chatint.logout()
    chatint.quit()
