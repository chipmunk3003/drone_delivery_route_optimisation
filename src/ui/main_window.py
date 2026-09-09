from tkinter import *
import threading

from simulation.drone import Drone
from ui.map_frame import MapFrame
from ui.order_frame import OrderFrame
from ui.widgets import *
from database.database import get_connection




class DroneDeliveryApp():

	def __init__(self):
		# Connect to database file
		conn = get_connection()
		# Create a cursor object
		cursor = conn.cursor()

		cursor.execute("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%';")
		tables = cursor.fetchall()

		for table in tables:
			print(f"\nTable: {table[0]}")
			cursor.execute(f"SELECT * FROM {table[0]}")
			for row in cursor.fetchall():
				print(row)
			
		# clears the order and orderline tables every time program is run
		cursor.execute("DELETE FROM orders")
		cursor.execute("DELETE FROM orderLine")


		# optionally replaces database values with vaues to test with
		# prespecified values for the starting stock in each warehouse
		startingStock1 = [18,30,25,12,21,14,0,15]
		startingStock2 = [11,29,17,9,21,18,0,13]

		replace = True

		if replace:
			# for each item updates the both warehouse stock values to show the starting quantities 
			for i in range(0,len(startingStock1)):
				
				cursor.execute('''
				UPDATE stock1
				SET numAvailable = ?
				WHERE productId = ?
			''', (startingStock1[i], i+1))
				
				cursor.execute('''
				UPDATE stock2
				SET numAvailable = ?
				WHERE productId = ?
			''', (startingStock2[i], i+1))


		conn.commit()


		# Creates root window
		self.root = Tk()
		self.root.state('zoomed')
		self.root.title("Drone delivery optimisation")

		# Configures grid in root
		self.root.columnconfigure(0, weight=1)
		self.root.columnconfigure(1, weight=1) 
		self.root.rowconfigure(1, weight=1)

		# Adds main title
		title = Label(
			self.root,
			text="Drone Delivery System",
			font=("Arial", 20, "bold"),
			pady=10
		)
		title.grid(row=0, column=0, columnspan=4, sticky="n")

		# Initialize UI
		self.orderMenu = OrderFrame(self.root)
		self.mapDisplay = MapFrame(self.root)
		self.deliveryDrone = Drone()

		self.deliveryDrone.passObjects(self.orderMenu, self.mapDisplay)
		self.orderMenu.passObjects(self.mapDisplay, self.deliveryDrone)
		self.mapDisplay.passObjects(self.orderMenu, self.deliveryDrone)


	def run(self):
		# creates & starts 2 threads that will run parallel with the main program
		checkTourThread = threading.Thread(target=self.deliveryDrone.checkStartTour)  # thread to check if a tour should be started
		moveDroneThread = threading.Thread(target=self.deliveryDrone.moveOnMap)   # thread to move the drone around the map if a tour in progress

		checkTourThread.start()
		moveDroneThread.start()

		# Run application
		self.root.mainloop()



