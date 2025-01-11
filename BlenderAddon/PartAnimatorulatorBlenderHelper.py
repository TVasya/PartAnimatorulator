bl_info = {
    "name": "PartAnimatorulator Helper",
    "author": "TerminatorVasya",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Import/Export > NFSU2 AnimSlot Data",
    "description": 'Helper addon to simplify creating partanimation for NFSU2. Imports animation exported from PartAnimatorulator and adds it to selected object. Also exports animation of selected object (in the range of the playback frame count). ONLY ROTATION IS SUPPORTED, PLEASE DO NOT TRY TO MAKE ANIMATIONS THAT USE MOVEMENT AND THEN ASK ME "why this doesnt work".',
    "category": "Import-Export",
}
# i swear to god this is unfair as hell, but i've used chatgpt here as well
# why does it rhyme lmao☠️

import bpy
import math
import os
from bpy_extras.io_utils import ImportHelper, ExportHelper
from pathlib import Path

# Import Rotation Animation
class ImportRotationAnimation(bpy.types.Operator, ImportHelper):
    bl_idname = "import_animation.nfsu2"
    bl_label = "Import NFSU2 Animation"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".txt"
    filter_glob: bpy.props.StringProperty(default="*.txt", options={'HIDDEN'})

    def execute(self, context):
        file_path = self.filepath
        obj = context.object

        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a valid object (e.g., a mesh) to apply the animation.")
            return {'CANCELLED'}

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            if not lines:
                self.report({'ERROR'}, "The file is empty or contains no valid data.")
                return {'CANCELLED'}

            if obj.animation_data is None:
                obj.animation_data_create()

            file_name = Path(file_path).stem
            action = bpy.data.actions.new(name=file_name)
            obj.animation_data.action = action
            obj.rotation_mode = 'XYZ'

            frame_count = 0
            for i, line in enumerate(lines):
                values = line.strip().split()
                if len(values) != 3:
                    self.report({'WARNING'}, f"Skipping invalid line {i + 1}: {line}")
                    continue

                try:
                    x_deg, y_deg, z_deg = map(float, values)
                    x_rad, y_rad, z_rad = math.radians(x_deg), math.radians(y_deg), math.radians(z_deg)

                    frame = i + 1  # Frame numbers start at 1
                    obj.rotation_euler = (x_rad, y_rad, z_rad)
                    obj.keyframe_insert(data_path="rotation_euler", frame=frame)

                    frame_count = frame

                except ValueError:
                    self.report({'WARNING'}, f"Skipping invalid line {i + 1}: {line}")
                    continue

            context.scene.frame_start = 1
            context.scene.frame_end = frame_count
            context.scene.render.fps = 30

            self.report({'INFO'}, f"Animation successfully imported and applied to {obj.name}. Frame range set to 1-{frame_count}, FPS set to 30.")
            return {'FINISHED'}

        except FileNotFoundError:
            self.report({'ERROR'}, f"File '{file_path}' not found.")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"An unexpected error occurred: {e}")
            return {'CANCELLED'}

# Export Rotation Animation
class ExportRotationAnimation(bpy.types.Operator, ExportHelper):
    bl_idname = "export_animation.nfsu2"
    bl_label = "Export NFSU2 Animation"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".txt"
    filter_glob: bpy.props.StringProperty(default="*.txt", options={'HIDDEN'})

    def execute(self, context):
        file_path = self.filepath
        obj = context.object

        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a valid object (e.g., a mesh) to export the animation.")
            return {'CANCELLED'}

        try:
            frame_start = context.scene.frame_start
            frame_end = context.scene.frame_end
            lines = []

            for frame in range(frame_start, frame_end + 1):
                context.scene.frame_set(frame)
                rotation = obj.rotation_euler

                # Convert from radians to degrees
                x_deg = math.degrees(rotation.x)
                y_deg = math.degrees(rotation.y)
                z_deg = math.degrees(rotation.z)

                # Write rotation data for this frame
                lines.append(f"{x_deg:.6f} {y_deg:.6f} {z_deg:.6f}\n")

            # Write to the specified file
            with open(file_path, 'w') as file:
                file.writelines(lines)

            self.report({'INFO'}, f"Animation successfully exported to {os.path.basename(file_path)}.")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"An unexpected error occurred: {e}")
            return {'CANCELLED'}

# Menu Functions
def menu_func_import(self, context):
    self.layout.operator(ImportRotationAnimation.bl_idname, text="NFSU2 AnimSlot Data (.txt)")

def menu_func_export(self, context):
    self.layout.operator(ExportRotationAnimation.bl_idname, text="NFSU2 AnimSlot Data (.txt)")

# Register and Unregister Functions
def register():
    bpy.utils.register_class(ImportRotationAnimation)
    bpy.utils.register_class(ExportRotationAnimation)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportRotationAnimation)
    bpy.utils.unregister_class(ExportRotationAnimation)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
