import random


# class to represent the graph of all the points to visit
# performs various graph algorithms (christofides)
class Graph: 

	#initialises graph
	def __init__(self,v):
		self.graph = []
		self.vertices = v   #represents the number of vertices in the graph

	# Function to add an edge to graph 
	def addEdge(self, u, v, w):
		self.graph.append([u,v,w]) #u is the starting vertex, v is the end vertex and w is the weight (distance between them)
		
	#generates adjacency matrix
	def generateAdjacencyMat(self):
		self.adjacencyMat = [[0 for x in range(self.vertices)] for y in range(self.vertices)]
		for u,v,w in self.graph:
			self.adjacencyMat[u][v] = w
			self.adjacencyMat[v][u] = w 
		

	# Function to construct MST using Kruskal's algorithm 
	def KruskalMST(self): 

	   # function to merge 2 lists in order
		def merge(list1,list2,pos):
			new = []
			index1 = 0
			index2 = 0
			while index1 <len(list1) and index2<len(list2): #while it hasn't reached the end of either list
				#compares the first value in both lists and adds the smaller one
				if list1[index1][pos] > list2[index2][pos]:
					new.append(list2[index2])
					index2 += 1
				elif list1[index1][pos] < list2[index2][pos]:
					new.append(list1[index1])
					index1 += 1
				#if equal adds both
				else:
					new.append(list1[index1])
					index1 += 1
					new.append(list2[index2])
					index2 += 1
			#checks if it has reached the end of both lists, and adds any items left in the list
			if index1 < len(list1):
				for i in range(index1,len(list1)):
					new.append(list1[i])
			elif index2 < len(list2):
				for i in range(index2,len(list2)):
					new.append(list2[i])
			return new

		# mergeSort function
		def mergeSort(items,pos):
			sortedList = []
			for i in range(0,len(items)):
				sortedList.append([items[i]]) #splits each item into its own individual list
			while len(sortedList) > 1: #while there is still more than one list in sortedList
				index = 0
				while index < len(sortedList)-1:
					new = merge(sortedList[index], sortedList[index+1], pos) #merges the two lists together in increasing order based on the value at index pos in each list
					#replaces the two lists by the new sorted one
					sortedList[index] = new
					index += 1
					sortedList.pop(index)
			return sortedList[0]

		#does depth first search to check if already visited node so cycle
		def dfs(adj,v,visited,prev):
			found = False
			visited[v] = True
			# explores all the neighbors of v
			for i in adj[v]:
				#if not already visited calls recursively to explore that node
				if visited[i[0]]==False:
					if dfs(adj,i[0],visited,v):
						found = True
				# if already visited and not previous one, cyclf found
				elif i[0]!=prev:
					found = True
			return found
				
		# called to check if cycle present in MST so far (when called u is 0)
		def isCycle(adj,vertices,u):
			visited=[]
			for x in range(vertices):
				visited.append(False)
			# calls dfs with u (0) as current node and -1 as previous
			return dfs(adj,u,visited,-1)

		# sorts edges in graph using mergesort based on 2nd element in edge (u,v,w)
		self.graph = mergeSort(self.graph,2)
		
		# initialises empty 2d array
		self.minSpanTree = [[] for i in range(self.vertices)]


		edgeCount = 0
		pos = 0  # the index of the current edge in the graph
		# repeats until sufficient edges or reach end of self.graph
		while edgeCount < self.vertices-1 and pos < len(self.graph):
			edge= self.graph[pos]
			u,v,w = edge
			pos +=1
			# adds edge at pos to MST
			self.minSpanTree[u].append((v,w))
			self.minSpanTree[v].append((u,w))
			
			# if cycle formed, removed edge
			if isCycle(self.minSpanTree,self.vertices,u):
				self.minSpanTree[u].remove((v,w))
				self.minSpanTree[v].remove((u,w))
			else:
				edgeCount += 1
				
				
			   

	# generates perfect minimum matching between the odd vertices in MST         
	def minMatching(self):
		
		# geneerates list of odd nodes from MST
		def oddVertex():
			odd = []
			for nodeNum in range(0,self.vertices):
				if len(self.minSpanTree[nodeNum]) % 2 == 1:
					odd.append(nodeNum)
			return odd
  
		
		# recursive function to get min weight perfect matching
		def minMatchRecursive(odd,adj,cost,matching):
			
			#base case for when only 2 odd vertices left
			if len(odd) == 2:
				return (cost + adj[odd[0]][odd[1]]), [[odd[0],odd[1],adj[odd[0]][odd[1]]]]

			#sets the inital match cost as a very large number
			matchCost = 1000000000
			bestMatch = []
			
			# tries all possible combinations of odd vertices
			for posU in range(0,len(odd)-1):
				u = odd[posU]
		
				for posV in range(posU+1,len(odd)):
					v = odd[posV]
					# creates new odd list without paired vertices
					newOdd = odd[:]
					newOdd.pop(posU)
					newOdd.pop(posV -1)
					
					# recursive call to get min matching for new odd list
					newCost, newMatch = minMatchRecursive(newOdd, adj, cost + adj[u][v], matching[:])
					# if better than current best cost, replaces it
					if newCost < matchCost:
						matchCost = newCost
						bestMatch = newMatch + [[u,v,adj[u][v]]]
			
			# adds best matching to final matching
			matching.extend(bestMatch)
			return matchCost, matching
				   

		odd = oddVertex() #finds all the odd vertices in graph 
		self.matchingCost, self.minWeightMatching = minMatchRecursive(odd,self.adjacencyMat, 0, []) 
		

	# finds and shortcuts the eulerian tour of the graph 
	def eulerian(self):
		
		# Function to find the Eulerian cycle in graph
		def findEulerian(graph):
			
			def findCycle(start):
				cycle = [] 
				stack = [start]  # Stack keeps track of current path traversal
				while stack:
					#checks if the top element in the stack has adjacent vertices
					u = stack[-1]  
					if graph[u]:
						#traverses along on the of the edges from that node and removes the edge
						v = graph[u].pop()
						graph[v].remove(u)
						stack.append(v)  #adds that node to the top of the stack and repeats process
					else:
						cycle.append(stack.pop())  # If no more neighbors, add to cycle
				return cycle  # Return the found cycle

			# Find a starting vertex with edges remaining
			start_vertex = next(vertex for vertex in graph if graph[vertex])
			cycle = findCycle(start_vertex)  # Find Eulerian cycle from the start vertex
			return cycle
	
		# Dictionary to store the combined graph (Minimum Spanning Tree + Minimum Weight Matching)
		combined = {}
	
		# Constructing the combined graph from minSpanTree and minWeightMatching
		for node in range(0, self.vertices):
			connections = []  # Stores edges for the current node
			for i in self.minSpanTree[node]:  # Add edges from minimum spanning tree
				connections.append(i[0])
			for edge in self.minWeightMatching:  # Add edges from minimum weight matching
				if edge[0] == node:
					connections.append(edge[1])
				elif edge[1] == node:
					connections.append(edge[0])
			combined[node] = connections  # Store connections in the combined graph
	
		# Find the Eulerian cycle in the combined graph
		self.eulerianCycle = findEulerian(combined)
	
		# Create an Eulerian shortcut (removing duplicate visits to nodes)
		self.eulerianShortcut = []
		for node in self.eulerianCycle:
			if node not in self.eulerianShortcut:  # Checks if node has already been visited in cycle
				self.eulerianShortcut.append(node)

		self.routeOptimisation() #does route optimisation

		#checks if the point at the front of the eulerian cycle is the warehouse
		while self.eulerianShortcut[0] != (self.vertices -1):
			#if not it acts like a circular queue moving all the items to the back until the warehouse is at the front
			self.eulerianShortcut.append(self.eulerianShortcut[0])
			self.eulerianShortcut.pop(0)


	#does random swapping algorithm to improve the solution
	def routeOptimisation(self):
		cost = self.calculateCost(self.eulerianShortcut)

		#repeats random swapping 5 times
		for i in range(0,5):
			
			eulerianChanged = self.eulerianShortcut[:]
			#randomly chooses 2 nodes in the cycle
			pos1 = random.randint(0,len(eulerianChanged)-1)
			pos2 = random.randint(0,len(eulerianChanged)-1)
			temp = eulerianChanged[pos2]
			eulerianChanged[pos2] = eulerianChanged[pos1]
			eulerianChanged[pos1] = temp

			#checks if t he new cost is lower than the old cost
			newCost = self.calculateCost(eulerianChanged)

			
			#checks if the new cost is lower than the old cost
			if newCost < cost:
				self.eulerianShortcut = eulerianChanged[:]
				cost = newCost
			


	# Calculates the cost of the current cycle    
	def calculateCost(self,cycle):
		
		self.cycleCost = 0
		# iterates through cycle and adds the corresponding weight from adjacency matrix
		for i in range(1,len(cycle)):
			self.cycleCost += self.adjacencyMat[cycle[i-1]][cycle[i]]
			
		return self.cycleCost 