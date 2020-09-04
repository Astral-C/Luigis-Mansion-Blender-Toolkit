import pth
import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from bStream import *

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
        maxlen=255,  # Max internal buffer length, longer would be clamped.
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
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        if(pth.save_anim(self.filepath)):
            return {'FINISHED'}
        else:
            #TODO: Show error
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(MansionPthImport.bl_idname, text="Luigi's Mansion Path Animaton (.pth)")

def menu_func_export(self, context):
    self.layout.operator(MansionPthExport.bl_idname, text="Luigi's Mansion Path Animaton (.pth)")



def register():
    #bpy.utils.register_class(MansionMDL)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    #bpy.utils.unregister_class(MansionMDL)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)