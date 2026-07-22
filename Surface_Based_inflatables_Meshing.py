import gmsh
import os
import numpy as np
import random
import json


#########################################################################################
""" new - 13.07.26 """
#########################################################################################


class MeshConfig:
        def __init__(self, filename, lc, Output_folder_path, Inflate_Surface_File_Path, Anchor_File_Path = None, Weld_File_Path = None, Free_Surface_File_Path = None, elementType = 0, meshDimension = 2, JSON_file_Location = None):
            #File Information
            self.filename = filename
            self.Output_folder_path = Output_folder_path
            self.JSON_file_Location = JSON_file_Location

            #Geometry Locations
            self.Inflate_Surface_File_Path = Inflate_Surface_File_Path
            self.Weld_File_Path = Weld_File_Path
            self.Anchor_File_Path = Anchor_File_Path
            self.Free_Surface_File_Path = Free_Surface_File_Path
            #Could be abstracted later

            #Mesh information
            self. lc = lc
            self.elementType = elementType
            #set element type as 2, this is tris in gmsh, this parameter very unlikely to change as it is for use with SOFA
            self.meshDimension = meshDimension
            #set meshdimension as 2, corresponding to surface, unlikely to every need volumes but who knows

        def readJSON(self, ):
            #read JSON information
            pass


def generateMesh(MeshConfig, saveMesh = True, openGMSH = False):
        
        ##### Initialising #####
        PhysicalGroups = {
              1 : {},
              2 : {},
              3 : {}
             }
        
        MeshEntities = {
              1 : {},
              2 : {},
              3 : {}
             }
        
        #Create dictionaries for information to pass SOFA, need to nest in dim as GMSH can have the same tags for different types

        gmsh.initialize()
        gmsh.clear()

        gmsh.model.add(MeshConfig.filename)

        ##### Import Geometry #####
        if MeshConfig.Inflate_Surface_File_Path:
            InflateSurface  = gmsh.model.occ.importShapes(MeshConfig.Inflate_Surface_File_Path)

        if MeshConfig.Weld_File_Path:
            Weld  = gmsh.model.occ.importShapes(MeshConfig.Weld_File_Path)

        if MeshConfig.Anchor_File_Path:
            Anchor  = gmsh.model.occ.importShapes(MeshConfig.Anchor_File_Path)
  
        if MeshConfig.Free_Surface_File_Path:
            FreeSurface  = gmsh.model.occ.importShapes(MeshConfig.Free_Surface_File_Path)
        #In future can try to do shape loading better, this requires you to export and import all the geometry separately and all geometry processes are done in grasshopper
        
        gmsh.model.occ.synchronize()

        gmsh.model.occ.removeAllDuplicates()

        ##### Physical Groups #####
        if MeshConfig.Inflate_Surface_File_Path:
            PhysicalGroup("InflateSurface", InflateSurface, PhysicalGroups, MeshEntities)
        
        if MeshConfig.Weld_File_Path:
            PhysicalGroup("Weld", Weld, PhysicalGroups, MeshEntities)
        
        if MeshConfig.Anchor_File_Path:
            PhysicalGroup("Anchor", Anchor, PhysicalGroups,MeshEntities)
        
        if MeshConfig.Free_Surface_File_Path:
            PhysicalGroup("FreeSurface", FreeSurface, PhysicalGroups,MeshEntities)

        ###### Meshing ######
        gmsh.model.occ.synchronize()
        #Literally cannot overdo this command in gmsh - all the problems will probably be as a result of not having it
        
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", MeshConfig.lc)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", MeshConfig.lc)
        #set Global element size

        #gmsh.option.setNumber("Mesh.SaveAll", 1)
        #Change if you want to save things outside of a physical group
        
        gmsh.model.mesh.SaveWithoutOrphans = 1
        #removes orphan nodes from output file

        gmsh.option.setNumber("Mesh.RecombineAll", MeshConfig.elementType) #if multiple surfaces, also 
        gmsh.model.mesh.generate(MeshConfig.meshDimension)

        gmsh.model.mesh.removeDuplicateNodes()
        #remove duplicate nodes in whole mesh, ensures mesh connectivity

        ###### Saving ######

        if saveMesh:
            Output_Filepath = os.path.join(MeshConfig.Output_folder_path, MeshConfig.filename + "_LC" + str(MeshConfig.lc) )
            gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
            #need this for current SOFA loader but if I make my own this could change things entirely
            gmsh.write(Output_Filepath + ".inp")
            gmsh.write(Output_Filepath + ".msh")

            GenerateSOFAbridgefile(PhysicalGroups, MeshEntities,  Output_Filepath)
            
        print(MeshEntities)

        if openGMSH:
            gmsh.fltk.run()

        gmsh.finalize()

        if saveMesh:
            return PhysicalGroups, MeshEntities,  Output_Filepath + ".msh"
        else:
             return None, None



def PhysicalGroup(name, dimTags,PhysicalGroups, MeshEntities):
    #define physical group, it appends this to a dictionary, and then a JSON file to use with SOFA
    gmsh.model.occ.synchronize()
    
    PhysicalGroupCount = gmsh.model.getPhysicalGroups()
    PhysicalGroupTag = len(PhysicalGroupCount) + 1

    #Define tag for referencing nodes and coordinates later
    EntityCount = len(dimTags)

    MaxDim = 0
    Tags = []
    for dim, tag in dimTags:
        if dim > MaxDim:
              MaxDim = dim
        Tags.append(tag)

        MeshEntities[dim][tag] = {
            "PhysicalGroupTag" : PhysicalGroupTag    
        }
    #Get dimTags into format required for addPhysicalGroup
        
    gmsh.model.addPhysicalGroup(dim = MaxDim, tags = Tags, tag = PhysicalGroupTag , name= name)
    
    PhysicalGroups[MaxDim][name] = {
            "name" : name,
            "PhysicalGroupTag" : PhysicalGroupTag,
            "EntityCount" : EntityCount,
            "Entities" : Tags
            #dim and tag correspond to physical group
         }
    #Create physical group dictionary for use with SOFA


def GenerateSOFAbridgefile(PhysicalGroups, MeshEntities, Output_Filepath):
    #Generate a dictionary that can be passed to SOFA, save as a JSON file with meshes
    for dim, dimdict in MeshEntities.items():
         print(dim)
         for tag, tagdict in dimdict.items():
            print(tag)
            #Nodes , Coords = gmsh.model.mesh.getNodes(2, 1)
            Nodes , Coords, _ = gmsh.model.mesh.getNodes(dim, tag)
            print(Nodes)
            #Retrieve all nodes and coordinates in mesh belingnig to physical group
            NodeCount = len(Nodes)
            NodeSample = []
            CoordinateSample =[]

            for i in range(5):
                #Sample 5 random nodes and get the coordinates
                NodeIndex = random.randint(0, NodeCount - 1)
                ChosenNodeTag = Nodes[NodeIndex]
                x = Coords[3*NodeIndex]
                y = Coords[3*NodeIndex + 1]
                z = Coords[3*NodeIndex + 2]
                #coordinate array is in form [x1,y1,z1,x2...]
                NodeCoordinates = [float(x), float(y), float(z)]
                NodeSample.append(int(ChosenNodeTag))
                CoordinateSample.append(NodeCoordinates)
                #Have to convert from NumPy for JSON file dumping
            
            tagdict.update({
                "NodeCount": NodeCount,
                "SampleNodes": NodeSample,
                "SampleCoords": CoordinateSample
         })
            
    SOFABridgeDict = {
        "MeshEntities" : MeshEntities,
        "PhysicalGroups" : PhysicalGroups
    }

    with open(Output_Filepath + ".json" , "w") as file:
        json.dump(SOFABridgeDict, file, indent=4)
              
            


if __name__ == "__main__":
    config = MeshConfig(filename = "Sim1_2D_Circle", lc = 4 ,
                        Output_folder_path = r"C:\Users\ucemeam\OneDrive - University College London\git\Simulating_Surface_Based_Inflatables\Simulation_SOFA\Sim1_2D_Circle\MESH_geometry",
                        Inflate_Surface_File_Path = r"C:\Users\ucemeam\OneDrive - University College London\git\Simulating_Surface_Based_Inflatables\Simulation_SOFA\Sim1_2D_Circle\STEP_geometry\Inflate.stp",
                        Anchor_File_Path = r"C:\Users\ucemeam\OneDrive - University College London\git\Simulating_Surface_Based_Inflatables\Simulation_SOFA\Sim1_2D_Circle\STEP_geometry\Anchor.stp",
                        Weld_File_Path = r"C:\Users\ucemeam\OneDrive - University College London\git\Simulating_Surface_Based_Inflatables\Simulation_SOFA\Sim1_2D_Circle\STEP_geometry\Weld.stp",
                        Free_Surface_File_Path = r"C:\Users\ucemeam\OneDrive - University College London\git\Simulating_Surface_Based_Inflatables\Simulation_SOFA\Sim1_2D_Circle\STEP_geometry\Free.stp")
    
    
    # config = MeshConfig.readJSON(r"C:\Users\ucemeam\OneDrive - University College London\git\Simulating_Surface_Based_Inflatables\Simulation_SOFA\Sim1_2D_Circle\Sim1config.JSON")
    PhysicalGroups, MeshEntities, MshFilePath = generateMesh(config, saveMesh = True, openGMSH = True)

