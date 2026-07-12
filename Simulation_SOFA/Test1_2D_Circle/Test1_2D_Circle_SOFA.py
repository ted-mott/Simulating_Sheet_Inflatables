import sys
sys.path.append(r"Simulation_SOFA")
from Surface_Based_Inflatables_SOFA import GMSHMesh
#GMSHMesh class created to access physical groups, path.append required for import, can only run this as main (for now)

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
mesh_data_dir = os.path.join(current_dir, "MESH_geometry")
#Need to set absolute path for mesh import for SOFA GUI to work

import Sofa
import Sofa.Core
import SofaRuntime
import Sofa.Gui


"""----------- JSON info ----------"""

InitialInflatablePressure = 0 #Pressure in Pa
FlowRate = 0.01 #Pressure/second for now
SupplyPressure  = 30000 #30kPa

YoungsModulus = 93000000.0 #E in Pa
PoissonsRatio = 0.45

MeshArea =  0.008 #Mesh Area in m^2
Density = 910 #Density in m^3/kg
Thickness = 0.0000635 #Thickness (63.5 microns/250 gauge) in m
Mass = Density*Thickness*MeshArea #Mass in kg
MeshFilename  = r"Test1_2D_Circlev2.msh"

InitialisationTime = 1 #in seconds, how long does the simulation get to settle before applying loads


Mesh_Location  = os.path.join(mesh_data_dir, MeshFilename)


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

    # Launch the GUI
    Sofa.Gui.GUIManager.Init("myscene", "imgui")
    Sofa.Gui.GUIManager.createGUI(root, __file__)
    Sofa.Gui.GUIManager.SetDimension(1080, 800)

    # Initialization of the scene will be done here
    Sofa.Gui.GUIManager.MainLoop(root)
    Sofa.Gui.GUIManager.closeGUI()



def createScene(rootNode):

    #Name of root node
    rootNode.name.value = "rootNode"
    #time step, S
    rootNode.dt = 0.00001
    #gravity in mmS-2
    rootNode.gravity.value = [ 0., 0. ,-9.81]


    rootNode.addObject("RequiredPlugin", pluginName=["Sofa.Component.StateContainer","Sofa.Component.Mass","Sofa.Component.MechanicalLoad",
                                                "Sofa.Component.LinearSolver.Iterative","Sofa.Component.ODESolver.Backward",
                                                "Sofa.Component.IO.Mesh","Sofa.Component.Topology.Container.Dynamic",
                                                "Sofa.Component.SolidMechanics.FEM.Elastic","Sofa.Component.Topology.Container.Constant",
                                                "Sofa.Component.Visual","Sofa.Component.Mapping.Linear","Sofa.GL.Component.Rendering3D",
                                                "Sofa.Component.Constraint.Projective","Sofa.Component.Engine.Select",
                                                "Sofa.Component.Constraint.Lagrangian.Correction","Sofa.Component.Constraint.Lagrangian.Model",
                                                "Sofa.Component.Constraint.Lagrangian.Solver","Sofa.Component.LinearSolver.Direct",
                                                "Sofa.Component.AnimationLoop","Sofa.GUI.Component","Sofa.Component.SolidMechanics.Spring",
                                                "Sofa.Component.Engine.Transform",'Sofa.Component.Collision.Geometry','Sofa.Component.Collision.Detection.Intersection',
                                                'Sofa.Component.Collision.Detection.Algorithm','Sofa.Component.Collision.Response.Contact'])


    #rootNode.addObject("FreeMotionAnimationLoop", computeBoundingBox=True)
    rootNode.addObject("DefaultAnimationLoop", computeBoundingBox=True)
  
    #collision pipeline!
    rootNode.addObject('CollisionPipeline')
    rootNode.addObject('BruteForceBroadPhase') # Broad phase
    rootNode.addObject('BVHNarrowPhase') # Narrow phase
    rootNode.addObject('MinProximityIntersection', name="Proximity", alarmDistance="0.0005", contactDistance="0.00025") #Intersection method used for the narrow phase
    rootNode.addObject('CollisionResponse', name="Response", response="PenalityContactForceField") # Reponse method when a contact is detected in the narrow phase
    

    rootNode.addObject("VisualStyle", displayFlags="showForceFields showCollisionModels showBehaviorModels showDetectionOutputs showNormals")
    #tells SOFA what models are allowed to be displayed

    """----------- Inflatable ----------"""
    #Define parent node
    
    Inflatable = rootNode.addChild("Inflatable")
    #GmshLoader should be attached to parent
    
    Mesh_Location  = os.path.join(mesh_data_dir, MeshFilename)
    GmshLoader = Inflatable.addObject("MeshGmshLoader", name="GmshLoader", filename= Mesh_Location, scale3d=[0.001, 0.001, 0.001])
    #GMSH .msh file units in mm, scale to m
    
    InflateSurfaceMesh = GMSHMesh(GmshLoader)
    InflateSurfaceMesh.MeshInfo()




    
####### Define sets and lists of nodes for features

    InflateSurfaceTrianglesIndices = InflateSurfaceMesh.PhysicalGroupNodes("triangle", 0)

    
    CoincidentEdgeNodeSet = set()

    for i in range (0, InflateSurfaceMesh.edge_groups_length):
        CoincidentNodes = InflateSurfaceMesh.PhysicalGroupNodes("edge", i, FlatSet = True)
        CoincidentEdgeNodeSet.update(CoincidentNodes)

    CoincidentEdgeNodes = list(CoincidentEdgeNodeSet)

    AnchorNodeSet = set()
    
    for i in range (2, InflateSurfaceMesh.triangle_groups_length):
        AnchorNodes = InflateSurfaceMesh.PhysicalGroupNodes("triangle", i, FlatSet = True)
        AnchorNodeSet.update(AnchorNodes)

    AnchorSurfaceIndices = list(AnchorNodeSet)


    #Defining contact sets required for later, converting to lists to use with python.
    #In future this could be a whole constructor class for inflatables but won't be atm

    AvoidContactSet = AnchorNodeSet | CoincidentEdgeNodeSet
    AvoidContactNodes = list(AvoidContactSet)


    AllSet = InflateSurfaceMesh.FlattenNodeList(InflateSurfaceMesh.triangles)
    #this returns a set of all the nodes in the mesh loader

    ContactSet = AllSet.difference(AvoidContactSet)
    ContactNodes = list(ContactSet)
    
    ####### Back to it :)




    Inflatable.addObject("EulerImplicitSolver",rayleighStiffness="0.1", rayleighMass="0.1")
    Inflatable.addObject("CGLinearSolver", iterations=200, tolerance=1e-9, threshold=1e-9)


    """----------- Inflatable Children----------"""


    InflatablePressure = 500
    #create an inflatable pressure controller for this!
    #controller should sit in inflatable class


    InflatableSurfaceA = Inflatable.addChild("InflatableSurfaceA")
    InflatableSurfaceA.addObject("TriangleSetTopologyContainer", name="topologyContainerA", src="@../GmshLoader")
    InflatableSurfaceA.addObject("MechanicalObject", template="Vec3d", name="StateContainerA", showObject=True)
    InflatableSurfaceA.addObject("UniformMass", totalMass = Mass )
    InflatableSurfaceA.addObject("TriangleFEMForceField", template="Vec3d", poissonRatio=PoissonsRatio, youngModulus=YoungsModulus, thickness = Thickness, method="large")
    InflatableSurfaceA.addObject("SurfacePressureForceField", name="Pressure_RegionA", pressure= InflatablePressure, triangleIndices = InflateSurfaceTrianglesIndices)
    InflatableSurfaceA.addObject("FixedProjectiveConstraint", name="AnchorA", indices= AnchorSurfaceIndices)


    InflateSurfaceACollision = InflatableSurfaceA.addChild("InflateSurfaceACollision")
    #InflateSurfaceACollision.addObject("PointSetTopologyContainer", name="topologyContainerACollis", src = "@../topologyContainerA", index = ContactSet) #triangles = , if make separate triangle surface use this
    InflateSurfaceACollision.addObject("PointSetTopologyContainer", name="topologyContainerACollis")
    InflateSurfaceACollision.addObject("MechanicalObject", name="StoringForces", template='Vec3d')
    InflateSurfaceACollision.addObject("SubsetMapping", template='Vec3d,Vec3d', input= "@../StateContainerA", output ="@StoringForces", indices = ContactNodes)
    InflateSurfaceACollision.addObject("SphereCollisionModel", name="CollisionModel", selfCollision = 1,  contactStiffness=3, radius = 0.001)


    


    # ### Hopefully this works :)

    InflatableSurfaceB = Inflatable.addChild("InflatableSurfaceB")
    InflatableSurfaceB.addObject("TriangleSetTopologyContainer", name="topologyContainerB", src="@../GmshLoader")
    InflatableSurfaceB.addObject("MechanicalObject", template="Vec3d", name="StateContainerB", showObject=True)
    #translation=[0.0, 0.0, 0.0] could be included in mechanical object here
    InflatableSurfaceB.addObject("UniformMass", totalMass = Mass )
    InflatableSurfaceB.addObject("TriangleFEMForceField", template="Vec3d", poissonRatio=PoissonsRatio, youngModulus=YoungsModulus, thickness = Thickness, method="large")
    InflatableSurfaceB.addObject("SurfacePressureForceField", name="Pressure_RegionB", pressure= - InflatablePressure, triangleIndices = InflateSurfaceTrianglesIndices)
    InflatableSurfaceB.addObject("FixedProjectiveConstraint", name="AnchorB", indices= AnchorSurfaceIndices)



    #welds for finger

    Inflatable.addObject("SpringForceField", name = "Weld", object1 = "@InflatableSurfaceA/StateContainerA",  object2 = "@InflatableSurfaceB/StateContainerB", springsIndices1 = CoincidentEdgeNodes, springsIndices2 = CoincidentEdgeNodes, stiffness = [100000], lengths =[0])
    
    #Weld to anchor - to be fixed
    Inflatable.addObject("SpringForceField", name = "Weld", object1 = "@InflatableSurfaceA/StateContainerA",  object2 = "@InflatableSurfaceB/StateContainerB", springsIndices1 = AnchorSurfaceIndices, springsIndices2 = AnchorSurfaceIndices, stiffness = [100000], lengths =[0])




    # ##########################################
	# # Collision representation of the finger object
	# collisionlModel = mechanicalModel.addChild("Collision")
	# collisionlModel.addObject("MeshTopology", name="topologyContainer", src=visualModel.loader.linkpath) # Use the same mesh topology than the visual model
	# collisionlModel.addObject("MechanicalObject", name="StoringForces") # Mechanical object storing the DoFs corresponding to the contact points and associated forces
	# collisionlModel.addObject("TriangleCollisionModel", name="CollisionModel", contactStiffness=3) # Triangular primitives used at the narrow phase
	# collisionlModel.addObject("BarycentricMapping", name="VisualMapping", input="@../StateContainer", output="@StoringForces") # Barycentric mapping connecting the two representations with different topologies
	


# Function used only if this script is called from a python environment
if __name__ == "__main__":
    main()