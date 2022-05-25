import bpy
import bmesh
from bStream import *


def load_model(pth):
    stream = bStream(path=pth)
    stream.seek(0x24)
    vertex_offset = stream.readUInt32()
    normal_offset = stream.readUInt32()
    triangle_data_offset = stream.readUInt32()
    triangle_group_offset = stream.readUInt32()
    gridIndex_data_offset = stream.readUInt32()
    gridIndex_data_offset_dupe = stream.readUInt32()
    unkown_data_offset = stream.readUInt32()

    stream.seek(vertex_offset) #vertex data always here

    vertices = []

    for x in range(int((normal_offset - vertex_offset) / 0xC)):
        v = [stream.readFloat(), stream.readFloat(), stream.readFloat()]
        vertices.append([v[0], -v[2], v[1]])

    #stream.seek(normalOffset)
    #self.normals = [[stream.readFloat(), stream.readFloat(), stream.readFloat()] for x in range((triangleDataOffset - normalOffset) / 0xC)]

    #Read triangle data
    stream.seek(triangle_data_offset)
    triangles = [readTriangle(stream) for x in range(int((triangle_group_offset - triangle_data_offset) / 0x18))]

    mesh = bpy.data.meshes.new('col.mp')
    mesh.from_pydata(vertices, [], triangles)
    mesh.update()

    col_obj = bpy.data.objects.new('col.mp', mesh)        
    bpy.context.scene.collection.objects.link(col_obj)

def readTriangle(stream):
    v = [stream.readUInt16() for x in range(3)]
    n = stream.readUInt16()
    et = [stream.readUInt16() for x in range(3)]
    unk1 = stream.readUInt16()
    unkf = stream.readFloat()
    unkSet = [stream.readUInt16(), stream.readUInt16()]
    return v