# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "C-Core Tools",
    "author" : "C-Core",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
from . import cct_export, cct_ops

class CCORETOOLS_BatchExportProps(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="Path", default="//", subtype='DIR_PATH')

class CCORETOOLS_PT_MainPanel(bpy.types.Panel):
    """Add-on"""
    bl_label = 'C-Core Tools'
    bl_idname = 'CCORETOOLS_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category =  'C-Core Tools'
    #bl_context = 'vertexpaint'

    def draw(self, context):
        #obj = context.active_object

        layout = self.layout

        layout.label(text="Vegetation Tools")
        layout.operator('ccoretools.origin_to_selected')
        layout.operator('ccoretools.origin_to_lowest_uv')
        layout.operator('ccoretools.vegetation_vertex_colors')
        layout.operator('ccoretools.vegetation_normals')

        layout.separator()
        
        layout.label(text="Batch Export Collections")

        props = context.scene.cct_export_props
        layout.prop(props, "path", text="Path")
        layout.operator("ccoretools.batch_export")


classes = (
    cct_export.CCORETOOLS_OT_BatchExport,
    cct_ops.CCORETOOLS_OT_OriginToSelected,
    cct_ops.CCORETOOLS_OT_OriginToLowestUv,
    cct_ops.CCORETOOLS_OT_VegetationVertexColors,
    cct_ops.CCORETOOLS_OT_VegetationNormals,
    CCORETOOLS_BatchExportProps,
    CCORETOOLS_PT_MainPanel
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.cct_export_props = bpy.props.PointerProperty(type=CCORETOOLS_BatchExportProps)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.cct_export_props
