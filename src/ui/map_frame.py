from tkinter import *
from tkinter import messagebox
from ui.widgets import PauseSimulationButton, ManualStartTourButton
from PIL import Image, ImageTk
import tkintermapview

from simulation.geometry import distBetween
from database.orders import get_order_by_location, get_order_items


# class to represent the left side of the display
class MapFrame:
	def __init__(self,parent):	
			
		# initialises the path as none and the delivery point pins placed as empty and no point selected
		self.TSPpath = None
		self.deliveryPointPins = {}
		self.tempMarker = None

		# Create map frame (Left side)
		self.mapFrame = Frame(parent,bg="#d9c796")
		self.mapFrame.grid(row=1, columnspan=2, sticky="nsew", padx=7.5,pady=15)

		# adds title above map
		mapLabel = Label(self.mapFrame, text="Current drone location:", font=("Arial", 14, "bold"), pady=10)
		mapLabel.place(x=10,y=10)

		#adds map
		self.map_widget = tkintermapview.TkinterMapView(self.mapFrame, width=800, height=460, corner_radius=5)
		self.map_widget.place(x=10,y=70)
		self.map_widget.set_position(51.7345329,0.4730532)
		self.map_widget.set_zoom(13)


		#displays each warehouse as a blue marker on the map
		self.warehouse1Coords = (51.7384678, 0.4673860)
		self.map_widget.set_position(51.7384678, 0.4673860, marker=True, marker_color_circle="#022e59", marker_color_outside="#014c94")
		self.warehouse2Coords = (51.7295375, 0.4761407)
		self.map_widget.set_position(51.7295375, 0.4761407, marker=True, marker_color_circle="#022e59", marker_color_outside="#014c94")
		
		#displays charging point as green marker on map
		self.chargingPointCoords = (51.7470199,0.4881171)
		self.map_widget.set_position(51.7470199,0.4881171, marker = True, marker_color_circle="#0c5902", marker_color_outside="#0f8000")


	def passObjects(self, orderMenu, deliveryDrone):
		self.orderMenu = orderMenu
		self.deliveryDrone = deliveryDrone

		self.addButtons()
		

	# method to display a new pin on the map and update the location when a delivery point is initially selected
	def add_location_event(self,coords):
		
		# checks if there is already a tentative delivery point selected and deletes it
		if self.tempMarker is not None:
			self.tempMarker.delete()
			
		# stores the temporary coordinates and places a pin at that point on the map
		self.tempCoords = coords
		self.tempMarker = self.map_widget.set_marker(coords[0], coords[1], marker_color_circle="#4077cf")
		
		# updates the location entry box to show the current point selected
		self.orderMenu.location.set(str(coords[0])+" "+str(coords[1]))


	# displays the relevant information to the user when the drone is clicked
	def droneClicked(self, marker):
		# displays the drone battery
		message = "The drone battery is "+ str(self.deliveryDrone.battery) +"%"
		messagebox.showinfo("drone battery",message)


	def addButtons(self):
		#loads and adjusts the drone icon from files
		image = Image.open(r"assets/drone.png")
		image = image.resize((50, 50))  # Resize image properly
		droneIcon = ImageTk.PhotoImage(image)

		#displays the drone on the map using the imported icon
		self.deliveryDrone.droneMarker = self.map_widget.set_position(self.deliveryDrone.coords[0], self.deliveryDrone.coords[1], icon=droneIcon, marker=True, command=self.droneClicked)
		
		# allows the user the option to select location if they right click on the map
		self.map_widget.add_right_click_menu_command(label="Select location", command=self.add_location_event, pass_coords=True) 

		# adds button to pause and play the drone delivery simulation
		pausePlayButton = PauseSimulationButton(self.mapFrame, "Pause Simulation", self.orderMenu, self, self.deliveryDrone)
		pausePlayButton.place()
		
		# adds button to manually start the tour
		startTourButton = ManualStartTourButton(self.mapFrame, "Manually start deliveries", self.orderMenu, self, self.deliveryDrone)
		startTourButton.place()


	# function to get the item and quantities selected in the clicked order
	def getOrderItems(self, deliveryCoords):
		# selects the orderId by the delivery coordinates
		orderId = get_order_by_location(deliveryCoords[0],deliveryCoords[1])
		# selects the product and quantity from the orderLine table using the orderId
		results = get_order_items(orderId[0])
		return results
	

	# calculates the expected time till delivery
	def calcDeliveryTime(self, deliveryCoords, coordsToVisit):
		
		# only makes predictions if the order is currently in the batch being delivered
		if deliveryCoords in coordsToVisit:
			# calculates the distance between the drone and the next point it will visit
			dist = distBetween(self.deliveryDrone.coords,coordsToVisit[0])

			# iterates through the points the drone will visit, adding up the distance between it and the previous point
			for i in range(0,len(coordsToVisit)):
				# repeats until the clicked point is found and breaks
				if coordsToVisit[i] != deliveryCoords:
					dist += distBetween(coordsToVisit[i],coordsToVisit[i+1])
				else:
					break
		# else return null value to indicate that no prediction made
		else:
			return None
		
		distM = dist*1000
		timeSec = distM/20  # uses time = distance/speed to get time expected in seconds
		
		if self.chargingPointCoords in coordsToVisit or self.deliveryDrone.coords == self.chargingPointCoords:
			timeToCharge = 600 * (100 - self.deliveryDrone.battery)/100
			timeSec += timeToCharge
		
		# converts to minutes and seconds and returns
		timeMin = int(timeSec // 60)
		timeSec = int(timeSec % 60)
		return timeMin,timeSec
	

	# function to show order details when a delivery point is clicked
	def deliveryPointClicked(self,marker):

		# iterates through all items in dictionary to get the coordinates of the marker clicked
		for coords, pin in self.deliveryPointPins.items():
			if pin == marker:
				markerCoords = coords
				break
		
		# calls getOrderItems to get the list of products in that order
		itemQuantityList = self.getOrderItems(markerCoords)

		# formats and adds all the items and their quantities to a string message
		orderItems = ""
		for item,quantity in itemQuantityList:
			if quantity != 0:
				orderItems += item + ": " + str(quantity)+ ". "
			
		# calls calcDeliveryTime to get the predicted time till delivery
		deliveryTime = self.calcDeliveryTime(markerCoords,self.deliveryDrone.coordinatePath)
		
		# checks if time predicted i.e if order items dispatched for delivery
		# displays appropriate messages
		if deliveryTime is not None:
			deliveryTimeMin, deliveryTimeSec = deliveryTime
			messagebox.showinfo("order details", "The order consists of the following... "+orderItems+"Delivery expected in "+str(deliveryTimeMin)+" minutes and "+str(deliveryTimeSec)+" seconds")
		else:
			messagebox.showinfo("order details", "The order consists of the following... "+orderItems+". The order has not yet been dispatched for delivery.")
