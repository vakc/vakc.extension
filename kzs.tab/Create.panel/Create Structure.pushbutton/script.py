# -*- coding: utf-8 -*-
__title__ = 'Create Structure'
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

    # # ╔═╗╦ ╦╔═╗╔═╗╔╦╗╔═╗
    # # ╚═╗╠═╣║╣ ║╣  ║ ╚═╗
    # # ╚═╝╩ ╩╚═╝╚═╝ ╩ ╚═╝  SHEETS
    # # =================================================
    # Titleblock_Id = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().FirstElementId()
    # New_sheet = ViewSheet.Create(doc, Titleblock_Id)
    # New_sheet.SheetNumber = 'First Sheet'
    # New_sheet.Name = 'First'

    # # ╦  ╦╦╔═╗╦ ╦╔═╗
    # # ╚╗╔╝║║╣ ║║║╚═╗
    # #  ╚╝ ╩╚═╝╚╩╝╚═╝  VIEWS
    # # =================================================
    # all_view_types = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
    # View_3D_type = [vt for vt in all_view_types if vt.ViewFamily == ViewFamily.ThreeDimensional][0]
    # new_3D = View3D.CreateIsometric(doc, View_3D_type.Id)

    # # ╦═╗╔═╗╔═╗╦╔═╗╔╗╔
    # # ╠╦╝║╣ ║ ╦║║ ║║║║
    # # ╩╚═╚═╝╚═╝╩╚═╝╝╚╝
    # # =================================================
    region_type_id = doc.GetDefaultElementTypeId(ElementTypeGroup.FilledRegionType)

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

    region = FilledRegion.Create(doc, region_type_id, active_view.Id, list_boundaries)

    # # ╔═╗╦  ╔═╗╔═╗╦═╗╔═╗
    # # ╠╣ ║  ║ ║║ ║╠╦╝╚═╗
    # # ╚  ╩═╝╚═╝╚═╝╩╚═╚═╝  FLOORS
    # # =================================================
    # floor_type_Id = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType().FirstElementId()
    # all_floor_in_views = FilteredElementCollector(doc).OfClass(Floor).WhereElementIsNotElementType().ToElements()
    # pt_4 = XYZ(40, -5, 0)
    # pt_5 = XYZ(60, -5, 0)
    # pt_6 = XYZ(60, 10, 0)
    # pt_7 = XYZ(40, 10, 0)
    #
    # l_4 = Line.CreateBound(pt_4, pt_5)
    # l_5 = Line.CreateBound(pt_5, pt_6)
    # l_6 = Line.CreateBound(pt_6, pt_7)
    # l_7 = Line.CreateBound(pt_7, pt_4)
    #
    # boundary = CurveLoop()
    #
    # boundary.Append(l_4)
    # boundary.Append(l_5)
    # boundary.Append(l_6)
    # boundary.Append(l_7)

    # pt_0 = XYZ(50, 0, 0)
    # pt_1 = XYZ(55, 0, 0)
    # pt_2 = XYZ(55, 5, 0)
    # pt_3 = XYZ(50, 5, 0)
    #
    # l_0 = Line.CreateBound(pt_0, pt_1)
    # l_1 = Line.CreateBound(pt_1, pt_2)
    # l_2 = Line.CreateBound(pt_2, pt_3)
    # l_3 = Line.CreateBound(pt_3, pt_0)
    #
    # boundary1 = CurveArray()
    #
    # boundary1.Append(l_0)
    # boundary1.Append(l_1)
    # boundary1.Append(l_2)
    # boundary1.Append(l_3)

    # list_boundaries = List[CurveLoop]()
    # list_boundaries.Add(boundary)
    # list_boundaries.Add(boundary1)

    # floor = Floor.Create(doc, list_boundaries, floor_type_Id, active_level.Id)
    # floor = doc.Create.NewOpening(all_floor_in_views[0], boundary1, False)

    # # ╔═╗╔═╗╔═╗╦ ╦  ╔═╗╦  ╔═╗╔╦╗╔═╗╔╗╔╔╦╗╔═╗
    # # ║  ║ ║╠═╝╚╦╝  ║╣ ║  ║╣ ║║║║╣ ║║║ ║ ╚═╗
    # # ╚═╝╚═╝╩   ╩   ╚═╝╩═╝╚═╝╩ ╩╚═╝╝╚╝ ╩ ╚═╝  COPY ELEMENTS
    # # =====================================================================================
    #
    # all_floor_in_views = FilteredElementCollector(doc).OfClass(Floor).WhereElementIsNotElementType().ToElementIds()
    # elements_to_copy = List[ElementId](all_floor_in_views)
    # for i in range(1,6):
    #     vector = XYZ(0, 10*i, 0)
    #     ElementTransformUtils.CopyElements(doc, elements_to_copy, vector)

    # # ╔╦╗╔═╗╦  ╔═╗╔╦╗╔═╗  ╔═╗╦  ╔═╗╔╦╗╔═╗╔╗╔╔╦╗╔═╗
    # #  ║║║╣ ║  ║╣  ║ ║╣   ║╣ ║  ║╣ ║║║║╣ ║║║ ║ ╚═╗
    # # ═╩╝╚═╝╩═╝╚═╝ ╩ ╚═╝  ╚═╝╩═╝╚═╝╩ ╩╚═╝╝╚╝ ╩ ╚═╝  DELETE ELEMENTS
    # # =====================================================================================
    #
    # all_floor_in_views = FilteredElementCollector(doc).OfClass(Floor).WhereElementIsNotElementType().ToElementIds()
    # elements_to_delete = List[ElementId](all_floor_in_views)
    # doc.Delete(elements_to_delete)



    t.Commit()





















