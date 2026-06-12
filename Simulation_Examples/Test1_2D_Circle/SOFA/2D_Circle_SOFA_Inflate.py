#runSofa 2D_Circle_SOFA_Inflate.py -l SofaPython3


def createScene(rootNode):
    #Name of root node
    rootNode.name.value = "rootNode"
    #time step, S
    rootNode.dt = 0.01
    #gravity in mS-2
    rootNode.gravity.value = [ 0., -9.81 ,0.]


    rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.MechanicalLoad',
                                                'Sofa.Component.LinearSolver.Iterative','Sofa.Component.ODESolver.Backward',
                                                'Sofa.Component.IO.Mesh','Sofa.Component.Topology.Container.Dynamic',
                                                'Sofa.Component.SolidMechanics.FEM.Elastic','Sofa.Component.Topology.Container.Constant',
                                                'Sofa.Component.Visual','Sofa.Component.Mapping.Linear','Sofa.GL.Component.Rendering3D',
                                                'Sofa.Component.Constraint.Projective','Sofa.Component.Engine.Select',
                                                'Sofa.Component.Constraint.Lagrangian.Correction','Sofa.Component.Constraint.Lagrangian.Model',
                                                'Sofa.Component.Constraint.Lagrangian.Solver','Sofa.Component.LinearSolver.Direct',
                                                'Sofa.Component.AnimationLoop','Sofa.GUI.Component'])


    rootNode.addObject("DefaultAnimationLoop", computeBoundingBox=True)
    #free motion animation loop needed for lagrangian constraints

    GmshLoader = rootNode.addObject("MeshGmshLoader", name='GmshLoader', filename=r"..\Test1_2D_Circle.msh")

    group1indices = list(range(21647, 31626))

    master_triangles = GmshLoader.triangles.value
    print(master_triangles)
    target_subset_triangles = master_triangles[21647 : 31626]


    # Subset = rootNode.addObject('SubsetTopology', name="group1", indices = group1indices)
    
    # print("--- GMSH DEBUG ---")
    # print("Filename used:", rootNode.GmshLoader.filename.value)
    # print("Triangle Groups:", rootNode.GmshLoader.triangleGroups)
    # print("------------------")

    rootNode.addObject('VisualStyle', displayFlags='showForceFields showCollisionModels showBehaviorModels showDetectionOutputs')
    #tells SOFA what models are allowed to be showed

    Circle_2D_Mechanical = rootNode.addChild("Circle_2D")

    Circle_2D_Mechanical.addObject("EulerImplicitSolver")
    Circle_2D_Mechanical.addObject("CGLinearSolver", iterations=200, tolerance=1e-09, threshold=1e-09)

    #Circle_2D_Mechanical.addObject("TriangleSetTopologyContainer", name="topologyContainer", src="@../GmshLoader",  triangles=target_subset_triangles )
    Circle_2D_Mechanical.addObject("TriangleSetTopologyContainer", name="topologyContainer", src="@../GmshLoader")

    Circle_2D_Mechanical.addObject("MechanicalObject", template="Vec3", name="StateContainer", showObject=True)

    Circle_2D_Mechanical.addObject('TriangleFEMForceField', template='Vec3', poissonRatio=0.3, youngModulus=100)
    #need a correct youngs modulus and also to get the units of mesh!

    #print(rootNode.GmshLoader.edgesGroups.value)
    print(GmshLoader.tags.getValueString())

    triangleArray = GmshLoader.triangles.value

    print(len(triangleArray))

    print(GmshLoader.Groups.getValueString())



    # visual_node = Circle_2D_Mechanical.addChild("visual_node")

    # Circle_2D_Mechanical.addObject('TriangleSetTopologyContainer', 
    #                                          name='SubsetContainer',
    #                                          position='@../AllPoints.position',
    #                                          tags=group1indices)

    #Circle_2D_Mechanical.addObject('OglModel', name="VisualModel", topology="@topologyContainer") # Connect with the object topology (could be connected to the mesh loader too)




    




"""Attempt at writing all the ones I think I need below, to be updated for future"""
    # rootNode.addObject("RequiredPlugin", pluginName=[
    #     'SoftRobots',#soft robots plugin
    #     'Sofa.Component.AnimationLoop',#for free motion animation loop
    #     'Sofa.Component.IO.Mesh',#mesh loader
    #     'Sofa.Component.StateContainer', #???
    #     'Sofa.Component.Topology.Container.Constant', #Mesh topologies are kept constant
    #     'Sofa.Component.SolidMechanics.FEM.Elastic',#FEM solver
    #     'Shell',
    #     'Sofa.Component.' ])





