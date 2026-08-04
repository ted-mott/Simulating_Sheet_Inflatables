import Sofa
import Sofa.Core
import SofaRuntime
import Sofa.Gui
import numpy as np


#########################################################################################
""" updated - 15.07.26 """
#########################################################################################


##### GMSH Geometry Manipulation ######

class GMSHLoaderExtended:
    #Expand GMSHLoader to retrieve sub-entities within loaded mesh
    #Can retrieve more information about those entities

    def __init__(self, loader_component):
        #takes in loader component and initialises triangle and edge groups
        self.loader = loader_component

        self.tets = np.array(self.loader.tetrahedra.value).copy()
        self.tet_entities = {}
        self.tet_entity_count = 0

        self.triangles = np.array(self.loader.triangles.value).copy()
        self.triangle_entities = {}
        self.triangle_entity_count = 0
        
        self.edges = np.array(self.loader.edges.value).copy()
        self.edge_entities = {}
        self.edge_entity_count = 0
       
        self.MeshCoordinates = np.array(self.loader.position.value).copy()
        #copy into np.array to avoid memory issues
        
        self.PopulateGroupList()


    def MeshInfo(self):
        #Print info about mesh in given meshloader
        print("-- GMSH File Information --")
        print("Filename used:", self.loader.filename.value)
        print("Found" ,self.tet_entity_count, "Tetrahedra Groups:", self.loader.tetrahedraGroups.getValueString())
        print("Found" ,self.triangle_entity_count, "Triangle Groups:", self.loader.trianglesGroups.getValueString())
        print("Found" , self.edge_entity_count, "Edge Groups:", self.loader.edgesGroups.getValueString())
        print("---------------------------")
        

    def PopulateGroupList(self):
        #SOFA gives group list in format "  -1 FirstPhysicalGroupIndex Range "
        #Note that SOFA uses "  -1 " delimiter to help parse the values
        tetString = self.loader.tetrahedraGroups.getValueString().split("  -1 ")
        tetIndices = self.ParseList(tetString)
        self.tet_entities = self.PopulateEntityDict(tetIndices, self.tets, 3)
        self.tet_entity_count = len(self.tet_entities)

        triString = self.loader.trianglesGroups.getValueString().split("  -1 ")
        triIndices = self.ParseList(triString)
        self.triangle_entities = self.PopulateEntityDict(triIndices, self.triangles, 2)
        self.triangle_entity_count = len(self.triangle_entities)

        edgeString = self.loader.edgesGroups.getValueString().split("  -1 ")
        edgeIndices = self.ParseList(edgeString)
        self.edge_entities = self.PopulateEntityDict(edgeIndices, self.edges, 1)
        self.edge_entity_count = len(self.edge_entities)


    @staticmethod
    def ParseList(StringList):
        #Remove first entity if null
        if StringList[0] == "" or StringList[0] == " ":
            StringList.pop(0)
        
        EntityId = 0
        EntityList = []


        #Parse Entityinfo string in EntityList and replace with int range
        for String in StringList:
            Entityinfo = String.split(" ")
            

            Start = int(Entityinfo[0])
            Span= int(Entityinfo[1])
            End = Start + Span
            
            Entity = (EntityId, Start , End)
            EntityList.append(Entity)
            #Now in format that can be used to populate entities dictionary

            EntityId = EntityId + 1

        return EntityList
    
    
    def PopulateEntityDict(self, EntityList, MeshEntities, EntityDim):
        #When physical group is called convert range(Start, Stop) into list of node indices that can be used by SOFA
        EntityDictionary = {}

        for Entity in EntityList:
            SOFAEntityId, Start, End = Entity
            EntityIndices = MeshEntities[Start: End]
            #Tris stored as [node1,node2,node3], Edges stored as [node1,node2]..etc.
            EntityNodes = self.FlattenNodelist(EntityIndices)
            EntityNodeCount = len(EntityNodes)
            EntityCoords = self.CoordinatesListFromNode(EntityNodes)
            
            EntityDictionary[SOFAEntityId] = {
                "Dimension" : EntityDim,
                "ElementIndices" : EntityIndices,
                "Nodes" : EntityNodes,
                "NodeCount" : EntityNodeCount,
                "EntityCoordinates" : EntityCoords
            }

        return EntityDictionary
    

    @staticmethod
    def FlattenNodelist(Nodelist):
        #strips nodes out of tuples inside Nodelist and adds to set to just give nodes of group
        FlatNodeSet = set()

        for Nodes in Nodelist:
            for Node in Nodes:
                FlatNodeSet.add(Node)
        
        #return as a list for use with SOFA
        return list(FlatNodeSet)
    
    def CoordinatesListFromNode(self, FlatNodeList):
        #returns coordinates of Nodelist, will share an index
        CoordinatesList = []

        for Node in FlatNodeList:
            #Node = int(Node)
            xyz = self.MeshCoordinates[Node]
            CoordinatesList.append(xyz)

        return CoordinatesList

        

class PhysicalGroup:
    #Class to store combinations of GMSH entities so they can be referenced by SOFA
    def __init__(self, GmshLoader_ElementTypeEntities, *Entities):
        
        self.PhysicalGroupEntities = Entities
        self.GmshLoader_ElementTypeEntities = GmshLoader_ElementTypeEntities
        self.PhysicalGroupDim = None
        self.PhysicalGroupTag = None

        self.Nodes = []
        self.ElementIndices = []

        self.LoadAndRemoveDupes()
        

    def LoadAndRemoveDupes(self):
        #Load Nodes and Elements from GmshLoaderExtended, put into set to ensure no repeats
        NodeSet = set()

        for Entity in self.PhysicalGroupEntities:

            if not self.PhysicalGroupDim:
                self.PhysicalGroupDim = self.GmshLoader_ElementTypeEntities[Entity]["Dimension"]
                #Ensures not repeatedly writing to PhysicalGroupDim
                ElementsIndicesList = self.GmshLoader_ElementTypeEntities[Entity]["ElementIndices"]
                #Also gives indication of first entity, is an nparray so annoying to initialise - this is a dodgy workaround
            else:
                EntityElementsIndices = self.GmshLoader_ElementTypeEntities[Entity]["ElementIndices"]
                ElementsIndicesList = np.concatenate((ElementsIndicesList, EntityElementsIndices))
                #Assuming no overlapping elements as they have been separated into entities
            
            EntityNodes = self.GmshLoader_ElementTypeEntities[Entity]["Nodes"]
            NodeSet.update(set(EntityNodes))
            #Entities very likely to have overlapping nodes so cull duplicates here

        self.Nodes = list(NodeSet)
        self.ElementIndices = ElementsIndicesList


    def ConstructfromJSON():
        #Create a constructor function for passing between
        pass



# ##### Constraints #####

# class Weld:
#     def __init__(self, NodeList, NodeDictionary, YoungsModulus, Thickness):
#         #uses springs at points
#         self.YoungModulus = YoungsModulus #in Pa
#         self.Thickness = Thickness #in m

#         self.NodeList = NodeList
#         self.NodeDictionary = NodeDictionary

#         self.weldsprings = {}
#         #need to figure output format!

#         self.DistanceBetweenNodes(self.NodeList, self.NodeDictionary)

#     def DistanceBetweenNodes(self, ):
#         pass







#########new controller

class ControllerMonitor(Sofa.Core.Controller):
    def __init__(self,  *args, **kwargs):
        # These are needed (and the normal way to override from a python class)
        Sofa.Core.Controller.__init__(self, *args, **kwargs)
        
        self.SimulationControllers = []
        #List of current controllers and associated keys?
        self.KeyMap = {}

        print("initialised Controller monitor:" , self.name.value)

    def onKeypressedEvent(self, event):
        pressedKey = event['key']
        #print("key pressed:" ,pressedKey)

        if pressedKey in self.KeyMap:
            for Controller, ChangeValue in self.KeyMap[pressedKey]:
                Controller.update(ChangeValue)

        elif pressedKey == "/":
            self.ControllerInfo()

    # def onAnimateBeginEvent(self, event):
    #     can use this to synchronise with other controller

    def AddController(self, Controller, ControlType, **kwargs):
        #store controller and type
        self.SimulationControllers.append((Controller, ControlType))

        #store keys and change values
        for key, value in kwargs.items():
            self.BindKey(key, Controller, value)
            #self.KeyMap[key] = [(Controller , int(value))]

    def BindKey(self, key, Controller, value):
        #Function allows multiple fields related to single key mapping
        if key in self.KeyMap:
            self.KeyMap[key].append((Controller , int(value)))
        else:
            self.KeyMap[key] = [(Controller , int(value))]


    def ControllerInfo(self):
        #print controller, current values
        #print key, controller, update
        if len(self.SimulationControllers) < 1:
            print("No Controllers")

        else:
            for Controller, ControlType in self.SimulationControllers:
                print(Controller.name.value, ", Type: ", ControlType, ", Current Value: ", Controller.current_value, ", Target Value: ", Controller.target_value)
      


class SOFA_Controller(Sofa.Core.Controller):
    def __init__(self, SOFAfield = None,  minVal = 0, maxVal = 30000, targetVal = 0, changeRate = 1, method = "Linear",  *args, **kwargs):
        #Initialise sofa controller
        Sofa.Core.Controller.__init__(self, *args, **kwargs)

        #Generic link to SOFA field
        self.SOFAfield = SOFAfield
        
        #Added to be simpler to interface with on script level
        self.target_value = targetVal
        self.current_value = 0
        self.previous_value = None

        self.max = maxVal
        self.min = minVal
        self.changeRate =changeRate
        #change per time step, defult 1 per step
        self.method = method
        #method to arrive at target, default Linear ramp
        print("Controller Initialised: ", self.name.value)

    def update(self, ChangeValue):
        #change target by set amount, based on keypress
        self.target_value = self.target_value + ChangeValue

        if self.target_value > self.max:
            self.target_value = self.max
        elif self.target_value < self.min:
            self.target_value = self.min

        print("target updated to: ", self.target_value)
    
    def poll(self):
        #compare current value to target value
        if  self.current_value == self.target_value:
            return None
        
        if self.method == "Linear":
            nextStep = self.LinearRamp()

        return nextStep

    def LinearRamp(self):
        #Calculate nextStep if values are ramped linearly
        if self.target_value < self.current_value:
            nextStep = self.current_value - self.changeRate

        elif self.target_value > self.current_value:
            nextStep = self.current_value + self.changeRate

        if self.changeRate >=  abs(self.target_value - self.current_value):
            nextStep = self.target_value
        
        return nextStep



class PressureController(SOFA_Controller):
    #Pressure controller is a controller but it updates the pressure value
    def onAnimateBeginEvent(self, event):
        nextStep = self.poll()
        if nextStep:    
            self.previous_value = self.current_value
            self.current_value = nextStep
            self.SOFAfield.pressure = self.current_value
            #Set SOFA parameter
            