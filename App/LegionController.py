from tkinter import*
from PIL import ImageTk, Image

root = Tk()
root.geometry('500x500')
root.title('LegionController')
root.resizable(False, False)

#Vars

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
img.thumbnail((100,100), Image.ANTIALIAS)
saveIcon = ImageTk.PhotoImage(img)
#Settings Icon
img = Image.open("/home/nutsu7/LegionController/App/img/settings.png") 
img.thumbnail((100,100), Image.ANTIALIAS)
settingsIcon = ImageTk.PhotoImage(img)


# Main Frames
page = Frame(root, bg='#000000', highlightbackground="white", highlightthickness=1)
page.place(relheight=0.80, relwidth=1)

modes = Frame(root, bg='#000000', highlightbackground="white", highlightthickness=1)
modes.place(rely=0.80, relheight=0.20, relwidth=1)


#Page


# Buttons
perfBtn = Button(modes, image=perfIcon, bg='#676871')
perfBtn.place(relwidth=0.20, relheight=1)

balancedBtn = Button(modes, image=balancedIcon, bg='#676871')
balancedBtn.place(relx=0.20, relwidth=0.20, relheight=1)

quietBtn = Button(modes,image=quietIcon, bg='#676871')
quietBtn.place(relx=0.40, relwidth=0.20, relheight=1)

saveBtn = Button(modes, image=saveIcon, bg='#676871')
saveBtn.place(relx=0.60, relwidth=0.20, relheight=1)

settingsBtn = Button(modes, image=settingsIcon, bg='#676871')
settingsBtn.place(relx=0.80, relwidth=0.20, relheight=1)

root.mainloop()