from abc import ABC, abstractmethod
from tkinter import *
from tkinter import messagebox
import time

from database.database import get_connection



# parent class what is inherited by all the buttons
class ButtonBase(ABC):
	#defines basic structure for button
	def __init__(self, parent, message, orderMenu, mapDisplay, deliveryDrone):
		self.message = StringVar()
		self.button = Button(
			parent,
			textvariable=self.message,  # variable message on button can be changed throughout running of the code
			command=self.action,
			activebackground="white",
			anchor="center",
			borderwidth=3,
			background="lightgreen",
			height=2,
			padx=10,
			pady=5,
			width=15
		)
		self.message.set(message)
		self.orderMenu = orderMenu
		self.mapDisplay = mapDisplay
		self.deliveryDrone = deliveryDrone

	#defines action of button
	@abstractmethod  #is an abstract method that is used by all the buttons that inherit the class
	def action(self):
		pass
	


#button to place the order selected
#inherits the button class	
class PlaceOrderButton(ButtonBase):
	
	#implements the abstact method from button base
	def action(self):		
		#uses the database to calculate the total weight of the order
		def getOrderWeight():
			conn = get_connection()
			cursor = conn.cursor()

			#gets the weight of the eah product from the database
			cursor.execute('SELECT weight FROM products')
			weights = cursor.fetchall()

			conn.commit()
			conn.close()
			
			#multiplies the weight of each order by the quantity ordered
			weight = self.orderMenu.milkSlider.getValue() * weights[0][0] + self.orderMenu.waterSlider.getValue() * weights[1][0] + self.orderMenu.pastaSlider.getValue() * weights[2][0] + self.orderMenu.tunaSlider.getValue() * weights[3][0] + self.orderMenu.cerealSlider.getValue() * weights[4][0] + self.orderMenu.breadSlider.getValue() *weights[5][0] + self.orderMenu.soupSlider.getValue()*weights[6][0] + self.orderMenu.medSlider.getValue()*weights[7][0]

			return weight
		

		confirmed = messagebox.askokcancel("confirm order", "Are you sure you want to place this order?") 
		
		if confirmed:

			#deletes marker if already placed (if the user selects location using the map)
			try:
				self.mapDisplay.tempMarker.delete()
			#otherwise entered location latitude and longitude
			except:
				coords = self.orderMenu.location.get()  #gets userinput into location box
				if coords != "":
					#splits input into lat and long
					coordArr = coords.split()
					self.mapDisplay.tempCoords = (float(coordArr[0]), float(coordArr[1]))
				else:
					#if empty, provides error message to user
					messagebox.showerror("error", "No location provided") 
					return None
			
			self.mapDisplay.tempMarker = None
		
			#checks if the delivery location is within the specified region
			if self.mapDisplay.tempCoords[0]<51.7592733 and self.mapDisplay.tempCoords[1]<0.5149852 and self.mapDisplay.tempCoords[0]>51.7146676 and self.mapDisplay.tempCoords[1]> 0.4420291:
			
				orderWeight = getOrderWeight()
				# check that the weight of the order is within the max load that the drone can carry
				if orderWeight < 15.9:
				
					#adds a marker for the delivery point on the map
					self.mapDisplay.deliveryPointPins[self.mapDisplay.tempCoords] = self.mapDisplay.map_widget.set_position(self.mapDisplay.tempCoords[0],self.mapDisplay.tempCoords[1], marker=True, command=self.mapDisplay.deliveryPointClicked)

					# adds it to the order queue with -1 representing filler for the orderId
					self.orderMenu.orderQueue.append([-1, orderWeight])
					
					# if the item is the first one added to the queue, starts the timer in checkConditions to start the tour
					if len(self.orderMenu.orderQueue) == 1:
						self.deliveryDrone.startTime = time.time()

					self.orderMenu.updateItemNums()  #changes the maximum quantities available for each item

				else:
					#gives error message is weight greater than drone max
					messagebox.showerror("error", "Order too heavy")
			else:
				#gives error message if location out of range
				messagebox.showerror("error", "Location out of range") 
		else:
			#gives confirmatiomn that order cancelled
			messagebox.showinfo("order status", "order successfully cancelled")
			

		#updates the display for self.orderMenu
		self.orderMenu.location.set("") 
		
	#places the button in the appropriate location
	def place(self):
		self.button.grid(columnspan=4, pady=10)  # Center button across 4 columns



#button to pause the simulation
#inherits the button class	
class PauseSimulationButton(ButtonBase):
	
	#implements the abstract method from button base class
	def action(self):
		
		#if the drone isn't currently paused, pauses it
		if not self.deliveryDrone.paused:
			self.message.set("Resume simulation")  # changes the message on the button
			self.deliveryDrone.paused = True
			
		# otherwise the drone must be paused, and so resumes it
		else:
			self.message.set("Pause simulation") # changes the message on the button
			self.deliveryDrone.paused = False
			

	#places the update map button in the appropriate location
	def place(self):
		self.button.place(x=10,y=550)
		


# button to manually start the drone delivery tour
# inherits the button base class 		
class ManualStartTourButton(ButtonBase):
	
	#implements the abstract method from button base class
	def action(self):
		
		#checks if the drone has finished its current tour
		if self.deliveryDrone.tourComplete:
			#checks if there are any orders pending
			if len(self.orderMenu.orderQueue) != 0:
				self.deliveryDrone.startTour()  #if all the conditions are met, starts the tour
			# if no orders placed, asks the user to place an order and try again
			else:
				messagebox.showerror("error starting tour", "No orders currently pending. Please place an order and try again")
		# if the drone is currently delivering packages, provides suitable error message
		else:
			messagebox.showerror("error starting tour", "Drones currently busy. Please wait until current tour is finished and try again")
			

	#places the start tour button in the appropriate location
	def place(self):
		self.button.place(x=675,y=550)
			
		
		

#base class to determine the format for each label
class LabelBase:
	#creates label for displaying each item name
	def __init__(self, parent, text, row, col):
		self.label = Label(parent, text=text, font=("Arial", 12), anchor="nw")
		self.label.grid(row=row, column=col, padx=10, pady=5, sticky="w")  # Left align text
	   
	#function to delete label
	def delete(self):
		self.label.destroy()


#base class that is used to represent the format for each slider
class ItemNum:
	#creates sliders for each item 
	def __init__(self, parent, maxNum, row):
		#if there aren't any of the item currently available in stock
		if maxNum == 0:
			#displays appropriate error message
			self.label = Label(parent, text="Currently unavailable", fg="red")
			self.label.grid(row=row, column=2, columnspan=2, padx=10, pady=5, sticky="ew")
		else:
			#creates slider that ranges from 0 to the maximum number of items available
			self.scale = Scale(parent, from_=0, to=maxNum, orient=HORIZONTAL, sliderlength=20)
			self.scale.grid(row=row, column=2, columnspan=2, padx=10, pady=5, sticky="ew")

	#function to delete the slider
	def delete(self):
		if hasattr(self,"scale"):
			self.scale.destroy()
		else:
			self.label.destroy()

	#returns the value of the slider or zero if item unavailable
	def getValue(self):
		return self.scale.get() if hasattr(self, "scale") else 0
