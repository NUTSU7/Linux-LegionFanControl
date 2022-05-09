#!/usr/bin/python
from tkinter import *
import customtkinter
from customtkinter import *
from PIL import ImageTk, Image
import os, time
from importlib_metadata import entry_points
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import configparser

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

config = configparser.ConfigParser()
config.add_section('fanCurveQuiet')
config.add_section('fanCurveBalanced')
config.add_section('fanCurvePerf')

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

root = CTk()
root.geometry('700x700')
root.title('LegionController')
root.resizable(False, False)
root.bind_all("<Button-1>", lambda event: event.widget.focus_set())

#Vars
cwd=os.getcwd()
currentPowerMode = -1
previousPowerMode = -1
perfBtnPressedValue = False
balancedBtnPressedValue = False
quietBtnPressedValue = False
fanSpeedCurrentLeft = -1
fanSpeedCurrentRight = -1
tempCurrentCPU = -1
tempCurrentGPU = -1
fanCurve = []
tempCurveCPU = []
tempCurveGPU = []
fanCurveCurrent = -1
tempCurveCurrentCPU = -1
tempCurveCurrentGPU = -1
fanCurveQuiet = []
fanCurveBalanced = []
fanCurvePerf = []

#Functions
def getCurrentPowerMode():
    global currentPowerMode
    global previousPowerMode

    previousPowerMode=currentPowerMode
    f = open("/sys/kernel/LegionController/powerMode", "r")
    currentPowerMode = int(f.read()[:-1])
    f.close
    if previousPowerMode != currentPowerMode:
        if currentPowerMode == 0: 
            perfBtn.configure(fg_color='#1c94cf')
            balancedBtn.configure(fg_color='#2333B4')
            quietBtn.configure(fg_color='#1c94cf')
        elif currentPowerMode == 1: 
            perfBtn.configure(fg_color='#2333B4')
            balancedBtn.configure(fg_color='#1c94cf')
            quietBtn.configure(fg_color='#1c94cf')
        elif currentPowerMode == 2: 
            perfBtn.configure(fg_color='#1c94cf')
            balancedBtn.configure(fg_color='#1c94cf')
            quietBtn.configure(fg_color='#2333B4')
        getFanCurve()
        changeEntryes()
    root.after(2000, getCurrentPowerMode)

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

def getCurrentData():
    global fanSpeedCurrentLeft
    global fanSpeedCurrentRight
    global tempCurrentCPU
    global tempCurrentGPU
    f = open("/sys/kernel/LegionController/fanSpeedCurrentLeft", "r")
    fanSpeedCurrentLeft = int(f.read()[:-1])*100
    f.close()
    fanSpeedCurrentLeftLabel['text']=str(fanSpeedCurrentLeft)+' RPM'
    f = open("/sys/kernel/LegionController/fanSpeedCurrentRight", "r")
    fanSpeedCurrentRight = int(f.read()[:-1])*100
    f.close()
    fanSpeedCurrentRightLabel['text']=str(fanSpeedCurrentRight)+' RPM'
    f = open("/sys/kernel/LegionController/tempCurrentCPU", "r")
    tempCurrentCPU = int(f.read()[:-1])
    f.close()
    tempCurrentCPULabel['text']=str(tempCurrentCPU)+' °C'
    f = open("/sys/kernel/LegionController/tempCurrentGPU", "r")
    tempCurrentGPU = int(f.read()[:-1])
    f.close()
    tempCurrentGPULabel['text']=str(tempCurrentGPU)+' °C'
    tempCurrentGPULabel.after(2000, getCurrentData)

def loadConfig():
    global currentPowerMode
    global fanCurveQuiet
    global fanCurveBalanced
    global fanCurvePerf
    global config
    configFileExist = os.path.exists("config.txt")
    
    if not configFileExist:
        config.set('fanCurveBalanced', 'fanCurve1', '0')
        config.set('fanCurveBalanced', 'fanCurve2', '1800')
        config.set('fanCurveBalanced', 'fanCurve3', '2200')
        config.set('fanCurveBalanced', 'fanCurve4', '2600')
        config.set('fanCurveBalanced', 'fanCurve5', '3500')
        config.set('fanCurveBalanced', 'fanCurve6', '3800')
        config.set('fanCurveBalanced', 'tempCurveCPU1', '0')
        config.set('fanCurveBalanced', 'tempCurveCPU2', '45')
        config.set('fanCurveBalanced', 'tempCurveCPU3', '55')
        config.set('fanCurveBalanced', 'tempCurveCPU4', '68')
        config.set('fanCurveBalanced', 'tempCurveCPU5', '78')
        config.set('fanCurveBalanced', 'tempCurveCPU6', '85')
        config.set('fanCurveBalanced', 'tempCurveGPU1', '0')
        config.set('fanCurveBalanced', 'tempCurveGPU2', '45')
        config.set('fanCurveBalanced', 'tempCurveGPU3', '55')
        config.set('fanCurveBalanced', 'tempCurveGPU4', '68')
        config.set('fanCurveBalanced', 'tempCurveGPU5', '78')
        config.set('fanCurveBalanced', 'tempCurveGPU6', '85')

        config.set('fanCurvePerf', 'fanCurve1', '0')
        config.set('fanCurvePerf', 'fanCurve2', '1800')
        config.set('fanCurvePerf', 'fanCurve3', '2200')
        config.set('fanCurvePerf', 'fanCurve4', '2600')
        config.set('fanCurvePerf', 'fanCurve5', '3500')
        config.set('fanCurvePerf', 'fanCurve6', '4400')
        config.set('fanCurvePerf', 'tempCurveCPU1', '0')
        config.set('fanCurvePerf', 'tempCurveCPU2', '45')
        config.set('fanCurvePerf', 'tempCurveCPU3', '55')
        config.set('fanCurvePerf', 'tempCurveCPU4', '68')
        config.set('fanCurvePerf', 'tempCurveCPU5', '78')
        config.set('fanCurvePerf', 'tempCurveCPU6', '91')
        config.set('fanCurvePerf', 'tempCurveGPU1', '0')
        config.set('fanCurvePerf', 'tempCurveGPU2', '45')
        config.set('fanCurvePerf', 'tempCurveGPU3', '55')
        config.set('fanCurvePerf', 'tempCurveGPU4', '68')
        config.set('fanCurvePerf', 'tempCurveGPU5', '78')
        config.set('fanCurvePerf', 'tempCurveGPU6', '91')

        config.set('fanCurveQuiet', 'fanCurve1', '0')
        config.set('fanCurveQuiet', 'fanCurve2', '1800')
        config.set('fanCurveQuiet', 'fanCurve3', '2200')
        config.set('fanCurveQuiet', 'fanCurve4', '2600')
        config.set('fanCurveQuiet', 'fanCurve5', '2900')
        config.set('fanCurveQuiet', 'fanCurve6', '3500')
        config.set('fanCurveQuiet', 'tempCurveCPU1', '0')
        config.set('fanCurveQuiet', 'tempCurveCPU2', '45')
        config.set('fanCurveQuiet', 'tempCurveCPU3', '55')
        config.set('fanCurveQuiet', 'tempCurveCPU4', '68')
        config.set('fanCurveQuiet', 'tempCurveCPU5', '72')
        config.set('fanCurveQuiet', 'tempCurveCPU6', '78')
        config.set('fanCurveQuiet', 'tempCurveGPU1', '0')
        config.set('fanCurveQuiet', 'tempCurveGPU2', '45')
        config.set('fanCurveQuiet', 'tempCurveGPU3', '55')
        config.set('fanCurveQuiet', 'tempCurveGPU4', '68')
        config.set('fanCurveQuiet', 'tempCurveGPU5', '72')
        config.set('fanCurveQuiet', 'tempCurveGPU6', '78')

        with open(cwd+r"config.ini", 'w') as configfile:
            config.write(configfile)
    else:
        config.read(cwd+'config.ini')
        fanCurveBalanced = config['fanCurveBalanced']
        fanCurvePerf = config['fanCurvePerf']
        fanCurveQuiet = config['fanCurveQuiet']

def getFanCurve():
    global fanCurve
    global tempCurveCPU
    global tempCurveGPU
    global currentPowerMode
    global config
    fanCurve = []
    tempCurveCPU = []
    tempCurveGPU = []
    
    if currentPowerMode == 0:
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve1']))
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve2']))
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve3']))
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve4']))
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve5']))
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve6']))
        tempCurveCPU.append(int(config['fanCurveBalanced']['tempCurveCPU1']))
        tempCurveCPU.append(int(config['fanCurveBalanced']['tempCurveCPU2']))
        tempCurveCPU.append(int(config['fanCurveBalanced']['tempCurveCPU3']))
        tempCurveCPU.append(int(config['fanCurveBalanced']['tempCurveCPU4']))
        tempCurveCPU.append(int(config['fanCurveBalanced']['tempCurveCPU5']))
        tempCurveCPU.append(int(config['fanCurveBalanced']['tempCurveCPU6']))
        tempCurveGPU.append(int(config['fanCurveBalanced']['tempCurveGPU1']))
        tempCurveGPU.append(int(config['fanCurveBalanced']['tempCurveGPU2']))
        tempCurveGPU.append(int(config['fanCurveBalanced']['tempCurveGPU3']))
        tempCurveGPU.append(int(config['fanCurveBalanced']['tempCurveGPU4']))
        tempCurveGPU.append(int(config['fanCurveBalanced']['tempCurveGPU5']))
        tempCurveGPU.append(int(config['fanCurveBalanced']['tempCurveGPU6']))
    elif currentPowerMode == 1:
        fanCurve.append(int(config['fanCurvePerf']['fanCurve1']))
        fanCurve.append(int(config['fanCurvePerf']['fanCurve2']))
        fanCurve.append(int(config['fanCurvePerf']['fanCurve3']))
        fanCurve.append(int(config['fanCurvePerf']['fanCurve4']))
        fanCurve.append(int(config['fanCurvePerf']['fanCurve5']))
        fanCurve.append(int(config['fanCurvePerf']['fanCurve6']))
        tempCurveCPU.append(int(config['fanCurvePerf']['tempCurveCPU1']))
        tempCurveCPU.append(int(config['fanCurvePerf']['tempCurveCPU2']))
        tempCurveCPU.append(int(config['fanCurvePerf']['tempCurveCPU3']))
        tempCurveCPU.append(int(config['fanCurvePerf']['tempCurveCPU4']))
        tempCurveCPU.append(int(config['fanCurvePerf']['tempCurveCPU5']))
        tempCurveCPU.append(int(config['fanCurvePerf']['tempCurveCPU6']))
        tempCurveGPU.append(int(config['fanCurvePerf']['tempCurveGPU1']))
        tempCurveGPU.append(int(config['fanCurvePerf']['tempCurveGPU2']))
        tempCurveGPU.append(int(config['fanCurvePerf']['tempCurveGPU3']))
        tempCurveGPU.append(int(config['fanCurvePerf']['tempCurveGPU4']))
        tempCurveGPU.append(int(config['fanCurvePerf']['tempCurveGPU5']))
        tempCurveGPU.append(int(config['fanCurvePerf']['tempCurveGPU6']))
    elif currentPowerMode == 2:
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve1']))
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve2']))
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve3']))
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve4']))
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve5']))
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve6']))
        tempCurveCPU.append(int(config['fanCurveQuiet']['tempCurveCPU1']))
        tempCurveCPU.append(int(config['fanCurveQuiet']['tempCurveCPU2']))
        tempCurveCPU.append(int(config['fanCurveQuiet']['tempCurveCPU3']))
        tempCurveCPU.append(int(config['fanCurveQuiet']['tempCurveCPU4']))
        tempCurveCPU.append(int(config['fanCurveQuiet']['tempCurveCPU5']))
        tempCurveCPU.append(int(config['fanCurveQuiet']['tempCurveCPU6']))
        tempCurveGPU.append(int(config['fanCurveQuiet']['tempCurveGPU1']))
        tempCurveGPU.append(int(config['fanCurveQuiet']['tempCurveGPU2']))
        tempCurveGPU.append(int(config['fanCurveQuiet']['tempCurveGPU3']))
        tempCurveGPU.append(int(config['fanCurveQuiet']['tempCurveGPU4']))
        tempCurveGPU.append(int(config['fanCurveQuiet']['tempCurveGPU5']))
        tempCurveGPU.append(int(config['fanCurveQuiet']['tempCurveGPU6']))
        
    

def changeEntryes():
    global fanCurve
    global tempCurveCPU
    fanCurveEntry1.delete(0, END)
    fanCurveEntry2.delete(0, END)
    fanCurveEntry3.delete(0, END)
    fanCurveEntry4.delete(0, END)
    fanCurveEntry5.delete(0, END)
    fanCurveEntry6.delete(0, END)

    tempCurveCPUEntry1.delete(0, END)
    tempCurveCPUEntry2.delete(0, END)
    tempCurveCPUEntry3.delete(0, END)
    tempCurveCPUEntry4.delete(0, END)
    tempCurveCPUEntry5.delete(0, END)
    tempCurveCPUEntry6.delete(0, END)

    tempCurveGPUEntry1.delete(0, END)
    tempCurveGPUEntry2.delete(0, END)
    tempCurveGPUEntry3.delete(0, END)
    tempCurveGPUEntry4.delete(0, END)
    tempCurveGPUEntry5.delete(0, END)
    tempCurveGPUEntry6.delete(0, END)

    fanCurveEntry1.insert(0, fanCurve[0])
    fanCurveEntry2.insert(0, fanCurve[1])
    fanCurveEntry3.insert(0, fanCurve[2])
    fanCurveEntry4.insert(0, fanCurve[3])
    fanCurveEntry5.insert(0, fanCurve[4])
    fanCurveEntry6.insert(0, fanCurve[5])

    tempCurveCPUEntry1.insert(0, tempCurveCPU[0])
    tempCurveCPUEntry2.insert(0, tempCurveCPU[1])
    tempCurveCPUEntry3.insert(0, tempCurveCPU[2])
    tempCurveCPUEntry4.insert(0, tempCurveCPU[3])
    tempCurveCPUEntry5.insert(0, tempCurveCPU[4])
    tempCurveCPUEntry6.insert(0, tempCurveCPU[5])

    tempCurveGPUEntry1.insert(0, int(tempCurveGPU[0]))
    tempCurveGPUEntry2.insert(0, int(tempCurveGPU[1]))
    tempCurveGPUEntry3.insert(0, int(tempCurveGPU[2]))
    tempCurveGPUEntry4.insert(0, int(tempCurveGPU[3]))
    tempCurveGPUEntry5.insert(0, int(tempCurveGPU[4]))
    tempCurveGPUEntry6.insert(0, int(tempCurveGPU[5]))

def saveBtnPressed():
    global fanCurve
    global tempCurveCPU
    global tempCurveGPU
    global currentPowerMode
    global config

    root.after(100, lambda: saveBtn.configure(fg_color='#2333B4'))
    root.after(500, lambda: saveBtn.configure(fg_color='#1c94cf'))
    
    if currentPowerMode == 0:
        config['fanCurveBalanced']['fanCurve1'] = fanCurveEntry1.get()
        config['fanCurveBalanced']['fanCurve2'] = fanCurveEntry2.get()
        config['fanCurveBalanced']['fanCurve3'] = fanCurveEntry3.get()
        config['fanCurveBalanced']['fanCurve4'] = fanCurveEntry4.get()
        config['fanCurveBalanced']['fanCurve5'] = fanCurveEntry5.get() 
        config['fanCurveBalanced']['fanCurve6'] = fanCurveEntry6.get()
        config['fanCurveBalanced']['tempCurveCPU1'] = tempCurveCPUEntry1.get()
        config['fanCurveBalanced']['tempCurveCPU2'] = tempCurveCPUEntry2.get()
        config['fanCurveBalanced']['tempCurveCPU3'] = tempCurveCPUEntry3.get()
        config['fanCurveBalanced']['tempCurveCPU4'] = tempCurveCPUEntry4.get()
        config['fanCurveBalanced']['tempCurveCPU5'] = tempCurveCPUEntry5.get()
        config['fanCurveBalanced']['tempCurveCPU6'] = tempCurveCPUEntry6.get()
        config['fanCurveBalanced']['tempCurveGPU1'] = tempCurveGPUEntry1.get()
        config['fanCurveBalanced']['tempCurveGPU2'] = tempCurveGPUEntry2.get()
        config['fanCurveBalanced']['tempCurveGPU3'] = tempCurveGPUEntry3.get()
        config['fanCurveBalanced']['tempCurveGPU4'] = tempCurveGPUEntry4.get()
        config['fanCurveBalanced']['tempCurveGPU5'] = tempCurveGPUEntry5.get()
        config['fanCurveBalanced']['tempCurveGPU6'] = tempCurveGPUEntry6.get()
    elif currentPowerMode == 1:
        config['fanCurvePerf']['fanCurve1'] = fanCurveEntry1.get()
        config['fanCurvePerf']['fanCurve2'] = fanCurveEntry2.get()
        config['fanCurvePerf']['fanCurve3'] = fanCurveEntry3.get()
        config['fanCurvePerf']['fanCurve4'] = fanCurveEntry4.get()
        config['fanCurvePerf']['fanCurve5'] = fanCurveEntry5.get() 
        config['fanCurvePerf']['fanCurve6'] = fanCurveEntry6.get()
        config['fanCurvePerf']['tempCurveCPU1'] = tempCurveCPUEntry1.get()
        config['fanCurvePerf']['tempCurveCPU2'] = tempCurveCPUEntry2.get()
        config['fanCurvePerf']['tempCurveCPU3'] = tempCurveCPUEntry3.get()
        config['fanCurvePerf']['tempCurveCPU4'] = tempCurveCPUEntry4.get()
        config['fanCurvePerf']['tempCurveCPU5'] = tempCurveCPUEntry5.get()
        config['fanCurvePerf']['tempCurveCPU6'] = tempCurveCPUEntry6.get()
        config['fanCurvePerf']['tempCurveGPU1'] = tempCurveGPUEntry1.get()
        config['fanCurvePerf']['tempCurveGPU2'] = tempCurveGPUEntry2.get()
        config['fanCurvePerf']['tempCurveGPU3'] = tempCurveGPUEntry3.get()
        config['fanCurvePerf']['tempCurveGPU4'] = tempCurveGPUEntry4.get()
        config['fanCurvePerf']['tempCurveGPU5'] = tempCurveGPUEntry5.get()
        config['fanCurvePerf']['tempCurveGPU6'] = tempCurveGPUEntry6.get()
    elif currentPowerMode == 2:
        config['fanCurveQuiet']['fanCurve1'] = fanCurveEntry1.get()
        config['fanCurveQuiet']['fanCurve2'] = fanCurveEntry2.get()
        config['fanCurveQuiet']['fanCurve3'] = fanCurveEntry3.get()
        config['fanCurveQuiet']['fanCurve4'] = fanCurveEntry4.get()
        config['fanCurveQuiet']['fanCurve5'] = fanCurveEntry5.get() 
        config['fanCurveQuiet']['fanCurve6'] = fanCurveEntry6.get()
        config['fanCurveQuiet']['tempCurveCPU1'] = tempCurveCPUEntry1.get()
        config['fanCurveQuiet']['tempCurveCPU2'] = tempCurveCPUEntry2.get()
        config['fanCurveQuiet']['tempCurveCPU3'] = tempCurveCPUEntry3.get()
        config['fanCurveQuiet']['tempCurveCPU4'] = tempCurveCPUEntry4.get()
        config['fanCurveQuiet']['tempCurveCPU5'] = tempCurveCPUEntry5.get()
        config['fanCurveQuiet']['tempCurveCPU6'] = tempCurveCPUEntry6.get()
        config['fanCurveQuiet']['tempCurveGPU1'] = tempCurveGPUEntry1.get()
        config['fanCurveQuiet']['tempCurveGPU2'] = tempCurveGPUEntry2.get()
        config['fanCurveQuiet']['tempCurveGPU3'] = tempCurveGPUEntry3.get()
        config['fanCurveQuiet']['tempCurveGPU4'] = tempCurveGPUEntry4.get()
        config['fanCurveQuiet']['tempCurveGPU5'] = tempCurveGPUEntry5.get()
        config['fanCurveQuiet']['tempCurveGPU6'] = tempCurveGPUEntry6.get()

    with open(cwd+r"config.ini", 'w') as configfile:
        config.write(configfile)

    getFanCurve()
    changeEntryes()

def changeFanCurve():
    global fanCurveCurrent
    
    f = open("/sys/module/LegionController/parameters/cFanCurveLeft", "w")
    f.write(str(fanCurveCurrent))
    f.close()

#Images
#Window icon
img = Image.open(cwd+"/img/main.xbm") # .ico for windows, .xbm for linux
mainIcon = ImageTk.PhotoImage(img)
root.tk.call('wm', 'iconphoto', root._w, mainIcon)
#Performance Mode Icon
img = Image.open(cwd+"/img/perf.png") 
img.thumbnail((80,80), Image.ANTIALIAS)
perfIcon = ImageTk.PhotoImage(img)
#Balanced Mode Icon
img = Image.open(cwd+"/img/balanced.png") 
img.thumbnail((80,80), Image.ANTIALIAS)
balancedIcon = ImageTk.PhotoImage(img)
#Quiet Mode Icon
img = Image.open(cwd+"/img/quiet.png") 
img.thumbnail((80,80), Image.ANTIALIAS)
quietIcon = ImageTk.PhotoImage(img)
#Save Icon
img = Image.open(cwd+"/img/save.png") 
img.thumbnail((80,80), Image.ANTIALIAS)
saveIcon = ImageTk.PhotoImage(img)
#Settings Icon
img = Image.open(cwd+"/img/settings.png") 
img.thumbnail((75,75), Image.ANTIALIAS)
settingsIcon = ImageTk.PhotoImage(img)

loadConfig()


# Main Frames
page = CTkFrame(root)
page.place(height=600, width=700)

modes = CTkFrame(root)
modes.place(y=600, height=100, width=700)

#Page Frames
fanCurveFrame = CTkFrame(page)
fanCurveFrame.place(relwidth=1, height=140, y=360)

currentDataFrame = CTkFrame(page)
currentDataFrame.place(y=500, height=100, relwidth=1)


# Fan Curve Input Left Frame elements
fanCurveText = CTkLabel(fanCurveFrame, text='Left Fan (RPM)', text_font=("Arial", 15))
fanCurveText.place(x=5, y=15, height=30, width=175)

tempCurveCPUText = CTkLabel(fanCurveFrame, text='CPU Temp (°C)', text_font=("Arial", 15))
tempCurveCPUText.place(x=5, y=55, height=30, width=175)

tempCurveGPUText = CTkLabel(fanCurveFrame, text='CPU Temp (°C)', text_font=("Arial", 15))
tempCurveGPUText.place(x=5, y=95, height=30, width=175)

fanCurveEntry1 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
fanCurveEntry1.place(x=180, y=15, height=30, width=70)

fanCurveEntry2 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
fanCurveEntry2.place(x=260, y=15, height=30, width=70)

fanCurveEntry3 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
fanCurveEntry3.place(x=340, y=15, height=30, width=70)

fanCurveEntry4 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
fanCurveEntry4.place(x=420, y=15, height=30, width=70)

fanCurveEntry5 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
fanCurveEntry5.place(x=500, y=15, height=30, width=70)

fanCurveEntry6 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
fanCurveEntry6.place(x=580, y=15, height=30, width=70)


tempCurveCPUEntry1 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveCPUEntry1.place(x=180, y=55, height=30, width=70)

tempCurveCPUEntry2 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveCPUEntry2.place(x=260, y=55, height=30, width=70)

tempCurveCPUEntry3 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveCPUEntry3.place(x=340, y=55, height=30, width=70)

tempCurveCPUEntry4 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveCPUEntry4.place(x=420, y=55, height=30, width=70)

tempCurveCPUEntry5 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveCPUEntry5.place(x=500, y=55, height=30, width=70)

tempCurveCPUEntry6 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveCPUEntry6.place(x=580, y=55, height=30, width=70)

tempCurveGPUEntry1 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveGPUEntry1.place(x=180, y=95, height=30, width=70)

tempCurveGPUEntry2 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveGPUEntry2.place(x=260, y=95, height=30, width=70)

tempCurveGPUEntry3 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveGPUEntry3.place(x=340, y=95, height=30, width=70)

tempCurveGPUEntry4 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveGPUEntry4.place(x=420, y=95, height=30, width=70)

tempCurveGPUEntry5 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveGPUEntry5.place(x=500, y=95, height=30, width=70)

tempCurveGPUEntry6 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveGPUEntry6.place(x=580, y=95, height=30, width=70)


#Current Data Frame elements
currentDataFrameFanSpeed = CTkFrame(currentDataFrame)
currentDataFrameFanSpeed.place(height=100, width=350)

currentDataFrameTemp = CTkFrame(currentDataFrame)
currentDataFrameTemp.place(height=100, width=350, x=350)


#Current Data Fan Speed
currentDataFrameFanSpeedText = CTkLabel(currentDataFrameFanSpeed, text='Current Fan Speed', text_font=("Arial", 15))
currentDataFrameFanSpeedText.place(rely=0.025, relheight=0.20, relwidth=1)

currentDataFrameFanSpeedLeftText = CTkLabel(currentDataFrameFanSpeed, text='Left Fan', text_font=("Arial", 15))
currentDataFrameFanSpeedLeftText.place(rely=0.3, relheight=0.30, relwidth=0.4)

currentDataFrameFanSpeedRightText = CTkLabel(currentDataFrameFanSpeed, text='Right Fan', text_font=("Arial", 15))
currentDataFrameFanSpeedRightText.place(rely=0.65, relheight=0.30, relwidth=0.4)

fanSpeedCurrentLeftLabel = CTkLabel(currentDataFrameFanSpeed, text_font=("Arial", 17))
fanSpeedCurrentLeftLabel.place(relx=0.4, rely=0.30, relheight=0.30, relwidth=0.5)

fanSpeedCurrentRightLabel = CTkLabel(currentDataFrameFanSpeed, text_font=("Arial", 17))
fanSpeedCurrentRightLabel.place(relx=0.4, rely=0.65, relheight=0.30, relwidth=0.5)


#Current Data Temps
currentDataFrameTempText = CTkLabel(currentDataFrameTemp, text='Current Temps', text_font=("Arial", 15))
currentDataFrameTempText.place(rely=0.025, relheight=0.20, relwidth=1)

currentDataFrameTempCPUText = CTkLabel(currentDataFrameTemp, text='CPU', text_font=("Arial", 15))
currentDataFrameTempCPUText.place(relx=0.005, rely=0.3, relheight=0.30, relwidth=0.4)

currentDataFrameTempGPUText = CTkLabel(currentDataFrameTemp, text='GPU', text_font=("Arial", 15))
currentDataFrameTempGPUText.place(relx=0.005, rely=0.65, relheight=0.30, relwidth=0.4)

tempCurrentCPULabel = CTkLabel(currentDataFrameTemp, text_font=("Arial", 17))
tempCurrentCPULabel.place(relx=0.4, rely=0.30, relheight=0.30, relwidth=0.5)

tempCurrentGPULabel = CTkLabel(currentDataFrameTemp, text_font=("Arial", 17))
tempCurrentGPULabel.place(relx=0.4, rely=0.65, relheight=0.30, relwidth=0.5)


# Buttons
perfBtn = CTkButton(modes, image=perfIcon, text='', command=perfBtnPressed)
perfBtn.place(x=100, width=90, height=90, y=5)

balancedBtn = CTkButton(modes, image=balancedIcon, text='', command=balancedBtnPressed)
balancedBtn.place(x=200, width=90, height=90, y=5)

quietBtn = CTkButton(modes, image=quietIcon, text='', command=quietBtnPressed)
quietBtn.place(x=300, width=90, height=90, y=5)

saveBtn = CTkButton(modes, image=saveIcon, text='', command=saveBtnPressed)
saveBtn.place(x=400, width=90, height=90, y=5)

settingsBtn = CTkButton(modes, image=settingsIcon, text='')
settingsBtn.place(x=500, width=90, height=90, y=5)

getCurrentPowerMode()
getCurrentData()

root.mainloop()