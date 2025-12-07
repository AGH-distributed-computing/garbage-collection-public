#garbageCollector.py

from localization import VerticeLocalization, EdgeLocalization, Localization

#All: fuelTankCapacity, fuelLevel, capacity, garbageLevel should be provided in litres
#crushingEfficiency is a coefficient, can take values (0,1] where 1 means no crushing at all
#To simplify, fuelConsumption is given in litres per hour. It is not far from the objective truth, though
class GarbageCollector:
    def __init__(self,
                 localization: Localization, #can be VerticeLocalization or EdgeLocalization
                 fuelTankCapacity,
                 fuelLevel,
                 capacity,
                 crushingEfficiency,
                 fuelConsumption,
                 timeSinceStart = 0, #in minutes
                 garbageLevel = 0
                 ):
        self.localization = localization
        self.fuelTankCapacity = fuelTankCapacity
        self.fuelLevel = fuelLevel
        self.capacity = capacity
        self.crushingEfficiency = crushingEfficiency
        self.fuelConsumption = fuelConsumption
        self.timeSinceStart = timeSinceStart
        self.garbageLevel = garbageLevel