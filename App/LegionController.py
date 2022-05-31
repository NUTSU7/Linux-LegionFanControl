#!/usr/bin/python
from tkinter import *
from numpy import *
from customtkinter import *
from PIL import ImageTk, Image
import os, time, configparser, customtkinter

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

config = configparser.ConfigParser()
config.add_section('fanCurveQuiet')
config.add_section('fanCurveBalanced')
config.add_section('fanCurvePerf')

root = CTk()
root.geometry('800x900')
root.title('LegionController')
root.resizable(False, False)

root.bind("<Button-1>", lambda event: event.widget.focus_set())

#Vars
cwd=os.getcwd()
currentPowerMode = -1
previousPowerMode = -1
perfBtnPressedValue = False
balancedBtnPressedValue = False
quietBtnPressedValue = False
fanSpeedCurrent = -1
tempCurrent = -1
tempCurrentCPU = -1
tempCurrentGPU = -1
fanCurve = []
tempCurve = []
fanCurveCurrent = -1
fanCurveQuiet = []
fanCurveBalanced = []
fanCurvePerf = []
graphX = []
graphY = []
useTempCPU = True
gridPointsX = [0.0, 15.554, 31.108, 46.662, 62.216, 77.77, 93.324, 108.878, 124.432, 139.986, 155.54, 171.094, 186.648, 202.202, 217.756, 233.31, 248.864, 264.418, 279.972, 295.526, 311.08, 326.634, 342.188, 357.742, 373.296, 388.85, 404.404, 419.958, 435.512, 451.06600000000003, 466.62, 482.17400000000004, 497.728, 513.282, 528.836, 544.39, 559.944, 575.498, 591.052, 606.606, 622.16, 637.714, 653.268, 668.822, 684.376, 699.9300000000001]
gridPointsY = [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500]
currentPoint = -1

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
        updateEntryes()
        updateCanvas()
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
    global fanSpeedCurrent
    global tempCurrentCPU
    global tempCurrentGPU
    f = open("/sys/kernel/LegionController/fanSpeedCurrent", "r")
    fanSpeedCurrent = int(f.read()[:-1])*100
    f.close()
    fanSpeedCurrentLabel['text']=str(fanSpeedCurrent)+' RPM'
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
    configFileExist = os.path.exists(cwd+"/config.ini")
    
    if not configFileExist:
        config.set('fanCurveBalanced', 'fanCurve1', '0')
        config.set('fanCurveBalanced', 'fanCurve2', '1800')
        config.set('fanCurveBalanced', 'fanCurve3', '2200')
        config.set('fanCurveBalanced', 'fanCurve4', '2600')
        config.set('fanCurveBalanced', 'fanCurve5', '3500')
        config.set('fanCurveBalanced', 'fanCurve6', '3800')
        config.set('fanCurveBalanced', 'tempCurve1', '0')
        config.set('fanCurveBalanced', 'tempCurve2', '45')
        config.set('fanCurveBalanced', 'tempCurve3', '55')
        config.set('fanCurveBalanced', 'tempCurve4', '70')
        config.set('fanCurveBalanced', 'tempCurve5', '80')
        config.set('fanCurveBalanced', 'tempCurve6', '85')

        config.set('fanCurvePerf', 'fanCurve1', '0')
        config.set('fanCurvePerf', 'fanCurve2', '1800')
        config.set('fanCurvePerf', 'fanCurve3', '2200')
        config.set('fanCurvePerf', 'fanCurve4', '2600')
        config.set('fanCurvePerf', 'fanCurve5', '3500')
        config.set('fanCurvePerf', 'fanCurve6', '4400')
        config.set('fanCurvePerf', 'tempCurve1', '0')
        config.set('fanCurvePerf', 'tempCurve2', '45')
        config.set('fanCurvePerf', 'tempCurve3', '55')
        config.set('fanCurvePerf', 'tempCurve4', '70')
        config.set('fanCurvePerf', 'tempCurve5', '80')
        config.set('fanCurvePerf', 'tempCurve6', '90')

        config.set('fanCurveQuiet', 'fanCurve1', '0')
        config.set('fanCurveQuiet', 'fanCurve2', '1800')
        config.set('fanCurveQuiet', 'fanCurve3', '2200')
        config.set('fanCurveQuiet', 'fanCurve4', '2600')
        config.set('fanCurveQuiet', 'fanCurve5', '2900')
        config.set('fanCurveQuiet', 'fanCurve6', '3500')
        config.set('fanCurveQuiet', 'tempCurve1', '0')
        config.set('fanCurveQuiet', 'tempCurve2', '45')
        config.set('fanCurveQuiet', 'tempCurve3', '55')
        config.set('fanCurveQuiet', 'tempCurve4', '70')
        config.set('fanCurveQuiet', 'tempCurve5', '75')
        config.set('fanCurveQuiet', 'tempCurve6', '80')

        with open(cwd+r"/config.ini", 'w') as configfile:
            config.write(configfile)
    else:
        config.read(cwd+'/config.ini')
        fanCurveBalanced = config['fanCurveBalanced']
        fanCurvePerf = config['fanCurvePerf']
        fanCurveQuiet = config['fanCurveQuiet']

def getFanCurve():
    #axes.x = RPM/100*15.554
    #axes.y = 500-(C*5+25)
    global fanCurve
    global tempCurve
    global currentPowerMode
    global config
    global graphX
    global graphY
    fanCurve = []
    tempCurve = []
    graphX = []
    graphY = []
    
    if currentPowerMode == 0:
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve1']))
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve2']))
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve3']))
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve4']))
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve5']))
        fanCurve.append(int(config['fanCurveBalanced']['fanCurve6']))
        tempCurve.append(int(config['fanCurveBalanced']['tempCurve1']))
        tempCurve.append(int(config['fanCurveBalanced']['tempCurve2']))
        tempCurve.append(int(config['fanCurveBalanced']['tempCurve3']))
        tempCurve.append(int(config['fanCurveBalanced']['tempCurve4']))
        tempCurve.append(int(config['fanCurveBalanced']['tempCurve5']))
        tempCurve.append(int(config['fanCurveBalanced']['tempCurve6']))
    elif currentPowerMode == 1:
        fanCurve.append(int(config['fanCurvePerf']['fanCurve1']))
        fanCurve.append(int(config['fanCurvePerf']['fanCurve2']))
        fanCurve.append(int(config['fanCurvePerf']['fanCurve3']))
        fanCurve.append(int(config['fanCurvePerf']['fanCurve4']))
        fanCurve.append(int(config['fanCurvePerf']['fanCurve5']))
        fanCurve.append(int(config['fanCurvePerf']['fanCurve6']))
        tempCurve.append(int(config['fanCurvePerf']['tempCurve1']))
        tempCurve.append(int(config['fanCurvePerf']['tempCurve2']))
        tempCurve.append(int(config['fanCurvePerf']['tempCurve3']))
        tempCurve.append(int(config['fanCurvePerf']['tempCurve4']))
        tempCurve.append(int(config['fanCurvePerf']['tempCurve5']))
        tempCurve.append(int(config['fanCurvePerf']['tempCurve6']))
    elif currentPowerMode == 2:
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve1']))
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve2']))
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve3']))
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve4']))
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve5']))
        fanCurve.append(int(config['fanCurveQuiet']['fanCurve6']))
        tempCurve.append(int(config['fanCurveQuiet']['tempCurve1']))
        tempCurve.append(int(config['fanCurveQuiet']['tempCurve2']))
        tempCurve.append(int(config['fanCurveQuiet']['tempCurve3']))
        tempCurve.append(int(config['fanCurveQuiet']['tempCurve4']))
        tempCurve.append(int(config['fanCurveQuiet']['tempCurve5']))
        tempCurve.append(int(config['fanCurveQuiet']['tempCurve6']))
    
    graphX.append(fanCurve[0]/100*15.554)
    graphX.append(fanCurve[1]/100*15.554)
    graphX.append(fanCurve[2]/100*15.554)
    graphX.append(fanCurve[3]/100*15.554)
    graphX.append(fanCurve[4]/100*15.554)
    graphX.append(fanCurve[5]/100*15.554)
    graphY.append(525-(tempCurve[0]*5))
    graphY.append(525-(tempCurve[1]*5))
    graphY.append(525-(tempCurve[2]*5))
    graphY.append(525-(tempCurve[3]*5))
    graphY.append(525-(tempCurve[4]*5))
    graphY.append(525-(tempCurve[5]*5))
    

def updateEntryes():
    global fanCurve
    global tempCurve
    global tempCurrentGPU

    fanCurveEntry1.delete(0, END)
    fanCurveEntry2.delete(0, END)
    fanCurveEntry3.delete(0, END)
    fanCurveEntry4.delete(0, END)
    fanCurveEntry5.delete(0, END)
    fanCurveEntry6.delete(0, END)

    tempCurveEntry1.delete(0, END)
    tempCurveEntry2.delete(0, END)
    tempCurveEntry3.delete(0, END)
    tempCurveEntry4.delete(0, END)
    tempCurveEntry5.delete(0, END)
    tempCurveEntry6.delete(0, END)


    fanCurveEntry1.insert(0, fanCurve[0])
    fanCurveEntry2.insert(0, fanCurve[1])
    fanCurveEntry3.insert(0, fanCurve[2])
    fanCurveEntry4.insert(0, fanCurve[3])
    fanCurveEntry5.insert(0, fanCurve[4])
    fanCurveEntry6.insert(0, fanCurve[5])

    tempCurveEntry1.insert(0, tempCurve[0])
    tempCurveEntry2.insert(0, tempCurve[1])
    tempCurveEntry3.insert(0, tempCurve[2])
    tempCurveEntry4.insert(0, tempCurve[3])
    tempCurveEntry5.insert(0, tempCurve[4])
    tempCurveEntry6.insert(0, tempCurve[5])

def saveBtnPressed():
    global fanCurve
    global tempCurve
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
        config['fanCurveBalanced']['tempCurve1'] = tempCurveEntry1.get()
        config['fanCurveBalanced']['tempCurve2'] = tempCurveEntry2.get()
        config['fanCurveBalanced']['tempCurve3'] = tempCurveEntry3.get()
        config['fanCurveBalanced']['tempCurve4'] = tempCurveEntry4.get()
        config['fanCurveBalanced']['tempCurve5'] = tempCurveEntry5.get()
        config['fanCurveBalanced']['tempCurve6'] = tempCurveEntry6.get()
    elif currentPowerMode == 1:
        config['fanCurvePerf']['fanCurve1'] = fanCurveEntry1.get()
        config['fanCurvePerf']['fanCurve2'] = fanCurveEntry2.get()
        config['fanCurvePerf']['fanCurve3'] = fanCurveEntry3.get()
        config['fanCurvePerf']['fanCurve4'] = fanCurveEntry4.get()
        config['fanCurvePerf']['fanCurve5'] = fanCurveEntry5.get() 
        config['fanCurvePerf']['fanCurve6'] = fanCurveEntry6.get()
        config['fanCurvePerf']['tempCurve1'] = tempCurveEntry1.get()
        config['fanCurvePerf']['tempCurve2'] = tempCurveEntry2.get()
        config['fanCurvePerf']['tempCurve3'] = tempCurveEntry3.get()
        config['fanCurvePerf']['tempCurve4'] = tempCurveEntry4.get()
        config['fanCurvePerf']['tempCurve5'] = tempCurveEntry5.get()
        config['fanCurvePerf']['tempCurve6'] = tempCurveEntry6.get()
    elif currentPowerMode == 2:
        config['fanCurveQuiet']['fanCurve1'] = fanCurveEntry1.get()
        config['fanCurveQuiet']['fanCurve2'] = fanCurveEntry2.get()
        config['fanCurveQuiet']['fanCurve3'] = fanCurveEntry3.get()
        config['fanCurveQuiet']['fanCurve4'] = fanCurveEntry4.get()
        config['fanCurveQuiet']['fanCurve5'] = fanCurveEntry5.get() 
        config['fanCurveQuiet']['fanCurve6'] = fanCurveEntry6.get()
        config['fanCurveQuiet']['tempCurve1'] = tempCurveEntry1.get()
        config['fanCurveQuiet']['tempCurve2'] = tempCurveEntry2.get()
        config['fanCurveQuiet']['tempCurve3'] = tempCurveEntry3.get()
        config['fanCurveQuiet']['tempCurve4'] = tempCurveEntry4.get()
        config['fanCurveQuiet']['tempCurve5'] = tempCurveEntry5.get()
        config['fanCurveQuiet']['tempCurve6'] = tempCurveEntry6.get()

    with open(cwd+r"/config.ini", 'w') as configfile:
        config.write(configfile)

    getFanCurve()
    updateEntryes()

def updateFanCurve():
    global fanCurveCurrent
    global fanCurve
    global useTempCPU
    global tempCurrent
    global tempCurrentCPU
    global tempCurrentGPU

    if useTempCPU:
        tempCurrent = tempCurrentCPU
    else:
        tempCurrent = tempCurrentGPU

    if tempCurrent >= tempCurve[0] and tempCurrent < tempCurve[1]:
        fanCurveCurrent = fanCurve[0]/100
    elif tempCurrent >= tempCurve[1] and tempCurrent < tempCurve[2]:
        fanCurveCurrent = fanCurve[1]/100
    elif tempCurrent >= tempCurve[2] and tempCurrent < tempCurve[3]:
        fanCurveCurrent = fanCurve[2]/100
    elif tempCurrent >= tempCurve[3] and tempCurrent < tempCurve[4]:
        fanCurveCurrent = fanCurve[3]/100
    elif tempCurrent >= tempCurve[4] and tempCurrent < tempCurve[5]:
        fanCurveCurrent = fanCurve[4]/100
    elif tempCurrent >= tempCurve[5]:
        fanCurveCurrent = fanCurve[5]/100

    f = open("/sys/module/LegionController/parameters/cFanCurve", "w")
    f.write(str(fanCurveCurrent)[:-2])
    f.close()
    
    root.after(1000, updateFanCurve)

def updateCanvas():
    global graphX
    global graphY

    fanCurveCanvas.delete("all")

    for i in arange(0, 700, 15.554):
        fanCurveCanvas.create_line([(i, 0), (i, 525)], tag='grid_line', fill='#adaaaa', width=0.5)

    for i in arange(0, 525, 25):
        fanCurveCanvas.create_line([(0, i), (725, i)], tag='grid_line', fill='#adaaaa', width=0.5)

    #fanCurveCanvas.create_line(0,475,graphX[0],graphY[0], fill='green', width=5)
    fanCurveCanvas.create_line(graphX[0],graphY[0],graphX[1],graphY[1], fill='green', width=5, smooth=1)
    fanCurveCanvas.create_line(graphX[1],graphY[1],graphX[2],graphY[2], fill='green', width=5, smooth=1)
    fanCurveCanvas.create_line(graphX[2],graphY[2],graphX[3],graphY[3], fill='green', width=5, smooth=1)
    fanCurveCanvas.create_line(graphX[3],graphY[3],graphX[4],graphY[4], fill='green', width=5, smooth=1)
    fanCurveCanvas.create_line(graphX[4],graphY[4],graphX[5],graphY[5], fill='green', width=5, smooth=1)

    fanCurveCanvas.create_oval(graphX[0]-3,graphY[0]-3,graphX[0]+3,graphY[0]+3,fill="black", width=3)
    fanCurveCanvas.create_oval(graphX[1]-3,graphY[1]-3,graphX[1]+3,graphY[1]+3,fill="black", width=3)
    fanCurveCanvas.create_oval(graphX[2]-3,graphY[2]-3,graphX[2]+3,graphY[2]+3,fill="black", width=3)
    fanCurveCanvas.create_oval(graphX[3]-3,graphY[3]-3,graphX[3]+3,graphY[3]+3,fill="black", width=3)
    fanCurveCanvas.create_oval(graphX[4]-3,graphY[4]-3,graphX[4]+3,graphY[4]+3,fill="black", width=3)
    fanCurveCanvas.create_oval(graphX[5]-3,graphY[5]-3,graphX[5]+3,graphY[5]+3,fill="black", width=3)

def getCurrentPoint(event):
    global graphX
    global graphY
    global gridPointsX
    global gridPointsY
    global currentPoint

    currentPoint = -1

    x,y = root.winfo_pointerxy()
    widget = root.winfo_containing(x,y)

    if(str(widget) == ".!ctkframe.!ctkframe.!ctkcanvas2"):
        x = (15.554 * round(event.x / 15.554))
        y = (25 * round(event.y / 25))

        for i in range(0, 6):
            if x == graphX[i] and y == graphY[i]:
                currentPoint = i

def inputCanvas(event):
    global graphX
    global graphY
    global currentPoint

    x,y = root.winfo_pointerxy()
    widget = root.winfo_containing(x,y)

    if(str(widget) == ".!ctkframe.!ctkframe.!ctkcanvas2"):
        graphX[currentPoint] = (15.554 * round(event.x / 15.554))
        graphY[currentPoint] = (25 * round(event.y / 25))
        updateCanvas()


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
page.place(height=800, relwidth=1)

modes = CTkFrame(root)
modes.place(y=800, height=100, relwidth=1)

#Page Frames

fanCurveGraph = CTkFrame(page)
fanCurveGraph.place(width=800, height=600)

fanCurveFrame = CTkFrame(page)
fanCurveFrame.place(relwidth=1, height=150, y=600)

currentDataFrame = CTkFrame(page)
currentDataFrame.place(y=700, height=100, relwidth=1)

# Fan Curve Graph

fanCurveCanvas = CTkCanvas(fanCurveGraph)
fanCurveCanvas.place(y=25, x=50, width=725, height=525)


# 77.77 15.554  RPM = ((axes.x-25)/15.554)*100
# axes.x = RPM/100*15.554

fanCurveLabelRPM1 = CTkLabel(fanCurveGraph, text='0', text_font=("Arial", 12))
fanCurveLabelRPM1.place(x=25, y=550, height=50, width=50)

fanCurveLabelRPM2 = CTkLabel(fanCurveGraph, text='500', text_font=("Arial", 12))
fanCurveLabelRPM2.place(x=102.77, y=550, height=50, width=50)

fanCurveLabelRPM3 = CTkLabel(fanCurveGraph, text='1000', text_font=("Arial", 12))
fanCurveLabelRPM3.place(x=180.54, y=550, height=50, width=50)

fanCurveLabelRPM4 = CTkLabel(fanCurveGraph, text='1500', text_font=("Arial", 12))
fanCurveLabelRPM4.place(x=258.31, y=550, height=50, width=50)

fanCurveLabelRPM5 = CTkLabel(fanCurveGraph, text='2000', text_font=("Arial", 12))
fanCurveLabelRPM5.place(x=336.08, y=550, height=50, width=50)

fanCurveLabelRPM6 = CTkLabel(fanCurveGraph, text='2500', text_font=("Arial", 12))
fanCurveLabelRPM6.place(x=413.85, y=550, height=50, width=50)

fanCurveLabelRPM7 = CTkLabel(fanCurveGraph, text='3000', text_font=("Arial", 12))
fanCurveLabelRPM7.place(x=491.62, y=550, height=50, width=50)

fanCurveLabelRPM8 = CTkLabel(fanCurveGraph, text='3500', text_font=("Arial", 12))
fanCurveLabelRPM8.place(x=569.39, y=550, height=50, width=50)

fanCurveLabelRPM9 = CTkLabel(fanCurveGraph, text='4000', text_font=("Arial", 12))
fanCurveLabelRPM9.place(x=647.16, y=550, height=50, width=50)

fanCurveLabelRPM10 = CTkLabel(fanCurveGraph, text='4500', text_font=("Arial", 12))
fanCurveLabelRPM10.place(x=725, y=550, height=50, width=50)

# 50  5  C = (525-axes.y)/5
# axes.y = 525-(C*5)

fanCurveLabelTemp1 = CTkLabel(fanCurveGraph, text='0', text_font=("Arial", 12))
fanCurveLabelTemp1.place(y=535, height=30, width=50)

fanCurveLabelTemp2 = CTkLabel(fanCurveGraph, text='10', text_font=("Arial", 12))
fanCurveLabelTemp2.place(y=475, height=50, width=50)

fanCurveLabelTemp3 = CTkLabel(fanCurveGraph, text='20', text_font=("Arial", 12))
fanCurveLabelTemp3.place(y=425, height=50, width=50)

fanCurveLabelTemp4 = CTkLabel(fanCurveGraph, text='30', text_font=("Arial", 12))
fanCurveLabelTemp4.place(y=375, height=50, width=50)

fanCurveLabelTemp5 = CTkLabel(fanCurveGraph, text='40', text_font=("Arial", 12))
fanCurveLabelTemp5.place(y=325, height=50, width=50)

fanCurveLabelTemp6 = CTkLabel(fanCurveGraph, text='50', text_font=("Arial", 12))
fanCurveLabelTemp6.place(y=275, height=50, width=50)

fanCurveLabelTemp7 = CTkLabel(fanCurveGraph, text='60', text_font=("Arial", 12))
fanCurveLabelTemp7.place(y=225, height=50, width=50)

fanCurveLabelTemp8 = CTkLabel(fanCurveGraph, text='70', text_font=("Arial", 12))
fanCurveLabelTemp8.place(y=175, height=50, width=50)

fanCurveLabelTemp8 = CTkLabel(fanCurveGraph, text='80', text_font=("Arial", 12))
fanCurveLabelTemp8.place(y=125, height=50, width=50)

fanCurveLabelTemp9 = CTkLabel(fanCurveGraph, text='90', text_font=("Arial", 12))
fanCurveLabelTemp9.place(y=75, height=50, width=50)

fanCurveLabelTemp10 = CTkLabel(fanCurveGraph, text='100', text_font=("Arial", 12))
fanCurveLabelTemp10.place(y=25, height=50, width=50)


# Fan Curve Input Left Frame elements
fanCurveText = CTkLabel(fanCurveFrame, text='Fan Speed (RPM)', text_font=("Arial", 15))
fanCurveText.place(x=5, y=15, height=30, width=175)

tempCurveText = CTkLabel(fanCurveFrame, text='Temp (°C)', text_font=("Arial", 15))
tempCurveText.place(x=5, y=55, height=30, width=175)


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


tempCurveEntry1 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveEntry1.place(x=180, y=55, height=30, width=70)

tempCurveEntry2 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveEntry2.place(x=260, y=55, height=30, width=70)

tempCurveEntry3 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveEntry3.place(x=340, y=55, height=30, width=70)

tempCurveEntry4 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveEntry4.place(x=420, y=55, height=30, width=70)

tempCurveEntry5 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveEntry5.place(x=500, y=55, height=30, width=70)

tempCurveEntry6 = CTkEntry(fanCurveFrame, text_font=("Arial", 15), justify='center')
tempCurveEntry6.place(x=580, y=55, height=30, width=70)


#Current Data Frame elements
currentDataFrameFanSpeed = CTkFrame(currentDataFrame)
currentDataFrameFanSpeed.place(height=100, width=400)

currentDataFrameTemp = CTkFrame(currentDataFrame)
currentDataFrameTemp.place(height=100, width=400, x=400)


#Current Data Fan Speed
currentDataFrameFanSpeedText = CTkLabel(currentDataFrameFanSpeed, text='Current Fan Speed', text_font=("Arial", 17), justify='center')
currentDataFrameFanSpeedText.place(rely=0.025, relheight=0.3, relwidth=1)

fanSpeedCurrentLabel = CTkLabel(currentDataFrameFanSpeed, text_font=("Arial", 17), justify='center', fg_color='#b8b6b0', text_color='black')
fanSpeedCurrentLabel.place(relx=0.3, rely=0.4, relheight=0.4, relwidth=0.4)


#Current Data Temps
currentDataFrameTempText = CTkLabel(currentDataFrameTemp, text='Current Temps', text_font=("Arial", 17), justify='center')
currentDataFrameTempText.place(relheight=0.20, relwidth=1)

currentDataFrameTempCPUText = CTkLabel(currentDataFrameTemp, text='CPU', text_font=("Arial", 17), justify='center')
currentDataFrameTempCPUText.place(rely=0.3, relheight=0.3, relwidth=0.5)

currentDataFrameTempGPUText = CTkLabel(currentDataFrameTemp, text='GPU', text_font=("Arial", 17), justify='center')
currentDataFrameTempGPUText.place(rely=0.65, relheight=0.3, relwidth=0.5)

tempCurrentCPULabel = CTkLabel(currentDataFrameTemp, text_font=("Arial", 17), justify='center', fg_color='#b8b6b0', text_color='black')
tempCurrentCPULabel.place(relx=0.55, rely=0.30, relheight=0.3, relwidth=0.40)

tempCurrentGPULabel = CTkLabel(currentDataFrameTemp, text_font=("Arial", 17), justify='center', fg_color='#b8b6b0', text_color='black')
tempCurrentGPULabel.place(relx=0.55, rely=0.65, relheight=0.3, relwidth=0.40)


# Buttons
perfBtn = CTkButton(modes, image=perfIcon, text='', command=perfBtnPressed)
perfBtn.place(x=150, width=90, height=90, y=5)

balancedBtn = CTkButton(modes, image=balancedIcon, text='', command=balancedBtnPressed)
balancedBtn.place(x=250, width=90, height=90, y=5)

quietBtn = CTkButton(modes, image=quietIcon, text='', command=quietBtnPressed)
quietBtn.place(x=350, width=90, height=90, y=5)

saveBtn = CTkButton(modes, image=saveIcon, text='', command=saveBtnPressed)
saveBtn.place(x=450, width=90, height=90, y=5)

settingsBtn = CTkButton(modes, image=settingsIcon, text='')
settingsBtn.place(x=550, width=90, height=90, y=5)

getCurrentPowerMode()
getCurrentData()
updateFanCurve()
root.bind("<ButtonPress-1>", getCurrentPoint)
root.bind("<ButtonRelease-1>", inputCanvas)

root.mainloop()