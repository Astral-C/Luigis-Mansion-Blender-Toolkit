import os
import bpy
import sys
import bmesh
from bStream import *
from gx_utils import *
from bin_writer.geometry import *
from bin_writer.materials import *
from util import to_triangles, to_triangles_uv
from gx_texture import gx_texture
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator 
from itertools import chain 
import numpy as np

# Ui things I hate
class GraphNodeSettingsPanel(bpy.types.Panel):
    bl_label = "Bin Node Settings"
    bl_idname = "OBJECT_PT_bin_node"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        row = self.layout.row()
        row.prop(bpy.context.active_object, "bin_render_flags")

class BinMaterialsSettingsPanel(bpy.types.Panel):
    bl_label = "Bin Material Settings"
    bl_idname = "MATERIAL_PT_BIN_SETTINGS"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    def draw(self, context):
        row = self.layout.row()
        row.prop(bpy.context.material, "bin_wrap_mode_u")
        row.prop(bpy.context.material, "bin_wrap_mode_v")
        row.prop(bpy.context.material, "bin_shader_tint")

bin_mat_wrap_modes = [
    ("CLAMP", "Clamp", "", 0),
    ("REPEAT", "Repeat", "", 1),
    ("MIRROR", "Mirror", "", 2),
]

bpy.utils.register_class(GraphNodeSettingsPanel)
bpy.types.Object.bin_render_flags = bpy.props.IntProperty(name="Render Flags",min=0,max=255)
bpy.types.Material.bin_wrap_mode_u = bpy.props.EnumProperty(name="Wrap U",items=bin_mat_wrap_modes)
bpy.types.Material.bin_wrap_mode_v = bpy.props.EnumProperty(name="Wrap V",items=bin_mat_wrap_modes)
bpy.types.Material.bin_shader_tint = bpy.props.FloatVectorProperty(name="Tint",subtype="COLOR",size=4,min=0.0,max=1.0,default=(1.0, 1.0, 1.0, 1.0))

#actual model loading stuff

class bin_model_import():
    def __init__(self, pth):
        self.name = os.path.basename(pth)
        stream = bStream(path=pth)
        stream.seek(12)
        self.offsets = [stream.readUInt32() for offset in range(21)]
        print(self.offsets)

        stream.seek(self.offsets[2])
        
        v_count = int((self.offsets[3] - self.offsets[2]) / 6) #0
        tc_count = int((self.offsets[10] - self.offsets[6]) / 8)#/8
        shader_count = int((self.offsets[11] - self.offsets[10]) / 0x28)

        self.verts = []
        for x in range(v_count):
            t = [stream.readInt16(), stream.readInt16(), stream.readInt16()]
            self.verts.append([t[0], -t[2], t[1]])

        self.materials = [self.readShader(stream, x) for x in range(shader_count)]
        stream.seek(self.offsets[6])
        self.texcoords = [[stream.readFloat(), stream.readFloat()] for x in range(tc_count)]
        
        root = bpy.data.objects.new('bin_model', None)
        bpy.context.scene.collection.objects.link(root)
        self.readGraphObjects(stream, 0, root)

    def readGraphObjects(self, stream, index, root):
        stream.seek(self.offsets[12] + (0x8C * index))
        
        parent_index = stream.readInt16()
        child_index = stream.readInt16()
        next_index = stream.readInt16()
        prev_index = stream.readInt16()
        stream.readInt8() # Padding
        render_flags = stream.readInt8() # RenderFlag
        stream.readInt16() # Padding
        scale = (stream.readFloat(), stream.readFloat(), stream.readFloat())
        rot = (stream.readFloat(), stream.readFloat(), stream.readFloat())
        pos_y = [stream.readFloat(), stream.readFloat(), stream.readFloat()]
        pos = (pos_y[0], -pos_y[2], pos_y[1])
        
        bbMin = (stream.readFloat(), stream.readFloat(), stream.readFloat())
        bbMax = (stream.readFloat(), stream.readFloat(), stream.readFloat())
        stream.readFloat() # unk1
        
        part_count = stream.readInt16()
        stream.readUInt16() #Padding
        part_offset = stream.readInt32()
        
        stream.seek(part_offset + self.offsets[12])
        parts = [[stream.readInt16(), stream.readInt16()] for x in range(part_count)]
        
        cur_obj = bpy.data.objects.new('Graph_Obj{0}'.format(index), None)
        cur_obj.bin_render_flags = render_flags 
        print(f"Render Flags: {root.bin_render_flags} For Object {cur_obj.name}")
        cur_obj.parent = root
        cur_obj.location = pos
        cur_obj.scale = scale
        bpy.context.scene.collection.objects.link(cur_obj)

        for part in parts:
            
            batch = self.readBatch(stream, part[1])
            material = self.materials[part[0]]
            
            mesh = bpy.data.meshes.new('Batch_{0}'.format(part[1]))
            mesh.from_pydata(self.verts, [], batch[0])

            bm = bmesh.new()
            bm.from_mesh(mesh)
            uv = bm.loops.layers.uv.new("UVMap")

            texcoord_tris = list(chain.from_iterable(batch[1]))
            for face in bm.faces:
                for loop in face.loops:
                    if(loop.index >= len(texcoord_tris) or texcoord_tris[loop.index] >= len(self.texcoords)):
                        continue
                    loop[uv].uv = self.texcoords[texcoord_tris[loop.index]]
            
            bm.to_mesh(mesh)
            bm.free()

            mesh.materials.append(material)
            mesh.update()
            
            batch_obj = bpy.data.objects.new('Batch_{0}'.format(part[1]), mesh)
            batch_obj.parent = cur_obj
            
            bpy.context.scene.collection.objects.link(batch_obj)
            bpy.context.view_layer.objects.active = batch_obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.delete_loose()
            bpy.ops.object.mode_set(mode='OBJECT')
            
        
        if(child_index >= 0):
            self.readGraphObjects(stream, child_index, cur_obj)
        if(next_index >= 0):
            self.readGraphObjects(stream, next_index, root)
        
    
    def readShader(self, stream, index):
        stream.seek(self.offsets[10] + (0x28 * index))
        stream.readUInt8()
        stream.readUInt8()
        stream.readUInt8()
        tint = stream.readUInt32()
        stream.readUInt8()
        bin_materials = self.readMaterial(stream, stream.readInt16(), tint)
        unk_index = [stream.readInt16() for x in range(7)]
        unk1_index = [stream.readUInt16() for x in range(8)]
        return bin_materials
        
    def readMaterial(self, stream, index, tint):
        if(index >= 0):
            stream.seek(self.offsets[1] + (0x14 * index))
            #print("Reading Material at {0:X}".format(self.offsets[1] + (0x14 * index)))
            mat = bpy.data.materials.new("BinMaterial_{}".format(index))
            mat.use_nodes = True
            mat_tree = mat.node_tree
            texIndex = stream.readInt16()
            stream.readUInt16()
            mat.bin_wrap_mode_u = ['CLAMP', 'REPEAT', 'MIRROR'][stream.readUInt8()]
            mat.bin_wrap_mode_v = ['CLAMP', 'REPEAT', 'MIRROR'][stream.readUInt8()]
            mat.bin_shader_tint = [(tint & 0xFF) / 255, (tint & 0x00FF) / 255, (tint & 0x0000FF) / 255, (tint & 0x0000FF) / 255]

            #mat.texture_coords = 'UV'
            #mat.mapping = 'FLAT'
            texture_node = mat_tree.nodes.new("ShaderNodeTexImage")
            texture_node.image = self.readTexture(stream, texIndex)
            bsdf = mat_tree.nodes.get('Principled BSDF')
            mat_tree.links.new(texture_node.outputs[0], bsdf.inputs[0])
            return mat
        
        else:
            return None

    def readTexture(self, stream, index):
        stream.seek(self.offsets[0] + (0xC * index))
        width = stream.readUInt16()
        height = stream.readUInt16()
        format = stream.readInt8()
        stream.readUInt8()
        stream.readUInt16()
        offset = stream.readUInt32()
        if(format == 0x0E):
            return gx_texture.bi_from_cmpr(stream, width, height, self.offsets[0] + offset, index)
        elif(format == 0x04):
            return gx_texture.bi_from_rgb565(stream, width, height, self.offsets[0] + offset, index)       
    
    def readBatch(self, stream, index, total_verts = 0):
        stream.seek(self.offsets[11] + 0x18*index)
        
        face_count = stream.readUInt16()
        list_size = (stream.readUInt16() << 5)
        
        attribute_field =  stream.readUInt32()

        mask = 1
        attribs = []
        for attrib in range(26):
            if(((attribute_field & mask) >> attrib) == 1):
                attribs.append(GXAttribute(attrib))
            mask = mask << 1
        
        #print(attribs)
        
        stream.readUInt16() # normals, positions
        stream.readUInt8() # uvs
        nbt = (stream.readUInt8() == 1) # nbt
        primitive_offset = stream.readUInt32()
        stream.seek(self.offsets[11]+primitive_offset)
        list_size += (primitive_offset+self.offsets[11])
        face_data, texcoords = self.readPrimitives(stream, attribs, list_size, total_verts, nbt)
        
        return (face_data, texcoords)
    
    def readAttrib(self, stream, nbt, attrib):
        if(nbt and attrib == GXAttribute.Normal):
            r = stream.readUInt16()
            stream.readUInt16()
            stream.readUInt16()
            return r

        else:
            return stream.readUInt16()


    def readPrimitives(self, stream, attributes, size, total_verts, nbt):
        local_texcoords = [] 
        face_data = [] # vertex indicies to use in this primitive
        gxprimitives = [] #stores raw element buffers
        
        print(f'Reading primitve with ttribs {attributes}')
        current_primitive = stream.readUInt8()
        # read the primitives
        while(GXPrimitiveTypes.valid_opcode(current_primitive) and stream.fhandle.tell() < size):
            gxprimitives.append((
                [[self.readAttrib(stream, nbt, attributes[y]) for y in range(len(attributes))] for x in range(stream.readUInt16())],
                current_primitive    
            ))
            current_primitive = stream.readUInt8()
        
        # create verts list
        for primitive in gxprimitives:
            v_index = attributes.index(GXAttribute.Position)
            t_index = (attributes.index(GXAttribute.Tex0) if GXAttribute.Tex0 in attributes else (attributes.index(GXAttribute.Tex1) if GXAttribute.Tex1 in attributes else 0))
            local_texcoords.extend(to_triangles_uv([vertex[t_index] for vertex in primitive[0]], primitive[1]))
            face_data.extend(to_triangles([vertex[v_index] for vertex in primitive[0]], primitive[1]))
            
        return (face_data, local_texcoords)

class bin_model_export():
    def __init__(self, pth):
        #Uses fixed name to get root of bin model, first child is the root of the scene graph
        root = bpy.context.scene.objects['bin_model'].children[0]
        
        self.meshes_used = []
        self.materials_used = []
        self.get_used_meshes(root)

        self.textures = TextureManager(self.materials_used)
        self.shaders = ShaderManager(self.textures.material_indices, self.materials_used)
        self.batches = BatchManager(self.meshes_used)
        
        print(f"Meshes being used are {self.meshes_used}")

        graph_nodes = []

        self.generate_scenegraph(root, graph_nodes, 0, -1, -1)

        print(graph_nodes)

        offsets = [0 for x in range(21)]
        out = bStream(path=pth)
        out.writeUInt8(0x02)
        out.writeString("NewBinModel") #generic name lmao
        out.writeUInt32List(offsets)

        offsets[0] = out.tell()
        self.textures.writeTextures(out)
        out.padTo32(out.tell())

        offsets[1] = out.tell()
        self.textures.writeMaterials(out)
        out.padTo32(out.tell())

        offsets[2] = out.tell()
        for mesh in self.meshes_used:
            for vertex in mesh.to_mesh().vertices:
                out.writeInt16(int(vertex.co[0]))
                out.writeInt16(int(vertex.co[2]))
                out.writeInt16(int(-vertex.co[1]))
        
        out.padTo32(out.tell())
        offsets[3] = out.tell()
        for mesh in self.meshes_used:
            mesh_data = mesh.to_mesh()
            for vertex in mesh_data.vertices:
                out.writeFloat(-int(vertex.normal[0]))
                out.writeFloat(-int(vertex.normal[1]))
                out.writeFloat(-int(vertex.normal[2]))

        out.padTo32(out.tell())
        offsets[6] = out.tell()
        for texcoord in self.batches.texcoord_data:
                out.writeFloat(texcoord[0])
                out.writeFloat(-texcoord[1])

        out.padTo32(out.tell())

        offsets[10] = out.tell()
        self.shaders.writeShaders(out)
        out.padTo32(out.tell())

        offsets[11] = out.tell()
        self.batches.write(out)
        out.padTo32(out.tell())

        offsets[12] = out.tell()

        out.pad(0x8C*len(graph_nodes))
        for node in graph_nodes:
            node['part_offset'] = out.tell() - offsets[12]
            for part in node['parts']:
                print(f"Writing Node {node['my_index']} Part: {part} at offset {out.tell():x}")
                out.writeInt16(part[1])
                out.writeInt16(part[0])
        
        out.padTo32(out.tell())
                
        out.seek(offsets[12])
        for node in graph_nodes:

            out.writeInt16(node['parent_index'])
            out.writeInt16(node['child_index'])
            out.writeInt16(node['next_index'])
            out.writeInt16(node['prev_index'])
            out.writeUInt8(node['render_flags'])
            out.writeUInt8(node['render_flags'])
            out.writeUInt16(0)
            for v in node['scale']:
                out.writeFloat(v)

            for v in node['rotation']:
                out.writeFloat(v)

            for v in node['position']:
                out.writeFloat(v)

            for v in range(6): #no bb for now, easy addition later
                out.writeFloat(0)

            out.writeFloat(0) #unk
            out.writeUInt16(node['part_count'])
            out.writeUInt16(0)
            out.writeUInt32(node['part_offset'])
            out.writeUInt32(0)
            out.writeUInt32List([0 for x in range(13)])


        out.seek(0x0C)
        out.writeUInt32List(offsets)
        out.close()

    def get_used_meshes(self, obj):
        for child in obj.children:
            if(child.type == 'MESH'):
                bpy.context.view_layer.objects.active = child
                bpy.ops.object.modifier_apply(modifier="TRIANGULATE")
                self.meshes_used.append(child)
                self.materials_used.append(child.active_material)
            if(child.type == 'EMPTY'):
                self.get_used_meshes(child)


    def generate_scenegraph(self, obj, scenegraph, cur_index, parent_index, prev_index):
        node = {
            'blender_node_name': obj.name,
            'my_index' : cur_index,
            'parent_index' : parent_index,
            'child_index' : -1,
            'next_index' : -1,
            'prev_index' : prev_index,
            'render_flags' : obj.bin_render_flags,
            'scale' : [1, 1, 1],
            'rotation' : [0, 0, 0],
            'position' : [obj.location[0], obj.location[2], -obj.location[1]],
            'part_count': 0,
            'parts':[],
            'part_offset': 0
        }

        scenegraph.append(node)

        lprev_index = 0
        parent_index = cur_index

        #Get the number of scenegraph children
        real_children = 0
        real_child_index = 0
        for child in obj.children:
            if(child.type == 'EMPTY'):
                real_children += 1

        next_stack = []
        for child in obj.children:
            if(child.type == 'EMPTY'):
                cur_index += 1
                real_child_index += 1
                if(node['child_index'] == -1):
                    node['child_index'] = cur_index
                    lprev_index = cur_index

                
                if(child is not obj.children[-1]):
                    next_stack.append(cur_index)

                cur_index = self.generate_scenegraph(child, scenegraph, cur_index, parent_index, lprev_index)
                lprev_index = real_child_index
                
                if(child is not obj.children[-1]):
                    scenegraph[next_stack[-1]]['next_index'] = cur_index+1 if real_child_index < real_children else -1
                    next_stack.pop()
            
            elif(child.type == 'MESH'):
                node['part_count'] += 1
                print(f"Looking for {child.name}, which is part of {obj.name} and has batch index {self.batches.getBatchIndex(child.name)}")
                node['parts'].append([self.batches.getBatchIndex(child.name), self.shaders.getShaderIndex(child.active_material.name)])

        return cur_index