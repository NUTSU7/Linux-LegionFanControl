#!/usr/bin/python
from tkinter import *
from numpy import *
from turtle import window_width
from unittest import TextTestResult
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
root.bind_all("<Button-1>", lambda event: event.widget.focus_set())

#Vars
cwd=os.getcwd()
currentPowerMode = -1
previousPowerMode = -1
perfBtnPressedValue = False
balancedBtnPressedValue = False
quietBtnPressedValue = False
fanSpeedCurrent = -1
tempCurrentCPU = -1
tempCurrentGPU = -1
fanCurve = []
tempCurveCPU = []
tempCurveGPU = []
fanCurveCurrent = -1
fanCurveQuiet = []
fanCurveBalanced = []
fanCurvePerf = []
graphRPM = []
graphTemp = []

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

        with open(cwd+r"/config.ini", 'w') as configfile:
            config.write(configfile)
    else:
        config.read(cwd+'/config.ini')
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
        
    

def updateEntryes():
    global fanCurve
    global tempCurveCPU
    global tempCurrentGPU

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

    tempCurveGPUEntry1.insert(0, tempCurveGPU[0])
    tempCurveGPUEntry2.insert(0, tempCurveGPU[1])
    tempCurveGPUEntry3.insert(0, tempCurveGPU[2])
    tempCurveGPUEntry4.insert(0, tempCurveGPU[3])
    tempCurveGPUEntry5.insert(0, tempCurveGPU[4])
    tempCurveGPUEntry6.insert(0, tempCurveGPU[5])

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

    with open(cwd+r"/config.ini", 'w') as configfile:
        config.write(configfile)

    getFanCurve()
    updateEntryes()

def updateFanCurve():
    global fanCurveCurrent
    global fanCurve
    global tempCurrentCPU
    global tempCurveGPU

    if tempCurrentCPU >= tempCurrentGPU:
        if tempCurrentCPU >= tempCurveCPU[0] and tempCurrentCPU < tempCurveCPU[1]:
            fanCurveCurrent = fanCurve[0]/100
        elif tempCurrentCPU >= tempCurveCPU[1] and tempCurrentCPU < tempCurveCPU[2]:
            fanCurveCurrent = fanCurve[1]/100
        elif tempCurrentCPU >= tempCurveCPU[2] and tempCurrentCPU < tempCurveCPU[3]:
            fanCurveCurrent = fanCurve[2]/100
        elif tempCurrentCPU >= tempCurveCPU[3] and tempCurrentCPU < tempCurveCPU[4]:
            fanCurveCurrent = fanCurve[3]/100
        elif tempCurrentCPU >= tempCurveCPU[4] and tempCurrentCPU < tempCurveCPU[5]:
            fanCurveCurrent = fanCurve[4]/100
        elif tempCurrentCPU >= tempCurveCPU[5]:
            fanCurveCurrent = fanCurve[5]/100
    else:
        if tempCurrentGPU >= tempCurveGPU[0] and tempCurrentGPU < tempCurveGPU[1]:
            fanCurveCurrent = fanCurve[0]/100
        elif tempCurrentGPU >= tempCurveGPU[1] and tempCurrentGPU < tempCurveGPU[2]:
            fanCurveCurrent = fanCurve[1]/100
        elif tempCurrentGPU >= tempCurveGPU[2] and tempCurrentGPU < tempCurveGPU[3]:
            fanCurveCurrent = fanCurve[2]/100
        elif tempCurrentGPU >= tempCurveGPU[3] and tempCurrentGPU < tempCurveGPU[4]:
            fanCurveCurrent = fanCurve[3]/100
        elif tempCurrentGPU >= tempCurveGPU[4] and tempCurrentGPU < tempCurveGPU[5]:
            fanCurveCurrent = fanCurve[4]/100
        elif tempCurrentGPU >= tempCurveGPU[5]:
            fanCurveCurrent = fanCurve[5]/100

    f = open("/sys/module/LegionController/parameters/cFanCurve", "w")
    f.write(str(fanCurveCurrent)[:-2])
    f.close()
    
    root.after(1000, updateFanCurve)

def updateCanvas():
    #axes.x = RPM/100*15.554
    #axes.y = 500-(C*5+25)
    global graphRPM
    global graphTemp
    graphRPM = []
    graphTemp = []

    fanCurveCanvas.delete("all")

    graphRPM.append(fanCurve[0]/100*15.554)
    graphRPM.append(fanCurve[1]/100*15.554)
    graphRPM.append(fanCurve[2]/100*15.554)
    graphRPM.append(fanCurve[3]/100*15.554)
    graphRPM.append(fanCurve[4]/100*15.554)
    graphRPM.append(fanCurve[5]/100*15.554)
    graphTemp.append(500-(tempCurveCPU[0]*5+25))
    graphTemp.append(500-(tempCurveCPU[1]*5+25))
    graphTemp.append(500-(tempCurveCPU[2]*5+25))
    graphTemp.append(500-(tempCurveCPU[3]*5+25))
    graphTemp.append(500-(tempCurveCPU[4]*5+25))
    graphTemp.append(500-(tempCurveCPU[5]*5+25))

    for i in arange(0, 700, 15.554):
        fanCurveCanvas.create_line([(i, 0), (i, 475)], tag='grid_line', fill='#adaaaa', width=0.5)

    for i in arange(0, 475, 25):
        fanCurveCanvas.create_line([(0, i), (725, i)], tag='grid_line', fill='#adaaaa', width=0.5)

    fanCurveCanvas.create_line(0,475,graphRPM[0],graphTemp[0], fill='green', width=5)
    fanCurveCanvas.create_line(graphRPM[0],graphTemp[0],graphRPM[1],graphTemp[1], fill='green', width=5)
    fanCurveCanvas.create_line(graphRPM[1],graphTemp[1],graphRPM[2],graphTemp[2], fill='green', width=5)
    fanCurveCanvas.create_line(graphRPM[2],graphTemp[2],graphRPM[3],graphTemp[3], fill='green', width=5)
    fanCurveCanvas.create_line(graphRPM[3],graphTemp[3],graphRPM[4],graphTemp[4], fill='green', width=5)
    fanCurveCanvas.create_line(graphRPM[4],graphTemp[4],graphRPM[5],graphTemp[5], fill='green', width=5)

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
fanCurveGraph.place(width=800, height=550)

fanCurveFrame = CTkFrame(page)
fanCurveFrame.place(relwidth=1, height=150, y=550)

currentDataFrame = CTkFrame(page)
currentDataFrame.place(y=700, height=100, relwidth=1)

# Fan Curve Graph

fanCurveCanvas = CTkCanvas(fanCurveGraph)
fanCurveCanvas.place(y=25, x=50, width=725, height=475)


# 77.77 15.554  RPM = ((axes.x-25)/15.554)*100
# axes.x = RPM/100*15.554

fanCurveLabelRPM1 = CTkLabel(fanCurveGraph, text='0', text_font=("Arial", 12))
fanCurveLabelRPM1.place(x=25, y=500, height=50, width=50)

fanCurveLabelRPM2 = CTkLabel(fanCurveGraph, text='500', text_font=("Arial", 12))
fanCurveLabelRPM2.place(x=102.77, y=500, height=50, width=50)

fanCurveLabelRPM3 = CTkLabel(fanCurveGraph, text='1000', text_font=("Arial", 12))
fanCurveLabelRPM3.place(x=180.54, y=500, height=50, width=50)

fanCurveLabelRPM4 = CTkLabel(fanCurveGraph, text='1500', text_font=("Arial", 12))
fanCurveLabelRPM4.place(x=258.31, y=500, height=50, width=50)

fanCurveLabelRPM5 = CTkLabel(fanCurveGraph, text='2000', text_font=("Arial", 12))
fanCurveLabelRPM5.place(x=336.08, y=500, height=50, width=50)

fanCurveLabelRPM6 = CTkLabel(fanCurveGraph, text='2500', text_font=("Arial", 12))
fanCurveLabelRPM6.place(x=413.85, y=500, height=50, width=50)

fanCurveLabelRPM7 = CTkLabel(fanCurveGraph, text='3000', text_font=("Arial", 12))
fanCurveLabelRPM7.place(x=491.62, y=500, height=50, width=50)

fanCurveLabelRPM8 = CTkLabel(fanCurveGraph, text='3500', text_font=("Arial", 12))
fanCurveLabelRPM8.place(x=569.39, y=500, height=50, width=50)

fanCurveLabelRPM9 = CTkLabel(fanCurveGraph, text='4000', text_font=("Arial", 12))
fanCurveLabelRPM9.place(x=647.16, y=500, height=50, width=50)

fanCurveLabelRPM10 = CTkLabel(fanCurveGraph, text='4500', text_font=("Arial", 12))
fanCurveLabelRPM10.place(x=725, y=500, height=50, width=50)

# 50  5  C = (500-axes.y-25)/5
# axes.y = 500-(C*5+25)

fanCurveLabelTemp1 = CTkLabel(fanCurveGraph, text='0', text_font=("Arial", 12))
fanCurveLabelTemp1.place(y=485, height=30, width=50)

fanCurveLabelTemp2 = CTkLabel(fanCurveGraph, text='10', text_font=("Arial", 12))
fanCurveLabelTemp2.place(y=425, height=50, width=50)

fanCurveLabelTemp3 = CTkLabel(fanCurveGraph, text='20', text_font=("Arial", 12))
fanCurveLabelTemp3.place(y=375, height=50, width=50)

fanCurveLabelTemp4 = CTkLabel(fanCurveGraph, text='30', text_font=("Arial", 12))
fanCurveLabelTemp4.place(y=325, height=50, width=50)

fanCurveLabelTemp5 = CTkLabel(fanCurveGraph, text='40', text_font=("Arial", 12))
fanCurveLabelTemp5.place(y=275, height=50, width=50)

fanCurveLabelTemp6 = CTkLabel(fanCurveGraph, text='50', text_font=("Arial", 12))
fanCurveLabelTemp6.place(y=225, height=50, width=50)

fanCurveLabelTemp7 = CTkLabel(fanCurveGraph, text='60', text_font=("Arial", 12))
fanCurveLabelTemp7.place(y=175, height=50, width=50)

fanCurveLabelTemp8 = CTkLabel(fanCurveGraph, text='80', text_font=("Arial", 12))
fanCurveLabelTemp8.place(y=125, height=50, width=50)

fanCurveLabelTemp9 = CTkLabel(fanCurveGraph, text='90', text_font=("Arial", 12))
fanCurveLabelTemp9.place(y=75, height=50, width=50)

fanCurveLabelTemp10 = CTkLabel(fanCurveGraph, text='100', text_font=("Arial", 12))
fanCurveLabelTemp10.place(y=25, height=50, width=50)


# Fan Curve Input Left Frame elements
fanCurveText = CTkLabel(fanCurveFrame, text='Fan Speed (RPM)', text_font=("Arial", 15))
fanCurveText.place(x=5, y=15, height=30, width=175)

tempCurveCPUText = CTkLabel(fanCurveFrame, text='CPU Temp (°C)', text_font=("Arial", 15))
tempCurveCPUText.place(x=5, y=55, height=30, width=175)

tempCurveGPUText = CTkLabel(fanCurveFrame, text='GPU Temp (°C)', text_font=("Arial", 15))
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

root.mainloop()