# -*- coding: utf-8 -*-
__title__ = 'CSV TEST'
__doc__   ="""This is a test of RevitAPI about calculate 
building cost."""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

# Regular + Autodesk
from Autodesk.Revit.DB import *
from pyrevit import forms, revit

import sys
import csv
import io


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝  VARIABLES
# =================================================

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application


csv_file_path = r'C:\Users\USER\Desktop\data.csv'


with forms.WarningBar(title='Pick an Element:'):
    elements = revit.pick_elements()


# ╔═╗╔═╗╦  ╦ ╦╔╦╗╔╗╔╔═╗  ╔═╗╔═╗╔═╗╔╦╗
# ║  ║ ║║  ║ ║║║║║║║╚═╗  ║  ║ ║╚═╗ ║
# ╚═╝╚═╝╩═╝╚═╝╩ ╩╝╚╝╚═╝  ╚═╝╚═╝╚═╝ ╩   COLUMNS COST
# =========================================================================================

column_types_info = {}

for element in elements:
    if isinstance(element, FamilyInstance):
        if element.Symbol.Category.Id.IntegerValue == int(BuiltInCategory.OST_Columns):
            column_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM)
            column_param_value = column_elem_type_param.AsValueString()

            column_volume = element.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble() / 35.315
            column_param_TopOffset = element.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).AsDouble() / 3.2808
            colume_param_BaseOffset = element.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM).AsDouble() / 3.2808
            column_param_TopLevelId = element.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).AsElementId()
            column_param_TopLevelHeight = doc.GetElement(column_param_TopLevelId).get_Parameter(BuiltInParameter.LEVEL_ELEV).AsDouble() / 3.2808
            column_param_BaseLevelId = element.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_PARAM).AsElementId()
            column_param_BaseLevelHeight = doc.GetElement(column_param_BaseLevelId).get_Parameter(BuiltInParameter.LEVEL_ELEV).AsDouble()
            column_height = column_param_TopOffset + column_param_TopLevelHeight - colume_param_BaseOffset - column_param_BaseLevelHeight

            if column_param_value not in column_types_info:
                column_types_info[column_param_value] = {
                    'type_name': column_param_value,
                    'column_all_volume': column_volume,
                    'column_all_height_1': column_height,
                    'column_all_height_2': column_height
                }
            else:
                column_types_info[column_param_value]['column_all_volume'] += column_volume
                column_types_info[column_param_value]['column_all_height_1'] += column_height
                column_types_info[column_param_value]['column_all_height_2'] += column_height

# Print the results
print('-' * 100)
print('*** Unit Price Analysis Table: ***')
print('-' * 100)
print('*** Column Analysis Table: ***')

for type_info in column_types_info.values():
    print('-' * 100)
    print('.Column Type Name:             {}'.format(type_info['type_name']))
    print('.Volume:             {} m³'.format(type_info['column_all_volume']))
    print('.Height:                     {} m'.format(type_info['column_all_height_1']))
    print('.Height:             {} m'.format(type_info['column_all_height_2']))

csv_file_path = 'C:\Users\USER\Desktop\data.csv'

with io.open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
    fieldnames = ['Column Type Name', '', '', '', '']
    writer = csv.writer(csv_file)
    writer.writerow(fieldnames)

    # Write data to the CSV file
    for index, type_info in enumerate(column_types_info.values(), start=1):
        writer.writerow([index, type_info['type_name'], '混凝土 Volume (m³)', type_info['column_all_volume']])
        writer.writerow(['', '', '主筋 Main Rebar (m)', type_info['column_all_height_1']])
        writer.writerow(['', '', '箍筋 Stirrup (m)', type_info['column_all_height_2']])
        writer.writerow(['', '', '', ''])


# ╔═╗╦═╗╔═╗╔╦╗╦╔╗╔╔═╗  ╔═╗╔═╗╔═╗╔╦╗
# ╠╣ ╠╦╝╠═╣║║║║║║║║ ╦  ║  ║ ║╚═╗ ║
# ╚  ╩╚═╩ ╩╩ ╩╩╝╚╝╚═╝  ╚═╝╚═╝╚═╝ ╩   FRAMING COST
# =========================================================================================


framing_types_info = {}

for element in elements:
    if isinstance(element, FamilyInstance):
        if element.Symbol.Category.Id.IntegerValue == int(BuiltInCategory.OST_StructuralFraming):
            Framing_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM)
            Framing_param_value = Framing_elem_type_param.AsValueString()

            Framing_volume = element.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble() / 35.315
            Framing_param_length = element.get_Parameter(BuiltInParameter.STRUCTURAL_FRAME_CUT_LENGTH).AsDouble() / 3.2808

            if Framing_param_value not in framing_types_info:
                framing_types_info[Framing_param_value] = {
                    'type_name': Framing_param_value,
                    'framing_all_volume': Framing_volume,
                    'framing_all_height_1': Framing_param_length,
                    'framing_all_height_2': Framing_param_length
                }
            else:
                framing_types_info[Framing_param_value]['framing_all_volume'] += Framing_volume
                framing_types_info[Framing_param_value]['framing_all_height_1'] += Framing_param_length
                framing_types_info[Framing_param_value]['framing_all_height_2'] += Framing_param_length


# Print the results

print('-' * 100)
print('*** Structural Framing Analysis Table: ***')

for type_info in framing_types_info.values():
    print('-' * 100)
    print('.Framing Type Name:             {}'.format(type_info['type_name']))
    print('.Volume:             {} m³'.format(type_info['framing_all_volume']))
    print('.Length:                     {} m'.format(type_info['framing_all_height_1']))
    print('.Length:             {} m'.format(type_info['framing_all_height_2']))

existing_data = []

with io.open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    existing_data = list(reader)

existing_data.append(['Framing Type Name', '', '', '', ''])

for index, type_info in enumerate(framing_types_info.values(), start=1):
    existing_data.append([index, type_info['type_name'], '混凝土 Volume (m³)', type_info['framing_all_volume']])
    existing_data.append(['', '', '主筋 Main Rebar (m)', type_info['framing_all_height_1']])
    existing_data.append(['', '', '箍筋 Stirrup (m)', type_info['framing_all_height_2']])
    existing_data.append(['', '', '', ''])

with io.open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(existing_data)


# ╦ ╦╔═╗╦  ╦    ╔═╗╔═╗╔═╗╔╦╗
# ║║║╠═╣║  ║    ║  ║ ║╚═╗ ║
# ╚╩╝╩ ╩╩═╝╩═╝  ╚═╝╚═╝╚═╝ ╩  WALL COST
# =========================================================================================


wall_types_info = {}

for element in elements:
    if isinstance(element, Wall):
        wall_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM)
        wall_param_value = wall_elem_type_param.AsValueString()

        wall_volume = element.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble() / 35.315
        wall_width  = element.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble() / 3.2808
        wall_height = element.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble() / 3.2808

        if wall_param_value not in wall_types_info:
            wall_types_info[wall_param_value] = {
                'type_name': wall_param_value,
                'wall_all_volume': wall_volume,
                'wall_all_width': wall_width,
                'wall_all_height': wall_height
            }
        else:
            wall_types_info[wall_param_value]['wall_all_volume'] += wall_volume
            wall_types_info[wall_param_value]['wall_all_width'] += wall_width
            wall_types_info[wall_param_value]['wall_all_height'] += wall_height


# Print the results

print('-' * 100)
print('*** Wall Analysis Table: ***')

for type_info in wall_types_info.values():
    print('-' * 100)
    print('.Wall Type Name:             {}'.format(type_info['type_name']))
    print('.Volume:             {} m³'.format(type_info['wall_all_volume']))
    print('.Width:                     {} m'.format(type_info['wall_all_width']))
    print('.Height:             {} m'.format(type_info['wall_all_height']))

existing_data.append(['Wall Type Name', '', '', '', ''])

for index, type_info in enumerate(wall_types_info.values(), start=1):
    existing_data.append([index, type_info['type_name'], '混凝土 Volume (m³)', type_info['wall_all_volume']])
    existing_data.append(['', '', '橫向主筋 Main Rebar (m)', type_info['wall_all_height']])
    existing_data.append(['', '', '縱向箍筋 Main Rebar (m)', type_info['wall_all_width']])
    existing_data.append(['', '', '', ''])


# ╔═╗╦  ╔═╗╔═╗╦═╗  ╔═╗╔═╗╔═╗╔╦╗
# ╠╣ ║  ║ ║║ ║╠╦╝  ║  ║ ║╚═╗ ║
# ╚  ╩═╝╚═╝╚═╝╩╚═  ╚═╝╚═╝╚═╝ ╩   FLOOR COST
# =========================================================================================

floor_types_info = {}

for element in elements:
    if isinstance(element, Floor):
        floor_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM)
        floor_param_value = floor_elem_type_param.AsValueString()

        floor_volume = element.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble() / 35.315


        if floor_param_value not in floor_types_info:
            floor_types_info[floor_param_value] = {
                'type_name': floor_param_value,
                'floor_all_volume': floor_volume
            }
        else:
            floor_types_info[floor_param_value]['floor_all_volume'] += floor_volume

# Print the results

print('-' * 100)
print('*** Floor Analysis Table: ***')

for type_info in floor_types_info.values():
    print('-' * 100)
    print('.Floor Type Name:             {}'.format(type_info['type_name']))
    print('.Volume:                     {} m³'.format(type_info['floor_all_volume']))

existing_data.append(['Floor Type Name', '', '', '', ''])

for index, type_info in enumerate(floor_types_info.values(), start=1):
    existing_data.append([index, type_info['type_name'], '混凝土 Volume (m³)', type_info['floor_all_volume']])
    existing_data.append(['', '', '', ''])


# ╦ ╦╦╔╗╔╔╦╗╔═╗╦ ╦╔═╗  ╔═╗╔╗╔╔╦╗  ╔╦╗╔═╗╔═╗╦═╗╔═╗  ╔═╗╔═╗╔═╗╔╦╗
# ║║║║║║║ ║║║ ║║║║╚═╗  ╠═╣║║║ ║║   ║║║ ║║ ║╠╦╝╚═╗  ║  ║ ║╚═╗ ║
# ╚╩╝╩╝╚╝═╩╝╚═╝╚╩╝╚═╝  ╩ ╩╝╚╝═╩╝  ═╩╝╚═╝╚═╝╩╚═╚═╝  ╚═╝╚═╝╚═╝ ╩   WINDOWS AND DOORS COST
# =========================================================================================


windows_doors_info = {}

for element in elements:
    if isinstance(element, FamilyInstance):
        if (element.Symbol.Category.Id.IntegerValue == int(BuiltInCategory.OST_Doors)) or (element.Symbol.Category.Id.IntegerValue == int(BuiltInCategory.OST_Windows)):
            windows_doors_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM)
            windows_doors_param_value = windows_doors_elem_type_param.AsValueString()

            if windows_doors_param_value not in windows_doors_info:
                windows_doors_info[windows_doors_param_value] = {
                    'type_name': windows_doors_param_value,
                    'count': 1
                }
            else:
                windows_doors_info[windows_doors_param_value]['count'] += 1

# Print the results
print('-' * 100)
print('*** Windows/Doors Analysis Table: ***')

for windows_doors_type, info in windows_doors_info.items():
    print('-' * 100)
    print('.Window/Doors Type Name:        {}'.format(info['type_name']))
    print('.Count:                      {}'.format(info['count']))

existing_data.append(['Window/Door Type Name', '', '', '', ''])

for index, type_info in enumerate(windows_doors_info.values(), start=1):
    existing_data.append([index, type_info['type_name'], '門數量 Count', type_info['count']])
    existing_data.append(['', '', '', ''])


# ╦═╗╔═╗╦╦  ╦╔╗╔╔═╗  ╔═╗╔═╗╔═╗╔╦╗
# ╠╦╝╠═╣║║  ║║║║║ ╦  ║  ║ ║╚═╗ ║
# ╩╚═╩ ╩╩╩═╝╩╝╚╝╚═╝  ╚═╝╚═╝╚═╝ ╩   RAILING COST
# =========================================================================================

railing_types_info = {}

for element in elements:
    if element.Category.Name == 'Railings':
        railing_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM)
        railing_param_value = railing_elem_type_param.AsValueString()

        railing_length = element.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble() / 3.2808

        if railing_param_value not in railing_types_info:
            railing_types_info[railing_param_value] = {
                'type_name': railing_param_value,
                'railing_all_length': railing_length
            }
        else:
            railing_types_info[railing_param_value]['railing_all_length'] += railing_length


# Print the results

print('-' * 100)
print('*** Railing Analysis Table: ***')

for type_info in railing_types_info.values():
    print('-' * 100)
    print('.Railing Type Name:             {}'.format(type_info['type_name']))
    print('.Length:                     {} m²'.format(type_info['railing_all_length']))

existing_data.append(['Railing Type Name', '', '', '', ''])

for index, type_info in enumerate(railing_types_info.values(), start=1):
    existing_data.append([index, type_info['type_name'], '欄杆長度 Length (m)', type_info['railing_all_length']])
    existing_data.append(['', '', '', ''])


# ╔═╗╦ ╦╦═╗╔╗╔╦╔╦╗╦ ╦╦═╗╔═╗  ╔═╗╔═╗╔═╗╔╦╗
# ╠╣ ║ ║╠╦╝║║║║ ║ ║ ║╠╦╝║╣   ║  ║ ║╚═╗ ║
# ╚  ╚═╝╩╚═╝╚╝╩ ╩ ╚═╝╩╚═╚═╝  ╚═╝╚═╝╚═╝ ╩  FURNITURE COST
# =========================================================================================


furniture_info = {}

for element in elements:
    if isinstance(element, FamilyInstance):
        if (element.Symbol.Category.Id.IntegerValue != int(BuiltInCategory.OST_Doors)) and (element.Symbol.Category.Id.IntegerValue != int(BuiltInCategory.OST_Windows)) and (element.Symbol.Category.Id.IntegerValue != int(BuiltInCategory.OST_Columns)) and (element.Symbol.Category.Id.IntegerValue != int(BuiltInCategory.OST_StructuralFraming)):
            furniture_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM)
            furniture_param_value = furniture_elem_type_param.AsValueString()

            if furniture_param_value not in furniture_info:
                furniture_info[furniture_param_value] = {
                    'type_name': furniture_param_value,
                    'count': 1
                }
            else:
                furniture_info[furniture_param_value]['count'] += 1

# Print the results
print('-' * 100)
print('*** Furniture Analysis Table: ***')

for furniture_type, info in furniture_info.items():

    print('-' * 100)
    print('.Furniture Type Name:        {}'.format(info['type_name']))
    print('.Count:                      {}'.format(info['count']))

existing_data.append(['Furniture/Device Type Name', '', '', '', ''])

for index, type_info in enumerate(furniture_info.values(), start=1):
    existing_data.append([index, type_info['type_name'], '數量 Count', type_info['count']])
    existing_data.append(['', '', '', ''])


# ╔═╗╔═╗╦  ╦╔═╗╔╦╗╔═╗╔╗╔╔╦╗
# ╠═╝╠═╣╚╗╔╝║╣ ║║║║╣ ║║║ ║
# ╩  ╩ ╩ ╚╝ ╚═╝╩ ╩╚═╝╝╚╝ ╩   PAVEMENT
# =========================================================================================


room_types_info = {}

for element in elements:
    if element.Category.Name == 'Rooms':
        Pavement_param_value = element.get_Parameter(BuiltInParameter.ROOM_NAME).AsValueString()

        Pavement_floor = element.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble() / 10.764
        Pavement_ceiling  = element.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble() / 10.764
        Pavement_wall_Perimeter = element.get_Parameter(BuiltInParameter.ROOM_PERIMETER).AsDouble() / 3.2808
        Pavement_room_Volume = element.get_Parameter(BuiltInParameter.ROOM_VOLUME).AsDouble() / 35.315
        Pavement_wall_height = round( Pavement_room_Volume / Pavement_floor , 2 )
        Pavement_wall = Pavement_wall_Perimeter * Pavement_wall_height

        if Pavement_param_value not in room_types_info:
            room_types_info[Pavement_param_value] = {
                'type_name': Pavement_param_value,
                'Pavement_all_floor': Pavement_floor,
                'Pavement_all_ceiling': Pavement_ceiling,
                'Pavement_all_wall': Pavement_wall
            }
        else:
            room_types_info[Pavement_param_value]['Pavement_all_floor'] += Pavement_floor
            room_types_info[Pavement_param_value]['Pavement_all_ceiling'] += Pavement_ceiling
            room_types_info[Pavement_param_value]['Pavement_all_wall'] += Pavement_wall


# Print the results

print('-' * 100)
print('*** Room Analysis Table: ***')

for type_info in room_types_info.values():
    print('-' * 100)
    print('.Room Name:             {}'.format(type_info['type_name']))
    print('.Floor:             {} m²'.format(type_info['Pavement_all_floor']))
    print('.Ceiling:                     {} m²'.format(type_info['Pavement_all_ceiling']))
    print('.Wall:             {} m²'.format(type_info['Pavement_all_wall']))

existing_data.append(['Room Type Name', '', '', '', ''])

for index, type_info in enumerate(room_types_info.values(), start=1):
    existing_data.append([index, type_info['type_name'], '地板面積 Floor Area (m²)', type_info['Pavement_all_floor']])
    existing_data.append(['', '', '天花板面積 Ceiling Area (m²)', type_info['Pavement_all_ceiling']])
    existing_data.append(['', '', '牆壁面積 Wall Area(m²)', type_info['Pavement_all_wall']])
    existing_data.append(['', '', '', ''])


with io.open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(existing_data)












