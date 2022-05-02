#!/usr/bin/python
from tkinter import *
from PIL import ImageTk, Image
import os, threading, time
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

params = {"xtick.color" : "white",
          "ytick.color" : "white",
          "axes.edgecolor" : "white",
          "figure.facecolor" : "black",
          "axes.facecolor" : "black",
          "axes.grid" : "True",
          "axes.xmargin" : "0",
          "axes.ymargin" : "0",
          "axes.zmargin" : "0",
          "axes.autolimit_mode" : "data"}
plt.rcParams.update(params)

root = Tk()
root.geometry('700x700')
root.title('LegionController')
root.resizable(False, False)

#Vars
cwd=os.getcwd()
currentPowerMode = -1
perfBtnPressedValue = False
balancedBtnPressedValue = False
quietBtnPressedValue = False
saveBtnPressedValue = False
fanSpeedCurrentLeft = -1
fanSpeedCurrentRight = -1
tempCurrentCPU = -1
tempCurrentGPU = -1
fanCurveLeft = []
fanCurveRight = []
tempCurveCPU = []
tempCurveGPU = []
curveLen = -1

#Functions
def getCurrentPowerMode():
    global currentPowerMode
    f = open("/sys/kernel/LegionController/powerMode", "r")
    currentPowerMode = int(f.read()[:-1])
    f.close
    if currentPowerMode == 0: 
        perfBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#2333B4', activebackground='#2333B4')
        quietBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.after(2000,getCurrentPowerMode)
    elif currentPowerMode == 1: 
        perfBtn.configure(bg='#2333B4', activebackground='#2333B4')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.after(2000,getCurrentPowerMode)
    elif currentPowerMode == 2: 
        perfBtn.configure(bg='#676871', activebackground='#676871')
        balancedBtn.configure(bg='#676871', activebackground='#676871')
        quietBtn.configure(bg='#2333B4', activebackground='#2333B4')
        quietBtn.after(2000,getCurrentPowerMode)

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
    elif perfBtnPressedValue:
        f = open("/sys/module/LegionController/parameters/cPowerMode", "w")
        f.write('1')
        f.close()
        perfBtnPressedValue = False
    elif quietBtnPressedValue:
        f = open("/sys/module/LegionController/parameters/cPowerMode", "w")
        f.write('2')
        f.close()
        quietBtnPressedValue = False

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

def getCurrentData():
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
    f = open("/sys/kernel/LegionController/tempCurrentCPU", "r")
    tempCurrentCPU = f.read()[:-1]
    f.close()
    tempCurrentCPULabel['text']=tempCurrentCPU+' °C'
    f = open("/sys/kernel/LegionController/tempCurrentGPU", "r")
    tempCurrentGPU = f.read()[:-1]
    f.close()
    tempCurrentGPULabel['text']=tempCurrentGPU+' °C'
    tempCurrentGPULabel.after(2000, getCurrentData)

def getCurrentFanCurve():
    global fanCurveLeft
    global fanCurveRight
    global tempCurveCPU
    global tempCurveGPU
    global tempCurrentCPU
    global curveLen
    fanCurveLeft = []
    fanCurveRight = []
    tempCurveCPU = []
    tempCurveGPU = []
    if int(tempCurrentCPU) < 40: curveLen=3
    elif currentPowerMode == 0: curveLen=8
    elif currentPowerMode == 1: curveLen=9
    elif currentPowerMode == 2: curveLen=7
    f = open("/sys/kernel/LegionController/fanCurveLeft", "r")
    for i in range(curveLen):
        fanCurveLeft.extend(f.read().split(' '))
    f.close()
    f = open("/sys/kernel/LegionController/fanCurveRight", "r")
    for i in range(curveLen):
        fanCurveRight.extend(f.read().split(' '))
    f.close()
    f = open("/sys/kernel/LegionController/tempCurveCPU", "r")
    for i in range(curveLen):
        tempCurveCPU.extend(f.read().split(' '))
    f.close()
    f = open("/sys/kernel/LegionController/tempCurveGPU", "r")
    for i in range(curveLen):
        tempCurveGPU.extend(f.read().split(' '))
    f.close()

    #Attemp for a graph
    #fanCurvePlot.cla()
    #fanCurvePlot.plot(fanCurveLeft,tempCurveCPU, color='blue')
    #fanCurvePlot.plot(fanCurveRight,tempCurveGPU, color='green')
    #fanCurveCanvas.draw()
    
    root.after(2000, getCurrentFanCurve)


#Images
#Window icon
img = Image.open(cwd+"/img/main.xbm") # .ico for windows, .xbm for linux
mainIcon = ImageTk.PhotoImage(img)
root.tk.call('wm', 'iconphoto', root._w, mainIcon)
#Performance Mode Icon
img = Image.open(cwd+"/img/perf.png") 
img.thumbnail((100,100), Image.ANTIALIAS)
perfIcon = ImageTk.PhotoImage(img)
#Balanced Mode Icon
img = Image.open(cwd+"/img/balanced.png") 
img.thumbnail((100,100), Image.ANTIALIAS)
balancedIcon = ImageTk.PhotoImage(img)
#Quiet Mode Icon
img = Image.open(cwd+"/img/quiet.png") 
img.thumbnail((100,100), Image.ANTIALIAS)
quietIcon = ImageTk.PhotoImage(img)
#Save Icon
img = Image.open(cwd+"/img/save.png") 
img.thumbnail((80,80), Image.ANTIALIAS)
saveIcon = ImageTk.PhotoImage(img)
#Settings Icon
img = Image.open(cwd+"/img/settings.png") 
img.thumbnail((75,75), Image.ANTIALIAS)
settingsIcon = ImageTk.PhotoImage(img)

# Main Frames
page = Frame(root, bg='#000000', highlightbackground="white", highlightthickness=1)
page.place(height=602, relwidth=1)

modes = Frame(root, bg='#000000', highlightbackground="white", highlightthickness=1)
modes.place(y=600, height=100, relwidth=1)

#Attemp for a graph
#fanCurveFig = Figure(figsize=(2,2), dpi=100)
#fanCurvePlot = fanCurveFig.add_subplot(122)
#fanCurvePlot.plot(fanCurveLeft,tempCurveCPU, color='blue')
#fanCurvePlot.plot(fanCurveRight,tempCurveGPU, color='green')
#fanCurvePlot.axes.xaxis.set_visible(False)
#fanCurvePlot.axes.yaxis.set_visible(False)

#Page Frames
fanCurveFigFrame = Frame(page, bg='#000000', highlightbackground="white", highlightthickness=1)
fanCurveFigFrame.place(relwidth=1,relheight=0.7)

currentDataFrame = Frame(page, bg='#000000', highlightbackground="white", highlightthickness=1)
currentDataFrame.place(rely=0.7, relheight=0.3, relwidth=1)

#Fan Curve Frame

#Attemp for a graph
#fanCurveCanvas = FigureCanvasTkAgg(fanCurveFig, fanCurveFigFrame)
#fanCurveCanvas.draw()
#fanCurveCanvas.get_tk_widget().place(relwidth=1, relheight=1)

#Current Data Frame elements
currentDataFrameFanSpeed = Frame(currentDataFrame, bg='#000000', highlightbackground="white", highlightthickness=1)
currentDataFrameFanSpeed.place(relheight=1, relwidth=0.5)

currentDataFrameTemp = Frame(currentDataFrame, bg='#000000', highlightbackground="white", highlightthickness=1)
currentDataFrameTemp.place(relheight=1, relwidth=0.5, relx=0.5)

#Current Data Fan Speed
currentDataFrameFanSpeedText = Label(currentDataFrameFanSpeed, text='Current Fan Speed', font=("Arial", 20), fg='white', bg='#000000')
currentDataFrameFanSpeedText.place(relx=0, rely=0.025, relheight=0.20, relwidth=1)

currentDataFrameFanSpeedLeftText = Label(currentDataFrameFanSpeed, text='Left Fan', font=("Arial", 15), fg='white', bg='#000000')
currentDataFrameFanSpeedLeftText.place(relx=0, rely=0.3, relheight=0.30, relwidth=0.4)

currentDataFrameFanSpeedRightText = Label(currentDataFrameFanSpeed, text='Right Fan', font=("Arial", 15), fg='white', bg='#000000')
currentDataFrameFanSpeedRightText.place(relx=0, rely=0.65, relheight=0.30, relwidth=0.4)

fanSpeedCurrentLeftLabel = Label(currentDataFrameFanSpeed, bg='#676871', activebackground='#676871', font=("Arial", 17), fg='black')
fanSpeedCurrentLeftLabel.place(relx=0.4, rely=0.30, relheight=0.30, relwidth=0.5)

fanSpeedCurrentRightLabel = Label(currentDataFrameFanSpeed, bg='#676871', activebackground='#676871', font=("Arial", 17), fg='black')
fanSpeedCurrentRightLabel.place(relx=0.4, rely=0.65, relheight=0.30, relwidth=0.5)

#Current Data Temps
currentDataFrameTempText = Label(currentDataFrameTemp, text='Current Temps', font=("Arial", 20), fg='white', bg='#000000')
currentDataFrameTempText.place(relx=0, rely=0.025, relheight=0.20, relwidth=1)

currentDataFrameTempCPUText = Label(currentDataFrameTemp, text='CPU', font=("Arial", 15), fg='white', bg='#000000')
currentDataFrameTempCPUText.place(relx=0.005, rely=0.3, relheight=0.30, relwidth=0.4)

currentDataFrameTempGPUText = Label(currentDataFrameTemp, text='GPU', font=("Arial", 15), fg='white', bg='#000000')
currentDataFrameTempGPUText.place(relx=0.005, rely=0.65, relheight=0.30, relwidth=0.4)

tempCurrentCPULabel = Label(currentDataFrameTemp, bg='#676871', activebackground='#676871', font=("Arial", 17), fg='black')
tempCurrentCPULabel.place(relx=0.4, rely=0.30, relheight=0.30, relwidth=0.5)

tempCurrentGPULabel = Label(currentDataFrameTemp, bg='#676871', activebackground='#676871', font=("Arial", 17), fg='black')
tempCurrentGPULabel.place(relx=0.4, rely=0.65, relheight=0.30, relwidth=0.5)


# Buttons
perfBtn = Button(modes, image=perfIcon, command=perfBtnPressed)
perfBtn.place(x=100, width=100, height=100) #relwidth=0.20, relheight=1, relx=0.2

balancedBtn = Button(modes, image=balancedIcon,command=balancedBtnPressed)
balancedBtn.place(x=200, width=100, height=100)

quietBtn = Button(modes,image=quietIcon,command=quietBtnPressed)
quietBtn.place(x=300, width=100, height=100)

saveBtn = Button(modes, image=saveIcon,bg='#676871', activebackground='#676871', command=saveBtnPressed)
saveBtn.place(x=400, width=100, height=100)

settingsBtn = Button(modes, image=settingsIcon,bg='#676871', activebackground='#676871')
settingsBtn.place(x=500, width=100, height=100)

getCurrentPowerMode()
getCurrentData()
getCurrentFanCurve()

root.mainloop()