# -*- coding: utf-8 -*-
__title__ = 'Architecture Cost'
__doc__   ="""This is a test of RevitAPI about calculate 
building cost using parameter 'Cost' of
each element type."""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝  IMPORTS
# =================================================

# Regular + Autodesk
from Autodesk.Revit.DB import *
from pyrevit import forms, revit

import sys


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

try:

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
                column_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
                column_param_value = column_elem_type_param.AsValueString()

                column_volume = element.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble() / 35.315
                column_cost = element.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_COST).AsDouble()
                column_total_cost = round(column_volume * column_cost, 0)

                if column_param_value not in column_types_info:
                    column_types_info[column_param_value] = {
                        'type_name': column_param_value,
                        'column_cost': column_cost,
                        'column_all_volume': column_volume,
                        'All_Cost': column_total_cost
                    }
                else:
                    column_types_info[column_param_value]['column_all_volume'] += column_volume
                    column_types_info[column_param_value]['All_Cost'] += column_cost


    # Print the results
    print('-' * 100)
    print('*** Unit Price Analysis Table: ***')
    print('-' * 100)
    print('*** Column Analysis Table: ***')

    for type_info in column_types_info.values():
        print('-' * 100)
        print('.Column Type Name:             {}'.format(type_info['type_name']))
        print('.Cost(per m³):             {} NT$'.format(type_info['column_cost']))
        print('.Volume:                     {} m³'.format(type_info['column_all_volume']))
        print('.Type Cost:             {} NT$'.format(type_info['All_Cost']))


    # ╔═╗╦═╗╔═╗╔╦╗╦╔╗╔╔═╗  ╔═╗╔═╗╔═╗╔╦╗
    # ╠╣ ╠╦╝╠═╣║║║║║║║║ ╦  ║  ║ ║╚═╗ ║
    # ╚  ╩╚═╩ ╩╩ ╩╩╝╚╝╚═╝  ╚═╝╚═╝╚═╝ ╩   FRAMING COST
    # =========================================================================================

    framing_types_info = {}

    for element in elements:
        if isinstance(element, FamilyInstance):
            if element.Symbol.Category.Id.IntegerValue == int(BuiltInCategory.OST_StructuralFraming):
                Framing_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
                Framing_param_value = Framing_elem_type_param.AsValueString()

                Framing_volume = element.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble() / 35.315
                Framing_cost = element.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_COST).AsDouble()
                Framing_total_cost = round(Framing_volume * Framing_cost, 0)

                if Framing_param_value not in framing_types_info:
                    framing_types_info[Framing_param_value] = {
                        'type_name': Framing_param_value,
                        'framing_cost': Framing_cost,
                        'framing_all_volume': Framing_volume,
                        'All_Cost': Framing_total_cost
                    }
                else:
                    framing_types_info[Framing_param_value]['framing_all_volume'] += Framing_volume
                    framing_types_info[Framing_param_value]['All_Cost'] += Framing_cost


    # Print the results

    print('-' * 100)
    print('*** Structural Framing Analysis Table: ***')

    for type_info in framing_types_info.values():
        print('-' * 100)
        print('.Framing Type Name:             {}'.format(type_info['type_name']))
        print('.Cost(per m³):             {} NT$'.format(type_info['framing_cost']))
        print('.Volume:                     {} m³'.format(type_info['framing_all_volume']))
        print('.Type Cost:             {} NT$'.format(type_info['All_Cost']))


    # ╦ ╦╔═╗╦  ╦    ╔═╗╔═╗╔═╗╔╦╗
    # ║║║╠═╣║  ║    ║  ║ ║╚═╗ ║
    # ╚╩╝╩ ╩╩═╝╩═╝  ╚═╝╚═╝╚═╝ ╩  WALL COST
    # =========================================================================================

    wall_types_info = {}

    for element in elements:
        if isinstance(element, Wall):
            wall_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
            wall_param_value = wall_elem_type_param.AsValueString()

            wall_volume = element.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble() / 35.315
            wall_cost = element.WallType.get_Parameter(BuiltInParameter.ALL_MODEL_COST).AsDouble()
            wall_total_cost = round(wall_volume * wall_cost, 0)

            if wall_param_value not in wall_types_info:
                wall_types_info[wall_param_value] = {
                    'type_name': wall_param_value,
                    'wall_cost': wall_cost,
                    'wall_all_volume': wall_volume,
                    'All_Cost': wall_total_cost
                }
            else:
                wall_types_info[wall_param_value]['wall_all_volume'] += wall_volume
                wall_types_info[wall_param_value]['All_Cost'] += wall_total_cost


    # Print the results

    print('-' * 100)
    print('*** Wall Analysis Table: ***')

    for type_info in wall_types_info.values():
        print('-' * 100)
        print('.Wall Type Name:             {}'.format(type_info['type_name']))
        print('.Cost(per m³):             {} NT$'.format(type_info['wall_cost']))
        print('.Volume:                     {} m³'.format(type_info['wall_all_volume']))
        print('.Type Cost:             {} NT$'.format(type_info['All_Cost']))


    # ╔═╗╦  ╔═╗╔═╗╦═╗  ╔═╗╔═╗╔═╗╔╦╗
    # ╠╣ ║  ║ ║║ ║╠╦╝  ║  ║ ║╚═╗ ║
    # ╚  ╩═╝╚═╝╚═╝╩╚═  ╚═╝╚═╝╚═╝ ╩   FLOOR COST
    # =========================================================================================

    floor_types_info = {}

    for element in elements:
        if isinstance(element, Floor):
            floor_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
            floor_param_value = floor_elem_type_param.AsValueString()

            floor_volume = element.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble() / 35.315
            floor_cost = element.FloorType.get_Parameter(BuiltInParameter.ALL_MODEL_COST).AsDouble()
            floor_total_cost = round(floor_volume * floor_cost, 0)

            if floor_param_value not in floor_types_info:
                floor_types_info[floor_param_value] = {
                    'type_name': floor_param_value,
                    'floor_cost': floor_cost,
                    'floor_all_volume': floor_volume,
                    'All_Cost': floor_total_cost
                }
            else:
                floor_types_info[floor_param_value]['floor_all_volume'] += floor_volume
                floor_types_info[floor_param_value]['All_Cost'] += floor_total_cost


    # Print the results

    print('-' * 100)
    print('*** Floor Analysis Table: ***')

    for type_info in floor_types_info.values():
        print('-' * 100)
        print('.Floor Type Name:             {}'.format(type_info['type_name']))
        print('.Cost(per m³):             {} NT$'.format(type_info['floor_cost']))
        print('.Volume:                     {} m³'.format(type_info['floor_all_volume']))
        print('.Type Cost:             {} NT$'.format(type_info['All_Cost']))


    # ╔═╗╔╦╗╔═╗╦╦═╗╔═╗
    # ╚═╗ ║ ╠═╣║╠╦╝╚═╗
    # ╚═╝ ╩ ╩ ╩╩╩╚═╚═╝  STAIRS
    # =========================================================================================

    stairs_types_info = {}

    for element in elements:
        if element.Category.Name == 'Stairs':
            stairs_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
            stairs_param_value = stairs_elem_type_param.AsValueString()
            stairs_riser_count = element.get_Parameter(BuiltInParameter.STAIRS_ACTUAL_NUM_RISERS).AsInteger()
            stairs_cost = doc.GetElement(element.GetTypeId()).get_Parameter(BuiltInParameter.ALL_MODEL_COST).AsDouble()
            stairs_total_cost = round(stairs_riser_count * stairs_cost, 0)

            if stairs_param_value not in stairs_types_info:
                stairs_types_info[stairs_param_value] = {
                    'type_name': stairs_param_value,
                    'stairs_cost': stairs_cost,
                    'stairs_all_riser_count': stairs_riser_count,
                    'All_Cost': stairs_total_cost
                }
            else:
                stairs_types_info[stairs_param_value]['stairs_all_riser_count'] += stairs_riser_count
                stairs_types_info[stairs_param_value]['All_Cost'] += stairs_total_cost


    # Print the results

    print('-' * 100)
    print('*** Stairs Analysis Table: ***')

    for type_info in stairs_types_info.values():
        print('-' * 100)
        print('.Stair Type Name:             {}'.format(type_info['type_name']))
        print('.Cost(per m²):             {} NT$'.format(type_info['stairs_cost']))
        print('.Riser Count:                     {} '.format(type_info['stairs_all_riser_count']))
        print('.Type Cost:             {} NT$'.format(type_info['All_Cost']))



    # ╦ ╦╦╔╗╔╔╦╗╔═╗╦ ╦╔═╗  ╔═╗╔╗╔╔╦╗  ╔╦╗╔═╗╔═╗╦═╗╔═╗  ╔═╗╔═╗╔═╗╔╦╗
    # ║║║║║║║ ║║║ ║║║║╚═╗  ╠═╣║║║ ║║   ║║║ ║║ ║╠╦╝╚═╗  ║  ║ ║╚═╗ ║
    # ╚╩╝╩╝╚╝═╩╝╚═╝╚╩╝╚═╝  ╩ ╩╝╚╝═╩╝  ═╩╝╚═╝╚═╝╩╚═╚═╝  ╚═╝╚═╝╚═╝ ╩   WINDOWS AND DOORS COST
    # =========================================================================================


    windows_doors_info = {}

    for element in elements:
        if isinstance(element, FamilyInstance):
            if (element.Symbol.Category.Id.IntegerValue == int(BuiltInCategory.OST_Doors)) or (element.Symbol.Category.Id.IntegerValue == int(BuiltInCategory.OST_Windows)):
                windows_doors_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
                windows_doors_param_value = windows_doors_elem_type_param.AsValueString()

                if windows_doors_param_value not in windows_doors_info:
                    windows_doors_info[windows_doors_param_value] = {
                        'type_name': windows_doors_param_value,
                        'count': 1,
                        'cost': element.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_COST).AsDouble()
                    }
                else:
                    windows_doors_info[windows_doors_param_value]['count'] += 1

    # Print the results
    print('-' * 100)
    print('*** Windows/Doors Analysis Table: ***')

    for windows_doors_type, info in windows_doors_info.items():
        total_cost = round(info['count'] * info['cost'], 0)

        print('-' * 100)
        print('.Window/Doors Type Name:        {}'.format(info['type_name']))
        print('.Cost(per):                  {} NT$'.format(info['cost']))
        print('.Count:                      {}'.format(info['count']))
        print('.Type Cost:                  {} NT$'.format(total_cost))


    # ╦═╗╔═╗╦╦  ╦╔╗╔╔═╗  ╔═╗╔═╗╔═╗╔╦╗
    # ╠╦╝╠═╣║║  ║║║║║ ╦  ║  ║ ║╚═╗ ║
    # ╩╚═╩ ╩╩╩═╝╩╝╚╝╚═╝  ╚═╝╚═╝╚═╝ ╩   RAILING COST
    # =========================================================================================

    railing_types_info = {}

    for element in elements:
        if element.Category.Name == 'Railings':
            railing_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
            railing_param_value = railing_elem_type_param.AsValueString()

            railing_length = element.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble() / 3.2808
            railing_cost = doc.GetElement(element.GetTypeId()).get_Parameter(BuiltInParameter.ALL_MODEL_COST).AsDouble()
            railing_total_cost = round(railing_length * railing_cost, 0)

            if railing_param_value not in railing_types_info:
                railing_types_info[railing_param_value] = {
                    'type_name': railing_param_value,
                    'railing_cost': railing_cost,
                    'railing_all_length': railing_length,
                    'All_Cost': railing_total_cost
                }
            else:
                railing_types_info[railing_param_value]['railing_all_length'] += railing_length
                railing_types_info[railing_param_value]['All_Cost'] += railing_total_cost


    # Print the results

    print('-' * 100)
    print('*** Railing Analysis Table: ***')

    for type_info in railing_types_info.values():
        print('-' * 100)
        print('.Railing Type Name:             {}'.format(type_info['type_name']))
        print('.Cost(per m²):             {} NT$'.format(type_info['railing_cost']))
        print('.Length:                     {} m²'.format(type_info['railing_all_length']))
        print('.Type Cost:             {} NT$'.format(type_info['All_Cost']))


    # ╔═╗╦ ╦╦═╗╔╗╔╦╔╦╗╦ ╦╦═╗╔═╗  ╔═╗╔═╗╔═╗╔╦╗
    # ╠╣ ║ ║╠╦╝║║║║ ║ ║ ║╠╦╝║╣   ║  ║ ║╚═╗ ║
    # ╚  ╚═╝╩╚═╝╚╝╩ ╩ ╚═╝╩╚═╚═╝  ╚═╝╚═╝╚═╝ ╩  FURNITURE COST
    # =========================================================================================


    furniture_info = {}

    for element in elements:
        if isinstance(element, FamilyInstance):
            if (element.Symbol.Category.Id.IntegerValue != int(BuiltInCategory.OST_Doors)) and (element.Symbol.Category.Id.IntegerValue != int(BuiltInCategory.OST_Windows)) and (element.Symbol.Category.Id.IntegerValue != int(BuiltInCategory.OST_Columns)) and (element.Symbol.Category.Id.IntegerValue != int(BuiltInCategory.OST_StructuralFraming)):
                furniture_elem_type_param = element.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
                furniture_param_value = furniture_elem_type_param.AsValueString()

                if furniture_param_value not in furniture_info:
                    furniture_info[furniture_param_value] = {
                        'type_name': furniture_param_value,
                        'count': 1,
                        'cost': element.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_COST).AsDouble()
                    }
                else:
                    furniture_info[furniture_param_value]['count'] += 1

    # Print the results
    print('-' * 100)
    print('*** Furniture Analysis Table: ***')

    for furniture_type, info in furniture_info.items():
        total_cost = round(info['count'] * info['cost'], 0)

        print('-' * 100)
        print('.Furniture Type Name:        {}'.format(info['type_name']))
        print('.Cost(per):                  {} NT$'.format(info['cost']))
        print('.Count:                      {}'.format(info['count']))
        print('.Type Cost:                  {} NT$'.format(total_cost))




    # ╔╦╗╔═╗╔╦╗╔═╗╦    ╔═╗╦═╗╦╔═╗╔═╗
    #  ║ ║ ║ ║ ╠═╣║    ╠═╝╠╦╝║║  ║╣
    #  ╩ ╚═╝ ╩ ╩ ╩╩═╝  ╩  ╩╚═╩╚═╝╚═╝  TOTAL PRICE
    # =========================================================================================


    print('-' * 100)
    print('*** Total Price: ***')
    print('-' * 100)

    # Total Columns Cost
    columns_total_cost = sum(info['All_Cost'] for info in column_types_info.values())
    print('.Total Columns Cost:       {} NT$'.format(columns_total_cost))

    # Total Structural Framing Cost
    Framing_total_cost = sum(info['All_Cost'] for info in framing_types_info.values())
    print('.Total Structural Framing Cost:       {} NT$'.format(Framing_total_cost))

    # Total Wall Cost
    walls_total_cost = sum(info['All_Cost'] for info in wall_types_info.values())
    print('.Total Wall Cost:       {} NT$'.format(walls_total_cost))

    # Total Floor Cost
    floor_total_cost = sum(info['All_Cost'] for info in floor_types_info.values())
    print('.Total Floor Cost:       {} NT$'.format(floor_total_cost))

    # Total Stairs Cost
    stair_total_cost = sum(info['All_Cost'] for info in stairs_types_info.values())
    print('.Total Stairs Cost:       {} NT$'.format(stair_total_cost))

    # Total Windows/Doors Cost
    windows_doors_total_cost = sum(round(info['count'] * info['cost'], 0) for info in windows_doors_info.values())
    print('.Total Windows/Doors Cost:  {} NT$'.format(windows_doors_total_cost))

    # Total Railing Cost
    railing_total_cost = sum(info['All_Cost'] for info in railing_types_info.values())
    print('.Total Railing Cost:       {} NT$'.format(railing_total_cost))

    # Total Furniture Cost
    furniture_total_cost = sum(round(info['count'] * info['cost'], 0) for info in furniture_info.values())
    print('.Total Furniture Cost:  {} NT$'.format(furniture_total_cost))


    print('-' * 100)
    # Overall Total Cost
    overall_total_cost = columns_total_cost + Framing_total_cost + walls_total_cost + floor_total_cost + stair_total_cost + windows_doors_total_cost + railing_total_cost + furniture_total_cost
    print('.Overall Total Cost:    {} NT$'.format(overall_total_cost))


except:
    sys.exit







