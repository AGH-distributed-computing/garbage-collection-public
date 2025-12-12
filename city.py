import heapq
import json
from collections import deque

from command import MoveToVertice, MoveToEdge, EmptyBin
from edge import Edge
from garbageCollector import GarbageCollector
from localization import VerticeLocalization, EdgeLocalization, RubbishBinSide
from vertice import Vertice
from rubbishBin import RubbishBin


# create side array of bins basing on data from JSON
def getBinFromData(binData):
    type = binData['binType']
    if (type != "detached_house"):
        if (type == "apartment_building"):
            usersCount = binData['apartmentCount']
        elif (type == "public_facility"):
            usersCount = binData['workerCount']
        elif (type == "production_plant"):
            usersCount = binData['workerCount']
        else:
            raise ValueError("Number of users must be provided when building type is other than detached_house")
        rubbishBin = RubbishBin(
            type=type,
            capacity=binData['capacity'],
            usersCount=usersCount
        )
    else:
        rubbishBin = RubbishBin(
            type=binData['binType'],
            capacity=binData['capacity'],
            usersCount=1
        )
    return rubbishBin


class City:

    #takes string in json format and adds its commands
    def parseOrdersForTruck(self, jsonOrders):
        data = json.loads(jsonOrders)
        truckName = data.get("truckName")

        truckNumber = self.getGarbageCollectorNumberByName(truckName)

        #this line may be used to replace currently existing commands
        #self.garbage_collector_commands[truckNumber].clear()

        commands = data.get("commands", [])
        for cmd in commands:
            cmd_type = cmd.get("type")

            if cmd_type == "goToVertice":
                destination = cmd.get("destination")
                move_cmd = MoveToVertice()
                move_cmd.verticeLocalization = VerticeLocalization(self.getVerticeNumberByName(destination))
                self.garbage_collector_commands[truckNumber].append(move_cmd)

            elif cmd_type == "goToEdgePlace":
                edge = cmd.get("edge")
                distance = cmd.get("distance")
                move_cmd = MoveToEdge()
                move_cmd.edgeLocalization = EdgeLocalization(self.getEdgeNumberByName(edge), distance)
                self.garbage_collector_commands[truckNumber].append(move_cmd)

            elif cmd_type == "collectGarbage":
                side = cmd.get("side")
                empty_cmd = EmptyBin()
                empty_cmd.side = RubbishBinSide.from_string(side)
                self.garbage_collector_commands[truckNumber].append(empty_cmd)

            else:
                raise ValueError(f"Unknown command type: {cmd_type}")

        #TODO: add checking garbage_collector_commands[truckNumber]


    def getGarbageCollectorByName(self, name):
        for garbageCollector in self.garbage_collectors:
            if(garbageCollector.name == name):
                return garbageCollector
        return None

    def getGarbageCollectorNumberByName(self, name):
        for idx, garbageCollector in enumerate(self.garbage_collectors):
            if (garbageCollector.name == name):
                return idx
        return None

    def getVerticeByName(self, name):
        for vertice in self.vertices:
            if(vertice.name == name):
                return vertice
        return None

    # returns True if bin was emptied
    def emptyBin(self, rubbishBin, binLocalization, garbageCollectorName):
        garbageCollector = self.getGarbageCollectorByName(garbageCollectorName)
        if garbageCollector is None:
            raise ValueError(f"Garbage collector with name {garbageCollectorName} not found!")

        if (isinstance(garbageCollector.localization, EdgeLocalization)):
            if (garbageCollector.localization == binLocalization):
                garbageLitres = rubbishBin.fillLevel
                if (garbageCollector.canCollectGarbage(garbageLitres)):
                    garbageCollector.collectGarbage(garbageLitres)
                    rubbishBin.emptyBin()
                    return True
        return False

    def getVerticeNumberByName(self, verticeName):
        return self.vertice_name_to_index[verticeName]

    def getEdgeNumberByName(self, edgeName):
        for idx, edge in enumerate(self.edges):
            if edge.name == edgeName:
                return idx
        return None

    def __init__(self, topographyFilePath, carFilePath, verbose=False):
        self.verbose = verbose
        # Load JSON data
        try:
            with open(topographyFilePath, 'r', encoding='utf-8') as f:
                topo_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{topographyFilePath}' not found.")
            raise
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in file '{topographyFilePath}'.")
            print(f"Details: {e}")
            raise

        # Initialize lists
        self.vertices = []
        self.edges = []
        self.map = []
        self.garbage_dumps = set()

        # Create vertices list and name-to-index mapping
        self.vertice_name_to_index = {}
        for idx, (name, vertice_data) in enumerate(topo_data['vertices'].items()):
            vertice = Vertice(
                name=name,
                xCoord=vertice_data['xCoord'],
                yCoord=vertice_data['yCoord'],
                isGarbageDump=vertice_data['isGarbageDump']
            )
            self.vertices.append(vertice)
            if(vertice.isGarbageDump):
                self.garbage_dumps.add(idx)
            self.vertice_name_to_index[name] = idx

        # Initialize adjacency list (one list per vertice)
        self.map = [[] for _ in range(len(self.vertices))]

        # Create edges list and populate adjacency list
        for idx, (name, edge_data) in enumerate(topo_data['edges'].items()):
            rightSideBins = {}
            leftSideBins = {}

            for bin_data in edge_data.get('rightSideBins', []):
                location = bin_data['location']
                rightSideBins[location] = getBinFromData(bin_data)

            for bin_data in edge_data.get('leftSideBins', []):
                location = bin_data['location']
                leftSideBins[location] = getBinFromData(bin_data)

            edge = Edge(
                name=name,
                length=edge_data['length'],
                isOneWay=edge_data['isOneWay'],
                isCollectingBothSidesAllowed=edge_data['isCollectingBothSidesAllowed'],
                firstVertice=edge_data['firstVertice'],
                secondVertice=edge_data['secondVertice'],
                trafficType=edge_data['trafficType'],
                trafficIntensity=edge_data['trafficIntensity'],
                rightSideBins=rightSideBins,
                leftSideBins=leftSideBins
            )
            self.edges.append(edge)

            # Get vertex indices
            first_idx = self.getVerticeNumberByName(edge_data['firstVertice'])
            second_idx = self.getVerticeNumberByName(edge_data['secondVertice'])

            # Add edge to adjacency list
            self.map[first_idx].append((second_idx, idx))

            # If not one-way, also add connection from second to first
            if not edge_data['isOneWay']:
                self.map[second_idx].append((first_idx, idx))

        try:
            with open(carFilePath, 'r', encoding='utf-8') as f:
                truck_data_json = json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{carFilePath}' not found.")
            raise
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in file '{carFilePath}'.")
            print(f"Details: {e}")
            raise

        self.garbage_collectors = []
        self.garbage_collector_commands = []

        for truck_name, truck_data in truck_data_json['trucks'].items():
            # Determine localization type
            if 'verticeLocalization' in truck_data:
                verticeNumber = self.getVerticeNumberByName(truck_data['verticeLocalization'])
                if verticeNumber is None:
                    raise ValueError(f"Vertex '{truck_data['verticeLocalization']}' not found for truck {truck_name}")
                localization = VerticeLocalization(verticeNumber)
            elif 'edgeLocalization' in truck_data:
                edge_loc = truck_data['edgeLocalization']
                edgeNumber = self.getEdgeNumberByName(edge_loc['edgeName'])
                if edgeNumber is None:
                    raise ValueError(f"Edge '{edge_loc['edgeName']}' not found for truck {truck_name}")
                distanceFromStart = edge_loc['distanceFromStart']
                if distanceFromStart > self.edges[edgeNumber].length:
                    raise ValueError(f"Truck's location {truck_name} cannot exceed street length")
                localization = EdgeLocalization(
                    edgeNumber,
                    distanceFromStart
                )
            else:
                raise ValueError(f"Truck {truck_name} does not have verticeLocalization or edgeLocalization")
            self.garbage_collector_commands.append(deque())

            gc = GarbageCollector(
                name=truck_name,
                localization=localization,
                fuelTankCapacity=truck_data['fuelTankCapacity'],
                fuelLevel=truck_data['fuelLevel'],
                capacity=truck_data['capacity'],
                crushingEfficiency=truck_data['crushingEfficiency'],
                fuelConsumption=truck_data['fuelConsumption'],
                timeSinceStart=truck_data.get('timeSinceStart', 0),
                garbageLevel=truck_data.get('garbageLevel', 0)
            )

            self.garbage_collectors.append(gc)

    #Allows to retrieve Bin having edge
    def getBinFromEdge(self, edge, distance, side):
        if(side=="left"):
            if(distance in edge.leftSideBins):
                return edge.leftSideBins[distance]
            else:
                print(f"Left side bin on distance: {distance} does not exist")
                return None
        elif(side=="right"):
            if(distance in edge.rightSideBins):
                return edge.rightSideBins[distance]
            else:
                print(f"Right side bin on distance: {distance} does not exist")
                return None
        else:
            print("Side must be either left or right")
            return None

    # this function simulates one step in time according to rubbish generation
    # it needs four time series types as arrays
    # current_time, time_series and tick duration given in minutes
    def updateRubbish(self,
                      detached_house_time_series,
                      apartment_building_time_series,
                      public_facility_time_series,
                      production_plant_time_series,
                      time_series_duration,
                      tick_duration,
                      current_time
                      ):
        series_index = (current_time % time_series_duration) // tick_duration
        for edge in self.edges:
            for rubbishBin in edge.rightSideBins.values():
                rubbishBin.updateRubbish(
                    detached_house_time_series,
                    apartment_building_time_series,
                    public_facility_time_series,
                    production_plant_time_series,
                    series_index
                )
            for rubbishBin in edge.leftSideBins.values():
                rubbishBin.updateRubbish(
                    detached_house_time_series,
                    apartment_building_time_series,
                    public_facility_time_series,
                    production_plant_time_series,
                    series_index
                )

    def decreaseAllFuel(self, minutes):
        for garbage_collector in self.garbage_collectors:
            garbage_collector.consumeFuel(minutes)

    #returns edge number that leads from source to destination
    def findEdgeNumberToReachVertice(self, sourceVertice, destinationVertice):
        if(sourceVertice < 0 or sourceVertice >= len(self.map)):
            print(f"Vertice with number '{sourceVertice}' not found.")
            return None
        if destinationVertice < 0 or destinationVertice >= len(self.vertices):
            print("Destination vertice does not exist")
            return None
        for (verticeNumber, edgeNumber) in self.map[sourceVertice]:
            if(verticeNumber == destinationVertice):
                return edgeNumber
        print(f"Edge connecting '{sourceVertice}' and '{destinationVertice}' not found.")
        return None

    def printLocalization(self, garbageCollector):
        if(self.verbose):
            print(f"Vehicle: '{garbageCollector.name}' is now at:")
            if(isinstance(garbageCollector.localization, VerticeLocalization)):
                print(f"intersection: '{self.vertices[garbageCollector.localization.verticeNumber].name}'")
            elif(isinstance(garbageCollector.localization, EdgeLocalization)):
                print(f"street: '{self.edges[garbageCollector.localization.edgeNumber].name}' on meter: '{garbageCollector.localization.distanceFromStart}'")

    def setTruckToTravelFromVerticeToVertice(self, garbageCollector, destinationVertice):
        if isinstance(garbageCollector.localization, VerticeLocalization):
            currentVertice = garbageCollector.localization.verticeNumber
            edgeNumber = self.findEdgeNumberToReachVertice(currentVertice, destinationVertice)
            garbageCollector.localization = EdgeLocalization(edgeNumber, 0)
        else:
            print("Function can be used only when truck is in vertice!")
#speed in kilometers per hour, duration and emptyBinDuration
    def executeOrders(self, speed, tickDuration, emptyBinDuration):
        timeList = []
        for i in range (0, len(self.garbage_collectors)):
            if self.garbage_collector_commands[i]:
                timeList.append((i, tickDuration))
        heap = [(-timeLeft, truck) for truck, timeLeft in timeList]
        heapq.heapify(heap)

        while heap:
            neg_timeLeft, truck = heapq.heappop(heap)
            timeLeft = -neg_timeLeft
            if timeLeft <= 0:
                break

            #tu wykonac pojedynczy ruch z poczatku kolejki
            #co jesli zostanie troche czasu, ale tyle, ze nie da sie zaladowac kosza, wtedy timeLeft nie bedzie zerem, a jakas wielkoscia
            #mozna wprowadzic funkcje, ktora sprawdza, czy dana smieciarka moze jeszcze cokolwiek zrobic i jesli nie, to usuwamy ja z kolejki
            #typu canExecuteOrder
            #w zasadzie problem jest tylko ze smieciami (bo jazda zawsze powinna wyzerować) wiec mozna dorobic if time < emptyBinDuration and nextOrder ==emptyBin
            garbageCollector = self.garbage_collectors[truck]
            if(self.garbage_collector_commands[truck].__len__() == 0):
                continue
            command = self.garbage_collector_commands[truck].popleft()
            usedTime = 0

            self.printLocalization(garbageCollector)

            #change garbage collecting check if there is a bin at current location and if is, collecting it instead of requiring location
            if(isinstance(command, EmptyBin)):
                if (timeLeft >= emptyBinDuration):  # if there's no time left for emptying the bin, we cannot do it
                    bin = self.getBinFromEdge(self.edges[garbageCollector.localization.edgeNumber], garbageCollector.localization.distanceFromStart, command.side)
                    if bin is None:
                        print(f"WARNING: No bin found at location")
                    else:
                        if(garbageCollector.canCollectGarbage(bin.fillLevel)):
                            garbageCollector.collectGarbage(bin.fillLevel)
                            bin.emptyBin()
                            usedTime += emptyBinDuration
                            if(self.verbose):
                                print(
                                    f"Garbage collector: '{garbageCollector.name}' collected '{bin.fillLevel} litres of garbage'.")
                            timeLeft -= usedTime
                            heapq.heappush(heap, (-timeLeft, truck))
                        else:
                            print(f"Garbage collector: '{garbageCollector.name}' is full and could not collect additional garbage.")
                else:
                    #instead of postponing emptying the bin we should be able to divide it between two ticks
                    self.garbage_collector_commands[truck].appendleft(command)
            else:
                if(self.verbose):
                    print(f"Garbage collector: '{garbageCollector.name}' travelling")
                #drive method from GarbageCollector has no idea about graph structure, so we place truck on point 0 on appropriate edge
                if(isinstance(garbageCollector.localization, VerticeLocalization) and isinstance(command, MoveToVertice)):
                    targetVertice = command.verticeLocalization.verticeNumber
                    currentVertice = garbageCollector.localization.verticeNumber
                    edgeNumber = self.findEdgeNumberToReachVertice(currentVertice, targetVertice)
                    #if truck travels in the opposite direction than distance incrementing, we need to start with full distance
                    if(currentVertice == self.edges[edgeNumber].secondVertice):
                        isTravelDirectionInversed = True
                        garbageCollector.localization = EdgeLocalization(edgeNumber, 0)
                    else:
                        isTravelDirectionInversed = False
                        garbageCollector.localization = EdgeLocalization(edgeNumber, self.edges[edgeNumber].length
                                                                         )
                    garbageCollector.setTargetLocalization(command.verticeLocalization)
                    usedTime = garbageCollector.drive(speed, tickDuration, self.edges[edgeNumber].length, self.garbage_dumps, isTravelDirectionInversed)

                elif(isinstance(garbageCollector.localization, VerticeLocalization) and isinstance(command, MoveToEdge)):
                    currentVertice = garbageCollector.localization.verticeNumber
                    # targetVertice is the vertice at which points direction of travel
                    if(currentVertice == self.getVerticeNumberByName(self.edges[command.edgeLocalization.edgeNumber].secondVertice)):
                        targetVertice = self.getVerticeNumberByName(self.edges[command.edgeLocalization.edgeNumber].firstVertice)
                        distance = self.edges[command.edgeLocalization.edgeNumber].length
                        isTravelDirectionInversed = True
                    else:
                        targetVertice = self.getVerticeNumberByName(self.edges[command.edgeLocalization.edgeNumber].secondVertice)
                        distance = 0
                        isTravelDirectionInversed = False
                    edgeNumber = self.findEdgeNumberToReachVertice(currentVertice, targetVertice)
                    garbageCollector.localization = EdgeLocalization(edgeNumber, distance)
                    garbageCollector.setTargetLocalization(command.edgeLocalization)
                    usedTime = garbageCollector.drive(speed, tickDuration,
                                                      self.edges[garbageCollector.localization.edgeNumber].length,
                                                      self.garbage_dumps,
                                                      isTravelDirectionInversed)

                elif(isinstance(garbageCollector.localization, EdgeLocalization) and isinstance(command, MoveToEdge)):
                    #maybe it should be cheked if both edges are the same
                    garbageCollector.setTargetLocalization(command.edgeLocalization)
                    if(garbageCollector.localization.distanceFromStart < command.edgeLocalization.distanceFromStart):
                        isTravelDirectionInversed = False
                    else:
                        isTravelDirectionInversed = True
                    usedTime = garbageCollector.drive(speed, tickDuration, self.edges[garbageCollector.localization.edgeNumber].length, self.garbage_dumps, isTravelDirectionInversed)

                elif(isinstance(garbageCollector.localization, EdgeLocalization) and isinstance(command, MoveToVertice)):
                    #if command.verticeLocalization is firstVertice of current edge, then set isTravelDirectionInversed = True
                    currentEdge = self.edges[garbageCollector.localization.edgeNumber]
                    if(self.vertices[command.verticeLocalization.verticeNumber].name == currentEdge.firstVertice):
                        isTravelDirectionInversed = True
                    elif(self.vertices[command.verticeLocalization.verticeNumber].name == currentEdge.secondVertice):
                        isTravelDirectionInversed = False
                    else:
                        print(
                            f"Vertice: '{self.vertices[command.verticeLocalization.verticeNumber].name}' cannot be rached directly from edge: '{self.edges[garbageCollector.localization.edgeNumber].name}'")
                    garbageCollector.setTargetLocalization(command.verticeLocalization)
                    usedTime = garbageCollector.drive(speed, tickDuration, self.edges[garbageCollector.localization.edgeNumber].length, self.garbage_dumps, isTravelDirectionInversed)

                self.printLocalization(garbageCollector)
                timeLeft -= usedTime
                heapq.heappush(heap, (-timeLeft, truck))



    #function returning bin by localization and side of the road, binLocalization is an instance of EdgeLocalization class
    def getBinByLocalization(self, binLocalization, binSide):
        if(isinstance(binLocalization, EdgeLocalization)):
            edgeNumber = binLocalization.edgeNumber
            #poszukac kosza o odleglosci i go zwrocic
            return self.getBinFromEdge(self.edges[edgeNumber], binLocalization.distanceFromStart, binSide)
        else:
            print("Localization of the bin must be of EdgeLocalization type")

#Allow to plan journey to point on edge
#distance parameter is the distance from sorce vertice
#    def OrderTruckMovementToEdge(self, garbageCollectorName, edgeName, distance)
        #jezeli truck jest w wierzcholku, pamietac zmienic na zerowa odleglosc na krawedzi wchodzacej do wierzcholka docelowego

