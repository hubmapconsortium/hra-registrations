# Lung Segmentation
rev. 2026-3-19

## Requirements:
- Blender 4.5.2<br>
- Visual Sudio Code (or other coding editor)
- Blender Development extension for Code
- Python Language Support extension for Code

Files, expected in the same folder (Lungs):
- **lung_segmentation exp.blend** => seeded Blender file with STL files and alignment images of all lobes
- **3d_array_part1.py** => Python script which creates the segmentation matrix, step 1
- **3d_array_part2.py** => Python script which uses the segmentation matrix to create block cuts from the organ sample, step 2
- **config_file.txt** => both 3d_array scripts read this file; it contains the name of the organ sample, model #, and count of segments along x,y,z axis
- **RUI_blocks.csv** => comma delimited text file containing specific block-IDs to be produced

VH Organs & parts, stl versions of VHF/VHM lung lobes
- VHF_RUL.stl
- VHF_RML.stl
- VHF_RLL.stl
- VHF_LUL.stl
- VHF_LLL.stl
- VHM_RUL.stl
- VHM_RML.stl
- VHM_RLL.stl
- VHM_LUL.stl
- VHM_LLL.stl

***

## Blender start file (lung_segmentation exp.blend)

<p align="center">
  <img src="images/1 blender outliner default.png" height="500">
</p>

The **Scene Collection** contains three further collections:
- **VHF stl imports** => STL organ imports used as sample organs and two prototype curve deformers
- **Male** => all needed assets to produce male segmentations
- **Female** => ditto for female

Contents of **Male Collection**:
- Five further collections, one for each lobe (VHM-RUL-organ, VHM-RML-organ, etc)

Contents of **VHM-RUL-organ** collection:
- **VHM-RUL-bg_image** => background image of real organ at center of scene, used to align 3d sample
- **VHM-RUL-deformer** => this can be added to an unseparated segment-matrix to conform its shape to the 3d-sample
- **VHM-RUL-original** => copy of the respective lobe from **VHF stl imports** collection
- **VHM-RUL-reference** => copy of VHM-RUL-original, recentered to facilitate alignment
- **VHM-RUL-sample** => copy of VHM-RUL-original, aligned to reference object and then used to make segments

***

## Alignment Procedure

The following steps have already been performed on all assets and are included here for reference.

**Male VHM-RUL lobe sample** is used here.

- Open **lung_segmentation exp.blend** in Blender
- In Outliner locate collection named **VHM-RUL-organ**
- Make collection and contents visible
- Collection contains: 
    1. **VHM-RUL-bg_image** => alignment image
    2. **VHM-RUL-deformer** => to be used on segmentation-matrix to conform to organ obect
    3. **VHM-RUL-original** => lobe 3d object from VH repo
    4. **VHM-RUL-reference** => recentered organ object for easier alignment
    5. **VHM-RUL-sample** => the 3d object used for segmentation

<p align="center">
  <img src="images/2 VHM-RUL after STL import.png" height="500">
</p>

Original 3d object appears at the location/rotation from RUI.

<p align="center">
  <img src="images/3 VHM-RUL import location.png" height="500">
</p>

### Alignment Objective:

The original imported 3d model, **VHM-RUL-original**, appears at its default location and rotation from the RUI. Visually that puts it a little left of the center and a good deal above the plane, even though the location and rotation in the transform inspector shows '0' for all axis. The resulting block array has to be delivered to the same location. We can use the transform and roation tools in Blender to move the 3d mesh around in the scene; this is reflected in updated location & rotation values in the transform inspector. To return the 3d mesh to its original position all location and rotation axis are reset to '0'.

For the segmentation to work as accurately as possible, the 3D mesh must be aligned with the reference image, **VHM-RUL-bg_image**. Depending on the sample in the image and the matching 3D mesh, this can take some effort to rotate and move the 3D mesh so that it has the same orientation as the image. In our process the original 3D mesh, **VHM-RUL-original**, is duplicated and renamed **VHM-RUL-reference**. The original 3D mesh stays un-altered and can be hidden. Now the origin of the duplicate is moved to the center of the mesh and the object is moved to the center of the scene. The mesh of the reference object, **VHM-RUL-reference**, is now centered to the scene origin (it is much easier to manipulate its location and rotation if the origin is inside the mesh). Now we use location & rotation tools to get a good visual alignment.

Once the reference object is aligned with the image, **VHM-RUL-original** is duplicated again. This will be the 3D mesh to be segmented; it is renamed **VHM-RUL-sample**. At the moment it is in the exact same postion as the original but it must be relocated and rotated to match the reference object - without altering its origin. This can be challenging because Blender's transformation & rotation gadgets appear at the origin of the selected object, in our case far outside of the mesh. Looking at the scene in top-down view is a good starting point, but also check from all side views. The sample object should overlap the reference object as good as possible. The first Python script will build a segmentation-matrix based on **VHM-RUL-sample**; the second script will use the segmentation matrix to divide the sample model.

Here the steps again:
- Create duplicate of **VHM-RUL-original** (move inside collection if necessary)
- Rename the copy **VHM-RUL-reference**
- Make sure Blender is in Object Mode
- Make sure **VHM-RUL-reference** is selected, in the Viewport select _Object->Set Origin->Geometry to Origin_

<p align="center">
  <img src="images/4 VHM-RUL after set origin.png" height="500">
</p>

Origin of reference object is now inside the geometry. This makes it easier to rotate and relocate.

- With reference object selected use Move/Rotate functions to match background image (it does not have to be on top of image)
- Start in top view and check from different angles
- Features of the lobe can be better indicators for a match than shape
- Create another duplicate of **VHM-RUL-original** (move to collection if necessary)
- Rename the copy **VHM-RUL-sample**
- DO NOT change center, scale, or 3d cursor!
- Match alignment to reference object. **VHM-RUL-sample** will be used for segmenting
- This alignment process can be challenging because the object origin is far out of the 3d mesh

<p align="center">
  <img src="images/5 VHM-RUL alignment 1.png" height="500">
</p>

<p align="center">
  <img src="images/6 VHM-RUL alignment of sample.png" height="500">
</p>

<p align="center">
  <img src="images/7 VHM-RUL alignment 2.png" height="300">
</p>

***

## Preparations to run the Python scripts

The automatic cutting procedure is done via two Python scripts _3d_array_part1.py_ and _3d_array_part2.py_. Both scripts must be in the same folder as the Blender file and must be properly configured before running. Blender has a built-in text editor and both scripts could be executed from the editor, keeping everything in a single file. To work this way one would open both .py files in the text editor and run from there.

The better option is to run these scripts as external scripts. For this we need a few lines of Python code in the text editor (see further down). In this way the two Python scripts can be edited with any text or programming editor. Here my preference is MS Code with a Blender Development extension and a Python Language extension. Blender Development extension allows to launch Blender from Code. The main advantage of this setup is that the Terminal window in Code now displays any console output produced by the Python code - running Blender solo will not show this output. This can be a valuable tool when problems arise.

### The configuration file _config_file.txt_

Currently the configuration file contains 5 lines of information:
1. Name of the lobe asset => used as a basename for all created objects; must match base name of **VHM-RUL-sample** in Outliner
2. Can be used as a secondary identifier; in this case Model 1,2,3
3. Number of "blocks" => corresponds to segments along the X axis, from right to left
4. Number of "slices" => corresponds to segments along the Y axis, from top to bottom
5. Number of "strips" => cooresponds tp segments along the Z axis, increasing along the z

        VHM-RUL  
        Model2  
        8  
        16  
        4

For several additional configuration options in both Python code files see below.

***

## Running Python script _3d_array_part1.py_

Before running _3d_array_part1.py_ make sure all products from potential earlier runs are removed as this could lead to naming conflicts. Especially the part2 script can create many hundreds of blocks, which, if not removed, could lead to slower performance. Move the desired sample object **VHM-RUL-sample** into the main Scene Collection, so the script can find it.

The part1 script will add a new collection by the name of **Segment_Matrix-VHM-RUL**. It then duplicates the sample object into the new collection, normalizes the object's location & rotation (so the mesh is at the object's origin and all axis are at '0' rotation). It then applies a bounding box modifier and segments the bounding box into the requested xyz matrix; 8, 16, 4 in the example.

Step-by-step:
- Move **VHM-RUL-sample** to Scene Collection (root collection) and make sure it is visible
- DO NOT change the name, the Python script will search for **VHM-RUL-sample**
- To avoid visual confusion, you can hide the **VHM-RUL-organ** collection and its contents
- Open Blender's internal text editor (switch to scripting or open a new window)
- Select script "array-part1" and run it

This creates a new collection of cutting segments called **Segment_Matrix-VHM-RUL**. The image shows the 8x16x4 grid matrix with the organ sample inside. In that collection we now find a single object, **VHM-RUL-box**.

<p align="center">
    <img src="images/8 VHM-RUL Segment Matrix.png" height="400">
    <img src="images/9 VHM-RUL Segment Matrix outliner.png" height="400">
</p>


## Manual conforming of segment-matrix to organ contour

Ultimately the blocks created in this whole process should map as good as possible to an actual organic sample, segmented by a researcher on a cutting board. In Blender's 3D environment we use organ models from the HubMap repository. The models appear as they are in a human body. Organic samples such as **VHM-RUL-bg_image** have a reduced thickness (z axis) and are cut laying flat on a board. Looking at the **VHM-RUL-box** from the side, we see that **VHM-RUL-organ** is not laying flat on the ground plane but has a very pronounced arc along the Y axis. 

<p align="center">
  <img src="images/10 VHM-RUL segmentation side view straight.png" height="300">
</p>

Looking at the center left-to-right line of the matrix, we can see that it is not at all aligning with the center line through the 3D object. If we use this straight matrix, many of the resulting blocks on the left will intersect with the wrong part of the 3D organ, or not intersect at all. To imitate reality, we might deform the 3D organ so that it lays flat on the surface, make the cut and then remove the deform before inserting it back into the RUI. An easier method is used here: Leave the 3D organ as is and bend the matrix.

Step-by-step:
- Add a curve deformer modifier to **VHM-RUL-box** and use **VHM-RUL-deformer** as the curve object

<p align="center">
  <img src="images/11 VHM-RUL segment matrix deformed 1.png" height="350">
  <img src="images/12 VHM-RUL segment matrix deformed 2.png" height="350">
</p>

- Due to the effect of the deformation curve, the matrix slides to the left; use the green arrow on the transform gadget and drag the matrix so it fully covers the 3D organ

<p align="center">
  <img src="images/13 VHM-RUL segment matrix deformed 3.png" height="400">
</p>

- Check alignment from top and other side views to make sure the matrix fully encloses the 3D organ
- When satisfied, apply curve modifier


## Running Python script _3d_array_part2.py_

We should now have a collection called **Segment_Matrix-VHM-RUL** with one object, **VHM-RUL-box**, in it. **VHM-RUL-box** is a segmented and deformed mesh all in a single object. To use it for block making it will be separated into individual, discrete objects.

Running _3d_array_part2.py_ will check if **Segment_Matrix-VHM-RUL** is present. If it is not separated it will separate it into individual block objects. Once the matrix has been separated, run _3d_array_part2.py_ again to commence with the organ block production. This can be a lengthy process, depending on the amount of blocks requested (the example here took about 5 minutes). This creates a new collection called **VHM-RUL**

A small suite of optional postprocessing operations is available (see further down). The produced block-array can now be exported as .fbx file.

Step-by-step
- In Blender's text editor select the script "array-part2" and run it
- Switch to MS Code's debug console to monitor the process
- The script checks the matrix object for separation. The example was not yet separated and shows this console output:

<p align="center">
  <img src="images/15 VHM-RUL console output.png" height="400">
</p>

- After running the script we get a separated matrix in Outliner:
<p align="center">
  <img src="images/14 VHM-RUL separated matrix.png" height="400">
</p>

- Run "array-part2" again to run actual block creation - this can take several minutes depending on number of assets and settings

<p align="center">
  <img src="images/16 VHM-RUL console output.png" height="700">
</p>

- A new collection called **VHM-RUL** is created in Outliner and shown in the 3D viewport at the **VHM-RUL-original** location

<p align="center">
  <img src="images/17 VHM-RUL blocks in outliner.png" height="700">
</p>
<p align="center">
  <img src="images/18 VHM-RUL segmented organ.png" height="500">
</p>

Depending on flag settings in the source code the following postprocessing operations are applied

***

## Automatic postprocessing

The following flags control further automatic processing of the created block array. Hopefully in a future update they can be moved to the configuration file. Note that both part1 & part2 scripts contain this code block but only part2 makes use of them.

### delete_empties
Running the segmentation process will create a boolean object from the intersection of each matrix block with a section of the 3D sample organ. Depending on where in the segment matrix this boolean intersection happens there may be many, few or no vertices in the box. Blocks with no vertex will be invisible in the viewport.

        delete_empties = True   # deletes any blocks with 0 vertices
        delete_empties = False  # all blocks are kept


### delete_unselected
Experiomental feature. part2 script reads a CSV file ("RUI_blocks.csv").
<p align="center">
  <img src="images/19 RUI Blocks CSV.png" height="500">
</p>
If the sample ID in the current run matches entries in the CSV file, all matching blocks are considered 'selected'.

        delete_unselected = True    # delete unselected blocks
        delete_unselected = False   # all blocks are kept


### hide_unselected
Experimental feature. This can hide any unselected blocks.

        hide_unselected = True      # hide, but don't delete unselected
        hide_unselected = False     # all blocks shown


### export_fbx
Automatically export ONLY the block array collection **VHM-RUL** as .fbx file. The example product would be exported as _VHM-RUL-Model2.fbx_ into the root folder of the projct ("Lung").

        export_fbx= True        # export FBX file after done
        export_fbx= False       # skip export

### name_debugging
Can be used for troubleshooting. Will rename created blocks using sequential numbers rather than sector coordinates.

        name_debugging = True  # sequence number, name, X,Y,Z (all numbers)
        name_debugging = False # default: name, X<chr>, Y<int>, Z<chr>


### natural_order
Forces the block coordinates into Gloria's scheme


        natural_order = True    # X<chr>, Y<int>, Z<chr>
        natural_order = False   # Y/slice(int), Z/strip(char), X/block(int) = Gloria's order


### add_materials
The material application algorithm cycles througb all materials avalailable in the scene, applying them in sequence to consecutive blocks.


        add_materials = True    # apply materials (colors) for better visual distinction, materials need to be in file!
        add_materials = False   # no materials applied

***

## Manual export of created block collection for RUI
Preferred graphics file format for RUI is GLB. Blender cannot export selected objects to GLB format. So we create FBX first.
- select collection **VHM-RUL**
- File->Export->FBX, Active Collection, Mesh only
- Save current scene
- New Blender scene (delete camera & light)
- Import FBX file
- export as GLB

***

## Notes
If you run the script trying to create an already existing asset group, the script will abort!

***

## Segmentation info header detail:
### segments_x,y,z (INT)
	full width, length, thickness divided by respective segmentation
	in Blender viewport, looking from TOP x=left/right, y=up/down, z=away/towards camera
	to make segments of (approx.) defined size: width=18, for 1cm segments make 18 segments

### segments_base_name (STRING)
	used as name stem for all created assets

### delete_empties (T/F)
	if TRUE will remove all empty segments (segments with no geometry)

### name_debugging
	produces segment names according to certain rules
	if FALSE name = segments_base_name + x(char) + Y(int) + Z(char)
	if TRUE name = <production seq.#> + segments_base_name + x,y,z(int)

### add_materials
	TRUE = applies available materials in a loop

### two collections, created from segments_base_name
    matrix_base_name = 'Segment_Matrix' + "-" + segments_base_name	
    organ_sample = segments_base_name + "-sample"

## Improvements

### use Blender UI to configure and run
Instead of updating information in the Python script and running it manually a Blender Addon could be created and linked to a UI panel.

### pause segmenting process to manually reshape cutting matrix
This could be helpful when only a specific part of the sample object is to be segmented.

***

## 2-array-part1 script

        import os
        import bpy

        # use to run external scripts
        # 2022/12/27

        #/Volumes/Venus/Earth/Projects/SICE/2021/HubMap/Millitome/hra-millitome-generator/OpenScad Code/V13/Python Pipeline/Python scripts
        filename = os.path.join(os.path.dirname(bpy.data.filepath), "3d_array_part1.py")
        exec(compile(open(filename).read(), filename, 'exec'))

***

## 3-array-part2 script

        import os
        import bpy

        # use to run external scripts
        # 2022/12/27

        #/Volumes/Venus/Earth/Projects/SICE/2021/HubMap/Millitome/hra-millitome-generator/OpenScad Code/V13/Python Pipeline/Python scripts
        filename = os.path.join(os.path.dirname(bpy.data.filepath), "3d_array_part1.py")
        exec(compile(open(filename).read(), filename, 'exec'))


***

## full 3d_array_part1.py script

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

***

## full 3d_array_part2.py script

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




