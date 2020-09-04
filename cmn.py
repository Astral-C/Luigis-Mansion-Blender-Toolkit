import os
import bpy
from bStream import *
from itertools import chain 

def load_anim(pth):
    stream = bStream(path=pth)
    cam_anim = bpy.data.objects.new(f"{os.path.basename(pth).split('.')[0]}", None)
    cmn_name = f"{os.path.basename(pth).split('.')[0]}_CAM"
    cmntarget_name = f"{os.path.basename(pth).split('.')[0]}_TGT"
    
    cam_action = bpy.data.actions.new(f"{cmn_name}_ACN")
    target_action = bpy.data.actions.new(f"{cmntarget_name}_ACN")

    cam = bpy.data.cameras.new(cmn_name)
    cam_obj = bpy.data.objects.new(cmn_name, cam)

    cam_target = bpy.data.objects.new(cmntarget_name, None)
    track = cam_obj.constraints.new("TRACK_TO")
    track.target = cam_target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    track.use_target_z = True

    cam_obj.parent = cam_anim
    cam_target.parent = cam_anim

    # Start loading anmation

    frame_count = stream.readUInt16()
    print(frame_count)
    stream.readUInt16() #Padding
    frames = {
        'x':[],
        'y':[],
        'z':[],
        'tx':[],
        'ty':[],
        'tz':[],
        'unk':[],
        'fov':[],
        'znear':[],
        'zfar':[]
    }
    
    XGroup = CMNLoadGroup(stream)
    YGroup = CMNLoadGroup(stream)
    ZGroup = CMNLoadGroup(stream)

    TXGroup = CMNLoadGroup(stream)
    TYGroup = CMNLoadGroup(stream)
    TZGroup = CMNLoadGroup(stream)

    UnkGroup = CMNLoadGroup(stream)
    FOVGroup = CMNLoadGroup(stream)
    ZNearGroup = CMNLoadGroup(stream)
    ZFarGroup = CMNLoadGroup(stream)

    #Load Frame Data
    CMNLoadGroupData(stream, XGroup, 'x', frames)
    CMNLoadGroupData(stream, YGroup, 'y', frames)
    CMNLoadGroupData(stream, ZGroup, 'z', frames)

    CMNLoadGroupData(stream, TXGroup, 'tx', frames)
    CMNLoadGroupData(stream, TYGroup, 'ty', frames)
    CMNLoadGroupData(stream, TZGroup, 'tz', frames)

    CMNLoadGroupData(stream, UnkGroup, 'unk', frames)
    CMNLoadGroupData(stream, FOVGroup, 'fov', frames)
    CMNLoadGroupData(stream, ZNearGroup, 'znear', frames)
    CMNLoadGroupData(stream, ZFarGroup, 'zfar', frames)

    #Set Frame Data
    bpy.context.scene.frame_end = frame_count
    cam_obj.animation_data_clear()
    cam_target.animation_data_clear()
    cam_anim_data = cam_obj.animation_data_create()
    cam_target_anim_data = cam_target.animation_data_create()


    GenerateFCurves(cam_action, 'x', 0, frames['x'])
    GenerateFCurves(cam_action, 'y', 1, frames['z'], invert=True)
    GenerateFCurves(cam_action, 'z', 2, frames['y'])

    GenerateFCurves(target_action,'x', 0, frames['tx'])
    GenerateFCurves(target_action,'y', 1, frames['tz'], invert=True)
    GenerateFCurves(target_action,'z', 2, frames['ty'])#clip_start

    #so apparently you cant animate fov in blender, stupid shit, fuck you.
    GenerateKeyframes(cam, "lens", frames['fov'])
    GenerateKeyframes(cam, "clip_start", frames['znear'])
    GenerateKeyframes(cam, "clip_end", frames['zfar'])


    cam_anim_data.action = cam_action
    cam_target_anim_data.action = target_action

    bpy.context.scene.collection.objects.link(cam_anim)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.collection.objects.link(cam_target)

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

def CMNLoadGroup(stream):
    return  {'KeyCount':stream.readUInt16(),'BeginIndex':stream.readUInt16(),'ElementCount':stream.readUInt16()}

def CMNWriteGroup(stream, group):
    stream.writeUInt16(group['KeyCount'])
    stream.writeUInt16(group['BeginIndex'])
    stream.writeUInt16(group['ElementCount']) # should always be 2 for now


def CMNLoadGroupData(stream, group, out_pos, frames):
    stream.seek(68 + (4 * group['BeginIndex']))
    for frame in range(0,group['KeyCount']):
        frame_data = [stream.readFloat() for x in range(0, group['ElementCount'])]

        if(group['ElementCount'] == 1):
            frames[out_pos].append([frame, frame_data[0]])

        else:
            frames[out_pos].append([int(frame_data[0]), frame_data[1]])

def CMNWriteGroupData(stream, curve, dummy=None, invert=False):
    begin_index = int((stream.fhandle.tell() - 68) / 4)
    print(f'Writing Group with begin index {begin_index}')

    if(dummy is not None):
        stream.writeFloat(dummy)
        return {'KeyCount': 1, 'BeginIndex':begin_index, 'ElementCount':1}
        
    for keyframe in curve.keyframe_points:
        stream.writeFloat(keyframe.co[0])
        stream.writeFloat(keyframe.co[1] if not invert else -keyframe.co[1])
        stream.writeFloat(1.0)

    return {'KeyCount': len(curve.keyframe_points), 'BeginIndex':begin_index, 'ElementCount':3}

def save_anim(pth):
    stream = bStream(path=pth)
    if(bpy.context.scene.camera is not None):
        cam = bpy.context.scene.camera
        if(not(cam.parent.type == 'EMPTY') or not (len(cam.parent.children) == 2)):

            return False
        

        stream.writeUInt16(int(bpy.context.scene.frame_end))
        stream.writeUInt16(0)
        groups_definitoins = stream.fhandle.tell()
        stream.pad(60)
        stream.writeFloat(1.18)
        
        cam_curves = cam.animation_data.action.fcurves
        target_curves = cam.parent.children[1].animation_data.action.fcurves
        ocam_curves = bpy.data.cameras[cam.name.split('.')[0]].animation_data.action.fcurves

        XGroup = CMNWriteGroupData(stream, cam_curves[0])
        YGroup = CMNWriteGroupData(stream, cam_curves[2])
        ZGroup = CMNWriteGroupData(stream, cam_curves[1], invert=True)

        TXGroup = CMNWriteGroupData(stream, target_curves[0])
        TYGroup = CMNWriteGroupData(stream, target_curves[2])
        TZGroup = CMNWriteGroupData(stream, target_curves[1], invert=True)
        
        # These groups are written manually due to not being anmiatible in blender or unknown 
        UnkGroup = CMNWriteGroupData(stream, None, dummy=0.0)
        FOVGroup = CMNWriteGroupData(stream, ocam_curves[0])

        ZNearGroup = CMNWriteGroupData(stream, ocam_curves[1])
        ZFarGroup = CMNWriteGroupData(stream, ocam_curves[2])

        stream.seek(groups_definitoins)

        CMNWriteGroup(stream, XGroup)
        CMNWriteGroup(stream, YGroup)
        CMNWriteGroup(stream, ZGroup)

        CMNWriteGroup(stream, TXGroup)
        CMNWriteGroup(stream, TYGroup)
        CMNWriteGroup(stream, TZGroup)

        CMNWriteGroup(stream, UnkGroup)
        CMNWriteGroup(stream, FOVGroup)
        CMNWriteGroup(stream, ZNearGroup)
        CMNWriteGroup(stream, ZFarGroup)

        return True
