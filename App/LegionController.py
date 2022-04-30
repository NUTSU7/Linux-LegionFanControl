#!/usr/bin/python
from tempfile import tempdir
from tkinter import *
from PIL import ImageTk, Image
import os, threading, time

root = Tk()
root.geometry('500x500')
root.title('LegionController')
root.resizable(False, False)

#Vars
currentMode = 0
perfBtnPressedValue = False
balancedBtnPressedValue = False
quietBtnPressedValue = False
saveBtnPressedValue = False

#Functions
def fcurrentMode():
    temp = 0
    global currentMode
    f = open("/sys/kernel/LegionController/powerMode", "rt")
    temp=f.read()
    f.close()
    temp=temp[:-1]
    if temp=='performance': 
        currentMode=1
        perfBtn.configure(bg='#2333B4', activebackground='#2333B4')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.after(1000,fcurrentMode)
    elif temp=='balanced': 
        currentMode=0
        perfBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#2333B4', activebackground='#2333B4')
        quietBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.after(1000,fcurrentMode)
    elif temp=='quiet': 
        currentMode=2
        perfBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.configure(bg='#2333B4', activebackground='#2333B4')
        quietBtn.after(1000,fcurrentMode)

def perfBtnPressed():
    global perfBtnPressedValue
    perfBtnPressedValue = True
    powerModeBtnPressed()

def balancedBtnPressed():
    global balancedBtnPressedValue
    balancedBtnPressedValue = True
    powerModeBtnPressed()

def quietBtnPressed():
    global quietBtnPressedValue
    quietBtnPressedValue = True
    powerModeBtnPressed()

def powerModeBtnPressed():
    global currentMode
    global balancedBtnPressedValue
    global perfBtnPressedValue
    global quietBtnPressedValue

    if balancedBtnPressedValue:
        balancedBtn.configure(bg='#2333B4', activebackground='#2333B4')
        f = open("/sys/module/LegionController/parameters/cPowerMode", "w")
        f.write("0")
        f.close()
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtnPressedValue = False
        currentMode = 0
    elif perfBtnPressedValue:
        perfBtn.configure(bg='#2333B4', activebackground='#2333B4')
        f = open("/sys/module/LegionController/parameters/cPowerMode", "w")
        f.write("1")
        f.close()
        perfBtn.configure(bg='#676871', activebackground='#676871')
        perfBtnPressedValue = False
        currentMode = 1
    elif quietBtnPressedValue:
        quietBtn.configure(bg='#2333B4', activebackground='#2333B4')
        f = open("/sys/module/LegionController/parameters/cPowerMode", "w")
        f.write("2")
        f.close()
        quietBtn.configure(bg='#676871', activebackground='#676871')
        quietBtnPressedValue = False
        currentMode = 2
    #os.system('cat /sys/kernel/LegionController/powerMode')


def saveBtnPressed():
    global saveBtnPressedValue
    saveBtnPressedValue = True
    root.after(100, lambda: saveBtn.configure(bg='#2333B4', activebackground='#2333B4'))
    root.after(400, lambda: saveBtn.configure(bg='#676871', activebackground='#676871'))

def btnLightUp():
    global saveBtnPressedValue
    if saveBtnPressedValue == True:
        saveBtn.configure(bg='#2333B4', activebackground='#2333B4')
        time.sleep(0.35)
        saveBtn.configure(bg='#676871', activebackground='#676871')
        saveBtnPressedValue = False
    time.sleep(0.2)


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
#label1 = Label(page)
#label1.place(anchor=CENTER,relx=0.25, rely=0.25, relheight=0.2, relwidth=0.5)


# Buttons
perfBtn = Button(modes, image=perfIcon, command=perfBtnPressed)
perfBtn.place(relwidth=0.20, relheight=1)

balancedBtn = Button(modes, image=balancedIcon,command=balancedBtnPressed)
balancedBtn.place(relx=0.20, relwidth=0.20, relheight=1)

quietBtn = Button(modes,image=quietIcon,command=quietBtnPressed)
quietBtn.place(relx=0.40, relwidth=0.20, relheight=1)

saveBtn = Button(modes, image=saveIcon,bg='#676871', activebackground='#676871', command=saveBtnPressed)
saveBtn.place(relx=0.60, relwidth=0.20, relheight=1)

settingsBtn = Button(modes, image=settingsIcon,bg='#676871', activebackground='#676871')
settingsBtn.place(relx=0.80, relwidth=0.20, relheight=1)


#saveBtnTh = threading.Thread(target=btnLightUp).start()

fcurrentMode()

root.mainloop()