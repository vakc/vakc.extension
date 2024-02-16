# -*- coding: utf-8 -*-
__title__ = 'Wall Parameters'
__doc__   ="""This is a test of RevitAPI Wall Parameters about 
how to work with them."""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

# Regular + Autodesk
from Autodesk.Revit.DB import *
from pyrevit import forms, revit

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# =================================================

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝  MAIN
# =================================================

with forms.WarningBar(title='Pick an Element:'):
    element = revit.pick_element()

element_type = type(element)

if element_type != Wall:
    forms.alert('You were supposed to pick a Wall.', exitscript=True)

print(element)
print(list(element.Parameters))

print('*** Parameters: ***')

for p in element.Parameters:
    if p.Definition.Name == 'Comments':  # DON'T USE THIS METHOD
        print("It's a Comment Parameter.")
        print(p.Id)
    print(p)
    print('.Name:             {}'.format(p.Definition.Name))
    print('.BuiltInParameter: {}'.format(p.Definition.BuiltInParameter))
    print('.StorageType:      {}'.format(p.StorageType))
    print('.IsShared:         {}'.format(p.IsShared))
    print('.IsReadOnly:       {}'.format(p.IsReadOnly))
    print("-"*50)

# ╔═╗╔═╗╔╦╗  ╔╗ ╦ ╦╦╦ ╔╦╗  ╦╔╗╔  ╔═╗╔═╗╦═╗╔═╗╔╦╗╔═╗╔╦╗╔═╗╦═╗╔═╗
# ║ ╦║╣  ║   ╠╩╗║ ║║║  ║───║║║║  ╠═╝╠═╣╠╦╝╠═╣║║║║╣  ║ ║╣ ╠╦╝╚═╗
# ╚═╝╚═╝ ╩   ╚═╝╚═╝╩╩═╝╩   ╩╝╚╝  ╩  ╩ ╩╩╚═╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═╚═╝  GET BUILT-IN PARAMETERS
# =========================================================================================

print('-' * 100)
print('*** Built-in Parameters: ***')
wall_comments  = element.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
wall_type_name = element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()

print('.Name:             {}'.format(wall_comments.Definition.Name))
print('.BuiltInParameter: {}'.format(wall_comments.Definition.BuiltInParameter))
print('.StorageType:      {}'.format(wall_comments.StorageType))
print('.IsShared:         {}'.format(wall_comments.IsShared))
print('.IsReadOnly:       {}'.format(wall_comments.IsReadOnly))
print("-"*50)

print(wall_comments.AsString())

# ╔═╗╔═╗╔╦╗  ╔═╗╔═╗╦═╗╔═╗╔╦╗╔═╗╔╦╗╔═╗╦═╗  ╔╗ ╦ ╦  ╔╗╔╔═╗╔╦╗╔═╗
# ║ ╦║╣  ║   ╠═╝╠═╣╠╦╝╠═╣║║║║╣  ║ ║╣ ╠╦╝  ╠╩╗╚╦╝  ║║║╠═╣║║║║╣
# ╚═╝╚═╝ ╩   ╩  ╩ ╩╩╚═╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═  ╚═╝ ╩   ╝╚╝╩ ╩╩ ╩╚═╝  GET PARAMETER BY NAME
# =========================================================================================

print('*** Getting Shared Parameters: ***')

# GET PROJECT/SHARED PARAMETER
sp_text = element.LookupParameter('sp_text')
# print(sp_text.AsString())

# sp_mat_id = element.LookupParameter('sp_material').AsElementId()
# sp_mat = doc.GetElement(sp_mat_id)
# print(sp_mat)
# print(sp_mat.Name)

sp_text = element.LookupParameter('sp_bool')
# print(sp_text.AsInteger())

# ╔═╗╔═╗╔╦╗  ╔╦╗╦ ╦╔═╗╔═╗  ╔═╗╔═╗╦═╗╔═╗╔╦╗╔═╗╔╦╗╔═╗╦═╗╔═╗
# ║ ╦║╣  ║    ║ ╚╦╝╠═╝║╣   ╠═╝╠═╣╠╦╝╠═╣║║║║╣  ║ ║╣ ╠╦╝╚═╗
# ╚═╝╚═╝ ╩    ╩  ╩ ╩  ╚═╝  ╩  ╩ ╩╩╚═╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═╚═╝  GET TYPE PARAMETERS
# =========================================================================================

print('-' * 100)
print("*** GET TYPE PARAMETERS ***")

wall_type = element.WallType
wall_type_description = wall_type.get_Parameter(BuiltInParameter.ALL_MODEL_DESCRIPTION)
wall_type_mark        = wall_type.get_Parameter(BuiltInParameter.WINDOW_TYPE_ID)

print(wall_type_description.AsString())
print(wall_type_mark.AsString())

# ╔═╗╔═╗╔╦╗  ╔═╗╔═╗╦═╗╔═╗╔╦╗╔═╗╔╦╗╔═╗╦═╗  ╦  ╦╔═╗╦  ╦ ╦╔═╗
# ╚═╗║╣  ║   ╠═╝╠═╣╠╦╝╠═╣║║║║╣  ║ ║╣ ╠╦╝  ╚╗╔╝╠═╣║  ║ ║║╣
# ╚═╝╚═╝ ╩   ╩  ╩ ╩╩╚═╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═   ╚╝ ╩ ╩╩═╝╚═╝╚═╝  SET PARAMETER VALUE
# =========================================================================================

# wall_comments = element.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
# sp_area       = element.LookupParameter('sp_area')
# sp_bool       = element.LookupParameter('sp_bool')
# sp_float      = element.LookupParameter('sp_float')
# sp_int        = element.LookupParameter('sp_int')
# sp_length     = element.LookupParameter('sp_length')
# sp_mat        = element.LookupParameter('sp_material')
# sp_text       = element.LookupParameter('sp_text')

# t = Transaction(doc, __title__)
#
# t.Start()
#
# wall_comments.Set('Where is the comment')
# print(wall_comments.AsString())
#
# sp_area.Set(555.55)
# sp_bool.Set(1)
# sp_float.Set(25.5)
# sp_int.Set(100)
# sp_length.Set(99.99)
# new_mat_id = ElementId(18974)
# sp_mat.Set(new_mat_id)
# sp_text.Set('here is it.')
#
# t.Commit()

# ╔═╗╦ ╦╔═╗╔╦╗╔═╗╔╦╗  ╔╦╗╔═╗╔═╗╦
# ║  ║ ║╚═╗ ║ ║ ║║║║   ║ ║ ║║ ║║
# ╚═╝╚═╝╚═╝ ╩ ╚═╝╩ ╩   ╩ ╚═╝╚═╝╩═╝  CUSTOM TOOL
# =========================================================================================

t = Transaction(doc, 'Writing ElementIds to Mark Parameter of Walls.')

t.Start()

wall_mark = element.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)
wall_mark.Set(str(element.Id))
print(element.Id)

t.Commit()

print('The script is complete.')