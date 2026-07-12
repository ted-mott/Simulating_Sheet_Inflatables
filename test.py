#runSofa test.py -l SofaPython3.so
def createScene(root_node):

   root = root_node.addChild('root', dt="0.01", gravity="0 0 0")

   root.addObject('RequiredPlugin', pluginName="Sofa.Component.AnimationLoop")
   root.addObject('RequiredPlugin', pluginName="Sofa.Component.Collision.Geometry")
   root.addObject('RequiredPlugin', pluginName="Sofa.Component.Constraint.Lagrangian.Correction")
   root.addObject('RequiredPlugin', pluginName="Sofa.Component.Constraint.Lagrangian.Solver")
   root.addObject('RequiredPlugin', pluginName="Sofa.Component.LinearSolver.Direct")
   root.addObject('RequiredPlugin', pluginName="Sofa.Component.Mass")
   root.addObject('RequiredPlugin', pluginName="Sofa.Component.ODESolver.Backward")
   root.addObject('RequiredPlugin', pluginName="Sofa.Component.SolidMechanics.Spring")
   root.addObject('RequiredPlugin', pluginName="Sofa.Component.StateContainer")
   root.addObject('RequiredPlugin', pluginName="Sofa.Component.Visual")
   root.addObject('VisualStyle', displayFlags=" showCollisionModels showForceFields")
   root.addObject('FreeMotionAnimationLoop', )
   root.addObject('BlockGaussSeidelConstraintSolver', maxIt="1000", tolerance="1e-10", printLog="false")

   object1 = root.addChild('Object1')

   object1.addObject('MechanicalObject', name="ms", template="Rigid3", position="0 0 0 0 0 0 0 1", showObject="false")
   object1.addObject('SphereCollisionModel', radius="0.01", color="0 1 0 1")

   object2 = root.addChild('Object2')

   object2.addObject('EulerImplicitSolver', rayleighMass="0", rayleighStiffness="0")
   object2.addObject('EigenSparseLU', template="CompressedRowSparseMatrix", name="LULinearSolver")
   object2.addObject('MechanicalObject', name="mstate", template="Rigid3", position="0.1 0 0  0  0 0 0 1")
   object2.addObject('SphereCollisionModel', color="1 0 0 1", radius="0.01")
   object2.addObject('RestShapeSpringsForceField', stiffness="11", angularStiffness="11", external_rest_shape="@../Object1/ms", points="0", external_points="0", drawSpring="true", springColor="1 1 1 1")
   object2.addObject('UniformMass', totalMass="0.01")
   object2.addObject('SphereCollisionModel', radius="0.0005", color="1 0 0  1")
   object2.addObject('LinearSolverConstraintCorrection', linearSolver="@LULinearSolver")