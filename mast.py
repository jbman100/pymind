#!/usr/bin/python3

import curses
import time
import random

###############################################################
############################### Variables #####################
###############################################################


length=5
choices=8
attempts=1
max_attempts=15


###############################################################
############################### Definitions ###################
###############################################################

def start_session(): #Start the curses windows
    screen = curses.initscr()
    curses.start_color()
    curses.curs_set(0)
    curses.use_default_colors()
    curses.noecho()
    curses.cbreak()
    return screen,curses.LINES,curses.COLS


def end_session(screen,log): #Return the terminal to its original state
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


def init_colors(): #Get a nice clean list of available color pairs
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_GREEN)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_CYAN)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_WHITE)

    colors = [curses.color_pair(k+1) for k in range(8)]
    return(colors)


def analysis(code): #Analyse a list to ease the answering system
    L=[[code[0],1]]
    for k in range(1,len(code)):
        missing = True
        for couple in L:
            if couple[0] == code[k]:
                couple[1]+=1
                missing = False
        if missing:
            L.append([code[k],1])
    return L #Here L is a list of lists, the latter being the digit and the amount of times it is featured in the code


def status(tent,code): #Returns the game's answer to tent, and if the code has been found
    T = analysis(tent)
    C = analysis(code)
    right = 0
    rspot = 0
    for i in T:
        for j in C:
            if i[0] == j[0]:
                right += min(i[1],j[1])
    for k in range(len(code)):
        if code[k] == tent[k]:
            rspot += 1
            right -= 1
    if rspot == 5:
        return(right,rspot,True)
    return(right,rspot,False)


def generate(choices): #Generate a code of digits between 0 and 'choices - 1'
    code = []
    for i in range(length):
        code.append(random.randint(0,choices-1))
    return(code)


def debug(win,display,to_print): #Display the code in case of need
    for k in ['E','B','U','G']:
        if win.listen() != ord(k):
            return False
    popup("The code is: __ __ __ __ __",display,to_print)


def end_game(found,to_print): #Properly end the game
    if found:
        popup("You win !",display)
    else:
        popup("Too bad ! The code was: __ __ __ __ __",display,to_print)



############################### Commentary Object #############

class commentary:

    def __init__(self,lines,columns):
        self.padding = 2
        self.height = (lines*2)//3
        self.width = columns//2

        self.win = curses.newwin(self.height,self.width,0,0)
        self.win.border(0)
        self.win.addstr(0,0,"<Help>",curses.A_REVERSE)

        self.win.addstr(2,2,"This is a game of Mastermind.")
        self.win.addstr(3,2,"Use the arrow keys to guess the color code.")
        self.win.addstr(4,2,"Press q to quit, or s to submit your choice.")
        self.win.addstr(5,2,"Once submitted, your attempts will be evaluated:")
        self.win.addstr(6,2,"- A white dot means that you correctly guessed a color.")
        self.win.addstr(7,2,"- A red dot means that you correctly guessed a color,")
        self.win.addstr(8,2,"and placed it at the right spot.")
        self.win.addstr(10,2,"You have "+str(max_attempts)+" attempts to find the answer.")

        self.win.refresh()


############################### Logger Object #################

class logger:

    def __init__(self,lines,columns):
        self.padding = 3
        self.next_line = self.padding
        self.hist = []

        self.height = lines
        self.width = columns//2

        self.capacity = (self.height - 2*self.padding)//2
        self.entry = 0
        self.first = 0

        self.win = curses.newwin(self.height,self.width,0,columns//2)
        self.win.border(0)
        self.win.addstr(0,0,"<Attempts>",curses.A_REVERSE)
        self.win.refresh()


    def prt(self,attempt,choice,r,rp,colors): #Print the attempt along with the answer
        self.win.move(self.next_line,self.padding)
        self.win.addstr("Attempt "+str(attempt)+" : ")
        for i in choice:
            self.win.addstr('  ',colors[i])
            self.win.addstr(' ')
        self.win.addstr('--> ')
        for k in range(r):
            self.win.addstr('  ',colors[7])
            self.win.addstr(' ')
        for k in range(rp):
            self.win.addstr('  ',colors[0])
            self.win.addstr(' ')
        self.win.refresh()


    def show(self,attempt,choice,r,rp,colors,new): #Update the log and the history if needed

        if new:
            self.entry += 1
            tmp = [k for k in choice]
            self.hist.append((attempt,tmp,r,rp))
            if self.entry - self.first > self.capacity:
                self.first = self.entry - self.capacity
                self.scroll(self.first,colors)
            else:
                self.prt(attempt,choice,r,rp,colors)
            self.next_line += 2

        else:
            self.prt(attempt,choice,r,rp,colors)
            self.next_line += 2


    def scroll(self,first_entry,colors): #Redraw the window to show the log from the desired first_entry
        self.win.clear()
        self.win.border(0)
        self.win.addstr(0,0,"<Attempts>",curses.A_REVERSE)
        self.win.addstr(0,(self.width-3)//2,"↑ k",curses.A_REVERSE)
        self.win.addstr(self.height-1 ,(self.width-3)//2,"↓ j",curses.A_REVERSE)
        self.next_line = self.padding

        last = first_entry + self.capacity

        for k in self.hist[first_entry:last]:
            (attempt,c,r,rp) = k
            self.show(attempt,c,r,rp,colors,False)


    def up(self,colors): #Decrease the first line and redraw
        if self.first > 0:
            self.first -= 1
            self.scroll(self.first,colors)


    def down(self,colors): #Increase the first line and redraw
        if self.first < self.entry and self.entry - self.first > 1:
            self.first += 1
            self.scroll(self.first,colors)


############################### Selector Object ###############

class selector:
    def __init__(self,lines,columns):
        self.choice = [0 for _ in range(5)]
        self.hover = 0
        self.padding = 5

        self.height = lines//3
        self.width = columns//2

        self.cy = self.height//2
        self.cx = (self.width-33)//2

        self.win = curses.newwin(self.height,self.width,lines*2//3,0)
        self.win.border(0)
        self.win.addstr(0,0,"<Select your code>",curses.A_REVERSE)
        self.win.addstr(self.cy-1,self.relativePos(),"↑↓")
        self.win.addstr(self.cy,self.cx,"__ __ __ __ __    Attempt: 01/"+str(max_attempts))
        self.win.addstr(self.cy+1,self.relativePos(),"↑↓")
        self.win.keypad(True)
        self.win.refresh()


    def relativePos(self): #Nifty function to calculate the position of the cursor
        return self.cx + 3*self.hover


    def listen(self): #Return the users input
        return self.win.getch(self.cy,self.relativePos())


    def move(self,inc): #Move the cursor along with the indicators
        self.win.addstr(self.cy-1,self.relativePos(),"  ")
        self.win.addstr(self.cy+1,self.relativePos(),"  ")
        self.hover = (self.hover + inc)%5
        self.win.addstr(self.cy-1,self.relativePos(),"↑↓")
        self.win.addstr(self.cy+1,self.relativePos(),"↑↓")


    def update_colors(self,inc,colors): #Update colors if KEY_UP/DOWN is pressed
        self.choice[self.hover] = (self.choice[self.hover] + inc)%8
        self.win.addstr(self.cy, self.relativePos(), '  ', colors[self.choice[self.hover]])


    def update_attempts(self,attempts): #Update attempts once a code is submitted
        if attempts < 10:
            self.win.addstr(self.cy,self.cx+28,str(attempts))
        else:
            self.win.addstr(self.cy,self.cx+27,str(attempts))


############################### Popup Object ##################

class popup:

    def __init__(self,message,display,to_print = ([],[])):
        self.length = len(message)
        self.x = (curses.COLS - self.length - 4)//2
        self.y = (curses.LINES - 5)//2

        self.win = curses.newwin(5,self.length+4,self.y,self.x)
        self.win.border(0)
        self.win.addstr(0,0,"<Dialog>",curses.A_REVERSE)
        self.win.addstr(2,2,message)

        code,colors = to_print
        if code != []:
            self.show_code(code,colors,message)
        self.win.refresh()

        self.win.getch()
        self.win.clear()
        self.win.refresh()

        for elmt in display:
            elmt.win.redrawwin()
            elmt.win.refresh()

    def show_code(self,code,colors,message): #Print a code in the message
        self.win.move(2,2 + len(message) - 14) #2 - Padding, -14 - Length of the code
        for k in code:
            self.win.addstr('  ',colors[k])
            self.win.addstr(' ')


###############################################################
############################### Main part #####################
###############################################################

s,li,co = start_session()

comm = commentary(li,co)
log = logger(li,co)
sel = selector(li,co)
display = [comm,sel,log]

colors = init_colors()

found = False
code = generate(choices)

while attempts <= max_attempts and found == False:
    input_ch = sel.listen()

    if input_ch == curses.KEY_RIGHT:
        sel.move(1)

    if input_ch == curses.KEY_LEFT:
        sel.move(-1)

    if input_ch == curses.KEY_UP:
        sel.update_colors(1,colors)

    if input_ch == curses.KEY_DOWN:
        sel.update_colors(-1,colors)

    if input_ch == ord('s'):
        right,rspot,found = status(sel.choice,code)
        log.show(attempts,sel.choice,right,rspot,colors,True)
        attempts += 1
        sel.update_attempts(attempts)

    if input_ch == ord('p'):
        popup("Martin est doux !",display)

    if input_ch == ord('k'):
        log.up(colors)

    if input_ch == ord('j'):
        log.down(colors)

    if input_ch == ord('D'):
        debug(sel,display,(code,colors))

    if input_ch == ord('R'):
        time.sleep(1)

    if input_ch == ord('q'):
        attempts += 100

end_game(found,(code,colors))
end_session(s,log)
