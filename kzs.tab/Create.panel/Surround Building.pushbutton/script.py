# -*- coding: utf-8 -*-
__title__ = 'Surround \nBuildings & Planting'
__doc__   ="""Version = 1.0
Date      = 02.22.2024
_________________________________________________
Description:

This tool is capable of reading and importing polylines
and circles from CAD files to generate architectural
masses and trees around the site in accordance with
the toposolid.
_________________________________________________
How-to:

-> Select the CAD file (ImportInstance).
-> Select the referenced topography (TopoSolid).
-> Generate the site model (Direct Shape and Planting
Family Instance).
_______________________________________________________________________________________________
If unsuccessful:

Consider redrawing the failed polyline in the CAD,
and then reload DWG to generate it again.
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
with forms.WarningBar(title='Pick CAD File:'):
    cad = revit.pick_element()
    cad_import = List[ElementId]()
    cad_import.Add(cad.Id)

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
    geom = toposolid.get_Geometry(Options())
    O1 = [value.ToProtoType() for value in geom]
    S1 = [Geometry.Explode(value) for value in O1]
    S2 = flatten_comprehension(S1)
    N1 = [Surface.NormalAtParameter(value, 0.5, 0.5) for value in S2]
    N2 = [value.Z for value in N1]
    B1 = [value < 0.1 for value in N2]
    S3 = boolmask(S2, B1, False)

    # Transform different polygons into corresponding building masses based on layers,
    # with a total of 9 layers of polygons to be converted.
    ### Logic
    # In the first attempt, try directly generating the original Polyline. If that doesn't
    # work, refine the vectors of each line in the polygon, and if all else fails, proceed
    # to the next step.

    for polyLine in pline:
        gStyle = doc.GetElement(polyLine.GraphicsStyleId)
        Layer = gStyle.GraphicsStyleCategory.Name

        if Layer == "1R":

            try:
                O1 = polyLine.ToProtoType()
                N3 = round(min([Geometry.DistanceTo(value,O1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(O1,V1)
                P1 = O2.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)
                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 4000 / 304.8)

                with Transaction(doc, "1R") as t:

                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                try:
                    O1 = polyLine.ToProtoType()
                    N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                    V1 = Vector.Scale(Vector.ZAxis(), N3)
                    O2 = Geometry.Translate(O1, V1)

                    from Autodesk.DesignScript.Geometry import Line

                    U2 = Geometry.Explode(O2)
                    V2 = [value.Direction for value in U2]
                    V3 = [Vector.Normalized(value) for value in V2]
                    N4 = [round(value.X, 2) for value in V3]
                    N5 = [round(value.Y, 2) for value in V3]
                    V4 = [Vector.ByCoordinates(value1, value2, 0) for value1, value2 in zip(N4, N5)]
                    P1 = [value.StartPoint for value in U2]
                    N6 = [value.Length for value in U2]
                    U3 = [Line.ByStartPointDirectionLength(v1, v2, v3) for v1, v2, v3 in zip(P1, V4, N6)]
                    P2 = [value.EndPoint for value in U3]

                    from Autodesk.Revit.DB import Line

                    RP1 = [value.ToRevitType() for value in P2]
                    curveloop = create_profile(RP1)
                    options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                    list_boundaries = List[CurveLoop]()
                    list_boundaries.Add(curveloop)
                    cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 4000 / 304.8)

                    with Transaction(doc, "1R") as t:

                        t.Start()

                        direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                        direct_shape.SetShape([cubic])

                        t.Commit()
                except:
                    pass


        if Layer == "2R":

            try:
                O1 = polyLine.ToProtoType()
                N3 = round(min([Geometry.DistanceTo(value,O1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(O1,V1)
                P1 = O2.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)
                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 4000 / 304.8)

                with Transaction(doc, "1R") as t:

                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                try:
                    O1 = polyLine.ToProtoType()
                    N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                    V1 = Vector.Scale(Vector.ZAxis(), N3)
                    O2 = Geometry.Translate(O1, V1)

                    from Autodesk.DesignScript.Geometry import Line

                    U2 = Geometry.Explode(O2)
                    V2 = [value.Direction for value in U2]
                    V3 = [Vector.Normalized(value) for value in V2]
                    N4 = [round(value.X, 2) for value in V3]
                    N5 = [round(value.Y, 2) for value in V3]
                    V4 = [Vector.ByCoordinates(value1, value2, 0) for value1, value2 in zip(N4, N5)]
                    P1 = [value.StartPoint for value in U2]
                    N6 = [value.Length for value in U2]
                    U3 = [Line.ByStartPointDirectionLength(v1, v2, v3) for v1, v2, v3 in zip(P1, V4, N6)]
                    P2 = [value.EndPoint for value in U3]

                    from Autodesk.Revit.DB import Line

                    RP1 = [value.ToRevitType() for value in P2]
                    curveloop = create_profile(RP1)
                    options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                    list_boundaries = List[CurveLoop]()
                    list_boundaries.Add(curveloop)
                    cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 7200 / 304.8)

                    with Transaction(doc, "2R") as t:

                        t.Start()

                        direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                        direct_shape.SetShape([cubic])

                        t.Commit()
                except:
                    pass


        if Layer == "3R":
            try:
                O1 = polyLine.ToProtoType()
                N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(O1, V1)
                P1 = O2.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)

                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 10400 / 304.8)

                with Transaction(doc, "3R") as t:
                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                try:
                    O1 = polyLine.ToProtoType()
                    N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                    V1 = Vector.Scale(Vector.ZAxis(), N3)
                    O2 = Geometry.Translate(O1, V1)

                    from Autodesk.DesignScript.Geometry import Line

                    U2 = Geometry.Explode(O2)
                    V2 = [value.Direction for value in U2]
                    V3 = [Vector.Normalized(value) for value in V2]
                    N4 = [round(value.X, 2) for value in V3]
                    N5 = [round(value.Y, 2) for value in V3]
                    V4 = [Vector.ByCoordinates(value1, value2, 0) for value1, value2 in zip(N4, N5)]
                    P1 = [value.StartPoint for value in U2]
                    N6 = [value.Length for value in U2]
                    U3 = [Line.ByStartPointDirectionLength(v1, v2, v3) for v1, v2, v3 in zip(P1, V4, N6)]
                    P2 = [value.EndPoint for value in U3]

                    from Autodesk.Revit.DB import Line

                    RP1 = [value.ToRevitType() for value in P2]
                    curveloop = create_profile(RP1)
                    options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                    list_boundaries = List[CurveLoop]()
                    list_boundaries.Add(curveloop)
                    cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 10400 / 304.8)

                    with Transaction(doc, "3R") as t:

                        t.Start()

                        direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                        direct_shape.SetShape([cubic])

                        t.Commit()
                except:
                    pass


        if Layer == "4R":
            try:
                O1 = polyLine.ToProtoType()
                N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(O1, V1)
                P1 = O2.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)

                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 13600 / 304.8)

                with Transaction(doc, "4R") as t:
                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                try:
                    O1 = polyLine.ToProtoType()
                    N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                    V1 = Vector.Scale(Vector.ZAxis(), N3)
                    O2 = Geometry.Translate(O1, V1)

                    from Autodesk.DesignScript.Geometry import Line

                    U2 = Geometry.Explode(O2)
                    V2 = [value.Direction for value in U2]
                    V3 = [Vector.Normalized(value) for value in V2]
                    N4 = [round(value.X, 2) for value in V3]
                    N5 = [round(value.Y, 2) for value in V3]
                    V4 = [Vector.ByCoordinates(value1, value2, 0) for value1, value2 in zip(N4, N5)]
                    P1 = [value.StartPoint for value in U2]
                    N6 = [value.Length for value in U2]
                    U3 = [Line.ByStartPointDirectionLength(v1, v2, v3) for v1, v2, v3 in zip(P1, V4, N6)]
                    P2 = [value.EndPoint for value in U3]

                    from Autodesk.Revit.DB import Line

                    RP1 = [value.ToRevitType() for value in P2]
                    curveloop = create_profile(RP1)
                    options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                    list_boundaries = List[CurveLoop]()
                    list_boundaries.Add(curveloop)
                    cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 13600 / 304.8)

                    with Transaction(doc, "4R") as t:

                        t.Start()

                        direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                        direct_shape.SetShape([cubic])

                        t.Commit()
                except:
                    pass


        if Layer == "5R":
            try:
                O1 = polyLine.ToProtoType()
                N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(O1, V1)
                P1 = O2.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)

                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 16800 / 304.8)

                with Transaction(doc, "5R") as t:
                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                try:
                    O1 = polyLine.ToProtoType()
                    N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                    V1 = Vector.Scale(Vector.ZAxis(), N3)
                    O2 = Geometry.Translate(O1, V1)

                    from Autodesk.DesignScript.Geometry import Line

                    U2 = Geometry.Explode(O2)
                    V2 = [value.Direction for value in U2]
                    V3 = [Vector.Normalized(value) for value in V2]
                    N4 = [round(value.X, 2) for value in V3]
                    N5 = [round(value.Y, 2) for value in V3]
                    V4 = [Vector.ByCoordinates(value1, value2, 0) for value1, value2 in zip(N4, N5)]
                    P1 = [value.StartPoint for value in U2]
                    N6 = [value.Length for value in U2]
                    U3 = [Line.ByStartPointDirectionLength(v1, v2, v3) for v1, v2, v3 in zip(P1, V4, N6)]
                    P2 = [value.EndPoint for value in U3]

                    from Autodesk.Revit.DB import Line

                    RP1 = [value.ToRevitType() for value in P2]
                    curveloop = create_profile(RP1)
                    options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                    list_boundaries = List[CurveLoop]()
                    list_boundaries.Add(curveloop)
                    cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 16800 / 304.8)

                    with Transaction(doc, "5R") as t:

                        t.Start()

                        direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                        direct_shape.SetShape([cubic])

                        t.Commit()
                except:
                    pass


        if Layer == "10R":
            try:
                O1 = polyLine.ToProtoType()
                N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(O1, V1)
                P1 = O2.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)

                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 32800 / 304.8)

                with Transaction(doc, "10R") as t:
                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                try:
                    O1 = polyLine.ToProtoType()
                    N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                    V1 = Vector.Scale(Vector.ZAxis(), N3)
                    O2 = Geometry.Translate(O1, V1)

                    from Autodesk.DesignScript.Geometry import Line

                    U2 = Geometry.Explode(O2)
                    V2 = [value.Direction for value in U2]
                    V3 = [Vector.Normalized(value) for value in V2]
                    N4 = [round(value.X, 2) for value in V3]
                    N5 = [round(value.Y, 2) for value in V3]
                    V4 = [Vector.ByCoordinates(value1, value2, 0) for value1, value2 in zip(N4, N5)]
                    P1 = [value.StartPoint for value in U2]
                    N6 = [value.Length for value in U2]
                    U3 = [Line.ByStartPointDirectionLength(v1, v2, v3) for v1, v2, v3 in zip(P1, V4, N6)]
                    P2 = [value.EndPoint for value in U3]

                    from Autodesk.Revit.DB import Line

                    RP1 = [value.ToRevitType() for value in P2]
                    curveloop = create_profile(RP1)
                    options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                    list_boundaries = List[CurveLoop]()
                    list_boundaries.Add(curveloop)
                    cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 32800 / 304.8)

                    with Transaction(doc, "10R") as t:

                        t.Start()

                        direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                        direct_shape.SetShape([cubic])

                        t.Commit()
                except:
                    pass


        if Layer == "1S":
            try:
                O1 = polyLine.ToProtoType()
                N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(O1, V1)
                P1 = O2.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)

                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 4000 / 304.8)

                with Transaction(doc, "1S") as t:
                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                try:
                    O1 = polyLine.ToProtoType()
                    N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                    V1 = Vector.Scale(Vector.ZAxis(), N3)
                    O2 = Geometry.Translate(O1, V1)

                    from Autodesk.DesignScript.Geometry import Line

                    U2 = Geometry.Explode(O2)
                    V2 = [value.Direction for value in U2]
                    V3 = [Vector.Normalized(value) for value in V2]
                    N4 = [round(value.X, 2) for value in V3]
                    N5 = [round(value.Y, 2) for value in V3]
                    V4 = [Vector.ByCoordinates(value1, value2, 0) for value1, value2 in zip(N4, N5)]
                    P1 = [value.StartPoint for value in U2]
                    N6 = [value.Length for value in U2]
                    U3 = [Line.ByStartPointDirectionLength(v1, v2, v3) for v1, v2, v3 in zip(P1, V4, N6)]
                    P2 = [value.EndPoint for value in U3]

                    from Autodesk.Revit.DB import Line

                    RP1 = [value.ToRevitType() for value in P2]
                    curveloop = create_profile(RP1)
                    options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                    list_boundaries = List[CurveLoop]()
                    list_boundaries.Add(curveloop)
                    cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 4000 / 304.8)

                    with Transaction(doc, "1S") as t:

                        t.Start()

                        direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                        direct_shape.SetShape([cubic])

                        t.Commit()
                except:
                    pass


        if Layer == "2S":
            try:
                O1 = polyLine.ToProtoType()
                N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(O1, V1)
                P1 = O2.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)

                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 7200 / 304.8)

                with Transaction(doc, "2S") as t:
                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                try:
                    O1 = polyLine.ToProtoType()
                    N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                    V1 = Vector.Scale(Vector.ZAxis(), N3)
                    O2 = Geometry.Translate(O1, V1)

                    from Autodesk.DesignScript.Geometry import Line

                    U2 = Geometry.Explode(O2)
                    V2 = [value.Direction for value in U2]
                    V3 = [Vector.Normalized(value) for value in V2]
                    N4 = [round(value.X, 2) for value in V3]
                    N5 = [round(value.Y, 2) for value in V3]
                    V4 = [Vector.ByCoordinates(value1, value2, 0) for value1, value2 in zip(N4, N5)]
                    P1 = [value.StartPoint for value in U2]
                    N6 = [value.Length for value in U2]
                    U3 = [Line.ByStartPointDirectionLength(v1, v2, v3) for v1, v2, v3 in zip(P1, V4, N6)]
                    P2 = [value.EndPoint for value in U3]

                    from Autodesk.Revit.DB import Line

                    RP1 = [value.ToRevitType() for value in P2]
                    curveloop = create_profile(RP1)
                    options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                    list_boundaries = List[CurveLoop]()
                    list_boundaries.Add(curveloop)
                    cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 7200 / 304.8)

                    with Transaction(doc, "2S") as t:

                        t.Start()

                        direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                        direct_shape.SetShape([cubic])

                        t.Commit()
                except:
                    pass


        if Layer == "2T":
            try:
                O1 = polyLine.ToProtoType()
                N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(O1, V1)
                P1 = O2.Points

                from Autodesk.Revit.DB import Line

                RP1 = [value.ToRevitType() for value in P1]
                curveloop = create_profile(RP1)
                options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(curveloop)

                cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 7200 / 304.8)

                with Transaction(doc, "2T") as t:
                    t.Start()

                    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                    direct_shape.SetShape([cubic])

                    t.Commit()
            except:
                try:
                    O1 = polyLine.ToProtoType()
                    N3 = round(min([Geometry.DistanceTo(value, O1) for value in S3]))
                    V1 = Vector.Scale(Vector.ZAxis(), N3)
                    O2 = Geometry.Translate(O1, V1)

                    from Autodesk.DesignScript.Geometry import Line

                    U2 = Geometry.Explode(O2)
                    V2 = [value.Direction for value in U2]
                    V3 = [Vector.Normalized(value) for value in V2]
                    N4 = [round(value.X, 2) for value in V3]
                    N5 = [round(value.Y, 2) for value in V3]
                    V4 = [Vector.ByCoordinates(value1, value2, 0) for value1, value2 in zip(N4, N5)]
                    P1 = [value.StartPoint for value in U2]
                    N6 = [value.Length for value in U2]
                    U3 = [Line.ByStartPointDirectionLength(v1, v2, v3) for v1, v2, v3 in zip(P1, V4, N6)]
                    P2 = [value.EndPoint for value in U3]

                    from Autodesk.Revit.DB import Line

                    RP1 = [value.ToRevitType() for value in P2]
                    curveloop = create_profile(RP1)
                    options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
                    list_boundaries = List[CurveLoop]()
                    list_boundaries.Add(curveloop)
                    cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 7200 / 304.8)

                    with Transaction(doc, "2T") as t:

                        t.Start()

                        direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                        direct_shape.SetShape([cubic])

                        t.Commit()
                except:
                    pass

    # Call out the trees symbol.
    # Transform different circles into corresponding planting types based on layers.

    for obj in circle:

        gStyle = doc.GetElement(obj.GraphicsStyleId)
        Layer = gStyle.GraphicsStyleCategory.Name

        if Layer == "apple tree":
            try:
                R1 = obj.ToProtoType()
                P1 = R1.CenterPoint
                N3 = round(min([Geometry.DistanceTo(value, P1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(P1, V1)

                with Transaction(doc, "apple tree") as t:
                    t.Start()

                    RP1 = O2.ToRevitType()
                    small_tree = get_type_by_name("Comman Apple - 6.0 Meters")
                    if small_tree and not small_tree.IsActive:
                        small_tree.Activate()

                    doc.Create.NewFamilyInstance(RP1, small_tree, StructuralType.NonStructural)
                    t.Commit()
            except:
                pass


        if Layer == "maple tree":
            try:
                R1 = obj.ToProtoType()
                P1 = R1.CenterPoint
                N3 = round(min([Geometry.DistanceTo(value, P1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(P1, V1)

                with Transaction(doc, "maple tree") as t:
                    t.Start()

                    RP1 = O2.ToRevitType()
                    small_tree = get_type_by_name("Red Maple - 9 Meters")
                    if small_tree and not small_tree.IsActive:
                        small_tree.Activate()

                    doc.Create.NewFamilyInstance(RP1, small_tree, StructuralType.NonStructural)
                    t.Commit()
            except:
                pass


        if Layer == "oak tree":
            try:
                R1 = obj.ToProtoType()
                P1 = R1.CenterPoint
                N3 = round(min([Geometry.DistanceTo(value, P1) for value in S3]))
                V1 = Vector.Scale(Vector.ZAxis(), N3)
                O2 = Geometry.Translate(P1, V1)

                with Transaction(doc, "oak tree") as t:
                    t.Start()

                    RP1 = O2.ToRevitType()
                    small_tree = get_type_by_name("Scarlet Oak - 12.5 Meters")
                    if small_tree and not small_tree.IsActive:
                        small_tree.Activate()

                    doc.Create.NewFamilyInstance(RP1, small_tree, StructuralType.NonStructural)
                    t.Commit()
            except:
                pass

finally:
    dynamo_model.ShutDown(shutdownHost=True)

















