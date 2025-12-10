#garbageCollector.py
from collections import deque

from localization import VerticeLocalization, EdgeLocalization, Localization

#All: fuelTankCapacity, fuelLevel, capacity, garbageLevel should be provided in litres
#crushingEfficiency is a coefficient, can take values (0,1] where 1 means no crushing at all
#To simplify, fuelConsumption is given in litres per hour. It is not far from the objective truth, though
class GarbageCollector:
    def __init__(self,
                 name,
                 localization: Localization, #can be VerticeLocalization or EdgeLocalization
                 fuelTankCapacity,
                 fuelLevel,
                 capacity,
                 crushingEfficiency,
                 fuelConsumption,
                 timeSinceStart = 0, #in minutes
                 garbageLevel = 0
                 ):
        self.name = name,
        self.localization = localization
        self.fuelTankCapacity = fuelTankCapacity
        self.fuelLevel = fuelLevel
        self.capacity = capacity
        self.crushingEfficiency = crushingEfficiency
        self.fuelConsumption = fuelConsumption
        self.timeSinceStart = timeSinceStart
        self.garbageLevel = garbageLevel
        self.targetLocalization = None

    def canCollectGarbage(self, litres):
        if(self.garbageLevel + litres * self.crushingEfficiency <= self.capcity):
            return True
        return False

    def collectGarbage(self, litres):
        self.garbageLevel += litres * self.crushingEfficiency

    def consumeFuel(self, minutes):
        self.fuelLevel -= self.fuelConsumption * minutes / 60
        self.fuelLevel = max(self.fuelLevel, 0)

    def setTargetLocalization(self, targetLocalization):
        self.targetLocalization = targetLocalization

    def canTakeNextOrder(self):
        if(self.targetLocalization is None):
            return True
        return False

#speed given in kilometers per hour, duration in minutes
#works only for edge to vertice or edge to edge
#Before travel between vertices, set lcalization to point 0 on appropriate edge
#returns time left out of duration param
    def drive(self, speed, duration, currentEdgeLength, garbageDumps):
        if(isinstance(self.localization, VerticeLocalization)):
            raise TypeError("trucks localization must be of type EdgeLocalization in order to use drive function")

        distanceTruckCanTravel = speed * 1000 * duration / 60
        if(isinstance(self.targetLocalization, VerticeLocalization)):
            if(self.localization.distanceFromStart + distanceTruckCanTravel >= currentEdgeLength):
                travelTime = (currentEdgeLength - self.localization.distanceFromStart) / 1000 / speed * 60
                self.localization = self.targetLocalization
                if(self.localization.verticeNumber in garbageDumps):
                    print(f"Garbage collector '{self.name}' reached the base. Refuelling and dumping garbage...")
                    self.baseReached()
                self.targetLocalization = None
                return travelTime
            else:
                self.localization.distanceFromStart += distanceTruckCanTravel
                return 0
        elif(isinstance(self.localization, EdgeLocalization)):
            travelDistance = self.localization.calculateDistance(self.targetLocalization)
            travelTime = travelDistance / 1000 / speed * 60
            if(self.localization.distanceFromStart + distanceTruckCanTravel >= travelDistance):
                self.localization = self.targetLocalization
                self.targetLocalization = None
                return travelTime
            else:
                self.localization.distanceFromStart += distanceTruckCanTravel
                return 0

    def baseReached(self):
        self.FuelLevel = self.fuelTankCapacity
        self.garbageLevel = 0
        self.timeSinceStart = 0
