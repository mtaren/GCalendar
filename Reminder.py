
from Tkinter import *
import tkFont
import winsound






class Reminder:
	def __init__(self,parent, event):
		winsound.PlaySound('bells.wav', winsound.SND_FILENAME)
		#The frame instance is stored in a local variable 'f'.
		#After creating the widget, we immediately call the 
		#pack method to make the frame visible.
		self.root = parent
		self.action = None
		self.times = []
		ROW = 0
		f = Frame(parent)
		f.pack(padx=15,pady=15)
		self.BIG = tkFont.Font(family="Helvetica", size=23	)
		self.MED = tkFont.Font(family="Helvetica", size=16)
		
		self.buttonpaddingx= 15
		self.outsidebuttonpaddingx = 5
		#------------------row 0----------------------#
		#self.title = Label(f, text = str(event['summary'])).grid(row = ROW)
		self.title = Label(f, text = str(event['summary']),width = 20, font = self.BIG, wraplength = 350).grid(row = ROW, columnspan=9, pady = 19)
		ROW = ROW + 1
		#------------------row 1----------------------#
		#self.delaytext = Label(f, text = 'Delay For:', font = self.MED).grid(row= ROW)
		#ROW = ROW + 1
		
		#------------------row 2----------------------#
		self.delayminutes = StringVar()
		self.delayminutes.set('5')
		self.minutetext = Label(f, text = 'Minutes:', font = self.MED ).grid(row= ROW, column = 0)
		self.minuteval = Entry( f, text = self.delayminutes, font = self.MED,width = 5, justify = CENTER).grid(row= ROW, column = 1)
		self.addminbutt = Button(f, text = "+" , padx = self.buttonpaddingx,font = self.MED,command = lambda: self.ChangeDelay(5, self.delayminutes)).grid(row = ROW, column = 2, padx = self.outsidebuttonpaddingx, pady = 4)
		self.addminbutt = Button(f, text = "-" , padx = self.buttonpaddingx,font = self.MED,command = lambda: self.ChangeDelay(-5, self.delayminutes)).grid(row = ROW, column = 3, padx = self.outsidebuttonpaddingx, pady = 4)
		ROW = ROW + 1
		#------------------row 3----------------------#
   		self.delayhours = StringVar()
		self.delayhours.set('0')
		self.hourtext = Label(f, text = 'Hours:', font = self.MED ).grid(row= ROW, column = 0)
		self.hourval = Entry( f, text = self.delayhours, font = self.MED,width = 5, justify = CENTER).grid(row= ROW, column = 1)
		self.addminbutt = Button(f, text = "+" , padx = self.buttonpaddingx,font = self.MED,command = lambda: self.ChangeDelay(1, self.delayhours)).grid(row = ROW, column = 2, padx = self.outsidebuttonpaddingx, pady = 4)
		self.addminbutt = Button(f, text = "-" , padx = self.buttonpaddingx,font = self.MED,command = lambda: self.ChangeDelay(-1, self.delayhours)).grid(row = ROW, column = 3, padx = self.outsidebuttonpaddingx, pady = 4)
		ROW = ROW + 1
		#------------------row 4----------------------#
   		self.delaydays = StringVar()
		self.delaydays.set('0')
		self.hourtext = Label(f, text = 'Days:', font = self.MED ).grid(row= ROW, column = 0)
		self.hourval = Entry( f, text = self.delaydays, font = self.MED,width = 5, justify = CENTER).grid(row= ROW, column = 1)
		self.addminbutt = Button(f, text = "+" , padx = self.buttonpaddingx,font = self.MED,command = lambda: self.ChangeDelay(1, self.delaydays)).grid(row = ROW, column = 2, padx = self.outsidebuttonpaddingx, pady = 4)
		self.addminbutt = Button(f, text = "-" , padx = self.buttonpaddingx,font = self.MED,command = lambda: self.ChangeDelay(-1, self.delaydays)).grid(row = ROW, column = 3, padx = self.outsidebuttonpaddingx, pady = 4)
		ROW = ROW + 1
		#------------------row 5----------------------#
   		self.delayweeks = StringVar()
		self.delayweeks.set('0')
		self.hourtext = Label(f, text = 'Weeks:', font = self.MED ).grid(row= ROW, column = 0)
		self.hourval = Entry( f, text = self.delayweeks, font = self.MED,width = 5, justify = CENTER).grid(row= ROW, column = 1)
		self.addminbutt = Button(f, text = "+" , padx = self.buttonpaddingx,font = self.MED,command = lambda: self.ChangeDelay(1, self.delayweeks)).grid(row = ROW, column = 2, padx = self.outsidebuttonpaddingx, pady = 4)
		self.addminbutt = Button(f, text = "-" , padx = self.buttonpaddingx,font = self.MED,command = lambda: self.ChangeDelay(-1, self.delayweeks)).grid(row = ROW, column = 3, padx = self.outsidebuttonpaddingx, pady = 4)
		ROW = ROW + 1
		#------------------row 6----------------------#
   		self.delaymonths = StringVar()
		self.delaymonths.set('0')
		self.hourtext = Label(f, text = 'Months:', font = self.MED ).grid(row= ROW, column = 0)
		self.hourval = Entry( f, text = self.delaymonths, font = self.MED,width = 5, justify = CENTER).grid(row= ROW, column = 1)
		self.addminbutt = Button(f, text = "+" , padx = self.buttonpaddingx,font = self.MED,command = lambda: self.ChangeDelay(1, self.delaymonths)).grid(row = ROW, column = 2, padx = self.outsidebuttonpaddingx, pady = 4)
		self.addminbutt = Button(f, text = "-" , padx = self.buttonpaddingx,font = self.MED,command = lambda: self.ChangeDelay(-1, self.delaymonths)).grid(row = ROW, column = 3, padx = self.outsidebuttonpaddingx, pady = 4)
		ROW = ROW + 1
		#------------------row 7----------------------#
   		self.addminbutt = Button(f, text = "Dismiss" ,command = self.Dismiss, font = self.MED ).grid(row = ROW, column = 0, columnspan = 2)
		self.addminbutt = Button(f, text = "Delay" ,command = self.Delay, font = self.MED ).grid(row = ROW, column = 2, columnspan = 2, pady = 7)
		ROW = ROW + 1
		#------------------row 8----------------------#
		#maybe add a delete event here?
		self.addminbutt = Button(f, text = "Delete" ,command = self.Delete, font = self.MED ).grid(row = ROW, column = 0, columnspan = 2)

		
	def Delete(self):
		self.action = 'Delete'
		self.root.destroy()
		
	def Dismiss(self):
		self.action = 'Dismiss'
		self.root.destroy()
	
		
	def Delay(self):
		self.action = 'Delay'
		self.times.append(int(self.delayminutes.get()))
		self.times.append(int(self.delayhours.get()))
		self.times.append(int(self.delaydays.get()))
		self.times.append(int(self.delayweeks.get()))
		self.times.append(int(self.delaymonths.get()))
		validdelay = self.CheckAllZeros(self.times) # checks if user delays for 0 time
		if validdelay == False:
			self.action = 'Dismiss'
		self.root.destroy()
	
	def CheckAllZeros(self, mylist):
		for item in mylist:
			if item != 0:
				return True
		return False #all zeros
	
	def ChangeDelay(self, addmins, textvar):
		minutes = int(textvar.get())
		minutes = minutes + addmins
		if minutes >= 0 :
			textvar.set(str(minutes))
			return 
		else:
			textvar.set('0')
		
	def print_this(self):
		print "this is to be printed"

		#Finally, we provide some script level code that creates
		# a Tk root widget,and one instance of the App class using 
		#the root widget as its parent:

   		#The last call is to the mainloop method on the root widget. It enters the
		#Tk event loop, in which the application will stay until the quit method is
		#called (just click the exit button), or the window is closed.


def Create_reminder(event):
	root = Tk()
	root.title(event['summary'])
	root.wm_attributes("-topmost", 1)
	app = Reminder(root, event)
	root.mainloop()
	return app.times, app.action


class Popup:
	def __init__(self,parent):
		#The frame instance is stored in a local variable 'f'.
		#After creating the widget, we immediately call the 
		#pack method to make the frame visible.

		f = Frame(parent)
		f.pack(padx=15,pady=15)
		
   		self.exit = Button(f, text="exit", command=parent.destroy)
		self.exit.pack(side=BOTTOM,padx=10,pady=10)

def Create_popup():
	root = Tk()
	root.title('Exception!')
	app = Popup(root)
	root.mainloop()


#if __name__ == '__main__':
#	root = Tk()
#	root.title('testing')
#	app = Reminder(root, 'test')
#	root.mainloop()