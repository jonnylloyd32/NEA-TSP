import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import networkx as nx
from abc import ABC, abstractmethod
from itertools import permutations
import math
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
        plt.show()

        
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

 
        unvisited.remove(nearest)
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

        return route
        #return cities


class twoOpt(tspSolver):

    def solve(self, cities):
        print("Running two opt heuristic solver")
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

        return route


#brute force solver class
class BruteForce(tspSolver):
    def solve(self, cities):
        print("running Brute Force")
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




        print(f"shortest distance calculated: {bestDistance}")
        return bestRoute


#dikjstras solver class
class Dijkstras(tspSolver):
    def solve(self, cities):
        print("running Dijkstras Algorithm")
        return cities
        

class TSP:

    def __init__(self, strategy):
        self.strategy = strategy

    def solve(self, cities):
        return self.strategy.solve(cities)

algorithmChoice = int(input("what algorithm woudl you like to choose: \n 1) Nearest Neighbour. \n 2) Brute Force. \n 3) Dijkstras. \n 4) Two Opt heuristic. \n "))
#algorithmChoice = 1
if algorithmChoice == 1:
    solver = TSP(NN())
elif algorithmChoice == 2:
    solver = TSP(BruteForce())
elif algorithmChoice == 3:
    solver = TSP(Dijkstras())
elif algorithmChoice == 4:
    solver = TSP(twoOpt())


route = solver.solve(cities)

#plots the graph itself
plotter = Plotter(route)
plotter.drawGraph()




