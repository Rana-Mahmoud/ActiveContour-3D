# This script implments 3D active contours on brain tumor data 3D volume .mha files
# import needed packages
import os
import numpy
import vtk
import csv
# ===== Load coloring data ========
def load_color_codes(colorfilename):
	''' The first integer is the label index,
	the same way it appears within the image data. 
	That is followed by the name of that tissue and 
	three integer values between 0 and 255 for the RGB color.'''
	fid = open(colorfilename, "r")
	reader = csv.reader(fid)
	dictRGB = {}
	''' Note that we are skipping the tissue name and more importantly that we are normalizing 
	the color values to a value between 0.0 and 1.0 as this is the range that VTK expects.  '''
	for line in reader:
	    dictRGB[int(line[0])] = [float(line[2])/255.0,
	                             float(line[3])/255.0,
	                             float(line[4])/255.0]
	fid.close()
	return dictRGB
# ======= Load .mha file ==========
def load_mha():
	# helper link:
	# https://pyscience.wordpress.com/2014/11/16/volume-rendering-with-python-and-vtk/
	#---------------------------------
	# Path to the .mha file
	big_tomur   = "./VSD.Brain.XX.O.MR_Flair.54512.mha"
	small_tomur = "./VSD.Brain.XX.O.MR_T1c.54514.mha"
	testing_sample = "./home/rana/Desktop/brain/nac_brain_atlas/brain_segmentation.mha"
	# Path to colorfile.txt 
	filenameColorfile = "/home/rana/Desktop/brain/nac_brain_atlas/colorfile.txt"
	# Opacity of the different volumes (between 0.0 and 1.0)
	volOpacityDef = 0.25
	# load the label-field under the provided .mha file.
	"""initially create a new vtkMetaImageReader object under reader 
	set the filename from which to read,"""
	reader = vtk.vtkMetaImageReader()
	reader.SetFileName(big_tomur)
	castFilter = vtk.vtkImageCast()
	castFilter.SetInputConnection(reader.GetOutputPort())
	castFilter.SetOutputScalarTypeToUnsignedShort()
	castFilter.Update()
	imdataBrainSeg = castFilter.GetOutput()
	print ("Load colores text successfully")
	# ======= Pre Rendering work ============
	print ("----Pre Rendering work------")
	#------------ Load colors data -----------
	'''Return : a dictionary dictRGB where the index-label acts as the key and
	 the value is a list with the RGB color assigned to that tissue.'''
	dictRGB = load_color_codes(filenameColorfile)
	print ("dictRGB :", len(dictRGB) )
	# define the color function in VTK 
	funcColor = vtk.vtkColorTransferFunction()
	for idx in dictRGB.keys():
	    funcColor.AddRGBPoint(idx, 
	                          dictRGB[idx][0],
	                          dictRGB[idx][1],
	                          dictRGB[idx][2])
	#print("funcColor :", funcColor)
	print ("Pre 1 : set VTK colores successfully")
	# ------------ Set Scalar opacity function  -------------
	'''Now that the color-function has been defined we need to define a scalar opacity function. 
	This will work in a similar manner with the difference being that we will use it to simply 
	match each label to an opacity value. '''
	funcOpacityScalar = vtk.vtkPiecewiseFunction()
	for idx in dictRGB.keys():
	    funcOpacityScalar.AddPoint(idx, volOpacityDef if idx<>0 else 0.0)
	print ("Pre 2 : set VTK Scalar opacity successfully")












### End Load_mha()
load_mha()
