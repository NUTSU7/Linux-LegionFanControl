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

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

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
functionCalled = False

#Functions
def getCurrentPowerMode():
    global currentPowerMode
    global previousPowerMode
    global curveLen

    previousPowerMode=currentPowerMode
    f = open("/sys/kernel/LegionController/powerMode", "r")
    currentPowerMode = int(f.read()[:-1])
    f.close
    if int(tempCurrentCPU) < 40: curveLen=3
    elif currentPowerMode == 0: curveLen=8
    elif currentPowerMode == 1: curveLen=9
    elif currentPowerMode == 2: curveLen=7
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
    root.after(2000, getCurrentPowerMode)

def perfBtnPressed():
    global perfBtnPressedValue
    global curveLen
    perfBtnPressedValue = True
    powerModeBtnPressed()

def balancedBtnPressed():
    global balancedBtnPressedValue
    global curveLen
    balancedBtnPressedValue = True
    powerModeBtnPressed()

def quietBtnPressed():
    global quietBtnPressedValue
    global curveLen
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
    getCurrentFanCurve()

def getCurrentData():
    global fanSpeedCurrentLeft
    global fanSpeedCurrentRight
    global tempCurrentCPU
    global tempCurrentGPU
    global curveLen
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
    if int(tempCurrentCPU) < 40: curveLen=3
    f = open("/sys/kernel/LegionController/tempCurrentGPU", "r")
    tempCurrentGPU = int(f.read()[:-1])
    f.close()
    tempCurrentGPULabel['text']=str(tempCurrentGPU)+' °C'
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
    initEntryes()

def initEntryes():
    global fanCurveLeft
    global fanCurveRight
    global tempCurveCPU
    global tempCurveGPU
    global curveLen
    
    fanCurveLeftInputEntry1.delete(0, END)
    fanCurveLeftInputEntry2.delete(0, END)
    fanCurveLeftInputEntry3.delete(0, END)
    fanCurveLeftInputEntry4.delete(0, END)
    fanCurveLeftInputEntry5.delete(0, END)
    fanCurveLeftInputEntry6.delete(0, END)
    fanCurveLeftInputEntry7.delete(0, END)
    fanCurveLeftInputEntry8.delete(0, END)
    fanCurveLeftInputEntry9.delete(0, END)

    tempCurveCPUInputEntry1.delete(0, END)
    tempCurveCPUInputEntry2.delete(0, END)
    tempCurveCPUInputEntry3.delete(0, END)
    tempCurveCPUInputEntry4.delete(0, END)
    tempCurveCPUInputEntry5.delete(0, END)
    tempCurveCPUInputEntry6.delete(0, END)
    tempCurveCPUInputEntry7.delete(0, END)
    tempCurveCPUInputEntry8.delete(0, END)
    tempCurveCPUInputEntry9.delete(0, END)

    fanCurveRightInputEntry1.delete(0, END)
    fanCurveRightInputEntry2.delete(0, END)
    fanCurveRightInputEntry3.delete(0, END)
    fanCurveRightInputEntry4.delete(0, END)
    fanCurveRightInputEntry5.delete(0, END)
    fanCurveRightInputEntry6.delete(0, END)
    fanCurveRightInputEntry7.delete(0, END)
    fanCurveRightInputEntry8.delete(0, END)
    fanCurveRightInputEntry9.delete(0, END)

    tempCurveGPUInputEntry1.delete(0, END)
    tempCurveGPUInputEntry2.delete(0, END)
    tempCurveGPUInputEntry3.delete(0, END)
    tempCurveGPUInputEntry4.delete(0, END)
    tempCurveGPUInputEntry5.delete(0, END)
    tempCurveGPUInputEntry6.delete(0, END)
    tempCurveGPUInputEntry7.delete(0, END)
    tempCurveGPUInputEntry8.delete(0, END)
    tempCurveGPUInputEntry9.delete(0, END)

    fanCurveLeftInputEntry1.insert(0, int(fanCurveLeft[0])*100)
    fanCurveLeftInputEntry2.insert(0, int(fanCurveLeft[1])*100)
    fanCurveLeftInputEntry3.insert(0, int(fanCurveLeft[2])*100)
    fanCurveLeftInputEntry4.insert(0, int(fanCurveLeft[3])*100)
    fanCurveLeftInputEntry5.insert(0, int(fanCurveLeft[4])*100)
    fanCurveLeftInputEntry6.insert(0, int(fanCurveLeft[5])*100)
    fanCurveLeftInputEntry7.insert(0, int(fanCurveLeft[6])*100)
    fanCurveLeftInputEntry8.insert(0, int(fanCurveLeft[7])*100)
    fanCurveLeftInputEntry9.insert(0, int(fanCurveLeft[8])*100)

    tempCurveCPUInputEntry1.insert(0, int(tempCurveCPU[0]))
    tempCurveCPUInputEntry2.insert(0, int(tempCurveCPU[1]))
    tempCurveCPUInputEntry3.insert(0, int(tempCurveCPU[2]))
    tempCurveCPUInputEntry4.insert(0, int(tempCurveCPU[3]))
    tempCurveCPUInputEntry5.insert(0, int(tempCurveCPU[4]))
    tempCurveCPUInputEntry6.insert(0, int(tempCurveCPU[5]))
    tempCurveCPUInputEntry7.insert(0, int(tempCurveCPU[6]))
    tempCurveCPUInputEntry8.insert(0, int(tempCurveCPU[7]))
    tempCurveCPUInputEntry9.insert(0, int(tempCurveCPU[8]))

    fanCurveRightInputEntry1.insert(0, int(fanCurveRight[0])*100)
    fanCurveRightInputEntry2.insert(0, int(fanCurveRight[1])*100)
    fanCurveRightInputEntry3.insert(0, int(fanCurveRight[2])*100)
    fanCurveRightInputEntry4.insert(0, int(fanCurveRight[3])*100)
    fanCurveRightInputEntry5.insert(0, int(fanCurveRight[4])*100)
    fanCurveRightInputEntry6.insert(0, int(fanCurveRight[5])*100)
    fanCurveRightInputEntry7.insert(0, int(fanCurveRight[6])*100)
    fanCurveRightInputEntry8.insert(0, int(fanCurveRight[7])*100)
    fanCurveRightInputEntry9.insert(0, int(fanCurveRight[8])*100)

    tempCurveGPUInputEntry1.insert(0, int(tempCurveGPU[0]))
    tempCurveGPUInputEntry2.insert(0, int(tempCurveGPU[1]))
    tempCurveGPUInputEntry3.insert(0, int(tempCurveGPU[2]))
    tempCurveGPUInputEntry4.insert(0, int(tempCurveGPU[3]))
    tempCurveGPUInputEntry5.insert(0, int(tempCurveGPU[4]))
    tempCurveGPUInputEntry6.insert(0, int(tempCurveGPU[5]))
    tempCurveGPUInputEntry7.insert(0, int(tempCurveGPU[6]))
    tempCurveGPUInputEntry8.insert(0, int(tempCurveGPU[7]))
    tempCurveGPUInputEntry9.insert(0, int(tempCurveGPU[8]))

def saveBtnPressed():
    global saveBtnPressedValue
    saveBtnPressedValue = True
    changeFanCurve()
    root.after(100, lambda: saveBtn.configure(bg='#2333B4'))
    root.after(400, lambda: saveBtn.configure(bg='#1c94cf'))

def changeFanCurve():
    global curveLen

    fanCurveLeft[0] = fanCurveLeftInputEntry1.get()[:-2]
    fanCurveLeft[1] = fanCurveLeftInputEntry2.get()[:-2]
    fanCurveLeft[2] = fanCurveLeftInputEntry3.get()[:-2]
    fanCurveLeft[3] = fanCurveLeftInputEntry4.get()[:-2]
    fanCurveLeft[4] = fanCurveLeftInputEntry5.get()[:-2]
    fanCurveLeft[5] = fanCurveLeftInputEntry6.get()[:-2]
    fanCurveLeft[6] = fanCurveLeftInputEntry7.get()[:-2]

    if curveLen >= 8:
        fanCurveLeft[7] = fanCurveLeftInputEntry8.get()[:-2]
    else:
        fanCurveLeft[7] = -1

    if curveLen >= 9:
        fanCurveLeft[8] = fanCurveLeftInputEntry9.get()[:-2]
    else:
        fanCurveLeft[8] = -1

    fanCurveRight[0] = fanCurveRightInputEntry1.get()[:-2]
    fanCurveRight[1] = fanCurveRightInputEntry2.get()[:-2]
    fanCurveRight[2] = fanCurveRightInputEntry3.get()[:-2]
    fanCurveRight[3] = fanCurveRightInputEntry4.get()[:-2]
    fanCurveRight[4] = fanCurveRightInputEntry5.get()[:-2]
    fanCurveRight[5] = fanCurveRightInputEntry6.get()[:-2]
    fanCurveRight[6] = fanCurveRightInputEntry7.get()[:-2]

    if curveLen >= 8:
        fanCurveRight[7] = fanCurveRightInputEntry8.get()[:-2]
    else:
        fanCurveRight[7] = -1

    if curveLen >= 9:
        fanCurveRight[8] = fanCurveRightInputEntry9.get()[:-2]
    else:
        fanCurveRight[8] = -1

    tempCurveCPU[1] = tempCurveCPUInputEntry2.get()
    tempCurveCPU[0] = tempCurveCPUInputEntry1.get()
    tempCurveCPU[2] = tempCurveCPUInputEntry3.get()
    tempCurveCPU[3] = tempCurveCPUInputEntry4.get()
    tempCurveCPU[4] = tempCurveCPUInputEntry5.get()
    tempCurveCPU[5] = tempCurveCPUInputEntry6.get()
    tempCurveCPU[6] = tempCurveCPUInputEntry7.get()

    if curveLen >= 8:
        tempCurveCPU[7] = tempCurveCPUInputEntry8.get()
    else:
        tempCurveCPU[7] = -1

    if curveLen >= 9:
        tempCurveCPU[8] = tempCurveCPUInputEntry9.get()
    else:
        tempCurveCPU[8] = -1

    tempCurveGPU[0] = tempCurveGPUInputEntry1.get()
    tempCurveGPU[1] = tempCurveGPUInputEntry2.get()
    tempCurveGPU[2] = tempCurveGPUInputEntry3.get()
    tempCurveGPU[3] = tempCurveGPUInputEntry4.get()
    tempCurveGPU[4] = tempCurveGPUInputEntry5.get()
    tempCurveGPU[5] = tempCurveGPUInputEntry6.get()
    tempCurveGPU[6] = tempCurveGPUInputEntry7.get()

    if curveLen >= 8:
        tempCurveGPU[7] = tempCurveGPUInputEntry8.get()
    else:
        tempCurveGPU[7] = -1
    
    if curveLen >= 9:
        tempCurveGPU[8] = tempCurveGPUInputEntry9.get()
    else:
        tempCurveGPU[8] = -1

    f = open("/sys/module/LegionController/parameters/cFanCurveLeft", "w")
    f.write(str(fanCurveLeft[0])+','+str(fanCurveLeft[1])+','+str(fanCurveLeft[2])+','+str(fanCurveLeft[3])+','+str(fanCurveLeft[4])+','+str(fanCurveLeft[5])+','+str(fanCurveLeft[6])+','+str(fanCurveLeft[7])+','+str(fanCurveLeft[8]))
    f.close()

    f = open("/sys/module/LegionController/parameters/cFanCurveRight", "w")
    f.write(str(fanCurveRight[0])+','+str(fanCurveRight[1])+','+str(fanCurveRight[2])+','+str(fanCurveRight[3])+','+str(fanCurveRight[4])+','+str(fanCurveRight[5])+','+str(fanCurveRight[6])+','+str(fanCurveRight[7])+','+str(fanCurveRight[8]))
    f.close()

    f = open("/sys/module/LegionController/parameters/cTempCurveCPU", "w")
    f.write(str(tempCurveCPU[0])+','+str(tempCurveCPU[1])+','+str(tempCurveCPU[2])+','+str(tempCurveCPU[3])+','+str(tempCurveCPU[4])+','+str(tempCurveCPU[5])+','+str(tempCurveCPU[6])+','+str(tempCurveCPU[7])+','+str(tempCurveCPU[8]))
    f.close()

    f = open("/sys/module/LegionController/parameters/cTempCurveGPU", "w")
    f.write(str(tempCurveGPU[0])+','+str(tempCurveGPU[1])+','+str(tempCurveGPU[2])+','+str(tempCurveGPU[3])+','+str(tempCurveGPU[4])+','+str(tempCurveGPU[5])+','+str(tempCurveGPU[6])+','+str(tempCurveGPU[7])+','+str(tempCurveGPU[8]))
    f.close()

#Images
#Window icon
img = Image.open(cwd+"/img/main.xbm") # .ico for windows, .xbm for linux
mainIcon = ImageTk.PhotoImage(img)
root.tk.call('wm', 'iconphoto', root._w, mainIcon)
#Performance Mode Icon
img = Image.open(cwd+"/img/perf.png") 
img.thumbnail((90,90), Image.ANTIALIAS)
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
page = CTkFrame(root, bg='#000000')
page.place(height=600, width=698, x=1, y=1)

modes = CTkFrame(root, bg='#000000')
modes.place(y=602, height=97, width=698, x=1)

#Attemp for a graph
#fanCurveFig = Figure(figsize=(2,2), dpi=100)
#fanCurvePlot = fanCurveFig.add_subplot(122)
#fanCurvePlot.plot(fanCurveLeft,tempCurveCPU, color='blue')
#fanCurvePlot.plot(fanCurveRight,tempCurveGPU, color='green')
#fanCurvePlot.axes.xaxis.set_visible(False)
#fanCurvePlot.axes.yaxis.set_visible(False)

#Page Frames
fanCurveFrame = CTkFrame(page, bg='white')
fanCurveFrame.place(relwidth=1,height=500)

currentDataFrame = CTkFrame(page, bg='white')
currentDataFrame.place(y=500, height=99, relwidth=1)


#Fan Curve Frame
fanCurveGraphFrame = CTkFrame(fanCurveFrame, bg='#000000')
fanCurveGraphFrame.place(height=299, relwidth=1)

fanCurveInputFrame = CTkFrame(fanCurveFrame, bg='white')
fanCurveInputFrame.place(y=300, height=199, relwidth=1)

#Attemp for a graph
#fanCurveCanvas = FigureCanvasTkAgg(fanCurveFig, fanCurveFigFrame)
#fanCurveCanvas.draw()
#fanCurveCanvas.get_tk_widget().place(relwidth=1, relheight=1)


#Fan Curve Input Frame elements
fanCurveLeftInputFrame = CTkFrame(fanCurveInputFrame, bg='#000000')
fanCurveLeftInputFrame.place(height=99, relwidth=1)

fanCurveRightInputFrame = CTkFrame(fanCurveInputFrame, bg='#000000')
fanCurveRightInputFrame.place(y=100, height=99, relwidth=1)


# Fan Curve Input Left Frame elements
fanCurveLeftInputText = CTkLabel(fanCurveLeftInputFrame, text='Left Fan (RPM)', text_font=("Arial", 12), fg='white', bg='#000000')
fanCurveLeftInputText.place(x=5, y=15, height=30, width=175)

tempCurveCPUInputText = CTkLabel(fanCurveLeftInputFrame, text='CPU Temp (°C)', text_font=("Arial", 12), fg='white', bg='#000000')
tempCurveCPUInputText.place(x=5, y=55, height=30, width=175)

fanCurveLeftInputEntry1 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveLeftInputEntry1.place(x=175, y=15, height=30, width=50)

fanCurveLeftInputEntry2 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveLeftInputEntry2.place(x=233, y=15, height=30, width=50)

fanCurveLeftInputEntry3 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveLeftInputEntry3.place(x=291, y=15, height=30, width=50)

fanCurveLeftInputEntry4 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveLeftInputEntry4.place(x=349, y=15, height=30, width=50)

fanCurveLeftInputEntry5 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveLeftInputEntry5.place(x=407, y=15, height=30, width=50)

fanCurveLeftInputEntry6 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveLeftInputEntry6.place(x=465, y=15, height=30, width=50)

fanCurveLeftInputEntry7 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveLeftInputEntry7.place(x=523, y=15, height=30, width=50)

fanCurveLeftInputEntry8 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveLeftInputEntry8.place(x=581, y=15, height=30, width=50)

fanCurveLeftInputEntry9 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveLeftInputEntry9.place(x=639, y=15, height=30, width=50)

tempCurveCPUInputEntry1 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveCPUInputEntry1.place(x=175, y=55, height=30, width=50)

tempCurveCPUInputEntry2 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveCPUInputEntry2.place(x=233, y=55, height=30, width=50)

tempCurveCPUInputEntry3 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveCPUInputEntry3.place(x=291, y=55, height=30, width=50)

tempCurveCPUInputEntry4 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveCPUInputEntry4.place(x=349, y=55, height=30, width=50)

tempCurveCPUInputEntry5 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveCPUInputEntry5.place(x=407, y=55, height=30, width=50)

tempCurveCPUInputEntry6 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveCPUInputEntry6.place(x=465, y=55, height=30, width=50)

tempCurveCPUInputEntry7 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveCPUInputEntry7.place(x=523, y=55, height=30, width=50)

tempCurveCPUInputEntry8 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveCPUInputEntry8.place(x=581, y=55, height=30, width=50)

tempCurveCPUInputEntry9 = CTkEntry(fanCurveLeftInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveCPUInputEntry9.place(x=639, y=55, height=30, width=50)


# Fan Curve Input Right Frame elements
fanCurveRightInputText = CTkLabel(fanCurveRightInputFrame, text='Right Fan (RPM)', text_font=("Arial", 12), fg='white', bg='#000000')
fanCurveRightInputText.place(x=2, y=15, height=30, width=175)

tempCurveCPUInputText = CTkLabel(fanCurveRightInputFrame, text='GPU Temp (°C)', text_font=("Arial", 12), fg='white', bg='#000000')
tempCurveCPUInputText.place(x=2, y=55, height=30, width=175)

fanCurveRightInputEntry1 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveRightInputEntry1.place(x=175, y=15, height=30, width=50)

fanCurveRightInputEntry2 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveRightInputEntry2.place(x=233, y=15, height=30, width=50)

fanCurveRightInputEntry3 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveRightInputEntry3.place(x=291, y=15, height=30, width=50)

fanCurveRightInputEntry4 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveRightInputEntry4.place(x=349, y=15, height=30, width=50)

fanCurveRightInputEntry5 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveRightInputEntry5.place(x=407, y=15, height=30, width=50)

fanCurveRightInputEntry6 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveRightInputEntry6.place(x=465, y=15, height=30, width=50)

fanCurveRightInputEntry7 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveRightInputEntry7.place(x=523, y=15, height=30, width=50)

fanCurveRightInputEntry8 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveRightInputEntry8.place(x=581, y=15, height=30, width=50)

fanCurveRightInputEntry9 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black')
fanCurveRightInputEntry9.place(x=639, y=15, height=30, width=50)

tempCurveGPUInputEntry1 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveGPUInputEntry1.place(x=175, y=55, height=30, width=50)

tempCurveGPUInputEntry2 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveGPUInputEntry2.place(x=233, y=55, height=30, width=50)

tempCurveGPUInputEntry3 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveGPUInputEntry3.place(x=291, y=55, height=30, width=50)

tempCurveGPUInputEntry4 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveGPUInputEntry4.place(x=349, y=55, height=30, width=50)

tempCurveGPUInputEntry5 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveGPUInputEntry5.place(x=407, y=55, height=30, width=50)

tempCurveGPUInputEntry6 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveGPUInputEntry6.place(x=465, y=55, height=30, width=50)

tempCurveGPUInputEntry7 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveGPUInputEntry7.place(x=523, y=55, height=30, width=50)

tempCurveGPUInputEntry8 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveGPUInputEntry8.place(x=581, y=55, height=30, width=50)

tempCurveGPUInputEntry9 = CTkEntry(fanCurveRightInputFrame, bg='#9E9EA4', text_font=("Arial", 15), fg='black', justify='center')
tempCurveGPUInputEntry9.place(x=639, y=55, height=30, width=50)


#Current Data Frame elements
currentDataFrameFanSpeed = CTkFrame(currentDataFrame, bg='#000000')
currentDataFrameFanSpeed.place(height=99, width=349)

currentDataFrameTemp = CTkFrame(currentDataFrame, bg='#000000')
currentDataFrameTemp.place(height=99, width=349, x=350)


#Current Data Fan Speed
currentDataFrameFanSpeedText = CTkLabel(currentDataFrameFanSpeed, text='Current Fan Speed', text_font=("Arial", 15), fg='white', bg='#000000')
currentDataFrameFanSpeedText.place(rely=0.025, relheight=0.20, relwidth=1)

currentDataFrameFanSpeedLeftText = CTkLabel(currentDataFrameFanSpeed, text='Left Fan', text_font=("Arial", 12), fg='white', bg='#000000')
currentDataFrameFanSpeedLeftText.place(rely=0.3, relheight=0.30, relwidth=0.4)

currentDataFrameFanSpeedRightText = CTkLabel(currentDataFrameFanSpeed, text='Right Fan', text_font=("Arial", 12), fg='white', bg='#000000')
currentDataFrameFanSpeedRightText.place(rely=0.65, relheight=0.30, relwidth=0.4)

fanSpeedCurrentLeftLabel = CTkLabel(currentDataFrameFanSpeed, bg='#9E9EA4', text_font=("Arial", 17), fg='black')
fanSpeedCurrentLeftLabel.place(relx=0.4, rely=0.30, relheight=0.30, relwidth=0.5)

fanSpeedCurrentRightLabel = CTkLabel(currentDataFrameFanSpeed, bg='#9E9EA4', text_font=("Arial", 17), fg='black')
fanSpeedCurrentRightLabel.place(relx=0.4, rely=0.65, relheight=0.30, relwidth=0.5)


#Current Data Temps
currentDataFrameTempText = CTkLabel(currentDataFrameTemp, text='Current Temps', text_font=("Arial", 15), fg='white', bg='#000000')
currentDataFrameTempText.place(rely=0.025, relheight=0.20, relwidth=1)

currentDataFrameTempCPUText = CTkLabel(currentDataFrameTemp, text='CPU', text_font=("Arial", 12), fg='white', bg='#000000')
currentDataFrameTempCPUText.place(relx=0.005, rely=0.3, relheight=0.30, relwidth=0.4)

currentDataFrameTempGPUText = CTkLabel(currentDataFrameTemp, text='GPU', text_font=("Arial", 12), fg='white', bg='#000000')
currentDataFrameTempGPUText.place(relx=0.005, rely=0.65, relheight=0.30, relwidth=0.4)

tempCurrentCPULabel = CTkLabel(currentDataFrameTemp, bg='#9E9EA4', text_font=("Arial", 17), fg='black')
tempCurrentCPULabel.place(relx=0.4, rely=0.30, relheight=0.30, relwidth=0.5)

tempCurrentGPULabel = CTkLabel(currentDataFrameTemp, bg='#9E9EA4', text_font=("Arial", 17), fg='black')
tempCurrentGPULabel.place(relx=0.4, rely=0.65, relheight=0.30, relwidth=0.5)


# Buttons
perfBtn = CTkButton(modes, image=perfIcon, text='', command=perfBtnPressed)
perfBtn.place(x=100, width=100, height=97)

balancedBtn = CTkButton(modes, image=balancedIcon, text='', command=balancedBtnPressed)
balancedBtn.place(x=200, width=100, height=97)

quietBtn = CTkButton(modes, image=quietIcon, text='', command=quietBtnPressed)
quietBtn.place(x=300, width=100, height=97)

saveBtn = CTkButton(modes, image=saveIcon, text='', command=saveBtnPressed)
saveBtn.place(x=400, width=100, height=97)

settingsBtn = CTkButton(modes, image=settingsIcon, text='')
settingsBtn.place(x=500, width=100, height=97)

getCurrentPowerMode()
getCurrentData()
getCurrentFanCurve()
initEntryes()

root.mainloop()