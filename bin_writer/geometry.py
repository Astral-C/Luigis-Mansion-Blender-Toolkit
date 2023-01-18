import math
import numpy as np
from bStream import *
import time
#from triangle_strip import find_strip
from pyffi.tristrip import stripify, GXVertex
from copy import deepcopy

def GeneratePrimitives(mesh, buffer, nbt, nenabled, mesh_data):
    start = time.time()
    normal_offset = 0
    uv_map_diffuse = mesh.uv_layers["UVMap_Diffuse"].data
    uv_map_bump = mesh.uv_layers["UVMap_Bump"].data

    buffer.writeUInt8(0x90)
    buffer.writeUInt16(len(mesh.polygons)*3)
    for polygon in mesh.polygons:
        for idx in range(3):
            loop = mesh.loops[polygon.loop_indices[idx]]

            duv = uv_map_diffuse[polygon.loop_indices[idx]].uv
            buv = uv_map_bump[polygon.loop_indices[idx]].uv

            vertex = mesh.vertices[loop.vertex_index].co
            normal = mesh.vertices[loop.vertex_index].normal #mesh.vertices[mesh.loops[polygon.loop_indices[idx]].vertex_index].co.cross(mesh.vertices[mesh.loops[polygon.loop_indices[(idx + 1) % 3]].vertex_index].co).cross(mesh.vertices[mesh.loops[polygon.loop_indices[(idx + 2) % 3]].vertex_index].co) #mesh.vertices[loop.vertex_index].normal
            binormal = loop.bitangent
            tangent = loop.tangent

            vi = -1
            duvi = -1
            buvi = -1
            noi = -1
            bni = -1
            ti = -1

            if(duv in mesh_data['uv']):
                duvi = mesh_data['uv'].index(duv)
            else:
                duvi = len(mesh_data['uv'])
                mesh_data['uv'].append(duv)

            if(nbt):
                if(buv in mesh_data['uv1']):
                    buvi = mesh_data['uv1'].index(buv)
                else:
                    buvi = len(mesh_data['uv1'])
                    mesh_data['uv1'].append(buv)       

            if(vertex in mesh_data['vertex']):
                vi = mesh_data['vertex'].index(vertex)
            else:
                vi = len(mesh_data['vertex'])
                mesh_data['vertex'].append(vertex)

            if (nenabled):
                if(normal in mesh_data['normal']):
                    noi = mesh_data['normal'].index(normal)

                else:
                    noi = len(mesh_data['normal'])
                    mesh_data['normal'].append(normal)

                if(nbt):
                    if(binormal in mesh_data['normal']):
                        bni = mesh_data['normal'].index(binormal)

                    else:
                        bni = len(mesh_data['normal'])
                        mesh_data['normal'].append(binormal)

                    if(tangent in mesh_data['normal']):
                        ti = mesh_data['normal'].index(tangent)

                    else:
                        ti = len(mesh_data['normal'])
                        mesh_data['normal'].append(tangent)


            buffer.writeUInt16(vi) # vertex
            if(nenabled):
                buffer.writeUInt16(noi) # normal
                if(nbt):
                    buffer.writeUInt16(bni)
                    buffer.writeUInt16(ti)
            buffer.writeUInt16(duvi)
            if(nbt):
                buffer.writeUInt16(buvi)

    end = time.time()
    print(f"Generated triangles batch for {mesh.name} in {end-start} seconds")

def GenerateQuadPrimitives(mesh, buffer, nbt, nenabled, mesh_data):
    start = time.time()
    normal_offset = 0
    uv_map = mesh.uv_layers.active.data

    #mesh.calc_normals_split()

    buffer.writeUInt8(0x80)
    buffer.writeUInt16(len(mesh.polygons)*4)
    for polygon in mesh.polygons:
        for idx in range(4):
            loop = mesh.loops[polygon.loop_indices[idx]]

            uv = uv_map[polygon.loop_indices[idx]].uv
            vertex = mesh.vertices[loop.vertex_index].co
            normal = mesh.vertices[loop.vertex_index].normal
            print('vertex normal at is :', normal)
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

            if (nenabled):
                if(normal in mesh_data['normal']):
                    noi = mesh_data['normal'].index(normal)
                else:
                    noi = len(mesh_data['normal'])
                    mesh_data['normal'].append(normal)

            buffer.writeUInt16(vi) # vertex
            if(nenabled):
                buffer.writeUInt16(noi) # normal
            buffer.writeUInt16(uvi)

    end = time.time()
    print(f"Generated quad batch for {mesh.name} in {end-start} seconds")

def GenerateTrifanPrimitives(mesh, buffer, nbt, nenabled, mesh_data):
    start = time.time()
    normal_offset = 0
    uv_map = mesh.uv_layers.active.data

    buffer.writeUInt8(0xA0)
    buffer.writeUInt16(len(mesh.loops))
    for loop in mesh.loops:
        uv = uv_map[polygon.loop_indices[idx]].uv
        vertex = mesh.vertices[loop.vertex_index].co
        normal = polygon.normal#mesh.vertices[mesh.loops[polygon.loop_indices[idx]].vertex_index].co.cross(mesh.vertices[mesh.loops[polygon.loop_indices[(idx + 1) % 3]].vertex_index].co).cross(mesh.vertices[mesh.loops[polygon.loop_indices[(idx + 2) % 3]].vertex_index].co) #mesh.vertices[loop.vertex_index].normal

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

        if (nenabled):
            if(normal in mesh_data['normal']):
                noi = mesh_data['normal'].index(normal)

            else:
                noi = len(mesh_data['normal'])
                mesh_data['normal'].append(normal)

        buffer.writeUInt16(vi) # vertex
        if(nenabled):
            buffer.writeUInt16(noi) # normal
        buffer.writeUInt16(uvi)

    end = time.time()
    print(f"Generated trifan batch for {mesh.name} in {end-start} seconds")

def GeneratePointsPrimitives(mesh, buffer, nbt, nenabled, mesh_data):
    print(f"points polycount is {len(mesh.loops)}")
    start = time.time()
    normal_offset = 0
    uv_map = mesh.uv_layers.active.data

    buffer.writeUInt8(0xB8)
    buffer.writeUInt16(len(mesh.loops))
    for loop in mesh.loops:
        uv = uv_map[loop.index].uv
        vertex = mesh.vertices[loop.vertex_index].co
        normal = polygon.normal #mesh.vertices[mesh.loops[polygon.loop_indices[idx]].vertex_index].co.cross(mesh.vertices[mesh.loops[polygon.loop_indices[(idx + 1) % 3]].vertex_index].co).cross(mesh.vertices[mesh.loops[polygon.loop_indices[(idx + 2) % 3]].vertex_index].co) #mesh.vertices[loop.vertex_index].normal
        
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

        if (nenabled):
            if(normal in mesh_data['normal']):
                noi = mesh_data['normal'].index(normal)

            else:
                noi = len(mesh_data['normal'])
                mesh_data['normal'].append(normal)

        buffer.writeUInt16(vi) # vertex
        if(nenabled):
            buffer.writeUInt16(noi) # normal
        buffer.writeUInt16(uvi)

    end = time.time()
    print(f"Generated points batch for {mesh.name} in {end-start} seconds")

def GenerateLinesPrimitives(mesh, buffer, nbt, nenabled, mesh_data):
    print(f"line strip polycount is {len(mesh.loops)}")
    start = time.time()
    normal_offset = 0
    uv_map = mesh.uv_layers.active.data

    used_edges = []
    vtx_count = 0

    buffer.writeUInt8(0xA8)
    vtx_count_loc = buffer.tell()
    buffer.writeUInt16(0)

    for loop in mesh.loops:
        if(loop.edge_index in used_edges):
            continue
        else:
            vtx_count += 2
            edge = mesh.edges[loop.edge_index]
            uv = uv_map[loop.index].uv
            vertex = mesh.vertices[edge.vertices[0]].co
            vertex2 = mesh.vertices[edge.vertices[1]].co
            normal = polygon.normal
 
            vi = -1
            vi2 = -1
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

            if(vertex2 in mesh_data['vertex']):
                vi2 = mesh_data['vertex'].index(vertex2)
            else:
                vi2 = len(mesh_data['vertex'])
                mesh_data['vertex'].append(vertex2)

            if (nenabled):
                if(normal in mesh_data['normal']):
                    noi = mesh_data['normal'].index(normal)
                else:
                    noi = len(mesh_data['normal'])
                    mesh_data['normal'].append(normal)

            buffer.writeUInt16(vi) # vertex
            if(nenabled):
                buffer.writeUInt16(noi) # normal
            buffer.writeUInt16(uvi)

            buffer.writeUInt16(vi2) # vertex
            if(nenabled):
                buffer.writeUInt16(noi) # normal
            buffer.writeUInt16(uvi)

    ret = buffer.tell()
    buffer.seek(vtx_count_loc)
    buffer.writeUInt16(vtx_count)
    buffer.seek(ret)
    
    end = time.time()
    print(f"Generated line strip batch for {mesh.name} in {end-start} seconds")

def GenerateTristripPrimitives(mesh, buffer, nbt, nenabled, mesh_data):
    normal_offset = 0
    uv_map = mesh.uv_layers.active.data

    #generate strip
    
    faces = []

    for polygon in mesh.polygons:
        tri = []
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

            tri.append(GXVertex(vi, noi, uvi))
        faces.append(tri)


    print("Looking for strips...")
    strips = stripify(faces)
    print(f"Strip Data {strips}")
    

    for strip in strips:
        buffer.writeUInt8(0x98)
        buffer.writeUInt16(len(strip))
        for tri in strip:
            buffer.writeUInt16(tri.vertex) # vertex
            if(nenabled):
                buffer.writeUInt16(tri.normal) # normal
            buffer.writeUInt16(tri.uv)

    print(f"Generated tristrips batch")

class BatchManager():
    def __init__(self, meshes, use_bump=False):
        total = 0
        
        self.batches = []
        self.batch_indices = {}
        self.mesh_data = {'vertex':[], 'normal':[], 'uv':[], 'uv1':[]}

        #To ensure that vertices are in the right order, we build the vertex/texcoord/normal lists here
        
        cur_batch = 0 
        for mesh in meshes:
            m = mesh.to_mesh()

            if(mesh.batch_use_nbt):
                m.calc_tangents(uvmap="UVMap_Bump")

            self.batches.append(Batch(m, mesh.batch_use_nbt, self.mesh_data, mesh.batch_use_normals, mesh.batch_use_positions, mesh.batch_primitive_type))
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
    def __init__(self, mesh, nbt, mesh_data, use_normals, use_positions, primitive_type):

        self.face_count = len(mesh.polygons) #Isnt used by the game so, not important really
        self.attributes = (0 | 1 << 9 | (1 << 10 if use_normals else 0) | 1 << 13 | (1 << 14 if nbt else 0))
        self.primitives = bStream()
        self.useNBT = nbt
        self.use_normals = use_normals
        self.use_positions = use_positions

        primitive_types = ['TRIANGLES', 'TRIANGLESTRIP', 'TRIANGLEFAN', 'QUADS', 'POINTS', 'LINES']
        primitive_type = primitive_types.index(primitive_type)
        print(f"Primitive Type is {primitive_type}")

        if(nbt):
            primitive_type = 0

        if(primitive_type == 0):
            GeneratePrimitives(mesh, self.primitives, self.useNBT, use_normals, mesh_data)
        elif(primitive_type == 1):
            GenerateTristripPrimitives(mesh, self.primitives, self.useNBT, use_normals, mesh_data)
        elif(primitive_type == 2):
            GenerateTrifanPrimitives(mesh, self.primitives, self.useNBT, use_normals, mesh_data)
        elif(primitive_type == 3):
            GenerateQuadPrimitives(mesh, self.primitives, self.useNBT, use_normals, mesh_data)
        elif(primitive_type == 4):
            GeneratePointsPrimitives(mesh, self.primitives, self.useNBT, use_normals, mesh_data)
        elif(primitive_type == 5):
            GenerateLinesPrimitives(mesh, self.primitives, self.useNBT, use_normals, mesh_data)
        else:
            GeneratePrimitives(mesh, self.primitives, self.useNBT, use_normals, mesh_data)
        
        self.primitives.padTo32(self.primitives.tell())
        self.primitives.seek(0)

    def writeHeader(self, stream, list_size, offset):
        stream.writeUInt16(self.face_count)
        stream.writeUInt16(list_size)
        stream.writeUInt32(self.attributes)
        stream.writeUInt8(self.use_normals) # Use Normals
        stream.writeUInt8(self.use_positions) # Use Positions. Sometimes its 2?????
        stream.writeUInt8(2 if self.useNBT else 1) # Uv Count
        stream.writeUInt8(self.useNBT) # Use NBT
        stream.writeUInt32(offset)
        stream.pad(8)

    def __del__(self):
        if(self.primitives is not None):
            self.primitives.close()

