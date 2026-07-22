# Simulating_Surface_Based_Inflatables
Simulation of Surface Based inflatables

Geometry creation done in Rhino, grasshopper script used to outline welds and flatten surfaces

GMSH used in simulation meshing to convert this to a MESH
    upload STEP files and JSON
    ****Could make it so that all you need is lasercutter file? could possibly put 

SOFA script examples available - uses Surfacebased inflatables which defines:
new gmsh loader
Pressure controller
Surface Inflatable balloon class
    Uses triangular contacts
    Lightweight - can approximate spring stiffness
    Heavyweight  - can use lagrangian constraints and contacts

    Shell by default but can switch to membrane if inflatable will only be in tension (although no need to use SOFA in that case really?)


