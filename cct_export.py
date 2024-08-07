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

import bpy
import math
import random
from mathutils import Color, Vector, Matrix

class CCORETOOLS_OT_BatchExport(bpy.types.Operator):
    bl_idname = 'ccoretools.batch_export'
    bl_label = 'Batch Export'
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.cct_export_props

        oldActiveLayer = context.view_layer.active_layer_collection

        for layerCollection in context.view_layer.layer_collection.children:
            if not layerCollection.visible_get():
                continue

            context.view_layer.active_layer_collection = layerCollection
            collection = layerCollection.collection

            if collection.name.startswith("."):
                continue

            objects = collection.all_objects.values()
            if not objects:
                continue

            parentObjects = []
            for obj in objects:
                if not obj.parent:
                    parentObjects.append(obj)

            parentObjects = sorted(
                parentObjects,
                key = lambda c: c.name.lower()
            )
            #print(parentObjects)

            obj0 = parentObjects[0]
            #print(obj0)
            moveToOrigin = obj0.location.copy()

            for obj in parentObjects:
                obj.location -= moveToOrigin

            filepath = bpy.path.abspath(props.path) + collection.name + '.glb'
            #print(filepath)
            #bpy.ops.export_scene.fbx(filepath=filepath, check_existing=False, use_active_collection=True, use_armature_deform_only=True, add_leaf_bones=False)
            bpy.ops.export_scene.gltf(filepath=filepath, check_existing=False, use_active_collection=True, export_apply=True, export_image_format='NONE', export_def_bones=True, export_vertex_color='ACTIVE')

            # restore location
            for obj in parentObjects:
                obj.location += moveToOrigin

        context.view_layer.active_layer_collection = oldActiveLayer

        return {'FINISHED'}
