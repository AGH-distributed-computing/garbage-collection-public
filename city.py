#city.py

import json
from logging import NullHandler

from edge import Edge
from garbageCollector import GarbageCollector
from localization import VerticeLocalization, EdgeLocalization
from vertice import Vertice
from rubbishBin import RubbishBin

def getVerticeNumberByName(vertices, verticeName):
    for idx, vertice in enumerate(vertices):
        if vertice.name ==  verticeName:
            return idx
    return None

def getEdgeNumberByName(edges, edgeName):
    for idx, edge in enumerate(edges):
        if edge.name == edgeName:
            return idx
    return None


class City:
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
                rubbishBin = RubbishBin(
                    type=bin_data['binType'],
                    capacity=bin_data['capacity']
                )
                rightSideBins[location] = rubbishBin

            for bin_data in edge_data.get('leftSideBins', []):
                location = bin_data['location']
                rubbishBin = RubbishBin(
                    type=bin_data['binType'],
                    capacity=bin_data['capacity']
                )
                leftSideBins[location] = rubbishBin

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
                verticeNumber = getVerticeNumberByName(self.vertices, truck_data['verticeLocalization'])
                if verticeNumber is None:
                    raise ValueError(f"Vertex '{truck_data['verticeLocalization']}' not found for truck {truck_name}")
                localization = VerticeLocalization(verticeNumber)
            elif 'edgeLocalization' in truck_data:
                edge_loc = truck_data['edgeLocalization']
                edgeNumber = getEdgeNumberByName(self.edges, edge_loc['edgeName'])
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
