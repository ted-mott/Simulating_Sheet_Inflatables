"""
Simulation_Meshing.py
Using to create a GMSH file that can be used in Abaqus or SOFA
27.01.2026
Ted M
________________________________________________________________________________________________
"""

"""
Libraries
________________________________________________________________________________________________
"""
import gmsh
import os
import numpy as np


"""
Functions
________________________________________________________________________________________________
""" 

def UI_Set_Variable(variable, variable_Name, Default_Setting):
    #Function used for simple command line UI to set parameters

    if Default_Setting:
        return(variable)
    
    #UI to set variables
    print(variable_Name + ": " , variable, "\nWould you like to change this?  y/n" )
    Change_Variable = input()
    if Change_Variable  == "y" or Change_Variable == "Y":
        print("Input New " + variable_Name + ": ")
        variable = input()
        print("New " + variable_Name + ": " , variable)

    return(variable)
    

def Curve_Loop_Generator(Curve_List):
    #Function generates curve loops, good for planar curves, can be used to find which curves are open adnd closed for fragment

    Closed_Loop_List = []
    Open_Loop_List = []

    for Curve in Curve_List:
        Curve_id = Curve[1]

        try:
            (gmsh.model.occ.addCurveLoop([Curve_id]))
            #curve loop id 
            Closed_Loop_List.append(Curve_id)
            print("Curve ", Curve_id, " is closed")
            
        except:
            Open_Loop_List.append(Curve_id)
            print("Curve ", Curve_id, " is open")

    return(Closed_Loop_List, Open_Loop_List)


def TagFromList(entityList):
    #Function to strip tags out of list of (dim,tag) used for physical groups
    tags = []
    for entity in entityList:
        tag = entity[1]
        tags.append(tag)

    return(tags)
    

def PhysicalGroupTag2Dim(Physical_Group_Tag):
    #Returns physical group dim from tag
    PhysicalGroups = gmsh.model.getPhysicalGroups()
    for dim,tag in PhysicalGroups:
        if tag == Physical_Group_Tag:
            return dim


def ConstructDimTag(dim, tags):
    #takes dim of group and list of tags, gmsh is not consistent with whether to use dim tags or list of tags.
    dim_tag = []
    for tag in tags:
        dim_tag.append((dim, tag))
    return(dim_tag)


def FragmentSurface(Surface_DimTag_List: list[int], Curve_DimTag_List: list[int]):
    #fragments surface into multiple surfaces using curves - returns orginal surface and created surfaces

    gmsh.model.occ.synchronize()
    surfaces_before = set(gmsh.model.occ.getEntities(dim=2))

    gmsh.model.occ.fragment(Surface_DimTag_List, Curve_DimTag_List)
    #default args fragment(objectDimTags, toolDimTags, tag=-1, removeObject=True, removeTool=True)
    gmsh.model.occ.synchronize()

    surfaces_after = set(gmsh.model.occ.getEntities(dim=2))
    surfaces_created = surfaces_after.difference(surfaces_before)
    CurveSurfaces = list(surfaces_created)
    #comparing surfaces before to after

    gmsh.model.occ.synchronize()

    if Surface_DimTag_List[0] in surfaces_after:

        print("surface exists", Surface_DimTag_List)
        
        return(Surface_DimTag_List, CurveSurfaces)
    
    else:
        print("surface destroyed, assuming main surface is largest")

        surfaces_sorted = sorted(CurveSurfaces, key=Area, reverse=True)
        #using sorted, takes list of surface dim tags, calculates Boundingbox size and returns list in order of largest to smallest
        MainSurface = surfaces_sorted[0]
        CurveSurfaces.remove(MainSurface)

        print("MainSurface", MainSurface)

        return([MainSurface], CurveSurfaces)


def Area(dimtag):
    #calculates area using dim tag
    dim, tag  = dimtag
    area = gmsh.model.occ.getMass(dim, tag)
    return(area)


def Duplicate(Physical_Group):
    #Function used to copy physical groups so that inflatable has 2 layers

    gmsh.model.occ.synchronize()

    entities = gmsh.model.getEntitiesForPhysicalName(Physical_Group)
    Group_dim = entities[0][0]
    #[0][0] gives dim of first item, in a physical group this must be the same as that is how they are set
    
    copied_entities = []

    for dim,tag in entities:
        copied = gmsh.model.occ.copy([(dim, tag)])
        copied_entities.append(copied[0])

    gmsh.model.occ.synchronize()

    gmsh.model.add_physical_group(Group_dim, TagFromList(copied_entities), name= Physical_Group + "_Copy" )

    return(copied_entities)


def Meshing():
    #Function used for simple command line UI to set meshing element type

    print("Set Mesh ELement Type Quad(q) or Tri(t)? \n*Tri required for use with SOFA")
    element_type = input()
    
    if element_type == "q" or element_type == "Q":
        try:
            gmsh.option.setNumber("Mesh.RecombineAll", 1)
            #Option 1 for quad, 0 for tri
            gmsh.model.mesh.generate(2)
            #(2) corresponds to dimension of mesh generated, 2 = surface, 1 = curve .etc.
        except:
            print("Angle in curve to sharp for quad mesh, meshing with triangles...")
            gmsh.option.setNumber("Mesh.RecombineAll", 0) #if multiple surfaces
            gmsh.model.mesh.generate(2)
        #If quad mesh is not possible flags error and continues with triangle mesh
    else:
            gmsh.option.setNumber("Mesh.RecombineAll", 0) #if multiple surfaces
            gmsh.model.mesh.generate(2)


def SaveGMSH(Output_Folder_Path):
    #Function used for simple command line UI to set save file parameters

    print("Save GMSH file? y/n")
    GMSHSave = input()
    
    if GMSHSave == "y" or GMSHSave == "Y":

        Output_Filename = "Test2_2D-Patterned_Circle.msh"
        print("Set file extension as .inp for use in Abaqus or .msh for use in SOFA")
        Output_Filename = UI_Set_Variable(Output_Filename, "Output Filename", Default_Setting)
        
        Output_Filepath = os.path.join(Output_Folder_Path, Output_Filename )
        gmsh.write(Output_Filepath)
        #Save gmsh file

        print("Mesh saved at " + Output_Filepath)



"""
Main
________________________________________________________________________________________________
"""
if __name__ == "__main__":

    """Default Settings"""
    
    Default_Setting = True

    STEP_Folder_Path = "Simulation_Examples/Test2b_2D-Patterned_Circle_Surface_Split/STEP_geometry"
    #Default path defined here
    Output_Folder_Path = "Simulation_Examples/Test2b_2D-Patterned_Circle_Surface_Split/MESH"
    #Set as the path for output files
    lc = 4.0
    #Default Global element size
    gmsh.option.setNumber("Geometry.OCCImportTolerance", 1e-8)

    """"Input config"""

    # print("Use Default Settings? y/n")
    # Default_Option = input()
    # if Default_Option == "n" or Default_Option == "N":
    #     Default_Setting = False
    # #Default Setting added to save having to input over and over again
    
    STEP_Folder_Path = UI_Set_Variable(STEP_Folder_Path, "STEP Folder Path", Default_Setting)

    Output_Folder_Path = UI_Set_Variable(Output_Folder_Path, "Output Folder Path", Default_Setting)
    #UI set Output Folder Path

    lc = UI_Set_Variable(lc, "Global Element Size", Default_Setting)
    #User input for global element size

    gmsh.initialize()
    #initialises GMSH environment
        
    gmsh.clear()
    #clear all previous GMSH geometry

    gmsh.model.add("FlatShape_GMSH")


    """Import STEP files"""

    InflateSurface = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "InflateSurface.stp"))

    Outer = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Outer.stp"))

    Coincident_Curves = None
    if os.path.exists(os.path.join(STEP_Folder_Path, "Coincident.stp")):
         Coincident_Curves = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Coincident.stp"))
         print("Coincident.stp found")
    
    Anchor = None
    if os.path.exists(os.path.join(STEP_Folder_Path, "Anchor.stp")):
        Anchor = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Anchor.stp"))
        print("Anchor.stp found")

    
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()
    #Laser weld perimeter and Outer laser curve are the only expected files


    # CordPoints = None
    # if os.path.exists(os.path.join(STEP_Folder_Path, "Cord_Points.stp")):
    #     CordPoints = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Cord_Points.stp"))
    #     print("Cord_Points.stp found")

    # JoinCurves = None
    # if os.path.exists(os.path.join(STEP_Folder_Path, "Join_Curves.stp")):
    #     CordPoints = gmsh.model.occ.importShapes(os.path.join(STEP_Folder_Path, "Join_Curves.stp"))
    #     print("Join_Curves.stp found")


    """Curve Loops"""
   
    if Anchor:
        gmsh.model.occ.synchronize()
        AnchorSurfaces = TagFromList(Anchor)
        AnchorCurves = []
        for Surf in AnchorSurfaces:
            Curve = gmsh.model.occ.get_curve_loops(Surf)
            Curve = Curve[1][0][0]
            print(Curve)
            AnchorCurves.append(Curve)
        
        gmsh.model.addPhysicalGroup(2, AnchorSurfaces, name= "Anchor_Surfaces")
        Duplicate("Anchor_Surfaces")
    
        gmsh.model.addPhysicalGroup(1, AnchorCurves, name= "AnchorCurves")
        Duplicate("AnchorCurves")



    Coincident_Curves_Closed = None
    Coincident_Curves_Open = None
    
    if Coincident_Curves:
        gmsh.model.occ.synchronize()
        Coincident_Curves_Closed, Coincident_Curves_Open = Curve_Loop_Generator(Coincident_Curves)

        print(Coincident_Curves_Closed)
        #curve loop generator was used for creting simple surfaces but is now used to seperate whether curve is open or closed.
        #open loops are embedded and closed loops are used to fragment surface


    """Embedding curves in Surfaces"""
    gmsh.option.setNumber("Geometry.ToleranceBoolean", 1e-4)


    if Coincident_Curves_Closed :
        gmsh.model.occ.synchronize()
        InflateSurface, CoincidentSurface = FragmentSurface(InflateSurface, ConstructDimTag(1, Coincident_Curves_Closed))

        gmsh.model.addPhysicalGroup(2, TagFromList(CoincidentSurface), name = "Coincident_Surfaces")
        Duplicate("Coincident_Surfaces")

        gmsh.model.addPhysicalGroup(1, Coincident_Curves_Closed, name = "Coincident_Curves_Closed")
        Duplicate("Coincident_Curves_Closed")
        

    gmsh.model.occ.synchronize()
    
    Inflate_Perimeter = gmsh.model.occ.get_curve_loops(InflateSurface[0][1])
    #get curve loops from surface for use in further simulations

    gmsh.model.occ.synchronize()
    
    gmsh.model.addPhysicalGroup(1, Inflate_Perimeter[1][0], name = "Inflate_Perimeter")
    Duplicate("Inflate_Perimeter")
    
    gmsh.model.addPhysicalGroup(2, TagFromList(InflateSurface), name = "Inflate_Surface")
    Inflate_Surface_Duplicate = Duplicate("Inflate_Surface")

    gmsh.model.addPhysicalGroup(2, TagFromList(Outer), name = "Outer_Surface")
    Duplicate("Outer_Surface")


    if Coincident_Curves_Open:
        
        gmsh.model.occ.synchronize()

        gmsh.model.mesh.embed( 1, Coincident_Curves_Open, 2, InflateSurface[0][1])
            
        gmsh.model.addPhysicalGroup(1, Coincident_Curves_Open, name = "Coincident_Curves_Open")

        Coincident_Curves_Open_Duplicate = Duplicate("Coincident_Curves_Open")
        gmsh.model.mesh.reverse(Coincident_Curves_Open_Duplicate)
        
        print(Inflate_Surface_Duplicate[0][1])

        gmsh.model.mesh.embed(1, TagFromList(Coincident_Curves_Open_Duplicate), 2, Inflate_Surface_Duplicate[0][1])


    """Meshing"""

    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc)
    #set Global element size

    gmsh.model.occ.synchronize()
    #using open cascade, need to synchronise geometry with GMSH

    Meshing()

    gmsh.model.mesh.reverse(Inflate_Surface_Duplicate)


    """Output"""

    SaveGMSH(Output_Folder_Path) 

    print("Open GMSH window? y/n")
    GMSHWindow = input()
    if GMSHWindow == "y" or GMSHWindow == "Y":
        gmsh.fltk.run()
        #opens up GMSH pop up window
    
    gmsh.finalize()
    #end gmsh process