# workflow to produce cutting matrix segment_matrix
# 2026-3-12

# run after 3d_array_part1.py
# requires fully arrayed box, separated OR non-separated

# TODO:
# better tracking of what state the process is in
# - do we have a separated matrix?
# - do we have existing blocks?
# - would be good not to have to resort to checking the scene
# - make a cleaning script to remove collections?
# - check if collections exist BEFORE trying to create new ones?
#
# V0.92
# -part2 allows repeated creation of blocks 
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

export_fbx = True              # export FBX file after done

name_debugging = False  # True: sequence#, name, X,Y,Z all numbers; False: name, X<chr), Y<int>, Z<chr>
natural_order = False   # True: X<chr), Y<int>, Z<chr>; False: Y(int), Z(char), X(int) = Gloria's order
add_materials = True    # True: apply materials (colors) for better visual distinction, materials need to be in file!

#----------read data from csv file-------------------
csv_folder = Path("")                       # placeholder - not used right now
csv_file = "RUI_blocks.csv"                 # this should come from config file
csv_file_path = os.path.join(csv_folder/csv_file)
print ('reading csv file: ' + csv_file_path)

segments_base_name = sample_id

block_list_array = []   # build block array here

block_type = " delete_empties"   # block type is used for file name extensions on export
if delete_unselected:
    block_type = " delete unselected"

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


    
    
##================
# duplicate nn number of LUL_0 into segments
def organsMake(c):
    print ("organsMake")
    
    for copy in range(c):
        # duplicate selected object
        bpy.ops.object.add_named(linked = False, name = organ_sample)

        # get currently selected object
        newObjs = bpy.context.selected_objects   # this is duplicate
        newObj = newObjs[0]  
        print(newObj.name)
        defaultCollection.objects.unlink(newObj) 
        segments.objects.link(newObj) 
    

# add and apply segments of cutting box matrix
def organsCut(d):
# this is list of objects in segments
    print ("organsCut")
    
    cx = 1  # counters start at 1
    cy = 1
    cz = 1
    c = 1
    
    organs = bpy.data.collections[segments_base_name].objects  # collection of organs

    for thisSegment in range(d):
        thisCutter = segment_matrix[thisSegment]    # for naming cutting blocks extend here
        thisSlice = organs[thisSegment]
        # print(str(thisSegment) + ", " + thisCutter.name + ", " + thisSlice.name)    # iteration
        #print(thisCutter.name)
        #print(thisSlice.name)
      
        bool1 = thisSlice.modifiers.new(type="BOOLEAN", name="bool_intersect")
        bool1.operation = 'INTERSECT'
        bool1.object = thisCutter
        bool1.use_hole_tolerant = True
        bool1.use_self = True
        
        bpy.context.view_layer.objects.active = thisSlice
        bpy.ops.object.modifier_apply(modifier="bool_intersect", report=False, merge_customdata=True, single_user=False, all_keyframes=False, use_selected_objects=False)

        mesh = thisSlice.to_mesh(preserve_all_data_layers=False, depsgraph=None)
        vcount = len(mesh.vertices)
        #print(str(thisSegment) + ", " + thisCutter.name + ", " + thisSlice.name + ' vertices: ' + str(vcount))    # iteration


        # rename segment
        if name_debugging:
            # format: running order, base_name, X, Y, Z as numbers
            thisSlice.name = str(c) + \
            '-' + segments_base_name + \
            '-' + str(cx) + \
            '-' + str(cy) + \
            '-' + str(cz)
        else:
            if natural_order:
                # format: base_name, X (char), Y (int), Z (char)
                thisSlice.name = segments_base_name + \
                    '-' + chr(cx + 64) + \
                    str(cy) + \
                    chr(cz + 64)
            else:
                # format: base_name, Y (int), Z (char), X (int))
                original_name = thisSlice.name
                thisSlice.name = segments_base_name + \
                '-' + str(cy) + \
                chr(cz + 64) + \
                 str(cx)
                
                thisCutter.name = thisCutter.name + \
                '-' + str(cy) + \
                chr(cz + 64) + \
                 str(cx)
                print('name mapping:' + original_name + ' ==> ' + thisSlice.name + ' ==> ' + thisCutter.name + ' vertices: ' + str(vcount))

        #print (thisSlice.location)
        #print (thisSlice.rotation_euler)
        thisSlice.location = mathutils.Vector((0,0,0))          # reset location
        thisSlice.rotation_euler = mathutils.Vector((0,0,0))    # reset rotation

        # evaluate section IDs
        if cx == segments_x:
            cx = 1          
            if cy == segments_y:
                cy = 1              
                if cz == segments_z:
                    cz = 1
                else:
                    cz += 1                    
            else:
                cy += 1
        else:
            cx += 1      
            
        c += 1                      
##================


## remove all segments that contain no mesh/vertices
def deleteEmpties():
    print("deleteEmpties")
    organs = bpy.data.collections[segments_base_name].objects  # collection of organs
    segment_count = len(organs)
    print("full segment set: " + str(segment_count)) 

    for o in bpy.data.collections[segments_base_name].objects:
        mesh = o.to_mesh(preserve_all_data_layers=False, depsgraph=None)
        vcount = len(mesh.vertices)

        # if segment has no vetices => delete
        if vcount == 0:
            bpy.data.objects.remove(o)

    organs = bpy.data.collections[segments_base_name].objects  # collection of organs
    segment_count = len(organs)
    print("cleaned segment set: " + str(segment_count)) 


# remove all segments not in block_list_array
def deleteUnselected():
    print("deleteUnselected")

    organs = bpy.data.collections[segments_base_name].objects  # collection of organs
    segment_count = len(organs)
    print("full segment set: " + str(segment_count)) 

    for o in bpy.data.collections[segments_base_name].objects:

        found = False
        for block in block_list_array:
            #print("current block: " + block)
            #print("segments_base_name: " + o.name)
            if (block == o.name):
                found = True
                break

        if not(found):
            bpy.data.objects.remove(o)

    organs = bpy.data.collections[segments_base_name].objects  # collection of organs
    segment_count = len(organs)
    print("cleaned segment set: " + str(segment_count)) 



# hide all segments not in block_list_array (from CSV sheet)
def hideUnselected():
    print("hideUnselected")

    organs = bpy.data.collections[segments_base_name].objects  # collection of organs
    segment_count = len(organs)
    print("full segment set: " + str(segment_count)) 

    for o in bpy.data.collections[segments_base_name].objects:

        found = False
        for block in block_list_array:
            #print("current block: " + block)
            #print("segments_base_name: " + o.name)
            if (block == o.name):
                found = True
                break

        if not(found):
                o.hide_set(True)

    organs = bpy.data.collections[segments_base_name].objects  # collection of organs
    segment_count = len(organs)
    print("cleaned segment set: " + str(segment_count)) 



## apply materials
def addMaterials():
    print("addMaterials")
    organs = bpy.data.collections[segments_base_name].objects  # collection of organs
    #segment_count = len(organs)

    # init materials
    number_of_materials = len(bpy.data.materials)
    running_m = 0

    for o in bpy.data.collections[segments_base_name].objects:
        # add material
        mat = bpy.data.materials[running_m]
        o.data.materials.append(mat)

        running_m += 1
        if (running_m == number_of_materials):
            running_m = 0


## save as FBX
def exportFBX():
    export_col_name = sample_id

    col = bpy.data.collections.get(export_col_name) # redundant?
    if col != None:
        print("exporting FBX")
        bpy.context.view_layer.active_layer_collection = bpy.data.scenes['Scene'].view_layers['ViewLayer'].layer_collection.children[col.name]

        bpy.ops.export_scene.fbx(
            filepath=sample_id + '-' + model_string + '.fbx', 
            check_existing=True, 
            filter_glob='*.fbx', 
            use_active_collection=True,
            collection='',
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            use_space_transform=True,
            object_types={'MESH'},
            use_mesh_modifiers=True,
            use_mesh_modifiers_render=True,
            mesh_smooth_type='OFF',
            colors_type='SRGB',
            path_mode='AUTO',
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=True,
            axis_forward='-Z',
            axis_up='Y')

    print(sample_id + " was successfully exported")

#-----------code starts here

# make the segment_matrix collection
#make_matrix(segments_x, segments_y, segments_z, matrix_base_name, organ_sample)
#======the cutting matrix is done

# run this part2 AFTER success with part1 #########

box_name = sample_id + '-box'                       # name of unseparated matrix box
collection_name = "Segment_Matrix-" + sample_id     # name of segment_matrix collection

# check if matrix collection exists (it was produced in part1)
col = bpy.data.collections.get(collection_name)
if col != None:
    print("Matrix collection exists. Checking for separation.")

    # check if unseparated matrix box is present
    obj = bpy.data.objects.get(box_name)
    if obj != None:
        print("Unseparated matrix box exists. Running separation.")
        # here we have collection with unseparated matrix ==> run separation then proceed
        bpy.ops.object.select_pattern(pattern = box_name, case_sensitive = True, extend = True)

        box_objs = bpy.context.selected_objects
        box_obj = box_objs[0]
        box_obj.name = sample_id + '-block'     # need to rename segment so it's not found on repeat run
        # <P> => separate=>by loose parts; should have segments_y number of segment_matrix
        bpy.ops.mesh.separate(type='LOOSE')
        print("Matrix separated. Run part2 script again for block creation.")
    else:
        print("Separated matrix exists. Creating sample blocks.")
        # here we should have the collection AND a separated matrix box ==> ready for block generation

        # obtain collections and number of items to process
        segment_matrix = bpy.data.collections[matrix_base_name].objects     # collection of segment_matrix
        segments_total = len(segment_matrix)                               # count objects in collection

        ## create new collection = segments_base_name, for LUL-0 segments
        segments = bpy.data.collections.new(segments_base_name)
        bpy.context.scene.collection.children.link(segments)
        bpy.ops.collection.create (name = segments_base_name)

        ## this is root collection
        defaultCollection = bpy.context.scene.collection

        bpy.ops.object.select_pattern(pattern = organ_sample, case_sensitive = True, extend = True)
        objs = bpy.context.selected_objects   # this is duplicate
        obj = objs[0]  # this is object to duplicate


        #=== make the organ segments
        organsMake(segments_total)
        organsCut(segments_total)

        ## post processing/cleanup
        # delete all blocks NOT in the CSV file
        if delete_unselected:
            deleteUnselected()

        # hide all blocks not in CSV file
        if hide_unselected:
            hideUnselected()

        # delete all blocks w/o vertices/empty
        if delete_empties:
            deleteEmpties()

        if add_materials:
            addMaterials()

        if export_fbx:
            exportFBX()

        print("Sample was segmented.")

else:
    print("Matrix collection does not exist. Did you run part1 script?")




