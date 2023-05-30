import sys
import toolutils

outputitem = None
inputindex = -1
inputitem = None
outputindex = -1

num_args = 1
h_extra_args = ''
pane = toolutils.activePane(kwargs)
if not isinstance(pane, hou.NetworkEditor):
    pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    if pane is None:
       hou.ui.displayMessage(
               'Cannot create node: cannot find any network pane')
       sys.exit(0)
else: # We're creating this tool from the TAB menu inside a network editor
    pane_node = pane.pwd()
    if "outputnodename" in kwargs and "inputindex" in kwargs:
        outputitem = pane_node.item(kwargs["outputnodename"])
        inputindex = kwargs["inputindex"]
        h_extra_args += 'set arg4 = "' + kwargs["outputnodename"] + '"\n'
        h_extra_args += 'set arg5 = "' + str(inputindex) + '"\n'
        num_args = 6
    if "inputnodename" in kwargs and "outputindex" in kwargs:
        inputitem = pane_node.item(kwargs["inputnodename"])
        outputindex = kwargs["outputindex"]
        h_extra_args += 'set arg6 = "' + kwargs["inputnodename"] + '"\n'
        h_extra_args += 'set arg9 = "' + str(outputindex) + '"\n'
        num_args = 9
    if "autoplace" in kwargs:
        autoplace = kwargs["autoplace"]
    else:
        autoplace = False
    # If shift-clicked we want to auto append to the current
    # node
    if "shiftclick" in kwargs and kwargs["shiftclick"]:
        if inputitem is None:
            inputitem = pane.currentNode()
            outputindex = 0
    if "nodepositionx" in kwargs and             "nodepositiony" in kwargs:
        try:
            pos = [ float( kwargs["nodepositionx"] ),
                    float( kwargs["nodepositiony"] )]
        except:
            pos = None
    else:
        pos = None

    if not autoplace and not pane.listMode():
        if pos is not None:
            pass
        elif outputitem is None:
            pos = pane.selectPosition(inputitem, outputindex, None, -1)
        else:
            pos = pane.selectPosition(inputitem, outputindex,
                                      outputitem, inputindex)

    if pos is not None:
        if "node_bbox" in kwargs:
            size = kwargs["node_bbox"]
            pos[0] -= size[0] / 2
            pos[1] -= size[1] / 2
        else:
            pos[0] -= 0.573625
            pos[1] -= 0.220625
        h_extra_args += 'set arg2 = "' + str(pos[0]) + '"\n'
        h_extra_args += 'set arg3 = "' + str(pos[1]) + '"\n'
h_extra_args += 'set argc = "' + str(num_args) + '"\n'

pane_node = pane.pwd()
child_type = pane_node.childTypeCategory().nodeTypes()

if 'subnet' not in child_type:
   hou.ui.displayMessage(
           'Cannot create node: incompatible pane network type')
   sys.exit(0)

# First clear the node selection
pane_node.setSelected(False, True)

h_path = pane_node.path()
h_preamble = 'set arg1 = "' + h_path + '"\n'
h_cmd = r'''
if ($argc < 2 || "$arg2" == "") then
   set arg2 = 0
endif
if ($argc < 3 || "$arg3" == "") then
   set arg3 = 0
endif
# Automatically generated script
# $arg1 - the path to add this node
# $arg2 - x position of the tile
# $arg3 - y position of the tile
# $arg4 - input node to wire to
# $arg5 - which input to wire to
# $arg6 - output node to wire to
# $arg7 - the type of this node
# $arg8 - the node is an indirect input
# $arg9 - index of output from $arg6

\set noalias = 1
set saved_path = `execute("oppwf")`
opcf $arg1

# Node $_obj_geo1_MMF_Remesh_Anim (Sop/subnet)
set _obj_geo1_MMF_Remesh_Anim = `run("opadd -e -n -v subnet MMF_Remesh_Anim")`
oplocate -x `$arg2 + 0` -y `$arg3 + 0` $_obj_geo1_MMF_Remesh_Anim
opspareds '    parm {         name    "label1"         baseparm         label   "Input #1 Label"         invisible         export  all     }     parm {         name    "label2"         baseparm         label   "Input #2 Label"         invisible         export  all     }     parm {         name    "label3"         baseparm         label   "Input #3 Label"         invisible         export  all     }     parm {         name    "label4"         baseparm         label   "Input #4 Label"         invisible         export  all     }     group {         name    "samplegeo"         label   "Sample Geo"          groupsimple {             name    "folder1"             label   "Rest Attributes"              parm {                 name    "restattrex"                 label   "Existing Rest Attribute"                 type    toggle                 default { "1" }                 help    "Turn on this checkbox in case that you have an existing rest attribute. If you don\'t have it, the tool will create it based on an explicit frame."                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "referencerestframe"                 label   "Reference Rest Frame"                 type    integer                 default { "$FSTART" }                 help    "This is the reference rest frame. As a recommendation, use a frame where the mesh is not intersecting itself."                 hidewhen "{ restattrex == 1 }"                 range   { 0 10 }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "restatt"                 label   "Rest Attribute"                 type    string                 default { "_rest" }                 help    "This is the rest attribute that you stored before this tool."                 hidewhen "{ restattrex == 0 }"                 parmtag { "script_callback_language" "python" }             }         }          groupsimple {             name    "piece"             label   "Piece Attributes"              parm {                 name    "remeshtype"                 label   "Remesh Type"                 type    oplist                 default { "" }                 help    "Those are the different setups ready to remesh your geometry. The fastest one is the \'Remesh by piece\', but you can try other systems in order to check how fast and how they look."                 menu {                     "0" "Remesh by piece"                     "1" "Remesh by UVs"                     "2" "Remesh by separated objects"                     "3" "Remesh by custom attrib"                 }                 parmtag { "oprelative" "/" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "uvattr"                 label   "UV Attribute"                 type    string                 default { "uv" }                 help    "This is the uv attribute that you stored before this tool."                 hidewhen "{ remeshtype != 1 }"                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "bucketsize"                 label   "Bucket Size"                 type    integer                 default { "2048" }                 help    "The bucket size represents the amount of points we are going to group to get a sigle patch. That means that if the mesh is bigger and has more polygons, the amount of patches is going to be higher."                 hidewhen "{ remeshtype != 0 }"                 range   { 0 10 }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "bucketvis"                 label   "Bucket Visualization"                 type    toggle                 default { "0" }                 help    "That is the perfect toggle to visualize the patches that you are generating."                 hidewhen "{ remeshtype != 0 }"                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "pieceatt"                 label   "Piece Attribute"                 type    string                 default { "name" }                 help    "This is the name attribute that you stored before this tool."                 hidewhen "{ remeshtype != 3 }"                 parmtag { "script_callback_language" "python" }             }         }          groupsimple {             name    "folder2"             label   "Matching Parms"              parm {                 name    "maxdist"                 label   "Max Distance"                 type    float                 default { "1" }                 help    "This is the amount of distance that the remeshed point is going to search in order to match the referenced animation. If your mesh is big, you could consider putting higher values to get a better deformation."                 range   { 0 10 }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "maxpts"                 label   "Max Points"                 type    integer                 default { "30" }                 help    "This is the amount of points that the remeshed point is going to search in order to match the referenced animation. You could consider putting higher values to get a smoother deformation."                 range   { 0 10 }                 parmtag { "script_callback_language" "python" }             }         }          groupsimple {             name    "folder3"             label   "Output settings"              parm {                 name    "recompuv"                 label   "Recompute UVs"                 type    toggle                 default { "0" }                 help    "This toggle is used in order to compute the UVs. Note that the mesh will change due to the kept seams."                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "checkuvs"                 label   "Check UVs"                 type    toggle                 default { "0" }                 help    "This is a quick checker to see if the UVs are working."                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "recompn"                 label   "Recompute Normals"                 type    toggle                 default { "0" }                 help    "If you would like to recompute the normals on the points, turn on this toggle."                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "dosinglepass"                 label   "Do Single Pass"                 type    toggle                 default { "0" }                 help    "This is a toggle that allows the user to set a concrete patch to see how is calculated. This is just a visualization option."                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "singlepass"                 label   "Single Pass"                 type    integer                 default { "0" }                 help    "You can choose the piece that you want to check by tweaking this parameter."                 disablewhen "{ dosinglepass == 0 }"                 range   { 0 10 }                 parmtag { "script_callback_language" "python" }             }             groupsimple {                 name    "deletegrps"                 label   "Remove Groups"                  multiparm {                     name    "deletions"                     label    "Number of Deletions"                     default 1                     parmtag { "autoscope" "0000000000000000" }                      parm {                         name    "enable#"                         label   "Enable"                         type    toggle                         nolabel                         joinnext                         default { "1" }                     }                     parm {                         name    "grouptype#"                         label   "Group Type"                         type    ordinal                         default { "0" }                         help    "If set to any, all group types whose name match the pattern will be removed. Otherwise, it only removes those groups of the same type as this field."                         disablewhen "{ enable# == 0 }"                         menu {                             "any"       "Any"                             "points"    "Points"                             "prims"     "Primitives"                             "edges"     "Edges"                             "vertices"  "Vertices"                         }                     }                     parm {                         name    "group#"                         label   "Group Names"                         type    string                         default { "" }                         help    "A space separated list of the groups to remove. * can be used as a wild card to match many groups at once."                         disablewhen "{ enable# == 0 }"                     }                 }                  parm {                     name    "removegrp"                     label   "Delete Unused Groups"                     type    toggle                     default { "off" }                     help    "Remove any groups that are empty."                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "script_callback_language" "python" }                 }             }              groupsimple {                 name    "delattr"                 label   "Remove Attributes"                  parm {                     name    "negate"                     label   "Delete Non Selected"                     type    toggle                     default { "off" }                     help    "When enabled, only the specified attributes are kept; otherwise, only the specified atributes are deleted."                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "script_callback_language" "python" }                 }                 parm {                     name    "doptdel"                     label   "Point Attributes"                     type    toggle                     nolabel                     joinnext                     default { "on" }                     help    "Specify existing point attributes to delete."                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "script_callback_language" "python" }                 }                 parm {                     name    "ptdel"                     label   "Point Attributes"                     type    string                     default { "" }                     help    "Specify existing point attributes to delete."                     disablewhen "{ doptdel == 0 }"                     menutoggle {                         [ "opmenu -l -a clean_attrs ptdel" ]                     }                     range   { 0 1 }                     parmtag { "autoscope" "0000000000000000" }                 }                 parm {                     name    "dovtxdel"                     label   "Vertex Attributes"                     type    toggle                     nolabel                     joinnext                     default { "on" }                     help    "Specify existing vertex attributes to delete."                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "script_callback_language" "python" }                 }                 parm {                     name    "vtxdel"                     label   "Vertex Attributes"                     type    string                     default { "" }                     help    "Specify existing vertex attributes to delete."                     disablewhen "{ dovtxdel == 0 }"                     menutoggle {                         [ "opmenu -l -a clean_attrs vtxdel" ]                     }                     range   { 0 1 }                     parmtag { "autoscope" "0000000000000000" }                 }                 parm {                     name    "doprimdel"                     label   "Primitive Attributes"                     type    toggle                     nolabel                     joinnext                     default { "on" }                     help    "Specify existing prim attributes to delete."                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "script_callback_language" "python" }                 }                 parm {                     name    "primdel"                     label   "Primitive Attributes"                     type    string                     default { "" }                     help    "Specify existing prim attributes to delete."                     disablewhen "{ doprimdel == 0 }"                     menutoggle {                         [ "opmenu -l -a clean_attrs primdel" ]                     }                     range   { 0 1 }                     parmtag { "autoscope" "0000000000000000" }                 }                 parm {                     name    "dodtldel"                     label   "Detail Attributes"                     type    toggle                     nolabel                     joinnext                     default { "on" }                     help    "Specify existing detail attributes to delete."                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "script_callback_language" "python" }                 }                 parm {                     name    "dtldel"                     label   "Detail Attributes"                     type    string                     default { "" }                     help    "Specify existing detail attributes to delete."                     disablewhen "{ dodtldel == 0 }"                     menutoggle {                         [ "opmenu -l -a clean_attrs dtldel" ]                     }                     range   { 0 1 }                     parmtag { "autoscope" "0000000000000000" }                 }             }          }      }      group {         name    "samplegeo_1"         label   "Remesh"          parm {             name    "group"             label   "Group"             type    string             default { "" }             menutoggle {                 [ "opmenu -l -a remesh1 group" ]             }             parmtag { "autoscope" "0000000000000000" }             parmtag { "script_action" "import soputils\\nkwargs[\'geometrytype\'] = (hou.geometryType.Primitives,)\\nkwargs[\'inputindex\'] = 0\\nsoputils.selectGroupParm(kwargs)" }             parmtag { "script_action_help" "Select geometry from an available viewport.\\nShift-click to turn on Select Groups." }             parmtag { "script_action_icon" "BUTTONS_reselect" }         }         parm {             name    "hard_edges"             label   "Hard Edges Group"             type    string             default { "" }             menutoggle {                 [ "opmenu -l -a remesh1 hard_edges" ]             }             parmtag { "autoscope" "0000000000000000" }             parmtag { "script_action" "import soputils\\nkwargs[\'geometrytype\'] = (hou.geometryType.Primitives,hou.geometryType.Edges,)\\nkwargs[\'inputindex\'] = 0\\nsoputils.selectGroupParm(kwargs)" }             parmtag { "script_action_help" "Select geometry from an available viewport.\\nShift-click to turn on Select Groups." }             parmtag { "script_action_icon" "BUTTONS_reselect" }         }         groupsimple {             name    "meshing"             label   "Meshing"              parm {                 name    "iterations"                 label   "Iterations"                 type    integer                 default { "2" }                 range   { 0! 10 }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "smoothing"                 label   "Smoothing"                 type    float                 default { "0.1" }                 range   { 0! 1 }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "inputptsonly"                 label   "Use Input Points Only"                 type    toggle                 default { "off" }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "detachfromnongroup"                 label   "Detach From Non-Group Geometry"                 type    toggle                 default { "off" }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "recomputenormals"                 label   "Recompute Normals"                 type    toggle                 default { "on" }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }         }          groupsimple {             name    "sizinggroup"             label   "Element Sizing"              parm {                 name    "sizing"                 label   "Edge Lengths"                 type    ordinal                 default { "uniform" }                 menu {                     "uniform"   "Uniform"                     "adaptive"  "Adaptive"                 }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "targetsize"                 label   "Target Size"                 type    float                 default { "0.2" }                 hidewhen "{ sizing == adaptive }"                 range   { 0! 1 }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "usemaxsize"                 label   "usemaxsize"                 type    toggle                 nolabel                 joinnext                 default { "off" }                 hidewhen "{ sizing == uniform }"                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "maxsize"                 label   "Max Size"                 type    float                 default { "0.1" }                 disablewhen "{ usemaxsize == 0 }"                 hidewhen "{ sizing == uniform }"                 range   { 0! 1 }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "useminsize"                 label   "useminsize"                 type    toggle                 nolabel                 joinnext                 default { "off" }                 hidewhen "{ sizing == uniform }"                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "minsize"                 label   "Min Size"                 type    float                 default { "0.1" }                 disablewhen "{ useminsize == 0 }"                 hidewhen "{ sizing == uniform }"                 range   { 0! 1 }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "density"                 label   "Relative Density"                 type    float                 default { "2" }                 hidewhen "{ sizing == uniform }"                 range   { 1! 10 }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "gradation"                 label   "Gradation"                 type    float                 default { "0.25" }                 hidewhen "{ sizing == uniform }"                 range   { 0! 1! }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             groupcollapsible {                 name    "sizingattribs"                 label   "Control Attributes"                 hidewhen "{ sizing == uniform }"                  parm {                     name    "usemeshsizeattrib"                     label   "usemeshsizeattrib"                     type    toggle                     nolabel                     joinnext                     default { "off" }                     hidewhen "{ sizing == uniform }"                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "script_callback_language" "python" }                 }                 parm {                     name    "meshsizeattrib"                     label   "Mesh Size Attribute"                     type    string                     default { "targetmeshsize" }                     disablewhen "{ usemeshsizeattrib == 0 }"                     hidewhen "{ sizing == uniform }"                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "sidefx::attrib_access" "readwrite" }                 }                 parm {                     name    "useminsizeattrib"                     label   "useminsizeattrib"                     type    toggle                     nolabel                     joinnext                     default { "off" }                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "script_callback_language" "python" }                 }                 parm {                     name    "minsizeattrib"                     label   "Min Size Attribute"                     type    string                     default { "minmeshsize" }                     disablewhen "{ useminsizeattrib == 0 }"                     hidewhen "{ sizing == uniform }"                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "sidefx::attrib_access" "readwrite" }                 }                 parm {                     name    "usemaxsizeattrib"                     label   "usemaxsizeattrib"                     type    toggle                     nolabel                     joinnext                     default { "off" }                     hidewhen "{ sizing == uniform }"                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "script_callback_language" "python" }                 }                 parm {                     name    "maxsizeattrib"                     label   "Max Size Attribute"                     type    string                     default { "maxmeshsize" }                     disablewhen "{ usemaxsizeattrib == 0 }"                     hidewhen "{ sizing == uniform }"                     parmtag { "autoscope" "0000000000000000" }                     parmtag { "sidefx::attrib_access" "readwrite" }                 }             }          }          groupsimple {             name    "outputattribs"             label   "Output Groups and Attributes"              parm {                 name    "useoutmeshsizeattrib"                 label   "useoutmeshsizeattrib"                 type    toggle                 nolabel                 joinnext                 default { "off" }                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "script_callback_language" "python" }             }             parm {                 name    "outmeshsizeattrib"                 label   "Mesh Size Attribute"                 type    string                 default { "meshsize" }                 disablewhen "{ useoutmeshsizeattrib == 0 }"                 parmtag { "autoscope" "0000000000000000" }                 parmtag { "sidefx::attrib_access" "readwrite" }             }         }      }  ' $_obj_geo1_MMF_Remesh_Anim
opparm $_obj_geo1_MMF_Remesh_Anim  deletions ( 1 )
chblockbegin
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim referencerestframe
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$FSTART' $_obj_geo1_MMF_Remesh_Anim/referencerestframe
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim singlepass ( 51 )
opcolor -c 0.97600001096725464 0.77999997138977051 0.2630000114440918 $_obj_geo1_MMF_Remesh_Anim
opset -d on -r on -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim
opuserdata -n 'wirestyle' -v 'rounded' $_obj_geo1_MMF_Remesh_Anim
opcf $_obj_geo1_MMF_Remesh_Anim

# Network Box $_obj_geo1_MMF_Remesh_Anim___netbox1
set _obj_geo1_MMF_Remesh_Anim___netbox1 = `run("nbadd -v __netbox1")`
nblocate -x `$arg2 + -7.09307` -y  `$arg3 + -0.938439` $_obj_geo1_MMF_Remesh_Anim___netbox1
nbsize -w 5.62966 -h 14.4879 $_obj_geo1_MMF_Remesh_Anim___netbox1
nbset  -m off $_obj_geo1_MMF_Remesh_Anim___netbox1
nbcolor -c 0.71 0.518 0.004 $_obj_geo1_MMF_Remesh_Anim___netbox1

# Network Box $_obj_geo1_MMF_Remesh_Anim___netbox2
set _obj_geo1_MMF_Remesh_Anim___netbox2 = `run("nbadd -v __netbox2")`
nblocate -x `$arg2 + -1.01079` -y  `$arg3 + -21.6024` $_obj_geo1_MMF_Remesh_Anim___netbox2
nbsize -w 7.02002 -h 18.7346 $_obj_geo1_MMF_Remesh_Anim___netbox2
nbset  -m off $_obj_geo1_MMF_Remesh_Anim___netbox2
nbcolor -c 0.71 0.518 0.004 $_obj_geo1_MMF_Remesh_Anim___netbox2

# Network Box $_obj_geo1_MMF_Remesh_Anim___netbox3
set _obj_geo1_MMF_Remesh_Anim___netbox3 = `run("nbadd -v __netbox3")`
nblocate -x `$arg2 + -1.01079` -y  `$arg3 + -34.794` $_obj_geo1_MMF_Remesh_Anim___netbox3
nbsize -w 7.02002 -h 12.7463 $_obj_geo1_MMF_Remesh_Anim___netbox3
nbset  -m off $_obj_geo1_MMF_Remesh_Anim___netbox3
nbcolor -c 0.71 0.518 0.004 $_obj_geo1_MMF_Remesh_Anim___netbox3

# Node $_obj_geo1_MMF_Remesh_Anim_set_rest_attr (Sop/attribwrangle)
set _obj_geo1_MMF_Remesh_Anim_set_rest_attr = `run("opadd -e -n -v attribwrangle set_rest_attr")`
oplocate -x `$arg2 + -1.34162` -y `$arg3 + 15.0623` $_obj_geo1_MMF_Remesh_Anim_set_rest_attr
opparm $_obj_geo1_MMF_Remesh_Anim_set_rest_attr  bindings ( 0 ) groupbindings ( 0 )
opparm $_obj_geo1_MMF_Remesh_Anim_set_rest_attr snippet ( 'v@rest = point(1, \'P\', @ptnum);' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_set_rest_attr
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_set_rest_attr
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_set_rest_attr
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_set_rest_attr
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_set_rest_attr

# Node $_obj_geo1_MMF_Remesh_Anim_rename (Sop/attribwrangle)
set _obj_geo1_MMF_Remesh_Anim_rename = `run("opadd -e -n -v attribwrangle rename")`
oplocate -x `$arg2 + 1.50238` -y `$arg3 + 15.0623` $_obj_geo1_MMF_Remesh_Anim_rename
opspareds '    group {         name    "folder1"         label   "Code"          parm {             name    "group"             baseparm             label   "Group"             export  none             bindselector points "Modify Points"                 "Select the points to affect and press Enter to complete."                 0 1 0xffffffff 0 grouptype 0         }         parm {             name    "grouptype"             baseparm             label   "Group Type"             export  none         }         parm {             name    "class"             baseparm             label   "Run Over"             export  none         }         parm {             name    "vex_numcount"             baseparm             label   "Number Count"             export  none         }         parm {             name    "vex_threadjobsize"             baseparm             label   "Thread Job Size"             export  none         }         parm {             name    "snippet"             baseparm             label   "VEXpression"             export  all         }         parm {             name    "exportlist"             baseparm             label   "Attributes to Create"             export  none         }         parm {             name    "vex_strict"             baseparm             label   "Enforce Prototypes"             export  none         }     }      group {         name    "folder1_1"         label   "Bindings"          parm {             name    "autobind"             baseparm             label   "Autobind by Name"             export  none         }         multiparm {             name    "bindings"             label    "Number of Bindings"             baseparm             default 0             parmtag { "autoscope" "0000000000000000" }             parmtag { "multistartoffset" "1" }              parm {                 name    "bindname#"                 baseparm                 label   "Attribute Name"                 export  none             }             parm {                 name    "bindparm#"                 baseparm                 label   "VEX Parameter"                 export  none             }         }          parm {             name    "groupautobind"             baseparm             label   "Autobind Groups by Name"             export  none         }         multiparm {             name    "groupbindings"             label    "Group Bindings"             baseparm             default 0             parmtag { "autoscope" "0000000000000000" }             parmtag { "multistartoffset" "1" }              parm {                 name    "bindgroupname#"                 baseparm                 label   "Group Name"                 export  none             }             parm {                 name    "bindgroupparm#"                 baseparm                 label   "VEX Parameter"                 export  none             }         }          parm {             name    "vex_cwdpath"             baseparm             label   "Evaluation Node Path"             export  none         }         parm {             name    "vex_outputmask"             baseparm             label   "Export Parameters"             export  none         }         parm {             name    "vex_updatenmls"             baseparm             label   "Update Normals If Displaced"             export  none         }         parm {             name    "vex_matchattrib"             baseparm             label   "Attribute to Match"             export  none         }         parm {             name    "vex_inplace"             baseparm             label   "Compute Results In Place"             export  none         }         parm {             name    "vex_selectiongroup"             baseparm             label   "Output Selection Group"             export  none         }         parm {             name    "vex_precision"             baseparm             label   "VEX Precision"             export  none         }     }      parm {         name    "rest_attr"         label   "Rest Attr"         type    string         default { "" }     } ' $_obj_geo1_MMF_Remesh_Anim_rename
opparm $_obj_geo1_MMF_Remesh_Anim_rename  bindings ( 0 ) groupbindings ( 0 )
opparm $_obj_geo1_MMF_Remesh_Anim_rename snippet ( 'v@rest = point(0, chs(\'rest_attr\'), @ptnum);' ) rest_attr ( '`chs("../restatt")`' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_rename
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_rename
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_rename
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_rename
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_rename

# Node $_obj_geo1_MMF_Remesh_Anim_set_rest_pos (Sop/attribwrangle)
set _obj_geo1_MMF_Remesh_Anim_set_rest_pos = `run("opadd -e -n -v attribwrangle set_rest_pos")`
oplocate -x `$arg2 + 0.1215` -y `$arg3 + -8.4177300000000006` $_obj_geo1_MMF_Remesh_Anim_set_rest_pos
opparm $_obj_geo1_MMF_Remesh_Anim_set_rest_pos  bindings ( 0 ) groupbindings ( 0 )
opparm $_obj_geo1_MMF_Remesh_Anim_set_rest_pos snippet ( 'v@P = v@rest;' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_set_rest_pos
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_set_rest_pos
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_set_rest_pos
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_set_rest_pos
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_set_rest_pos
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_set_rest_pos

# Node $_obj_geo1_MMF_Remesh_Anim_capture (Sop/attribwrangle)
set _obj_geo1_MMF_Remesh_Anim_capture = `run("opadd -e -n -v attribwrangle capture")`
oplocate -x `$arg2 + 0.479215` -y `$arg3 + -13.961` $_obj_geo1_MMF_Remesh_Anim_capture
opspareds '    group {         name    "folder1"         label   "Code"          parm {             name    "group"             baseparm             label   "Group"             export  none             bindselector points "Modify Points"                 "Select the points to affect and press Enter to complete."                 0 1 0xffffffff 0 grouptype 0         }         parm {             name    "grouptype"             baseparm             label   "Group Type"             export  none         }         parm {             name    "class"             baseparm             label   "Run Over"             export  none         }         parm {             name    "vex_numcount"             baseparm             label   "Number Count"             export  none         }         parm {             name    "vex_threadjobsize"             baseparm             label   "Thread Job Size"             export  none         }         parm {             name    "snippet"             baseparm             label   "VEXpression"             export  all         }         parm {             name    "exportlist"             baseparm             label   "Attributes to Create"             export  none         }         parm {             name    "vex_strict"             baseparm             label   "Enforce Prototypes"             export  none         }     }      group {         name    "folder1_1"         label   "Bindings"          parm {             name    "autobind"             baseparm             label   "Autobind by Name"             export  none         }         multiparm {             name    "bindings"             label    "Number of Bindings"             baseparm             default 0             parmtag { "autoscope" "0000000000000000" }             parmtag { "multistartoffset" "1" }              parm {                 name    "bindname#"                 baseparm                 label   "Attribute Name"                 export  none             }             parm {                 name    "bindparm#"                 baseparm                 label   "VEX Parameter"                 export  none             }         }          parm {             name    "groupautobind"             baseparm             label   "Autobind Groups by Name"             export  none         }         multiparm {             name    "groupbindings"             label    "Group Bindings"             baseparm             default 0             parmtag { "autoscope" "0000000000000000" }             parmtag { "multistartoffset" "1" }              parm {                 name    "bindgroupname#"                 baseparm                 label   "Group Name"                 export  none             }             parm {                 name    "bindgroupparm#"                 baseparm                 label   "VEX Parameter"                 export  none             }         }          parm {             name    "vex_cwdpath"             baseparm             label   "Evaluation Node Path"             export  none         }         parm {             name    "vex_outputmask"             baseparm             label   "Export Parameters"             export  none         }         parm {             name    "vex_updatenmls"             baseparm             label   "Update Normals If Displaced"             export  none         }         parm {             name    "vex_matchattrib"             baseparm             label   "Attribute to Match"             export  none         }         parm {             name    "vex_inplace"             baseparm             label   "Compute Results In Place"             export  none         }         parm {             name    "vex_selectiongroup"             baseparm             label   "Output Selection Group"             export  none         }         parm {             name    "vex_precision"             baseparm             label   "VEX Precision"             export  none         }     }      parm {         name    "maxdist"         label   "Maxdist"         type    float         default { "0" }         range   { 0 1 }     }     parm {         name    "maxpts"         label   "Maxpts"         type    integer         default { "0" }         range   { 0 10 }     } ' $_obj_geo1_MMF_Remesh_Anim_capture
opparm $_obj_geo1_MMF_Remesh_Anim_capture  bindings ( 0 ) groupbindings ( 0 )
chblockbegin
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_capture maxdist
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../maxdist")' $_obj_geo1_MMF_Remesh_Anim_capture/maxdist
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_capture maxpts
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../maxpts")' $_obj_geo1_MMF_Remesh_Anim_capture/maxpts
chblockend
opparm $_obj_geo1_MMF_Remesh_Anim_capture snippet ( 'float maxdist = chf(\'maxdist\');\nint maxpts = chi(\'maxpts\');\nint npts[] = nearpoints(1, v@P, maxdist, maxpts);\ni[]@npts = npts;\n\n\n\nfloat weights[];\n\n\n\nforeach(int val; npts){\n    vector npos = point(1, \'P\', val);\n    float ndist = distance(v@P, npos);\n    ndist = fit(ndist, 0, maxdist, 1, 0);\n    push(weights, ndist);\n}\n\n\n\nf[]@weights = weights;' ) maxdist ( maxdist ) maxpts ( maxpts )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_capture
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_capture
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_capture
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_capture
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_capture
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_capture

# Node $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix (Sop/attribwrangle)
set _obj_geo1_MMF_Remesh_Anim_get_offset_matrix = `run("opadd -e -n -v attribwrangle get_offset_matrix")`
oplocate -x `$arg2 + 2.7132999999999998` -y `$arg3 + -13.961` $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix
opparm $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix  bindings ( 0 ) groupbindings ( 0 )
opparm $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix snippet ( '\nvector npos = point(1, \'P\', @ptnum);\nv@offset = npos-v@P;\n\nint npts[] = neighbours(0, @ptnum);\nvector ndir = point(1, \'P\', npts[0]);\nvector tan1 = npos - ndir;\nndir = point(1, \'P\', npts[1]);\nvector tan2 = npos - ndir;\nvector up = cross(tan1, tan2);\n\nmatrix3 xformnew= maketransform(normalize(tan1), normalize(up));\n\nndir = point(0, \'P\', npts[0]);\ntan1 = v@P - ndir;\nndir = point(0, \'P\', npts[1]);\ntan2 = v@P - ndir;\nup = cross(tan1, tan2);\n\nmatrix3 xformold= maketransform(normalize(tan1), normalize(up));\n\nmatrix3 totalxform = invert(xformold)*xformnew;\n\n3@xform = totalxform;\n\n' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix

# Node $_obj_geo1_MMF_Remesh_Anim_set_deform (Sop/attribwrangle)
set _obj_geo1_MMF_Remesh_Anim_set_deform = `run("opadd -e -n -v attribwrangle set_deform")`
oplocate -x `$arg2 + 1.67801` -y `$arg3 + -15.046200000000001` $_obj_geo1_MMF_Remesh_Anim_set_deform
opparm $_obj_geo1_MMF_Remesh_Anim_set_deform  bindings ( 0 ) groupbindings ( 0 )
opparm $_obj_geo1_MMF_Remesh_Anim_set_deform snippet ( 'float weights[] = f[]@weights;\nint npts[] = i[]@npts;\nfloat sumweights = 0;\nvector sumoffsets = {0,0,0};\n\n\n\nint val = 0;\n\n\n\nforeach(int npt; npts){\n    vector opos = point(1, \'P\', npt);\n    matrix3 xform = point(1, \'xform\', npt);\n    vector offset = point(1, \'offset\', npt);\n    \n    vector pos = v@P;\n    pos -= opos;\n    pos *= xform;\n    pos += opos;\n    pos -= v@P;\n    \n    offset += pos;\n    \n    offset *= weights[val];\n    sumweights += weights[val];\n    sumoffsets += offset;\n    val++;\n}\n\n\n\nvector finaloffset = sumoffsets / sumweights;\nv@P += finaloffset;' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_set_deform
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_set_deform
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_set_deform
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_set_deform
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_set_deform
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_set_deform

# Node $_obj_geo1_MMF_Remesh_Anim_set_rest (Sop/timeshift)
set _obj_geo1_MMF_Remesh_Anim_set_rest = `run("opadd -e -n -v timeshift set_rest")`
oplocate -x `$arg2 + -0.5` -y `$arg3 + 16.231100000000001` $_obj_geo1_MMF_Remesh_Anim_set_rest
chblockbegin
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_set_rest frame
chkey -t 0 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../referencerestframe")' $_obj_geo1_MMF_Remesh_Anim_set_rest/frame
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_set_rest time
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$T' $_obj_geo1_MMF_Remesh_Anim_set_rest/time
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_set_rest frange1
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$FSTART' $_obj_geo1_MMF_Remesh_Anim_set_rest/frange1
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_set_rest frange2
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$FEND' $_obj_geo1_MMF_Remesh_Anim_set_rest/frange2
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_set_rest trange1
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$TSTART' $_obj_geo1_MMF_Remesh_Anim_set_rest/trange1
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_set_rest trange2
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$TEND' $_obj_geo1_MMF_Remesh_Anim_set_rest/trange2
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_set_rest frame ( frame )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_set_rest
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_set_rest
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_set_rest
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_set_rest
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_set_rest

# Node $_obj_geo1_MMF_Remesh_Anim_switch_set_rest (Sop/switch)
set _obj_geo1_MMF_Remesh_Anim_switch_set_rest = `run("opadd -e -n -v switch switch_set_rest")`
oplocate -x `$arg2 + 0.091682299999999994` -y `$arg3 + 14.1745` $_obj_geo1_MMF_Remesh_Anim_switch_set_rest
chblockbegin
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_switch_set_rest input
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../restattrex")' $_obj_geo1_MMF_Remesh_Anim_switch_set_rest/input
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_switch_set_rest input ( input )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_switch_set_rest
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_switch_set_rest
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_switch_set_rest
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_switch_set_rest
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_switch_set_rest

# Node $_obj_geo1_MMF_Remesh_Anim_promote_name (Sop/attribpromote)
set _obj_geo1_MMF_Remesh_Anim_promote_name = `run("opadd -e -n -v attribpromote promote_name")`
oplocate -x `$arg2 + 5.3926400000000001` -y `$arg3 + 1.87724` $_obj_geo1_MMF_Remesh_Anim_promote_name
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_promote_name inname ( '`chs("../pieceatt")`' ) outclass ( primitive )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_promote_name
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_promote_name
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_promote_name
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_promote_name
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_promote_name

# Node $_obj_geo1_MMF_Remesh_Anim_set_name (Sop/attribute)
set _obj_geo1_MMF_Remesh_Anim_set_name = `run("opadd -e -n -v attribute set_name")`
oplocate -x `$arg2 + 5.3926400000000001` -y `$arg3 + 0.66990300000000003` $_obj_geo1_MMF_Remesh_Anim_set_name
opparm $_obj_geo1_MMF_Remesh_Anim_set_name  ptrenames ( 0 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 )
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_set_name stdswitcher ( 2 2 2 2 2 ) ptrenames ( 0 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 ) frompr0 ( '`chs("../pieceatt")`' ) topr0 ( name )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_set_name
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_set_name
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_set_name
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_set_name
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_set_name

# Node $_obj_geo1_MMF_Remesh_Anim_create_piece_connectivity (Sop/connectivity)
set _obj_geo1_MMF_Remesh_Anim_create_piece_connectivity = `run("opadd -e -n -v connectivity create_piece_connectivity")`
oplocate -x `$arg2 + 1.7198` -y `$arg3 + 0.66990300000000003` $_obj_geo1_MMF_Remesh_Anim_create_piece_connectivity
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_create_piece_connectivity connecttype ( prim ) attribname ( name ) attribtype ( string ) prefix ( piece_ )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_create_piece_connectivity
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_create_piece_connectivity
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_create_piece_connectivity
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_create_piece_connectivity
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_create_piece_connectivity

# Node $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece (Sop/switch)
set _obj_geo1_MMF_Remesh_Anim_switch_it_base_piece = `run("opadd -e -n -v switch switch_it_base_piece")`
oplocate -x `$arg2 + 0.1245` -y `$arg3 + -1.8395699999999999` $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece input
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../remeshtype")' $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece/input
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece input ( input )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece

# Node $_obj_geo1_MMF_Remesh_Anim_freeze_frame (Sop/timeshift)
set _obj_geo1_MMF_Remesh_Anim_freeze_frame = `run("opadd -e -n -v timeshift freeze_frame")`
oplocate -x `$arg2 + 0.1245` -y `$arg3 + -4.8960299999999997` $_obj_geo1_MMF_Remesh_Anim_freeze_frame
chblockbegin
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_freeze_frame frame
chkey -t 0 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../referencerestframe")' $_obj_geo1_MMF_Remesh_Anim_freeze_frame/frame
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_freeze_frame time
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$T' $_obj_geo1_MMF_Remesh_Anim_freeze_frame/time
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_freeze_frame frange1
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$FSTART' $_obj_geo1_MMF_Remesh_Anim_freeze_frame/frange1
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_freeze_frame frange2
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$FEND' $_obj_geo1_MMF_Remesh_Anim_freeze_frame/frange2
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_freeze_frame trange1
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$TSTART' $_obj_geo1_MMF_Remesh_Anim_freeze_frame/trange1
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_freeze_frame trange2
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F '$TEND' $_obj_geo1_MMF_Remesh_Anim_freeze_frame/trange2
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_freeze_frame frame ( frame )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_freeze_frame
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_freeze_frame
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_freeze_frame
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_freeze_frame
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_freeze_frame
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_freeze_frame

# Node $_obj_geo1_MMF_Remesh_Anim_compile_end (Sop/compile_end)
set _obj_geo1_MMF_Remesh_Anim_compile_end = `run("opadd -e -n -v compile_end compile_end")`
oplocate -x `$arg2 + 1.6826099999999999` -y `$arg3 + -21.363099999999999` $_obj_geo1_MMF_Remesh_Anim_compile_end
opcolor -c 0.75 0.75 0 $_obj_geo1_MMF_Remesh_Anim_compile_end
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_compile_end
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_compile_end
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_compile_end
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_compile_end
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_compile_end
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_compile_end

# Node $_obj_geo1_MMF_Remesh_Anim_compile_freeze (Sop/compile_begin)
set _obj_geo1_MMF_Remesh_Anim_compile_freeze = `run("opadd -e -n -v compile_begin compile_freeze")`
oplocate -x `$arg2 + 0.12609999999999999` -y `$arg3 + -6.1646299999999998` $_obj_geo1_MMF_Remesh_Anim_compile_freeze
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_compile_freeze blockpath ( ../compile_end )
opcolor -c 0.75 0.75 0 $_obj_geo1_MMF_Remesh_Anim_compile_freeze
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_compile_freeze
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_compile_freeze
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_compile_freeze
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_compile_freeze
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_compile_freeze
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_compile_freeze

# Node $_obj_geo1_MMF_Remesh_Anim_compile_anim (Sop/compile_begin)
set _obj_geo1_MMF_Remesh_Anim_compile_anim = `run("opadd -e -n -v compile_begin compile_anim")`
oplocate -x `$arg2 + 3.3637999999999999` -y `$arg3 + -6.1646299999999998` $_obj_geo1_MMF_Remesh_Anim_compile_anim
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_compile_anim blockpath ( ../compile_end )
opcolor -c 0.75 0.75 0 $_obj_geo1_MMF_Remesh_Anim_compile_anim
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_compile_anim
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_compile_anim
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_compile_anim
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_compile_anim
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_compile_anim
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_compile_anim

# Node $_obj_geo1_MMF_Remesh_Anim_out_deform (Sop/block_end)
set _obj_geo1_MMF_Remesh_Anim_out_deform = `run("opadd -e -n -v block_end out_deform")`
oplocate -x `$arg2 + 1.6826099999999999` -y `$arg3 + -16.142700000000001` $_obj_geo1_MMF_Remesh_Anim_out_deform
chblockbegin
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_out_deform dosinglepass
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../dosinglepass")' $_obj_geo1_MMF_Remesh_Anim_out_deform/dosinglepass
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_out_deform singlepass
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../singlepass")' $_obj_geo1_MMF_Remesh_Anim_out_deform/singlepass
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_out_deform itermethod ( pieces ) method ( merge ) class ( primitive ) attrib ( name ) blockpath ( ../in_anim ) templatepath ( ../in_anim ) dosinglepass ( dosinglepass ) singlepass ( singlepass ) multithread ( on )
opcolor -c 0.75 0.40000000596046448 0 $_obj_geo1_MMF_Remesh_Anim_out_deform
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_out_deform
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_out_deform
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_out_deform
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_out_deform
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_out_deform
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_out_deform

# Node $_obj_geo1_MMF_Remesh_Anim_in_anim (Sop/block_begin)
set _obj_geo1_MMF_Remesh_Anim_in_anim = `run("opadd -e -n -v block_begin in_anim")`
oplocate -x `$arg2 + 3.3637999999999999` -y `$arg3 + -7.2503299999999999` $_obj_geo1_MMF_Remesh_Anim_in_anim
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_in_anim method ( piece ) blockpath ( ../out_deform )
opcolor -c 0.75 0.40000000596046448 0 $_obj_geo1_MMF_Remesh_Anim_in_anim
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_in_anim
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_in_anim
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_in_anim
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_in_anim
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_in_anim
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_in_anim

# Node $_obj_geo1_MMF_Remesh_Anim_in_freeze (Sop/block_begin)
set _obj_geo1_MMF_Remesh_Anim_in_freeze = `run("opadd -e -n -v block_begin in_freeze")`
oplocate -x `$arg2 + 0.12609999999999999` -y `$arg3 + -7.2503299999999999` $_obj_geo1_MMF_Remesh_Anim_in_freeze
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_in_freeze method ( piece ) blockpath ( ../out_deform )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_in_freeze
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_in_freeze
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_in_freeze
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_in_freeze
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_in_freeze
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_in_freeze

# Node $_obj_geo1_MMF_Remesh_Anim_remesh (Sop/remesh::2.0)
set _obj_geo1_MMF_Remesh_Anim_remesh = `run("opadd -e -n -v remesh::2.0 remesh")`
oplocate -x `$arg2 + -0.61078500000000002` -y `$arg3 + -11.7043` $_obj_geo1_MMF_Remesh_Anim_remesh
chblockbegin
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh group
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../group")' $_obj_geo1_MMF_Remesh_Anim_remesh/group
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh hard_edges
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../hard_edges")' $_obj_geo1_MMF_Remesh_Anim_remesh/hard_edges
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh iterations
chkey -t 0 -v 2 -m 0 -a 0 -A 0 -T a  -F 'ch("../iterations")' $_obj_geo1_MMF_Remesh_Anim_remesh/iterations
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh smoothing
chkey -t 0 -v 0.10000000000000001 -m 0 -a 0 -A 0 -T a  -F 'ch("../smoothing")' $_obj_geo1_MMF_Remesh_Anim_remesh/smoothing
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh inputptsonly
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../inputptsonly")' $_obj_geo1_MMF_Remesh_Anim_remesh/inputptsonly
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh detachfromnongroup
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../detachfromnongroup")' $_obj_geo1_MMF_Remesh_Anim_remesh/detachfromnongroup
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh recomputenormals
chkey -t 0 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../recomputenormals")' $_obj_geo1_MMF_Remesh_Anim_remesh/recomputenormals
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh sizing
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../sizing")' $_obj_geo1_MMF_Remesh_Anim_remesh/sizing
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh targetsize
chkey -t 0 -v 0.20000000000000001 -m 0 -a 0 -A 0 -T a  -F 'ch("../targetsize")' $_obj_geo1_MMF_Remesh_Anim_remesh/targetsize
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh usemaxsize
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../usemaxsize")' $_obj_geo1_MMF_Remesh_Anim_remesh/usemaxsize
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh maxsize
chkey -t 0 -v 0.10000000000000001 -m 0 -a 0 -A 0 -T a  -F 'ch("../maxsize")' $_obj_geo1_MMF_Remesh_Anim_remesh/maxsize
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh useminsize
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../useminsize")' $_obj_geo1_MMF_Remesh_Anim_remesh/useminsize
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh minsize
chkey -t 0 -v 0.10000000000000001 -m 0 -a 0 -A 0 -T a  -F 'ch("../minsize")' $_obj_geo1_MMF_Remesh_Anim_remesh/minsize
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh density
chkey -t 0 -v 2 -m 0 -a 0 -A 0 -T a  -F 'ch("../density")' $_obj_geo1_MMF_Remesh_Anim_remesh/density
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh gradation
chkey -t 0 -v 0.25 -m 0 -a 0 -A 0 -T a  -F 'ch("../gradation")' $_obj_geo1_MMF_Remesh_Anim_remesh/gradation
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh usemeshsizeattrib
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../usemeshsizeattrib")' $_obj_geo1_MMF_Remesh_Anim_remesh/usemeshsizeattrib
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh meshsizeattrib
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../meshsizeattrib")' $_obj_geo1_MMF_Remesh_Anim_remesh/meshsizeattrib
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh useminsizeattrib
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../useminsizeattrib")' $_obj_geo1_MMF_Remesh_Anim_remesh/useminsizeattrib
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh minsizeattrib
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../minsizeattrib")' $_obj_geo1_MMF_Remesh_Anim_remesh/minsizeattrib
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh usemaxsizeattrib
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../usemaxsizeattrib")' $_obj_geo1_MMF_Remesh_Anim_remesh/usemaxsizeattrib
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh maxsizeattrib
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../maxsizeattrib")' $_obj_geo1_MMF_Remesh_Anim_remesh/maxsizeattrib
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh useoutmeshsizeattrib
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../useoutmeshsizeattrib")' $_obj_geo1_MMF_Remesh_Anim_remesh/useoutmeshsizeattrib
chadd -t 0 0 $_obj_geo1_MMF_Remesh_Anim_remesh outmeshsizeattrib
chkey -t 0 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../outmeshsizeattrib")' $_obj_geo1_MMF_Remesh_Anim_remesh/outmeshsizeattrib
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_remesh group ( group ) hard_edges ( hard_edges ) iterations ( iterations ) smoothing ( smoothing ) inputptsonly ( inputptsonly ) detachfromnongroup ( detachfromnongroup ) recomputenormals ( recomputenormals ) sizing ( sizing ) targetsize ( targetsize ) usemaxsize ( usemaxsize ) maxsize ( maxsize ) useminsize ( useminsize ) minsize ( minsize ) density ( density ) gradation ( gradation ) usemeshsizeattrib ( usemeshsizeattrib ) meshsizeattrib ( meshsizeattrib ) useminsizeattrib ( useminsizeattrib ) minsizeattrib ( minsizeattrib ) usemaxsizeattrib ( usemaxsizeattrib ) maxsizeattrib ( maxsizeattrib ) useoutmeshsizeattrib ( useoutmeshsizeattrib ) outmeshsizeattrib ( outmeshsizeattrib )
opset -d on -r on -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_remesh
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_remesh
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_remesh
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_remesh
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_remesh
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_remesh

# Node $_obj_geo1_MMF_Remesh_Anim_REMESH (Sop/null)
set _obj_geo1_MMF_Remesh_Anim_REMESH = `run("opadd -e -n -v null REMESH")`
oplocate -x `$arg2 + -0.60578500000000002` -y `$arg3 + -12.8462` $_obj_geo1_MMF_Remesh_Anim_REMESH
opcolor -c 0 0 0 $_obj_geo1_MMF_Remesh_Anim_REMESH
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_REMESH
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_REMESH
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_REMESH
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_REMESH
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_REMESH
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_REMESH

# Node $_obj_geo1_MMF_Remesh_Anim_STATIC (Sop/null)
set _obj_geo1_MMF_Remesh_Anim_STATIC = `run("opadd -e -n -v null STATIC")`
oplocate -x `$arg2 + 1.4114` -y `$arg3 + -12.8462` $_obj_geo1_MMF_Remesh_Anim_STATIC
opcolor -c 0 0 0 $_obj_geo1_MMF_Remesh_Anim_STATIC
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_STATIC
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_STATIC
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_STATIC
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_STATIC
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_STATIC
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_STATIC

# Node $_obj_geo1_MMF_Remesh_Anim_ANIM (Sop/null)
set _obj_geo1_MMF_Remesh_Anim_ANIM = `run("opadd -e -n -v null ANIM")`
oplocate -x `$arg2 + 3.3672` -y `$arg3 + -12.8462` $_obj_geo1_MMF_Remesh_Anim_ANIM
opcolor -c 0 0 0 $_obj_geo1_MMF_Remesh_Anim_ANIM
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_ANIM
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_ANIM
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_ANIM
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_ANIM
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_ANIM
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_ANIM

# Node $_obj_geo1_MMF_Remesh_Anim_del_unused (Sop/attribdelete)
set _obj_geo1_MMF_Remesh_Anim_del_unused = `run("opadd -e -n -v attribdelete del_unused")`
oplocate -x `$arg2 + 1.6775599999999999` -y `$arg3 + -27.971599999999999` $_obj_geo1_MMF_Remesh_Anim_del_unused
opparm $_obj_geo1_MMF_Remesh_Anim_del_unused ptdel ( 'npts weights rest' ) primdel ( 'nameobj id' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_del_unused
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_del_unused
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_del_unused
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_del_unused
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_del_unused
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_del_unused

# Node $_obj_geo1_MMF_Remesh_Anim_store_prim_id (Sop/attribwrangle)
set _obj_geo1_MMF_Remesh_Anim_store_prim_id = `run("opadd -e -n -v attribwrangle store_prim_id")`
oplocate -x `$arg2 + -6.6688200000000002` -y `$arg3 + 11.752000000000001` $_obj_geo1_MMF_Remesh_Anim_store_prim_id
opparm $_obj_geo1_MMF_Remesh_Anim_store_prim_id  bindings ( 0 ) groupbindings ( 0 )
opparm $_obj_geo1_MMF_Remesh_Anim_store_prim_id class ( primitive ) snippet ( 'i@id = i@primnum;' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_store_prim_id
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_store_prim_id
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_store_prim_id
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_store_prim_id
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_store_prim_id
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_store_prim_id

# Node $_obj_geo1_MMF_Remesh_Anim_create_obj_name (Sop/connectivity)
set _obj_geo1_MMF_Remesh_Anim_create_obj_name = `run("opadd -e -n -v connectivity create_obj_name")`
oplocate -x `$arg2 + -6.6658200000000001` -y `$arg3 + 10.7727` $_obj_geo1_MMF_Remesh_Anim_create_obj_name
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_create_obj_name connecttype ( prim ) attribname ( nameobj ) attribtype ( string ) prefix ( piece_ )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_create_obj_name
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_create_obj_name
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_create_obj_name
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_create_obj_name
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_create_obj_name
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_create_obj_name

# Node $_obj_geo1_MMF_Remesh_Anim_set_to_ref (Sop/timeshift)
set _obj_geo1_MMF_Remesh_Anim_set_to_ref = `run("opadd -e -n -v timeshift set_to_ref")`
oplocate -x `$arg2 + -4.8334999999999999` -y `$arg3 + 9.6158900000000003` $_obj_geo1_MMF_Remesh_Anim_set_to_ref
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_set_to_ref frame
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../referencerestframe")' $_obj_geo1_MMF_Remesh_Anim_set_to_ref/frame
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_set_to_ref time
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F '$T' $_obj_geo1_MMF_Remesh_Anim_set_to_ref/time
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_set_to_ref frange1
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F '$FSTART' $_obj_geo1_MMF_Remesh_Anim_set_to_ref/frange1
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_set_to_ref frange2
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F '$FEND' $_obj_geo1_MMF_Remesh_Anim_set_to_ref/frange2
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_set_to_ref trange1
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F '$TSTART' $_obj_geo1_MMF_Remesh_Anim_set_to_ref/trange1
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_set_to_ref trange2
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F '$TEND' $_obj_geo1_MMF_Remesh_Anim_set_to_ref/trange2
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_set_to_ref frame ( frame )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_set_to_ref
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_set_to_ref
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_set_to_ref
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_set_to_ref
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_set_to_ref
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_set_to_ref

# Node $_obj_geo1_MMF_Remesh_Anim_out_pieces (Sop/block_end)
set _obj_geo1_MMF_Remesh_Anim_out_pieces = `run("opadd -e -n -v block_end out_pieces")`
oplocate -x `$arg2 + -4.8369499999999999` -y `$arg3 + 1.6152500000000001` $_obj_geo1_MMF_Remesh_Anim_out_pieces
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_out_pieces itermethod ( pieces ) method ( merge ) class ( primitive ) attrib ( nameobj ) blockpath ( ../in_named_objs ) templatepath ( ../in_named_objs )
opcolor -c 0.75 0.40000000596046448 0 $_obj_geo1_MMF_Remesh_Anim_out_pieces
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_out_pieces
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_out_pieces
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_out_pieces
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_out_pieces
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_out_pieces
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_out_pieces

# Node $_obj_geo1_MMF_Remesh_Anim_in_named_objs (Sop/block_begin)
set _obj_geo1_MMF_Remesh_Anim_in_named_objs = `run("opadd -e -n -v block_begin in_named_objs")`
oplocate -x `$arg2 + -4.8319000000000001` -y `$arg3 + 8.4188799999999997` $_obj_geo1_MMF_Remesh_Anim_in_named_objs
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_in_named_objs method ( piece ) blockpath ( ../out_pieces )
opcolor -c 0.75 0.40000000596046448 0 $_obj_geo1_MMF_Remesh_Anim_in_named_objs
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_in_named_objs
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_in_named_objs
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_in_named_objs
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_in_named_objs
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_in_named_objs
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_in_named_objs

# Node $_obj_geo1_MMF_Remesh_Anim_get_bucket_size (Sop/attribwrangle)
set _obj_geo1_MMF_Remesh_Anim_get_bucket_size = `run("opadd -e -n -v attribwrangle get_bucket_size")`
oplocate -x `$arg2 + -3.6164100000000001` -y `$arg3 + 7.2747799999999998` $_obj_geo1_MMF_Remesh_Anim_get_bucket_size
opspareds '    group {         name    "folder1"         label   "Code"          parm {             name    "group"             baseparm             label   "Group"             export  none             bindselector points "Modify Points"                 "Select the points to affect and press Enter to complete."                 0 1 0xffffffff 0 grouptype 0         }         parm {             name    "grouptype"             baseparm             label   "Group Type"             export  none         }         parm {             name    "class"             baseparm             label   "Run Over"             export  none         }         parm {             name    "vex_numcount"             baseparm             label   "Number Count"             export  none         }         parm {             name    "vex_threadjobsize"             baseparm             label   "Thread Job Size"             export  none         }         parm {             name    "snippet"             baseparm             label   "VEXpression"             export  all         }         parm {             name    "exportlist"             baseparm             label   "Attributes to Create"             export  none         }         parm {             name    "vex_strict"             baseparm             label   "Enforce Prototypes"             export  none         }     }      group {         name    "folder1_1"         label   "Bindings"          parm {             name    "autobind"             baseparm             label   "Autobind by Name"             export  none         }         multiparm {             name    "bindings"             label    "Number of Bindings"             baseparm             default 0             parmtag { "autoscope" "0000000000000000" }             parmtag { "multistartoffset" "1" }              parm {                 name    "bindname#"                 baseparm                 label   "Attribute Name"                 export  none             }             parm {                 name    "bindparm#"                 baseparm                 label   "VEX Parameter"                 export  none             }         }          parm {             name    "groupautobind"             baseparm             label   "Autobind Groups by Name"             export  none         }         multiparm {             name    "groupbindings"             label    "Group Bindings"             baseparm             default 0             parmtag { "autoscope" "0000000000000000" }             parmtag { "multistartoffset" "1" }              parm {                 name    "bindgroupname#"                 baseparm                 label   "Group Name"                 export  none             }             parm {                 name    "bindgroupparm#"                 baseparm                 label   "VEX Parameter"                 export  none             }         }          parm {             name    "vex_cwdpath"             baseparm             label   "Evaluation Node Path"             export  none         }         parm {             name    "vex_outputmask"             baseparm             label   "Export Parameters"             export  none         }         parm {             name    "vex_updatenmls"             baseparm             label   "Update Normals If Displaced"             export  none         }         parm {             name    "vex_matchattrib"             baseparm             label   "Attribute to Match"             export  none         }         parm {             name    "vex_inplace"             baseparm             label   "Compute Results In Place"             export  none         }         parm {             name    "vex_selectiongroup"             baseparm             label   "Output Selection Group"             export  none         }         parm {             name    "vex_precision"             baseparm             label   "VEX Precision"             export  none         }     }      parm {         name    "bsize"         label   "Bsize"         type    integer         default { "0" }         range   { 0 10 }     } ' $_obj_geo1_MMF_Remesh_Anim_get_bucket_size
opparm $_obj_geo1_MMF_Remesh_Anim_get_bucket_size  bindings ( 0 ) groupbindings ( 0 )
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_get_bucket_size bsize
chkey -t 42.166666666666664 -v 24000 -m 0 -a 0 -A 0 -T a  -F 'ch("../bucketsize")' $_obj_geo1_MMF_Remesh_Anim_get_bucket_size/bsize
chblockend
opparm $_obj_geo1_MMF_Remesh_Anim_get_bucket_size class ( detail ) snippet ( 'int bsize = chi(\'bsize\');\n\ni@npts = max(1, npoints(0) / bsize);' ) bsize ( bsize )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_get_bucket_size
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_get_bucket_size
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_get_bucket_size
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_get_bucket_size
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_get_bucket_size
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_get_bucket_size

# Node $_obj_geo1_MMF_Remesh_Anim_scatter_pts (Sop/scatter::2.0)
set _obj_geo1_MMF_Remesh_Anim_scatter_pts = `run("opadd -e -n -v scatter::2.0 scatter_pts")`
oplocate -x `$arg2 + -3.61341` -y `$arg3 + 5.97912` $_obj_geo1_MMF_Remesh_Anim_scatter_pts
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_scatter_pts npts
chkey -t 42.166666666666664 -v 1000 -m 0 -a 0 -A 0 -T a  -F 'detail(0, \'npts\', 0)' $_obj_geo1_MMF_Remesh_Anim_scatter_pts/npts
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_scatter_pts npts ( npts )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_scatter_pts
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_scatter_pts
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_scatter_pts
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_scatter_pts
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_scatter_pts
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_scatter_pts

# Node $_obj_geo1_MMF_Remesh_Anim_set_subname (Sop/attribwrangle)
set _obj_geo1_MMF_Remesh_Anim_set_subname = `run("opadd -e -n -v attribwrangle set_subname")`
oplocate -x `$arg2 + -3.6164100000000001` -y `$arg3 + 4.7692800000000002` $_obj_geo1_MMF_Remesh_Anim_set_subname
opparm $_obj_geo1_MMF_Remesh_Anim_set_subname  bindings ( 0 ) groupbindings ( 0 )
opparm $_obj_geo1_MMF_Remesh_Anim_set_subname snippet ( 'i@subname = i@ptnum;' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_set_subname
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_set_subname
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_set_subname
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_set_subname
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_set_subname
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_set_subname

# Node $_obj_geo1_MMF_Remesh_Anim_transfer_subname (Sop/attribtransfer)
set _obj_geo1_MMF_Remesh_Anim_transfer_subname = `run("opadd -e -n -v attribtransfer transfer_subname")`
oplocate -x `$arg2 + -4.8369499999999999` -y `$arg3 + 3.87425` $_obj_geo1_MMF_Remesh_Anim_transfer_subname
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_transfer_subname cardswitcher ( 1 1 ) primitiveattribs ( off ) pointattriblist ( subname ) kernel ( uniform ) maxsamplecount ( 3 ) threshold ( off )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_transfer_subname
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_transfer_subname
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_transfer_subname
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_transfer_subname
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_transfer_subname
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_transfer_subname

# Node $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims (Sop/attribpromote)
set _obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims = `run("opadd -e -n -v attribpromote promote_subname_to_prims")`
oplocate -x `$arg2 + -4.8369499999999999` -y `$arg3 + 2.7447499999999998` $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims inname ( subname ) outclass ( primitive ) method ( max )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims

# Node $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces (Sop/attribwrangle)
set _obj_geo1_MMF_Remesh_Anim_concat_name_pieces = `run("opadd -e -n -v attribwrangle concat_name_pieces")`
oplocate -x `$arg2 + -6.6688200000000002` -y `$arg3 + 0.66890300000000003` $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces
opparm $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces  bindings ( 0 ) groupbindings ( 0 )
opparm $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces class ( primitive ) snippet ( 'int match_prim = findattribval(1, \'prim\', \'id\', i@id);\n\ns@name = s@nameobj + \'_\' + itoa(prim(1, \'subname\', match_prim));' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces

# Node $_obj_geo1_MMF_Remesh_Anim_split_uvs (Sop/splitpoints)
set _obj_geo1_MMF_Remesh_Anim_split_uvs = `run("opadd -e -n -v splitpoints split_uvs")`
oplocate -x `$arg2 + 0.1245` -y `$arg3 + -9.6660599999999999` $_obj_geo1_MMF_Remesh_Anim_split_uvs
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_split_uvs useattrib ( on ) attribname ( uv ) tol ( 9.9999999999999995e-07 )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_split_uvs
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_split_uvs
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_split_uvs
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_split_uvs
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_split_uvs
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_split_uvs

# Node $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs (Sop/switchif)
set _obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs = `run("opadd -e -n -v switchif switchif_keep_uvs")`
oplocate -x `$arg2 + -0.61078500000000002` -y `$arg3 + -10.5501` $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs
opparm $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs  tests ( 1 )
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs expr1
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../recompuv")' $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs/expr1
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs expr1 ( expr1 )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs

# Node $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces (Sop/block_end)
set _obj_geo1_MMF_Remesh_Anim_out_fused_pieces = `run("opadd -e -n -v block_end out_fused_pieces")`
oplocate -x `$arg2 + 3.3052600000000001` -y `$arg3 + -19.403300000000002` $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces itermethod ( pieces ) method ( merge ) class ( primitive ) attrib ( nameobj ) blockpath ( ../in_pieces ) templatepath ( ../in_pieces ) multithread ( on )
opcolor -c 0.75 0.40000000596046448 0 $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces

# Node $_obj_geo1_MMF_Remesh_Anim_in_pieces (Sop/block_begin)
set _obj_geo1_MMF_Remesh_Anim_in_pieces = `run("opadd -e -n -v block_begin in_pieces")`
oplocate -x `$arg2 + 3.3052600000000001` -y `$arg3 + -17.2514` $_obj_geo1_MMF_Remesh_Anim_in_pieces
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_in_pieces method ( piece ) blockpath ( ../out_fused_pieces )
opcolor -c 0.75 0.40000000596046448 0 $_obj_geo1_MMF_Remesh_Anim_in_pieces
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_in_pieces
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_in_pieces
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_in_pieces
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_in_pieces
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_in_pieces
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_in_pieces

# Node $_obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1 (Sop/connectivity)
set _obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1 = `run("opadd -e -n -v connectivity create_uv_connectivity1")`
oplocate -x `$arg2 + -1.4421900000000001` -y `$arg3 + 0.66990300000000003` $_obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1 connecttype ( prim ) attribname ( name ) attribtype ( string ) prefix ( piece_ ) byuv ( on ) uvattrib ( '`chs("../uvattr")`' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1

# Node $_obj_geo1_MMF_Remesh_Anim_set_name_obj (Sop/connectivity)
set _obj_geo1_MMF_Remesh_Anim_set_name_obj = `run("opadd -e -n -v connectivity set_name_obj")`
oplocate -x `$arg2 + 0.1245` -y `$arg3 + -3.3678900000000001` $_obj_geo1_MMF_Remesh_Anim_set_name_obj
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_set_name_obj connecttype ( prim ) attribname ( nameobj ) attribtype ( string ) prefix ( piece_ )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_set_name_obj
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_set_name_obj
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_set_name_obj
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_set_name_obj
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_set_name_obj
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_set_name_obj

# Node $_obj_geo1_MMF_Remesh_Anim_fuse (Sop/fuse::2.0)
set _obj_geo1_MMF_Remesh_Anim_fuse = `run("opadd -e -n -v fuse::2.0 fuse")`
oplocate -x `$arg2 + 3.3036599999999998` -y `$arg3 + -18.322800000000001` $_obj_geo1_MMF_Remesh_Anim_fuse
opparm $_obj_geo1_MMF_Remesh_Anim_fuse  numpointattribs ( 0 ) numgroups ( 0 )
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_fuse tol3d ( 0.0001 )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_fuse
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_fuse
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_fuse
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_fuse
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_fuse
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_fuse

# Node $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs (Sop/switchif)
set _obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs = `run("opadd -e -n -v switchif switchif_fuse_for_uvs")`
oplocate -x `$arg2 + 1.6810099999999999` -y `$arg3 + -20.337499999999999` $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs
opparm $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs  tests ( 1 )
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs expr1
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../recompuv")' $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs/expr1
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs expr1 ( expr1 )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs
nbop $_obj_geo1_MMF_Remesh_Anim___netbox2 add $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs

# Node $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE (Sop/null)
set _obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE = `run("opadd -e -n -v null REMESH_BY_PIECE")`
oplocate -x `$arg2 + -6.6608200000000002` -y `$arg3 + -0.60843899999999995` $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE
opcolor -c 0 0 0 $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE

# Node $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS (Sop/null)
set _obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS = `run("opadd -e -n -v null REMESH_BY_UVS")`
oplocate -x `$arg2 + -1.43719` -y `$arg3 + -0.60843899999999995` $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS
opcolor -c 0 0 0 $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS

# Node $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE (Sop/null)
set _obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE = `run("opadd -e -n -v null REMESH_BY_CUSTOM_ATTRIBUTE")`
oplocate -x `$arg2 + 5.4010899999999999` -y `$arg3 + -0.60843899999999995` $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE
opcolor -c 0 0 0 $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE

# Node $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT (Sop/null)
set _obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT = `run("opadd -e -n -v null REMESH_BY_SEPARATED_OBJECT")`
oplocate -x `$arg2 + 1.7248000000000001` -y `$arg3 + -0.60843899999999995` $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT
opcolor -c 0 0 0 $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F off -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT

# Node $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket (Sop/switchif)
set _obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket = `run("opadd -e -n -v switchif switchif_visualize_bucket")`
oplocate -x `$arg2 + 1.6810099999999999` -y `$arg3 + -33.222099999999998` $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket
opparm $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket  tests ( 1 )
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket expr1
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'if((ch("../bucketvis")==1) && (ch("../remeshtype")==0), 0, 1)' $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket/expr1
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket expr1 ( expr1 ) attribowner1 ( detail )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket

# Node $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals (Sop/switchif)
set _obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals = `run("opadd -e -n -v switchif switchif_recompute_normals")`
oplocate -x `$arg2 + 1.6810099999999999` -y `$arg3 + -26.881799999999998` $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals
opparm $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals  tests ( 1 )
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals expr1
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../recompn")' $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals/expr1
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals expr1 ( expr1 )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals

# Node $_obj_geo1_MMF_Remesh_Anim_recompute_normals (Sop/normal)
set _obj_geo1_MMF_Remesh_Anim_recompute_normals = `run("opadd -e -n -v normal recompute_normals")`
oplocate -x `$arg2 + 2.7814700000000001` -y `$arg3 + -25.988099999999999` $_obj_geo1_MMF_Remesh_Anim_recompute_normals
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_recompute_normals type ( typepoint ) origifzero ( off )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_recompute_normals
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_recompute_normals
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_recompute_normals
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_recompute_normals
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_recompute_normals
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_recompute_normals

# Node $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs (Sop/switchif)
set _obj_geo1_MMF_Remesh_Anim_switchif_check_uvs = `run("opadd -e -n -v switchif switchif_check_uvs")`
oplocate -x `$arg2 + 1.6810099999999999` -y `$arg3 + -29.805800000000001` $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs
opparm $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs  tests ( 1 )
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs expr1
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../checkuvs")' $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs/expr1
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs expr1 ( expr1 )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs

# Node $_obj_geo1_MMF_Remesh_Anim_uvquickshade (Sop/uvquickshade)
set _obj_geo1_MMF_Remesh_Anim_uvquickshade = `run("opadd -e -n -v uvquickshade uvquickshade")`
oplocate -x `$arg2 + 2.9182800000000002` -y `$arg3 + -28.957699999999999` $_obj_geo1_MMF_Remesh_Anim_uvquickshade
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_uvquickshade
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_uvquickshade
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_uvquickshade
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_uvquickshade
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_uvquickshade
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_uvquickshade

# Node $_obj_geo1_MMF_Remesh_Anim_clean_grps (Sop/groupdelete)
set _obj_geo1_MMF_Remesh_Anim_clean_grps = `run("opadd -e -n -v groupdelete clean_grps")`
oplocate -x `$arg2 + 1.6810099999999999` -y `$arg3 + -30.875599999999999` $_obj_geo1_MMF_Remesh_Anim_clean_grps
opmultiparm $_obj_geo1_MMF_Remesh_Anim_clean_grps 'enable#' '../enable#' 'grouptype#' '../grouptype#' 'group#' '../group#'
opparm $_obj_geo1_MMF_Remesh_Anim_clean_grps  deletions ( 1 )
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_grps deletions
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../deletions")' $_obj_geo1_MMF_Remesh_Anim_clean_grps/deletions
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_grps removegrp
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../removegrp")' $_obj_geo1_MMF_Remesh_Anim_clean_grps/removegrp
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_grps enable1
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../enable1")' $_obj_geo1_MMF_Remesh_Anim_clean_grps/enable1
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_grps grouptype1
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../grouptype1")' $_obj_geo1_MMF_Remesh_Anim_clean_grps/grouptype1
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_grps group1
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../group1")' $_obj_geo1_MMF_Remesh_Anim_clean_grps/group1
chblockend
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_clean_grps deletions ( deletions ) removegrp ( removegrp ) enable1 ( enable1 ) grouptype1 ( grouptype1 ) group1 ( group1 )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_clean_grps
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_clean_grps
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_clean_grps
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_clean_grps
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_clean_grps
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_clean_grps

# Node $_obj_geo1_MMF_Remesh_Anim_clean_attrs (Sop/attribdelete)
set _obj_geo1_MMF_Remesh_Anim_clean_attrs = `run("opadd -e -n -v attribdelete clean_attrs")`
oplocate -x `$arg2 + 1.6775599999999999` -y `$arg3 + -31.866` $_obj_geo1_MMF_Remesh_Anim_clean_attrs
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_attrs negate
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F 'ch("../negate")' $_obj_geo1_MMF_Remesh_Anim_clean_attrs/negate
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_attrs doptdel
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../doptdel")' $_obj_geo1_MMF_Remesh_Anim_clean_attrs/doptdel
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_attrs ptdel
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../ptdel")' $_obj_geo1_MMF_Remesh_Anim_clean_attrs/ptdel
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_attrs dovtxdel
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../dovtxdel")' $_obj_geo1_MMF_Remesh_Anim_clean_attrs/dovtxdel
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_attrs vtxdel
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../vtxdel")' $_obj_geo1_MMF_Remesh_Anim_clean_attrs/vtxdel
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_attrs doprimdel
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../doprimdel")' $_obj_geo1_MMF_Remesh_Anim_clean_attrs/doprimdel
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_attrs primdel
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../primdel")' $_obj_geo1_MMF_Remesh_Anim_clean_attrs/primdel
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_attrs dodtldel
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'ch("../dodtldel")' $_obj_geo1_MMF_Remesh_Anim_clean_attrs/dodtldel
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_clean_attrs dtldel
chkey -t 42.166666666666664 -v 0 -m 0 -a 0 -A 0 -T a  -F 'chs("../dtldel")' $_obj_geo1_MMF_Remesh_Anim_clean_attrs/dtldel
chblockend
opparm $_obj_geo1_MMF_Remesh_Anim_clean_attrs negate ( negate ) doptdel ( doptdel ) ptdel ( ptdel ) dovtxdel ( dovtxdel ) vtxdel ( vtxdel ) doprimdel ( doprimdel ) primdel ( primdel ) dodtldel ( dodtldel ) dtldel ( dtldel )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_clean_attrs
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_clean_attrs
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_clean_attrs
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_clean_attrs
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_clean_attrs
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_clean_attrs

# Node $_obj_geo1_MMF_Remesh_Anim_rename_name_1 (Sop/attribute)
set _obj_geo1_MMF_Remesh_Anim_rename_name_1 = `run("opadd -e -n -v attribute rename_name_1")`
oplocate -x `$arg2 + -1.44564` -y `$arg3 + 1.87724` $_obj_geo1_MMF_Remesh_Anim_rename_name_1
opparm $_obj_geo1_MMF_Remesh_Anim_rename_name_1  ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 )
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_rename_name_1 ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 ) frompt0 ( name ) topt0 ( _oldname ) frompr0 ( name ) topr0 ( _oldname )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_rename_name_1
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_rename_name_1
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_rename_name_1
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_rename_name_1
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_rename_name_1

# Node $_obj_geo1_MMF_Remesh_Anim_rename_name_2 (Sop/attribute)
set _obj_geo1_MMF_Remesh_Anim_rename_name_2 = `run("opadd -e -n -v attribute rename_name_2")`
oplocate -x `$arg2 + 1.71635` -y `$arg3 + 1.87724` $_obj_geo1_MMF_Remesh_Anim_rename_name_2
opparm $_obj_geo1_MMF_Remesh_Anim_rename_name_2  ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 )
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_rename_name_2 ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 ) frompt0 ( name ) topt0 ( _oldname ) frompr0 ( name ) topr0 ( _oldname )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_rename_name_2
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_rename_name_2
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_rename_name_2
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_rename_name_2
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_rename_name_2

# Node $_obj_geo1_MMF_Remesh_Anim_rename_name_3 (Sop/attribute)
set _obj_geo1_MMF_Remesh_Anim_rename_name_3 = `run("opadd -e -n -v attribute rename_name_3")`
oplocate -x `$arg2 + 6.2436499999999997` -y `$arg3 + 4.5302199999999999` $_obj_geo1_MMF_Remesh_Anim_rename_name_3
opparm $_obj_geo1_MMF_Remesh_Anim_rename_name_3  ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 )
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_rename_name_3 stdswitcher ( 2 2 2 2 2 ) ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 ) updatevar ( off ) encodenames ( on ) frompt0 ( '`chs("../pieceatt")`' ) topt0 ( _oldname ) frompr0 ( '`chs("../pieceatt")`' ) topr0 ( _oldname )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_rename_name_3
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_rename_name_3
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_rename_name_3
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_rename_name_3
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_rename_name_3

# Node $_obj_geo1_MMF_Remesh_Anim_copy_oldname (Sop/attribcopy)
set _obj_geo1_MMF_Remesh_Anim_copy_oldname = `run("opadd -e -n -v attribcopy copy_oldname")`
oplocate -x `$arg2 + 5.3926400000000001` -y `$arg3 + 3.1411799999999999` $_obj_geo1_MMF_Remesh_Anim_copy_oldname
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_copy_oldname attribname ( _oldname )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_copy_oldname
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_copy_oldname
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_copy_oldname
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_copy_oldname
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_copy_oldname

# Node $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1 (Sop/attribute)
set _obj_geo1_MMF_Remesh_Anim_rename_oldname_1 = `run("opadd -e -n -v attribute rename_oldname_1")`
oplocate -x `$arg2 + 1.6775599999999999` -y `$arg3 + -23.906300000000002` $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1
opparm $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1  ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 )
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1 ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 ) frompt0 ( _oldname ) topt0 ( '`chs("../pieceatt")`' ) frompr0 ( _oldname ) topr0 ( '`chs("../pieceatt")`' )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1

# Node $_obj_geo1_MMF_Remesh_Anim_switchif_rename (Sop/switchif)
set _obj_geo1_MMF_Remesh_Anim_switchif_rename = `run("opadd -e -n -v switchif switchif_rename")`
oplocate -x `$arg2 + 1.6810099999999999` -y `$arg3 + -25.043500000000002` $_obj_geo1_MMF_Remesh_Anim_switchif_rename
opparm $_obj_geo1_MMF_Remesh_Anim_switchif_rename  tests ( 1 )
chblockbegin
chadd -t 42.166666666666664 42.166666666666664 $_obj_geo1_MMF_Remesh_Anim_switchif_rename expr1
chkey -t 42.166666666666664 -v 1 -m 0 -a 0 -A 0 -T a  -F 'if((ch("../remeshtype")==3), 0, 1)' $_obj_geo1_MMF_Remesh_Anim_switchif_rename/expr1
chblockend
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_switchif_rename
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_switchif_rename
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_switchif_rename
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_switchif_rename
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_switchif_rename
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_switchif_rename

# Node $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2 (Sop/attribute)
set _obj_geo1_MMF_Remesh_Anim_rename_oldname_2 = `run("opadd -e -n -v attribute rename_oldname_2")`
oplocate -x `$arg2 + 3.8255300000000001` -y `$arg3 + -23.906300000000002` $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2
opparm $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2  ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 )
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2 stdswitcher ( 2 2 2 2 2 ) ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 ) frompt0 ( _oldname ) topt0 ( name ) frompr0 ( _oldname ) topr0 ( name )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2

# Node $_obj_geo1_MMF_Remesh_Anim_del_name_mod (Sop/attribdelete)
set _obj_geo1_MMF_Remesh_Anim_del_name_mod = `run("opadd -e -n -v attribdelete del_name_mod")`
oplocate -x `$arg2 + 1.6775599999999999` -y `$arg3 + -22.730899999999998` $_obj_geo1_MMF_Remesh_Anim_del_name_mod
opparm $_obj_geo1_MMF_Remesh_Anim_del_name_mod primdel ( name )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_del_name_mod
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_del_name_mod
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_del_name_mod
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_del_name_mod
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_del_name_mod
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_del_name_mod

# Node $_obj_geo1_MMF_Remesh_Anim_rename_name_4 (Sop/attribute)
set _obj_geo1_MMF_Remesh_Anim_rename_name_4 = `run("opadd -e -n -v attribute rename_name_4")`
oplocate -x `$arg2 + -6.66927` -y `$arg3 + 12.8392` $_obj_geo1_MMF_Remesh_Anim_rename_name_4
opparm $_obj_geo1_MMF_Remesh_Anim_rename_name_4  ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 )
opparm -V 19.0.383 $_obj_geo1_MMF_Remesh_Anim_rename_name_4 ptrenames ( 1 ) vtxrenames ( 0 ) primrenames ( 1 ) detailrenames ( 0 ) rmanconversions ( 0 ) frompt0 ( name ) topt0 ( _oldname ) frompr0 ( name ) topr0 ( _oldname )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_rename_name_4
nbop $_obj_geo1_MMF_Remesh_Anim___netbox1 add $_obj_geo1_MMF_Remesh_Anim_rename_name_4
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_rename_name_4
opuserdata -n '___Version___' -v '18.5.696' $_obj_geo1_MMF_Remesh_Anim_rename_name_4
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_rename_name_4
opuserdata -n '___toolid___' -v 'remesh' $_obj_geo1_MMF_Remesh_Anim_rename_name_4

# Node $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket (Sop/color)
set _obj_geo1_MMF_Remesh_Anim_color_vis_bucket = `run("opadd -e -n -v color color_vis_bucket")`
oplocate -x `$arg2 + -6.6608200000000002` -y `$arg3 + -31.865950017881392` $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket
opparm $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket  ramp ( 2 )
opparm $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket class ( 1 ) colortype ( 4 ) rampattribute ( name ) ramp2pos ( 1 ) ramp2c ( 1 1 1 )
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket
opuserdata -n '___Version___' -v '' $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket
opuserdata -n '___toolcount___' -v '2' $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket
opuserdata -n '___toolid___' -v 'sop_color' $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket

# Node $_obj_geo1_MMF_Remesh_Anim_output (Sop/output)
set _obj_geo1_MMF_Remesh_Anim_output = `run("opadd -e -n -v output output")`
oplocate -x `$arg2 + 1.6810100093132252` -y `$arg3 + -34.477782866913962` $_obj_geo1_MMF_Remesh_Anim_output
opset -d off -r off -h off -f off -y off -t off -l off -s off -u off -F on -c on -e on -b off $_obj_geo1_MMF_Remesh_Anim_output
nbop $_obj_geo1_MMF_Remesh_Anim___netbox3 add $_obj_geo1_MMF_Remesh_Anim_output
opexprlanguage -s hscript $_obj_geo1_MMF_Remesh_Anim_output

# Sticky Note __stickynote1
python -c 'hou.pwd().createStickyNote("__stickynote1")'
python -c 'hou.pwd().findStickyNote("__stickynote1").setColor(hou.Color((0.71, 0.518, 0.004)))'
python -c 'hou.pwd().findStickyNote("__stickynote1").setText("In this part of the setup we are splitting the geometry into different pieces based on a bucket size. \n\nThe point of doing this is to generate more tasks to perform in the multithreading system when everything is compiled.\n\nThe speed of the setup is based on your machine\'s amount of threads and the pieces that we want to compute. Be aware of the number of pieces that you have because initializing the process takes time. You\'ll need to find a proper bucket size related with your computer setting to enjoy the highest speed performance.")'
python -c 'hou.pwd().findStickyNote("__stickynote1").setTextSize(0)'
python -c 'hou.pwd().findStickyNote("__stickynote1").setTextColor(hou.Color((0, 0, 0)))'
python -c 'hou.pwd().findStickyNote("__stickynote1").setDrawBackground(True)'
python -c 'hou.pwd().findStickyNote("__stickynote1").setPosition(hou.Vector2(-11.923, 8.97656))'
python -c 'hou.pwd().findStickyNote("__stickynote1").setSize(hou.Vector2(4.3346, 4.64792))'
python -c 'hou.pwd().findStickyNote("__stickynote1").setMinimized(False)'

# Sticky Note __stickynote2
python -c 'hou.pwd().createStickyNote("__stickynote2")'
python -c 'hou.pwd().findStickyNote("__stickynote2").setColor(hou.Color((0.976, 0.78, 0.263)))'
python -c 'hou.pwd().findStickyNote("__stickynote2").setText("Due to we need a rest position, I\'m asking to get one form an attribute or, if there isn\'t, the user can choose a frame to do all the computations based on a reference frame.")'
python -c 'hou.pwd().findStickyNote("__stickynote2").setTextSize(0)'
python -c 'hou.pwd().findStickyNote("__stickynote2").setTextColor(hou.Color((0, 0, 0)))'
python -c 'hou.pwd().findStickyNote("__stickynote2").setDrawBackground(True)'
python -c 'hou.pwd().findStickyNote("__stickynote2").setPosition(hou.Vector2(3.98814, 15.0244))'
python -c 'hou.pwd().findStickyNote("__stickynote2").setSize(hou.Vector2(3.18917, 1.95926))'
python -c 'hou.pwd().findStickyNote("__stickynote2").setMinimized(False)'

# Sticky Note __stickynote3
python -c 'hou.pwd().createStickyNote("__stickynote3")'
python -c 'hou.pwd().findStickyNote("__stickynote3").setColor(hou.Color((0.976, 0.78, 0.263)))'
python -c 'hou.pwd().findStickyNote("__stickynote3").setText("The remesh by uvs, separated objects and custom attributes are systems based on connectivity. In some cases, it\'s important to rename the attribute because later we\'ll use the \'name\' in order to iterate.")'
python -c 'hou.pwd().findStickyNote("__stickynote3").setTextSize(0)'
python -c 'hou.pwd().findStickyNote("__stickynote3").setTextColor(hou.Color((0, 0, 0)))'
python -c 'hou.pwd().findStickyNote("__stickynote3").setDrawBackground(True)'
python -c 'hou.pwd().findStickyNote("__stickynote3").setPosition(hou.Vector2(8.64872, 0.0265518))'
python -c 'hou.pwd().findStickyNote("__stickynote3").setSize(hou.Vector2(3.69648, 1.92569))'
python -c 'hou.pwd().findStickyNote("__stickynote3").setMinimized(False)'

# Sticky Note __stickynote4
python -c 'hou.pwd().createStickyNote("__stickynote4")'
python -c 'hou.pwd().findStickyNote("__stickynote4").setColor(hou.Color((0.71, 0.518, 0.004)))'
python -c 'hou.pwd().findStickyNote("__stickynote4").setText("This compiled system allows the user to iterate on each one of the pieces that we selected previously as a \'remesh type\'.\n\nIn order to keep the uvs, I decided to split the the points based on seam edges, so those would be kept in the remesh process. The meshing part is going to be a bit different, but we wil keep the uvs.\n\nThe remesh node is by default super-fast depending on the amount of target size we are applying, but just as a first instance seem to be appropiate for a fast performing set up.\n\nThe capture node get the points and weights from each one of the points based on a maximum point and distance values. The get_offset_matrix gets the matrix and offset that the mesh currently have comparing itself being static and animated. When everything is computed, I decided to set the matrix xform and offset to the new mesh.\n")'
python -c 'hou.pwd().findStickyNote("__stickynote4").setTextSize(0)'
python -c 'hou.pwd().findStickyNote("__stickynote4").setTextColor(hou.Color((0, 0, 0)))'
python -c 'hou.pwd().findStickyNote("__stickynote4").setDrawBackground(True)'
python -c 'hou.pwd().findStickyNote("__stickynote4").setPosition(hou.Vector2(7.04541, -8.07783))'
python -c 'hou.pwd().findStickyNote("__stickynote4").setSize(hou.Vector2(5.99946, 5.28495))'
python -c 'hou.pwd().findStickyNote("__stickynote4").setMinimized(False)'

# Sticky Note __stickynote5
python -c 'hou.pwd().createStickyNote("__stickynote5")'
python -c 'hou.pwd().findStickyNote("__stickynote5").setColor(hou.Color((0.71, 0.518, 0.004)))'
python -c 'hou.pwd().findStickyNote("__stickynote5").setText("I\'m fusing the points just to make sure that we don\'t have the mesh opened iterating based on \'nameobj\'. This is just a clean up part if you are using the uv recompute.")'
python -c 'hou.pwd().findStickyNote("__stickynote5").setTextSize(0)'
python -c 'hou.pwd().findStickyNote("__stickynote5").setTextColor(hou.Color((0, 0, 0)))'
python -c 'hou.pwd().findStickyNote("__stickynote5").setDrawBackground(True)'
python -c 'hou.pwd().findStickyNote("__stickynote5").setPosition(hou.Vector2(7.04541, -18.138))'
python -c 'hou.pwd().findStickyNote("__stickynote5").setSize(hou.Vector2(5.99946, 1.19212))'
python -c 'hou.pwd().findStickyNote("__stickynote5").setMinimized(False)'

# Sticky Note __stickynote6
python -c 'hou.pwd().createStickyNote("__stickynote6")'
python -c 'hou.pwd().findStickyNote("__stickynote6").setColor(hou.Color((0.976, 0.78, 0.263)))'
python -c 'hou.pwd().findStickyNote("__stickynote6").setText("I decided to use a color node to set a random color based on the naming in order to see the amount of pieces that we currently have.")'
python -c 'hou.pwd().findStickyNote("__stickynote6").setTextSize(0)'
python -c 'hou.pwd().findStickyNote("__stickynote6").setTextColor(hou.Color((0, 0, 0)))'
python -c 'hou.pwd().findStickyNote("__stickynote6").setDrawBackground(True)'
python -c 'hou.pwd().findStickyNote("__stickynote6").setPosition(hou.Vector2(-11.518, -33.2221))'
python -c 'hou.pwd().findStickyNote("__stickynote6").setSize(hou.Vector2(3.44123, 1.43115))'
python -c 'hou.pwd().findStickyNote("__stickynote6").setMinimized(False)'
oporder -e set_rest_attr rename set_rest_pos capture get_offset_matrix set_deform set_rest switch_set_rest promote_name set_name create_piece_connectivity switch_it_base_piece freeze_frame compile_end compile_freeze compile_anim out_deform in_anim in_freeze remesh REMESH STATIC ANIM del_unused store_prim_id create_obj_name set_to_ref out_pieces in_named_objs get_bucket_size scatter_pts set_subname transfer_subname promote_subname_to_prims concat_name_pieces split_uvs switchif_keep_uvs out_fused_pieces in_pieces create_uv_connectivity1 set_name_obj fuse switchif_fuse_for_uvs REMESH_BY_PIECE REMESH_BY_UVS REMESH_BY_CUSTOM_ATTRIBUTE REMESH_BY_SEPARATED_OBJECT switchif_visualize_bucket switchif_recompute_normals recompute_normals switchif_check_uvs uvquickshade clean_grps clean_attrs rename_name_1 rename_name_2 rename_name_3 copy_oldname rename_oldname_1 switchif_rename rename_oldname_2 del_name_mod rename_name_4 color_vis_bucket output 
opcf ..
opset -p on $_obj_geo1_MMF_Remesh_Anim

opcf $arg1
opwire -n $_obj_geo1_unpack1 -0 $_obj_geo1_MMF_Remesh_Anim
opcf $_obj_geo1_MMF_Remesh_Anim
opwire -n -i 0 -0 $_obj_geo1_MMF_Remesh_Anim_set_rest_attr
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_rest -1 $_obj_geo1_MMF_Remesh_Anim_set_rest_attr
opwire -n -i 0 -0 $_obj_geo1_MMF_Remesh_Anim_rename
opwire -n $_obj_geo1_MMF_Remesh_Anim_in_freeze -0 $_obj_geo1_MMF_Remesh_Anim_set_rest_pos
opwire -n $_obj_geo1_MMF_Remesh_Anim_REMESH -0 $_obj_geo1_MMF_Remesh_Anim_capture
opwire -n $_obj_geo1_MMF_Remesh_Anim_STATIC -1 $_obj_geo1_MMF_Remesh_Anim_capture
opwire -n $_obj_geo1_MMF_Remesh_Anim_STATIC -0 $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix
opwire -n $_obj_geo1_MMF_Remesh_Anim_ANIM -1 $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix
opwire -n $_obj_geo1_MMF_Remesh_Anim_capture -0 $_obj_geo1_MMF_Remesh_Anim_set_deform
opwire -n $_obj_geo1_MMF_Remesh_Anim_get_offset_matrix -1 $_obj_geo1_MMF_Remesh_Anim_set_deform
opwire -n -i 0 -0 $_obj_geo1_MMF_Remesh_Anim_set_rest
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_rest_attr -0 $_obj_geo1_MMF_Remesh_Anim_switch_set_rest
opwire -n $_obj_geo1_MMF_Remesh_Anim_rename -1 $_obj_geo1_MMF_Remesh_Anim_switch_set_rest
opwire -n $_obj_geo1_MMF_Remesh_Anim_copy_oldname -0 $_obj_geo1_MMF_Remesh_Anim_promote_name
opwire -n $_obj_geo1_MMF_Remesh_Anim_promote_name -0 $_obj_geo1_MMF_Remesh_Anim_set_name
opwire -n $_obj_geo1_MMF_Remesh_Anim_rename_name_2 -0 $_obj_geo1_MMF_Remesh_Anim_create_piece_connectivity
opwire -n $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE -0 $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece
opwire -n $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS -1 $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece
opwire -n $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT -2 $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece
opwire -n $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE -3 $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_name_obj -0 $_obj_geo1_MMF_Remesh_Anim_freeze_frame
opwire -n $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs -0 $_obj_geo1_MMF_Remesh_Anim_compile_end
opwire -n $_obj_geo1_MMF_Remesh_Anim_freeze_frame -0 $_obj_geo1_MMF_Remesh_Anim_compile_freeze
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_name_obj -0 $_obj_geo1_MMF_Remesh_Anim_compile_anim
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_deform -0 $_obj_geo1_MMF_Remesh_Anim_out_deform
opwire -n $_obj_geo1_MMF_Remesh_Anim_compile_anim -0 $_obj_geo1_MMF_Remesh_Anim_in_anim
opwire -n $_obj_geo1_MMF_Remesh_Anim_compile_freeze -0 $_obj_geo1_MMF_Remesh_Anim_in_freeze
opwire -n $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs -0 $_obj_geo1_MMF_Remesh_Anim_remesh
opwire -n $_obj_geo1_MMF_Remesh_Anim_remesh -0 $_obj_geo1_MMF_Remesh_Anim_REMESH
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_rest_pos -0 $_obj_geo1_MMF_Remesh_Anim_STATIC
opwire -n $_obj_geo1_MMF_Remesh_Anim_in_anim -0 $_obj_geo1_MMF_Remesh_Anim_ANIM
opwire -n $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals -0 $_obj_geo1_MMF_Remesh_Anim_del_unused
opwire -n $_obj_geo1_MMF_Remesh_Anim_rename_name_4 -0 $_obj_geo1_MMF_Remesh_Anim_store_prim_id
opwire -n $_obj_geo1_MMF_Remesh_Anim_store_prim_id -0 $_obj_geo1_MMF_Remesh_Anim_create_obj_name
opwire -n $_obj_geo1_MMF_Remesh_Anim_create_obj_name -0 $_obj_geo1_MMF_Remesh_Anim_set_to_ref
opwire -n $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims -0 $_obj_geo1_MMF_Remesh_Anim_out_pieces
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_to_ref -0 $_obj_geo1_MMF_Remesh_Anim_in_named_objs
opwire -n $_obj_geo1_MMF_Remesh_Anim_in_named_objs -0 $_obj_geo1_MMF_Remesh_Anim_get_bucket_size
opwire -n $_obj_geo1_MMF_Remesh_Anim_get_bucket_size -0 $_obj_geo1_MMF_Remesh_Anim_scatter_pts
opwire -n $_obj_geo1_MMF_Remesh_Anim_scatter_pts -0 $_obj_geo1_MMF_Remesh_Anim_set_subname
opwire -n $_obj_geo1_MMF_Remesh_Anim_in_named_objs -0 $_obj_geo1_MMF_Remesh_Anim_transfer_subname
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_subname -1 $_obj_geo1_MMF_Remesh_Anim_transfer_subname
opwire -n $_obj_geo1_MMF_Remesh_Anim_transfer_subname -0 $_obj_geo1_MMF_Remesh_Anim_promote_subname_to_prims
opwire -n $_obj_geo1_MMF_Remesh_Anim_create_obj_name -0 $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces
opwire -n $_obj_geo1_MMF_Remesh_Anim_out_pieces -1 $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_rest_pos -0 $_obj_geo1_MMF_Remesh_Anim_split_uvs
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_rest_pos -0 $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs
opwire -n $_obj_geo1_MMF_Remesh_Anim_split_uvs -1 $_obj_geo1_MMF_Remesh_Anim_switchif_keep_uvs
opwire -n $_obj_geo1_MMF_Remesh_Anim_fuse -0 $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces
opwire -n $_obj_geo1_MMF_Remesh_Anim_out_deform -0 $_obj_geo1_MMF_Remesh_Anim_in_pieces
opwire -n $_obj_geo1_MMF_Remesh_Anim_rename_name_1 -0 $_obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1
opwire -n $_obj_geo1_MMF_Remesh_Anim_switch_it_base_piece -0 $_obj_geo1_MMF_Remesh_Anim_set_name_obj
opwire -n $_obj_geo1_MMF_Remesh_Anim_in_pieces -0 $_obj_geo1_MMF_Remesh_Anim_fuse
opwire -n $_obj_geo1_MMF_Remesh_Anim_out_deform -0 $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs
opwire -n $_obj_geo1_MMF_Remesh_Anim_out_fused_pieces -1 $_obj_geo1_MMF_Remesh_Anim_switchif_fuse_for_uvs
opwire -n $_obj_geo1_MMF_Remesh_Anim_concat_name_pieces -0 $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE
opwire -n $_obj_geo1_MMF_Remesh_Anim_create_uv_connectivity1 -0 $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_UVS
opwire -n $_obj_geo1_MMF_Remesh_Anim_set_name -0 $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_CUSTOM_ATTRIBUTE
opwire -n $_obj_geo1_MMF_Remesh_Anim_create_piece_connectivity -0 $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_SEPARATED_OBJECT
opwire -n $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket -0 $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket
opwire -n $_obj_geo1_MMF_Remesh_Anim_clean_attrs -1 $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket
opwire -n $_obj_geo1_MMF_Remesh_Anim_switchif_rename -0 $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals
opwire -n $_obj_geo1_MMF_Remesh_Anim_recompute_normals -1 $_obj_geo1_MMF_Remesh_Anim_switchif_recompute_normals
opwire -n $_obj_geo1_MMF_Remesh_Anim_switchif_rename -0 $_obj_geo1_MMF_Remesh_Anim_recompute_normals
opwire -n $_obj_geo1_MMF_Remesh_Anim_del_unused -0 $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs
opwire -n $_obj_geo1_MMF_Remesh_Anim_uvquickshade -1 $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs
opwire -n $_obj_geo1_MMF_Remesh_Anim_del_unused -0 $_obj_geo1_MMF_Remesh_Anim_uvquickshade
opwire -n $_obj_geo1_MMF_Remesh_Anim_switchif_check_uvs -0 $_obj_geo1_MMF_Remesh_Anim_clean_grps
opwire -n $_obj_geo1_MMF_Remesh_Anim_clean_grps -0 $_obj_geo1_MMF_Remesh_Anim_clean_attrs
opwire -n $_obj_geo1_MMF_Remesh_Anim_switch_set_rest -0 $_obj_geo1_MMF_Remesh_Anim_rename_name_1
opwire -n $_obj_geo1_MMF_Remesh_Anim_switch_set_rest -0 $_obj_geo1_MMF_Remesh_Anim_rename_name_2
opwire -n $_obj_geo1_MMF_Remesh_Anim_switch_set_rest -0 $_obj_geo1_MMF_Remesh_Anim_rename_name_3
opwire -n $_obj_geo1_MMF_Remesh_Anim_switch_set_rest -0 $_obj_geo1_MMF_Remesh_Anim_copy_oldname
opwire -n $_obj_geo1_MMF_Remesh_Anim_rename_name_3 -1 $_obj_geo1_MMF_Remesh_Anim_copy_oldname
opwire -n $_obj_geo1_MMF_Remesh_Anim_del_name_mod -0 $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1
opwire -n $_obj_geo1_MMF_Remesh_Anim_rename_oldname_1 -0 $_obj_geo1_MMF_Remesh_Anim_switchif_rename
opwire -n $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2 -1 $_obj_geo1_MMF_Remesh_Anim_switchif_rename
opwire -n $_obj_geo1_MMF_Remesh_Anim_del_name_mod -0 $_obj_geo1_MMF_Remesh_Anim_rename_oldname_2
opwire -n $_obj_geo1_MMF_Remesh_Anim_compile_end -0 $_obj_geo1_MMF_Remesh_Anim_del_name_mod
opwire -n $_obj_geo1_MMF_Remesh_Anim_switch_set_rest -0 $_obj_geo1_MMF_Remesh_Anim_rename_name_4
opwire -n $_obj_geo1_MMF_Remesh_Anim_REMESH_BY_PIECE -0 $_obj_geo1_MMF_Remesh_Anim_color_vis_bucket
opwire -n $_obj_geo1_MMF_Remesh_Anim_switchif_visualize_bucket -0 $_obj_geo1_MMF_Remesh_Anim_output
opcf ..

set oidx = 0
if ($argc >= 9 && "$arg9" != "") then
    set oidx = $arg9
endif

if ($argc >= 5 && "$arg4" != "") then
    set output = $_obj_geo1_MMF_Remesh_Anim
    opwire -n $output -$arg5 $arg4
endif
if ($argc >= 6 && "$arg6" != "") then
    set input = $_obj_geo1_MMF_Remesh_Anim
    if ($arg8) then
        opwire -n -i $arg6 -0 $input
    else
        opwire -n -o $oidx $arg6 -0 $input
    endif
endif
opcf $saved_path
'''
hou.hscript(h_preamble + h_extra_args + h_cmd)
