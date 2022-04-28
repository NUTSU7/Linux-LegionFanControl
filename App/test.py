from tkinter import * 
from tkinter.ttk import *
  
# create tkinter window
gui = Tk() 
  
# Adding widgets to the window
Label(gui, text='Setting', font=('Verdana', 15))
  
# Create a photoimage object to use the image
photo = PhotoImage(file = r"/home/nutsu7/LegionController/App/img/quiet.png") 

# Add image to button
b = Button(gui, image=photo)
b.grid(row=0, column=2, sticky=S, padx=250)
  
mainloop()