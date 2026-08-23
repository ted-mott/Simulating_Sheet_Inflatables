# Simulating_Surface_Based_Inflatables
Simulation of Surface Based inflatables

Geometry creation done in Rhino. Grasshopper script used to outline welds and flatten surfaces. Surfaces exported as STEP files.
    
GMSH used in simulation meshing to convert STEP files to .msh files, mesh script also produces JSON to help redefine physical groups in SOFA
    New GMSH meshing : https://github.com/ted-mott/Simulating_Sheet_Inflatables/blob/main/Surface_Based_inflatables_Meshing.py
    Old GMSH meshing : https://github.com/ted-mott/Simulating_Sheet_Inflatables/blob/main/Outdated/Surface_Based_Inflatables_Meshing/Simulation_Meshing.py

SOFA script examples available:
    New SOFA examples : https://github.com/ted-mott/Simulating_Sheet_Inflatables/tree/main/Simulation_SOFA

Extended SOFA functions with python wrapper:
    https://github.com/ted-mott/Simulating_Sheet_Inflatables/blob/main/Simulation_SOFA/Surface_Based_Inflatables_SOFA.py
    
    Extended GMSH loader - can access physical groups
    Extended controller - controller monitor can update multiple controller per scene

