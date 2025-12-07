#edge.py

class Edge:
    def __init__(self,
                 name,
                 length,
                 isOneWay,
                 isCollectingBothSidesAllowed,
                 firstVertice, #source vertice
                 secondVertice, #target vertice
                 trafficType,
                 trafficIntensity,
                 rightSideBins,
                 leftSideBins):
        self.name = name
        self.length = length
        self.isOneWay = isOneWay
        self.isCollectingBothSidesAllowed = isCollectingBothSidesAllowed
        self.firstVertice = firstVertice
        self.secondVertice = secondVertice
        self.trafficType = trafficType
        self.trafficIntensity = trafficIntensity
        self.rightSideBins = rightSideBins
        self.leftSideBins = leftSideBins