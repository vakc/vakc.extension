# -*- coding: utf-8 -*-
__title__ = 'Surround Buildings'
__doc__   ="""This is a test of RevitAPI about using Dynamo API
place surround buildings of the site using DWG
file."""

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

def get_type_by_name(type_name):
    """Extra Function to get Family Type by name."""
    # CREATE RULE
    param_type = ElementId(BuiltInParameter.ALL_MODEL_TYPE_NAME)
    f_param = ParameterValueProvider(param_type)
    evaluator = FilterStringEquals()
    f_rule = FilterStringRule(f_param, evaluator, type_name)

    # CREATE FILTER
    filter_type_name = ElementParameterFilter(f_rule)

    # GET ELEMENTS
    return FilteredElementCollector(doc).WherePasses(filter_type_name).WhereElementIsElementType().FirstElement()


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

cad_import = FilteredElementCollector(doc).OfClass(ImportInstance).WhereElementIsNotElementType().ToElementIds()

pline = []
circle = []
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

                        if hasattr(obj, 'IsCyclic') :
                            circle.append(obj)

# Open up Dynamo

dynamo_model = StartupUtils.MakeModel(CLImode=True)
dynamo_model.Start()

try:
    # this line is important because converting geometry needs a reference of
    # DocumentManager.Instance.CurrentUIDocument, which is None if we don't set it
    # to current uidoc (luckily, they leave it public get/set)
    DocumentManager.Instance.CurrentUIDocument = revit.uidoc

    # Transform different polygons into corresponding building masses based on layers, with a total of 9 layers of polygons to be converted.

    for polyLine in pline:
        gStyle = doc.GetElement(polyLine.GraphicsStyleId)
        Layer = gStyle.GraphicsStyleCategory.Name

        if Layer == "1R":
            O1 = polyLine.ToProtoType()
            P1 = O1.Points

            from Autodesk.Revit.DB import Line

            RP1 = [value.ToRevitType() for value in P1]
            curveloop = create_profile(RP1)
            options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(curveloop)

            cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 4000 / 304.8)

            with Transaction(doc, __title__) as t:

                t.Start()

                direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                direct_shape.SetShape([cubic])

                t.Commit()


        if Layer == "2R":
            O1 = polyLine.ToProtoType()
            P1 = O1.Points

            from Autodesk.Revit.DB import Line

            RP1 = [value.ToRevitType() for value in P1]
            curveloop = create_profile(RP1)
            options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(curveloop)

            cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 7200 / 304.8)

            with Transaction(doc, __title__) as t:

                t.Start()

                direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                direct_shape.SetShape([cubic])

                t.Commit()


        if Layer == "3R":
            O1 = polyLine.ToProtoType()
            P1 = O1.Points

            from Autodesk.Revit.DB import Line

            RP1 = [value.ToRevitType() for value in P1]
            curveloop = create_profile(RP1)
            options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(curveloop)

            cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 10400 / 304.8)

            with Transaction(doc, __title__) as t:

                t.Start()

                direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                direct_shape.SetShape([cubic])

                t.Commit()


        if Layer == "4R":
            try:
                O1 = polyLine.ToProtoType()
                P1 = O1.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)

                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 13600 / 304.8)

                with Transaction(doc, __title__) as t:
                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                pass


        if Layer == "5R":
            O1 = polyLine.ToProtoType()
            P1 = O1.Points

            from Autodesk.Revit.DB import Line

            RP1 = [value.ToRevitType() for value in P1]
            curveloop = create_profile(RP1)
            options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(curveloop)

            cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 16800 / 304.8)

            with Transaction(doc, __title__) as t:
                t.Start()

                direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                direct_shape.SetShape([cubic])

                t.Commit()


        if Layer == "10R":
            try:
                O1 = polyLine.ToProtoType()
                P1 = O1.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)

                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 32800 / 304.8)

                with Transaction(doc, __title__) as t:
                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                pass


        if Layer == "1S":
            O1 = polyLine.ToProtoType()
            P1 = O1.Points

            from Autodesk.Revit.DB import Line

            RP1 = [value.ToRevitType() for value in P1]
            curveloop = create_profile(RP1)
            options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(curveloop)

            cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 4000 / 304.8)

            with Transaction(doc, __title__) as t:
                t.Start()

                direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                direct_shape.SetShape([cubic])

                t.Commit()


        if Layer == "2S":
            O1 = polyLine.ToProtoType()
            P1 = O1.Points

            from Autodesk.Revit.DB import Line

            RP1 = [value.ToRevitType() for value in P1]
            curveloop = create_profile(RP1)
            options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(curveloop)

            cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 4000 / 304.8)

            with Transaction(doc, __title__) as t:
                t.Start()

                direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                direct_shape.SetShape([cubic])

                t.Commit()


        if Layer == "2T":
            O1 = polyLine.ToProtoType()
            P1 = O1.Points

            from Autodesk.Revit.DB import Line

            RP1 = [value.ToRevitType() for value in P1]
            curveloop = create_profile(RP1)
            options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(curveloop)

            cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 4000 / 304.8)

            with Transaction(doc, __title__) as t:
                t.Start()

                direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                direct_shape.SetShape([cubic])

                t.Commit()


finally:
    dynamo_model.ShutDown(shutdownHost=True)


# Call out the trees symbol.



# Transform different circles into corresponding planting types based on layers.

for obj in circle:

    gStyle = doc.GetElement(obj.GraphicsStyleId)
    Layer = gStyle.GraphicsStyleCategory.Name

    if Layer == "apple tree":
        arc_center = obj.Center
        with Transaction(doc, __title__) as t:
            t.Start()
            small_tree = get_type_by_name("Comman Apple - 6.0 Meters")
            if small_tree and not small_tree.IsActive:
                small_tree.Activate()

            mid_tree = get_type_by_name("Red Maple - 9 Meters")
            if mid_tree and not mid_tree.IsActive:
                mid_tree.Activate()

            big_tree = get_type_by_name("Scarlet Oak - 12.5 Meters")
            if big_tree and not big_tree.IsActive:
                big_tree.Activate()

            doc.Create.NewFamilyInstance(arc_center, small_tree, StructuralType.NonStructural)
            t.Commit()
    if Layer == "maple tree":
        arc_center = obj.Center
        with Transaction(doc, __title__) as t:
            t.Start()
            doc.Create.NewFamilyInstance(arc_center, mid_tree, StructuralType.NonStructural)
            t.Commit()
    if Layer == "oak tree":
        arc_center = obj.Center
        with Transaction(doc, __title__) as t:
            t.Start()
            doc.Create.NewFamilyInstance(arc_center, big_tree, StructuralType.NonStructural)
            t.Commit()














