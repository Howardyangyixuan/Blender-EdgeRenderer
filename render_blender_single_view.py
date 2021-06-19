# A simple script that uses blender to render views of a single object by rotation the camera around it.
# Also produces depth map at the same time.
#
# Tested with Blender 2.9
# Yyx modify 
# 1. add CYCLES setting include gpu & cpu
# 2. keep in 2.9, add material & background color (have to set transparency to false)
# 3. add EEVEE setting include Ambient Occlusion
# 4. roration and position for atlas result
# Example:
# blender --background --python mytest.py -- --views 10 /path/to/my.obj
#

import argparse, sys, os, math, re
import bpy
from glob import glob

parser = argparse.ArgumentParser(description='Renders given obj file by rotation a camera around it.')
parser.add_argument('--views', type=int, default=30,
                    help='number of views to be rendered')
parser.add_argument('obj', type=str,
                    help='Path to the obj file to be rendered.')
parser.add_argument('edge', type=str,
                    help='Path to the edge obj file to be rendered.')
parser.add_argument('--output_folder', type=str, default='/tmp',
                    help='The path the output will be dumped to.')
parser.add_argument('--scale', type=float, default=1,
                    help='Scaling factor applied to model. Depends on size of mesh.')
parser.add_argument('--remove_doubles', type=bool, default=True,
                    help='Remove double vertices to improve mesh quality.')
parser.add_argument('--edge_split', type=bool, default=True,
                    help='Adds edge split filter.')
parser.add_argument('--depth_scale', type=float, default=1.4,
                    help='Scaling that is applied to depth. Depends on size of mesh. Try out various values until you get a good result. Ignored if format is OPEN_EXR.')
parser.add_argument('--color_depth', type=str, default='8',
                    help='Number of bit per channel used for output. Either 8 or 16.')
parser.add_argument('--format', type=str, default='PNG',
                    help='Format of files generated. Either PNG or OPEN_EXR')
parser.add_argument('--resolution', type=int, default=1024,
                    help='Resolution of the images.')
parser.add_argument('--engine', type=str, default='BLENDER_EEVEE',
                    help='Blender internal engine for rendering. E.g. CYCLES, BLENDER_EEVEE, ...')

argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)

# Set up rendering
context = bpy.context
scene = bpy.context.scene
render = bpy.context.scene.render


render.engine = args.engine
# render.engine = 'CYCLES'
# CYCLES settings
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# EEVEE settings
bpy.context.scene.eevee.use_gtao = True
bpy.context.scene.eevee.gtao_factor = 5
bpy.context.scene.eevee.gtao_distance = 1
bpy.context.scene.eevee.gtao_quality = 0.25

render.image_settings.color_mode = 'RGBA' # ('RGB', 'RGBA', ...)
render.image_settings.color_depth = args.color_depth # ('8', '16')
render.image_settings.file_format = args.format # ('PNG', 'OPEN_EXR', 'JPEG, ...)
render.resolution_percentage = 100
render.resolution_x = args.resolution * (100 / render.resolution_percentage)
render.resolution_y = args.resolution * (100 / render.resolution_percentage)
render.film_transparent = True
# render.film_transparent = False

scene.use_nodes = True
scene.view_layers["View Layer"].use_pass_normal = True
scene.view_layers["View Layer"].use_pass_diffuse_color = True
scene.view_layers["View Layer"].use_pass_object_index = True

nodes = bpy.context.scene.node_tree.nodes
links = bpy.context.scene.node_tree.links

# Clear default nodes
for n in nodes:
    nodes.remove(n)

# Create input render layer node
render_layers = nodes.new('CompositorNodeRLayers')

# Delete default cube
context.active_object.select_set(True)
bpy.ops.object.delete()

# Import textured mesh
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.import_scene.obj(filepath=args.obj)
bpy.ops.import_scene.obj(edgepath=args.edge)
# bpy.ops.import_mesh.ply(filepath = args.obj)

obj = bpy.context.selected_objects[0]
context.view_layer.objects.active = obj

# Possibly disable specular shading
for slot in obj.material_slots:
    node = slot.material.node_tree.nodes['Principled BSDF']
    node.inputs['Specular'].default_value = 0.05

if args.scale != 1:
    bpy.ops.transform.resize(value=(args.scale,args.scale,args.scale))
    bpy.ops.object.transform_apply(scale=True)
if args.remove_doubles:
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')
if args.edge_split:
    bpy.ops.object.modifier_add(type='EDGE_SPLIT')
    context.object.modifiers["EdgeSplit"].split_angle = 1.32645
    bpy.ops.object.modifier_apply(modifier="EdgeSplit")

# Set objekt IDs
obj.pass_index = 1

#Yyx 
def select_object(obj):
    clear_selection()
    bpy.context.selected_objects.clear()
    bpy.context.scene.objects.active = obj
    obj.select = True
    return obj

# select obj
prototype = bpy.context.object
bpy.ops.object.select_all(action='SELECT')
# a little side
bpy.context.object.rotation_euler[0] = 0
bpy.context.object.rotation_euler[1] = 0
#30
bpy.context.object.rotation_euler[2] = -0.523599
#45
# bpy.context.object.rotation_euler[2] = -0.785398


#front
# bpy.context.object.rotation_euler[0] = -8.93609
# bpy.context.object.rotation_euler[1] = -3.14159
# bpy.context.object.rotation_euler[2] = -15.708

#atlas
# bpy.context.object.location[0] = 0.065471
# bpy.context.object.location[1] = -0.030256
# bpy.context.object.location[2] = 0.05539
# bpy.context.object.rotation_euler[0] = -7.72888
# bpy.context.object.rotation_euler[1] = 3.54133
# bpy.context.object.rotation_euler[2] = 4.36812

# add material & world background color
mat = bpy.data.materials.new("my")
bpy.ops.object.material_slot_add()
prototype.material_slots[0].material = mat
bpy.data.materials["my"].use_nodes = True
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
bpy.data.materials["my"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.5, 0.5, 0.5, 1)
bpy.data.materials["my"].node_tree.nodes["Principled BSDF"].inputs[19].default_value = 1

# # Make light just directional, disable shadows.
light = bpy.data.lights['Light']
light.type = 'SUN'
light.use_shadow = False
# Possibly disable specular shading:
light.specular_factor = 1.0
light.energy = 5.0

# Add another light source so stuff facing away from light is not completely dark
bpy.ops.object.light_add(type='SUN')
light2 = bpy.data.lights['Sun']
light2.use_shadow = False
light2.specular_factor = 3.0
light2.energy = 1
bpy.data.objects['Sun'].rotation_euler = bpy.data.objects['Light'].rotation_euler
bpy.data.objects['Sun'].rotation_euler[0] += 180

# Place camera
cam = scene.objects['Camera']
cam.location = (0, 2, 1)
cam.data.lens = 35# 60 mm focal length
cam.data.sensor_width = 32
cam.data.sensor_height = 32.0
# cam.data.sensor_width = float(camObj.data.sensor_height) / im_size * im_size

cam_constraint = cam.constraints.new(type='TRACK_TO')
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'

cam_empty = bpy.data.objects.new("Empty", None)
cam_empty.location = (0, 0, 0)
cam.parent = cam_empty

scene.collection.objects.link(cam_empty)
context.view_layer.objects.active = cam_empty
cam_constraint.target = cam_empty

stepsize = 360.0 / args.views
rotation_mode = 'XYZ'

# model_identifier = os.path.split(os.path.split(args.obj)[0])[1]
model_identifier = args.obj.split('/')[-1].split('.')[0]
current = './'
print("model:",model_identifier)
print("model:",args.obj)
# fp = os.path.join(os.path.abspath(args.output_folder), model_identifier, model_identifier)
fp = os.path.join(os.path.abspath(args.output_folder), current, model_identifier)

for i in range(0, args.views):
    print("Rotation {}, {}".format((stepsize * i), math.radians(stepsize * i)))

    render_file_path = fp + '_r_{0:03d}'.format(int(i * stepsize))
    # render_file_path = fp + '_r_{0:03d}'.format(int(i * stepsize))

    scene.render.filepath = render_file_path
    # depth_file_output.file_slots[0].path = render_file_path + "_depth"
    # normal_file_output.file_slots[0].path = render_file_path + "_normal"
    # albedo_file_output.file_slots[0].path = render_file_path + "_albedo"
    # id_file_output.file_slots[0].path = render_file_path + "_id"

    bpy.ops.render.render(write_still=True)  # render still

    cam_empty.rotation_euler[2] += math.radians(stepsize)

# For debugging the workflow
#bpy.ops.wm.save_as_mainfile(filepath='debug.blend')
