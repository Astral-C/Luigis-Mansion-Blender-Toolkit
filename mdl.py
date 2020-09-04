import bpy
import bmesh
from bStream import *

class mdl_model():
    def __init__(self, pth):
        stream = bStream(path=pth)

        if(stream.readUInt32() != 0x04B40000):
            return

        self.face_count = stream.readUInt16()
        stream.readUInt16() # 2 byte padding
        self.graph_node_count = stream.readUInt16()
        self.packet_count = stream.readUInt16()
        self.weight_count = stream.readUInt16()
        self.joint_count = stream.readUInt16()
        self.position_count = stream.readUInt16()
        self.normal_count = stream.readUInt16()
        self.color_count = stream.readUInt16()
        self.texcoord_count = stream.readUInt16()
        stream.fhandle.read(8) # 8 bytes padding
        self.texture_count = stream.readUInt16()
        stream.readUInt16() # 2 bytes padding
        self.sampler_count = stream.readUInt16()
        self.draw_element_count = stream.readUInt16()
        self.material_count = stream.readUInt16()
        self.shape_count = stream.readUInt16()
        stream.readUInt32() # 4 bytes padding

        self.graph_node_offset = stream.readUInt32()
        self.packet_offset = stream.readUInt32()
        self.matrix_offset = stream.readUInt32()
        self.weight_offset = stream.readUInt32()
        self.joint_index_offset = stream.readUInt32()
        self.weight_table_offset = stream.readUInt32()
        self.position_offset = stream.readUInt32()
        self.normal_offset = stream.readUInt32()
        self.color_offset = stream.readUInt32()
        self.texcoord_offset = stream.readUInt32()
        stream.fhandle.read(8) # 8 bytes padding
        self.texture_array_offset = stream.readUInt32()
        stream.readUInt32() # 2 bytes padding
        self.material_offset = stream.readUInt32()
        self.sampler_offset = stream.readUInt32()
        self.shape_offset = stream.readUInt32()
        self.draw_element_offset = stream.readUInt32()
        stream.fhandle.read(8) # 8 bytes padding

        stream.seek(self.position_offset)
        self.raw_vertices = [stream.readVec3() for pos in range(self.position_count)]

        stream.seek(self.normal_offset)
        self.raw_normals = [stream.readVec3() for norm in range(self.normal_count)]

        stream.seek(self.color_offset)
        self.raw_colors = [[stream.readUInt8(), stream.readUInt8(), stream.readUInt8(), stream.readUInt8()] for col in range(self.color_count)]

        stream.seek(self.texcoord_offset)
        self.raw_texcoords = [[stream.readFloat(), stream.readFloat()] for coord in range(self.texcoord_count)]

        mesh = bpy.data.meshes.new(pth.split('/')[-1].split('.')[0])  # add a new mesh
        mesh.from_pydata(self.vertices, [], [])
        bm = bmesh.new()
        bm.from_mesh(mesh)



        # make the bmesh the object's mesh
        bm.to_mesh(mesh)  
        bm.free()  # always do this when finished
        
        mesh.update()

        mdl_obj = bpy.data.objects.new('mdl_obj', mesh)

        bpy.context.scene.collection.objects.link(mdl_obj)
        bpy.context.view_layer.objects.active = mdl_obj
        bpy.ops.object.mode_set(mode='EDIT')
        #bpy.ops.mesh.delete_loose()
        bpy.ops.object.mode_set(mode='OBJECT')


    def to_blender(self):
        pass