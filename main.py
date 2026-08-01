import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
#import networkx as nx
import time
import numpy as np
import math
from abc import ABC, abstractmethod
from itertools import permutations
from itertools import combinations

#print(nx.__version__)


#creates the city class and give each object x and y coordinate parameters
class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y


    #calculates the distance to the next city according to the algorithm
    def distanceTo(self, next):
        actualDist = math.sqrt((self.x - next.x)**2 + (self.y - next.y)**2)
        return actualDist

    def __repr__(self):
        return f"City({self.x}, {self.y})"



def RouteDistanceCalc(route):
    distance = 0

    for i in range(len(route)):
        current = route[i]
        nextCity = route[(i+1) % len(route)]

        distance += current.distanceTo(nextCity)

    return distance


#the function to load the cities from the given filename
def loadCities(filename):
    cities = []

#error handling

    try:
        with open(filename) as file:
            for line in file:
                x, y = map(int, line.strip().split(","))
                cities.append(City(x, y))
                
#checks if the file name is available and calls this 
    except FileNotFoundError:
        raise Exception("Check if the file is added to the folder correctly or if you miss-spelt it") 

#checks if the file has the correct format to read
    except ValueError:
        raise Exception("coordinates in the file must be in the form x,y") 
    return cities

#gets the name of the file to read
#coord_file = input("Enter the name of the file you wnat to solve for:")
coord_file = "Coords.txt"
#actually does the loading
cities = loadCities(coord_file)

class Plotter:
    def __init__(self, cities):
        self.cities = cities

    def drawGraph(self):
        plt.ylim(-90, 90)
        plt.xlim(-180, 180)


        #loads the map image file
        img = plt.imread("Equirectangular.jpg")

        #creates a list of xand y coordinates from each city object
        xCoords = [city.x for city in self.cities]
        yCoords = [city.y for city in self.cities]

        #puts the map background in the correct place
        plt.imshow(img, extent=[-180, 180, -90, 90])

        #actually plots the points using the coord list from above assigning values to the points
        plt.scatter(xCoords, yCoords, color = "black", s = 10)


        #plots the number of the city in order of reading from the file
        for i in range(len(self.cities)):
            plt.text(xCoords[i], yCoords[i], str(i), color = "red")

        #draws the route
        xCoords.append(self.cities[0].x)
        yCoords.append(self.cities[0].y)
        plt.plot(xCoords, yCoords, color="white")
        

        
        #handles the values and labels on the graph that never change
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.title("TSP Cities")
        plt.axis("equal")    
        plt.grid(True)
        plt.show()


class tspSolver(ABC):
    #abstracty method to define the contract for the algorithms to abide by 
    #ensures that every method must solve
    @abstractmethod
    def solve (self, cities):
        pass




#nearest naighbour solver class
class NN(tspSolver):
    
    
    def solve(self, cities):
        
        totalDistance = 0
        print("running nearest neighbour")
        route = []
        #creates a copy of the list of cities and stores it as unvisited

        unvisited = cities.copy()
        #print(f"list of cities + coords i am going to explore: {unvisited}")
        current = unvisited.pop(0)

        route.append(current)

        if len(unvisited) == 0:
            return route
        else:
            nearest = unvisited[0]

 
        #unvisited.remove(nearest)
        #checks if they have all been visited yet and continues if there are still some cities that are yet to be visited
        while len(unvisited) > 0:
            nearest = unvisited[0]

            #loops through the list of all unvisited cities
            for city in unvisited:
                #if the distance to the current city is less than distance to the 
                if current.distanceTo(city) < current.distanceTo(nearest):
                    nearest = city

            previous = current
            current = nearest

            route.append(current)
            unvisited.remove(current)

            totalDistance += previous.distanceTo(current)
            print(current)

        totalDistance += current.distanceTo(route[0])    
        print (f"this routes total distance is: {totalDistance}")
        
        
        print(route)
        return route
        #return cities


class twoOpt(tspSolver):

   
    def solve(self, cities):
        
        
        route = NN().solve(cities)
        improved = True 

        #while the routes efficiency is still being improved
        while improved:
            improved = False


            optimal = RouteDistanceCalc(route)
         

            #logic of despair and agony
            #loops through the list of cities in a loop
            #the -2 here is necessary to leave enough room for th j variable to be at least 2 values ahead of it in the list
            #if it was only 1 value ahead it wouldnt make a great difference in the route
            #i chooses where the reversed section ends and j chooses where it starts
            #flipping wasteman

            for i in range(1, len(route)-2):

                for j in range(i+1, len(route)):
                    #need to reverse the section between i and j
                    newRoute = (route[:i] + route[i:j][::-1] + route[j:])


                    newDistance = RouteDistanceCalc(newRoute)

                    #checks if the new distance is better than the "optimal" distance
                    if newDistance < optimal:
                        route = newRoute
                        optimal = newDistance
                        improved = True
                    
                    

        print("Improved distance:", RouteDistanceCalc(route))
        
        
       
        print(route)
        return route


#brute force solver class
class BruteForce(tspSolver):

    
    def solve(self, cities):
        if len(cities) > 12:
            print("WARNING: MANY NODES PRESENT WILL TAKE GAES")
        
        
        print(cities)
        #loads it as infinity because we are lookiong for the smallest value so we start checking from the biggest value
        bestDistance = math.inf
        bestRoute = []

        unvisited = cities.copy()
        

        print(f"list of cities + coords i am going to explore: {unvisited}")

        startCity = unvisited.pop(0)
        print(f"Starting city: {startCity}")
        print(f"Remaining cities: {unvisited}")

        #generates every possible order of the unvisitd cities left
        for permutation in permutations(unvisited):
            #adds the start city to the end of the now list of every combination (was a tuple before the "list" conversion)
            currentRoute = [startCity] + list(permutation)
            currentDistance = RouteDistanceCalc(currentRoute)

            if currentDistance < bestDistance:
                bestDistance = currentDistance
                bestRoute = currentRoute



        totalDistance = bestDistance
        print(f"shortest distance calculated: {bestDistance}")
        

       
        

        return bestRoute


#HeldKarp solver class
#please dont ask me to explain any of this dude, im talking to you Joe!
#OR ELSE... *ominous music plays*
#its actually given my brain aids
class HeldKarp(tspSolver):
    def solve(self, cities):
        #number of cities in the path
        numCities = len(cities)


        #this bastard creates a matrix using the number of cities, at the time its 12, so it creates a 12 X 12  2D matrix an dfills it in with 0's
        dist = np.zeros((numCities, numCities), dtype=float)
        #print(dist)


        #fills in the matrix with the distanceTo method essentially calculating the distance to each node from the starting point
        for i in range (numCities):
            for j in range (numCities):
                dist[i][j] = cities[i].distanceTo(cities[j])

        #print(dist)

        #two dictionaries
        #dp is shortest distance knonwn for a route
        #it is a subset of visited cites and the current city


        # p[arent is the previous city
        #

        #
        dp = {}
        parent = {}
        for i in range(1, numCities):
            subset = frozenset([0, i])

            dp[(subset, i)] = dist[0][i]

            parent[(subset, i)] = 0
        #print("dp:", dp)
        #print("parent:", parent)
        #print("number of cities:", numCities)
       
        for subset_size in range(3, numCities + 1):
            for subset in combinations(range(numCities), subset_size):
                if 0 not in subset:
                    continue

                subset = frozenset(subset)

                for j in subset:
                    if j == 0:
                        continue

                    #
                    best_cost = float('inf')
                    best_parent = None

                    prev_subset = subset - {j}

                    for i in prev_subset:
                        if i == 0:
                            continue

                        cost = dp[(prev_subset, i)] + dist[i][j]
                        if cost < best_cost:
                            best_cost = cost
                            best_parent = i

                    dp[(subset, j)] = best_cost
                    parent[(subset, j)] = best_parent

        all_cities = frozenset(range(numCities))

        best_cost = float('inf')
        best_last_city = None

        for j in range(1, numCities):
            cost = dp[(all_cities, j)] + dist[j][0]
            if cost < best_cost:
                best_cost = cost
                best_last_city = j

        path = []

        subset = all_cities
        last = best_last_city

        while last != 0:
            path.append(last)
            last = parent[(subset, last)]
            subset = subset - {path[-1]}

        path.append(0)

        path.reverse()
        path.append(0)



        myRoute = [cities[i] for i in path]


        totalDist = RouteDistanceCalc(myRoute)
        print(totalDist)
        return myRoute
        

class TSP:

    def __init__(self, strategy):
        self.strategy = strategy

    def solve(self, cities):
        return self.strategy.solve(cities)

try:
    algorithmChoice = int(input("what algorithm woudl you like to choose: \n 1) Nearest Neighbour. \n 2) Brute Force. \n 3) Two Opt heuristic. \n 4) Held Karp algorithm. \n"))
except ValueError:
    raise Exception("Please enter a number")

#algorithmChoice = 1

if algorithmChoice == 1:
    timeStart = time.perf_counter()
    print("running nearest neighbour")
    solver = TSP(NN())
    timeEnd = time.perf_counter()
    print(f"Runtime: {timeEnd - timeStart:.6f} seconds")


elif algorithmChoice == 2:

    print("running Brute Force algorithm")
    solver = TSP(BruteForce())



elif algorithmChoice == 3:

    print("running two opt heuristic")
    solver = TSP(twoOpt())



elif algorithmChoice == 4:
    
    print("running Held Karp's")
    solver = TSP(HeldKarp())
    

timeStart = time.perf_counter()
route = solver.solve(cities)
timeEnd = time.perf_counter()
print(f"Runtime: {timeEnd - timeStart:.6f} seconds")
#plots the graph itself
plotter = Plotter(route)
plotter.drawGraph()




