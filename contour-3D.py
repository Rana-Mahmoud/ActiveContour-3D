# This script implments 3D active contours on brain tumor data 3D volume .mha files
# import needed packages
import os
import numpy
import vtk
# ======= Load .mha file ==========
def load_mha():
	# helper link:
	# https://pyscience.wordpress.com/2014/11/16/volume-rendering-with-python-and-vtk/
	#---------------------------------
	# Path to the .mha file
	big_tomur   = "./VSD.Brain.XX.O.MR_Flair.54512.mha"
	small_tomur = "./VSD.Brain.XX.O.MR_T1c.54514.mha"
	# Opacity of the different volumes (between 0.0 and 1.0)
	volOpacityDef = 0.25
	# load the label-field under the provided .mha file.
	reader = vtk.vtkMetaImageReader()
	reader.SetFileName(big_tomur)
	castFilter = vtk.vtkImageCast()
	castFilter.SetInputConnection(reader.GetOutputPort())
	castFilter.SetOutputScalarTypeToUnsignedShort()
	castFilter.Update()
	imdataBrainSeg = castFilter.GetOutput()
### End Load_mha()
load_mha()