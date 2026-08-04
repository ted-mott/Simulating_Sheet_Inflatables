import sys
sys.path.append(r"Simulation_SOFA")
from Surface_Based_Inflatables_SOFA import *
#GMSHMesh class created to access physical groups, path.append required for import, can only run this as main (for now)

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
mesh_data_dir = os.path.join(current_dir, "MESH_geometry")
#Need to set absolute path for mesh import for SOFA GUI to work

import Sofa
import Sofa.Core
import SofaRuntime
import Sofa.Gui

#########################################################################################
""" 2D Circle Simulation"""
#########################################################################################

##### JSON info #####

# InitialInflatablePressure = 0 #Pressure in Pa
# FlowRate = 0.01 #Pressure/second for now
# SupplyPressure  = 30000 #30kPa
# Now in controller

YoungsModulus = 93000000.0 #E in Pa
PoissonsRatio = 0.45

MeshArea =  0.008 #Mesh Area in m^2
Density = 910 #Density in m^3/kg
Thickness = 0.0000635 #Thickness (63.5 microns/250 gauge) in m
Mass = Density*Thickness*MeshArea #Mass in kg
MeshFilename  = r"Sim1_2D_Circle_LC4.msh"

InitialisationTime = 1 #in seconds, how long does the simulation get to settle before applying loads

Mesh_Location  = os.path.join(mesh_data_dir, MeshFilename)



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
    rootNode.dt = 0.01
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
    

    rootNode.addObject("VisualStyle", displayFlags="showForceFields showCollisionModels showBehaviorModels showDetectionOutputs")
    #tells SOFA what models are allowed to be displayed

    monitor = ControllerMonitor(name="monitor")
    #need to create object first to get access to python class functions
    rootNode.addObject(monitor)
    #Controller monitor can keep track of 
    

    ##### Inflatable #####
    #Define parent node as inflatble
    
    Inflatable = rootNode.addChild("Inflatable")
    #GmshLoader should be attached to parent
    
    Mesh_Location  = os.path.join(mesh_data_dir, MeshFilename)
    GmshLoader = Inflatable.addObject("MeshGmshLoader", name="GmshLoader", filename= Mesh_Location, scale3d=[0.001, 0.001, 0.001])
    GmshLoader2 = Inflatable.addObject("MeshGmshLoader", name="GmshLoader2", filename= Mesh_Location, scale3d=[0.001, 0.001, 0.001], translation = [0.0, 0.0, 0.001])
    #GMSH .msh file units in mm, scale to m
    
    InflateSurfaceMesh = GMSHLoaderExtended(GmshLoader)
    #Class created to extract entities available in GSMH file
    InflateSurfaceMesh.MeshInfo()

    InflateSurfaceMesh2 = GMSHLoaderExtended(GmshLoader2)
    #Class created to extract entities available in GSMH file
    InflateSurfaceMesh2.MeshInfo()



    ##### Define Physical groups #####

    InflateSurface = PhysicalGroup(InflateSurfaceMesh.triangle_entities, 0)
    Weld = PhysicalGroup(InflateSurfaceMesh.triangle_entities, 1)
    Anchor = PhysicalGroup(InflateSurfaceMesh.triangle_entities, 2, 3, 4, 5)
    Outer = PhysicalGroup(InflateSurfaceMesh.triangle_entities, 6)

    NoWeld = PhysicalGroup(InflateSurfaceMesh.triangle_entities, 0, 6)
    #New group created for contacts
 
    ##### Define Solvers #####

    Inflatable.addObject("EulerImplicitSolver",rayleighStiffness="0.1", rayleighMass="0.1")
    Inflatable.addObject("CGLinearSolver", iterations=200, tolerance=1e-9, threshold=1e-9)
    #Should set tolerance and threshold to 1e-10, based on dof scale of 1e-3 and error of 1e-2, tol should be dof err squared



    ##### Define Pressure #####

    ##### Inflated Surface and Fixed Anchor Constraints #####
    #Inflatable surfaces are children of inflatable to keep enclosed, B is copy of A with Negative pressure

    InflatableSurfaceA = Inflatable.addChild("InflatableSurfaceA")
    InflatableSurfaceA.addObject("TriangleSetTopologyContainer", name="topologyContainerA", src="@../GmshLoader")
    InflatableSurfaceA.addObject("MechanicalObject", template="Vec3d", name="StateContainerA", showObject=True)
    InflatableSurfaceA.addObject("UniformMass", totalMass = Mass )
    InflatableSurfaceA.addObject("TriangleFEMForceField", template="Vec3d", poissonRatio=PoissonsRatio, youngModulus=YoungsModulus, thickness = Thickness, method="large")
    SurfacePressureA = InflatableSurfaceA.addObject("SurfacePressureForceField", name="SurfacePressureA", pressure= 0, triangleIndices = InflateSurface.ElementIndices)
    #If it has a variable name it is interfacing with python
    InflatableSurfaceA.addObject("FixedProjectiveConstraint", name="AnchorA", indices= Anchor.Nodes)


    InflatableSurfaceB = Inflatable.addChild("InflatableSurfaceB")
    InflatableSurfaceB.addObject("TriangleSetTopologyContainer", name="topologyContainerB", src="@../GmshLoader2")
    InflatableSurfaceB.addObject("MechanicalObject", template="Vec3d", name="StateContainerB", showObject=True)
    InflatableSurfaceB.addObject("UniformMass", totalMass = Mass )
    InflatableSurfaceB.addObject("TriangleFEMForceField", template="Vec3d", poissonRatio=PoissonsRatio, youngModulus=YoungsModulus, thickness = Thickness, method="large")
    SurfacePressureB = InflatableSurfaceB.addObject("SurfacePressureForceField", name="SurfacePressureB", pressure= 0, triangleIndices = InflateSurface.ElementIndices)
    #Needed for use in controller#
    InflatableSurfaceB.addObject("FixedProjectiveConstraint", name="AnchorB", indices= Anchor.Nodes)
    


    ##### Weld ######
    #There are options for what weld type to use Lagrange or simple SpringForceFields

    Inflatable.addObject("SpringForceField", name = "Weld",
                         object1 = "@InflatableSurfaceA/StateContainerA",  object2 = "@InflatableSurfaceB/StateContainerB",
                         springsIndices1 = Weld.Nodes, springsIndices2 = Weld.Nodes, stiffness = [100000], lengths =[0])



    #### Collision #####

    collisionlModelANW = InflatableSurfaceA.addChild("collisionlModelANW")
    collisionlModelANW.addObject("TriangleSetTopologyContainer", name="Collision_A_No_Welds", src="@../topologyContainerA", triangles = NoWeld.ElementIndices)
    collisionlModelANW.addObject("MechanicalObject", name="StoringForcesANW")
    collisionlModelANW.addObject("TriangleCollisionModel", name="TriCollisionModelA", contactStiffness=10, selfCollision = 1, bothSide = 1)
    # collisionlModelANW.addObject("LineCollisionModel", name="LineCollisionModelA", contactStiffness=10, selfCollision = 1, bothSide = 1)
    # collisionlModelANW.addObject("PointCollisionModel", name="PointCollisionModelA", contactStiffness=10, selfCollision = 1, bothSide = 1)
    collisionlModelANW.addObject('IdentityMapping', input="@../StateContainerA", output="@StoringForcesANW")

    collisionlModelAW = InflatableSurfaceA.addChild("collisionlModelAW")
    collisionlModelAW.addObject("TriangleSetTopologyContainer", name="Collision_A_Welds", src="@../topologyContainerA", triangles = Weld.ElementIndices)
    collisionlModelAW.addObject("MechanicalObject", name="StoringForcesAW")
    collisionlModelAW.addObject("TriangleCollisionModel", name="TriCollisionModelAW", contactStiffness=10, selfCollision = 1, bothSide = 1)
    # collisionlModelAW.addObject("LineCollisionModel", name="LineCollisionModelAW", contactStiffness=10, selfCollision = 1, bothSide = 1)
    # collisionlModelAW.addObject("PointCollisionModel", name="PointCollisionModelAW", contactStiffness=10, selfCollision = 1, bothSide = 1)
    # collisionlModelANW.addObject("BarycentricMapping", name="VisualMapping", input="@../StateContainer", output="@StoringForces") # Barycentric mapping connecting the two representations with different topologies
    collisionlModelAW.addObject('IdentityMapping', input="@../StateContainerA", output="@StoringForcesAW")

    collisionlModelBNW = InflatableSurfaceB.addChild("collisionlModelBNW")
    collisionlModelBNW.addObject("TriangleSetTopologyContainer", name="Collision_B_No_Welds", src="@../topologyContainerB", triangles = NoWeld.ElementIndices)
    collisionlModelBNW.addObject("MechanicalObject", name="StoringForcesBNW")
    collisionlModelBNW.addObject("TriangleCollisionModel", name="TriCollisionModelB", contactStiffness=10, selfCollision = 1, bothSide = 1)
    # collisionlModelBNW.addObject("LineCollisionModel", name="LineCollisionModelB", contactStiffness=10, selfCollision = 1, bothSide = 1)
    # collisionlModelBNW.addObject("PointCollisionModel", name="PointCollisionModelB", contactStiffness=10, selfCollision = 1, bothSide = 1)
    # collisionlModelANW.addObject("BarycentricMapping", name="VisualMapping", input="@../StateContainer", output="@StoringForces") # Barycentric mapping connecting the two representations with different topologies
    collisionlModelBNW.addObject('IdentityMapping', input="@../StateContainerB", output="@StoringForcesBNW")


    ##### Define controllers #####
    PressureControlA = PressureController( SOFAfield = SurfacePressureA, name = "PressureControlA", targetVal= 200)
    InflatableSurfaceA.addObject(PressureControlA)
    monitor.AddController(PressureControlA, "Pressure", W = 10, S = -10)
    #by adding to monitor can change values with key press

    PressureControlB = PressureController( SOFAfield = SurfacePressureB, name = "PressureControlB", maxVal = 0, minVal = -30000, targetVal= -200)
    InflatableSurfaceB.addObject(PressureControlB)
    monitor.AddController(PressureControlB, "Pressure", W = -10, S = 10 )

    monitor.ControllerInfo()
    #print info about all controllers in scene
        


# Function used only if this script is called from a python environment
if __name__ == "__main__":
    main()