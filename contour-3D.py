# This script implments 3D active contours on brain tumor data 3D volume .mha files
# import needed packages
import os
import vtk
import math
import cmath
import numpy
# ======= Load .mha file ==========
def load_mha():
	# Create the renderer, the render window, and the interactor. The
	# renderer draws into the render window, the interactor enables mouse-
	# and keyboard-based interaction with the scene.
	aRenderer = vtk.vtkRenderer()
	renWin = vtk.vtkRenderWindow()
	renWin.AddRenderer(aRenderer)
	iren = vtk.vtkRenderWindowInteractor()
	iren.SetRenderWindow(renWin)
	# helper link:
	# https://pyscience.wordpress.com/2014/11/16/volume-rendering-with-python-and-vtk/
	#---------------------------------
	# Path to the .mha file
	big_tomur   = "VSD.Brain.XX.O.MR_Flair.54512.mha"
	small_tomur = "VSD.Brain.XX.O.MR_T1c.54514.mha"
	# load the label-field under the provided .mha file.
	"""initially create a new vtkMetaImageReader object under reader 
	set the filename from which to read,"""
	reader = vtk.vtkMetaImageReader()
	reader.SetFileName(big_tomur)
	reader.Update()
	# Next we need access to the metadata in order to 
	# calculate those ConstPixelDims and ConstPixelSpacing variables:
	# Load dimensions using `GetDataExtent`
	_extent = reader.GetDataExtent()
	ConstPixelDims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]
	# Check dimentions of the 3D object
	# dimentions [240, 240, 155]
	print("ConstPixelDims: ",ConstPixelDims) 
	# An isosurface, or contour value of 500 is known to correspond to the
	# liver of the patient. Once generated, a vtkPolyDataNormals filter is
	# is used to create normals for smooth surface shading during rendering.
	# The triangle stripper is used to create triangle strips from the
	# isosurface these render much faster on may systems.
	liverExtractor = vtk.vtkContourFilter()
	liverExtractor.SetInputConnection(reader.GetOutputPort())
	liverExtractor.SetValue(1, 100)
	# Helper link :
	# http://www.programcreek.com/python/example/11893/vtk.vtkContourFilter
	# example 3
	# set disc
	deciLiver = vtk.vtkDecimatePro()
	deciLiver.SetInputConnection(liverExtractor.GetOutputPort())
	deciLiver.SetTargetReduction(.1)
	deciLiver.PreserveTopologyOn()
	# Use a filter to smooth the data (will add triangles and smooth)
	smoother = vtk.vtkSmoothPolyDataFilter()
	smoother.SetInputConnection(deciLiver.GetOutputPort())
	smoother.SetNumberOfIterations(100)
	smoother.SetFeatureAngle(90.0)
	smoother.SetRelaxationFactor(.7)
	# Set Normals
	liverNormals = vtk.vtkPolyDataNormals()
	liverNormals.SetInputConnection(smoother.GetOutputPort())
	liverNormals.SetFeatureAngle(180.0)
	#set stripper
	liverStripper = vtk.vtkStripper()
	liverStripper.SetInputConnection(liverNormals.GetOutputPort())
	# Create a mapper and actor for smoothed dataset
	liverMapper = vtk.vtkPolyDataMapper()
	liverMapper.SetInputConnection(liverStripper.GetOutputPort())
	liverMapper.ScalarVisibilityOff()
	# set actor
	liver = vtk.vtkActor()
	liver.SetMapper(liverMapper)
	liver.GetProperty().SetDiffuseColor(.9, .5, .1)
	liver.GetProperty().SetSpecular(5)
	liver.GetProperty().SetSpecularPower(60)
	liver.GetProperty().SetOpacity(0.1)
	
	# An isosurface, or contour value of 1150 is known to correspond to the
	# liver of the patient. Once generated, a vtkPolyDataNormals filter is
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
	aRenderer.AddActor(liver)
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







### End Load_mha()
load_mha()
