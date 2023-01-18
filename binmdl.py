import os
import bpy
import sys
import bmesh
from bStream import *
from gx_utils import *
from bin_writer.geometry import *
from bin_writer.materials import *
from util import to_triangles, to_triangles_uv, to_triangles_gxverts
from pyffi.tristrip import GXVertex
from gx_texture import gx_texture
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator 
import itertools 
import numpy as np

# Ui things I hate
class GraphNodeSettingsPanel(bpy.types.Panel):
    bl_label = "Bin Node Settings"
    bl_idname = "OBJECT_PT_bin_node"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        if(bpy.context.active_object.type == 'EMPTY'):
            box = self.layout.box()
            box.label(text="Render Settings", icon="MOD_WIREFRAME")

            box.row().prop(bpy.context.active_object, "bin_render_cast_shadow", toggle=True)

            row = box.row()
            row.prop(bpy.context.active_object, "bin_render_fourthwall", toggle=True)
            row.prop(bpy.context.active_object, "bin_render_ceiling", toggle=True)

            row = box.row()
            row.prop(bpy.context.active_object, "bin_render_transparent", toggle=True)
            row.prop(bpy.context.active_object, "bin_render_fullbright", toggle=True)

            row = box.row()
            row.prop(bpy.context.active_object, "bin_render_rf16", toggle=True)
            row.prop(bpy.context.active_object, "bin_render_rf32", toggle=True)



            box = self.layout.box()
            box.label(text="Node Import/Export", icon="EXPORT")
            box.operator_context = 'INVOKE_DEFAULT' #'INVOKE_AREA'
            box.operator("import_anim.mansionanm", text="Import ANM")
            box.operator("export_anim.mansionanm", text="Export ANM")
            box.operator("export_model.mansionbin", text="Export Bin")
            
        if(bpy.context.active_object.type == 'MESH'):
            box = self.layout.box()
            box.label(text="Mesh Settings", icon="MOD_WIREFRAME")
            row = box.row()
            row.prop(bpy.context.active_object, "batch_use_normals", toggle=True)
            #row.prop(bpy.context.active_object, "batch_use_positions")
            row.prop(bpy.context.active_object, "batch_use_nbt", toggle=True)
            row = box.row()
            row.prop(bpy.context.active_object, "batch_primitive_type")


class BinMaterialsSettingsPanel(bpy.types.Panel):
    bl_label = "Bin Material Settings"
    bl_idname = "MATERIAL_PT_BIN_SETTINGS"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    def draw(self, context):
        box = self.layout.box()
        box.label(text="Texture Format", icon="TEXTURE")
        box.row().prop(bpy.context.material, "gx_img_type", text='')

        box = self.layout.box()
        box.label(text="Wrap Modes", icon='UV')
        row = box.row()
        row.label(text="U")
        row.prop(bpy.context.material, "bin_wrap_mode_u", expand=True)
        row = box.row()
        row.label(text="V")
        row.prop(bpy.context.material, "bin_wrap_mode_v", expand=True)

        box = self.layout.box()
        box.label(text="Tint Settings", icon="COLOR")
        box.row().prop(bpy.context.material, "bin_shader_tint", text='')

        box = self.layout.box()
        box.label(text="Unknown Settings", icon="QUESTION")
        row = box.row()
        row.prop(bpy.context.material, "bin_shader_unk1")
        row.prop(bpy.context.material, "bin_shader_unk2")
        row.prop(bpy.context.material, "bin_shader_unk3")

        box = self.layout.box()
        box.label(text="Unknown Settings", icon="QUESTION")
        row = box.row()
        row.prop(bpy.context.material, "bin_shader_metadata")

wrap_modes = ['CLAMP', 'REPEAT', 'MIRROR']

bin_mat_wrap_modes = [
    ("CLAMP", "Clamp", "", 0),
    ("REPEAT", "Repeat", "", 1),
    ("MIRROR", "Mirror", "", 2),
]

primitive_types = ['TRIANGLES', 'TRIANGLESTRIP', 'TRIANGLEFAN', 'QUADS', 'POINTS', 'LINES']
primitive_types = [
    ("TRIANGLES", "Triangles", "", 0),
    ("TRIANGLESTRIP", "Triangle Strips", "", 1),
    ("TRIANGLEFAN", "Triangle Fans", "", 2),
    ("QUADS", "Quads", "", 3),
    ("POINTS", "Points", "", 4),
    ("LINES", "Lines", "", 5),
]

supported_tex_types = [
    ("CMPR", "CMPR", "", 0),
    ("RGB565", "RGB565", "", 1),
    ("RGB5A3", "RGB5A3", "", 2),
    ("I4", "I4", "", 3),
]


bpy.utils.register_class(GraphNodeSettingsPanel) #must be registered here
bpy.types.Object.batch_use_normals = bpy.props.BoolProperty(name="Use Normals", default=True)
bpy.types.Object.batch_use_nbt= bpy.props.BoolProperty(name="Use NBT", default=False)
bpy.types.Object.batch_use_positions = bpy.props.IntProperty(name="Use Positions",min=0,max=255,default=2)
bpy.types.Object.batch_primitive_type = bpy.props.EnumProperty(name="Primitive Type",items=primitive_types,default="TRIANGLES")
bpy.types.Object.bin_render_cast_shadow = bpy.props.BoolProperty(name="Cast Shadow", default=True)
bpy.types.Object.bin_render_fourthwall = bpy.props.BoolProperty(name="Fourth Wall", default=False)
bpy.types.Object.bin_render_transparent = bpy.props.BoolProperty(name="Transparent", default=False)
bpy.types.Object.bin_render_rf16 = bpy.props.BoolProperty(name="RF16", default=False)
bpy.types.Object.bin_render_rf32 = bpy.props.BoolProperty(name="RF32", default=False)
bpy.types.Object.bin_render_fullbright = bpy.props.BoolProperty(name="Full Bright", default=False)
bpy.types.Object.bin_render_ceiling = bpy.props.BoolProperty(name="Ceiling", default=False)
bpy.types.Material.bin_wrap_mode_u = bpy.props.EnumProperty(name="Wrap U",items=bin_mat_wrap_modes,default="REPEAT")
bpy.types.Material.bin_wrap_mode_v = bpy.props.EnumProperty(name="Wrap V",items=bin_mat_wrap_modes,default="REPEAT")
bpy.types.Material.bin_shader_tint = bpy.props.FloatVectorProperty(name="Tint",subtype="COLOR",size=4,min=0.0,max=1.0,default=(1.0, 1.0, 1.0, 1.0))

bpy.types.Material.bin_shader_unk1 = bpy.props.IntProperty(name="Mat Unknown 1",min=-1,max=255,default=1)
bpy.types.Material.bin_shader_unk2 = bpy.props.IntProperty(name="Mat Unknown 2",min=-1,max=255,default=1)
bpy.types.Material.bin_shader_unk3 = bpy.props.IntProperty(name="Mat Unknown 3",min=-1,max=255,default=0)

bpy.types.Material.bin_shader_metadata = bpy.props.IntVectorProperty(name="Material Mystery", size=7, default=(0,0,0,0,0,0,0))


bpy.types.Material.gx_img_type = bpy.props.EnumProperty(name="Texture Format", items=supported_tex_types)

#actual model loading stuff

class bin_model_import():
    def __init__(self, pth):
        self.name = os.path.basename(pth)
        stream = bStream(path=pth)
        stream.seek(1)
        name = stream.readString(len=11)
        self.offsets = [stream.readUInt32() for offset in range(21)]

        stream.seek(self.offsets[2])
        
        no = 4
        v_count = int((self.offsets[3] - self.offsets[2]) / 6) #0
        while v_count <= 0:
            v_count = int((self.offsets[no] - self.offsets[2]) / 6)
            no += 1

        n_count = int((self.offsets[6] - self.offsets[3]) / 12)
        tc0_count = int(((self.offsets[10] if self.offsets[7] == 0 else self.offsets[7]) - self.offsets[6]) / 8)#/8
        tc1_count = int((self.offsets[10] - self.offsets[7]) / 8)#/8
        shader_count = int((self.offsets[11] - self.offsets[10]) / 0x28)

        self.verts = []
        for x in range(v_count):
            t = [stream.readInt16(), stream.readInt16(), stream.readInt16()]
            self.verts.append([t[0], -t[2], t[1]])

        stream.seek(self.offsets[3])
        self.normals = []
        for x in range(n_count):
            t = [stream.readFloat(), stream.readFloat(), stream.readFloat()]
            self.normals.append([t[0], -t[2], t[1]])



        self.materials = [self.readShader(stream, x) for x in range(shader_count)]
        stream.seek(self.offsets[6])
        self.texcoords0 = [[stream.readFloat(), stream.readFloat()] for x in range(tc0_count)]

        if(self.offsets[7] != 0):
            stream.seek(self.offsets[7])
            self.texcoords1 = [[stream.readFloat(), stream.readFloat()] for x in range(tc1_count)]
        
        self.readGraphObjects(stream, 0, None, name)

    def readGraphObjects(self, stream, index, root, name=None):
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
        print(f"Part Count on read: {part_count}")
        stream.readUInt16() #Padding
        part_offset = stream.readInt32()
        
        stream.seek(part_offset + self.offsets[12])
        parts = [[stream.readInt16(), stream.readInt16()] for x in range(part_count)]
        
        cur_obj = bpy.data.objects.new('Graph_Obj{0}'.format(index) if name == None else name, None)
        #cur_obj.bin_render_flags = render_flags 


        cur_obj.bin_render_cast_shadow = (render_flags & (1 << 1)) != 0 
        cur_obj.bin_render_fourthwall = (render_flags & (1 << 2)) != 0
        cur_obj.bin_render_transparent = (render_flags & (1 << 3)) != 0 
        cur_obj.bin_render_rf16 = (render_flags & (1 << 4)) != 0
        cur_obj.bin_render_rf32 = (render_flags & (1 << 5)) != 0
        cur_obj.bin_render_fullbright = (render_flags & (1 << 6)) != 0
        cur_obj.bin_render_ceiling = (render_flags & (1 << 7)) != 0

        cur_obj.parent = root
        cur_obj.location = pos
        cur_obj.rotation_euler = (math.degrees(rot[0] * 0.001523), -math.degrees(rot[2] * 0.001523), math.degrees(rot[1] * 0.001523))
        cur_obj.scale = scale
        bpy.context.scene.collection.objects.link(cur_obj)

        for part in parts:
            
            batch = self.readBatch(stream, part[1])
            material = self.materials[part[0]]
            
            mesh = bpy.data.meshes.new('Batch_{0}'.format(part[1]))
            mesh.calc_normals_split()

            #mesh.use_auto_smooth = True
            mesh.from_pydata(self.verts, [], [[vtx.vertex for vtx in tri] for tri in batch[0]])


            bm = bmesh.new()
            bm.from_mesh(mesh)
            duv = bm.loops.layers.uv.new("UVMap_Diffuse")
            buv = bm.loops.layers.uv.new("UVMap_Bump")
            imported_normals = bm.loops.layers.float_vector.new("imported_normals")
            
            face_idx = 0
            for face in bm.faces:
                for vtx in range(3):
                    loop = face.loops[vtx]

                    loop[duv].uv = self.texcoords0[batch[0][face_idx][vtx].uv]
                    if(batch[0][face_idx][vtx].uv1 != -1):
                        loop[buv].uv = self.texcoords1[batch[0][face_idx][vtx].uv1]

                    if(batch[0][face_idx][vtx].normal != -1):
                        loop[imported_normals] = self.normals[batch[0][face_idx][vtx].normal]

                face_idx+=1

            
            bm.to_mesh(mesh)
            bm.free()

            mesh.materials.append(material)
            mesh.update()

            batch_obj = bpy.data.objects.new('Batch_{0}'.format(part[1]), mesh)
            batch_obj.batch_use_normals = batch[1]
            batch_obj.batch_use_positions = batch[2]
            batch_obj.batch_use_nbt = batch[3]
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
        mat = bpy.data.materials.new("BinMaterial_{}".format(index))
        mat.bin_shader_unk1 = stream.readUInt8()
        mat.bin_shader_unk2 = stream.readUInt8()
        mat.bin_shader_unk3 = stream.readUInt8()
        tint = stream.readUInt32()
        stream.readUInt8()

        mat.bin_shader_tint = [(tint & 0xFF) / 255.0, (tint & 0x00FF) / 255.0, (tint & 0x0000FF) / 255.0, (tint & 0x000000FF) / 255.0]

        tex_indices = [stream.readUInt16() for x in range(8)]
        self.readMaterial(stream, tex_indices[0], mat, False)
        for tex in tex_indices[1:]:
            if(tex != -1):
                self.readMaterial(stream, tex, mat, True)

        return mat
        
    def readMaterial(self, stream, index, mat, isBump):
        if(index >= 0 and index < 100):
            stream.seek(self.offsets[1] + (0x14 * index))
            #print("Reading Material at {0:X}".format(self.offsets[1] + (0x14 * index)))
            mat.use_nodes = True
            mat_tree = mat.node_tree
            texIndex = stream.readInt16()
            stream.readUInt16()
            u = stream.readUInt8()
            v = stream.readUInt8()

            if(u == 0):
                mat.bin_wrap_mode_u = 'CLAMP'
            elif(u == 2):
                mat.bin_wrap_mode_u = 'MIRROR'
            else:
                mat.bin_wrap_mode_u = 'REPEAT'

            if(v == 0):
                mat.bin_wrap_mode_v = 'CLAMP'
            elif(v == 2):
                mat.bin_wrap_mode_v = 'MIRROR'
            else:
                mat.bin_wrap_mode_v = 'REPEAT'

            print(f"{mat.name}: {mat.bin_wrap_mode_u}, {mat.bin_wrap_mode_v}")

            texture_node = mat_tree.nodes.new("ShaderNodeTexImage")
            texture_node.image = self.readTexture(stream, texIndex, mat)

            bsdf = mat_tree.nodes.get('Principled BSDF')
            if(not isBump):
                texture_node.label = "BinTexture"
                mat_tree.links.new(texture_node.outputs[0], bsdf.inputs[0])
            else:
                #TODO: make this more accurate to the game.
                disp = mat_tree.nodes.new("ShaderNodeDisplacement")
                texture_node.label = "BinBumpTexture"
                texture_node.interpolation = 'Cubic' #?
                mat_tree.links.new(texture_node.outputs[0], disp.inputs[0])
                mat_tree.links.new(disp.outputs[0], mat_tree.nodes.get('Material Output').inputs[2])
                pass

            for x in range(7):
                mat.bin_shader_metadata[x] = stream.readUInt16()
            

    def readTexture(self, stream, index, mat):
        stream.seek(self.offsets[0] + (0xC * index))
        width = stream.readUInt16()
        height = stream.readUInt16()
        format = stream.readInt8()
        stream.readUInt8()
        stream.readUInt16()
        offset = stream.readUInt32()
        if(format == 0x0E):
            mat.gx_img_type = 'CMPR'
            return gx_texture.bi_from_cmpr(stream, width, height, self.offsets[0] + offset, index)
        elif(format == 0x05):
            mat.gx_img_type = 'RGB5A3'
            return gx_texture.bi_from_rgb5A3(stream, width, height, self.offsets[0] + offset, index)      
        elif(format == 0x04):
            mat.gx_img_type = 'RGB565'
            return gx_texture.bi_from_rgb565(stream, width, height, self.offsets[0] + offset, index) 
        elif(format == 0x00):
            mat.gx_img_type = 'I4'
            return gx_texture.bi_from_i4(stream, width, height, self.offsets[0] + offset, index) 
        else:
            print(f"Unsupported format {hex(format)}!")

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
        
        print(attribs)
        
        use_normals = bool(stream.readUInt8()) # normals
        use_positions = stream.readUInt8() # positions
        print(f"uvs count is #{stream.readUInt8()}") # uvs
        nbt = bool(stream.readUInt8()) # nbt
        primitive_offset = stream.readUInt32()
        stream.seek(self.offsets[11]+primitive_offset)
        list_size += (primitive_offset+self.offsets[11])
        verts = self.readPrimitives(stream, attribs, list_size, total_verts, nbt)
        
        return (verts, use_normals, use_positions, nbt)
    
    def readAttrib(self, stream, nbt, attrib):
        if(nbt and attrib == GXAttribute.Normal):
            r = stream.readInt16()
            stream.readInt16()
            stream.readInt16()
            return r

        else:
            return stream.readInt16()


    def readPrimitives(self, stream, attribs, size, total_verts, nbt):
        gxprimitives = [] #stores raw element buffers

        triangulated = []
        
        #print(f'Reading primitve with attribs {attributes}')
        current_primitive = stream.readUInt8()

        # read the primitives
        while(GXPrimitiveTypes.valid_opcode(current_primitive) and stream.fhandle.tell() < size):
            gxprimitives.append((
                [[self.readAttrib(stream, nbt, attribs[y]) for y in range(len(attribs))] for x in range(stream.readUInt16())],
                current_primitive    
            ))
            current_primitive = stream.readUInt8()
        
        # create verts list
        for primitive in gxprimitives:    
            triangulated.extend(to_triangles_gxverts([GXVertex(vertex[attribs.index(GXAttribute.Position)], -1 if GXAttribute.Normal not in attribs else vertex[attribs.index(GXAttribute.Normal)], (vertex[attribs.index(GXAttribute.Tex0)] if GXAttribute.Tex0 in attribs else -1), (vertex[attribs.index(GXAttribute.Tex1)] if GXAttribute.Tex1 in attribs else -1)) for vertex in primitive[0]], primitive[1]))


        return triangulated

class bin_model_export():
    def __init__(self, pth, compat):
        root = bpy.context.selected_objects[0]
        
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
        
        if(len(root.name) < 11):
            out.writeString(root.name + (" " * (11 - len(root.name))))
        else:
            out.writeString(root.name[0:11])

        out.writeUInt32List(offsets)

        offsets[0] = out.tell()
        self.textures.writeTextures(out)
        if(compat): #pad after textures
            out.padTo32(out.tell())

        offsets[1] = out.tell()
        self.textures.writeMaterials(out)
        if(compat): # pad after materials
            out.padTo32(out.tell())

        offsets[2] = out.tell()
        for vertex in self.batches.mesh_data['vertex']:
            out.writeInt16(int(vertex[0]))
            out.writeInt16(int(vertex[2]))
            out.writeInt16(int(-vertex[1]))
        
        if(compat): # pad after vertices
            out.padTo32(out.tell())
    
        offsets[3] = out.tell()
        for normal in self.batches.mesh_data['normal']:
            out.writeFloat(normal[0])
            out.writeFloat(normal[2])
            out.writeFloat(-normal[1])

        if(compat): #pad after normals
            out.padTo32(out.tell())

        offsets[6] = out.tell()
        for uv in self.batches.mesh_data['uv']:
            out.writeFloat(uv[0])
            out.writeFloat(-uv[1])

        if(compat): #pad after uv1
            out.padTo32(out.tell())
            
        if(len(self.batches.mesh_data['uv1']) > 0):
            offsets[7] = out.tell()
            for uv in self.batches.mesh_data['uv1']:
                out.writeFloat(uv[0])
                out.writeFloat(-uv[1])

        if(compat): #pad after uvs
            out.padTo32(out.tell())


        offsets[10] = out.tell()
        self.shaders.writeShaders(out)
        if(compat): #pad after shaders
            out.padTo32(out.tell())


        offsets[11] = out.tell()
        self.batches.write(out)
        if(compat): #pad after batches
            out.padTo32(out.tell())

        offsets[12] = out.tell()

        out.pad(0x8C*len(graph_nodes))
        for node in graph_nodes:
            node['part_offset'] = out.tell() - offsets[12]
            print(f"Writing part count: {len(node['parts'])}")
            for part in node['parts']:
                print(f"Writing Node {node['my_index']} Part: {part} at offset {out.tell():x}")
                out.writeInt16(part[1])
                out.writeInt16(part[0])
        
        if(compat): #Pad after scenegraph
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
                if(child not in self.meshes_used):
                    self.meshes_used.append(child)
                if(child.active_material not in self.materials_used):
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
            'render_flags' : 0,
            'scale' : [obj.scale[0], obj.scale[1], obj.scale[2]],
            'rotation' : [math.radians(obj.rotation_euler[0])/0.001523, math.radians(obj.rotation_euler[2])/0.001523, -math.radians(obj.rotation_euler[1])/0.001523],
            'position' : [obj.location[0], obj.location[2], -obj.location[1]],
            'part_count': 0,
            'parts':[],
            'part_offset': 0
        }


        node['render_flags'] |= (obj.bin_render_cast_shadow << 1) 
        node['render_flags'] |= (obj.bin_render_fourthwall << 2)
        node['render_flags'] |= (obj.bin_render_transparent << 3) 
        node['render_flags'] |= (obj.bin_render_rf16 << 4)
        node['render_flags'] |= (obj.bin_render_rf32 << 5)
        node['render_flags'] |= (obj.bin_render_fullbright << 6)
        node['render_flags'] |= (obj.bin_render_ceiling << 7)

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
