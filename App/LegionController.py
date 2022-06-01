#!/usr/bin/python
from tkinter import *
from numpy import *
from customtkinter import *
from PIL import ImageTk, Image
import os, time, configparser, customtkinter
import atexit

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

config = configparser.ConfigParser()
config.add_section('fanCurveQuiet')
config.add_section('fanCurveBalanced')
config.add_section('fanCurvePerf')

root = CTk()
root.geometry('800x800')
root.title('LegionController')
root.resizable(False, False)

root.bind("<Button-1>", lambda event: event.widget.focus_set())

#Vars
cwd=os.getcwd()
moduleDir = os.getcwd()[:-4]+'/Module'
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
    #axes.y = 500-(C*5)
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
    

def saveBtnPressed():
    global fanCurve
    global tempCurve
    global currentPowerMode
    global config

    root.after(100, lambda: saveBtn.configure(fg_color='#2333B4'))
    root.after(500, lambda: saveBtn.configure(fg_color='#1c94cf'))

    if currentPowerMode == 0:
        config['fanCurveBalanced']['fanCurve1'] = str(fanCurve[0])
        config['fanCurveBalanced']['fanCurve2'] = str(fanCurve[1])
        config['fanCurveBalanced']['fanCurve3'] = str(fanCurve[2])
        config['fanCurveBalanced']['fanCurve4'] = str(fanCurve[3])
        config['fanCurveBalanced']['fanCurve5'] = str(fanCurve[4]) 
        config['fanCurveBalanced']['fanCurve6'] = str(fanCurve[5])
        config['fanCurveBalanced']['tempCurve1'] = str(tempCurve[0])
        config['fanCurveBalanced']['tempCurve2'] = str(tempCurve[1])
        config['fanCurveBalanced']['tempCurve3'] = str(tempCurve[2])
        config['fanCurveBalanced']['tempCurve4'] = str(tempCurve[3])
        config['fanCurveBalanced']['tempCurve5'] = str(tempCurve[4])
        config['fanCurveBalanced']['tempCurve6'] = str(tempCurve[5])
    elif currentPowerMode == 1:
        config['fanCurvePerf']['fanCurve1'] = str(fanCurve[0])
        config['fanCurvePerf']['fanCurve2'] = str(fanCurve[1])
        config['fanCurvePerf']['fanCurve3'] = str(fanCurve[2])
        config['fanCurvePerf']['fanCurve4'] = str(fanCurve[3])
        config['fanCurvePerf']['fanCurve5'] = str(fanCurve[4]) 
        config['fanCurvePerf']['fanCurve6'] = str(fanCurve[5])
        config['fanCurvePerf']['tempCurve1'] = str(tempCurve[0])
        config['fanCurvePerf']['tempCurve2'] = str(tempCurve[1])
        config['fanCurvePerf']['tempCurve3'] = str(tempCurve[2])
        config['fanCurvePerf']['tempCurve4'] = str(tempCurve[3])
        config['fanCurvePerf']['tempCurve5'] = str(tempCurve[4])
        config['fanCurvePerf']['tempCurve6'] = str(tempCurve[5])
    elif currentPowerMode == 2:
        config['fanCurveQuiet']['fanCurve1'] = str(fanCurve[0])
        config['fanCurveQuiet']['fanCurve2'] = str(fanCurve[1])
        config['fanCurveQuiet']['fanCurve3'] = str(fanCurve[2])
        config['fanCurveQuiet']['fanCurve4'] = str(fanCurve[3])
        config['fanCurveQuiet']['fanCurve5'] = str(fanCurve[4]) 
        config['fanCurveQuiet']['fanCurve6'] = str(fanCurve[5])
        config['fanCurveQuiet']['tempCurve1'] = str(tempCurve[0])
        config['fanCurveQuiet']['tempCurve2'] = str(tempCurve[1])
        config['fanCurveQuiet']['tempCurve3'] = str(tempCurve[2])
        config['fanCurveQuiet']['tempCurve4'] = str(tempCurve[3])
        config['fanCurveQuiet']['tempCurve5'] = str(tempCurve[4])
        config['fanCurveQuiet']['tempCurve6'] = str(tempCurve[5])

    with open(cwd+r"/config.ini", 'w') as configfile:
        config.write(configfile)

    getFanCurve()

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

    if tempCurrent >= 0 and tempCurrent < tempCurve[1]:
        fanCurveCurrent = int(fanCurve[0]/100)
    elif tempCurrent >= tempCurve[1] and tempCurrent < tempCurve[2]:
        fanCurveCurrent = int(fanCurve[1]/100)
    elif tempCurrent >= tempCurve[2] and tempCurrent < tempCurve[3]:
        fanCurveCurrent = int(fanCurve[2]/100)
    elif tempCurrent >= tempCurve[3] and tempCurrent < tempCurve[4]:
        fanCurveCurrent = int(fanCurve[3]/100)
    elif tempCurrent >= tempCurve[4] and tempCurrent < tempCurve[5]:
        fanCurveCurrent = int(fanCurve[4]/100)
    elif tempCurrent >= tempCurve[5]:
        fanCurveCurrent = int(fanCurve[5]/100)

    f = open("/sys/module/LegionController/parameters/cFanCurve", "w")
    f.write(str(fanCurveCurrent))
    f.close()
    #print(fanCurve, ' ', tempCurve, ' ', fanCurveCurrent, ' ',tempCurrent)
    root.after(1000, updateFanCurve)

def updateCanvas():
    global graphX
    global graphY

    fanCurveCanvas.delete("all")
    ##adaaaa
    for i in arange(0, 700, 15.554):
        fanCurveCanvas.create_line([(i, 0), (i, 525)], tag='grid_line', fill='#000000', width=0.5)

    for i in arange(0, 525, 25):
        fanCurveCanvas.create_line([(0, i), (725, i)], tag='grid_line', fill='#000000', width=0.5)

    fanCurveCanvas.create_line(graphX[0],graphY[0],graphX[1],graphY[1], fill='#1c94cf', width=5, smooth=1)
    fanCurveCanvas.create_line(graphX[1],graphY[1],graphX[2],graphY[2], fill='#1c94cf', width=5, smooth=1)
    fanCurveCanvas.create_line(graphX[2],graphY[2],graphX[3],graphY[3], fill='#1c94cf', width=5, smooth=1)
    fanCurveCanvas.create_line(graphX[3],graphY[3],graphX[4],graphY[4], fill='#1c94cf', width=5, smooth=1)
    fanCurveCanvas.create_line(graphX[4],graphY[4],graphX[5],graphY[5], fill='#1c94cf', width=5, smooth=1)

    fanCurveCanvas.create_oval(graphX[0]-3,graphY[0]-3,graphX[0]+3,graphY[0]+3,fill="black", width=3)
    fanCurveCanvas.create_oval(graphX[1]-3,graphY[1]-3,graphX[1]+3,graphY[1]+3,fill="black", width=3)
    fanCurveCanvas.create_oval(graphX[2]-3,graphY[2]-3,graphX[2]+3,graphY[2]+3,fill="black", width=3)
    fanCurveCanvas.create_oval(graphX[3]-3,graphY[3]-3,graphX[3]+3,graphY[3]+3,fill="black", width=3)
    fanCurveCanvas.create_oval(graphX[4]-3,graphY[4]-3,graphX[4]+3,graphY[4]+3,fill="black", width=3)
    fanCurveCanvas.create_oval(graphX[5]-3,graphY[5]-3,graphX[5]+3,graphY[5]+3,fill="black", width=3)

def getCurrentPoint(event):
    global graphX
    global graphY
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
    #RPM = (axes.x/15.554)*100
    #C = (525-axes.y)/5
    global graphX
    global graphY
    global currentPoint

    x,y = root.winfo_pointerxy()
    widget = root.winfo_containing(x,y)

    if(str(widget) == ".!ctkframe.!ctkframe.!ctkcanvas2"):
        if currentPoint != -1:
            x = (15.554 * round(event.x / 15.554))
            y = (25 * round(event.y / 25))
            if (currentPoint == 0) or (x >= graphX[currentPoint-1] and y <= graphY[currentPoint-1]):
                if (currentPoint == 5) or (x <= graphX[currentPoint+1] and y >= graphY[currentPoint+1]):
                    if (currentPoint == 0) or ((x != graphX[currentPoint-1] and y != graphY[currentPoint-1]) or (x == graphX[currentPoint-1] and y != graphY[currentPoint-1]) or (x != graphX[currentPoint-1] and y == graphY[currentPoint-1])):
                        if (currentPoint == 5) or ((x != graphX[currentPoint+1] and y != graphY[currentPoint+1]) or (x == graphX[currentPoint+1] and y != graphY[currentPoint+1]) or (x != graphX[currentPoint+1] and y == graphY[currentPoint+1])):
                            graphX[currentPoint] = x
                            graphY[currentPoint] = y
                            fanCurve[currentPoint] = int(graphX[currentPoint] / 15.554 * 100)
                            tempCurve[currentPoint] = int((525 - graphY[currentPoint]) / 5)

            updateCanvas()


def insertModule():
    global moduleDir

    temp = 'sudo insmod ' + moduleDir + '/LegionController.ko'

    os.system(temp)


def exit():
    global moduleDir

    temp = 'sudo rmmod ' + moduleDir + '/LegionController.ko'

    os.system(temp)

#Images
#Window icon
img = Image.open(cwd+"/img/main.xbm") # .ico for windows, .xbm for linux
mainIcon = ImageTk.PhotoImage(img)
root.tk.call('wm', 'iconphoto', root._w, mainIcon)
#Performance Mode Icon
img = Image.open(cwd+"/img/perf.png") 
img.thumbnail((70,70), Image.ANTIALIAS)
perfIcon = ImageTk.PhotoImage(img)
#Balanced Mode Icon
img = Image.open(cwd+"/img/balanced.png") 
img.thumbnail((70,70), Image.ANTIALIAS)
balancedIcon = ImageTk.PhotoImage(img)
#Quiet Mode Icon
img = Image.open(cwd+"/img/quiet.png") 
img.thumbnail((70,70), Image.ANTIALIAS)
quietIcon = ImageTk.PhotoImage(img)
#Save Icon
img = Image.open(cwd+"/img/save.png") 
img.thumbnail((70,70), Image.ANTIALIAS)
saveIcon = ImageTk.PhotoImage(img)
#Settings Icon
img = Image.open(cwd+"/img/settings.png") 
img.thumbnail((70,70), Image.ANTIALIAS)
settingsIcon = ImageTk.PhotoImage(img)

insertModule()
loadConfig()

# Main Frames
page = CTkFrame(root)
page.place(height=700, relwidth=1)

modes = CTkFrame(root)
modes.place(y=700, height=100, relwidth=1)

#Page Frames

fanCurveGraph = CTkFrame(page)
fanCurveGraph.place(width=800, height=600)

currentDataFrame = CTkFrame(page)
currentDataFrame.place(y=600, height=100, relwidth=1)

# Fan Curve Graph

fanCurveCanvas = CTkCanvas(fanCurveGraph, bg='#b8b6b0')
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
perfBtn.place(x=150, width=80, height=80, y=5)

balancedBtn = CTkButton(modes, image=balancedIcon, text='', command=balancedBtnPressed)
balancedBtn.place(x=250, width=80, height=80, y=5)

quietBtn = CTkButton(modes, image=quietIcon, text='', command=quietBtnPressed)
quietBtn.place(x=350, width=80, height=80, y=5)

saveBtn = CTkButton(modes, image=saveIcon, text='', command=saveBtnPressed)
saveBtn.place(x=450, width=80, height=80, y=5)

settingsBtn = CTkButton(modes, image=settingsIcon, text='')
settingsBtn.place(x=550, width=80, height=80, y=5)

getCurrentPowerMode()
getCurrentData()
updateFanCurve()

root.bind("<ButtonPress-1>", getCurrentPoint)
root.bind("<ButtonRelease-1>", inputCanvas)

atexit.register(exit)

root.mainloop()