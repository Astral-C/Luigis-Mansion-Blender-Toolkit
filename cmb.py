import bpy
import bmesh
from bStream import *

def import_model(pth):
    stream = bStream(path=pth)
    stream.endian = '<'


    cmb_chunk = read_cmb_chunk(stream)
    stream.seek(cmb_chunk['skl_chunk_offset'])

    skl_chunk = read_skl_chunk(stream)

    stream.seek(cmb_chunk['vatr_chunk_offset'])
    vatr_chunk = read_vatr_chunk(stream, cmb_chunk['vatr_chunk_offset'])

    amt = bpy.data.armatures.new(f"{cmb_chunk['name']}_skl")
    cmb_object = bpy.data.objects.new(cmb_chunk['name'], amt)

    scene = bpy.context.scene
    bpy.context.scene.collection.objects.link(cmb_object)
    bpy.context.view_layer.objects.active = cmb_object

    ## Mesh Set up
    mesh = bpy.data.meshes.new(f"{cmb_chunk['name']}_mesh_data")
    mesh.from_pydata(vatr_chunk['positions'], [], [])
    mesh.update()

    mesh_obj = bpy.data.objects.new(f"{cmb_chunk['name']}_mesh", mesh)     
    mesh_obj.parent = cmb_object   
    bpy.context.scene.collection.objects.link(mesh_obj)

    #Resume Adding Skeleton
    bpy.ops.object.mode_set(mode='EDIT')

    for bone in skl_chunk['bones']:
        blender_bone = amt.edit_bones.new(f"bone_{bone['id']}")
        parent = amt.edit_bones.get(f"bone_{bone['parent']}")
        print(f"Added bone 'bone_{bone['id']}', parent id is {bone['parent']}, found {parent.name if parent is not None else '(None)'} in armature")

        blender_bone.parent = parent if parent is not None else None
        offset_from = (parent.head if parent is not None else [0,0,0])
        blender_bone.head = [bone['translation'][0] + offset_from[0], (-bone['translation'][2]) + offset_from[1], bone['translation'][1] + offset_from[2]]
        blender_bone.tail = [bone['translation'][0] + offset_from[0], (-bone['translation'][2]) + offset_from[1], bone['translation'][1] + offset_from[2]]
        blender_bone.tail[2] += 1
    
    bpy.ops.object.mode_set(mode='OBJECT')

def read_cmb_chunk(stream):
    return {
        'magic' : stream.readString(4),
        'file_size' : stream.readUInt32(),
        'version' : stream.readUInt32(),
        'unused' : stream.readUInt32(),
        'name' : stream.readString(16),
        'vertex_indices_count' : stream.readUInt32(),
        'skl_chunk_offset' : stream.readUInt32(),
        'mats_chunk_offset' : stream.readUInt32(),
        'tex_chunk_offset' : stream.readUInt32(),
        'sklm_chunk_offset' : stream.readUInt32(),
        'luts_chunk_offset' : stream.readUInt32(),
        'vatr_chunk_offset' : stream.readUInt32(),
        'vertex_indces_data_offset' : stream.readUInt32(),
        'texture_data_offset' : stream.readUInt32()
    }

def read_skl_chunk(stream):
    chunk = {
        'magic' : stream.readString(4),
        'size' : stream.readUInt32(),
        'bone_count' : stream.readUInt32(),
        'unknown' : stream.readUInt32(),
        'bones' : []
    }
    print(f"Reading Bones at {stream.tell():x}, there are {chunk['bone_count']} bones")
    chunk['bones'] = [
        {
            'id':stream.readUInt8(),
            'unknown':stream.readUInt8(),
            'parent':stream.readInt16(),
            'scale':[stream.readFloat(),stream.readFloat(),stream.readFloat()],
            'rotation':[stream.readFloat(),stream.readFloat(),stream.readFloat()],
            'translation':[stream.readFloat(),stream.readFloat(),stream.readFloat()],
            'unk1' : stream.readUInt16(),
            'unk2' : stream.readUInt16()
        } for b in range(chunk['bone_count'])
    ]

    return chunk

def read_sklm_chunk(stream, start_offset):
    chunk = {
        'magic' : stream.readString(4),
        'size' : stream.readUInt32(),
        'mshs_offset' : stream.readUInt32(),
        'shp_offset' : stream.readUInt32(),
        'msh_chunk' : {},
        'shp_chunk' : {}
    }

    stream.seek(start_offset + chunk['mshs_offset'])
    chunk['mshs_chunk'] = read_mshs_chunk(stream)

    stream.seek(start_offset + chunk['shp_offset'])
    chunk['shp_chunk'] = read_shp_chunk(stream)

    return chunk


def read_mshs_chunk(stream):
    chunk = {
        'magic' : stream.readString(4),
        'size' : stream.readUInt32(),
        'mesh_count' : stream.readUInt32(),
        'unk_count' : stream.readUInt16(),
        'id_count' : stream.readUInt16(),
        'meshes' : []
    }

    chunk['meshes'] = [{
        'sepd_index' : stream.readUInt16(),
        'material_index' : stream.readUInt8(),
        'id' : stream.readUInt8(),
        'unk' : stream.readU32s(21)
    } for x in range(chunk['mesh_count'])]

    return chunk

def read_shp_chunk(stream):
    pass

def read_vatr_chunk(stream, offset):
    chunk = {
        'magic' : stream.readString(4),
        'size' : stream.readUInt32(),
        'max_index' : stream.readUInt32(),
        'positions' : [],
        'positions_slice' : [stream.readUInt32(), stream.readUInt32()],
        'normals' : [],
        'normals_slice' : [stream.readUInt32(), stream.readUInt32()],
        'tangents' : [],
        'tangents_slice' : [stream.readUInt32(), stream.readUInt32()],
        'colors' : [],
        'colors_slice' : [stream.readUInt32(), stream.readUInt32()],
        'uv0' : [],
        'uv0_slice' : [stream.readUInt32(), stream.readUInt32()],
        'uv1' : [],
        'uv1_slice' : [stream.readUInt32(), stream.readUInt32()],
        'uv2' : [],
        'uv2_slice' : [stream.readUInt32(), stream.readUInt32()],
        'bone_indices' : [],
        'bone_indices_slice' : [stream.readUInt32(), stream.readUInt32()],
        'bone_weights' : [],
        'bone_weights_slice' : [stream.readUInt32(), stream.readUInt32()],
    }

    stream.seek(chunk['positions_slice'][1])
    print(f"Vertex Count: {chunk['positions_slice'][0]}")
    chunk['positions'] = [[stream.readFloat(), stream.readFloat(), stream.readFloat()] for x in range(chunk['positions_slice'][0] // 12)]

    return chunk