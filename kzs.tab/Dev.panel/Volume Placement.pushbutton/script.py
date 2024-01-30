# -*- coding: utf-8 -*-
__title__ = 'Volume Placement'
__doc__   ="""This is a test of RevitAPI about using Dynamo
Doing Volume Placement."""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================
import sys
import clr
import random

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
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

import clr
clr.AddReference('System')
from System.Collections.Generic import List

clr.AddReference("DynamoApplications")
from Dynamo.Applications import StartupUtils


from pyrevit import forms, revit


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# =================================================

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

active_view = doc.ActiveView

def boolmask(list1, list2, condition):
    return [elem1 for elem1, elem2 in zip(list1, list2) if elem2 == condition]

def flatten_comprehension(matrix):
    return [item for row in matrix for item in row]


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIN
# =================================================

with forms.WarningBar(title='Pick an Element:'):
    element = revit.pick_element()

dynamo_model = StartupUtils.MakeModel(CLImode=True)
dynamo_model.Start()

try:
    # this line is important because converting geometry needs a reference of
    # DocumentManager.Instance.CurrentUIDocument, which is None if we don't set it
    # to current uidoc (luckily, they leave it public get/set)
    DocumentManager.Instance.CurrentUIDocument = revit.uidoc

    opt = Options()
    outlist = []

    geom = element.get_Geometry(opt)

    O1 = [value.ToProtoType() for value in geom]
    S1 = [Geometry.Explode(value) for value in O1]
    S2 = flatten_comprehension(S1)

    N1 = [Surface.NormalAtParameter(value, 0.5, 0.5) for value in S2]
    B1 = [Vector.IsAlmostEqualTo(value, Vector.ZAxis()) for value in N1]
    S3 = boolmask(S2, B1, True)
    E1 = [value.Edges for value in S3]
    E2 = flatten_comprehension(E1)
    U1 = [value.CurveGeometry for value in E2]
    C1 = PolyCurve.ByJoinedCurves(tuple(U1),0.001,False,0)


    U2 = Curve.OffsetMany(C1, -3500, C1.Normal)
    # P1 = []
    # for i in range(10):
    #     for j in range(10):
    #         P1.append(Surface.PointAtParameter(tuple(S3)[0], i / 10, j / 10))
    step = 0.1
    u = [i * step for i in range(int(1 / step) + 1)]

    P1 = []
    for x in u:
        for y in u:
            P1.append(Surface.PointAtParameter(S3[0], x, y))

    B2 = [Geometry.DoesIntersect(value, S3[0]) for value in P1]
    P2 = boolmask(P1, B2, True)
    N2 = [Geometry.DistanceTo(value, U2[0]) for value in P2]
    B3 = [x >= 7500 for x in N2]
    P4 = random.choice(boolmask(P2, B3, True))


    N3 = [i for i in range(8000, 15000, 1000)]
    N4 = random.choice(N3)
    N5 = round ( 150000000/float(N4) ,0 )

    rot = [i for i in range(0, 360, 10)]
    rotate = random.choice(rot)


    D1 = CoordinateSystem.ByOrigin(P4)
    D2 = CoordinateSystem.Rotate(D1, P4, Vector.ZAxis(), rotate)
    R1 = Rectangle.ByWidthLength(D2,N4,N5)
    C2 = Geometry.Explode(R1)



    L1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().FirstElementId()




    S4 = Surface.ByPatch(R1)
    N6 = round( S4.Area / 1000000 ,2 )

    print('.Floor Area:             {} m²'.format(N6))
    print('.Width:             {} m'.format(N4))
    print('.Length:                     {} m'.format(N5))

    P5 = Polygon.Center(R1)
    N7 = [i for i in range(-10000, 10000, 4000)]

    P3 = []
    for x in N7:
        for y in N7:
            V1 = Vector.Scale(D2.XAxis,x)
            P6 = Geometry.Translate(P5, V1)
            V2 = Vector.Scale(D2.YAxis,y)
            P7 = Geometry.Translate(P6, V2)
            P3.append(P7)

    B4 = [Geometry.DoesIntersect(value, S4) for value in P3]
    P8 = boolmask(P3, B4, True)
    M1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsElementType().FirstElement()


    with Transaction(doc,__title__) as t :

        t.Start()

        RC1 = [value.ToRevitType() for value in C2]
        [Wall.Create(doc, value, L1, False) for value in RC1]

        RP1 = [value.ToRevitType() for value in P8]
        [doc.Create.NewFamilyInstance(value, M1, doc.GetElement(L1), StructuralType.NonStructural) for value in RP1]

        t.Commit()






finally:
    dynamo_model.ShutDown(shutdownHost=True)