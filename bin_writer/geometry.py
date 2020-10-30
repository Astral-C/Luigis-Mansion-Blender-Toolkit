import math
import numpy as np
from bStream import *

def GeneratePrimitives(mesh, buffer, nbt, start, uvs):
    normal_offset = 0
    uv_map = mesh.uv_layers.active.data
    for polygon in mesh.polygons:
        buffer.writeUInt8(0x90)
        buffer.writeUInt16(3)
        
        for idx in range(3):

            loop = mesh.loops[polygon.loop_indices[idx]]
            
            buffer.writeUInt16(start + loop.vertex_index) # vertex
            buffer.writeUInt16(start + loop.vertex_index + normal_offset) # normal
            
            # Disabled until I can find a good way to solve the indexing problem
            #if(nbt):
            #    buffer.writeUInt16(start + loop.vertex_index + normal_offset + 1) # bitangent
            #    buffer.writeUInt16(start + loop.vertex_index + normal_offset + 2) # tangent
            #    mesh_data['normals'][start + loop.vertex_index + normal_offset + 1] = polygon.bitangent
            #    mesh_data['normals'][start + loop.vertex_index + normal_offset + 2] = polygon.tangent
            #    normal_offset += 2
            uvs.append([uv_map[polygon.loop_indices[idx]].uv[0], uv_map[polygon.loop_indices[idx]].uv[1]])
            buffer.writeUInt16(len(uvs)-1) # texcoord Index


def GenerateTristripPrimitives(mesh, buffer, nbt, start):
    normal_offset = 0
    previous_edges = []
    #for polygon in mesh.polygons:
    #    for 

class BatchManager():
    def __init__(self, meshes, use_bump=False):
        total = 0
        
        self.batches = []
        self.batch_indices = {}
        self.texcoord_data = []

        #To ensure that vertices are in the right order, we build the vertex/texcoord/normal lists here
        
        cur_batch = 0 
        for mesh in meshes:
            m = mesh.to_mesh()
            #m.calc_tangents() #make sure we have tangent data
            #self.texcoord_data.extend([[0, 0] for x in range(len(m.vertices))])
            self.batches.append(Batch(m, total, use_bump, self.texcoord_data, mesh.batch_use_normals, mesh.batch_use_positions))
            self.batch_indices[m.name] = cur_batch
            total += len(m.vertices)
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
        batch_headers.padTo32(batch_headers.tell())
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
    def __init__(self, mesh, start, nbt, uvs, use_normals, use_positions):

        self.face_count = len(mesh.polygons) #Isnt used by the game so, not important really
        self.attributes = (0 | 1 << 9 | 1 << 10 | 1 << 13)
        self.primitives = bStream()
        #SpaceCats: I dont like this, nbt should only be on where its used.
        #TODO: Find a way to only enable nbt on only meshes that use it
        self.useNBT = nbt
        self.use_normals = use_normals
        self.use_positions = use_positions
        GeneratePrimitives(mesh, self.primitives, self.useNBT, start, uvs)
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

