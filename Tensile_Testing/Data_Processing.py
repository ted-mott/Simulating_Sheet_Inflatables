import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

"""___Variables___"""

# #Initial sample size in mm, data is in m/N/s
SampleWidth = 20.0
SampleThickness = 0.063
#250 Gauge
SampleLength = 80.0

SampleCrossSectionArea = SampleWidth * SampleThickness
#in mm^2

# #Youngs Modulus region of interest
LowerDisplacementTarget = 0.5
UpperDisplacementTarget = 6.0

#From test start to end
TestNumStart = 41
TestNumEnd = 60

FolderPath = r"C:\Users\ucemeam\OneDrive - University College London\git\Simulating_Surface_Based_Inflatables\Tensile_Testing\Tensile_Test_05-05-2026"
#change the filename naming convention in function as required



"""___Functions___"""
def MakeFileName(TestNum):
    #Make Filename from test num
    Filename = "TensileRH_72_" + str(TestNum) + "_1.csv"
    #Tensile Test .csv naming convention
    return(Filename)


def ImportData(Filename, FolderPath):
    
    data_types = {
        'Time' : float,
        'Displacement' : float,
        'Force' : float
    }

    DataFrame  = pd.read_csv(os.path.join(FolderPath, FileName), skiprows = [1] )
    return(DataFrame)

   
def UltimateTensileStrength(Data, SampleCrossSectionArea):
    #Maximum force/ orginal area

    ForceMax = Data['Force'].max()
    #ForceMax in N

    Sample_UTS = float(ForceMax) / (SampleCrossSectionArea * 10**-6)

    return(Sample_UTS)


def YoungsModulus(Data, SampleCrossSectionArea, SampleLength):
    #Find forces at displacement value, this can then be used to calculate youngs modulus

    AboveTarget = Data['Displacement'].where(Data['Displacement'] > LowerDisplacementTarget)
    Loweridx = AboveTarget.idxmin()
    LowerTime, LowerDisplacement, LowerForce = Data.iloc[Loweridx]

    BelowTarget = Data['Displacement'].where(Data['Displacement'] < UpperDisplacementTarget)
    Upperidx = BelowTarget.idxmax()
    UpperTime, UpperDisplacement, UpperForce = Data.iloc[Upperidx]

    Youngs_Modulus = CalculateYoungsModulus(LowerForce, LowerDisplacement, UpperForce, UpperDisplacement, SampleCrossSectionArea, SampleLength)

    return(Youngs_Modulus)


def CalculateYoungsModulus(ForceA, DisplacementA, ForceB, DisplacementB, CrossSectionalArea, OriginalLength):
    #Youngs modulus =  stress / strain, stress = F/A, strain = change in length/ original length
    
    DeltaF = ForceB - ForceA
    DeltaDisplacement = DisplacementB - DisplacementA

    EngineeringStress = DeltaF / (CrossSectionalArea * 10**-6)
    Strain = DeltaDisplacement / OriginalLength

    E = EngineeringStress/Strain

    return(E)


def YieldStrength(Data, YoungsModulus, OriginalLength, CrossSectionalArea):
    #Find slope and use this to find Yield Strength
    Offset = 0.002 * OriginalLength * 10**-3

    OffsetData = ((Data['Displacement']* 10**-3/(OriginalLength * 10**-3)) - Offset) * YoungsModulus * CrossSectionalArea * 10**-6
    BelowOffset = Data['Force'].where(Data['Force'] < OffsetData)
    YieldIdx = BelowOffset.first_valid_index()

    YieldForce = Data['Force'].iloc[YieldIdx]
    YieldStrength = YieldForce / (CrossSectionalArea * 10**-6)

    return(YieldStrength)

    combineddf = Data.join(BelowOffset, lsuffix='_data', rsuffix='_offset')

    print(combineddf)
    ax = combineddf.plot(kind='scatter', x='Displacement', y='Force_data', color = 'blue')
    combineddf.plot(kind='scatter', x='Displacement', y='Force_offset', color = 'red', ax=ax)
    plt.show()

    return(YieldStrength)







def ExportCSV():
    pass


def Interpolate():
    pass
#using pandas
#interpolate data

#calculate mean and standard dev and append

def Plot():
    pass
    #plot data in matplotlib
    #save data as pdf



if __name__ == "__main__":
    MaterialProperties = pd.DataFrame(columns = ["test_id", "UTS (Pa)", "Youngs_Modulus (Pa)", "Yield_Strength (Pa)", "Max Displacement(mm)"])

    TestNum = TestNumStart

    FileName = MakeFileName(TestNum)

    while TestNumStart <= TestNum and TestNum <= TestNumEnd:

        if os.path.exists(os.path.join(FolderPath, FileName)):
            
            FileName = MakeFileName(TestNum)

            Data = ImportData(FileName, FolderPath)
            #CSV in format time, displacement, force

            Ult_Ten_Strength = UltimateTensileStrength(Data, SampleCrossSectionArea)

            Youngs_Modulus = YoungsModulus(Data, SampleCrossSectionArea, SampleLength)

            Yield_Strength = YieldStrength(Data, Youngs_Modulus, SampleLength, SampleCrossSectionArea)
            
            MaxDisplacement = Data['Displacement'].max()

            MaterialProperties.loc[len(MaterialProperties)] = [FileName, Ult_Ten_Strength, Youngs_Modulus, Yield_Strength, MaxDisplacement]

          
            
            # Interpolate()

            # Plot()

            TestNum = TestNum + 1

    MaterialPropertiesSummary = MaterialProperties.describe()
    
    print(MaterialPropertiesSummary)    
    print(MaterialProperties)

    OutputFilename = str(TestNumStart) + "_to_" + str(TestNumEnd)

    MaterialProperties.to_csv(OutputFilename + ".csv", float_format="{:.2e}".format)
    MaterialPropertiesSummary.to_csv(OutputFilename + "_summary.csv", float_format="{:.2e}".format)

