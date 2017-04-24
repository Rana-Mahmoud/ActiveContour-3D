# This script implments 3D active contours on brain tumor data 3D volume .mha files
# import needed packages
import os
import cv2
import vtk
import math
import cmath
import numpy
from vtk.util import numpy_support
# ======= Load .mha file ==========
def load_mha():
	# helper link:
	# https://pyscience.wordpress.com/2014/11/16/volume-rendering-with-python-and-vtk/
	#---------------------------------
	# Path to the .mha file
	big_Tumor   = "VSD.Brain.XX.O.MR_Flair.54512.mha"
	small_Tumor = "VSD.Brain.XX.O.MR_T1c.54514.mha"
	# load the label-field under the provided .mha file.
	"""initially create a new vtkMetaImageReader object under reader 
	set the filename from which to read,"""
	reader = vtk.vtkMetaImageReader()
	reader.SetFileName(big_Tumor)
	reader.Update()
	# Next we need access to the metadata in order to 
	# calculate those ConstPixelDims and ConstPixelSpacing variables:
	# Load dimensions using `GetDataExtent`
	_extent = reader.GetDataExtent()
	ConstPixelDims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]
	# Check dimentions of the 3D object
	# dimentions [240, 240, 155]
	print("ConstPixelDims: ",ConstPixelDims) 
	# Load spacing values 
	# ElementSpacing = 1.0 1.0 1.0
	# (0.40039101243019104, 0.40039101243019104, 0.4499969482421875)
	ConstPixelSpacing = ( 1.0 ,1.0 ,1.0 )
	# Load all the pixel data into an appropriate sized NumPy array named bigTumorArr
	x = numpy.arange(0.0, (ConstPixelDims[0]+1)*ConstPixelSpacing[0], ConstPixelSpacing[0])
	y = numpy.arange(0.0, (ConstPixelDims[1]+1)*ConstPixelSpacing[1], ConstPixelSpacing[1])
	z = numpy.arange(0.0, (ConstPixelDims[2]+1)*ConstPixelSpacing[2], ConstPixelSpacing[2])
	# Get the 'vtkImageData' object from the reader
	imageData = reader.GetOutput()
	print("imageData :",imageData)
	# Get the 'vtkPointData' object from the 'vtkImageData' object
	pointData = imageData.GetPointData()
	print("pointData :",pointData)
	# Ensure that only one array exists within the 'vtkPointData' object
	assert (pointData.GetNumberOfArrays()==1)
	# Get the `vtkArray` (or whatever derived type) which is needed for the `numpy_support.vtk_to_numpy` function
	arrayData = pointData.GetArray(0)
	print("arrayData : ",arrayData)
	# Convert the `vtkArray` to a NumPy array
	bigTumorArr = numpy_support.vtk_to_numpy(arrayData)
	# Reshape the NumPy array to 3D using 'ConstPixelDims' as a 'shape'
	bigTumorArr = bigTumorArr.reshape(ConstPixelDims, order='F')
	print("Dimensions of Big tumor Array : ", bigTumorArr.shape) 
	return bigTumorArr , reader
### End Load_mha()
def render_brainVolume(reader):
	# Create the renderer, the render window, and the interactor. The
	# renderer draws into the render window, the interactor enables mouse-
	# and keyboard-based interaction with the scene.
	aRenderer = vtk.vtkRenderer()
	renWin = vtk.vtkRenderWindow()
	renWin.AddRenderer(aRenderer)
	iren = vtk.vtkRenderWindowInteractor()
	iren.SetRenderWindow(renWin)
	# An isosurface, or contour value of 500 is known to correspond to the
	# brain of the patient. Once generated, a vtkPolyDataNormals filter is
	# is used to create normals for smooth surface shading during rendering.
	# The triangle stripper is used to create triangle strips from the
	# isosurface these render much faster on may systems.
	brainExtractor = vtk.vtkContourFilter()
	brainExtractor.SetInputConnection(reader.GetOutputPort())
	brainExtractor.SetValue(1, 100)
	# Helper link :
	# http://www.programcreek.com/python/example/11893/vtk.vtkContourFilter
	# example 3
	# set disc
	decibrain = vtk.vtkDecimatePro()
	decibrain.SetInputConnection(brainExtractor.GetOutputPort())
	decibrain.SetTargetReduction(.1)
	decibrain.PreserveTopologyOn()
	# Use a filter to smooth the data (will add triangles and smooth)
	smoother = vtk.vtkSmoothPolyDataFilter()
	smoother.SetInputConnection(decibrain.GetOutputPort())
	smoother.SetNumberOfIterations(100)
	smoother.SetFeatureAngle(90.0)
	smoother.SetRelaxationFactor(.7)
	# Set Normals
	brainNormals = vtk.vtkPolyDataNormals()
	brainNormals.SetInputConnection(smoother.GetOutputPort())
	brainNormals.SetFeatureAngle(180.0)
	#set stripper
	brainStripper = vtk.vtkStripper()
	brainStripper.SetInputConnection(brainNormals.GetOutputPort())
	# Create a mapper and actor for smoothed dataset
	brainMapper = vtk.vtkPolyDataMapper()
	brainMapper.SetInputConnection(brainStripper.GetOutputPort())
	brainMapper.ScalarVisibilityOff()
	# set actor
	brain = vtk.vtkActor()
	brain.SetMapper(brainMapper)
	brain.GetProperty().SetDiffuseColor(.9, .5, .1)
	brain.GetProperty().SetSpecular(5)
	brain.GetProperty().SetSpecularPower(60)
	brain.GetProperty().SetOpacity(0.1)
	
	# An isosurface, or contour value of 1150 is known to correspond to the
	# brain of the patient. Once generated, a vtkPolyDataNormals filter is
	# is used to create normals for smooth surface shading during rendering.
	# The triangle stripper is used to create triangle strips from the
	# isosurface these render much faster on may systems.
	tumorExtractor = vtk.vtkContourFilter()
	tumorExtractor.SetInputConnection(reader.GetOutputPort())
	tumorExtractor.SetValue(0, 0)
	# Use a filter to smooth the data (will add triangles and smooth)
	#smootherTumor = vtk.vtkSmoothPolyDataFilter()
	#smootherTumor.SetInputConnection(tumorExtractor.GetOutputPort())
	#smootherTumor.SetNumberOfIterations(100)
	#smootherTumor.SetFeatureAngle(60.0)
	#smootherTumor.SetRelaxationFactor(.5)
	## set Normals
	#tumorNormals = vtk.vtkPolyDataNormals()
	#tumorNormals.SetInputConnection(smootherTumor.GetOutputPort())
	#tumorNormals.SetFeatureAngle(160.0)
	#tumorStripper = vtk.vtkStripper()
	#tumorStripper.SetInputConnection(tumorNormals.GetOutputPort())
	#tumorMapper = vtk.vtkPolyDataMapper()
	#tumorMapper.SetInputConnection(tumorStripper.GetOutputPort())
	#tumorMapper.ScalarVisibilityOff()
	#tumor = vtk.vtkActor()
	#tumor.SetMapper(tumorMapper)
	#tumor.GetProperty().SetDiffuseColor(.2, 0, .8)
	#tumor.GetProperty().SetSpecular(5)
	#tumor.GetProperty().SetSpecularPower(60)
	#tumor.GetProperty().SetOpacity(0.5)
	
	# An outline provides context around the data.
	outlineData = vtk.vtkOutlineFilter()
	outlineData.SetInputConnection(reader.GetOutputPort())
	mapOutline = vtk.vtkPolyDataMapper()
	mapOutline.SetInputConnection(outlineData.GetOutputPort())
	outline = vtk.vtkActor()
	outline.SetMapper(mapOutline)
	outline.GetProperty().SetColor(0, 0, 0)
	
	# It is convenient to create an initial view of the data. The FocalPoint
	# and Position form a vector direction. Later on (ResetCamera() method)
	# this vector is used to position the camera to look at the data in
	# this direction.
	aCamera = vtk.vtkCamera()
	aCamera.SetViewUp(0, 0, -1)
	aCamera.SetPosition(0, 1, 0)
	aCamera.SetFocalPoint(0, 0, 0)
	aCamera.ComputeViewPlaneNormal()
	
	# Actors are added to the renderer. An initial camera view is created.
	# The Dolly() method moves the camera towards the FocalPoint,
	# thereby enlarging the image.
	aRenderer.AddActor(outline)
	aRenderer.AddActor(brain)
	#aRenderer.AddActor(tumor)
	aRenderer.SetActiveCamera(aCamera)
	aRenderer.ResetCamera()
	aCamera.Dolly(1.5)
	
	# Set a background color for the renderer and set the size of the
	# render window (expressed in pixels).
	aRenderer.SetBackground(1, 1, 1)
	renWin.SetSize(640, 480)
	
	# Note that when camera movement occurs (as it does in the Dolly()
	# method), the clipping planes often need adjusting. Clipping planes
	# consist of two planes: near and far along the view direction. The
	# near plane clips out objects in front of the plane the far plane
	# clips out objects behind the plane. This way only what is drawn
	# between the planes is actually rendered.
	aRenderer.ResetCameraClippingRange()
	
	# Interact with the data.
	iren.Initialize()
	renWin.Render()
	iren.Start()
### End render_brainVolume
def initialize_contour(brainArrData,brainReader):
### initialize_contour
def main():
	# =============== first load mha volum ===============
	brainArr , brainObj = load_mha()
	x,y,z = brainArr.shape
	print("brainArr x :", x )
	print("brainArr y :", y )
	print("brainArr z :", z )
	#=========== Render the volume ===============
	#--------- NEED fix tumor intensity ---------
	#render_brainVolume(brainObj)
	#--------------------------------------
	temp = brainArr[:,:,75]
	print("temp image shape :", temp.shape)
	# Try to see max valye in the arr
	max_vale = brainArr.max() 
	print("max value in the arr :", max_vale)
	# ---------------- try to normalize initinisties ----------------
	# loop on all pixels to normalize intinisties
	#normBrainArr = brainArr
	#for a in xrange(1,x):
	#	for b in xrange(1,y):
	#		for c in xrange(1,z):
	#			normBrainArr[a,b,c] = brainArr[a,b,c]/255
	## Try to see max value in the arr after normalization
	#max_vale2 = normBrainArr.max() 
	#print("max value in the arr after normalization:", max_vale2)
	#---------------------------------------------------------------
	# ------------------- Loop to get fram by fram -------------------
	# Access array 3D fram by fram x-y plan
	#for i in xrange(1,z):
	#	curr_fram =  brainArr[:,:,i]
	# 	#cv2.imshow('fram {0}'.format(i),brainArr[:,:,i])
	#	#cv2.waitKey()
	#	break
	#================= Initialize Contour ======================
	''' I am gona Initialize contour by ball equation in 3d ,
	its center is highest pixel value index and r by try and error'''
	initContour = initialize_contour(brainArr,brainObj)
main()
