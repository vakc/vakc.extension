# -*- coding: utf-8 -*-
__title__ = 'Dynamo Test'
__doc__   ="""This is a test of RevitAPI about using Dynamo
API Creating/Deleting/Copying Elements."""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

import clr

clr.AddReference('System')
from System.Collections.Generic import List

clr.AddReference("DynamoApplications")
from Dynamo.Applications import StartupUtils

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType

from pyrevit import revit

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# =================================================

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

active_view = doc.ActiveView

def create_profile(points):

    l_0 = Line.CreateBound(points[0], points[1])
    l_1 = Line.CreateBound(points[1], points[2])
    l_2 = Line.CreateBound(points[2], points[3])
    l_3 = Line.CreateBound(points[3], points[0])

    boundary = CurveLoop()
    boundary.Append(l_0)
    boundary.Append(l_1)
    boundary.Append(l_2)
    boundary.Append(l_3)

    return boundary

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIN
# =================================================


dynamo_model = StartupUtils.MakeModel(CLImode=True)
dynamo_model.Start()

try:
    # this line is important because converting geometry needs a reference of
    # DocumentManager.Instance.CurrentUIDocument, which is None if we don't set it
    # to current uidoc (luckily, they leave it public get/set)
    DocumentManager.Instance.CurrentUIDocument = revit.uidoc

    C1 = Line.ByStartPointEndPoint(Point.ByCoordinates(0,0,0),Point.ByCoordinates(1000,0,0))
    RC1 = C1.ToRevitType()
    C2 = Line.ByStartPointEndPoint(Point.ByCoordinates(0,2000,0),Point.ByCoordinates(1000,2000,0))
    H1 = 3400
    L1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().FirstElementId()
    W1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType().FirstElement()

    # R1 = Rectangle.ByWidthLength(CoordinateSystem.ByOrigin(0,0,0), 8000, 8000)
    # P1 = Polygon.Corners(R1)
    # RP1 = [value.ToXyz() for value in P1]

    # P1 = Point.ByCoordinates(1000,0,0)
    # RP1 = P1.ToXyz()
    # P2 = Point.ByCoordinates(2000,0,0)
    # RP2 = P2.ToXyz()
    # P3 = Point.ByCoordinates(2000,1000,0)
    # RP3 = P3.ToXyz()
    # P4 = Point.ByCoordinates(1000,1000,0)
    # RP4 = P4.ToXyz()
    #
    # l_0 = Line.CreateBound(RP1, RP2)
    # l_1 = Line.CreateBound(RP2, RP3)
    # l_2 = Line.CreateBound(RP3, RP4)
    # l_3 = Line.CreateBound(RP4, RP1)
    #
    # boundary1 = CurveLoop()
    #
    # boundary1.Append(l_0)
    # boundary1.Append(l_1)
    # boundary1.Append(l_2)
    # boundary1.Append(l_3)
    #
    # list_boundaries = List[CurveLoop]()
    # list_boundaries.Add(boundary1)


    with Transaction(doc,__title__) as t :

        t.Start()

        # region_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.FilledRegionType)
        # region = FilledRegion.Create(doc, region_type_id, active_view.Id, list_boundaries)
        Wall.Create(doc, RC1, L1, StructuralType.NonStructural)

        t.Commit()

finally:
    dynamo_model.ShutDown(shutdownHost=True)















