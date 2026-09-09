import time
from tkinter import messagebox

from simulation.geometry import distBetween, calcBearing, calcNewPoint
from algorithms.graph import Graph
from database.database import get_connection



#class to represnt the drone
class Drone:
	def __init__(self):
		#initialises the drone with full battery from the charging station 
		self.coords = (51.7470199,0.4881171)
		self.battery = 20
		self.startTime = time.time()
		self.tourComplete = True
		self.pointsToVisitLatLong = []
		self.coordinatePath = []
		self.payload = 0
		self.paused = False


	# passes in the order and map display objects
	def passObjects(self, orderMenu, mapDisplay):
		self.orderMenu = orderMenu
		self.mapDisplay = mapDisplay


	# returns the flight time of the drone on full battery at a certain payload
	def calcMaxFlightTime(self,payload):
		# compares the payload to values, checking which region its in and returns the corresponding flight time in seconds
		if payload==0:
			return 3000
		elif payload<=2.3:
			return 2502
		elif payload<=4.5:
			return 1998
		elif payload<= 6.8:
			return 1596
		elif payload<= 9.1:
			return 1320
		elif payload<=11.3:
			return 1080
		elif payload<=13.6:
			return 750
		else:
			return 645


	# procedure that moves the drone around the map
	def moveOnMap(self):
		
		# calculates the battery taken in a time interval of 0.25 seconds depending on the drone payload
		def calcBatteryTaken():				
			
			maxFlightTime = self.calcMaxFlightTime(self.payload)  #gets the fight time on 100% using calcMaxFlightTime
			batteryTaken = 100*(0.25/maxFlightTime)  # uses the time interval to calculate the battery taken in that duration
			return batteryTaken		
		

		# helper function to move the drone
		def move():
			
			# calculates the time taken to charge the drone from the current battery 
			def calculateTimeToCharge(currentBattery):
				TIME0TO100 = 600  # constant to represent the time to fully charge the drone from 0%
				batteryToAdd = 100 - currentBattery  #calculates the amount of battery that needs to be added to get to 100%
				timeToCharge = TIME0TO100 * batteryToAdd/100  # uses the proportion of battery to be added to calculate the time to charge the drone
				return timeToCharge
			

			# calculates the increase in battery in the time interval
			def calcBatteryIncreaseInTime(time):
				TIME0TO100 = 600  # constant to represent the time to fully charge the drone from 0%
				increase = time*100 /TIME0TO100  # calculates the increase
				return increase
			

			# checks if the current tour is complete and if the drone is not paused
			while not self.tourComplete and not self.paused:
				
				# uses a constant to represent the time between moving the drone in the simulation
				TIMEBETWEEN = 0.25
				time.sleep(TIMEBETWEEN)  # pauses the thread for that amount of time
				distInTimeBetween = TIMEBETWEEN*0.02  # calcualates distance travelled in that time
				
				# deletes the drawn path and gets the next point to visit 
				self.mapDisplay.TSPpath.delete()
				nextPoint = self.coordinatePath[0]
				
				# checks if the point is within the distance travelled
				# checks if the drone reaches the next point within the time interval specified
				if distBetween(self.coords, nextPoint) < distInTimeBetween:
					
					#removes the point visited from the list
					self.coordinatePath.pop(0)
					
					#sets the drone marker to that delivery point and draws the new path on the map
					self.droneMarker.set_position(nextPoint[0], nextPoint[1])
					if self.coordinatePath != []:
						self.mapDisplay.TSPpath = self.mapDisplay.map_widget.set_path([self.coords]+self.coordinatePath, color = '#f05118', width=2)

					#checks if the point visited is a delivery point
					if nextPoint in self.mapDisplay.deliveryPointPins:
						
						#uses deliveryPointPins dictionary to the marker for the delivery point and deletes it from the map and the dictionary
						nextMarker = self.mapDisplay.deliveryPointPins.get(nextPoint)
						nextMarker.delete()  #deletes from the map
						del self.mapDisplay.deliveryPointPins[nextPoint]  #deletes reference from the dictionary
						

						# selects the basic order details from the database using the latitude and longitude coordinates
						cursor.execute("SELECT orderWeight, orderId, timeOrderPlaced FROM orders WHERE deliveryLat = ? AND deliveryLong = ?", (nextPoint[0], nextPoint[1]))
						orderWeight, orderId, timeOrderPlaced = cursor.fetchone()
						
						# updates the drone payload using the fact that the drone drops off items at delivery points
						self.payload -= orderWeight  #takes away the order weight from the drones payload

						# send message to user that order has been completed and asks if they want more details
						moreInfo = messagebox.askyesno("order status", "Order "+str(orderId)+" has been completed. Would you like more order details?")
						
						# selects the order information from the database using the orderId
						cursor.execute("""
										SELECT products.name, orderLine.quantity
										FROM orderLine
										JOIN products ON orderLine.productId = products.productId
										WHERE orderLine.orderId = ?;
									""", (orderId,))

						items = cursor.fetchall()
							
						#calculates the time that has passed since the order was placed to get the time taken to complete the order
						timeTakenSeconds = time.time() - timeOrderPlaced

						# checks if they want more information
						if moreInfo:
							timeTakenMinutesSeconds = (timeTakenSeconds//60, timeTakenSeconds%60)
							message = "The order took "+ str(timeTakenMinutesSeconds[0])+ " minutes and "+ str(timeTakenMinutesSeconds[1])+ " seconds to be delivered. The items delivered are specified below: "
							
							# adds the items fetched to the message
							for item, quantity in items:
								# checks if the item is ordered
								if quantity != 0:
									message += "" +item+ " "+str(quantity)
								
							messagebox.showinfo("order information", message)  # displays a message whith the order information to the user

					# checks if the next point to visit is the charging point
					elif nextPoint == self.mapDisplay.chargingPointCoords:
						# displays the drone battery to the user
						messagebox.showinfo("drone status", "Drone battery "+str(self.battery)+"%. Charging in progress")
						
						# calculates the time at which the drone will be fully charged and checks if that time has been reached
						timeCharged = time.time() + calculateTimeToCharge(self.battery)
						while time.time() < timeCharged:
							TIMEBETWEENUPDATES = 0.25  # constant to represent the time interval in which the drone battery is updated
							time.sleep(TIMEBETWEENUPDATES)  # pauses the thread for the time interval
							# updates the drone battery
							self.battery += calcBatteryIncreaseInTime(TIMEBETWEENUPDATES)  # uses the calcBatteryIncreaseInTime
						
					# otherwise the point must be a warehouse
					else:
						# checks if it visits warehouse1
						if nextPoint == self.mapDisplay.warehouse1Coords:
							self.payload += self.warehouse1batchWeight  # adds on the weight of the items picked up from warehouse1
						# else visits warehouse2
						else:
							self.payload += self.warehouse2batchWeight  # adds on the weight of the items picked up from warehouse1
						

					# checks if the point visited was the last point on the path
					if len(self.coordinatePath)	== 0:
						self.tourComplete = True  # sets tourComplete as True
						self.pointsToVisitLatLong = []  # clears the pointsToVisitLatLong list
						# sets the drone location to the point
						self.coords = nextPoint 
						self.droneMarker.set_position(self.coords[0], self.coords[1])
						self.payload = 0  # resets the payload to 0
						break  # breaks so the drone isn't moved again
					

					# calculates the distance left after the drone has moved to the last point
					distLeft = distInTimeBetween - distBetween(self.coords, nextPoint)
					nextPoint = self.coordinatePath[0]  # updates the next point to the item at the front of the path list
					distInTimeBetween = distLeft  
					self.mapDisplay.TSPpath.delete()  # deletes the path on the map
				

				# updates the drone battery
				batteryTakenInTime = calcBatteryTaken()  # calls the calcBatteryTaken function
				self.battery -= batteryTakenInTime  # updates the drone battery
				
				print("payload", self.payload)
				print(self.battery)

				
				# updates the map after the drone moves
				self.coords = calcNewPoint(self.coords, nextPoint, distInTimeBetween)  # calls the calcNewPoint function to get the new coordinates of the drone
				self.droneMarker.set_position(self.coords[0], self.coords[1])  # sets the new drone position marker
				self.mapDisplay.TSPpath = self.mapDisplay.map_widget.set_path([self.coords]+self.coordinatePath, color = '#f05118', width=2)  # draws the new path on the map
			

		# connects to the database
		conn = get_connection()
		cursor = conn.cursor()
		
		# loop to check if the drone should be moved after a fixed period of time
		while True:
			time.sleep(0.25)  # sleeps the thread for 0.25 seconds before checking if the drone should be moved
			move()
				
			
	#function to check if the drone is ready to start a delivery cycle
	def checkStartTour(self):
		
		#if more than 7 items in the order queue or 60 seconds have passed starts tour
		def checkConditions():
			
			# checks the relevant conditions ass well as whether the previous tour has finished and if the drone has been paused
			while (len(self.orderMenu.orderQueue) >=7 or (time.time() - self.startTime) > 60) and self.tourComplete and not self.paused:
				
				# checks if the order queue is empty
				if len(self.orderMenu.orderQueue) ==0:
					self.startTime = time.time()  # resets the startTime to the current time and breaks out of the loop
					break
				self.startTour()  # otherwise starts the tour
				
			# checks if the drone has been paused
			if self.paused:
				pauseTime = time.time() #records the time the drone was paused
				
				#repeatedly checks if the drone is still paused every 0.75 seconds
				while self.paused:
					time.sleep(0.75)
					
				# once the drone stops being paused, calculates the time it was paused for
				pauseDuration = time.time() - pauseTime
				self.startTime += pauseDuration  # factors this into the time before the tour is started
				
		
		# repeatedly checks the conditions every 0.75 seconds
		while True:
			checkConditions()
			time.sleep(0.75)
			


	def getWarehousesNumTaken(self,warehouses):
		
		warehouse1Taken = []
		warehouse2Taken = []

		conn = get_connection()
		cursor = conn.cursor()
		
		# fetches the product weight information and the number of each product available in warehouse 1
		cursor.execute('''SELECT stock1.numAvailable, products.weight
					   FROM products
					   JOIN stock1 ON products.productId = stock1.productId''')
		warehouse1Numbers = cursor.fetchall()
		
		# fetches the product weight information and the number of each product available in warehouse 2
		cursor.execute('''SELECT stock2.numAvailable, products.weight
					   FROM products
					   JOIN stock2 ON products.productId = stock2.productId''')
		warehouse2Numbers = cursor.fetchall()
		
		# initialises the weight of items picked from each warehouse as 0
		self.warehouse1batchWeight = 0
		self.warehouse2batchWeight = 0
		
		
		# iterates through each product
		for i in range(0,len(self.orderMenu.batchQuantities)):
			# gets all the relevant information about the product
			numOrdered = self.orderMenu.batchQuantities[i]  # gets the number of the product required for the batch delivery
			productWeight = warehouse1Numbers[i][1]  # gets the product weight
			warehouse1Value = warehouse1Numbers[i][0]  # gets the number available in warehouse 1
			warehouse2Value = warehouse2Numbers[i][0]  # gets the number available in warehouse 2
			
			# checks if only warehouse 1 will be visited
			if warehouses == "1":
				warehouse1Taken.append(numOrdered)
				warehouse2Taken.append(0)
				self.warehouse1batchWeight += numOrdered * productWeight  # adds on the total weight of the items picked up from warehouse 1
				
			# checks if only warehouse 2 will be visited
			elif warehouses == "2":
				warehouse1Taken.append(0)
				warehouse2Taken.append(numOrdered)
				self.warehouse2batchWeight += numOrdered * productWeight  # adds on the total weight of the items picked up from warehouse 2				

			# otherwise both warehouses must be visted
			else:
				# initially tries to take half of the stock from each warehosue to keep the numbers relatively even
				halfOrdered = numOrdered/2
		
				# checks if there is enough available in warehouse 1 to get half of the required amount
				if warehouse1Value < halfOrdered:
					left = halfOrdered - warehouse1Value  # calculates how much extra needs to be taken from the other warehouse to account for less in warehouse1
					
					#updates the warehouse 1 values
					self.warehouse1batchWeight +=  warehouse1Value * productWeight  # adds on the total weight of the items picked up from warehouse 1
					warehouse1Taken.append(0)
					
					#updates the warehouse 2 values
					warehouse2Taken.append(left + halfOrdered)  # decreases the warehouse 2 value by the half plus the carry over from warehouse 1
					self.warehouse2batchWeight +=  (left + halfOrdered) * productWeight  # adds on the total weight of the items picked up from warehouse 2
					

				# checks if there is enough available in warehouse 2 to get half of the required amount
				elif warehouse2Value < halfOrdered:
					left = halfOrdered - warehouse2Value  # calculates how much extra needs to be taken from the other warehouse to account for less in warehouse2
					
					#updates the warehouse 2 values
					self.warehouse2batchWeight +=  warehouse2Value * productWeight   # adds on the total weight of the items picked up from warehouse 2
					warehouse2Taken.append(0)  # since all the stock is taken from warehouse 2, sets the value to 0
					
					#updates the warehouse 1 values
					warehouse1Taken.append(left+ halfOrdered)  # decreases the warehouse 1 value by the half plus the carry over from warehouse 2
					self.warehouse1batchWeight +=  (left + halfOrdered) * productWeight  # adds on the total weight of the items picked up from warehouse 1
					

				# otherwise there is more than halfOrdered in both warehouses
				else:
					#updates the warehouse 1 value by taking away the halfOrdered
					warehouse1Taken.append(halfOrdered)
					self.warehouse1batchWeight += halfOrdered * productWeight  # updates the warehouse1 weight
					#updates the warehouse 1 value by taking away the halfOrdered
					warehouse2Taken.append(halfOrdered)
					self.warehouse2batchWeight += halfOrdered * productWeight  # updates the warehouse1 weight

		return warehouse1Taken,warehouse2Taken
	


		
	# updates the database with the new stock after the items to be collected by the drone have been put aside
	# inputs which warehouses will be visited as an attribute
	def updateTable(self,warehouses):
		# Connect to database file
		conn = get_connection()
		cursor = conn.cursor()
		
		cursor.execute('''SELECT numAvailable FROM stock1''')
		warehouse1Stock = cursor.fetchall()
		cursor.execute('''SELECT numAvailable FROM stock2''')
		warehouse2Stock = cursor.fetchall()

		warehouse1Taken,warehouse2Taken = self.getWarehousesNumTaken(warehouses)

		# iterates through each product
		for i in range(0,len(self.orderMenu.batchQuantities)):
			warehouse1Value = warehouse1Stock[i][0] - warehouse1Taken[i]
			warehouse2Value = warehouse2Stock[i][0] - warehouse2Taken[i]
			
			# updates the stock in warehouse 1 for that product to the new value calculated
			cursor.execute('''UPDATE stock1
						SET numAvailable = ?
						WHERE productId = ?
				''', (warehouse1Value, i+1))
			
			# updates the stock in warehouse 2 for that product to the new value calculated
			cursor.execute('''UPDATE stock2
						SET numAvailable = ?
						WHERE productId = ?
				''', (warehouse2Value, i+1))
			
		conn.commit()
	

	# fuction to start the delivery tour
	def startTour(self):	
		
		# selects and adds the orders from the orderQueue using first-fit binpacking algorithm
		def addOrdersToBatch():
			
			#establishes a connection to the database
			conn = get_connection()
			cursor = conn.cursor()

			pos = 0  # initialises the position pointer in the orderQueue to the starting value

			# repeats until it reaches the end of the queue
			while pos < len(self.orderMenu.orderQueue):
				
				#selects the order at pos and its details
				order = self.orderMenu.orderQueue[pos]
				orderId = order[0]
				weight = order[1]
				
				# checks if the order added onto all the current orders would exceed the max drone weight limit
				if self.orderMenu.batchWeight + weight < 15.9:
					# selects the orderpoint coordinates using the database and the orderid
					cursor.execute("SELECT deliveryLat, deliveryLong FROM orders WHERE orderId = ?", (order[0],))
					coords = cursor.fetchone()
			
					self.pointsToVisitLatLong.append(coords)  # adds its coordinates to the points to visit list
					self.orderMenu.batchWeight += weight  # adds its weight to the batchWeight
					self.orderMenu.orderQueue.remove(order)  # removes it from the orderQueue

					# updates the batch quantities with the order details (item quanitites)
					# iterates theough all the products
					for i in range(0,8):
						# selects the amount of the item in that order from the database
						cursor.execute("SELECT quantity FROM orderLIne WHERE orderId = ? AND productId = ?", (orderId,i+1))
						num = cursor.fetchone()[0]
						self.orderMenu.batchQuantities[i] += num  # updates the batch quantities list
						self.orderMenu.totalOrdersQuanitities[i] -= num  # updates the order quantities in the queue
					
				# otherwise, if the weight added on would be too heavy
				else:
					pos += 1  # moves the pointer to the next item in the list

		

		#uses the availability in each warehouse to determine which ones are necessary to visit
		# returns both if both necessary, either if both have all items or 1 or 2 specifically if only one
		def checkWarehousesToVisit():
			oneNeeded = False
			twoNeeded = False

			#selects the stock of each item in each warehouse
			conn = get_connection()
			cursor = conn.cursor()
			
			cursor.execute('''SELECT numAvailable FROM stock1''')
			warehouse1Numbers = cursor.fetchall()
		
			cursor.execute('''SELECT numAvailable FROM stock2''')
			warehouse2Numbers = cursor.fetchall()
			
			conn.commit()

			
			#checks each item to see which warehouse they are available in
			for i in range(0,len(self.orderMenu.batchQuantities)):
				#if quantity in batch is greater than in each warehouse needs to visit both
				if self.orderMenu.batchQuantities[i] > warehouse1Numbers[i][0] and self.orderMenu.batchQuantities[i] > warehouse2Numbers[i][0]:
					oneNeeded = True
					twoNeeded = True
				#if quantity in warehouse 2 but not in warehouse 1
				elif self.orderMenu.batchQuantities[i] > warehouse1Numbers[i][0]:
					twoNeeded = True
				#if quantity in warehouse 1 but not in warehouse 2
				elif self.orderMenu.batchQuantities[i] > warehouse2Numbers[i][0]:
					oneNeeded = True

			#if both needed returns both
			if oneNeeded and twoNeeded:
				return "both"
			#if only warehouse1 needed, returns 1
			elif oneNeeded:
				return "1"
			#if only warehouse2 needed, returns 2
			elif twoNeeded:
				return "2"
			#if neither one is necessary, returns either
			else:
				return "either"
			

		#function to check if charging needed before starting delivery cycle
		def checkChargingNeeded(trialPath, path, warehousesToVisit):
			conn = get_connection()
			cursor = conn.cursor()

			batteryNeededTrial = 0
			batteryNeeded = 0
					
			if warehousesToVisit =="either":
				self.getWarehousesNumTaken("1")

				#adds cost from last delivery point to charging station to the path costs
				payload = 0
				distWithPayload = distBetween(trialPath[-1], self.mapDisplay.chargingPointCoords) + distBetween(self.coords, trialPath[0])
				timeInDist = distWithPayload / 0.02
				timeIn100 = self.calcMaxFlightTime(payload)
				batteryTaken = 100* timeInDist / timeIn100
				batteryNeededTrial += batteryTaken
				
				for i in range(0,len(trialPath)-1):
					if trialPath[i] == self.mapDisplay.warehouse1Coords:
						payload += self.warehouse1batchWeight
					elif trialPath[i] == self.mapDisplay.warehouse2Coords:
						payload += self.warehouse2batchWeight
					else:
						cursor.execute('''SELECT orderWeight FROM orders WHERE deliveryLat = ? AND deliveryLong = ?''', (trialPath[i][0], trialPath[i][1]))
						weight = cursor.fetchone()[0]
						payload -= weight
					
					distWithPayload = distBetween(trialPath[i],trialPath[i+1])
					timeInDist = distWithPayload/0.02
					timeIn100 = self.calcMaxFlightTime(payload)
					batteryTaken = 100* timeInDist / timeIn100
					batteryNeededTrial += batteryTaken
				
				self.getWarehousesNumTaken("2")

			else:
				self.getWarehousesNumTaken(warehousesToVisit)
				
		
			payload = 0
			distWithPayload = distBetween(self.coords, path[0]) + distBetween(path[-1],self.mapDisplay.chargingPointCoords)
			timeInDist = distWithPayload / 0.02
			timeIn100 = self.calcMaxFlightTime(payload)
			batteryNeeded += 100* timeInDist / timeIn100
			
			for i in range(0,len(path)-1):
				if path[i] == self.mapDisplay.warehouse1Coords:
					payload += self.warehouse1batchWeight
				elif path[i] == self.mapDisplay.warehouse2Coords:
					payload += self.warehouse2batchWeight
				else:
					cursor.execute('''SELECT orderWeight FROM orders WHERE deliveryLat = ? AND deliveryLong = ?''', (path[i][0], path[i][1]))
					weight = cursor.fetchone()[0]
					payload -= weight
										
				distWithPayload = distBetween(path[i],path[i+1])
				timeInDist = distWithPayload/0.02
				timeIn100 = self.calcMaxFlightTime(payload)
				batteryNeeded += 100* timeInDist / timeIn100
				

			print(batteryNeeded, "batteryneeded")
			print(batteryNeededTrial, "trial battery needed")
			print(self.battery, "actual battery")
			
			
			

			if batteryNeeded <= self.battery:
				return False
			else:
				if batteryNeededTrial < self.battery and batteryNeededTrial != 0:
					return False
				else:
					return True

			

		#if there is currently a path on the map, deletes it
		if self.mapDisplay.TSPpath is not None:
			self.mapDisplay.TSPpath.delete()
			
		addOrdersToBatch()
				
		#starts off with the trial cost at a very high number
		trialCost = 1000000000000
		chargingTrialCost = 100000000000
		trialCoordinatePath = []
		warehousesToVisit = checkWarehousesToVisit()  #checks which warehouses need to be visited depending on the batch numbers
			
		# if both warehouses need to be visited
		if warehousesToVisit == "both":			
			
			#checks if warehouse 1 is closer to the current drone location
			if distBetween(self.coords, self.mapDisplay.warehouse1Coords) < distBetween(self.coords, self.mapDisplay.warehouse2Coords):
				# sets up the cycle to start with warehouse 1 and then go to warehouse 2
				warehouseCycleStartCoords = self.mapDisplay.warehouse1Coords
				self.pointsToVisitLatLong.append(self.mapDisplay.warehouse2Coords)
			# if warehouse 2 is closer to the current drone location
			else:
				# sets up the cycle to start with warehouse 1 and then go to warehouse 2
				warehouseCycleStartCoords = self.mapDisplay.warehouse2Coords
				self.pointsToVisitLatLong.append(self.mapDisplay.warehouse1Coords)

		#if only warehouse1 necessary 
		elif warehousesToVisit == "1":
			# adds warehouse 1 coordinates to the points to visit list
			self.pointsToVisitLatLong.append(self.mapDisplay.warehouse1Coords)
			warehouseCycleStartCoords = self.mapDisplay.warehouse1Coords  #starts the tour with warehouse 1
			
		#if only warehouse1 necessary
		elif warehousesToVisit == "2":
			# adds warehouse 1 coordinates to the points to visit list
			self.pointsToVisitLatLong.append(self.mapDisplay.warehouse2Coords)
			warehouseCycleStartCoords = self.mapDisplay.warehouse2Coords  #starts the tour with warehouse 2
			
		# if visiting either warehouse is possible
		else:
			# starts by setting warehouse 1 as the warehouse to visit
			self.pointsToVisitLatLong.append(self.mapDisplay.warehouse1Coords)
			warehouseCycleStartCoords = self.mapDisplay.warehouse1Coords
				
			# creates a trial graph using warehouse 1
			trial = Graph(len(self.pointsToVisitLatLong))
		
			# adds all the edges to the graph
			for u in range(0,len(self.pointsToVisitLatLong)):
				for v in range(u+1,len(self.pointsToVisitLatLong)):
					w = distBetween(self.pointsToVisitLatLong[u],self.pointsToVisitLatLong[v])
					trial.addEdge(u,v,w)
					
			# used the graph class functions to generate a trial tsp tour
			trial.generateAdjacencyMat()  #generates the adjacency matrix
			trial.KruskalMST()  # generates the minimum spanning tree using kruskals
			trial.minMatching()  # generates an off perfect minimum matching
			trial.eulerian()  #shortcuts to get a eulerian cycle

			# calculates the cost of the trial cycle
			trialCost = trial.calculateCost(trial.eulerianShortcut)
			
			# adds the coordiantes of each point in the selected path to the coordinate path
			for i in range(0,len(trial.eulerianShortcut)):
				trialCoordinatePath.append(self.pointsToVisitLatLong[trial.eulerianShortcut[i]])

			# removes warehouse 1 from the points to visit list and adds warehouse 2 instead
			self.pointsToVisitLatLong.pop()
			self.pointsToVisitLatLong.append(self.mapDisplay.warehouse2Coords)
					
			# gets the coordinate of the last delivery point
			self.lastDeliveryCoords = self.pointsToVisitLatLong[trial.eulerianShortcut[trial.vertices-1]]
			
			# calculates the trial cost if the drone charges first
			chargingTrialCost = trialCost + distBetween(self.mapDisplay.chargingPointCoords, warehouseCycleStartCoords)

			# sets up the warehouse to visit to the warehouse 2
			warehouseCycleStartCoords = self.mapDisplay.warehouse2Coords

				
		# creates a graph using the points in points to visit
		g = Graph(len(self.pointsToVisitLatLong))
		
		# adds all the edges to the graph
		for u in range(0,len(self.pointsToVisitLatLong)):
			for v in range(u+1,len(self.pointsToVisitLatLong)):
				w = distBetween(self.pointsToVisitLatLong[u],self.pointsToVisitLatLong[v])
				g.addEdge(u,v,w)
					
		# used the graph class functions to generate a trial tsp tour
		g.generateAdjacencyMat()  # generates the adjacency matrix
		g.KruskalMST()  # generates the minimum spanning tree using kruskals
		g.minMatching()  # generates an off perfect minimum matching
		g.eulerian()  # shortcuts to get a eulerian cycle
		
		# calculates the cost of the cycle
		cost = g.calculateCost(g.eulerianShortcut)
		
		# adds the coordiantes of each point in the selected path to the coordinate path
		if warehousesToVisit == "both":
			self.coordinatePath.append(warehouseCycleStartCoords)
			
		for i in range(0,len(g.eulerianShortcut)):
			self.coordinatePath.append(self.pointsToVisitLatLong[g.eulerianShortcut[i]])
			
		
		# calculates the cost if the drone charges first
		chargingCost = cost + distBetween(self.mapDisplay.chargingPointCoords, warehouseCycleStartCoords)
			
		# checks if the drone needs charging before starting the deliveries using the checkChargingNeeded function
		chargingNeeded = checkChargingNeeded(trialCoordinatePath,self.coordinatePath, warehousesToVisit)
		print("charging needed: ",chargingNeeded)
				
		# checks if the drone needs to be charged
		if chargingNeeded:
			# compares whether the trialCost with charging is less than the normal cost with charging
			if chargingTrialCost < chargingCost:
				# updates the program to use the trial cycle
				self.coordinatePath = trialCoordinatePath[:]
				# replaces warehouse 2 in the points to visit with warehouse 1
				self.pointsToVisitLatLong.pop()
				self.pointsToVisitLatLong.append(self.mapDisplay.warehouse1Coords)
		
		# if the drone doesn't need charging
		else:
			# compares whether the trialCost is less than the normal cost
			if trialCost < cost:
				# updates the program to use the trial cycle
				self.coordinatePath = trialCoordinatePath[:]
				# replaces warehouse 2 in the points to visit with warehouse 1
				self.pointsToVisitLatLong.pop()
				self.pointsToVisitLatLong.append(self.mapDisplay.warehouse1Coords)
				
					
		# if it needs to be charged, adds the charging point to the front of the list
		if chargingNeeded:
			self.coordinatePath.insert(0,self.mapDisplay.chargingPointCoords)
					
		self.mapDisplay.TSPpath = self.mapDisplay.map_widget.set_path([self.coords]+self.coordinatePath, color = '#f05118', width=2)  # draws the intended path on the map
		
				
		#updates the stock tables in the database to reflect the new availabilities
		self.updateTable(warehousesToVisit)
	
		#resets all the relevant values
		self.orderMenu.batchQuantities = [0,0,0,0,0,0,0,0]  # resets the batch quanitites
		self.orderMenu.batchWeight = 0  # resets the batchweight
		self.tourComplete = False  # flags that a tour is currently in progress
