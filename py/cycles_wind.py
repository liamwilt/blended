##__BASICS__##

import bpy
import numpy as np
import mathutils
import os
import random
import itertools

c = bpy.context
d = bpy.data
o = bpy.ops
scene = d.scenes["Scene"]
render = d.scenes["Scene"].render
cbod = d.objects['Cloth']
cphys = d.objects['Cloth'].modifiers['Cloth'].settings


##__VALUES__##

b = [0.05]
m = [0.15, 0.30, 0.60, 0.90, 1.00]

##__Manipulating__Cycles__Nodes__##

c.scene.render.engine = 'CYCLES'
o.object.select_all(action='TOGGLE')
cbod.select = True
c.scene.objects.active = cbod

the_mat=d.materials["the_mat"]

the_mat.node_tree.nodes.clear()
ctex=the_mat.node_tree.nodes.new(type="ShaderNodeTexImage")
diffuse=the_mat.node_tree.nodes.new(type = 'ShaderNodeBsdfDiffuse')
out=the_mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')

ld_img=d.images.load("/home/william/blender/textures/floral02.jpg") ##  <---------- IMAGE FILE PATH
ctex.image=ld_img

c.object.active_material.node_tree.links.new(ctex.outputs['Color'], diffuse.inputs['Color'])
c.object.active_material.node_tree.links.new(diffuse.outputs['BSDF'], out.inputs['Surface'])


##__PROGRAM__##

def wind():
    ed = 57.2957795 #the approximate value of ~1 radian in euler degrees
    rrx = np.linspace(-1.658064, -1.483531, 3) #radian range 'x'
    rrz = np.linspace(-3.141594,3.141594, 36) #radian range 'z' 
    
    x=random.choice(rrx) #radian rotation 'x'
    z=random.choice(rrz) #radian rotation 'z'
    
#    tf = open('Blender_Python_Files/Sample Mass 5/SampleM5.txt', 'a')
#    
#    tf.write('Video_Sm_' + N + '\n')
#    tf.write('x = ' + (str(round(x*ed, 0))) + '\n')
#    tf.write('y = 0' + '\n')
#    tf.write('z = ' + (str(round(z*ed, 0))) + '\n')
#    
#    tf.close()   
    
    d.objects["Field"].rotation_euler[0] = x
    d.objects["Field"].rotation_euler[2] = z

def windvid(k,h):
        
    cphys.air_damping=0.66
    
    cphys.quality=12
    cphys.mass=m[h]
    cphys.structural_stiffness=10
    cphys.bending_stiffness=b[k]
    cphys.spring_damping=6.5
    
    global N
    N = (str(k))+(str(h))
    
    wind()
    scene.frame_start = 1
    scene.frame_end = 300
    render.filepath="/home/william/blender/renders/" + 'Video_VSS_' + N +'_'  ## <------- RENDER FILE PATH
    o.render.render(animation=True)
    
for tup in itertools.product([0,1,2,3,4,5], repeat = 2):
        windvid(*tup)