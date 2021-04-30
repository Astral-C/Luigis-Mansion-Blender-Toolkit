import math
import numpy as np
from bStream import *
import time

class GXVertex():
    def __init__(self, vertex, normal, uv):
        self.vertex = vertex
        self.normal = normal
        self.uv = uv

def GeneratePrimitives(mesh, buffer, nbt, mesh_data):
    start = time.time()
    normal_offset = 0
    uv_map = mesh.uv_layers.active.data
    for polygon in mesh.polygons:
        buffer.writeUInt8(0x90)
        buffer.writeUInt16(3)
        for idx in range(3):
            loop = mesh.loops[polygon.loop_indices[idx]]

            uv = uv_map[polygon.loop_indices[idx]].uv
            vertex = mesh.vertices[loop.vertex_index].co
            normal = mesh.vertices[loop.vertex_index].normal
            vi = -1
            uvi = -1
            noi = -1
            if(uv in mesh_data['uv']):
                uvi = mesh_data['uv'].index(uv)
            else:
                uvi = len(mesh_data['uv'])
                mesh_data['uv'].append(uv)

            if(vertex in mesh_data['vertex']):
                vi = mesh_data['vertex'].index(vertex)
            else:
                vi = len(mesh_data['vertex'])
                mesh_data['vertex'].append(vertex)

            if(normal in mesh_data['normal']):
                noi = mesh_data['normal'].index(normal)
            else:
                noi = len(mesh_data['normal'])
                mesh_data['normal'].append(normal)

            buffer.writeUInt16(vi) # vertex
            buffer.writeUInt16(noi) # normal
            buffer.writeUInt16(uvi)

    end = time.time()
    print(f"Generated batch for {mesh.name} in {end-start} seconds")

def GenerateTristripPrimitives(mesh, buffer, nbt, mesh_data):
    normal_offset = 0
    uv_map = mesh.uv_layers.active.data
    for polygon in mesh.polygons:
        buffer.writeUInt8(0x98)
        buffer.writeUInt16(len(polygon.loop_indices))

        for l in polygon.loop_indices:
            loop = mesh.loops[l]

            uv = uv_map[l].uv
            vertex = mesh.vertices[loop.vertex_index].co
            normal = mesh.vertices[loop.vertex_index].normal
            vi = -1
            uvi = -1
            noi = -1
            if(uv in mesh_data['uv']):
                uvi = mesh_data['uv'].index(uv)
            else:
                uvi = len(mesh_data['uv'])
                mesh_data['uv'].append(uv)

            if(vertex in mesh_data['vertex']):
                vi = mesh_data['vertex'].index(vertex)
            else:
                vi = len(mesh_data['vertex'])
                mesh_data['vertex'].append(vertex)

            if(normal in mesh_data['normal']):
                noi = mesh_data['normal'].index(normal)
            else:
                noi = len(mesh_data['normal'])
                mesh_data['normal'].append(normal)

            buffer.writeUInt16(vi) # vertex
            buffer.writeUInt16(noi) # normal
            buffer.writeUInt16(uvi)

class BatchManager():
    def __init__(self, meshes, use_tristrips, use_bump=False):
        total = 0
        
        self.batches = []
        self.batch_indices = {}
        self.mesh_data = {'vertex':[], 'normal':[], 'uv':[]}

        #To ensure that vertices are in the right order, we build the vertex/texcoord/normal lists here
        
        cur_batch = 0 
        for mesh in meshes:
            m = mesh.to_mesh()

            self.batches.append(Batch(m, use_bump, self.mesh_data, mesh.batch_use_normals, mesh.batch_use_positions, use_tristrips))
            self.batch_indices[m.name] = cur_batch

            cur_batch += 1
            print(f"Added Batch for mesh {m.name} with index {cur_batch}")

    def getBatchIndex(self, name):
        #print(f"Asked for batch {name}")
        if(name in self.batch_indices):
            return self.batch_indices[name]
        else:
            return -1

    def write(self, stream):
        batch_headers = bStream()
        primitive_buffer = bStream()
        
        batch_headers.pad((0x18 * len(self.batches)))
        primitives_start = batch_headers.tell()
        batch_headers.seek(0)

        for batch in self.batches:
            list_start = primitive_buffer.tell()
            primitive_buffer.write(batch.primitives.fhandle.read())
            list_end = primitive_buffer.tell()
            batch.writeHeader(batch_headers, math.ceil((list_end - list_start)/32), list_start + primitives_start)

        batch_headers.seek(0)
        primitive_buffer.seek(0)
        stream.write(batch_headers.fhandle.read())
        stream.write(primitive_buffer.fhandle.read())
        batch_headers.close()
        primitive_buffer.close()

class Batch():
    def __init__(self, mesh, nbt, mesh_data, use_normals, use_positions, use_tristrips):

        self.face_count = len(mesh.polygons) #Isnt used by the game so, not important really
        self.attributes = (0 | 1 << 9 | 1 << 10 | 1 << 13)
        self.primitives = bStream()
        self.useNBT = nbt
        self.use_normals = use_normals
        self.use_positions = use_positions

        if(use_tristrips):
            GenerateTristripPrimitives(mesh, self.primitives, self.useNBT, mesh_data)
        else:
            GeneratePrimitives(mesh, self.primitives, self.useNBT, mesh_data)
        
        self.primitives.padTo32(self.primitives.tell())
        self.primitives.seek(0)

    def writeHeader(self, stream, list_size, offset):
        stream.writeUInt16(self.face_count)
        stream.writeUInt16(list_size)
        stream.writeUInt32(self.attributes)
        stream.writeUInt8(self.use_normals) # Use Normals
        stream.writeUInt8(self.use_positions) # Use Positions. Sometimes its 2?????
        stream.writeUInt8(1) # Uv Count
        stream.writeUInt8(0) # Use NBT
        stream.writeUInt32(offset)
        stream.pad(8)

    def __del__(self):
        if(self.primitives is not None):
            self.primitives.close()

