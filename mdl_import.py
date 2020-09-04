import mdl
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from bStream import *

class MansionMDL(bpy.types.Operator, ImportHelper):
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
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        mdl.mdl_model(self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(MansionMDL.bl_idname, text="Luigi's Mansion MDL (.mdl)")


def register():
    #bpy.utils.register_class(MansionMDL)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    #bpy.utils.unregister_class(MansionMDL)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)