import os
import bpy
import anm, binmdl, col, cmn, mdl, pth
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import Operator
from bStream import *

class MansionBinImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_model.mansionbin"
    bl_label = "Import Bin"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    @classmethod
    def poll(cls, context):
        return context is not None
    
    filename_ext = ".bin"

    filter_glob: StringProperty(
        default="*.bin",
        options={'HIDDEN'},
        maxlen=255,
    )

    #apply_wrap_modes: BoolProperty(
    #    default=False
    #)

    def execute(self, context):
        binmdl.bin_model_import(self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MansionBinExport(bpy.types.Operator, ExportHelper):
    bl_idname = "export_model.mansionbin"
    bl_label = "Export Bin"
    bl_description = "Export Bin model using this node as the root"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    @classmethod
    def poll(cls, context):
        return context is not None
    
    filename_ext = ".bin"

    filter_glob: StringProperty(
        default="*.bin",
        options={'HIDDEN'},
        maxlen=255,
    )

    compat_mode: BoolProperty(
        default=True,
        name="Console Compatible",
        description="Properly pad custom model. Disable this for smaller models that only work on emulator."
    )

    def execute(self, context):
        if(os.path.exists(self.filepath)):
            os.remove(self.filepath)
        binmdl.bin_model_export(self.filepath, self.compat_mode)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MansionAnmImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_anim.mansionanm"
    bl_label = "Import ANM"
    bl_description = "Import Bin animation using this node as the root"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    @classmethod
    def poll(cls, context):
        return context is not None
    
    filename_ext = ".anm"

    filter_glob: StringProperty(
        default="*.anm",
        options={'HIDDEN'},
        maxlen=255,  
    )

    def execute(self, context):
        anm.load_anim(self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MansionAnmExport(bpy.types.Operator, ExportHelper):
    bl_idname = "export_anim.mansionanm"
    bl_label = "Export ANM"
    bl_description = "Export Bin animation using this node as the root"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    @classmethod
    def poll(cls, context):
        return context is not None
    
    filename_ext = ".anm"

    filter_glob: StringProperty(
        default="*.anm",
        options={'HIDDEN'},
        maxlen=255,
    )

    loop: BoolProperty(
        default=False
    )

    def execute(self, context):
        if(os.path.exists(self.filepath)):
            os.remove(self.filepath)
        anm.write_anim(self.filepath, self.loop)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MansionMDLImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_model.mansionmdl"
    bl_label = "Import MDL"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    @classmethod
    def poll(cls, context):
        return context is not None
    
    filename_ext = ".mdl"

    filter_glob: StringProperty(
        default="*.mdl",
        options={'HIDDEN'},
        maxlen=255,  
    )

    def execute(self, context):
        mdl.mdl_model(self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MansionCmnImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_model.mansioncmn"
    bl_label = "Import CMN"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    @classmethod
    def poll(cls, context):
        return context is not None
    
    filename_ext = ".cmn"

    filter_glob: StringProperty(
        default="*.cmn",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        cmn.load_anim(self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MansionCmnExport(bpy.types.Operator, ExportHelper):
    bl_idname = "export_model.mansioncmn"
    bl_label = "Export CMN"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    @classmethod
    def poll(cls, context):
        return context is not None
    
    filename_ext = ".cmn"

    filter_glob: StringProperty(
        default="*.cmn",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        if(os.path.exists(self.filepath)):
            os.remove(self.filepath)
        if(cmn.save_anim(self.filepath)):
            return {'FINISHED'}
        else:
            #TODO: Show error
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MansionPthImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_model.mansionpth"
    bl_label = "Import PTH"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    @classmethod
    def poll(cls, context):
        return context is not None
    
    filename_ext = ".pth"

    filter_glob: StringProperty(
        default="*.pth",
        options={'HIDDEN'},
        maxlen=255,  
    )

    def execute(self, context):
        pth.load_anim(self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MansionPthExport(bpy.types.Operator, ExportHelper):
    bl_idname = "export_model.mansionpth"
    bl_label = "Export PTH"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    @classmethod
    def poll(cls, context):
        return context is not None
    
    filename_ext = ".pth"

    filter_glob: StringProperty(
        default="*.pth",
        options={'HIDDEN'},
        maxlen=255,  
    )

    def execute(self, context):
        if(os.path.exists(self.filepath)):
            os.remove(self.filepath)
        if(pth.save_anim(self.filepath)):
            return {'FINISHED'}
        else:
            #TODO: Show error
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MansionColImport(bpy.types.Operator, ImportHelper):
    bl_idname = "import_model.mansioncol"
    bl_label = "Import COLMP"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    @classmethod
    def poll(cls, context):
        return context is not None
    
    filename_ext = ".mp"

    filter_glob: StringProperty(
        default="*.mp",
        options={'HIDDEN'},
        maxlen=255,  
    )

    def execute(self, context):
        col.load_model(self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class TOPBAR_MT_file_import_mansion(bpy.types.Menu):
    bl_idname = 'import_model.mansion'
    bl_label = "Luigi's Mansion"

    def draw(self, context):
        layout = self.layout
        self.layout.operator(MansionBinImport.bl_idname, text="Bin (.bin)")
        #self.layout.operator(MansionMDLImport.bl_idname, text="MDL (.mdl)")
        self.layout.operator(MansionColImport.bl_idname, text="Collision (.mp)")
        self.layout.operator(MansionCmnImport.bl_idname, text="CMN (.cmn)")
        self.layout.operator(MansionPthImport.bl_idname, text="PTH (.pth)")

class TOPBAR_MT_file_export_mansion(bpy.types.Menu):
    bl_idname = 'export_model.mansion'
    bl_label = "Luigi's Mansion"

    def draw(self, context):
        layout = self.layout
        self.layout.operator(MansionCmnExport.bl_idname, text="CMN (.cmn)")
        self.layout.operator(MansionPthExport.bl_idname, text="PTH (.pth)")

def menu_func_import(self, context):
    self.layout.menu(TOPBAR_MT_file_import_mansion.bl_idname)

def menu_func_export(self, context):
    self.layout.menu(TOPBAR_MT_file_export_mansion.bl_idname)

def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)