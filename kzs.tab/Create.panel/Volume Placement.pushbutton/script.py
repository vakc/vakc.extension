# -*- coding: utf-8 -*-
__title__ = 'Design \nVolume Placement'
__doc__   ="""Version = 1.0
Date      = 02.17.2024
_________________________________________________
Description:

This tool can generate architectural design masses for social
housing based on the location of the site and building lines,
taking into account the required building coverage and floor
area ratio.
_________________________________________________
How-to:

-> Select the CAD File (Get the Arch-Line).
-> Select the site (Floor).
-> Input the building coverage ratio.
-> Input the floor area ratio.
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

# Find 'Arch line' in cad file

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
                        gStyle = doc.GetElement(obj.GraphicsStyleId)
                        layer = gStyle.GraphicsStyleCategory.Name
                        layerNames.append(layer)
                        pline.append(obj)

for polyLine in pline:
    gStyle = doc.GetElement(polyLine.GraphicsStyleId)
    Layer = gStyle.GraphicsStyleCategory.Name
    if Layer == "Arch line":
        arch_line = polyLine

### Define Basic Variables
# Retrieve the Site Floor using pyrevit API
with forms.WarningBar(title='Pick Site Pad:'):
    site_geometry = revit.pick_element()
# Get the Site Floor Area Parameter
site_area      = site_geometry.get_Parameter(BuiltInParameter.HOST_AREA_COMPUTED).AsDouble() / 10.764
# Set the Design building area and floor area
building_area  = forms.ask_for_string(default='60',prompt='Selected site area is {} m².\nEnter building Area Ratio(%):'.format(site_area),title='Option Creator')
floor_area     = forms.ask_for_string(default='150',prompt='Selected site area is {} m².\nBuilding area is {} %.\nEnter Floor Area (%):'.format(site_area,building_area),title='Option Creator')


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIN
# =================================================

dynamo_model = StartupUtils.MakeModel(CLImode=True)
dynamo_model.Start()

try:
    # Implementing a while true loop to filter solutions that meet the design criteria
    while True:
        ### Define Design Variables
        # Random choice the angle for rotation based on an Arch_line
        rotate_value = random.choice([i for i in range(-8, 8, 1)])
        # Randomly selecting the number of floors for design
        floor_value = random.choice([i for i in range(8, 15, 1)])
        # Based on the randomly selected total number of floors, a list representing the height of all floor (no roof). Example: [0, 4000, 7400, 10800, 14200, 17600, 21000, 24400, 27800]
        f2 = floor_value - 2
        all_floor_elevation = sum(([0, 4000], [i for i in range(7400, (3400 * f2) + 7400, 3400)]), [])
        # Based on the randomly selected total number of floors, a list of each floor height
        floor_height = sum(([4000/304.8], [3400/304.8] * (floor_value - 1)), [])

        ### Using Dynamo Background
        # this line is important because converting geometry needs a reference of
        # DocumentManager.Instance.CurrentUIDocument, which is None if we don't set it
        # to current uidoc (luckily, they leave it public get/set)
        DocumentManager.Instance.CurrentUIDocument = revit.uidoc


        ### Define Site Boundary
        site_pad = site_geometry.get_Geometry(Options())
        # Explode the geometric solid of the Site Floor into multiple surfaces and flatten the list
        O1 = [value.ToProtoType() for value in site_pad]
        S1 = [Geometry.Explode(value) for value in O1]
        S2 = flatten_comprehension(S1)
        # Identify surface whose normal at the center aligns with the Z-axis direction for configuring the initial design face
        V1 = [Surface.NormalAtParameter(value, 0.5, 0.5) for value in S2]
        B1 = [Vector.IsAlmostEqualTo(value, Vector.ZAxis()) for value in V1]
        S3 = boolmask(S2, B1, True)
        # Convert the surface into a polycurve
        E1 = [value.Edges for value in S3]
        E2 = flatten_comprehension(E1)
        U1 = [value.CurveGeometry for value in E2]
        U2 = PolyCurve.ByJoinedCurves(tuple(U1),0.001,False,0)
        # Define Buildable Boundary : Offset 3.5 meter for define retreat distance.
        U3 = Curve.OffsetMany(U2, -3500, U2.Normal)

        ### Define Arch Line : Using Define Coordinate System
        U4 = arch_line.ToProtoType()
        # Project the arch_line onto the design face, retrieve the vector of this line, calculate the angle between this vector
        # and the x-axis. Establish a coordinate system at the center point of the arch_line in the direction of the arch_line
        P1 = Curve.PointAtParameter(U4, 0.5)
        C1 = CoordinateSystem.ByOrigin(P1)
        U5 = [Surface.ProjectInputOnto(value, U4, Vector.ZAxis()) for value in S3]
        N2 = Vector.AngleAboutAxis(U5[0][0].Direction, Vector.XAxis(), Vector.ZAxis())
        C2 = CoordinateSystem.Rotate(C1, P1, Vector.ZAxis(), -N2 + rotate_value)

        ### Point Placement
        # Creating a grid on the design face and placing points on it.
        step = 0.1
        u = [i * step for i in range(int(1 / step) + 1)]
        P2 = []
        for x in u:
            for y in u:
                P2.append(Surface.PointAtParameter(S3[0], x, y))
        # Filter out points that do not intersect with the design face.
        B2 = [Geometry.DoesIntersect(value, S3[0]) for value in P2]
        P3 = boolmask(P2, B2, True)
        # Filter out points with a distance less than 7500 from the edges of the buildable area.
        N3 = [Geometry.DistanceTo(value, U3[0]) for value in P3]
        B3 = [x >= 7500 for x in N3]
        # Randomly select one point from all the points that meet the specified criteria.
        P4 = random.choice(boolmask(P3, B3, True))

        ### First Placement
        # Assign a random value list for the arrangement of room types, ensuring that the initial point serves as the center.
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
        # Using the random list values and the X-axis of the design coordinate system as vectors.
        V2 = [Vector.Scale(C2.XAxis, value) for value in L2]
        # Move previously center point using the vector.
        P5 = [Geometry.Translate(P4, value) for value in V2]
        # Redefine the coordinate system for each initial point of the First Placement.
        C3 = [CoordinateSystem.ByOrigin(value) for value in P5]
        C4 = [CoordinateSystem.Rotate(value, value2, Vector.ZAxis(), -N2 + rotate_value) for value, value2 in zip(C3, P5)]
        # Place rectangles for individual room types.
        R1 = [Rectangle.ByWidthLength(value, value2, 8000) for value, value2 in zip(C4, L1)]
        # Randomly select a rectangle from a single room type as the initial position for Third Placement.
        R2 = random.choice(sum([boolmask(R1, [round(value.Width) == 4200 for value in R1], True)], []))
        # Remove the randomly selected rectangle, leaving the rest as all the units for First Placement.
        R3 = boolmask(R1, [value == R2 for value in R1], False)


        ### Second Placement
        # Move the First Placement directly using the Y-axis of the coordinate system for each initial point of the First
        # Placement as vectors, with a distance of 10200.(corridor 2200 plus unit depth 8000)
        V3 = [value.YAxis for value in C4]
        R4 = [Geometry.Translate(value, value2, 10200) for value, value2 in zip(R1, V3)]

        ### Third Placement
        # Extract the coordinate system of the randomly selected rectangle from First Placement and use it as the initial
        # coordinate system for Third Placement.
        C5 = boolmask(C4, [value == R2 for value in R1], True)
        # Assign a random value list for the arrangement of room types, ensuring that the initial point serves as the corner.
        # Starting from -4000 to account for moving half the room depth distance.
        L3 = [4200, 4200, 4200, 4200, 4200, 9100, 9100, 9100, 12800, 12800]
        random.shuffle(L3)
        L4 = []
        for i in range(len(L3)):
            if i <= 0:
                valuey = -4200 - (L3[i] / 2)
                L4.append(valuey)
                i += 1;
            else:
                valuey = valuey - ((L3[i - 1] + L3[i]) / 2)
                L4.append(valuey)
                if (i == len(L3) - 1):
                    break;
                i += 1;
        # After placing points along the Y-axis vector of the initial coordinate system, move them by a distance of 5100 along
        # the X-axis (half of the corridor 1100 plus half of the room depth 4000).
        C6 = [CoordinateSystem.Translate(C5[0], C5[0].YAxis, value) for value in L4]
        C7 = [CoordinateSystem.Translate(value, C5[0].XAxis, -5100) for value in C6]
        # Place rectangles for individual room types.
        R5 = [Rectangle.ByWidthLength(value, 8000, value2) for value, value2 in zip(C7, L3)]
        # Duplicate a set of initial coordinate systems for each room type unit along the X-axis direction, extending them to
        # the other side of the corridor, with a distance of 10200 (room depth 8000 plus corridor width 2200).
        R6 = [Geometry.Translate(value, C5[0].XAxis, 10200) for value in R5]


        ### All Rooms & Check Position
        # Merge all the rectangles of room type units into one list, where R3 represents First Placement, R4 represents Second
        # Placement, and R5 along with R6 represent Third Placement.
        R7 = sum([R3, R4, R5, R6], [])
        # Filter out units with a distance less than 1000 from the Buildable Boundary curve.
        N4 = [Geometry.DistanceTo(value, U3[0]) for value in R7]
        R8 = boolmask(R7, [x > 1000 for x in N4], True)
        # Filter out units that are outside the design face.
        # Some rectangles intersect with the Design Face, but they are not entirely within the surface. Utilize the intersection
        # of the two to check if it forms four lines, determining if the rectangle is fully inside the base.
        R9 = boolmask(R8, [Geometry.DoesIntersect(value, S3[0]) for value in R8], True)
        N5 = [Geometry.Intersect(value, S3[0]) for value in R9]
        R10 = boolmask(R9, [x == 4 for x in [len(value) for value in N5]], True)
        # Patch all the rectangles together to create a surface.
        S4 = [Surface.ByPatch(value) for value in R10]

        ### StairCase Position & Divide List
        # Retrieve the center points of all the rectangles for room-type units.
        P7 = [Polygon.Center(value) for value in R10]
        # Place a core for stairs every 500 square meters based on the area of all typical-floor room-type units. After calculating
        # the required number of cores, divide the total number of room unit by this value to determine the parameter for spacing
        # rooms between each core.
        N6 = round(len(P7) / (round(sum([value.Area for value in S4]) / 500000000) + 1))
        N7 = [i for i in range(random.choice([0, 1, 2, 3, 4, 5]), len(P7), int(N6))]
        # Retrieve the center points of the units to be replaced with stair cores.
        P8 = [P7[value] for value in N7]
        # Retrieve the rectangles of the units to be replaced with stair cores.
        R11 = [R10[value] for value in N7]
        # Remove all remaining room-type unit rectangles after excluding the stair core rectangles.
        R12 = [element for element in R10 if element not in R11]
        # Room Rectangle Length.
        N8 = [round(value) for value in [value.Length for value in R12]]
        # Two List / Rectangle and Length.
        D1 = list(zip(R12, N8))
        # SubList Rectangle-Length.
        R13 = sorted(D1, key=lambda x: x[1])
        # Use Length To Group Item.
        R14 = [list(group) for key, group in groupby([R13[i][0] for i in range(len(R13))], key=lambda x: N8[R12.index(x)])]
        # StairCase Volume + Room Volume.
        R15 = [R11] + R14
        # Move all flat rectangles according to the floor height distance.
        R16 = [[[Geometry.Translate(value, Vector.ZAxis(), value2) for value in sublist] for sublist in R15] for value2 in all_floor_elevation]
        # Group all rectangles of the same unit type into separate sublists.
        R17 = [sum(sublist, []) for sublist in zip(*R16)]
        # Place units on the same floor into separate sublists.
        R18 = []
        for value in R16:
            R18.append(list_flatten(value))
        # Decompose each unit's rectangle into four corner points.
        P9 = [[Polygon.Corners(value) for value in sublist] for sublist in R18]
        # Combine all unit rectangles into a single list and flatten it.
        R17_patch = [[Surface.ByPatch(value) for value in sublist] for sublist in R17]
        R17_patch2 = flatten_comprehension(R17_patch)


        ### First Corridor
        # Retrieve the center coordinate origin of the first rectangle in First Placement, move along the
        # Y-axis by a distance of 4000, and along the X-axis by the negative width of the first rectangle.
        P10 = Geometry.Translate(Geometry.Translate(P5[0], C4[0].YAxis, 4000), C4[0].XAxis, -L1[0] / 2)
        # Move a distance of 100000 along the X-axis from the extracted corridor origin.
        U4 = Line.ByStartPointDirectionLength(P10, C4[0].XAxis, 100000)
        # Retrieve units, among those that meet the boundary conditions, which intersect with the corridor line.
        U5 = [Geometry.Intersect(value, U4) for value in boolmask(R10, [Geometry.DoesIntersect(value, U4) for value in R10], True)]
        # Retrieve the line connecting the starting point of the first line and the endpoint of the last line in the intersection lines.
        U6 = Line.ByStartPointEndPoint(U5[0][0].StartPoint, U5[-1][0].EndPoint)
        # Create another edge line for the corridor (width 2200) and loft the two side reference lines together. Finally, retrieve the
        # vertices of the surface as reference points for creating the boundary of the corridor.
        U7 = Geometry.Translate(U6, C4[0].YAxis, 2200)
        S5 = [PolySurface.ByLoft([U6, U7])]
        V4 = S5[0].Vertices
        P11 = [value.PointGeometry for value in V4]
        # Move all corridor vertices according to the floor height distance.
        P12 = [[Geometry.Translate(value, Vector.ZAxis(), value2) for value in P11] for value2 in all_floor_elevation]


        ### Second Corridor
        # Retrieve the coordinate system previously used as the starting point for Third Placement, move it 1100 units along the X-axis
        # (half of the corridor), and 4000 units along the Y-axis to set it as the starting point for the second corridor.
        P13 = Geometry.Translate(Geometry.Translate(C5[0].Origin, C5[0].YAxis, 4000), C5[0].XAxis, 1100)
        # Move a distance of -100000 along the X-axis from the extracted corridor origin. The negative distance is used because Third
        # Placement is configured in the opposite direction of the source coordinate system.
        U8 = Line.ByStartPointDirectionLength(P13, C5[0].YAxis, -100000)
        # The reason for using try/except here is that there may be situations where configuring the Second corridor is not possible.
        # When such a situation occurs, the system needs to skip it and continue with the execution.
        try:
            # Similar to the method used for creating the First Corridor, start by finding intersection lines, then draw a line connecting
            # the start and end points. Offset by 2200, loft it into a single surface, retrieve the boundary points, and then move it according
            # to the all_floor_elevation.
            U9 = [Geometry.Intersect(value, U8) for value in boolmask(R10, [Geometry.DoesIntersect(value, U8) for value in R10], True)]
            U10 = Line.ByStartPointEndPoint(P13, U9[-1][0].EndPoint)
            U11 = Geometry.Translate(U10, C5[0].XAxis, -2200)
            S6 = [PolySurface.ByLoft([U10, U11])]
            V5 = S6[0].Vertices
            P14 = [value.PointGeometry for value in V5]
            P15 = [[Geometry.Translate(value, Vector.ZAxis(), value2) for value in P14] for value2 in all_floor_elevation]
        except:
            P15 = []
            S6 = []
        # It is assumed that when there is a Second corridor, the total surface will consider the presence of the Second Corridor, and vice versa.
        if S6:
            building_area_union = flatten_comprehension([R17_patch2 + S5 + S6])
        else:
            building_area_union = flatten_comprehension([R17_patch2 + S5])
        # First, union all surfaces together to create a single surface, and then calculate its area. This will be the total floor area.
        volume_surface = Surface.ByUnion(building_area_union)
        volume_surface_area = volume_surface.Area


        # Filter condition: Continue with the subsequent program when the Second corridor does exist and the total area is greater
        # than the volume floor area.
        if S6:
            if round((volume_surface_area / 1000000) , 2) > (site_area * float(floor_area) / 100):

                ### Floor Surface
                # Union all the typical floor mass rectangles together. (Room / Staircase / Corridor)
                S7 = [[Surface.ByPatch(value) for value in sublist] for sublist in R15]
                S8 = Surface.ByUnion(flatten_comprehension(S7))
                S9 = Surface.ByUnion(flatten_comprehension([[S8], S5, S6]))


                ### Column Point
                # Create a rational column spacing sequence by expanding from the centroid of the mass.
                N9 = [i for i in range(-69050, 73450, 7500)]
                # Place columns by offsetting from the center point of the first unit in Third Placement,
                # both to the left and right by the column spacing distance.
                C8 = [CoordinateSystem.Translate(C7[0], C7[0].XAxis, value) for value in N9]
                C9 = [[CoordinateSystem.Translate(value1, C7[0].YAxis, value2) for value1 in C8] for value2 in N9]
                # Flatten all coordinate systems into a single-layered list and retrieve the origins of the coordinate systems.
                C10 = flatten_comprehension(C9)
                P16 = [value.Origin for value in C10]
                # Identify all points that intersect with the design mass surface.
                B4 = [Geometry.DoesIntersect(value, S9) for value in P16]
                P17 = boolmask(P16, B4, True)

                ### Tree
                # Define the locations for placing trees within the site boundary.
                step = 0.1
                u1 = [i * step for i in range(int(1 / step) + 1)]
                step2 = 0.2
                u2 = [i * step for i in range(int(1 / step) + 1)]
                P18 = []
                for x in u1:
                    for y in u2:
                        P18.append(Surface.PointAtParameter(S3[0], x, y))
                # Identify all points that don't intersect with the design mass surface.
                P19 = boolmask(P18, [Geometry.DoesIntersect(value, S9) for value in P18], False)
                # The distance between tree placements must be greater than 7000 from the site boundary.
                N10 = [Geometry.DistanceTo(value, U2) for value in P19]
                P20 = boolmask(P19, [x > 7000 for x in N10], True)
                # All conditions are met, geometry generation is complete, and finally, the while true loop needs to be terminated.
                break




    # Since the current line function is Dynamo's function, the next step is to replace it with the Revit Line function as the
    # geometry needs to be converted into Revit objects.
    from Autodesk.Revit.DB import Line

    ### Element In Revit
    # All Revit element generation needs to be wrapped within a Transaction.
    with Transaction(doc, __title__) as t:

        t.Start()

        ### Create DirectShape Unit
        # Convert all corner points of residential and staircase unit rectangles to Revit geometry type, then wrap them with CurveLoops,
        # finally create a Revit DirectShape. The list here has two layers and needs to be unpacked.
        RP1 = [[[value.ToRevitType() for value in sublist] for sublist in sublist] for sublist in P9]
        curveloop = [[create_profile(value) for value in sublist] for sublist in RP1]
        options = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
        for idx, curve in enumerate(curveloop):
            for idx1, cur in enumerate(curve):
                list_boundaries = List[CurveLoop]()
                list_boundaries.Add(cur)
                curveloop[idx][idx1] = list_boundaries
        cubic = [[GeometryCreationUtilities.CreateExtrusionGeometry(value, XYZ.BasisZ, value2) for value in sublist] for value2, sublist in zip(floor_height,curveloop)]
        for idx, cub in enumerate(cubic):
            for idx1, c in enumerate(cub):
                direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
                direct_shape.SetShape([c])

        # Convert all corner points of first corridor to Revit geometry type, then wrap them with CurveLoops,
        # finally create a Revit DirectShape.
        RP2 = [[value.ToRevitType() for value in sublist] for sublist in P12]
        curveloop1 = [create_profile(value) for value in RP2]
        options1 = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
        for idx, curve in enumerate(curveloop1):
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(curve)
            curveloop1[idx] = list_boundaries
        cubic1 = [GeometryCreationUtilities.CreateExtrusionGeometry(value, XYZ.BasisZ, value2) for value,value2 in zip(curveloop1,floor_height)]
        for idx, cub in enumerate(cubic1):
            direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
            direct_shape.SetShape([cub])

        # Convert all corner points of second corridor to Revit geometry type, then wrap them with CurveLoops,
        # finally create a Revit DirectShape.
        RP3 = [[value.ToRevitType() for value in sublist] for sublist in P15]
        curveloop2 = [create_profile(value) for value in RP3]
        options2 = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
        for idx, curve in enumerate(curveloop2):
            list_boundaries = List[CurveLoop]()
            list_boundaries.Add(curve)
            curveloop2[idx] = list_boundaries
        cubic2 = [GeometryCreationUtilities.CreateExtrusionGeometry(value, XYZ.BasisZ, value2) for value,value2 in zip(curveloop2,floor_height)]
        for idx, cub in enumerate(cubic2):
            direct_shape = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
            direct_shape.SetShape([cub])

        ### Create Columns
        # Identify the foundational Level for placing columns, in this case, 'Level 1'.
        L1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
        for level in L1:
            if level.Name == 'Level 1':
                L2 = level
        # Identify the type of column to be placed, in this case, starting with the first type (default type).
        M1 = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsElementType().FirstElement()
        if M1 and not M1.IsActive:
            M1.Activate()
        # Convert points from Dynamo to Revit type, and then use these configured points to place columns.
        RC1 = [value.ToRevitType() for value in P17]
        columns = [doc.Create.NewFamilyInstance(value, M1, L2, StructuralType.NonStructural) for value in RC1]
        # Adjust the height of the columns based on the total building height.
        for column in columns:
            columns_height_Parameter = column.get_Parameter(BuiltInParameter.SCHEDULE_TOP_LEVEL_OFFSET_PARAM)
            columns_height_Parameter.Set((sum(floor_height)))

        ### Create Plantings
        # Define the type of trees to be placed, and then place the trees at the specified points.
        RP4 = [value.ToRevitType() for value in P20]
        small_tree = get_type_by_name("Scarlet Oak - 12.5 Meters")
        if small_tree and not small_tree.IsActive:
            small_tree.Activate()
        tree_placement = [doc.Create.NewFamilyInstance(value, small_tree, StructuralType.NonStructural) for value in RP4]

        t.Commit()



    # Print the data of the design option on the console.
    print('-' * 100)
    print('.Site Area:             {} m²'.format(site_area))
    print('.Floor Count:             {} m²'.format(floor_value))
    print('.Building Area:             {} m²'.format(round((volume_surface_area / floor_value / 1000000), 2)))
    print('.Floor Area:             {} m²'.format(round((volume_surface_area / 1000000), 2)))

    # Store the various performance indicators of the design option in a CSV file. If the CSV already exists,
    # update the existing file by appending the data.
    path = forms.ask_for_string(default='C:\Users\USER\Desktop', prompt='Enter csv save path:', title='Option Creator')
    csv_file_path = r'{}\data.csv'.format(path)
    if not os.path.isfile(csv_file_path):
        with io.open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Design Option', '', '', '', ''])
            writer.writerow(['Site Area', 'Floor Count', 'Building Area', 'Floor Area'])
            writer.writerow([site_area, floor_value, round((volume_surface_area / floor_value / 1000000), 2),round((volume_surface_area / 1000000), 2)])
    else:
        with io.open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            existing_data = list(reader)
            existing_data.append([site_area, floor_value, round((volume_surface_area / floor_value / 1000000), 2),round((volume_surface_area / 1000000), 2)])
        with io.open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(existing_data)

# Terminate the background execution of the Dynamo program.
finally:
    dynamo_model.ShutDown(shutdownHost=True)