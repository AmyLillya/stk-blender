#!BPY

# Copyright (c) 2017 SPM author(s)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

bl_info = {
    "name": "SPM (Space paritioned mesh) format",
    "author": "Benau, Richard Qian",
    "description": "Import-Export from or to the SPM format (the SuperTuxKart mesh format)",
    "version": (2,0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "wiki_url": "https://supertuxkart.net/Community",
    "tracker_url": "https://github.com/supertuxkart/stk-blender/issues",
    "category": "Import-Export"}

if "bpy" in locals():
    import importlib
    if "import_spm" in locals():
        importlib.reload(import_spm)
    if "export_spm" in locals():
        importlib.reload(export_spm)
else:
    from . import import_spm, export_spm

import bpy, bpy_extras, os

# ==== Import OPERATOR ====
from bpy_extras.io_utils import (ImportHelper)

class SPM_Import_Operator(bpy.types.Operator, ImportHelper):
    bl_idname = ("screen.spm_import")
    bl_label = ("SPM Import")
    bl_options = {'UNDO'}

    filename_ext = ".spm"
    filter_glob: bpy.props.StringProperty(default="*.spm", options={'HIDDEN'})
    extra_tex_path: bpy.props.StringProperty(name="Texture path",\
    description="Extra directory for textures, importer will search recursively")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "extra_tex_path")
    def execute(self, context):
        keywords = self.as_keywords(ignore=("filter_glob",))
        import_spm.loadSPM(context, **keywords)
        context.view_layer.update()
        return {"FINISHED"}

# ==== CONFIRM OPERATOR ====
class SPM_Confirm_Operator(bpy.types.Operator):
    bl_idname = ("screen.spm_confirm")
    bl_label = ("File Exists, Overwrite?")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        writeSPMFile(SPM_Confirm_Operator.filepath)
        return {'FINISHED'}

# ==== EXPORT OPERATOR ====
from bpy_extras.io_utils import ExportHelper

class SPM_Export_Operator(bpy.types.Operator, ExportHelper):
    """"Save a SPM File"""

    bl_idname = ("screen.spm_export")
    bl_label = ("Export SPM")
    bl_option = {'PRESET'}

    filename_ext = ".spm"
    filter_glob: bpy.props.StringProperty(
        default="*.spm",
        options={'HIDDEN'},
    )

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    selected: bpy.props.BoolProperty(name="Export selected only", default = False)
    localsp: bpy.props.BoolProperty(name="Use local coordinates", default = False)
    applymodifiers: bpy.props.BoolProperty(name="Apply modifiers", default = True)
    do_sp: bpy.props.BoolProperty(name="Do mesh splitting (for space partitioning)", default = False)
    overwrite_without_asking: bpy.props.BoolProperty(name="Overwrite without asking", default = False)
    keyframes_only: bpy.props.BoolProperty(name="Export keyframes only for animated mesh", default = True)
    export_normal: bpy.props.BoolProperty(name="Export normal in mesh", default = True)
    export_vcolor: bpy.props.BoolProperty(name="Export vertex color in mesh", default = True)
    export_tangent: bpy.props.BoolProperty(name="Calculate tangent and bitangent sign for mesh", default = True)
    static_mesh_frame: bpy.props.IntProperty(name="Frame for static mesh usage", default = -1)

    def execute(self, context):
        spm_parameters = {}
        spm_parameters["export-selected"] = self.selected
        spm_parameters["local-space"    ] = self.localsp
        spm_parameters["apply-modifiers"] = self.applymodifiers
        spm_parameters["keyframes-only"] = self.keyframes_only
        spm_parameters["export-normal"] = self.export_normal
        spm_parameters["export-vcolor"] = self.export_vcolor
        spm_parameters["export-tangent"] = self.export_tangent
        spm_parameters["static-mesh-frame"] = self.static_mesh_frame
        spm_parameters["do-sp"] = self.do_sp

        if self.filepath == "":
            return {'FINISHED'}

        print("EXPORT", self.filepath)

        obj_list = []
        try:
            obj_list = context.scene.obj_list
        except:
            pass

        if len(obj_list) > 0:
            export_spm.writeSPMFile(self.filepath, spm_parameters, obj_list)
        else:
            if os.path.exists(self.filepath) and not self.overwrite_without_asking:
                SPM_Confirm_Operator.filepath = self.filepath
                bpy.ops.screen.spm_confirm('INVOKE_DEFAULT')
                return {'FINISHED'}
            else:
                export_spm.writeSPMFile(self.filepath, spm_parameters)
        return {'FINISHED'}

# Add to a menu
def menu_func_import(self, context):
    self.layout.operator(SPM_Import_Operator.bl_idname, text="SPM (.spm)")

def menu_func_export(self, context):
    self.layout.operator(SPM_Export_Operator.bl_idname, text="SPM (.spm)")

classes = (
    SPM_Import_Operator,
    SPM_Export_Operator,
    SPM_Confirm_Operator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register
