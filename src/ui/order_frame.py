from tkinter import *
import time

from ui.widgets import PlaceOrderButton, ItemNum, LabelBase
from database.database import get_connection
from database.inventory import get_warehouse_stock



#Displays the orderFrame with its contents
class OrderFrame:
	def __init__(self, parent):
		
		# function to get the total stock available when the program is started using the database
		def getStartingTotals():
			# selects the product name and the number available in warehouse 1 & 2
			warehouse1Numbers = get_warehouse_stock(stockNum="stock1")
			warehouse2Numbers = get_warehouse_stock(stockNum="stock2")
			
			totalStock = []  # initialises empty list for total stock
			# iterates through each product available and sums the number available in each warehouse
			for i in range(0,len(warehouse1Numbers)):
				total = warehouse1Numbers[i][1] + warehouse2Numbers[i][1]
				totalStock.append((warehouse1Numbers[i][0], total))  # adds the item name and the total number available to the total stock list
				
			return totalStock
			

		# starts off with all the values as 0 as no orders placed yet
		self.totalOrdersQuanitities = [0,0,0,0,0,0,0,0]  
		self.batchQuantities = [0,0,0,0,0,0,0,0]
		self.orderQueue = []
		self.batchWeight = 0

		# Create order frame (Right side of screen)
		self.orderFrame = Frame(parent, bg="#84CEEB")
		self.orderFrame.grid(row=1, column=2, sticky="nsew", padx=7.5,pady=15)  # places it on the right side of the screen
		self.orderFrame.columnconfigure(1, weight=1)  # Make the scale sliders expand

		# Creates and displays the order instructions
		orderInstruction = Label(self.orderFrame, text="Place a new order below:", font=("Arial", 14, "bold"), pady=10)
		orderInstruction.grid(row=0, columnspan=4)  # places it at the top of the orderFrame
		
		totalStock = getStartingTotals()  # calls getStartingTotals to get the initial number for each slider

		#Adds each item and corresponding slider using the label base and itemNum classes
		self.milkLabel = LabelBase(self.orderFrame, totalStock[0][0], 1,0)
		self.milkSlider = ItemNum(self.orderFrame, totalStock[0][1], 1)
		self.waterLabel = LabelBase(self.orderFrame, totalStock[1][0], 2,0)
		self.waterSlider = ItemNum(self.orderFrame, totalStock[1][1], 2)
		self.pastaLabel = LabelBase(self.orderFrame, totalStock[2][0], 3,0)
		self.pastaSlider = ItemNum(self.orderFrame, totalStock[2][1], 3)
		self.tunaLabel = LabelBase(self.orderFrame, totalStock[3][0], 4,0)
		self.tunaSlider = ItemNum(self.orderFrame, totalStock[3][1], 4)
		self.cerealLabel = LabelBase(self.orderFrame, totalStock[4][0], 5,0)
		self.cerealSlider = ItemNum(self.orderFrame, totalStock[4][1], 5)
		self.breadLabel = LabelBase(self.orderFrame, totalStock[5][0], 6,0)
		self.breadSlider = ItemNum(self.orderFrame, totalStock[5][1], 6)
		self.soupLabel = LabelBase(self.orderFrame, totalStock[6][0], 7,0)
		self.soupSlider = ItemNum(self.orderFrame, totalStock[6][1], 7)
		self.medLabel = LabelBase(self.orderFrame, totalStock[7][0], 8,0)
		self.medSlider = ItemNum(self.orderFrame, totalStock[7][1], 8)
		

		#creates and places a label for the location instructions
		locationInstruction = Label(self.orderFrame, text="Enter the delivery location below or select on the map:", font=("Arial", 14, "bold"), pady=10)
		locationInstruction.grid(row=9, columnspan=4)
		
		#Creates label and entry box for latitude and longitude values and displays it to user
		LabelBase(self.orderFrame, "Location:", 10,0) 
		self.location= StringVar()  # creates a variable string value for it
		
		# creates and places the entry box with a the value entered stored in self.location
		locationEntry = Entry(self.orderFrame, textvariable=self.location)
		locationEntry.grid(row=10, column=1, columnspan=3, sticky="ew", padx=10)
		

	def passObjects(self, mapDisplay, deliveryDrone):
		self.mapDisplay = mapDisplay
		self.deliveryDrone = deliveryDrone

		self.addButtons()


	def addButtons(self):
		# creates and places the order Button
		orderButton = PlaceOrderButton(self.orderFrame, "Place Order", self, self.mapDisplay, self.deliveryDrone)
		orderButton.place()

	
	# function to get new total values for the sliders after an order is placed
	def getNewTotals(self):
		
		# adds the product id and value from the order to the orderNum array
		orderNum = []
		orderNum.append((1,self.milkSlider.getValue()))
		orderNum.append((2,self.waterSlider.getValue()))
		orderNum.append((3,self.pastaSlider.getValue()))
		orderNum.append((4,self.tunaSlider.getValue()))
		orderNum.append((5,self.cerealSlider.getValue()))
		orderNum.append((6,self.breadSlider.getValue()))
		orderNum.append((7,self.soupSlider.getValue()))
		orderNum.append((8,self.medSlider.getValue()))
		
		# connects to the database
		conn = get_connection()
		cursor = conn.cursor()
		
		# add entry to orders table for the order placed
		cursor.execute('''INSERT INTO orders (deliveryLat, deliveryLong, orderWeight, timeOrderPlaced)
					   VALUES (?,?,?,?)''', (self.mapDisplay.tempCoords[0], self.mapDisplay.tempCoords[1],self.orderQueue[len(self.orderQueue)-1][1],time.time()))
		conn.commit()
		
		# gets the orderId of the order from the database table
		cursor.execute("SELECT orderId FROM orders WHERE deliveryLat = ? AND deliveryLong = ?", (self.mapDisplay.tempCoords[0], self.mapDisplay.tempCoords[1]))
		orderId = cursor.fetchone()
		orderId = orderId[0]
		
		# updates the orderId value of the order in orderQueue from -1
		self.orderQueue[len(self.orderQueue)-1][0] = orderId
		

		# selects the product name and the number available in warehouse 1 & 2
		warehouse1Numbers = get_warehouse_stock(stockNum="stock1")
		warehouse2Numbers = get_warehouse_stock(stockNum="stock2")

		
		totalStock = []  # initialises the total stock and empty list
		# iterates through each product
		for i in range(0,len(orderNum)):
		    # gets the number of that product ordered and increases this to the quantities of all the orders list
			quantity = orderNum[i][1]
			self.totalOrdersQuanitities[i] += quantity  
			# appends the product name and the total number of that item available to the totalStock list
			stockNum = warehouse1Numbers[i][1] + warehouse2Numbers[i][1] - self.totalOrdersQuanitities[i]
			totalStock.append((warehouse1Numbers[i][0], stockNum))
			
			# adds an entry for the product and the number ordered into the orderLine table
			cursor.execute('''INSERT INTO orderLine(orderId, productId, quantity)
				  VALUES (?,?,?)''', (orderId, i+1, quantity)) #add to orderline table
			
		conn.commit()
			
		return totalStock
		
	
	# updates the max item numbers in the display window 
	def updateItemNums(self):
		# used the getNewTotals function to get the new total available as a 2d array
		totalNum = self.getNewTotals()

		# deletes all the current labels and sliders
		self.milkLabel.delete()
		self.milkSlider.delete()
		self.waterLabel.delete()
		self.waterSlider.delete()
		self.pastaLabel.delete()
		self.pastaSlider.delete()
		self.tunaLabel.delete()
		self.tunaSlider.delete()
		self.cerealLabel.delete()
		self.cerealSlider.delete()
		self.breadLabel.delete()
		self.breadSlider.delete()
		self.soupLabel.delete()
		self.soupSlider.delete()
		self.medLabel.delete()
		self.medSlider.delete()

		#updates each item and corresponding slider using the values in totalNum
		self.milkLabel = LabelBase(self.orderFrame, totalNum[0][0], 1,0)
		self.milkSlider = ItemNum(self.orderFrame, totalNum[0][1], 1)
		self.waterLabel = LabelBase(self.orderFrame, totalNum[1][0], 2,0)
		self.waterSlider = ItemNum(self.orderFrame, totalNum[1][1], 2)
		self.pastaLabel = LabelBase(self.orderFrame, totalNum[2][0], 3,0)
		self.pastaSlider = ItemNum(self.orderFrame, totalNum[2][1], 3)
		self.tunaLabel = LabelBase(self.orderFrame, totalNum[3][0], 4,0)
		self.tunaSlider = ItemNum(self.orderFrame, totalNum[3][1], 4)
		self.cerealLabel = LabelBase(self.orderFrame, totalNum[4][0], 5,0)
		self.cerealSlider = ItemNum(self.orderFrame, totalNum[4][1], 5)
		self.breadLabel = LabelBase(self.orderFrame, totalNum[5][0], 6,0)
		self.breadSlider = ItemNum(self.orderFrame, totalNum[5][1], 6)
		self.soupLabel = LabelBase(self.orderFrame, totalNum[6][0], 7,0)
		self.soupSlider = ItemNum(self.orderFrame, totalNum[6][1], 7)
		self.medLabel = LabelBase(self.orderFrame, totalNum[7][0], 8,0)
		self.medSlider = ItemNum(self.orderFrame, totalNum[7][1], 8)
		