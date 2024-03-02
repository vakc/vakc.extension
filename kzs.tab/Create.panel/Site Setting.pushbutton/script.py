# -*- coding: utf-8 -*-
__title__ = 'Place \nSite Pad & Levels'
__doc__   ="""Version = 1.0
Date      = 02.17.2024
_________________________________________________
Description:

This tool is capable of reading and importing polycurves
from the 'Site' layer of CAD file. It uses this information
to generate a site pad on a reasonable elevation and
simultaneously produces 15 Level Elements. The first floor
is set at 4.2 meters, while the subsequent floors are all
set at 3.4 meters.
_________________________________________________
How-to:

-> Select the CAD file to be generated (ImportInstance).
-> Select the referenced topography (TopoSolid).
-> Generate the Site Pad and Levels.
_______________________________________________________________________________________________
Author: vakc"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

from itertools import groupby
import sys
import clr
import random

clr.AddReference("RevitAPI")

import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('System')
from System.Collections.Generic import List

clr.AddReference("DynamoApplications")
from Dynamo.Applications import StartupUtils

from pyrevit import forms, revit


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝  FUNCTIONS
# =================================================

def boolmask(list1, list2, condition):
    return [elem1 for elem1, elem2 in zip(list1, list2) if elem2 == condition]

def flatten_comprehension(matrix):
    return [item for row in matrix for item in row]

def create_profile(points):
    curve_loop = CurveLoop()

    for i in range(len(points)):
        start_point = points[i]
        end_point = points[(i + 1) % len(points)]  # Wrap around for the last point

        line = Line.CreateBound(start_point, end_point)
        curve_loop.Append(line)

    return curve_loop



# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# =================================================

# Document Setting
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
active_view = doc.ActiveView




# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIN
# =================================================

# Select the imported DWG file and create two groups: one for polylines and another for circles.


with forms.WarningBar(title='Pick CAD File:'):
    cad = revit.pick_element()
    cad_import = List[ElementId]()
    cad_import.Add(cad.Id)

pline = []
layerNames = []

if cad_import.Count > 0:
    importId = cad_import[0]
    importInstance = doc.GetElement(importId)

    if isinstance(importInstance, ImportInstance):
        geoEle = importInstance.get_Geometry(Options())

        for geoObj in geoEle:
            if isinstance(geoObj, GeometryInstance):
                geoInst = geoObj
                geoElement = geoInst.GetInstanceGeometry()
                if geoElement is not None:
                    for obj in geoElement:
                        if isinstance(obj, PolyLine):
                            gStyle = doc.GetElement(obj.GraphicsStyleId)
                            layer = gStyle.GraphicsStyleCategory.Name

                            layerNames.append(layer)
                            pline.append(obj)

# Select the TopoSolid

with forms.WarningBar(title='Pick Toposolid:'):
    toposolid = revit.pick_element()

# Open up Dynamo

dynamo_model = StartupUtils.MakeModel(CLImode=True)
dynamo_model.Start()

try:
    # this line is important because converting geometry needs a reference of
    # DocumentManager.Instance.CurrentUIDocument, which is None if we don't set it
    # to current uidoc (luckily, they leave it public get/set)
    DocumentManager.Instance.CurrentUIDocument = revit.uidoc


    # Modify toposurface to a surface

    opt = Options()
    outlist = []
    geom = toposolid.get_Geometry(opt)

    O1 = [value.ToProtoType() for value in geom]
    S1 = [Geometry.Explode(value) for value in O1]
    S2 = flatten_comprehension(S1)
    N1 = [Surface.NormalAtParameter(value, 0.5, 0.5) for value in S2]
    N2 = [value.Z for value in N1]
    B1 = [value < 0.1 for value in N2]
    S3 = boolmask(S2, B1, False)
    S4 = Surface.ByUnion(S3)


    # Transform different polygons into corresponding building masses based on layers, with a total of 9 layers of polygons to be converted.

    for polyLine in pline:
        gStyle = doc.GetElement(polyLine.GraphicsStyleId)
        Layer = gStyle.GraphicsStyleCategory.Name

        if Layer == "Site":
            try:

                O1 = polyLine.ToProtoType()
                C1 = Surface.ProjectInputOnto(S4, O1, Vector.ZAxis())
                C2 = PolyCurve.ByJoinedCurves(tuple(C1), 0.001, False, 0)
                N1 = Geometry.DistanceTo(O1, C2)

                P1 = O1.Points


                LevelToCopy = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
                for level in LevelToCopy:
                    if level.Name == 'L1':
                        level = level

                floor_type_Id = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElementIds()


                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)


                with Transaction(doc, __title__) as t:

                    t.Start()

                    level_1 = ElementTransformUtils.CopyElement(doc, level.Id, XYZ(0, 0, N1 / 304.8))
                    doc.GetElement(level_1[0]).Name = 'Level 1'

                    for i in range(2, 15):
                        offset = (N1 + 4000 + (i - 2) * 3400) / 304.8
                        new_level = ElementTransformUtils.CopyElement(doc, level.Id, XYZ(0, 0, offset))
                        doc.GetElement(new_level[0]).Name = 'Level {}'.format(i)

                    floor = Floor.Create(doc, list_boundaries, floor_type_Id[0], level_1[0])



                    t.Commit()

            except:
                pass

finally:
    dynamo_model.ShutDown(shutdownHost=True)

