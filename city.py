import json
from gc import garbage

from edge import Edge
from garbageCollector import GarbageCollector
from localization import VerticeLocalization, EdgeLocalization
from vertice import Vertice
from rubbishBin import RubbishBin


# create side array of bins basing on data from JSON
def getBinFromData(binData):
    location = binData['location']
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

    def getGarbageCollectorByName(self, name):
        for garbageCollector in self.garbage_collectors:
            if(garbageCollector.name == name):
                return garbageCollector
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
        for idx, vertice in enumerate(self.vertices):
            if vertice.name == verticeName:
                return idx
        return None

    def getEdgeNumberByName(self, edgeName):
        for idx, edge in enumerate(self.edges):
            if edge.name == edgeName:
                return idx
        return None

    def __init__(self, topographyFilePath, carFilePath):
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

        # Create vertices list and name-to-index mapping
        vertice_name_to_index = {}
        for idx, (name, vertice_data) in enumerate(topo_data['vertices'].items()):
            vertice = Vertice(
                name=name,
                xCoord=vertice_data['xCoord'],
                yCoord=vertice_data['yCoord'],
                isGarbageDump=vertice_data['isGarbageDump']
            )
            self.vertices.append(vertice)
            vertice_name_to_index[name] = idx

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
            first_idx = vertice_name_to_index[edge_data['firstVertice']]
            second_idx = vertice_name_to_index[edge_data['secondVertice']]

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

    def moveAllGarbageCollectors(self, speed, duration):
        for garbageCollector in self.garbage_collectors:
            if garbageCollector.targetLocalization != None:  # if current truck has no target, we skip it
                if (isinstance(garbageCollector.localization,
                               VerticeLocalization)):  # drive function accepts only edge-vertice or edge-edge, so we need to set appropriate with distanceFromStart equal to 0
                    targetEdgeNumber = None
                    targetVertice = garbageCollector.targetLocalization.verticeNumber
                    for (verticeNumber, edgeNumber) in self.map[garbageCollector.localization.verticeNumber]:
                        if verticeNumber == targetVertice:
                            targetEdgeNumber = edgeNumber
                    if (targetEdgeNumber is None):
                        raise TypeError(
                            "Target vertice is not adjacent to source vertice!")
                    targetLocalization = EdgeLocalization(targetEdgeNumber, 0)
                    garbageCollector.setTargetLocalization(targetLocalization)

                # Only get currentEdgeLength and drive if the collector is on an edge
                if isinstance(garbageCollector.localization, EdgeLocalization):
                    currentEdgeLength = self.edges[garbageCollector.localization.edgeNumber].length
                    garbageCollector.drive(speed, duration, currentEdgeLength)


    #Allows to plan journey to adjacent vertice
    def orderTruckMovementToVertice(self, garbageCollectorName, verticeName):
        verticeNumber = self.getVerticeByName(verticeName)
        if(verticeNumber is None):
            print(f"Vertice with name {verticeName} not found!")
            return
        garbageCollector = self.getGarbageCollectorByName(garbageCollectorName)
        currentLocalization = garbageCollector.localization
        currentEdge = None
        if(isinstance(currentLocalization, EdgeLocalization)):
            currentEdge = currentLocalization.edgeNumber
        else:
            print("This function allows orders only one step ahead")
            return
        if(self.edges[currentEdge].secondVertice == verticeNumber):
            verticeDestination = VerticeLocalization(verticeNumber)
            garbageCollector.setTargetLocalization(verticeDestination)
        else:
            print(f"Vertice with name {verticeName} is not adjacent to road, on which truck is!")
            return

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

