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

class CCORETOOLS_OT_OriginToSelected(bpy.types.Operator):
    bl_idname = 'ccoretools.origin_to_selected'
    bl_label = 'Origin to Selected'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return context.object.mode == 'EDIT' and obj is not None and obj.type == 'MESH'

    def execute(self, context):
        oldPivot = bpy.context.scene.tool_settings.transform_pivot_point
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'        
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.context.scene.tool_settings.transform_pivot_point = oldPivot

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


class CCORETOOLS_OT_OriginToLowestUv(bpy.types.Operator):
    bl_idname = 'ccoretools.origin_to_lowest_uv'
    bl_label = 'Origin to Lowest UV'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            return False

        for obj in context.selected_objects:
            if obj.type != 'MESH':
                return False

        return True

    def execute(self, context):
        oldMode = context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        oldSelection = context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in oldSelection:
            mesh = obj.data

            if not mesh.uv_layers:
                continue

            uvs = mesh.uv_layers.values()[0]
            minUvDistance = 100000
            vertexPos = context.scene.cursor.location

            for loop_index, loop in enumerate(mesh.loops):
                uvDistance = uvs.data[loop_index].uv.length
                if uvDistance < minUvDistance:
                    minUvDistance = uvDistance
                    vertexPos = mesh.vertices[loop.vertex_index].co

            context.scene.cursor.location = obj.matrix_world @ vertexPos
            
            obj.select_set(state=True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            obj.select_set(state=False)

        for obj in oldSelection:
            obj.select_set(state=True)

        bpy.ops.object.mode_set(mode=oldMode)

        return {'FINISHED'} 

class CCORETOOLS_OT_VegetationVertexColors(bpy.types.Operator):
    bl_idname = 'ccoretools.vegetation_vertex_colors'
    bl_label = 'Vegetation Vertex Colors'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH'

    def fillVC(self, mesh, color, weights):
        if not mesh.vertex_colors:
            mesh.vertex_colors.new()

        cols = mesh.vertex_colors[0]

        for loop_index, loop in enumerate(mesh.loops):
            c = cols.data[loop_index].color
            for i in range(0, 4):
                c[i] = (1 - weights[i]) * c[i] + weights[i] * color[i]

            cols.data[loop_index].color = c

    def distanceVC(self, obj, origin, maxDistance, channel):
        maxDistance = max(maxDistance, 0.0000001)

        mesh = obj.data
        cols = mesh.vertex_colors[0]

        for loop_index, loop in enumerate(mesh.loops):
            vi = loop.vertex_index
            vertexPos = obj.matrix_world @ mesh.vertices[vi].co
            distance = min(1.0, (vertexPos - origin).length / maxDistance)
        
            cols.data[loop_index].color[channel] = distance

    def findMaxDistance(self, obj, origin):
        maxDistance = 0

        mesh = obj.data
        for loop in mesh.loops:
            vi = loop.vertex_index
            vertexPos = obj.matrix_world @ mesh.vertices[vi].co
            maxDistance = max(maxDistance, (vertexPos - origin).length)
        
        return maxDistance

    def execute(self, context):
        oldMode = context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        blackColor = [0] * 4
        allSet = [1] * 4
        
        trunkObj = context.active_object
        self.fillVC(trunkObj.data, blackColor, allSet)

        random.seed(trunkObj.name)

        for branchObj in trunkObj.children:
            if branchObj.type != 'MESH':
                continue

            branchId = random.random()
            branchFillColor = [0, branchId, 0, 0]
            self.fillVC(branchObj.data, branchFillColor, allSet)
            for leafObj in branchObj.children:
                if branchObj.type == 'MESH':
                    self.fillVC(leafObj.data, branchFillColor, allSet)

            branchOrigin = branchObj.matrix_world.to_translation()

            maxDistance = self.findMaxDistance(branchObj, branchOrigin)
            for leafObj in branchObj.children:
                if branchObj.type == 'MESH':
                    maxDistance = max(maxDistance, self.findMaxDistance(leafObj, branchOrigin))

            self.distanceVC(branchObj, branchOrigin, maxDistance, 2)
            for leafObj in branchObj.children:
                if branchObj.type == 'MESH':
                    self.distanceVC(leafObj, branchOrigin, maxDistance, 2)
                    
                    leafOrigin = leafObj.matrix_world.to_translation()
                    maxLeafDistance = self.findMaxDistance(leafObj, leafOrigin)
                    self.distanceVC(leafObj, leafOrigin, maxLeafDistance, 0)

        bpy.ops.object.mode_set(mode=oldMode)

        return {'FINISHED'}