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
currentPowerMode = -1
perfBtnPressedValue = False
balancedBtnPressedValue = False
quietBtnPressedValue = False
saveBtnPressedValue = False
initPowerModeBtns = False
fanSpeedCurrentLeft = -1
fanSpeedCurrentRight = -1
tempCurrentCPU = -1
tempCurrentGPU = -1

#Functions
def checkCurrentPowerMode():
    global currentPowerMode
    global initPowerModeBtns
    if not initPowerModeBtns:
        f = open("/sys/kernel/LegionController/powerMode", "r")
        currentPowerMode = int(f.read()[:-1])
        f.close
        initPowerModeBtns = True
    os.system('cat /sys/kernel/LegionController/powerMode')
    if currentPowerMode == 0: 
        perfBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#2333B4', activebackground='#2333B4')
        quietBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.after(2000,checkCurrentPowerMode)
    elif currentPowerMode == 1: 
        perfBtn.configure(bg='#2333B4', activebackground='#2333B4')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.after(2000,checkCurrentPowerMode)
    elif currentPowerMode == 2: 
        perfBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.configure(bg='#2333B4', activebackground='#2333B4')
        quietBtn.after(2000,checkCurrentPowerMode)

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
    global currentPowerMode
    global balancedBtnPressedValue
    global perfBtnPressedValue
    global quietBtnPressedValue

    if balancedBtnPressedValue:
        f = open("/sys/module/LegionController/parameters/cPowerMode", "w")
        f.write('0')
        f.close()
        balancedBtnPressedValue = False
        currentPowerMode = 0
    elif perfBtnPressedValue:
        f = open("/sys/module/LegionController/parameters/cPowerMode", "w")
        f.write('1')
        f.close()
        perfBtnPressedValue = False
        currentPowerMode = 1
    elif quietBtnPressedValue:
        f = open("/sys/module/LegionController/parameters/cPowerMode", "w")
        f.write('2')
        f.close()
        quietBtnPressedValue = False
        currentPowerMode = 2


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

def checkCurrentData():
    global fanSpeedCurrentLeft
    global fanSpeedCurrentRight
    global tempCurrentCPU
    global tempCurrentGPU

    f = open("/sys/kernel/LegionController/fanSpeedCurrentLeft", "r")
    fanSpeedCurrentLeft = f.read()[:-1]
    f.close()
    fanSpeedCurrentLeftLabel['text']=fanSpeedCurrentLeft+' RPM'
    f = open("/sys/kernel/LegionController/fanSpeedCurrentRight", "r")
    fanSpeedCurrentRight = f.read()[:-1]
    f.close()
    fanSpeedCurrentRightLabel['text']=fanSpeedCurrentRight+' RPM'
    f = open("/sys/kernel/LegionController/fanTempCurrentCPU", "r")
    tempCurrentCPU = f.read()[:-1]
    f.close()
    tempCurrentCPULabel['text']=tempCurrentCPU+' °C'
    f = open("/sys/kernel/LegionController/fanTempCurrentGPU", "r")
    tempCurrentGPU = f.read()[:-1]
    f.close()
    tempCurrentGPULabel['text']=tempCurrentGPU+' °C'
    tempCurrentGPULabel.after(1000, checkCurrentData)

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


#Page Frames
fanCurve = Frame(page, bg='#000000', highlightbackground="white", highlightthickness=1)
fanCurve.place(relwidth=1,relheight=0.7)

currentData = Frame(page, bg='#000000', highlightbackground="white", highlightthickness=1)
currentData.place(rely=0.7, relheight=0.3, relwidth=1)

#Current Data Frame elements
currentDataFanSpeed = Frame(currentData, bg='#000000', highlightbackground="white", highlightthickness=1)
currentDataFanSpeed.place(relheight=1, relwidth=0.5)

currentDataTemp = Frame(currentData, bg='#000000', highlightbackground="white", highlightthickness=1)
currentDataTemp.place(relheight=1, relwidth=0.5, relx=0.5)

#Current Data Fan Speed
currentDataFanSpeedText = Label(currentDataFanSpeed, text='Current Fan Speed', font=("Arial", 20), fg='white', bg='#000000')
currentDataFanSpeedText.place(relx=0, rely=0.025, relheight=0.20, relwidth=1)

currentDataFanSpeedLeftText = Label(currentDataFanSpeed, text='Left Fan', font=("Arial", 15), fg='white', bg='#000000')
currentDataFanSpeedLeftText.place(relx=0, rely=0.3, relheight=0.30, relwidth=0.4)

currentDataFanSpeedRightText = Label(currentDataFanSpeed, text='Right Fan', font=("Arial", 15), fg='white', bg='#000000')
currentDataFanSpeedRightText.place(relx=0, rely=0.65, relheight=0.30, relwidth=0.4)

fanSpeedCurrentLeftLabel = Label(currentDataFanSpeed, bg='#676871', activebackground='#676871', font=("Arial", 17), fg='black')
fanSpeedCurrentLeftLabel.place(relx=0.4, rely=0.30, relheight=0.30, relwidth=0.5)

fanSpeedCurrentRightLabel = Label(currentDataFanSpeed, bg='#676871', activebackground='#676871', font=("Arial", 17), fg='black')
fanSpeedCurrentRightLabel.place(relx=0.4, rely=0.65, relheight=0.30, relwidth=0.5)

#Current Data Temps
currentDataTempText = Label(currentDataTemp, text='Current Temps', font=("Arial", 20), fg='white', bg='#000000')
currentDataTempText.place(relx=0, rely=0.025, relheight=0.20, relwidth=1)

currentDataTempCPUText = Label(currentDataTemp, text='CPU', font=("Arial", 15), fg='white', bg='#000000')
currentDataTempCPUText.place(relx=0.005, rely=0.3, relheight=0.30, relwidth=0.4)

currentDataTempGPUText = Label(currentDataTemp, text='GPU', font=("Arial", 15), fg='white', bg='#000000')
currentDataTempGPUText.place(relx=0.005, rely=0.65, relheight=0.30, relwidth=0.4)

tempCurrentCPULabel = Label(currentDataTemp, bg='#676871', activebackground='#676871', font=("Arial", 17), fg='black')
tempCurrentCPULabel.place(relx=0.4, rely=0.30, relheight=0.30, relwidth=0.5)

tempCurrentGPULabel = Label(currentDataTemp, bg='#676871', activebackground='#676871', font=("Arial", 17), fg='black')
tempCurrentGPULabel.place(relx=0.4, rely=0.65, relheight=0.30, relwidth=0.5)

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
checkCurrentData()
root.mainloop()