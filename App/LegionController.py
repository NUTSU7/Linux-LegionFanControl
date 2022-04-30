#!/usr/bin/python
from multiprocessing import cpu_count
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
initPowerModeBtns = False

#Functions
def checkCurrentPowerMode():
    global currentMode
    global initPowerModeBtns
    temp = 0
    if not initPowerModeBtns:
        stream = os.popen('cat /sys/kernel/LegionController/powerMode')
        currentMode = int(stream.read())
        initPowerModeBtns = True
    os.system('cat /sys/kernel/LegionController/powerMode')
    print(temp)
    if currentMode == 0: 
        perfBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#2333B4', activebackground='#2333B4')
        quietBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.after(1000,checkCurrentPowerMode)
    elif currentMode == 1: 
        perfBtn.configure(bg='#2333B4', activebackground='#2333B4')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.after(1000,checkCurrentPowerMode)
    elif currentMode == 2: 
        perfBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.configure(bg='#2333B4', activebackground='#2333B4')
        quietBtn.after(1000,checkCurrentPowerMode)

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
        os.system('echo 0 > /sys/module/LegionController/parameters/cPowerMode')
        balancedBtnPressedValue = False
        currentMode = 0
    elif perfBtnPressedValue:
        os.system('echo 1 > /sys/module/LegionController/parameters/cPowerMode')
        perfBtnPressedValue = False
        currentMode = 1
    elif quietBtnPressedValue:
        os.system('echo 2 > /sys/module/LegionController/parameters/cPowerMode')
        quietBtnPressedValue = False
        currentMode = 2


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

checkCurrentPowerMode()

root.mainloop()