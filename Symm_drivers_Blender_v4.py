bl_info = {
    "name": "Bone Drivers Symmetrizer",
    "author": "Jonas Aguilar Borrego",
    "version": (4, 0),
    "blender": (4, 2, 0),
    "location": "Armature",
    "description": "Symmetrize drivers in selected bones",
    "warning": "Only TRANSFORMS or CONSTRAINTS drivers",
    "doc_url": "",
    "support": "COMMUNITY",
    "category": "Rigging",
}

import bpy
import re

class SymDriversOperator(bpy.types.Operator):
    bl_idname = "object.sym_drivers"
    bl_label = "Symmetrize selected drivers"
    bl_description = "Symmetrize drivers in selected bones"

    def execute(self, context):

        bpy.ops.object.mode_set(mode='POSE') # Cambiar a POSE MODE

        def replace_lateral(name): # Definimos la funcion de reemplazo usando regex 
            pattern = re.compile(r'(?<![a-zA-Z])([._-]?[lLrR][._-]?)(?![a-zA-Z])') # Patron regex para letras seguidas y/o precedidas de simbolos
            
            def replace(match): # Metodo de la logica del reemplazo
                side = match.group(0)
                if 'L' in side:
                    return side.replace('L', 'R')
                elif 'R' in side:
                    return side.replace('R', 'L')
                elif 'l' in side:
                    return side.replace('l', 'r')
                elif 'r' in side:
                    return side.replace('r', 'l')
                return side
            return pattern.sub(replace, name)

        def find_symm_bone(bone_name): # Método para buscar el lateral simétrico
            sym_bone_name = replace_lateral(bone_name)
            return sym_bone_name if sym_bone_name != bone_name else ''


        def copy_modifier_attributes(source_mod, target_mod): # Método para copiar los atributos de un modifier de un objeto a otro
            common_attributes = ['mute', 'active', 'use_influence', 'influence', 'use_restricted_range', 'frame_start', 'frame_end', 'blend_in', 'blend_out']
            generator_attributes = ['mode', 'use_additive', 'poly_order', 'coefficients']
            fcurve_generator_attributes = ['function_type', 'use_additive', 'amplitude', 'phase_multiplier', 'phase_offset', 'value_offset']
            envelope_attributes = ['reference_value', 'default_min', 'default_max']
            cycles_attributes = ['mode_before', 'cycles_before', 'mode_after', 'cycles_after']
            noise_attributes = ['blend_type', 'scale', 'strength', 'offset', 'phase', 'depth']
            limit_attributes = ['use_min_x', 'min_x', 'use_min_y', 'min_y', 'use_max_x', 'max_x', 'use_max_y', 'max_y']
            stepped_attributes = ['frame_step', 'frame_offset', 'use_frame_start', 'frame_start', 'use_frame_end', 'frame_end']

            all_attributes = [common_attributes, generator_attributes, fcurve_generator_attributes, envelope_attributes, cycles_attributes, noise_attributes, limit_attributes, stepped_attributes]

            for attributes in all_attributes: # Iterar cada Modifier
                try:
                    for att in attributes: # Iterar cada atributo del Modifier actual
                        setattr(target_mod, att, getattr(source_mod, att)) # Configurar el atributo del nuevo driver copiando el original
                except AttributeError:
                    pass

        s_bones = [bone.name for bone in bpy.context.selected_pose_bones] # Obtener la lista de huesos seleccionados

        all_bones = [] # Obtener la lista de todos los nombres de huesos en cada armature en la escena
        for obj in bpy.context.scene.objects:
            if obj.type == 'ARMATURE':
                all_bones.extend([bone.name for bone in obj.pose.bones])

        # OBTENER LOS DRIVERS ---------------------------------------------------------------------------------------------------------------
        for arm in bpy.context.scene.objects: # Iterar cada OBJETO de los SELECCIONADO actualmente
            if arm.type == 'ARMATURE': # Si el OBJETO ACTUAL es un ARMATURE
                for d in range(len(arm.animation_data.drivers)): # Iterar cada DRIVER en el ARMATURE ACTUAL
                    drv = arm.animation_data.drivers[d] # Obtener el driver con index actual [d]
                    dpath = drv.data_path # Obtener el data_path del driver actual
                    property = dpath[dpath.rfind('.')+1:] # Obtener el nombre de la Driven Property
                    axis = drv.array_index # Obtener el index de Driven Property
                    bone = re.search(r'"(.*?)"', dpath).group(1) # Obtener el nombre del bone OWNER 
                    
                    constraint = None # Crear una variable para almacenar el nombre del posible CONSTRAINT
                    if re.search(r'\.constraints\["(.+?)"]', dpath):
                        constraint = re.search(r'\.constraints\["(.+?)"]', dpath).group(1)
                    else:
                        del constraint
                    
                    sym_bone = find_symm_bone(bone) # Comprobar que su simétrico existe
                    if bone in s_bones and sym_bone and sym_bone in all_bones: # Si el bone está seleccionado y su simétrico existe
                        bone = sym_bone # Simetrizar el nombre
                    
                        # Intentar crear el driver simétrico
                        try: drv_new = arm.pose.bones[bone].constraints[constraint].driver_add(property) # Intentamos crear el driver en un Constraint
                        except Exception: pass # Si no es posible, pasar al siguiente
                        try: drv_new = arm.pose.bones[bone].driver_add(property, axis) # Intentamos crear el driver en un Transform
                        except Exception: pass # Si no es posible, pasar al siguiente
                        
                        # CONFIGURAR LAS PROPIEDADES DEL DRIVER -----------------------------------------------------------------------------
                        drv_new.driver.type = drv.driver.type # Copiar el tipo de Driver SCRIPTED, AVERAGE, SUM, MIN o MAX
                        drv_new.driver.expression = drv.driver.expression  # Copiar la expression, por si la hubiera
                        drv_new.driver.use_self = drv.driver.use_self  # Copiar el valor de la casilla use_self por si hubiera expression
                        
                        
                        # CONFIGURAR LAS VARIABLES DEL DRIVER -------------------------------------------------------------------------------  
                        for i in range(len(drv.driver.variables)): # Obtener la longitud de la matriz de variables para iterar
                            var = drv_new.driver.variables.new()  # Crear una nueva variable y la almacenar en var para pegar sus propiedades
                            var.name = drv.driver.variables[i].name  # Pegar el nombre de cada variable
                            var.type = drv.driver.variables[i].type  # Pegar el tipo: SINGLE_PROP, TRANSFORMS, ROTATION_DIFF, LOC_DIFF
                                        
                            for j in range(len(drv.driver.variables[i].targets)):  # Iterar cada target de cada variable
                                try: var.targets[j].id_type = drv.driver.variables[i].targets[j].id_type # Se intenta pegar el Object
                                except AttributeError: pass  # Si el tipo de variable no es SINGLE_PROP, no se puede, así que pasamos
                                var.targets[j].id = drv.driver.variables[i].targets[j].id # El id del Object será siempre el Armature 
                                var.targets[j].bone_target = find_symm_bone(drv.driver.variables[i].targets[j].bone_target) # Invertir el posible bone_target
                                var.targets[j].data_path = find_symm_bone(drv.driver.variables[i].targets[j].data_path) # Invertir el posible data_path
                                var.targets[j].transform_type = drv.driver.variables[i].targets[j].transform_type  # Solo para type TRANSFORMS
                                var.targets[j].rotation_mode = drv.driver.variables[i].targets[j].rotation_mode  # Solo para transform ROTATION
                                var.targets[j].transform_space = drv.driver.variables[i].targets[j].transform_space  # Solo para type TRANSFORMS y LOC_DIFF
                                                               
                        # CONFIGURAR LAS PROPIEDADES DE LA F-CURVE --------------------------------------------------------------------------
                        drv_new.keyframe_points.add(len(drv.keyframe_points))  # Añadir a la fcurve tantos keyframes como tiene la original
                        KEYattributes = ['extrapolation', 'color_mode', 'color', 'auto_smoothing']  # Almacenar los atributos de la curva
                        for att in KEYattributes:  #Iterar por los atributos de la curva para pegar los del original
                            setattr(drv_new, att, getattr(drv, att))
                        if len(drv.keyframe_points) > 0: #Si la Fcurve original tiene keyframe_points
                            drv_new.keyframe_points.add(count=len(drv.keyframe_points)) #añadir tantos puntos como la longitud de la Fcurve original
                            for p in range(len(drv.keyframe_points)):  # Iterar los keyframes
                                PNTattributes = ['interpolation', 'co', 'handle_left_type', 'handle_left', 'handle_right_type', 'handle_right']
                                for att in PNTattributes:  #  Iterar pegando los valores de los originales de cada coordenada, handles y sus tipos
                                    setattr(drv_new.keyframe_points[p], att, getattr(drv.keyframe_points[p], att))
                            drv_new.keyframe_points.sort() # Asegurar de que todos los puntos estan organizados cronologicamente

                        # CONFIGURAR LAS PROPIEDADES DE LOS MODIFIERS (iterar cada modifier) ------------------------------------------------
                        drv_new.modifiers.remove(drv_new.modifiers[0]) # Eliminar el modificador que se genera automáticamente
                        for drv_mod in drv.modifiers:  # Iterar por cada modificador que contenga el driver original
                            drvM = drv_new.modifiers.new(drv_mod.type)  # Crear un nuevo modifier del mismo tipo
                            copy_modifier_attributes(drv_mod, drvM) # Llamar a la funcion de copiar atributos
                       
        bpy.ops.object.mode_set(mode='EDIT') # Volver a EDIT MODE

        return {'FINISHED'}

def register():
    bpy.utils.register_class(SymDriversOperator)
    bpy.types.VIEW3D_MT_edit_armature.append(menu_func)
    bpy.types.VIEW3D_MT_armature_context_menu.append(context_menu_func)

def unregister():
    bpy.utils.unregister_class(SymDriversOperator)
    bpy.types.VIEW3D_MT_edit_armature.remove(menu_func)
    bpy.types.VIEW3D_MT_armature_context_menu.remove(context_menu_func)

def menu_func(self, context):
    self.layout.operator("object.sym_drivers")

def context_menu_func(self, context):
    self.layout.operator("object.sym_drivers")

if __name__ == "__main__":
    register()
