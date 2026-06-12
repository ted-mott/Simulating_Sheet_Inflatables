import pytest
from Data_Processing import *

def test_filename_output_format_int():
    Filename = MakeFileName(5)
    assert Filename == "TensileRH_72_5_1.csv"


def test_CalculateYoungsModulus_int():
    testE = CalculateYoungsModulus(1, 1, 2, 2, 1, 1)
    #CalculateYoungsModulus(ForceA, DisplacementA, ForceB, DisplacementB, SampleCrossSectionArea, SampleLength)
    assert testE == 1

