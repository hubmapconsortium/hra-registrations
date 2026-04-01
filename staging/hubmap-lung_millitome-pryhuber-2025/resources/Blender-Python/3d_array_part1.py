# workflow to produce cutting matrix segment_matrix
# 2026-3-12
#
# V1.02
# -read inputs from config_file
# -updated orientation of bounding-box (-X, -Y, +Z)

import bpy
import bmesh
import os
import typing
import mathutils
import csv
from pathlib import Path
from math import radians

# read config file-------------------------------------------------------------
config_file = "config_file.txt"
print(config_file)

with open(config_file) as f:
    # 4 lines
    # 1 = sample ID
    # 2 = segments X
    # 3 = segments Y
    # 4 = segments Z
    sample_id = f.readline()[:-1]
    model_string = f.readline()[:-1]
    segments_x = int(f.readline()[:-1])
    segments_y = int(f.readline()[:-1])
    segments_z = int(f.readline()[:-1])

print("Sample ID = "+sample_id)

segments_base_name = sample_id  # collection name and root name for copies of LUL

#-----segmentation info header-----------it's this or config_file
#   !!label order/spreadsheet: y(int), z(char), x(int)!!
#   when looking from TOP orientation
# segments_x = 3        # blocks (right to left)
# segments_y = 4        # slices (top to bottom)
# segments_z = 2        # layers = strips (z towards viewer))
#segments_base_name = "D260-LUL"  # collection name and root name for copies of LUL

# the following three cleanup procedures are mutually exclusive, only one should be True at any one time.
# if all three are false no cleanup takes place
delete_empties = True      # delete empty segments
delete_unselected = False   # delete unselected
hide_unselected = False      # hide unselected

name_debugging = False  # True: sequence#, name, X,Y,Z all numbers; False: name, X<chr), Y<int>, Z<chr>
natural_order = False   # True: X<chr), Y<int>, Z<chr>; False: Y(int), Z(char), X(int) = Gloria's order
add_materials = True    # True: apply materials (colors) for better visual distinction, materials need to be in file!

#----------read data from csv file-------------------
csv_folder = Path("")                       # placeholder - not used right now
csv_file = "RUI_blocks.csv"                 # this should come from config file
csv_file_path = os.path.join(csv_folder/csv_file)
print ('reading csv file: ' + csv_file_path)

segments_base_name = sample_id

block_list_array = []

# assemble primary array from selection in primary csv file
with open(csv_file_path) as file:
    csv_file = csv.reader(file)
    counter = 0

    for line in csv_file:
        col1_lab_ID = line[0]
        col2_sample_ID = line[1]
        sample_ID = col2_sample_ID[:8]
        col3_y = line[2]
        col4_z = line[3]
        col5_x = line[4]
        col6_gender = line[5]

        if col1_lab_ID != "origin_lab_id":       # skip header line of CSV file
            # col1 match or blank AND col2 match or blank
            if (sample_ID == segments_base_name):
                counter += 1
                block_list_array.append(col2_sample_ID)

                print (sample_ID)

        else:
            headers1_list = line     # pick up headers
            print(headers1_list)


print(f'number items in block_list_array: {counter}')
print (block_list_array)

#----extended setup
#------to create extended object names------DO NOT Change
matrix_base_name = 'Segment_Matrix' + "-" + segments_base_name  # collection of cutting segments
organ_sample = segments_base_name + "-sample"                   # collection for organ segments


# make bounding box geometry node
def bounding_box_1_node_group(node_tree_names: dict[typing.Callable, str]):
    """Initialize Bounding Box node group"""
    bounding_box_1 = bpy.data.node_groups.new(type='GeometryNodeTree', name="Bounding Box")

    bounding_box_1.color_tag = 'NONE'
    bounding_box_1.description = ""
    bounding_box_1.default_group_node_width = 140

    # bounding_box_1 interface

    # Socket Bounding Box
    bounding_box_socket = bounding_box_1.interface.new_socket(name="Bounding Box", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    bounding_box_socket.attribute_domain = 'POINT'
    bounding_box_socket.default_input = 'VALUE'
    bounding_box_socket.structure_type = 'AUTO'

    # Socket Min
    min_socket = bounding_box_1.interface.new_socket(name="Min", in_out='OUTPUT', socket_type='NodeSocketVector')
    min_socket.default_value = (0.0, 0.0, 0.0)
    min_socket.min_value = -3.4028234663852886e+38
    min_socket.max_value = 3.4028234663852886e+38
    min_socket.subtype = 'NONE'
    min_socket.attribute_domain = 'POINT'
    min_socket.default_input = 'VALUE'
    min_socket.structure_type = 'AUTO'

    # Socket Max
    max_socket = bounding_box_1.interface.new_socket(name="Max", in_out='OUTPUT', socket_type='NodeSocketVector')
    max_socket.default_value = (0.0, 0.0, 0.0)
    max_socket.min_value = -3.4028234663852886e+38
    max_socket.max_value = 3.4028234663852886e+38
    max_socket.subtype = 'NONE'
    max_socket.attribute_domain = 'POINT'
    max_socket.default_input = 'VALUE'
    max_socket.structure_type = 'AUTO'

    # Socket Geometry
    geometry_socket = bounding_box_1.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    geometry_socket.attribute_domain = 'POINT'
    geometry_socket.default_input = 'VALUE'
    geometry_socket.structure_type = 'AUTO'

    # Socket Use Radius
    use_radius_socket = bounding_box_1.interface.new_socket(name="Use Radius", in_out='INPUT', socket_type='NodeSocketBool')
    use_radius_socket.default_value = True
    use_radius_socket.attribute_domain = 'POINT'
    use_radius_socket.description = "For curves, point clouds, and Grease Pencil, take the radius attribute into account when computing the bounds."
    use_radius_socket.default_input = 'VALUE'
    use_radius_socket.structure_type = 'AUTO'

    # Initialize bounding_box_1 nodes

    # Node Group Input
    group_input = bounding_box_1.nodes.new("NodeGroupInput")
    group_input.name = "Group Input"

    # Node Group Output
    group_output = bounding_box_1.nodes.new("NodeGroupOutput")
    group_output.name = "Group Output"
    group_output.is_active_output = True

    # Node Bounding Box
    bounding_box_2 = bounding_box_1.nodes.new("GeometryNodeBoundBox")
    bounding_box_2.name = "Bounding Box"

    # Set locations
    bounding_box_1.nodes["Group Input"].location = (-440.0, 0.0)
    bounding_box_1.nodes["Group Output"].location = (300.0, 0.0)
    bounding_box_1.nodes["Bounding Box"].location = (-70.0, 0.0)

    # Set dimensions
    bounding_box_1.nodes["Group Input"].width  = 140.0
    bounding_box_1.nodes["Group Input"].height = 100.0

    bounding_box_1.nodes["Group Output"].width  = 140.0
    bounding_box_1.nodes["Group Output"].height = 100.0

    bounding_box_1.nodes["Bounding Box"].width  = 140.0
    bounding_box_1.nodes["Bounding Box"].height = 100.0

    # Initialize bounding_box_1 links

    # group_input.Geometry -> bounding_box_2.Geometry
    bounding_box_1.links.new(
        bounding_box_1.nodes["Group Input"].outputs[0],
        bounding_box_1.nodes["Bounding Box"].inputs[0]
    )
    # group_input.Use Radius -> bounding_box_2.Use Radius
    bounding_box_1.links.new(
        bounding_box_1.nodes["Group Input"].outputs[1],
        bounding_box_1.nodes["Bounding Box"].inputs[1]
    )
    # bounding_box_2.Bounding Box -> group_output.Bounding Box
    bounding_box_1.links.new(
        bounding_box_1.nodes["Bounding Box"].outputs[0],
        bounding_box_1.nodes["Group Output"].inputs[0]
    )
    # bounding_box_2.Min -> group_output.Min
    bounding_box_1.links.new(
        bounding_box_1.nodes["Bounding Box"].outputs[1],
        bounding_box_1.nodes["Group Output"].inputs[1]
    )
    # bounding_box_2.Max -> group_output.Max
    bounding_box_1.links.new(
        bounding_box_1.nodes["Bounding Box"].outputs[2],
        bounding_box_1.nodes["Group Output"].inputs[2]
    )

    return bounding_box_1



# make cutting box matrix
def make_matrix(segments_x, segments_y, segments_z, matrix_base_name, organ_sample):
    print ("make_matrix")

    #bpy.ops.object.select_pattern(pattern = organ_sample, case_sensitive = True, extend = True)
    #sample_objs = bpy.context.selected_objects   # this is duplicate
    #sample_obj = sample_objs[0]
    
    # make New Collection segmentsBaseName
    segments_collection = bpy.data.collections.new(matrix_base_name)
    bpy.context.scene.collection.children.link(segments_collection)
    bpy.ops.collection.create (name=matrix_base_name)

    # duplicate organ_sample; get pointer
    bpy.ops.object.add_named(linked = False, name = organ_sample)
    objs = bpy.context.selected_objects   # this is duplicate
    obj = objs[0]  
    bb_obj = obj

    # rename organ_samplex
    obj.name = organ_sample+'x'  # rename for sequence

    # move LUL_2 to segments_collection
    # add/link object to collection
    defaultCollection = bpy.context.scene.collection  # scene collection
    defaultCollection.objects.unlink(obj)   # must unlink from root collection first
    segments_collection.objects.link(obj) 

    # apply trans/rot to organ_samplex
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)

    # add boundingBox modifier to LUL_2 ======
    node_tree_names : dict[typing.Callable, str] = {}

    bounding_box = bounding_box_1_node_group(node_tree_names)
    node_tree_names[bounding_box_1_node_group] = bounding_box.name

    # APPLY TO CURRENT OBJECT
    obj = bpy.context.object
    mod = obj.modifiers.new('Bounding Box', 'NODES')
    mod.node_group = bounding_box
    #=======================

    # apply boundingBox modifier
    bpy.ops.object.modifier_apply(modifier='Bounding Box', report=False, merge_customdata=True, single_user=False, all_keyframes=False, use_selected_objects=False)
    
    # object origin to center of geometry
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

    #======obj here is bounding-box
    print (bb_obj.name)
    print (bb_obj.location)
    print (bb_obj.dimensions)

    # ==== offset calculation to put box at correct start corner ==> (dimension − (dimension / segments)) / 2

    # calculate offset for first block, aligned looking from top in Blender
    # X -- from TOP to BOTTOM; -Y
    # current_x + (length-of-bb - length-of-segment/2)
    new_locx = bb_obj.location[0] + ((bb_obj.dimensions[0] - (bb_obj.dimensions[0]/segments_x)) / 2)

    # Y -- from RIGHT to LEFT; -X
    # current_y + (length-of-bb - length-of-segment/2)
    new_locy = bb_obj.location[1] + ((bb_obj.dimensions[1] - (bb_obj.dimensions[1]/segments_y)) / 2)

    # Z -- UP; +Z
    # current_z - length-of-bb - length-of-segment/2
    new_locz = bb_obj.location[2] - ((bb_obj.dimensions[2] - (bb_obj.dimensions[2]/segments_z)) / 2)

    # scale/dimension matrix segments = x/segments_x, y/segments_y ==============
    obj.scale = mathutils.Vector((1/segments_x ,1/segments_y, 1/segments_z)) 
    
    obj.location[0] = new_locx
    obj.location[1] = new_locy
    obj.location[2] = new_locz

       
    # add ARRAY modifier (segments_x, xoffset)
    array_modifier = obj.modifiers.new(name='matrix_x', type='ARRAY')
    array_modifier.count = segments_x
    array_modifier.relative_offset_displace = mathutils.Vector((-1,0,0))

    # add ARRAY modifier (segments_y, yoffset)
    array_modifier = obj.modifiers.new(name='matrix_y', type='ARRAY')
    array_modifier.count = segments_y
    array_modifier.relative_offset_displace = mathutils.Vector((0,-1,0))

    # add ARRAY modifier (segments_z, zoffset)
    array_modifier = obj.modifiers.new(name='matrix_z', type='ARRAY')
    array_modifier.count = segments_z
    array_modifier.relative_offset_displace = mathutils.Vector((0,0,1))

    # apply ARRAY modifier(s) in order
    bpy.ops.object.modifier_apply(modifier='matrix_x', report=False, merge_customdata=True, single_user=False, all_keyframes=False, use_selected_objects=False)
    bpy.ops.object.modifier_apply(modifier='matrix_y', report=False, merge_customdata=True, single_user=False, all_keyframes=False, use_selected_objects=False)
    bpy.ops.object.modifier_apply(modifier='matrix_z', report=False, merge_customdata=True, single_user=False, all_keyframes=False, use_selected_objects=False)

    # <P> => separate=>by loose parts; should have segments_y number of segment_matrix
    #bpy.ops.mesh.separate(type='LOOSE')
    obj.name = sample_id+"-box"
    


#-----------code starts here

# check if matrix already exists - don't run twice

# make the segment_matrix collection if it doesn't exist
coll = bpy.data.collections.get(matrix_base_name )
if coll is None:
    make_matrix(segments_x, segments_y, segments_z, matrix_base_name, organ_sample)
else:
    print(matrix_base_name + " exists already.")

######### this is manual labor ===========
# add NurbsPath (deformer), Deform_Axis=X
# the box will relocate
# make sure it fits sample, use transform along X axis to align with sample
# apply Modifier ==> the modifier will be cloned to each block. Memory?

# run part2 ++++++++++++++
print("adjust shape using deformer then run part2")
