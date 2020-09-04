import os
import bpy
from bStream import *
from itertools import chain 

def load_anim(pth):
    stream = bStream(path=pth)
    target_name = f"{os.path.basename(pth).split('.')[0]}_PTH"
    target_action = bpy.data.actions.new(f"{target_name}_PTH_ACN")

    target = bpy.data.objects.new(target_name, None)

    # Start loading anmation

    frame_count = stream.readUInt16()
    print(frame_count)
    stream.readUInt16() #Padding
    frames = {
        'x':[],
        'y':[],
        'z':[],
        'rx':[],
        'ry':[],
        'rz':[]
    }
    
    XGroup = PTHLoadGroup(stream)
    YGroup = PTHLoadGroup(stream)
    ZGroup = PTHLoadGroup(stream)

    RXGroup = PTHLoadGroup(stream)
    RYGroup = PTHLoadGroup(stream)
    RZGroup = PTHLoadGroup(stream)

    key_data_offset = stream.readUInt32()

    #Load Frame Data
    PTHLoadGroupData(stream, key_data_offset, XGroup, 'x', frames)
    PTHLoadGroupData(stream, key_data_offset, YGroup, 'y', frames)
    PTHLoadGroupData(stream, key_data_offset, ZGroup, 'z', frames)

    PTHLoadGroupData(stream, key_data_offset, RXGroup, 'rx', frames)
    PTHLoadGroupData(stream, key_data_offset, RYGroup, 'ry', frames)
    PTHLoadGroupData(stream, key_data_offset, RZGroup, 'rz', frames)

    #Set Frame Data
    bpy.context.scene.frame_end = frame_count
    target.animation_data_clear()
    target_anim_data = target.animation_data_create()


    GenerateFCurves(target_action,'x', 0, frames['x'])
    GenerateFCurves(target_action,'y', 1, frames['z'], invert=True)
    GenerateFCurves(target_action,'z', 2, frames['y'])#clip_start

    target_anim_data.action = target_action

    bpy.context.scene.collection.objects.link(target)

def GenerateFCurves(action, track, track_index, keyframes, invert=False):
    curve = action.fcurves.new("location", index=track_index, action_group=f"Loc{track.upper()}")
    curve.keyframe_points.add(count=len(keyframes))

    if(invert):
        for f in range(len(keyframes)):
            keyframes[f][1] = -keyframes[f][1]

    curve.keyframe_points.foreach_set("co", list(chain.from_iterable(keyframes)))
    curve.update()

def GenerateKeyframes(obj, data_path, keyframes):
    for keyframe in keyframes:
        obj[data_path] = keyframe[1]
        obj.keyframe_insert(data_path, frame=keyframe[0])

def PTHLoadGroup(stream):
    return  {'KeyCount':stream.readUInt16(),'BeginIndex':stream.readUInt16(),'ElementCount':stream.readUInt16()}

def PTHWriteGroup(stream, group):
    stream.writeUInt16(group['KeyCount'])
    stream.writeUInt16(group['BeginIndex'])
    stream.writeUInt16(group['ElementCount']) # should always be 2 for now


def PTHLoadGroupData(stream, offset, group, out_pos, frames):
    stream.seek(offset + (4 * group['BeginIndex']))
    for frame in range(0,group['KeyCount']):
        frame_data = [stream.readFloat() for x in range(0, group['ElementCount'])]

        if(group['ElementCount'] == 1):
            frames[out_pos].append([frame, frame_data[0]])

        else:
            frames[out_pos].append([int(frame_data[0]), frame_data[1]])

def PTHWriteGroupData(stream, curve, data_offset, dummy=None, invert=False):
    begin_index = int((stream.fhandle.tell() - data_offset) / 4)
    print(f'Writing Group with begin index {begin_index}')

    if(dummy is not None):
        stream.writeFloat(dummy)
        return {'KeyCount': 1, 'BeginIndex':begin_index, 'ElementCount':1}
        
    for keyframe in curve.keyframe_points:
        stream.writeFloat(keyframe.co[0])
        stream.writeFloat(keyframe.co[1] if not invert else -keyframe.co[1])
        stream.writeFloat(1.0)

    return {'KeyCount': len(curve.keyframe_points), 'BeginIndex':begin_index, 'ElementCount':3}

def save_anim(pth): #TODO
    stream = bStream(path=pth)
    obj = bpy.context.view_layer.objects.active

    if(not(obj.type == 'EMPTY')):
        return False
        

    stream.writeUInt16(int(bpy.context.scene.frame_end))
    stream.writeUInt16(0)
    groups_definitoins = stream.fhandle.tell()
    stream.pad(36)
    keydata_offset = stream.fhandle.tell()
    stream.writeUInt32(0)
        
    target_curves = obj.animation_data.action.fcurves

    data_offset = stream.fhandle.tell()
    XGroup = PTHWriteGroupData(stream, target_curves[0], data_offset)
    YGroup = PTHWriteGroupData(stream, target_curves[2], data_offset)
    ZGroup = PTHWriteGroupData(stream, target_curves[1], data_offset, invert=True)
        
    # These groups are written manually due to not being anmiatible in blender or unknown 
    UnkGroup1 = PTHWriteGroupData(stream, None, data_offset, dummy=0.0)
    UnkGroup2 = PTHWriteGroupData(stream, None, data_offset, dummy=0.0)
    UnkGroup3 = PTHWriteGroupData(stream, None, data_offset, dummy=0.0)
    
    stream.seek(groups_definitoins)

    PTHWriteGroup(stream, XGroup)
    PTHWriteGroup(stream, YGroup)
    PTHWriteGroup(stream, ZGroup)

    PTHWriteGroup(stream, UnkGroup1)
    PTHWriteGroup(stream, UnkGroup2)
    PTHWriteGroup(stream, UnkGroup3)

    stream.seek(keydata_offset)
    stream.writeUInt32(data_offset)

    return True
