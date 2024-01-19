# -*- coding: utf-8 -*-
__title__ = 'Dynamo Test'
__doc__   ="""This is a test of RevitAPI about using Dynamo
Creating/Deleting/Copying Elements."""

# Load the Python Standard and DesignScript Libraries
import sys

import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# clr.AddReference("RevitAPI")
#
# import Autodesk
# from Autodesk.Revit.DB import *

Point = Point.ByCoordinates(0,0,0)
Point2 = Point.ByCoordinates(100,0,0)






















