import cmn
import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from bStream import *

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
        maxlen=255,  # Max internal buffer length, longer would be clamped.
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
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        if(cmn.save_anim(self.filepath)):
            return {'FINISHED'}
        else:
            #TODO: Show error
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(MansionCmnImport.bl_idname, text="Luigi's Mansion Camera Animaton (.cmn)")

def menu_func_export(self, context):
    self.layout.operator(MansionCmnExport.bl_idname, text="Luigi's Mansion Camera Animaton (.cmn)")



def register():
    #bpy.utils.register_class(MansionMDL)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    #bpy.utils.unregister_class(MansionMDL)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)