
import Sofa
import Sofa.Core
import SofaRuntime
import Sofa.Gui
import numpy as np


class GMSHMesh:
    #Class is expanding gmshloader in SOFA to retrieve physical groups
    #Currently only retrieves the collections and is not mapped back to physical groups - unsure how to achieve this

    def __init__(self, loader_component):
        #takes in loader component and initialises triangle and edge groups
        self.loader = loader_component

        self.triangle_group_indices = []
        self.triangle_groups_length = 0
        self.triangles = np.array(self.loader.triangles.value).copy()
        
        self.edge_group_indices = []
        self.edge_groups_length = 0
        self.edges = np.array(self.loader.edges.value).copy()

        self.MeshCoordinates = np.array(self.loader.position.value).copy()
        #copy into np.array to avoid memory issues
        
        self.PopulateGroupList()


    def MeshInfo(self):
        #Print info about mesh in given meshloader
        print("-- GMSH File Information --")
        print("Filename used:", self.loader.filename.value)
        print("Found" ,self.triangle_groups_length, "Triangle Groups:", self.loader.trianglesGroups.getValueString())
        print("Found" , self.edge_groups_length, "Edge Groups:", self.loader.edgesGroups.getValueString())
        print("---------------------------")
        

    def PopulateGroupList(self):
        #SOFA gives group list in format "  -1 FirstPhysicalGroupIndex Range "
        #Note that SOFA uses "  -1 " delimiter to help parse the values
        self.triangle_group_indices = self.loader.trianglesGroups.getValueString().split("  -1 ")
        self.triangle_group_indices = self.ParseList(self.triangle_group_indices)
        
        self.triangle_groups_length = len(self.triangle_group_indices)

        self.edge_group_indices = self.loader.edgesGroups.getValueString().split("  -1 ")
        self.edge_group_indices = self.ParseList(self.edge_group_indices)

        self.edge_groups_length = len(self.edge_group_indices)


    @staticmethod
    def ParseList(PhysicalGroup):
        #Further parse into range lists
        if PhysicalGroup[0] == "" or PhysicalGroup[0] == " ":
            PhysicalGroup.pop(0)
        
        #Parse start and range values
        for i in range(0, len(PhysicalGroup)):
            GroupRange = PhysicalGroup[i].split(" ")
            
            Start = int(GroupRange[0])
            Span= int(GroupRange[1])
            
            PhysicalGroup[i] = (Start , Start + Span)

        return(PhysicalGroup)


    def PhysicalGroupNodes(self, targetType, PhysicalGroupIndex, FlatSet = None, FlatList = None):
        #When physical group is called convert range(Start, Stop) into list of node indices that can be used by SOFA
        
        if targetType == "triangle":
            #recover start and end that have been parsed
            Start, End = (self.triangle_group_indices[PhysicalGroupIndex])
            #query SOFA for triangles based on index
            nodeList = self.triangles[Start: End]
        
        elif targetType == "edge":
            Start, End = (list(self.edge_group_indices[PhysicalGroupIndex]))
            nodeList = self.edges[Start:End]

        if FlatSet or FlatList:
            nodeSet = self.FlattenNodeList(nodeList)

            if FlatList:
                return list(nodeSet)
            
            return nodeSet

        return nodeList


    def FlattenNodeList(self, nodeList):
        #Extracts nodes into a set of nodes
        FlatNodeSet = set()
        for Nodes in nodeList:
            for Node in Nodes:
                FlatNodeSet.add(Node)
        return FlatNodeSet


    def PhysicalGroupIndices(self, targetType, PhysicalGroupIndex):
        #When physical group is called convert range(Start, Stop) into list of triangle indices that can be used by SOFA
        if targetType == "triangle":
            #recover start and end that have been parsed
            Start, End = (self.triangle_group_indices[PhysicalGroupIndex])
            return(list(range(Start, End)))
        
        elif targetType == "edge":
            Start, End = (list(self.edge_group_indices[PhysicalGroupIndex]))
            return(list(range(Start, End)))


    def NodeCoordinates (self, NodeList):
        #Returns dictionary of nodes and x y z coordinates
        Coordinates = {}

        for Nodes in NodeList:
            for Node in Nodes:
                xyz = self.MeshCoordinates[Node]
                Coordinates[Node] = {
                    "x": xyz[0],
                    "y": xyz[1],
                    "z": xyz[2]
                }
            
        print(Coordinates)

        return(Coordinates)
        



class Weld:
    def __init__(self, NodeList, NodeDictionary, YoungsModulus, Thickness):
        #uses springs at points
        self.YoungModulus = YoungsModulus #in Pa
        self.Thickness = Thickness #in m

        self.NodeList = NodeList
        self.NodeDictionary = NodeDictionary

        self.weldsprings = {}
        #need to figure output format!

        self.DistanceBetweenNodes(self.NodeList, self.NodeDictionary)

    def DistanceBetweenNodes(self, ):
        pass









class PressureController:
    pass












def main():
    # Call the SOFA function to create the root node
    root = Sofa.Core.Node("root")

    SofaRuntime.importPlugin("SofaImGui")

    # Call the createScene function, as runSofa does
    createScene(root)

    # Once defined, initialization of the scene graph
    Sofa.Simulation.initRoot(root)

    # # Launch the GUI (imgui is now by default, to use Qt please refer to the example "basic-useQtGui.py")
    # Sofa.Gui.GUIManager.Init("myscene", "imgui")
    # Sofa.Gui.GUIManager.createGUI(root, __file__)
    # Sofa.Gui.GUIManager.SetDimension(1080, 800)

    # # Initialization of the scene will be done here
    # Sofa.Gui.GUIManager.MainLoop(root)
    # Sofa.Gui.GUIManager.closeGUI()



def createScene(rootNode):

    #Name of root node
    rootNode.name.value = "rootNode"
    #time step, S
    rootNode.dt = 0.01
    #gravity in mmS-2
    rootNode.gravity.value = [ 0., 0. ,-9.81]


    rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.MechanicalLoad',
                                                'Sofa.Component.LinearSolver.Iterative','Sofa.Component.ODESolver.Backward',
                                                'Sofa.Component.IO.Mesh','Sofa.Component.Topology.Container.Dynamic',
                                                'Sofa.Component.SolidMechanics.FEM.Elastic','Sofa.Component.Topology.Container.Constant',
                                                'Sofa.Component.Visual','Sofa.Component.Mapping.Linear','Sofa.GL.Component.Rendering3D',
                                                'Sofa.Component.Constraint.Projective','Sofa.Component.Engine.Select',
                                                'Sofa.Component.Constraint.Lagrangian.Correction','Sofa.Component.Constraint.Lagrangian.Model',
                                                'Sofa.Component.Constraint.Lagrangian.Solver','Sofa.Component.LinearSolver.Direct',
                                                'Sofa.Component.AnimationLoop','Sofa.GUI.Component'])


    #rootNode.addObject("FreeMotionAnimationLoop", computeBoundingBox=True)
    rootNode.addObject("DefaultAnimationLoop", computeBoundingBox=True)
    #free motion animation loop needed for lagrangian constraints
    rootNode.addObject('LCPConstraintSolver', tolerance="1e-3", maxIt="1000")
    
    rootNode.addObject('VisualStyle', displayFlags='showForceFields showCollisionModels showBehaviorModels showDetectionOutputs showNormals')
    #tells SOFA what models are allowed to be displayed


    """----------- Inflatable ----------"""
    #Define parent node
    
    Inflatable = rootNode.addChild("Inflatable")
    #GmshLoader should be attached to parent
    

    GmshLoader = Inflatable.addObject("MeshGmshLoader", name='GmshLoader', filename= r"C:\Users\ucemeam\OneDrive - University College London\git\Simulating_Surface_Based_Inflatables\Simulation_SOFA\Test1_2D_Circle\MESH_geometry\Test1_2D_Circlev2.msh", scale3d=[0.001, 0.001, 0.001])
    #GMSH .msh file units in mm, scale to m
    
    TestMesh = GMSHMesh(GmshLoader)

    TestMesh.MeshInfo()









# Function used only if this script is called from a python environment
if __name__ == '__main__':
    main()