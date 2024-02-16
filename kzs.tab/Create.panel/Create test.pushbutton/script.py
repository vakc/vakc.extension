# -*- coding: utf-8 -*-
__title__ = 'Create Element'
__doc__   ="""This is a test of RevitAPI about
Creating/Deleting/Copying Elements."""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

# Regular + Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType

#.NET IMPORTS
import clr
clr.AddReference('System')
from System.Collections.Generic import List

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# =================================================

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIN
# =================================================
with Transaction(doc,__title__) as t :

    t.Start()


    pt_0 = XYZ(50, 0, 0)
    pt_1 = XYZ(55, 0, 0)
    pt_2 = XYZ(55, 5, 0)
    pt_3 = XYZ(50, 5, 0)

    l_0 = Line.CreateBound(pt_0, pt_1)
    l_1 = Line.CreateBound(pt_1, pt_2)
    l_2 = Line.CreateBound(pt_2, pt_3)
    l_3 = Line.CreateBound(pt_3, pt_0)

    boundary = CurveLoop()
    boundary.Append(l_0)
    boundary.Append(l_1)
    boundary.Append(l_2)
    boundary.Append(l_3)

    list_boundaries = List[CurveLoop]()
    Boundary = list_boundaries.Add(boundary)

    cubic = GeometryCreationUtilities.CreateExtrusionGeometry(list_boundaries, XYZ.BasisZ, 3300 / 304.8)

    direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
    direct_shape.SetShape([cubic])

    # material = ElementId(18953)
    # graphics_style_id = direct_shape.GetGraphicsStyleId()
    # graphics_style = doc.GetElement(graphics_style_id)
    #
    # graphics_style.SurfaceForegroundPatternId = FillPattern.RepeatingPatterns.Dots
    # graphics_style.SurfaceForegroundPatternColor = material.Color
    # graphics_style.SetProjectionFillColor(direct_shape.Category.Id, material.Color)

    t.Commit()