# Custom Script by Zach.X.G.Zheng
# zach@zachitect.com

# Enable DotNet via Common Language Runtime
import clr

# Import RevitAPI
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
# from Autodesk.Revit.DB.Structure import *

# Import RevitAPIUI
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

# Import System
clr.AddReference('System')
from System.Collections.Generic import List

# Import Revit Nodes
clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.Elements)

# Import DesignScript
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Import Revit Services & Transaction
clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Pointing the current Document
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
view = uidoc.ActiveView;

# ----- Dynamo Input -----

def AllPlacedRoomsDoc(doc):
	PlacedRooms = []
	RoomCollector = FilteredElementCollector(doc)
	RoomsCollected = RoomCollector.OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
	for room in RoomsCollected:
		if room.Location != None and room.Area != 0:
			PlacedRooms.append(room)
	return PlacedRooms

def AllPlacedRooms(doc, view):
	PlacedRooms = []
	RoomCollector = FilteredElementCollector(doc, view.Id)
	RoomsCollected = RoomCollector.OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
	for room in RoomsCollected:
		if room.Location != None and room.Area != 0:
			PlacedRooms.append(room)
	return PlacedRooms

def RoomCentroid(room):
	centroid = None
	for solid in room.get_Geometry(Options()):
		centroid = solid.ComputeCentroid()
	if room.IsPointInRoom(centroid) == False:
		return room.Location.Point
	return centroid

def RoomToCentreVector(room):
	location = room.Location.Point
	centroid = RoomCentroid(room)
	sx = location.X
	sy = location.Y
	ex = centroid.X
	ey = centroid.Y
	vector = XYZ(ex-sx, ey-sy, 0)
	return vector

AllPlacedRoomsIds = []
for each in AllPlacedRoomsDoc(doc):
	AllPlacedRoomsIds.append(each.Id)

SelectedRooms = []
SelectedElements = UnwrapElement(IN[0])
if isinstance(IN[0],list):
	for each in SelectedElements:
		if each.Id in AllPlacedRoomsIds:
			SelectedRooms.append(each)
else:
	if SelectedElements.Id in AllPlacedRoomsIds:
		SelectedRooms.append(SelectedElements)

# ----- Dynamo Codes -----

# Start the Transaction
TransactionManager.Instance.EnsureInTransaction(doc)


if IN[2] == True:
	for room in AllPlacedRoomsDoc(doc):
		room.Location.Move(RoomToCentreVector(room))
elif IN[1] == True:
	for room in AllPlacedRooms(doc, view):
		room.Location.Move(RoomToCentreVector(room))
else:
	for room in SelectedRooms:
		room.Location.Move(RoomToCentreVector(room))
TransactionManager.Instance.TransactionTaskDone()
# Finish the Transaction

# Python Node Output
