import os
import bpy
from bStream import *
from itertools import chain 
import math

def load_anim(pth):
    stream = bStream(path=pth)

    root = bpy.context.selected_objects[0].children[0]


    #version
    stream.readUInt8()
    loop = stream.readUInt8()
    stream.readUInt16() #Padding
    frame_count = stream.readUInt32()
    scale_key_offset = stream.readUInt32()
    rotate_key_offset = stream.readUInt32()
    translate_key_offset = stream.readUInt32()
    node_group_offset = stream.readUInt32()
    bpy.context.scene.frame_end = frame_count

    index = 1
    print(f"Reading Nodes at: {stream.fhandle.tell()}")
    stream.seek(node_group_offset)
    ANMLoadNode(root, stream, scale_key_offset, rotate_key_offset, translate_key_offset)
    ANMLoadNodes(stream, root, index, scale_key_offset, rotate_key_offset, translate_key_offset, node_group_offset)

def ANMLoadNode(node, stream, scale_key_offset, rotate_key_offset, translate_key_offset):
    node.animation_data_clear()
    node_anim_data = node.animation_data_create()

    node_frames = {
        'sx':[],
        'sy':[],
        'sz':[],
        'rx':[],
        'ry':[],
        'rz':[],
        'x':[],
        'y':[],
        'z':[]
    }

    SXGroup = ANMLoadGroupDef(stream)
    SYGroup = ANMLoadGroupDef(stream)
    SZGroup = ANMLoadGroupDef(stream)

    RXGroup = ANMLoadGroupDef(stream)
    RYGroup = ANMLoadGroupDef(stream)
    RZGroup = ANMLoadGroupDef(stream)

    XGroup = ANMLoadGroupDef(stream)
    YGroup = ANMLoadGroupDef(stream)
    ZGroup = ANMLoadGroupDef(stream)

    ANMLoadGroupData(stream, scale_key_offset, SXGroup, 'sx', node_frames)
    ANMLoadGroupData(stream, scale_key_offset, SYGroup, 'sy', node_frames)
    ANMLoadGroupData(stream, scale_key_offset, SZGroup, 'sz', node_frames)
            
    ANMLoadGroupData(stream, rotate_key_offset, RXGroup, 'rx', node_frames, True)
    ANMLoadGroupData(stream, rotate_key_offset, RYGroup, 'ry', node_frames, True)
    ANMLoadGroupData(stream, rotate_key_offset, RZGroup, 'rz', node_frames, True)

    ANMLoadGroupData(stream, translate_key_offset, XGroup, 'x', node_frames)
    ANMLoadGroupData(stream, translate_key_offset, YGroup, 'y', node_frames)
    ANMLoadGroupData(stream, translate_key_offset, ZGroup, 'z', node_frames)
            
    node_action = bpy.data.actions.new(f"{node.name}_ACN")

    GenerateFCurves(node_action, "scale", 'x', 0, node_frames['sx'])
    GenerateFCurves(node_action, "scale", 'y', 1, node_frames['sz'])
    GenerateFCurves(node_action, "scale", 'z', 2, node_frames['sy'])

    GenerateFCurves(node_action, "rotation_euler", 'x', 0, node_frames['rx'])
    GenerateFCurves(node_action, "rotation_euler", 'y', 1, node_frames['rz'], invert=True)
    GenerateFCurves(node_action, "rotation_euler", 'z', 2, node_frames['ry'])

    GenerateFCurves(node_action, "location", 'x', 0, node_frames['x'])
    GenerateFCurves(node_action, "location", 'y', 1, node_frames['z'], invert=True)
    GenerateFCurves(node_action, "location", 'z', 2, node_frames['y'])

    node_anim_data.action = node_action

def ANMLoadNodes(stream, local_root, index, scale_key_offset, rotate_key_offset, translate_key_offset, node_group_offset):
    for node in local_root.children:
        stream.seek(node_group_offset + (index * 0x36))
        print(f"Reading Anims for Node {node.name}")

        if(node.type == "EMPTY"):
            ANMLoadNode(node, stream, scale_key_offset, rotate_key_offset, translate_key_offset)
            index += 1

            if(len(node.children) > 0):
                ANMLoadNodes(stream, node, index, scale_key_offset, rotate_key_offset, translate_key_offset, node_group_offset)

def GenerateFCurves(action, curve, track, track_index, keyframes, invert=False):
    curve = action.fcurves.new(curve, index=track_index, action_group=f"Loc{track.upper()}")
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

def ANMLoadGroupDef(stream):
    return  {'KeyCount':stream.readUInt16(),'BeginIndex':stream.readUInt16(),'Flags':stream.readUInt16()}

def ANMLoadGroupData(stream, offset, group, out_pos, frames, rot=False):
    stream.seek(offset + (4 * group['BeginIndex']))

    if(group['KeyCount'] == 1):
        frames[out_pos].append([0, stream.readFloat()])

    else:
        for frame in range(0,group['KeyCount']):
            frame_data = [stream.readFloat() for x in range(0, (4 if(group["Flags"] == 0x80) else 3))]
            frames[out_pos].append([int(frame_data[0]), frame_data[1] if not rot else math.degrees(frame_data[1] * 0.0001533981)])