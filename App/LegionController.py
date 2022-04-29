#!/usr/bin/python
from tempfile import tempdir
from tkinter import*
from PIL import ImageTk, Image
import os

root = Tk()
root.geometry('500x500')
root.title('LegionController')
root.resizable(False, False)

#Vars
currentMode = 0
temp = 0
def fcurrentMode():
    global temp
    global currentMode
    f = open("/sys/kernel/LegionController/powerMode", "r")
    temp=f.read()
    f.close()
    label2['text']=temp
    if temp=='performance': 
        currentMode=1
        perfBtn.configure(bg='#2333B4', activebackground='#2333B4')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.configure(bg='#676871', activebackground='#676871')
        saveBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
    elif temp=='balanced': 
        currentMode=2
        perfBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#2333B4', activebackground='#2333B4')
        quietBtn.configure(bg='#676871', activebackground='#676871')
        saveBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
    elif temp=='quiet': 
        currentMode=3
        perfBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.configure(bg='#2333B4', activebackground='#2333B4')
        saveBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
    label1['text']='1'

#Images
#Window icon
img = Image.open("/home/nutsu7/LegionController/App/img/main.xbm") # .ico for windows, .xbm for linux
mainIcon = ImageTk.PhotoImage(img)
root.tk.call('wm', 'iconphoto', root._w, mainIcon)
#Performance Mode Icon
img = Image.open("/home/nutsu7/LegionController/App/img/perf.png") 
img.thumbnail((100,100), Image.ANTIALIAS)
perfIcon = ImageTk.PhotoImage(img)
#Balanced Mode Icon
img = Image.open("/home/nutsu7/LegionController/App/img/balanced.png") 
img.thumbnail((100,100), Image.ANTIALIAS)
balancedIcon = ImageTk.PhotoImage(img)
#Quiet Mode Icon
img = Image.open("/home/nutsu7/LegionController/App/img/quiet.png") 
img.thumbnail((100,100), Image.ANTIALIAS)
quietIcon = ImageTk.PhotoImage(img)
#Save Icon
img = Image.open("/home/nutsu7/LegionController/App/img/save.png") 
img.thumbnail((80,80), Image.ANTIALIAS)
saveIcon = ImageTk.PhotoImage(img)
#Settings Icon
img = Image.open("/home/nutsu7/LegionController/App/img/settings.png") 
img.thumbnail((75,75), Image.ANTIALIAS)
settingsIcon = ImageTk.PhotoImage(img)


# Main Frames
page = Frame(root, bg='#000000', highlightbackground="white", highlightthickness=1)
page.place(relheight=0.80, relwidth=1)

modes = Frame(root, bg='#000000', highlightbackground="white", highlightthickness=1)
modes.place(rely=0.80, relheight=0.20, relwidth=1)


#Page
label1 = Label(page)
label1.place(anchor=CENTER,relx=0.25, rely=0.25, relheight=0.2, relwidth=0.5)
label2 = Label(page)
label2.place(anchor=CENTER,relx=0.25, rely=0.5, relheight=0.2, relwidth=0.5)

# Buttons
perfBtn = Button(modes, image=perfIcon)
perfBtn.place(relwidth=0.20, relheight=1)

balancedBtn = Button(modes, image=balancedIcon)
balancedBtn.place(relx=0.20, relwidth=0.20, relheight=1)

quietBtn = Button(modes,image=quietIcon)
quietBtn.place(relx=0.40, relwidth=0.20, relheight=1)

saveBtn = Button(modes, image=saveIcon)
saveBtn.place(relx=0.60, relwidth=0.20, relheight=1)

settingsBtn = Button(modes, image=settingsIcon)
settingsBtn.place(relx=0.80, relwidth=0.20, relheight=1)

fcurrentMode()

root.mainloop()