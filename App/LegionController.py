#!/usr/bin/python
from tkinter import *
from xmlrpc.client import boolean
from numpy import *
from customtkinter import *
from PIL import ImageTk, Image
import os, time, configparser, customtkinter
import atexit
#import pystray
#from pystray import MenuItem as item

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
configDir = '/etc/'
imgDir = sys._MEIPASS + '/img/'
moduleDir = sys._MEIPASS + '/Module/'
currentPowerMode = -1
previousPowerMode = -1
perfBtnPressedValue = False
balancedBtnPressedValue = False
quietBtnPressedValue = False
settingsBtnPressedvalue = False
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
useTemp = True
useTempVar = BooleanVar(None, useTemp)
currentPoint = -1
currentModeColor = ''
resetSelection = -1
setting = []

#Functions
def getCurrentPowerMode():
    global currentPowerMode
    global previousPowerMode
    global currentModeColor

    previousPowerMode=currentPowerMode
    f = open("/sys/kernel/LegionController/powerMode", "r")
    currentPowerMode = int(f.read()[:-1])
    f.close
    if previousPowerMode != currentPowerMode:
        if currentPowerMode == 0: 
            currentModeColor = '#7DC8E9'
            perfBtn.configure(fg_color='#1c94cf')
            balancedBtn.configure(fg_color=currentModeColor)
            quietBtn.configure(fg_color='#1c94cf')
        elif currentPowerMode == 1: 
            currentModeColor = '#F11515'
            perfBtn.configure(fg_color=currentModeColor)
            balancedBtn.configure(fg_color='#1c94cf')
            quietBtn.configure(fg_color='#1c94cf')
        elif currentPowerMode == 2: 
            currentModeColor = '#2333B4'
            perfBtn.configure(fg_color='#1c94cf')
            balancedBtn.configure(fg_color='#1c94cf')
            quietBtn.configure(fg_color=currentModeColor)
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
    global resetSelection

    configFileExist = os.path.exists(configDir+"/LegionController.ini")

    if (not configFileExist) or (resetSelection == 0):
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
    
    if (not configFileExist) or (resetSelection == 1):
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

    if (not configFileExist) or (resetSelection == 2):
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

    if (not configFileExist) or (resetSelection == 0) or (resetSelection == 1 ) or (resetSelection == 2):
        with open(configDir+r"/LegionController.ini", 'w') as configfile:
            config.write(configfile)
    else:
        config.read(configDir+'/LegionController.ini')
        fanCurveBalanced = config['fanCurveBalanced']
        fanCurvePerf = config['fanCurvePerf']
        fanCurveQuiet = config['fanCurveQuiet']

def getFanCurve():
    #axes.x = RPM/100*15.554
    #axes.y = 510-(C*5)
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
    graphY.append(510-(tempCurve[0]*5))
    graphY.append(510-(tempCurve[1]*5))
    graphY.append(510-(tempCurve[2]*5))
    graphY.append(510-(tempCurve[3]*5))
    graphY.append(510-(tempCurve[4]*5))
    graphY.append(510-(tempCurve[5]*5))
    

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

    with open(configDir+r"/LegionController.ini", 'w') as configfile:
        config.write(configfile)

    getFanCurve()

def updateFanCurve():
    global fanCurveCurrent
    global fanCurve
    global useTemp
    global tempCurrent
    global tempCurrentCPU
    global tempCurrentGPU

    useTemp = bool(useTempVar.get())

    if useTemp:
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
    root.after(2000, updateFanCurve)

def updateCanvas():
    global graphX
    global graphY
    global currentModeColor

    fanCurveCanvas.delete("all")
    #15.554
    #stipple="gray50"
    for i in arange(0, 710, 15.554):
        if int((i % 77.77)) == 0:
            fanCurveCanvas.create_line([(i, 0), (i, 510)], tag='grid_line', fill='white', width=0.5)
        else:
            fanCurveCanvas.create_line([(i, 500), (i, 510)], tag='grid_line', fill='white', width=0.5)
    #25
    for i in arange(10, 510, 25):
        if int(((i-10) % 50)) == 0:
            fanCurveCanvas.create_line([(0, i), (710, i)], tag='grid_line', fill='white', width=0.5)
        else:
            fanCurveCanvas.create_line([(0, i), (10, i)], tag='grid_line', fill='white', width=0.5)

    #1c94cf
    fanCurveCanvas.create_line(graphX[0],graphY[0],graphX[1],graphY[1], fill=currentModeColor, width=7, smooth=1)
    fanCurveCanvas.create_line(graphX[1],graphY[1],graphX[2],graphY[2], fill=currentModeColor, width=7, smooth=1)
    fanCurveCanvas.create_line(graphX[2],graphY[2],graphX[3],graphY[3], fill=currentModeColor, width=7, smooth=1)
    fanCurveCanvas.create_line(graphX[3],graphY[3],graphX[4],graphY[4], fill=currentModeColor, width=7, smooth=1)
    fanCurveCanvas.create_line(graphX[4],graphY[4],graphX[5],graphY[5], fill=currentModeColor, width=7, smooth=1)

    fanCurveCanvas.create_oval(graphX[1]-5,graphY[1]-5,graphX[1]+5,graphY[1]+5,fill="White", width=3)
    fanCurveCanvas.create_oval(graphX[0]-5,graphY[0]-5,graphX[0]+5,graphY[0]+5,fill="White", width=3)
    fanCurveCanvas.create_oval(graphX[2]-5,graphY[2]-5,graphX[2]+5,graphY[2]+5,fill="White", width=3)
    fanCurveCanvas.create_oval(graphX[3]-5,graphY[3]-5,graphX[3]+5,graphY[3]+5,fill="White", width=3)
    fanCurveCanvas.create_oval(graphX[4]-5,graphY[4]-5,graphX[4]+5,graphY[4]+5,fill="White", width=3)
    fanCurveCanvas.create_oval(graphX[5]-5,graphY[5]-5,graphX[5]+5,graphY[5]+5,fill="White", width=3)

def getCurrentPoint(event):
    global graphX
    global graphY
    global currentPoint

    currentPoint = -1

    x,y = root.winfo_pointerxy()
    widget = root.winfo_containing(x,y)
    #print(graphX)
    #print(graphY)
    if(str(widget) == ".!ctkframe.!ctkframe.!ctkcanvas2"):
        x = (15.554 * round(event.x / 15.554))
        y = (25 * round(event.y / 25))+10

        for i in range(0, 6):
            if x == graphX[i] and y == graphY[i]:
                currentPoint = i
        #print(x,' ',y)


def inputCanvas(event):
    #RPM = (axes.x/15.554)*100
    #C = ((510-axes.y)/5)+10
    global graphX
    global graphY
    global currentPoint

    maxGraphX = 699.9300000000001
    maxGraphY = 10
    x,y = root.winfo_pointerxy()
    widget = root.winfo_containing(x,y)

    if(str(widget) == ".!ctkframe.!ctkframe.!ctkcanvas2"):
        if currentPoint != -1:
            x = (15.554 * round(event.x / 15.554))
            y = (25 * round(event.y / 25))+10
            #print(x,' ',y)
            if (currentPoint == 0) or (x >= graphX[currentPoint-1] and y <= graphY[currentPoint-1]):
                if (currentPoint == 5) or (x <= graphX[currentPoint+1] and y >= graphY[currentPoint+1]):
                    if (currentPoint == 0) or ((x != graphX[currentPoint-1] and y != graphY[currentPoint-1]) or (x == graphX[currentPoint-1] and y != graphY[currentPoint-1]) or (x != graphX[currentPoint-1] and y == graphY[currentPoint-1])):
                        if (currentPoint == 5) or ((x != graphX[currentPoint+1] and y != graphY[currentPoint+1]) or (x == graphX[currentPoint+1] and y != graphY[currentPoint+1]) or (x != graphX[currentPoint+1] and y == graphY[currentPoint+1])):
                            if x <= maxGraphX and y >= maxGraphY:
                                graphX[currentPoint] = x
                                graphY[currentPoint] = y
                                fanCurve[currentPoint] = int(graphX[currentPoint] / 15.554 * 100)
                                tempCurve[currentPoint] = int((510 - graphY[currentPoint]) / 5)
                                #print(tempCurve[currentPoint],' ',fanCurve[currentPoint])

            updateCanvas()


def insertModule():
    global moduleDir

    temp = 'sudo insmod ' + moduleDir + '/LegionController.ko'

    os.system(temp)


def exit():
    global moduleDir

    temp = 'sudo rmmod ' + moduleDir + '/LegionController.ko'

    os.system(temp)

def settingsFrameShowHide():
    global settingsBtnPressedvalue

    if settingsBtnPressedvalue:
        settingsFrame.place_forget()
        settingsBtn.configure(fg_color='#1c94cf')
        settingsBtnPressedvalue = False
    else:
        settingsFrame.place(y=600, height=100, relwidth=1)
        settingsBtn.configure(fg_color='#2333B4')
        settingsBtnPressedvalue = True

def resetBtnPressed():
    global currentPowerMode
    global resetSelection

    if currentPowerMode == 0:
        resetSelection = 0
    elif currentPowerMode == 1:
        resetSelection = 1
    elif currentPowerMode == 2:
        resetSelection = 2

    loadConfig()

    resetSelection = -1

    getFanCurve()
    updateCanvas()


#Attempt to add tray icon support
#def quitWindow(icon, item):
#   icon.stop()
#   root.destroy()
#
#def showWindow(icon, item):
#   icon.stop()
#   root.after(0,root.deiconify())
#
#def hideWindow():
#   root.withdraw()
#   #image=Image.open("favicon.ico")
#   menu=(item('Quit', quitWindow), item('Show', showWindow))
#   icon=pystray.Icon("name", mainIcon, "My System Tray Icon", menu)
#   icon.run()

#Images
#Window icon
img = Image.open(imgDir+"/img/main.png") # .ico for windows, .xbm for linux
mainIcon = ImageTk.PhotoImage(img)
root.tk.call('wm', 'iconphoto', root._w, mainIcon)
#Performance Mode Icon
img = Image.open(imgDir+"/img/perf.png") 
img.thumbnail((70,70), Image.ANTIALIAS)
perfIcon = ImageTk.PhotoImage(img)
#Balanced Mode Icon
img = Image.open(imgDir+"/img/balanced.png") 
img.thumbnail((70,70), Image.ANTIALIAS)
balancedIcon = ImageTk.PhotoImage(img)
#Quiet Mode Icon
img = Image.open(imgDir+"/img/quiet.png") 
img.thumbnail((70,70), Image.ANTIALIAS)
quietIcon = ImageTk.PhotoImage(img)
#Save Icon
img = Image.open(imgDir+"/img/save.png") 
img.thumbnail((70,70), Image.ANTIALIAS)
saveIcon = ImageTk.PhotoImage(img)
#Settings Icon
img = Image.open(imgDir+"/img/settings.png") 
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
#b8b6b0
fanCurveCanvas = CTkCanvas(fanCurveGraph, bg='#383838')
fanCurveCanvas.place(y=40, x=50, width=710, height=510)


# 77.77 15.554  RPM = ((axes.x-25)/15.554)*100
# axes.x = RPM/100*15.554

fanCurveLabelRPM = CTkLabel(fanCurveGraph, text='Fan Speed (RPM)', text_font=("SF UI Display", 14), justify='center')
fanCurveLabelRPM.place(x=312.5, y=0, height=35, width=175)

fanCurveLabelRPM1 = CTkLabel(fanCurveGraph, text='0', text_font=("SF UI Display", 12), justify='center')
fanCurveLabelRPM1.place(x=25, y=550, height=50, width=60)

fanCurveLabelRPM2 = CTkLabel(fanCurveGraph, text='500', text_font=("SF UI Display", 12), justify='center')
fanCurveLabelRPM2.place(x=97.77, y=550, height=50, width=60)

fanCurveLabelRPM3 = CTkLabel(fanCurveGraph, text='1000', text_font=("SF UI Display", 12), justify='center')
fanCurveLabelRPM3.place(x=175.54, y=550, height=50, width=60)

fanCurveLabelRPM4 = CTkLabel(fanCurveGraph, text='1500', text_font=("SF UI Display", 12), justify='center')
fanCurveLabelRPM4.place(x=253.31, y=550, height=50, width=60)

fanCurveLabelRPM5 = CTkLabel(fanCurveGraph, text='2000', text_font=("SF UI Display", 12), justify='center')
fanCurveLabelRPM5.place(x=331.08, y=550, height=50, width=60)

fanCurveLabelRPM6 = CTkLabel(fanCurveGraph, text='2500', text_font=("SF UI Display", 12), justify='center')
fanCurveLabelRPM6.place(x=408.85, y=550, height=50, width=60)

fanCurveLabelRPM7 = CTkLabel(fanCurveGraph, text='3000', text_font=("SF UI Display", 12), justify='center')
fanCurveLabelRPM7.place(x=486.62, y=550, height=50, width=60)

fanCurveLabelRPM8 = CTkLabel(fanCurveGraph, text='3500', text_font=("SF UI Display", 12), justify='center')
fanCurveLabelRPM8.place(x=564.39, y=550, height=50, width=60)

fanCurveLabelRPM9 = CTkLabel(fanCurveGraph, text='4000', text_font=("SF UI Display", 12), justify='center')
fanCurveLabelRPM9.place(x=642.16, y=550, height=50, width=60)

fanCurveLabelRPM10 = CTkLabel(fanCurveGraph, text='4500', text_font=("SF UI Display", 12), justify='center')
fanCurveLabelRPM10.place(x=720, y=550, height=50, width=60)

# 50  5  C = (525-axes.y)/5
# axes.y = 525-(C*5)

fanCurveCanvasTemp = CTkCanvas(fanCurveGraph, bg='#383838', highlightthickness=0)
fanCurveCanvasTemp.create_text((4, 4), angle='270', anchor='sw', text='Temperature (°C)', fill="white", font=("SF UI Display", 14))
fanCurveCanvasTemp.place(x=765, y=220, height=160, width=35)

fanCurveLabelTemp1 = CTkLabel(fanCurveGraph, text='0', text_font=("SF UI Display", 12))
fanCurveLabelTemp1.place(y=535, height=30, width=50)

fanCurveLabelTemp2 = CTkLabel(fanCurveGraph, text='10', text_font=("SF UI Display", 12))
fanCurveLabelTemp2.place(y=475, height=50, width=50)

fanCurveLabelTemp3 = CTkLabel(fanCurveGraph, text='20', text_font=("SF UI Display", 12))
fanCurveLabelTemp3.place(y=425, height=50, width=50)

fanCurveLabelTemp4 = CTkLabel(fanCurveGraph, text='30', text_font=("SF UI Display", 12))
fanCurveLabelTemp4.place(y=375, height=50, width=50)

fanCurveLabelTemp5 = CTkLabel(fanCurveGraph, text='40', text_font=("SF UI Display", 12))
fanCurveLabelTemp5.place(y=325, height=50, width=50)

fanCurveLabelTemp6 = CTkLabel(fanCurveGraph, text='50', text_font=("SF UI Display", 12))
fanCurveLabelTemp6.place(y=275, height=50, width=50)

fanCurveLabelTemp7 = CTkLabel(fanCurveGraph, text='60', text_font=("SF UI Display", 12))
fanCurveLabelTemp7.place(y=225, height=50, width=50)

fanCurveLabelTemp8 = CTkLabel(fanCurveGraph, text='70', text_font=("SF UI Display", 12))
fanCurveLabelTemp8.place(y=175, height=50, width=50)

fanCurveLabelTemp8 = CTkLabel(fanCurveGraph, text='80', text_font=("SF UI Display", 12))
fanCurveLabelTemp8.place(y=125, height=50, width=50)

fanCurveLabelTemp9 = CTkLabel(fanCurveGraph, text='90', text_font=("SF UI Display", 12))
fanCurveLabelTemp9.place(y=75, height=50, width=50)

fanCurveLabelTemp10 = CTkLabel(fanCurveGraph, text='100', text_font=("SF UI Display", 12))
fanCurveLabelTemp10.place(y=25, height=50, width=50)


#Current Data Frame elements
currentDataFrameFanSpeed = CTkFrame(currentDataFrame)
currentDataFrameFanSpeed.place(height=100, width=400)

currentDataFrameTemp = CTkFrame(currentDataFrame)
currentDataFrameTemp.place(height=100, width=400, x=400)


#Current Data Fan Speed
currentDataFrameFanSpeedText = CTkLabel(currentDataFrameFanSpeed, text='Current Fan Speed', text_font=("SF UI Display", 15), justify='center')
currentDataFrameFanSpeedText.place(y=2.5, height=30, relwidth=1)

fanSpeedCurrentLabel = CTkLabel(currentDataFrameFanSpeed, text_font=("SF UI Display", 17), justify='center', fg_color='#b8b6b0', text_color='black')
fanSpeedCurrentLabel.place(x=120, y=40, height=40, width=160)


#Current Data Temps
currentDataFrameTempText = CTkLabel(currentDataFrameTemp, text='Current Temps', text_font=("SF UI Display", 15), justify='center')
currentDataFrameTempText.place(y=2.5, height=30, relwidth=1)

currentDataFrameTempCPUText = CTkLabel(currentDataFrameTemp, text='CPU', text_font=("SF UI Display", 15), justify='center')
currentDataFrameTempCPUText.place(x=102.6, y=35, height=20, width=75)

currentDataFrameTempGPUText = CTkLabel(currentDataFrameTemp, text='GPU', text_font=("SF UI Display", 15), justify='center')
currentDataFrameTempGPUText.place(x=222.5, y=35, height=20, width=75)

tempCurrentCPULabel = CTkLabel(currentDataFrameTemp, text_font=("SF UI Display", 15), justify='center', fg_color='#b8b6b0', text_color='black')
tempCurrentCPULabel.place(x=102.5, y=65, height=25, width=75)

tempCurrentGPULabel = CTkLabel(currentDataFrameTemp, text_font=("SF UI Display", 15), justify='center', fg_color='#b8b6b0', text_color='black')
tempCurrentGPULabel.place(x=222.5, y=65, height=25, width=75)


# Buttons
perfBtn = CTkButton(modes, image=perfIcon, text='', command=perfBtnPressed)
perfBtn.place(x=60, width=80, height=80, y=10)

balancedBtn = CTkButton(modes, image=balancedIcon, text='', command=balancedBtnPressed)
balancedBtn.place(x=160, width=80, height=80, y=10)

quietBtn = CTkButton(modes, image=quietIcon, text='', command=quietBtnPressed)
quietBtn.place(x=260, width=80, height=80, y=10)

saveBtn = CTkButton(modes, image=saveIcon, text='', command=saveBtnPressed, fg_color='#1c94cf')
saveBtn.place(x=460, width=80, height=80, y=10)

resetBtn = CTkButton(modes, text='Reset\nCurve', command=resetBtnPressed, fg_color='#1c94cf', text_font=("SF UI Display", 17), text_color='black')
resetBtn.place(x=560, width=80, height=80, y=10)

settingsBtn = CTkButton(modes, image=settingsIcon, text='', command=settingsFrameShowHide, fg_color='#1c94cf')
settingsBtn.place(x=660, width=80, height=80, y=10)


settingsFrame = CTkFrame(page)

useTempFrame = CTkFrame(settingsFrame)
useTempFrame.place(width=400, height=50)

useTempLabel = CTkLabel(useTempFrame, text='Used Temperature', text_font=("SF UI Display", 12), justify='center')
useTempLabel.place(x=20, y=15,width=180, height=20)

useTempCPURB = CTkRadioButton(useTempFrame, text="CPU", variable=useTempVar, value=True)
useTempCPURB.place(x=220, y=15)

useTempGPURB = CTkRadioButton(useTempFrame, text="GPU", variable=useTempVar, value=False)
useTempGPURB.place(x=300, y=15)


getCurrentPowerMode()
getCurrentData()
updateFanCurve()

root.bind("<ButtonPress-1>", getCurrentPoint)
root.bind("<ButtonRelease-1>", inputCanvas)

#root.protocol('WM_DELETE_WINDOW', hideWindow)

atexit.register(exit)

root.mainloop()