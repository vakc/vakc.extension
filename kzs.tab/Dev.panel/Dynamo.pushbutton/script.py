# -*- coding: utf-8 -*-
__title__ = 'Dynamo Test'
__doc__   ="""This is a test of RevitAPI about using Dynamo
Creating/Deleting/Copying Elements."""
#
# # ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# # ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# # ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# # =================================================
#
# import clr
# import sys
#
# import Autodesk
# from Autodesk.Revit.DB import *
# from Autodesk.Revit.DB.Structure import StructuralType
#
#
# clr.AddReference('ProtoGeometry')
# from Autodesk.DesignScript.Geometry import *
#
#
# clr.AddReference('RevitNodes')
# import Revit
# clr.ImportExtensions(Revit.Elements)
# clr.ImportExtensions(Revit.GeometryConversion)
#
#
# # ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# # ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
# #  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# # =================================================
#
# doc   = __revit__.ActiveUIDocument.Document
# uidoc = __revit__.ActiveUIDocument
# app   = __revit__.Application
#
# active_view = doc.ActiveView
#
# with Transaction(doc,__title__) as t :
#
#     t.Start()
#
#
#     C1 = Line.ByStartPointEndPoint(Point.ByCoordinates(0,0,0),Point.ByCoordinates(1000,0,0))
#     H1 = 3400
#     L1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().FirstElementId()
#     W1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType().FirstElement()
#
#     # Start
#     S1 = C1.ToRevitType()
#
#     Wall.Create(doc, S1, L1, False)
#
#
#     t.Commit()

import clr

clr.AddReference("DynamoApplications")
from Dynamo.Applications import StartupUtils


dynamo_model = StartupUtils.MakeModel(CLImode=True)
dynamo_model.Start()
clr.AddReference("RevitNodes")


import Revit
clr.ImportExtensions(Revit.GeometryConversion)
clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralType

from pyrevit import revit

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

active_view = doc.ActiveView



try:
    # this line is important because converting geometry needs a reference of
    # DocumentManager.Instance.CurrentUIDocument, which is None if we don't set it
    # to current uidoc (luckily, they leave it public get/set)
    DocumentManager.Instance.CurrentUIDocument = revit.uidoc

    C1 = Line.ByStartPointEndPoint(Point.ByCoordinates(0,0,0),Point.ByCoordinates(1000,0,0))
    C2 = Line.ByStartPointEndPoint(Point.ByCoordinates(0,2000,0),Point.ByCoordinates(1000,2000,0))
    H1 = 3400
    L1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().FirstElementId()
    W1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType().FirstElement()

    with Transaction(doc,__title__) as t :

        t.Start()
        # Start
        S1 = C1.ToRevitType()
        S2 = C2.ToRevitType()

        Wall.Create(doc, S1, L1, False)
        Wall.Create(doc, S2, L1, False)


        t.Commit()

finally:
    dynamo_model.ShutDown(shutdownHost=True)















