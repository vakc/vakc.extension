# -*- coding: utf-8 -*-
__title__ = 'Group Unit Elements \nPlacement'
__doc__   ="""Version = 1.0
Date      = 02.28.2024
_________________________________________________
Description:

This tool can replace the DirectShape volume of each unit with
a grouped placement of unit components for architectural design
masses in social housing. It then deletes the original DirectShape
volumes.
_________________________________________________
How-to:

-> Select all the DirectShapes that you want to replace with grouped
components (selecting other objects is also fine).
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
import csv
import io
import os
import math

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

def list_flatten(ls):
    flatten_ls=[]
    for row in ls:
        flatten_ls += row
    return flatten_ls

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

# Select the design elements in Revit.
with forms.WarningBar(title='Pick Site Pad:'):
    all_element = revit.pick_elements()
# Filter out elements that are not DirectShape in Revit.
directshape_geometry = []
for element in all_element:
    if isinstance(element,DirectShape):
        directshape_geometry.append(element)

# Open the Dynamo program in the background.
dynamo_model = StartupUtils.MakeModel(CLImode=True)
dynamo_model.Start()

try:
    # this line is important because converting geometry needs a reference of
    # DocumentManager.Instance.CurrentUIDocument, which is None if we don't set it
    # to current uidoc (luckily, they leave it public get/set)
    DocumentManager.Instance.CurrentUIDocument = revit.uidoc

    ### Categorize the units.
    # Convert the Revit DirectShape into geometry.
    unit_dynamo_geometry = [value.get_Geometry(Options()) for value in directshape_geometry]
    # Convert the Revit geoemtry into dynamo geometry.
    O1 = [[value.ToProtoType() for value in sublist] for sublist in unit_dynamo_geometry]
    O2 = flatten_comprehension(O1)
    # Decompose each solid into 6 surfaces.
    S1 = [Geometry.Explode(value) for value in O2]
    # Identify surfaces whose normal at the center aligns with the Z-axis direction for configuring the initial design face
    V1 = [[Surface.NormalAtParameter(value, 0.5, 0.5) for value in sublist] for sublist in S1]
    B1 = [[Vector.IsAlmostEqualTo(value, Vector.Reverse(Vector.ZAxis())) for value in sublist] for sublist in V1]
    S2 = [boolmask(value, value2, True) for value,value2 in zip(S1,B1)]
    S3 = flatten_comprehension(S2)
    # Decompose each surface to obtain their respective edges. Then, categorize them based on the length of the first edge
    # curve of each surface.
    E1 = [value.Edges for value in S3]
    U1 = [[value.CurveGeometry for value in sublist] for sublist in E1]
    U2 = [sublist[0] for sublist in U1]
    N1 = [round(value) for value in [value.Length for value in U2]]
    D1 = list(zip(S3, N1))
    S4 = sorted(D1, key=lambda x: x[1])
    S5 = [list(group) for key, group in groupby([S4[i][0] for i in range(len(S4))], key=lambda x: N1[S3.index(x)])]
    # Separate the surfaces of the three categorized unit types.


    ### First Single Room Type
    for surface_list in S5:
        if round(surface_list[0].Edges[0].CurveGeometry.Length) == 4200:
            first_single_type_surface = surface_list

    for surface in first_single_type_surface:
        P1 = Surface.PointAtParameter(surface, 0.5, 0.5)
        U3 = Line.ByStartPointDirectionLength(P1, Vector.ZAxis(), 10)

        E2 = surface.Edges
        U4 = [value.CurveGeometry for value in E2]
        N2 = Vector.AngleAboutAxis(U4[0].Direction, Vector.XAxis(), Vector.ZAxis())

        group_type = FilteredElementCollector(doc).OfClass(GroupType).WhereElementIsElementType().ToElements()

        with Transaction(doc, __title__) as t:
            t.Start()
            RP1 = P1.ToRevitType()
            RU1 = U3.ToRevitType()
            group_1 = doc.Create.PlaceGroup(RP1, group_type[0])
            group_1_rotate = ElementTransformUtils.RotateElement(doc, group_1.Id, RU1, -N2 * math.pi / 180)
            t.Commit()

    ### First Double Room Type
    for surface_list in S5:
        if round(surface_list[0].Edges[0].CurveGeometry.Length) == 9100:
            first_double_type_surface = surface_list
    for surface in first_double_type_surface:
        P1 = Surface.PointAtParameter(surface, 0.5, 0.5)
        U3 = Line.ByStartPointDirectionLength(P1, Vector.ZAxis(), 10)

        E2 = surface.Edges
        U4 = [value.CurveGeometry for value in E2]
        N2 = Vector.AngleAboutAxis(U4[0].Direction, Vector.XAxis(), Vector.ZAxis())

        group_type = FilteredElementCollector(doc).OfClass(GroupType).WhereElementIsElementType().ToElements()

        with Transaction(doc, __title__) as t:
            t.Start()
            RP1 = P1.ToRevitType()
            RU1 = U3.ToRevitType()
            group_1 = doc.Create.PlaceGroup(RP1, group_type[1])
            group_1_rotate = ElementTransformUtils.RotateElement(doc, group_1.Id, RU1, -N2 * math.pi / 180)
            t.Commit()

    ### First Triple Room Type
    for surface_list in S5:
        if round(surface_list[0].Edges[0].CurveGeometry.Length) == 12800:
            first_triple_type_surface = surface_list
    for surface in first_triple_type_surface:
        P1 = Surface.PointAtParameter(surface, 0.5, 0.5)
        U3 = Line.ByStartPointDirectionLength(P1, Vector.ZAxis(), 10)

        E2 = surface.Edges
        U4 = [value.CurveGeometry for value in E2]
        N2 = Vector.AngleAboutAxis(U4[0].Direction, Vector.XAxis(), Vector.ZAxis())

        group_type = FilteredElementCollector(doc).OfClass(GroupType).WhereElementIsElementType().ToElements()

        with Transaction(doc, __title__) as t:
            t.Start()
            RP1 = P1.ToRevitType()
            RU1 = U3.ToRevitType()
            group_1 = doc.Create.PlaceGroup(RP1, group_type[2])
            group_1_rotate = ElementTransformUtils.RotateElement(doc, group_1.Id, RU1, -N2 * math.pi / 180)
            t.Commit()

    ## Second Single Room Type
    second_single_type_surface = []
    for surface_list in S5:
        if round(surface_list[0].Edges[1].CurveGeometry.Length) == 4200:
            second_single_type_surface.append(surface_list)
        else:
            pass
    if second_single_type_surface:
        for surfaces in second_single_type_surface:
            for surface in surfaces:
                P1 = Surface.PointAtParameter(surface, 0.5, 0.5)
                U3 = Line.ByStartPointDirectionLength(P1, Vector.ZAxis(), 10)

                E2 = surface.Edges
                U4 = [value.CurveGeometry for value in E2]
                N2 = Vector.AngleAboutAxis(U4[0].Direction, Vector.XAxis(), Vector.ZAxis())

                group_type = FilteredElementCollector(doc).OfClass(GroupType).WhereElementIsElementType().ToElements()

                with Transaction(doc, __title__) as t:
                    t.Start()
                    RP1 = P1.ToRevitType()
                    RU1 = U3.ToRevitType()
                    group_1 = doc.Create.PlaceGroup(RP1, group_type[0])
                    group_1_rotate = ElementTransformUtils.RotateElement(doc, group_1.Id, RU1, (-N2+90) * math.pi / 180)
                    t.Commit()

    ### Second Double Room Type
    second_double_type_surface = []
    for surface_list in S5:
        if round(surface_list[0].Edges[1].CurveGeometry.Length) == 9100:
            second_double_type_surface.append(surface_list)
        else:
            pass
    if second_double_type_surface:
        for surfaces in second_double_type_surface:
            for surface in surfaces:
                P1 = Surface.PointAtParameter(surface, 0.5, 0.5)
                U3 = Line.ByStartPointDirectionLength(P1, Vector.ZAxis(), 10)

                E2 = surface.Edges
                U4 = [value.CurveGeometry for value in E2]
                N2 = Vector.AngleAboutAxis(U4[0].Direction, Vector.XAxis(), Vector.ZAxis())

                group_type = FilteredElementCollector(doc).OfClass(GroupType).WhereElementIsElementType().ToElements()

                with Transaction(doc, __title__) as t:
                    t.Start()
                    RP1 = P1.ToRevitType()
                    RU1 = U3.ToRevitType()
                    group_1 = doc.Create.PlaceGroup(RP1, group_type[1])
                    group_1_rotate = ElementTransformUtils.RotateElement(doc, group_1.Id, RU1, (-N2+90) * math.pi / 180)
                    t.Commit()

    ### Secong Triple Room Type
    second_triple_type_surface = []
    for surface_list in S5:
        if round(surface_list[0].Edges[1].CurveGeometry.Length) == 12800:
            second_triple_type_surface.append(surface_list)
        else:
            pass
    if second_triple_type_surface:
        for surfaces in second_triple_type_surface:
            for surface in surfaces:
                P1 = Surface.PointAtParameter(surface, 0.5, 0.5)
                U3 = Line.ByStartPointDirectionLength(P1, Vector.ZAxis(), 10)

                E2 = surface.Edges
                U4 = [value.CurveGeometry for value in E2]
                N2 = Vector.AngleAboutAxis(U4[0].Direction, Vector.XAxis(), Vector.ZAxis())

                group_type = FilteredElementCollector(doc).OfClass(GroupType).WhereElementIsElementType().ToElements()

                with Transaction(doc, __title__) as t:
                    t.Start()
                    RP1 = P1.ToRevitType()
                    RU1 = U3.ToRevitType()
                    group_1 = doc.Create.PlaceGroup(RP1, group_type[2])
                    group_1_rotate = ElementTransformUtils.RotateElement(doc, group_1.Id, RU1, (-N2+90) * math.pi / 180)
                    t.Commit()

    with Transaction(doc, __title__) as t:
        t.Start()
        for element in directshape_geometry:
            doc.Delete(element.Id)
        t.Commit()




finally:
    dynamo_model.ShutDown(shutdownHost=True)