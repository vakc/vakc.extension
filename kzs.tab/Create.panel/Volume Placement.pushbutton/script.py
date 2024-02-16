# -*- coding: utf-8 -*-
__title__ = 'Volume Placement'
__doc__   ="""This is a test of RevitAPI about using Dynamo API
study Volume Placement."""

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

# Define Basic Variables

with forms.WarningBar(title='Pick an Element:'):
    site_geometry = revit.pick_element()
site_area      = site_geometry.get_Parameter(BuiltInParameter.HOST_AREA_COMPUTED).AsDouble() / 10.764
building_area  = forms.ask_for_string(default='150',prompt='Selected site area is {} m².\nEnter building Area Ratio(%):'.format(site_area),title='Option Creator')
floor_area     = forms.ask_for_string(default='150',prompt='Selected site area is {} m².\nBuilding area is {} %.\nEnter Floor Area (%):'.format(site_area,building_area),title='Option Creator')
rotate_value   = random.choice([i for i in range(0,360,10)])
floor_value    = random.choice([i for i in range(8,15,1)])
f1             = floor_value - 2
f2             = floor_value - 1
typical_floor  = [i for i in range(7600,(3300*f1)+7600,3300)]
ground_floor   = sum(([0,4000],[i for i in range(7600,(3300*f2)+7600,3300)]),[])

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
    opt = Options()
    outlist = []
    geom = site_geometry.get_Geometry(opt)

    # Site Boundary
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

    # Placement Point
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
    P3 = random.choice(boolmask(P2, B3, True))

    # First Placement
    L1 = [4200, 4200, 4200, 4200, 4200, 9100, 9100, 9100, 12800, 12800]
    random.shuffle(L1)
    L2 = []
    for i in range(len(L1)):
        if i <= 0:
            valuey = -40000 + (L1[i] / 2)
            L2.append(valuey)
            i += 1;
        else:
            valuey = valuey + ((L1[i - 1] + L1[i]) / 2)
            L2.append(valuey)
            if (i == len(L1) - 1):
                break
            i += 1
    V1 = [Vector.Scale(Vector.YAxis(), value) for value in L2]
    V2 = [Vector.Rotate(value, Vector.ZAxis(), rotate_value) for value in V1]
    P4 = [Geometry.Translate(P3, value) for value in V2]
    C2 = [CoordinateSystem.ByOrigin(value) for value in P4]
    C3 = [CoordinateSystem.Rotate(value, value2, Vector.ZAxis(), rotate_value) for value, value2 in zip(C2, P4)]
    R1 = [Rectangle.ByWidthLength(value, 8000, value2) for value, value2 in zip(C3, L1)]
    R2 = random.choice(sum([boolmask(R1, [round(value.Height) == 4200 for value in R1], True)], []))
    R3 = boolmask(R1, [value == R2 for value in R1], False)

    # Second Placement
    V3 = [value.XAxis for value in C3]
    R4 = [Geometry.Translate(value, value2, 10200) for value, value2 in zip(R1, V3)]

    # Third Placement
    C4 = boolmask(C3, [value == R2 for value in R1], True)
    L3 = [4200, 4200, 4200, 4200, 4200, 9100, 9100, 9100, 12800, 12800]
    random.shuffle(L3)
    L4 = []
    for i in range(len(L3)):
        if i <= 0:
            valuey = -4000 - (L3[i] / 2)
            L4.append(valuey)
            i += 1;
        else:
            valuey = valuey - ((L3[i - 1] + L3[i]) / 2)
            L4.append(valuey)
            if (i == len(L3) - 1):
                break;
            i += 1;
    C5 = [CoordinateSystem.Translate(C4[0], C4[0].XAxis, value) for value in L4]
    C6 = [CoordinateSystem.Translate(value, C4[0].YAxis, -5100) for value in C5]
    R5 = [Rectangle.ByWidthLength(value, value2, 8000) for value, value2 in zip(C6, L3)]
    R6 = [Geometry.Translate(value, C4[0].YAxis, 10200) for value in R5]

    # All Rooms & Check Position
    R7 = sum([R3, R4, R5, R6], [])
    N3 = [Geometry.DistanceTo(value, U2[0]) for value in R7]
    R8 = boolmask(R7, [x > 1000 for x in N3], True)
    R9 = boolmask(R8, [Geometry.DoesIntersect(value, S3[0]) for value in R8], True)
    N4 = [Geometry.Intersect(value, S3[0]) for value in R9]
    R10 = boolmask(R9, [x == 4 for x in [len(value) for value in N4]], True)
    S4 = [Surface.ByPatch(value) for value in R10]

    # StairCase Position & Divide List
    P5 = [Polygon.Center(value) for value in R10]
    N5 = round(len(P5) / (round(sum([value.Area for value in S4]) / 500000000) + 1))
    N6 = [i for i in range(random.choice([0, 1, 2, 3, 4, 5]), len(P5), int(N5))]
    P6 = [P5[value] for value in N6]
    R11 = [R10[value] for value in N6]  # StairCase Volume
    R12 = [element for element in R10 if element not in R11]  # Room Volume
    N7 = [round(value) for value in [value.Length for value in R12]]  #  Room Rectangle Length
    D1 = list(zip(R12, N7))  # Two List / Rectangle and Length
    R13 = sorted(D1, key=lambda x: x[1])  #  SubList Rectangle-Length
    R14 = [list(group) for key, group in groupby([R13[i][0] for i in range(len(R13))], key=lambda x: N7[R12.index(x)])]  # Use Length To Group Item
    R15 = [R11] + R14  # StairCase Volume + Room Volume
    R16 = [[[Geometry.Translate(value, Vector.ZAxis(), value2) for value in sublist] for sublist in R15] for value2 in ground_floor]
    R17 = [sum(sublist, []) for sublist in zip(*R16)]
    P7 = [[Polygon.Corners(value) for value in sublist] for sublist in R17]
    R17_patch = [[Surface.ByPatch(value) for value in sublist] for sublist in R17]
    R17_patch2 = flatten_comprehension(R17_patch)


    # First Corridor

    P8 = Geometry.Translate(Geometry.Translate(P4[0], C3[0].XAxis, 4000), C3[0].YAxis, -L1[0] / 2)
    U3 = Line.ByStartPointDirectionLength(P8, C3[0].YAxis, 100000)
    U4 = [Geometry.Intersect(value, U3) for value in boolmask(R10, [Geometry.DoesIntersect(value, U3) for value in R10], True)]
    U5 = Line.ByStartPointEndPoint(U4[0][0].StartPoint, U4[-1][0].EndPoint)
    U6 = Geometry.Translate(U5, C3[0].XAxis, 2200)
    S5 = [PolySurface.ByLoft([U5, U6])]
    V4 = S5[0].Vertices
    P9 = [value.PointGeometry for value in V4]
    P10 = [[Geometry.Translate(value, Vector.ZAxis(), value2) for value in P9] for value2 in ground_floor]

    # Second Corridor

    P11 = Geometry.Translate(Geometry.Translate(C4[0].Origin, C4[0].XAxis, 4000), C4[0].YAxis, 1100)
    U7 = Line.ByStartPointDirectionLength(P11, C4[0].XAxis, -100000)
    try:
        U8 = [Geometry.Intersect(value, U7) for value in boolmask(R10, [Geometry.DoesIntersect(value, U7) for value in R10], True)]
        U9 = Line.ByStartPointEndPoint(P11, U8[-1][0].StartPoint)
        U10 = Geometry.Translate(U9, C4[0].YAxis, -2200)
        S6 = [PolySurface.ByLoft([U9, U10])]
        V5 = S6[0].Vertices
        P12 = [value.PointGeometry for value in V5]
        P13 = [[Geometry.Translate(value, Vector.ZAxis(), value2) for value in P12] for value2 in ground_floor]
    except:
        P13 = []
        S6  = []

    if S6:
        building_area_union = flatten_comprehension([R17_patch2 + S5 + S6])
    else:
        building_area_union = flatten_comprehension([R17_patch2 + S5])

    volume_surface = Surface.ByUnion(building_area_union)
    volume_surface_area = volume_surface.Area



    # Column Point

    N8 = [i for i in range(-46550,43450,7500)]
    C7 = [CoordinateSystem.Translate(C6[0], C6[0].XAxis, value) for value in N8]
    C8 = [[CoordinateSystem.Translate(value1, C6[0].YAxis, value2) for value1 in C7] for value2 in N8]
    C9 = flatten_comprehension(C8)
    P14 = [value.Origin for value in C9]
    B4 = [Geometry.DoesIntersect(value, volume_surface) for value in P14]
    P15 = boolmask(P14, B4, True)
    RC1 = [value.ToRevitType() for value in P15]



    from Autodesk.Revit.DB import Line

    # Volume In Revit

    RP1 = [[[value.ToRevitType() for value in sublist] for sublist in sublist] for sublist in P7]
    curveloop = [[create_profile(value) for value in sublist] for sublist in RP1]
    options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
    for idx, curve in enumerate(curveloop):
        for idx1, cur in enumerate(curve):
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(cur)
            curveloop[idx][idx1] = list_boundaries
    cubic = [[GeometryCreationUtilities.CreateExtrusionGeometry(value, XYZ.BasisZ, 3300/304.8) for value in sublist] for sublist in curveloop]

    RP2 = [[value.ToRevitType() for value in sublist] for sublist in P10]
    curveloop1 = [create_profile(value) for value in RP2]
    options1 = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
    for idx, curve in enumerate(curveloop1):
        list_boundaries = List[CurveLoop]()
        list_boundaries.Add(curve)
        curveloop1[idx] = list_boundaries
    cubic1 = [GeometryCreationUtilities.CreateExtrusionGeometry(value, XYZ.BasisZ, 3300/304.8) for value in curveloop1]

    if P13:
        RP3 = [[value.ToRevitType() for value in sublist] for sublist in P13]
        curveloop2 = [create_profile(value) for value in RP3]
        options2 = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
        for idx, curve in enumerate(curveloop2):
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(curve)
            curveloop2[idx] = list_boundaries
        cubic2 = [GeometryCreationUtilities.CreateExtrusionGeometry(value, XYZ.BasisZ, 3300 / 304.8) for value in curveloop2]

    else :
        cubic2 = []


    with Transaction(doc,__title__) as t :

        t.Start()

        for idx, cub in enumerate(cubic):
            for idx1, c in enumerate(cub):
                direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                direct_shape.SetShape([c])

        for idx, cub in enumerate(cubic1):
            direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
            direct_shape.SetShape([cub])

        if cubic2:
            for idx, cub in enumerate(cubic2):
                direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                direct_shape.SetShape([cub])


        L1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().FirstElementId()
        M1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsElementType().FirstElement()

        if M1 and not M1.IsActive:
            M1.Activate()

        columns = [doc.Create.NewFamilyInstance(value, M1, doc.GetElement(L1), StructuralType.NonStructural) for value in RC1]
        for column in columns:
            columns_height_Parameter = column.get_Parameter(BuiltInParameter.SCHEDULE_TOP_LEVEL_OFFSET_PARAM)
            columns_height_Parameter.Set( ( (f1*3300) + 7600) / 304.8)


        t.Commit()



    print('-' * 100)
    print('.Site Area:             {} m²'.format(site_area))
    print('.Floor Count:             {} m²'.format(floor_value))
    print('.Building Area:             {} m²'.format(round((volume_surface_area/1000000),2)))
    print('.Floor Area:             {} m²'.format( round((volume_surface_area * floor_value /1000000) , 2)))



    #
    # N3 = [i for i in range(8000, 15000, 1000)]
    # N4 = random.choice(N3)
    # N5 = round ( number_area/float(N4) ,0 )
    #
    # rot = [i for i in range(0, 360, 10)]
    # rotate = random.choice(rot)
    #
    #
    # D1 = CoordinateSystem.ByOrigin(P4)
    # D2 = CoordinateSystem.Rotate(D1, P4, Vector.ZAxis(), rotate)
    # R1 = Rectangle.ByWidthLength(D2,N4,N5)
    # C2 = Geometry.Explode(R1)
    #
    # L1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().FirstElementId()
    #
    #
    # S4 = Surface.ByPatch(R1)
    # N6 = round( S4.Area / 1000000 ,2 )
    #
    # print('.Floor Area:             {} m²'.format(N6))
    # print('.Width:             {} m'.format(N4/1000))
    # print('.Length:                     {} m'.format(N5/1000))
    #
    # P5 = Polygon.Center(R1)
    # N7 = [i for i in range(-10000, 10000, 4000)]
    #
    # P3 = []
    # for x in N7:
    #     for y in N7:
    #         V1 = Vector.Scale(D2.XAxis,x)
    #         P6 = Geometry.Translate(P5, V1)
    #         V2 = Vector.Scale(D2.YAxis,y)
    #         P7 = Geometry.Translate(P6, V2)
    #         P3.append(P7)
    #
    # B4 = [Geometry.DoesIntersect(value, S4) for value in P3]
    # P8 = boolmask(P3, B4, True)
    # M1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsElementType().FirstElement()
    #
    #
    #
    # with Transaction(doc,__title__) as t :
    #
    #     t.Start()
    #
    #     if M1 and not M1.IsActive:
    #         M1.Activate()
    #
    #     RC1 = [value.ToRevitType() for value in C2]
    #     [Wall.Create(doc, value, L1, False) for value in RC1]
    #
    #     RP1 = [value.ToRevitType() for value in P8]
    #     [doc.Create.NewFamilyInstance(value, M1, doc.GetElement(L1), StructuralType.NonStructural) for value in RP1]
    #
    #     t.Commit()






finally:
    dynamo_model.ShutDown(shutdownHost=True)