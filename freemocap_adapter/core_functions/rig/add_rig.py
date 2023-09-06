import math as m

import bpy
import mathutils

from freemocap_adapter.core_functions.bones.calculate_bone_length_statistics import calculate_bone_length_statistics
from freemocap_adapter.core_functions.empties.update_empty_positions import get_empty_positions
from freemocap_adapter.data_models.bones.bone_definitions import VIRTUAL_BONES
from freemocap_adapter.data_models.bones.bone_constraints import BONES_CONSTRAINTS


def add_rig(bone_length_method: str = 'median_length',
            keep_symmetry: bool = False,
            add_fingers_constraints: bool = False,
            use_limit_rotation: bool = False):
    # Deselect all objects
    for object in bpy.data.objects:
        object.select_set(False)

    # If there is an existing metarig, delete it
    try:
        print('Deleting previous metarigs...')
        for object in bpy.data.objects:
            if object.type == "ARMATURE":
                bpy.data.objects.remove(object, do_unlink=True)
    except:
        print('No existing metarigs to delete')

    # Add normal human armature
    bpy.ops.object.armature_human_metarig_add()
    # Rename metarig armature to "root"
    bpy.data.armatures[0].name = "root"
    # Get reference to armature
    rig = bpy.data.objects['metarig']
    # Rename the rig object to root
    rig.name = "root"
    # Get reference to the renamed armature
    rig = bpy.data.objects['root']

    if bone_length_method == 'median_length':

        print('Adding rig with median length method...')

        # Update the empty positions dictionary
        get_empty_positions()

        # Update the information of the virtual bones
        calculate_bone_length_statistics()

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        # Select the only the rig
        rig.select_set(True)

        # Get rig height as the sum of the major bones length in a standing position. Assume foot declination angle of 23º
        avg_ankle_projection_length = (m.sin(m.radians(23)) * VIRTUAL_BONES['foot.R']['median'] + m.sin(m.radians(23)) *
                                       VIRTUAL_BONES['foot.L']['median']) / 2
        avg_shin_length = (VIRTUAL_BONES['shin.R']['median'] + VIRTUAL_BONES['shin.L']['median']) / 2
        avg_thigh_length = (VIRTUAL_BONES['thigh.R']['median'] + VIRTUAL_BONES['thigh.L']['median']) / 2

        rig_height = avg_ankle_projection_length + avg_shin_length + avg_thigh_length + VIRTUAL_BONES['spine'][
            'median'] + VIRTUAL_BONES['spine.001']['median'] + VIRTUAL_BONES['neck']['median']

        # Calculate new rig proportion
        rig_new_proportion = rig_height / rig.dimensions.z
        # Scale the rig by the new proportion
        rig.scale = (rig_new_proportion, rig_new_proportion, rig_new_proportion)

        # Apply transformations to rig (scale must be (1, 1, 1) so it doesn't fail on send2ue export
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Get references to the different rig bones
        bpy.ops.object.mode_set(mode='EDIT')

        spine = rig.data.edit_bones['spine']
        spine_003 = rig.data.edit_bones['spine.003']
        spine_004 = rig.data.edit_bones['spine.004']
        spine_005 = rig.data.edit_bones['spine.005']
        spine_006 = rig.data.edit_bones['spine.006']
        face = rig.data.edit_bones['face']
        nose = rig.data.edit_bones['nose']
        breast_R = rig.data.edit_bones['breast.R']
        breast_L = rig.data.edit_bones['breast.L']
        shoulder_R = rig.data.edit_bones['shoulder.R']
        shoulder_L = rig.data.edit_bones['shoulder.L']
        upper_arm_R = rig.data.edit_bones['upper_arm.R']
        upper_arm_L = rig.data.edit_bones['upper_arm.L']
        forearm_R = rig.data.edit_bones['forearm.R']
        forearm_L = rig.data.edit_bones['forearm.L']
        hand_R = rig.data.edit_bones['hand.R']
        hand_L = rig.data.edit_bones['hand.L']
        pelvis_R = rig.data.edit_bones['pelvis.R']
        pelvis_L = rig.data.edit_bones['pelvis.L']
        thigh_R = rig.data.edit_bones['thigh.R']
        thigh_L = rig.data.edit_bones['thigh.L']
        shin_R = rig.data.edit_bones['shin.R']
        shin_L = rig.data.edit_bones['shin.L']
        foot_R = rig.data.edit_bones['foot.R']
        foot_L = rig.data.edit_bones['foot.L']
        toe_R = rig.data.edit_bones['toe.R']
        toe_L = rig.data.edit_bones['toe.L']
        heel_02_R = rig.data.edit_bones['heel.02.R']
        heel_02_L = rig.data.edit_bones['heel.02.L']

        # Get the hips_center z position as the sum of heel, shin and thigh lengths
        hips_center_z_pos = avg_ankle_projection_length + avg_shin_length + avg_thigh_length

        # Move the spine and pelvis bone heads to the point (0, 0, hips_center_z_pos)
        spine.head = (0, 0, hips_center_z_pos)
        pelvis_R.head = (0, 0, hips_center_z_pos)
        pelvis_L.head = (0, 0, hips_center_z_pos)

        # Calculate the average length of the pelvis bones
        avg_pelvis_length = (VIRTUAL_BONES['pelvis.R']['median'] + VIRTUAL_BONES['pelvis.L']['median']) / 2

        # Set the pelvis bones length based on the keep symmetry parameter
        pelvis_R_length = avg_pelvis_length if keep_symmetry else VIRTUAL_BONES['pelvis.R']['median']
        pelvis_L_length = avg_pelvis_length if keep_symmetry else VIRTUAL_BONES['pelvis.L']['median']

        # Align the pelvis bone tails to the hips center
        pelvis_R.tail = (-pelvis_R_length, 0, hips_center_z_pos)
        pelvis_L.tail = (pelvis_L_length, 0, hips_center_z_pos)
        # Reset pelvis bones rotations
        pelvis_R.roll = 0
        pelvis_L.roll = 0

        # Move thighs bone head to the position of corresponding pelvis bone tail
        thigh_R.head = (-pelvis_R_length, 0, hips_center_z_pos)
        thigh_L.head = (pelvis_L_length, 0, hips_center_z_pos)

        # Set the thigh bones length based on the keep symmetry parameter
        thigh_R_length = avg_thigh_length if keep_symmetry else VIRTUAL_BONES['thigh.R']['median']
        thigh_L_length = avg_thigh_length if keep_symmetry else VIRTUAL_BONES['thigh.L']['median']

        # Align the thighs bone tail to the bone head
        thigh_R.tail = (-pelvis_R_length, 0, hips_center_z_pos - thigh_R_length)
        thigh_L.tail = (pelvis_L_length, 0, hips_center_z_pos - thigh_L_length)

        # Set the shin bones length based on the keep symmetry parameter
        shin_R_length = avg_shin_length if keep_symmetry else VIRTUAL_BONES['shin.R']['median']
        shin_L_length = avg_shin_length if keep_symmetry else VIRTUAL_BONES['shin.L']['median']

        # Align the shin bones to the thigh bones
        shin_R.tail = (-pelvis_R_length, 0, hips_center_z_pos - thigh_R_length - shin_R_length)
        shin_L.tail = (pelvis_L_length, 0, hips_center_z_pos - thigh_L_length - shin_L_length)

        # Remove the toe bones
        rig.data.edit_bones.remove(rig.data.edit_bones['toe.R'])
        rig.data.edit_bones.remove(rig.data.edit_bones['toe.L'])

        # Move the foot bones tail to adjust their length depending on keep symmetry and also form a 23º degree with the horizontal plane
        avg_foot_length = (VIRTUAL_BONES['foot.R']['median'] + VIRTUAL_BONES['foot.L']['median']) / 2

        # Set the foot bones length based on the keep symmetry parameter
        foot_R_length = avg_foot_length if keep_symmetry else VIRTUAL_BONES['foot.R']['median']
        foot_L_length = avg_foot_length if keep_symmetry else VIRTUAL_BONES['foot.L']['median']

        foot_R.tail = (
        -pelvis_R_length, -foot_R_length * m.cos(m.radians(23)), foot_R.head[2] - foot_R_length * m.sin(m.radians(23)))
        foot_L.tail = (
        pelvis_L_length, -foot_L_length * m.cos(m.radians(23)), foot_L.head[2] - foot_L_length * m.sin(m.radians(23)))

        # Move the heel bones so their head is aligned with the ankle on the x axis
        avg_heel_length = (VIRTUAL_BONES['heel.02.R']['median'] + VIRTUAL_BONES['heel.02.L']['median']) / 2

        # Set the heel bones length based on the keep symmetry parameter
        heel_02_R_length = avg_heel_length if keep_symmetry else VIRTUAL_BONES['heel.02.R']['median']
        heel_02_L_length = avg_heel_length if keep_symmetry else VIRTUAL_BONES['heel.02.L']['median']

        heel_02_R.head = (-pelvis_R_length, heel_02_R.head[1], heel_02_R.head[2])
        heel_02_R.length = heel_02_R_length
        heel_02_L.head = (pelvis_L_length, heel_02_L.head[1], heel_02_L.head[2])
        heel_02_L.length = heel_02_L_length

        # Make the heel bones be connected with the shin bones
        heel_02_R.parent = shin_R
        heel_02_R.use_connect = True
        heel_02_L.parent = shin_L
        heel_02_L.use_connect = True

        # Add a pelvis bone to the root and then make it the parent of spine, pelvis.R and pelvis.L bones
        pelvis = rig.data.edit_bones.new('pelvis')
        pelvis.head = spine.head
        pelvis.tail = spine.head + mathutils.Vector([0, 0.1, 0])

        # Change the pelvis.R, pelvis.L, thigh.R, thigh.L and spine parent to the new pelvis bone
        pelvis_R.parent = pelvis
        pelvis_R.use_connect = False
        pelvis_L.parent = pelvis
        pelvis_L.use_connect = False
        thigh_R.parent = pelvis
        thigh_R.use_connect = False
        thigh_L.parent = pelvis
        thigh_L.use_connect = False
        spine.parent = pelvis
        spine.use_connect = False

        # Change parent of spine.003 bone to spine to erase bones spine.001 and spine.002
        spine_003.parent = spine
        spine_003.use_connect = True
        # Remove spine.001 and spine.002 bones
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.001'])
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.002'])

        # Rename spine.003 to spine.001
        rig.data.edit_bones['spine.003'].name = "spine.001"
        spine_001 = rig.data.edit_bones['spine.001']

        # Adjust the spine bone length and align it vertically
        spine.tail = (spine.head[0], spine.head[1], spine.head[2] + VIRTUAL_BONES['spine']['median'])

        # Adjust the spine.001 bone length and align it vertically
        spine_001.tail = (
        spine_001.head[0], spine_001.head[1], spine_001.head[2] + VIRTUAL_BONES['spine.001']['median'])

        # Calculate the shoulders head z offset from the spine.001 tail. This to raise the shoulders and breasts by that offset
        shoulder_z_offset = spine_001.tail[2] - shoulder_R.head[2]

        # Raise breasts and shoulders by the z offset
        breast_R.head[2] += shoulder_z_offset
        breast_R.tail[2] += shoulder_z_offset
        breast_L.head[2] += shoulder_z_offset
        breast_L.tail[2] += shoulder_z_offset
        shoulder_R.head[2] += shoulder_z_offset
        shoulder_R.tail[2] += shoulder_z_offset
        shoulder_L.head[2] += shoulder_z_offset
        shoulder_L.tail[2] += shoulder_z_offset

        # Get average shoulder length
        avg_shoulder_length = (VIRTUAL_BONES['shoulder.R']['median'] + VIRTUAL_BONES['shoulder.L']['median']) / 2

        # Set the shoulder bones length based on the keep symmetry parameter
        shoulder_R_length = avg_shoulder_length if keep_symmetry else VIRTUAL_BONES['shoulder.R']['median']
        shoulder_L_length = avg_shoulder_length if keep_symmetry else VIRTUAL_BONES['shoulder.L']['median']

        # Move the shoulder tail in the x axis
        shoulder_R.tail[0] = spine_001.tail[0] - shoulder_R_length
        shoulder_L.tail[0] = spine_001.tail[0] + shoulder_L_length

        # Calculate the upper_arms head x and z offset from the shoulder_R tail. This to raise and adjust the arms and hands by that offset
        upper_arm_R_x_offset = shoulder_R.tail[0] - upper_arm_R.head[0]
        upper_arm_R_z_offset = spine_001.tail[2] - upper_arm_R.head[2]
        upper_arm_L_x_offset = shoulder_L.tail[0] - upper_arm_L.head[0]
        upper_arm_L_z_offset = spine_001.tail[2] - upper_arm_L.head[2]

        upper_arm_R.head[2] += upper_arm_R_z_offset
        upper_arm_R.tail[2] += upper_arm_R_z_offset
        upper_arm_R.head[0] += upper_arm_R_x_offset
        upper_arm_R.tail[0] += upper_arm_R_x_offset
        for bone in upper_arm_R.children_recursive:
            if not bone.use_connect:
                bone.head[2] += upper_arm_R_z_offset
                bone.tail[2] += upper_arm_R_z_offset
                bone.head[0] += upper_arm_R_x_offset
                bone.tail[0] += upper_arm_R_x_offset
            else:
                bone.tail[2] += upper_arm_R_z_offset
                bone.tail[0] += upper_arm_R_x_offset

        upper_arm_L.head[2] += upper_arm_L_z_offset
        upper_arm_L.tail[2] += upper_arm_L_z_offset
        upper_arm_L.head[0] += upper_arm_L_x_offset
        upper_arm_L.tail[0] += upper_arm_L_x_offset
        for bone in upper_arm_L.children_recursive:
            if not bone.use_connect:
                bone.head[2] += upper_arm_L_z_offset
                bone.tail[2] += upper_arm_L_z_offset
                bone.head[0] += upper_arm_L_x_offset
                bone.tail[0] += upper_arm_L_x_offset
            else:
                bone.tail[2] += upper_arm_L_z_offset
                bone.tail[0] += upper_arm_L_x_offset

        # Align the y position of breasts, shoulders, arms and hands to the y position of the spine.001 tail
        # Calculate the breasts head y offset from the spine.001 tail
        breast_y_offset = spine_001.tail[1] - breast_R.head[1]
        # Move breast by the y offset
        breast_R.head[1] += breast_y_offset
        breast_R.tail[1] += breast_y_offset
        breast_L.head[1] += breast_y_offset
        breast_L.tail[1] += breast_y_offset

        # Temporarily remove breast bones. (Comment these lines if breast bones are needed)
        rig.data.edit_bones.remove(rig.data.edit_bones[breast_R.name])
        rig.data.edit_bones.remove(rig.data.edit_bones[breast_L.name])

        # Set the y position to which the arms bones will be aligned
        arms_bones_y_pos = spine_001.tail[1]
        # Move shoulders on y axis and also move shoulders head to the center at x=0 ,
        shoulder_R.head[1] = arms_bones_y_pos
        shoulder_R.head[0] = 0
        shoulder_R.tail[1] = arms_bones_y_pos
        shoulder_L.head[1] = arms_bones_y_pos
        shoulder_L.head[0] = 0
        shoulder_L.tail[1] = arms_bones_y_pos

        # Move upper_arm and forearm
        upper_arm_R.head[1] = arms_bones_y_pos
        upper_arm_R.tail[1] = arms_bones_y_pos
        upper_arm_L.head[1] = arms_bones_y_pos
        upper_arm_L.tail[1] = arms_bones_y_pos

        # Calculate hand head y offset to arms_bones_y_pos to move the whole hand
        hand_R_y_offset = arms_bones_y_pos - hand_R.head[1]
        hand_L_y_offset = arms_bones_y_pos - hand_L.head[1]

        # Move hands and its children by the y offset (forearm tail is moved by hand head)
        hand_R.head[1] += hand_R_y_offset
        hand_R.tail[1] += hand_R_y_offset
        for bone in hand_R.children_recursive:
            if not bone.use_connect:
                bone.head[1] += hand_R_y_offset
                bone.tail[1] += hand_R_y_offset
            else:
                bone.tail[1] += hand_R_y_offset

        hand_L.head[1] += hand_L_y_offset
        hand_L.tail[1] += hand_L_y_offset
        for bone in hand_L.children_recursive:
            if not bone.use_connect:
                bone.head[1] += hand_L_y_offset
                bone.tail[1] += hand_L_y_offset
            else:
                bone.tail[1] += hand_L_y_offset

        # Change to Pose Mode to rotate the arms and make a T Pose for posterior retargeting
        bpy.ops.object.mode_set(mode='POSE')
        pose_upper_arm_R = rig.pose.bones['upper_arm.R']
        pose_upper_arm_R.rotation_mode = 'XYZ'
        pose_upper_arm_R.rotation_euler = (0, m.radians(-7), m.radians(-29))
        pose_upper_arm_R.rotation_mode = 'QUATERNION'
        pose_upper_arm_L = rig.pose.bones['upper_arm.L']
        pose_upper_arm_L.rotation_mode = 'XYZ'
        pose_upper_arm_L.rotation_euler = (0, m.radians(7), m.radians(29))
        pose_upper_arm_L.rotation_mode = 'QUATERNION'
        pose_forearm_R = rig.pose.bones['forearm.R']
        pose_forearm_R.rotation_mode = 'XYZ'
        pose_forearm_R.rotation_euler = (0, 0, m.radians(-4))
        pose_forearm_R.rotation_mode = 'QUATERNION'
        pose_forearm_L = rig.pose.bones['forearm.L']
        pose_forearm_L.rotation_mode = 'XYZ'
        pose_forearm_L.rotation_euler = (0, 0, m.radians(4))
        pose_forearm_L.rotation_mode = 'QUATERNION'
        pose_hand_R = rig.pose.bones['hand.R']
        pose_hand_R.rotation_mode = 'XYZ'
        pose_hand_R.rotation_euler = (m.radians(-5.7), 0, m.radians(-3.7))
        pose_hand_R.rotation_mode = 'QUATERNION'
        pose_hand_L = rig.pose.bones['hand.L']
        pose_hand_L.rotation_mode = 'XYZ'
        pose_hand_L.rotation_euler = (m.radians(-5.7), 0, m.radians(3.7))
        pose_hand_L.rotation_mode = 'QUATERNION'
        pose_thigh_R = rig.pose.bones['thigh.R']
        pose_thigh_R.rotation_mode = 'XYZ'
        pose_thigh_R.rotation_euler = (0, 0, m.radians(3))
        pose_thigh_R.rotation_mode = 'QUATERNION'
        pose_foot_R = rig.pose.bones['foot.R']
        pose_foot_R.rotation_mode = 'XYZ'
        pose_foot_R.rotation_euler = (0, 0, m.radians(4))
        pose_foot_R.rotation_mode = 'QUATERNION'
        pose_thigh_L = rig.pose.bones['thigh.L']
        pose_thigh_L.rotation_mode = 'XYZ'
        pose_thigh_L.rotation_euler = (0, 0, m.radians(-3))
        pose_thigh_L.rotation_mode = 'QUATERNION'
        pose_foot_L = rig.pose.bones['foot.L']
        pose_foot_L.rotation_mode = 'XYZ'
        pose_foot_L.rotation_euler = (0, 0, m.radians(-4))
        pose_foot_L.rotation_mode = 'QUATERNION'

        # Apply the actual pose to the rest pose
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=False)

        # Change mode to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Get new bone references
        upper_arm_R = rig.data.edit_bones['upper_arm.R']
        upper_arm_L = rig.data.edit_bones['upper_arm.L']
        forearm_R = rig.data.edit_bones['forearm.R']
        forearm_L = rig.data.edit_bones['forearm.L']
        hand_R = rig.data.edit_bones['hand.R']
        hand_L = rig.data.edit_bones['hand.L']

        # Get average upperarm length
        avg_upper_arm_length = (VIRTUAL_BONES['upper_arm.R']['median'] + VIRTUAL_BONES['upper_arm.L']['median']) / 2

        # Set the upperarm bones length based on the keep symmetry parameter
        upper_arm_R_length = avg_upper_arm_length if keep_symmetry else VIRTUAL_BONES['upper_arm.R']['median']
        upper_arm_L_length = avg_upper_arm_length if keep_symmetry else VIRTUAL_BONES['upper_arm.L']['median']

        # Move the upper_arm tail in the x axis
        upper_arm_R.tail[0] = upper_arm_R.head[0] - upper_arm_R_length
        upper_arm_L.tail[0] = upper_arm_L.head[0] + upper_arm_L_length

        # Get average forearm length
        avg_forearm_length = (VIRTUAL_BONES['forearm.R']['median'] + VIRTUAL_BONES['forearm.L']['median']) / 2

        # Set the forearm bones length based on the keep symmetry parameter
        forearm_R_length = avg_forearm_length if keep_symmetry else VIRTUAL_BONES['forearm.R']['median']
        forearm_L_length = avg_forearm_length if keep_symmetry else VIRTUAL_BONES['forearm.L']['median']

        # Calculate the x axis offset of the current forearm tail x position and the forearm head x position plus the calculated forearm length
        # This is to move the forearm tail and all the hand bones
        forearm_R_tail_x_offset = (forearm_R.head[0] - forearm_R_length) - forearm_R.tail[0]
        forearm_L_tail_x_offset = (forearm_L.head[0] + forearm_L_length) - forearm_L.tail[0]

        # Move forearms tail and its children by the x offset
        forearm_R.tail[0] += forearm_R_tail_x_offset
        for bone in forearm_R.children_recursive:
            if not bone.use_connect:
                bone.head[0] += forearm_R_tail_x_offset
                bone.tail[0] += forearm_R_tail_x_offset
            else:
                bone.tail[0] += forearm_R_tail_x_offset

        forearm_L.tail[0] += forearm_L_tail_x_offset
        for bone in forearm_L.children_recursive:
            if not bone.use_connect:
                bone.head[0] += forearm_L_tail_x_offset
                bone.tail[0] += forearm_L_tail_x_offset
            else:
                bone.tail[0] += forearm_L_tail_x_offset

        #############################################################
        ### DEBUG ###
        if False:
            # Add an auxiliary bone to the side of the upperarms and forearms to check their rotation
            upper_arm_R_Rot = rig.data.edit_bones.new('uppe_rarm.R.Rot')
            upper_arm_R_Rot.head = (
            upper_arm_R.head[0] - upper_arm_R_length / 2, upper_arm_R.head[1], upper_arm_R.head[2])
            upper_arm_R_Rot.tail = (upper_arm_R_Rot.head[0], upper_arm_R_Rot.head[1], upper_arm_R_Rot.head[2] + 0.1)
            upper_arm_R_Rot.parent = upper_arm_R
            upper_arm_R_Rot.use_connect = False
            upper_arm_L_Rot = rig.data.edit_bones.new('uppe_rarm.L.Rot')
            upper_arm_L_Rot.head = (
            upper_arm_L.head[0] + upper_arm_L_length / 2, upper_arm_L.head[1], upper_arm_L.head[2])
            upper_arm_L_Rot.tail = (upper_arm_L_Rot.head[0], upper_arm_L_Rot.head[1], upper_arm_L_Rot.head[2] + 0.1)
            upper_arm_L_Rot.parent = upper_arm_L
            upper_arm_L_Rot.use_connect = False
            forearm_R_Rot = rig.data.edit_bones.new('uppe_rarm.R.Rot')
            forearm_R_Rot.head = (forearm_R.head[0] - forearm_R_length / 2, forearm_R.head[1], forearm_R.head[2])
            forearm_R_Rot.tail = (forearm_R_Rot.head[0], forearm_R_Rot.head[1], forearm_R_Rot.head[2] + 0.1)
            forearm_R_Rot.parent = forearm_R
            forearm_R_Rot.use_connect = False
            forearm_L_Rot = rig.data.edit_bones.new('uppe_rarm.L.Rot')
            forearm_L_Rot.head = (forearm_L.head[0] + forearm_L_length / 2, forearm_L.head[1], forearm_L.head[2])
            forearm_L_Rot.tail = (forearm_L_Rot.head[0], forearm_L_Rot.head[1], forearm_L_Rot.head[2] + 0.1)
            forearm_L_Rot.parent = forearm_L
            forearm_L_Rot.use_connect = False
        #############################################################

        # Get average hand length
        avg_hand_length = (VIRTUAL_BONES['hand.R']['median'] + VIRTUAL_BONES['hand.L']['median']) / 2

        # Set the forearm bones length based on the keep symmetry parameter
        hand_R_length = avg_hand_length if keep_symmetry else VIRTUAL_BONES['hand.R']['median']
        hand_L_length = avg_hand_length if keep_symmetry else VIRTUAL_BONES['hand.L']['median']

        # Move hands tail to match the average length
        hand_R.tail[0] = hand_R.head[0] - hand_R_length
        hand_L.tail[0] = hand_L.head[0] + hand_L_length

        ### Adjust the position of the neck, head and face bones ###
        spine_001 = rig.data.edit_bones['spine.001']
        spine_004 = rig.data.edit_bones['spine.004']
        nose = rig.data.edit_bones['nose']
        nose_001 = rig.data.edit_bones['nose.001']

        # Set spine.004 bone head position equal to the spine.001 tail
        spine_004.head = (spine_001.tail[0], spine_001.tail[1], spine_001.tail[2])

        # Change spine.004 tail position values
        spine_004.tail = (spine_004.head[0], spine_004.head[1], spine_004.head[2] + VIRTUAL_BONES['neck']['median'])

        # Change the parent of the face bone for the spine.004 bone
        face = rig.data.edit_bones['face']
        face.parent = spine_004
        face.use_connect = False

        # Remove spine.005 and spine.006 bones
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.005'])
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.006'])

        # Calculate the y and z offset of the nose.001 bone tail using the imaginary head_nose bone. Assume a 18º of declination angle
        nose_y_offset = -VIRTUAL_BONES['head_nose']['median'] * m.cos(m.radians(18)) - nose_001.tail[1]
        nose_z_offset = (spine_004.tail[2] - VIRTUAL_BONES['head_nose']['median'] * m.sin(m.radians(18))) - \
                        nose_001.tail[2]

        # Move the face bone on the z axis using the calculated offset
        face.head[2] += nose_z_offset
        face.tail[2] += nose_z_offset

        # Move on the y and z axis the children bones from the face bone using the calculated offsets
        for bone in face.children_recursive:
            if not bone.use_connect:
                bone.head[1] += nose_y_offset
                bone.tail[1] += nose_y_offset
                bone.head[2] += nose_z_offset
                bone.tail[2] += nose_z_offset
            else:
                bone.tail[1] += nose_y_offset
                bone.tail[2] += nose_z_offset

        # Move the face bone head to align it horizontally
        face.head[1] = spine_004.tail[1]
        face.head[2] = face.tail[2]
        face.tail[1] = face.head[1] - (VIRTUAL_BONES['head_nose']['median'] * m.cos(m.radians(18)) / 2)

        # Rename spine.004 to neck
        rig.data.edit_bones['spine.004'].name = "neck"

        # Rotate the spine and neck bones to complete the TPOSE
        bpy.ops.object.mode_set(mode='POSE')

        pose_spine = rig.pose.bones['spine']
        pose_spine.rotation_mode = 'XYZ'
        pose_spine.rotation_euler = (m.radians(3), 0, 0)
        pose_spine.rotation_mode = 'QUATERNION'
        pose_spine_001 = rig.pose.bones['spine.001']
        pose_spine_001.rotation_mode = 'XYZ'
        pose_spine_001.rotation_euler = (m.radians(-10), 0, 0)
        pose_spine_001.rotation_mode = 'QUATERNION'
        pose_neck = rig.pose.bones['neck']
        pose_neck.rotation_mode = 'XYZ'
        pose_neck.rotation_euler = (m.radians(6), 0, 0)
        pose_neck.rotation_mode = 'QUATERNION'

        # Apply the actual pose to the rest pose
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=False)

        # Adjust the fingers

        # Change mode to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Get new bone references
        hand_R = rig.data.edit_bones['hand.R']
        hand_L = rig.data.edit_bones['hand.L']
        palm_01_R = rig.data.edit_bones['palm.01.R']
        palm_01_L = rig.data.edit_bones['palm.01.L']
        palm_02_R = rig.data.edit_bones['palm.02.R']
        palm_02_L = rig.data.edit_bones['palm.02.L']
        palm_03_R = rig.data.edit_bones['palm.03.R']
        palm_03_L = rig.data.edit_bones['palm.03.L']
        palm_04_R = rig.data.edit_bones['palm.04.R']
        palm_04_L = rig.data.edit_bones['palm.04.L']
        thumb_01_R = rig.data.edit_bones['thumb.01.R']
        thumb_01_L = rig.data.edit_bones['thumb.01.L']
        thumb_02_R = rig.data.edit_bones['thumb.02.R']
        thumb_02_L = rig.data.edit_bones['thumb.02.L']
        thumb_03_R = rig.data.edit_bones['thumb.03.R']
        thumb_03_L = rig.data.edit_bones['thumb.03.L']
        f_index_01_R = rig.data.edit_bones['f_index.01.R']
        f_index_01_L = rig.data.edit_bones['f_index.01.L']
        f_index_02_R = rig.data.edit_bones['f_index.02.R']
        f_index_02_L = rig.data.edit_bones['f_index.02.L']
        f_index_03_R = rig.data.edit_bones['f_index.03.R']
        f_index_03_L = rig.data.edit_bones['f_index.03.L']
        f_middle_01_R = rig.data.edit_bones['f_middle.01.R']
        f_middle_01_L = rig.data.edit_bones['f_middle.01.L']
        f_middle_02_R = rig.data.edit_bones['f_middle.02.R']
        f_middle_02_L = rig.data.edit_bones['f_middle.02.L']
        f_middle_03_R = rig.data.edit_bones['f_middle.03.R']
        f_middle_03_L = rig.data.edit_bones['f_middle.03.L']
        f_ring_01_R = rig.data.edit_bones['f_ring.01.R']
        f_ring_01_L = rig.data.edit_bones['f_ring.01.L']
        f_ring_02_R = rig.data.edit_bones['f_ring.02.R']
        f_ring_02_L = rig.data.edit_bones['f_ring.02.L']
        f_ring_03_R = rig.data.edit_bones['f_ring.03.R']
        f_ring_03_L = rig.data.edit_bones['f_ring.03.L']
        f_pinky_01_R = rig.data.edit_bones['f_pinky.01.R']
        f_pinky_01_L = rig.data.edit_bones['f_pinky.01.L']
        f_pinky_02_R = rig.data.edit_bones['f_pinky.02.R']
        f_pinky_02_L = rig.data.edit_bones['f_pinky.02.L']
        f_pinky_03_R = rig.data.edit_bones['f_pinky.03.R']
        f_pinky_03_L = rig.data.edit_bones['f_pinky.03.L']

        # Add the thumb carpals
        thumb_carpal_R = rig.data.edit_bones.new('thumb.carpal.R')
        thumb_carpal_R.head = hand_R.head
        thumb_carpal_R.tail = thumb_carpal_R.head + mathutils.Vector([0, -VIRTUAL_BONES['thumb.carpal.R']['median'], 0])
        thumb_carpal_L = rig.data.edit_bones.new('thumb.carpal.L')
        thumb_carpal_L.head = hand_L.head
        thumb_carpal_L.tail = thumb_carpal_L.head + mathutils.Vector([0, -VIRTUAL_BONES['thumb.carpal.L']['median'], 0])

        # Asign the parent to thumb carpals
        thumb_carpal_R.parent = hand_R
        thumb_carpal_R.use_connect = False
        thumb_carpal_L.parent = hand_L
        thumb_carpal_L.use_connect = False

        # Change the parent of thumb.01 to thumb.carpal
        thumb_01_R.parent = thumb_carpal_R
        thumb_01_L.parent = thumb_carpal_L

        # Create a palm bones list and phalanges dictionary to continue the finger adjustment
        palm_bones = [thumb_carpal_R, thumb_carpal_L, palm_01_R, palm_01_L, palm_02_R, palm_02_L, palm_03_R, palm_03_L,
                      palm_04_R, palm_04_L]
        phalanges = {
            'thumb.carpal.R': [thumb_01_R, thumb_02_R, thumb_03_R],
            'thumb.carpal.L': [thumb_01_L, thumb_02_L, thumb_03_L],
            'palm.01.R': [f_index_01_R, f_index_02_R, f_index_03_R],
            'palm.01.L': [f_index_01_L, f_index_02_L, f_index_03_L],
            'palm.02.R': [f_middle_01_R, f_middle_02_R, f_middle_03_R],
            'palm.02.L': [f_middle_01_L, f_middle_02_L, f_middle_03_L],
            'palm.03.R': [f_ring_01_R, f_ring_02_R, f_ring_03_R],
            'palm.03.L': [f_ring_01_L, f_ring_02_L, f_ring_03_L],
            'palm.04.R': [f_pinky_01_R, f_pinky_02_R, f_pinky_03_R],
            'palm.04.L': [f_pinky_01_L, f_pinky_02_L, f_pinky_03_L],
        }

        # Iterate through the palm bones to adjust several properties
        for palm_bone in palm_bones:
            # Change the first phalange connect setting to True
            phalanges[palm_bone.name][0].use_connect = True
            # Move the head of the metacarpal bones to match the hand bone head
            palm_bone.head = palm_bone.parent.head
            # Move the tail of the metacarpal bones so they are aligned horizontally
            palm_bone.tail[2] = palm_bone.head[2]
            # Change metacarpal bones lengths
            palm_bone.length = VIRTUAL_BONES[palm_bone.name]['median']

        # Align the phalanges to the x axis (set bones head and tail y position equal to yz position of metacarpals bone tail)
        for palm_bone in palm_bones:
            for phalange in phalanges[palm_bone.name]:
                phalange.head = phalange.parent.tail
                # Calculate the sign to multiply the length of the phalange
                length_sign = -1 if ".R" in phalange.name else 1
                # Set the length by moving the bone tail along the x axis. Using this instead of just setting bone.length because that causes some bone inversions
                phalange.tail = (
                phalange.head[0] + length_sign * VIRTUAL_BONES[phalange.name]['median'], phalange.head[1],
                phalange.head[2])
                # Reset the phalange bone roll to 0
                phalange.roll = 0

        # Rotate the thumb bones to form a natural pose
        bpy.ops.object.mode_set(mode='POSE')

        pose_thumb_carpal_R = rig.pose.bones['thumb.carpal.R']
        pose_thumb_carpal_R.rotation_mode = 'XYZ'
        pose_thumb_carpal_R.rotation_euler = (m.radians(-28.048091), m.radians(7.536737), m.radians(-40.142189))
        pose_thumb_carpal_R.rotation_mode = 'QUATERNION'
        pose_thumb_01_R = rig.pose.bones['thumb.01.R']
        pose_thumb_01_R.rotation_mode = 'XYZ'
        # pose_thumb_01_R.rotation_euler      = (m.radians(20), m.radians(0), m.radians(80))
        pose_thumb_01_R.rotation_euler = (m.radians(0), m.radians(0), m.radians(90))
        pose_thumb_01_R.rotation_mode = 'QUATERNION'
        # pose_thumb_02_R                     = rig.pose.bones['thumb.02.R']
        # pose_thumb_02_R.rotation_mode       = 'XYZ'
        # pose_thumb_02_R.rotation_euler      = (m.radians(0), m.radians(0), m.radians(-25))
        # pose_thumb_02_R.rotation_mode       = 'QUATERNION'
        # pose_thumb_03_R                     = rig.pose.bones['thumb.03.R']
        # pose_thumb_03_R.rotation_mode       = 'XYZ'
        # pose_thumb_03_R.rotation_euler      = (m.radians(0), m.radians(0), m.radians(-10))
        # pose_thumb_03_R.rotation_mode       = 'QUATERNION'
        pose_thumb_carpal_L = rig.pose.bones['thumb.carpal.L']
        pose_thumb_carpal_L.rotation_mode = 'XYZ'
        pose_thumb_carpal_L.rotation_euler = (m.radians(-28.048091), m.radians(-7.536737), m.radians(40.142189))
        pose_thumb_carpal_L.rotation_mode = 'QUATERNION'
        pose_thumb_01_L = rig.pose.bones['thumb.01.L']
        pose_thumb_01_L.rotation_mode = 'XYZ'
        # pose_thumb_01_L.rotation_euler      = (m.radians(20), m.radians(0), m.radians(-80))
        pose_thumb_01_L.rotation_euler = (m.radians(0), m.radians(0), m.radians(-90))
        pose_thumb_01_L.rotation_mode = 'QUATERNION'
        # pose_thumb_02_L                     = rig.pose.bones['thumb.02.L']
        # pose_thumb_02_L.rotation_mode       = 'XYZ'
        # pose_thumb_02_L.rotation_euler      = (m.radians(0), m.radians(0), m.radians(25))
        # pose_thumb_02_L.rotation_mode       = 'QUATERNION'
        # pose_thumb_03_L                     = rig.pose.bones['thumb.03.L']
        # pose_thumb_03_L.rotation_mode       = 'XYZ'
        # pose_thumb_03_L.rotation_euler      = (m.radians(0), m.radians(0), m.radians(10))
        # pose_thumb_03_L.rotation_mode       = 'QUATERNION'

        # Rotate the forearms on the z axis to bend the elbows a little bit and avoid incorrect rotations
        pose_forearm_R = rig.pose.bones['forearm.R']
        pose_forearm_R.rotation_mode = 'XYZ'
        pose_forearm_R.rotation_euler = (m.radians(1), m.radians(0), m.radians(0))
        pose_forearm_R.rotation_mode = 'QUATERNION'
        pose_forearm_L = rig.pose.bones['forearm.L']
        pose_forearm_L.rotation_mode = 'XYZ'
        pose_forearm_L.rotation_euler = (m.radians(1), m.radians(0), m.radians(0))
        pose_forearm_L.rotation_mode = 'QUATERNION'

        # Apply the actual pose to the rest pose
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=False)

        # Change mode to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

    elif bone_length_method == 'current_frame':

        print('Adding rig with current frame length method...')

        # Scale armature so it fits the capture empties height in a standing position. The reference point will be hips_center
        # Get the rig z dimension
        rig_z_dimension = rig.dimensions.z
        # Get hips_center global position
        hips_center_glob_pos = bpy.data.objects['hips_center'].matrix_world.translation
        # Get the rig thigh.R bone head z position (this will be aligned with the hips_center empty
        thigh_r_z_pos = (rig.matrix_world @ rig.pose.bones['thigh.R'].head)[2]
        # Calculate the proportion between the hips_center z pos and the thigh_r_z_pos
        hips_center_to_thigh_R = hips_center_glob_pos[2] / thigh_r_z_pos

        # Scale the rig by the hips_center_z and the thigh_r_z_pos proportion
        rig.scale = (hips_center_to_thigh_R, hips_center_to_thigh_R, hips_center_to_thigh_R)
        # Apply transformations to rig (scale must be (1, 1, 1) so it doesn't fail on send2ue export
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Get references to the different rig bones
        bpy.ops.object.mode_set(mode='EDIT')

        spine = rig.data.edit_bones['spine']
        spine_003 = rig.data.edit_bones['spine.003']
        spine_004 = rig.data.edit_bones['spine.004']
        spine_005 = rig.data.edit_bones['spine.005']
        spine_006 = rig.data.edit_bones['spine.006']
        face = rig.data.edit_bones['face']
        nose = rig.data.edit_bones['nose']
        breast_R = rig.data.edit_bones['breast.R']
        breast_L = rig.data.edit_bones['breast.L']
        shoulder_R = rig.data.edit_bones['shoulder.R']
        shoulder_L = rig.data.edit_bones['shoulder.L']
        upper_arm_R = rig.data.edit_bones['upper_arm.R']
        upper_arm_L = rig.data.edit_bones['upper_arm.L']
        forearm_R = rig.data.edit_bones['forearm.R']
        forearm_L = rig.data.edit_bones['forearm.L']
        hand_R = rig.data.edit_bones['hand.R']
        hand_L = rig.data.edit_bones['hand.L']
        pelvis_R = rig.data.edit_bones['pelvis.R']
        pelvis_L = rig.data.edit_bones['pelvis.L']
        thigh_R = rig.data.edit_bones['thigh.R']
        thigh_L = rig.data.edit_bones['thigh.L']
        shin_R = rig.data.edit_bones['shin.R']
        shin_L = rig.data.edit_bones['shin.L']
        foot_R = rig.data.edit_bones['foot.R']
        foot_L = rig.data.edit_bones['foot.L']
        toe_R = rig.data.edit_bones['toe.R']
        toe_L = rig.data.edit_bones['toe.L']
        heel_02_R = rig.data.edit_bones['heel.02.R']
        heel_02_L = rig.data.edit_bones['heel.02.L']

        # Move spine and pelvis bones head to hips_center location
        spine.head = hips_center_glob_pos
        pelvis_R.head = hips_center_glob_pos
        pelvis_L.head = hips_center_glob_pos
        # Align each pelvis bone tail to its corresponding hip empty
        right_hip_glob_pos = bpy.data.objects['right_hip'].matrix_world.translation
        left_hip_glob_pos = bpy.data.objects['left_hip'].matrix_world.translation
        pelvis_R.tail = right_hip_glob_pos
        pelvis_L.tail = left_hip_glob_pos

        # Calculate the length of the thighs as the average distance between the hips and knees empties
        # Get global position of knee empties
        right_knee_glob_pos = bpy.data.objects['right_knee'].matrix_world.translation
        left_knee_glob_pos = bpy.data.objects['left_knee'].matrix_world.translation
        # Get average distance
        thigh_length = (m.dist(right_hip_glob_pos, right_knee_glob_pos) + m.dist(left_hip_glob_pos,
                                                                                 left_knee_glob_pos)) / 2
        # Move the thighs tail in the z axis
        thigh_R.tail[2] = right_hip_glob_pos[2] - thigh_length
        thigh_L.tail[2] = left_hip_glob_pos[2] - thigh_length

        # Calculate the length of the shins as the average distance between the knees and ankle empties
        # Get global position of ankle empties
        right_ankle_glob_pos = bpy.data.objects['right_ankle'].matrix_world.translation
        left_ankle_glob_pos = bpy.data.objects['left_ankle'].matrix_world.translation
        # Get average distance
        shin_length = (m.dist(right_knee_glob_pos, right_ankle_glob_pos) + m.dist(left_knee_glob_pos,
                                                                                  left_ankle_glob_pos)) / 2
        # Move the shins tail in the z axis
        shin_R.tail[2] = shin_R.head[2] - shin_length
        shin_L.tail[2] = shin_L.head[2] - shin_length

        # Calculate the distance between thighs bone heads and the corresponding hip empty in the x and y axes
        thigh_R_head_x_offset = right_hip_glob_pos[0] - thigh_R.head[0]
        thigh_R_head_y_offset = right_hip_glob_pos[1] - thigh_R.head[1]
        thigh_L_head_x_offset = left_hip_glob_pos[0] - thigh_L.head[0]
        thigh_L_head_y_offset = left_hip_glob_pos[1] - thigh_L.head[1]

        # Translate the entire legs using the previous offsets

        # Right leg
        thigh_R.head[0] += thigh_R_head_x_offset
        thigh_R.head[1] += thigh_R_head_y_offset
        thigh_R.tail[0] += thigh_R_head_x_offset
        # Align the thigh vertically
        thigh_R.tail[1] = thigh_R.head[1]
        shin_R.tail[0] += thigh_R_head_x_offset
        shin_R.tail[1] += thigh_R_head_y_offset
        foot_R.tail[0] += thigh_R_head_x_offset
        toe_R.tail[0] += thigh_R_head_x_offset
        heel_02_R.head[0] += thigh_R_head_x_offset
        heel_02_R.head[1] += thigh_R_head_y_offset
        heel_02_R.tail[0] += thigh_R_head_x_offset
        heel_02_R.tail[1] += thigh_R_head_y_offset

        # Move the right heel so its bone head aligns with the right ankle in the x axis
        heel_02_R_head_x_offset = shin_R.tail[0] - heel_02_R.head[0]
        heel_02_R.head[0] += heel_02_R_head_x_offset
        heel_02_R.tail[0] += heel_02_R_head_x_offset
        # Make the heel bone be connected with the shin bone
        heel_02_R.use_connect = True

        # Left leg
        thigh_L.head[0] += thigh_L_head_x_offset
        thigh_L.head[1] += thigh_L_head_y_offset
        thigh_L.tail[0] += thigh_L_head_x_offset
        # Align the thigh vertically
        thigh_L.tail[1] = thigh_L.head[1]
        shin_L.tail[0] += thigh_L_head_x_offset
        shin_L.tail[1] += thigh_L_head_y_offset
        foot_L.tail[0] += thigh_L_head_x_offset
        toe_L.tail[0] += thigh_L_head_x_offset
        heel_02_L.head[0] += thigh_L_head_x_offset
        heel_02_L.head[1] += thigh_L_head_y_offset
        heel_02_L.tail[0] += thigh_L_head_x_offset
        heel_02_L.tail[1] += thigh_L_head_y_offset

        # Move the left heel so its bone head aligns with the left ankle in the x axis
        heel_02_L_head_x_offset = shin_L.tail[0] - heel_02_L.head[0]
        heel_02_L.head[0] += heel_02_L_head_x_offset
        heel_02_L.tail[0] += heel_02_L_head_x_offset
        # Make the heel bone be connected with the shin bone
        heel_02_L.use_connect = True

        # Add a pelvis bone to the root and then make it the parent of spine, pelvis.R and pelvis.L bones
        pelvis = rig.data.edit_bones.new('pelvis')
        pelvis.head = hips_center_glob_pos
        pelvis.tail = hips_center_glob_pos + mathutils.Vector([0, 0.1, 0])

        # Change the pelvis.R, pelvis.L, thigh.R, thigh.L and spine parent to the new pelvis bone
        pelvis_R.parent = pelvis
        pelvis_R.use_connect = False
        pelvis_L.parent = pelvis
        pelvis_L.use_connect = False
        thigh_R.parent = pelvis
        thigh_R.use_connect = False
        thigh_L.parent = pelvis
        thigh_L.use_connect = False
        spine.parent = pelvis
        spine.use_connect = False

        # Change parent of spine.003 bone to spine to erase bones spine.001 and spine.002
        spine_003.parent = spine
        spine_003.use_connect = True
        # Remove spine.001 and spine.002 bones
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.001'])
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.002'])

        # Rename spine.003 to spine.001
        rig.data.edit_bones['spine.003'].name = "spine.001"
        spine_001 = rig.data.edit_bones['spine.001']

        # Calculate the distance between the hips_center empty and the trunk_center empty
        # This distance will be the length of the spine bone
        # Get trunk_center global position
        trunk_center_glob_pos = bpy.data.objects['trunk_center'].matrix_world.translation
        # Get distance to hips_center empty
        spine_length = m.dist(trunk_center_glob_pos, hips_center_glob_pos)

        # Change spine tail position values
        spine.tail[1] = spine.head[1]
        spine.tail[2] = spine.head[2] + spine_length

        # Calculate the distance between the trunk_center empty and the neck_center empty
        # This distance will be the length of the spine.001 bone
        # Get neck_center global position
        neck_center_glob_pos = bpy.data.objects['neck_center'].matrix_world.translation
        # Get distance to trunk_center empty
        spine_001_length = m.dist(neck_center_glob_pos, trunk_center_glob_pos)

        # Change spine.001 tail position values
        spine_001.tail[1] = spine_001.head[1]
        spine_001.tail[2] = spine_001.head[2] + spine_001_length

        # Calculate the shoulders head z offset from the spine.001 tail. This to raise the shoulders and breasts by that offset
        shoulder_z_offset = spine_001.tail[2] - shoulder_R.head[2]

        # Raise breasts and shoulders by the z offset
        breast_R.head[2] += shoulder_z_offset
        breast_R.tail[2] += shoulder_z_offset
        breast_L.head[2] += shoulder_z_offset
        breast_L.tail[2] += shoulder_z_offset
        shoulder_R.head[2] += shoulder_z_offset
        shoulder_R.tail[2] += shoulder_z_offset
        shoulder_L.head[2] += shoulder_z_offset
        shoulder_L.tail[2] += shoulder_z_offset

        # Calculate the shoulders length as the average of the distance between neck_center empty and shoulder empties
        # Get global position of shoulder empties
        right_shoulder_glob_pos = bpy.data.objects['right_shoulder'].matrix_world.translation
        left_shoulder_glob_pos = bpy.data.objects['left_shoulder'].matrix_world.translation
        # Get average distance
        shoulder_length = (m.dist(neck_center_glob_pos, right_shoulder_glob_pos) + m.dist(neck_center_glob_pos,
                                                                                          left_shoulder_glob_pos)) / 2
        # Move the shoulder tail in the x axis
        shoulder_R.tail[0] = spine_001.tail[0] - shoulder_length
        shoulder_L.tail[0] = spine_001.tail[0] + shoulder_length

        # Calculate the upper_arms head x and z offset from the shoulder_R tail. This to raise and adjust the arms and hands by that offset
        upper_arm_R_x_offset = shoulder_R.tail[0] - upper_arm_R.head[0]
        upper_arm_R_z_offset = spine_001.tail[2] - upper_arm_R.head[2]

        upper_arm_R.head[2] += upper_arm_R_z_offset
        upper_arm_R.tail[2] += upper_arm_R_z_offset
        upper_arm_R.head[0] += upper_arm_R_x_offset
        upper_arm_R.tail[0] += upper_arm_R_x_offset
        for bone in upper_arm_R.children_recursive:
            if not bone.use_connect:
                bone.head[0] += upper_arm_R_x_offset
                bone.tail[0] += upper_arm_R_x_offset
                bone.head[2] += upper_arm_R_z_offset
                bone.tail[2] += upper_arm_R_z_offset
            else:
                bone.tail[0] += upper_arm_R_x_offset
                bone.tail[2] += upper_arm_R_z_offset

        upper_arm_L.head[2] += upper_arm_R_z_offset
        upper_arm_L.tail[2] += upper_arm_R_z_offset
        upper_arm_L.head[0] -= upper_arm_R_x_offset
        upper_arm_L.tail[0] -= upper_arm_R_x_offset
        for bone in upper_arm_L.children_recursive:
            if not bone.use_connect:
                bone.head[0] -= upper_arm_R_x_offset
                bone.tail[0] -= upper_arm_R_x_offset
                bone.head[2] += upper_arm_R_z_offset
                bone.tail[2] += upper_arm_R_z_offset
            else:
                bone.tail[0] -= upper_arm_R_x_offset
                bone.tail[2] += upper_arm_R_z_offset

        # Align the y position of breasts, shoulders, arms and hands to the y position of the spine.001 tail
        # Calculate the breasts head y offset from the spine.001 tail
        breast_y_offset = spine_001.tail[1] - breast_R.head[1]
        # Move breast by the y offset
        breast_R.head[1] += breast_y_offset
        breast_R.tail[1] += breast_y_offset
        breast_L.head[1] += breast_y_offset
        breast_L.tail[1] += breast_y_offset

        # Set the y position to which the arms bones will be aligned
        arms_bones_y_pos = spine_001.tail[1]
        # Move shoulders on y axis and also move shoulders head to the center at x=0 ,
        shoulder_R.head[1] = arms_bones_y_pos
        shoulder_R.head[0] = 0
        shoulder_R.tail[1] = arms_bones_y_pos
        shoulder_L.head[1] = arms_bones_y_pos
        shoulder_L.head[0] = 0
        shoulder_L.tail[1] = arms_bones_y_pos

        # Move upper_arm and forearm
        upper_arm_R.head[1] = arms_bones_y_pos
        upper_arm_R.tail[1] = arms_bones_y_pos
        upper_arm_L.head[1] = arms_bones_y_pos
        upper_arm_L.tail[1] = arms_bones_y_pos

        # Calculate hand head y offset to arms_bones_y_pos to move the whole hand
        hand_y_offset = arms_bones_y_pos - hand_R.head[1]

        # Move hands and its children by the y offset (forearm tail is moved by hand head)
        hand_R.head[1] += hand_y_offset
        hand_R.tail[1] += hand_y_offset
        for bone in hand_R.children_recursive:
            if not bone.use_connect:
                bone.head[1] += hand_y_offset
                bone.tail[1] += hand_y_offset
            else:
                bone.tail[1] += hand_y_offset

        hand_L.head[1] += hand_y_offset
        hand_L.tail[1] += hand_y_offset
        for bone in hand_L.children_recursive:
            if not bone.use_connect:
                bone.head[1] += hand_y_offset
                bone.tail[1] += hand_y_offset
            else:
                bone.tail[1] += hand_y_offset

        # Change to Pose Mode to rotate the arms and make a T Pose for posterior retargeting
        bpy.ops.object.mode_set(mode='POSE')
        pose_upper_arm_R = rig.pose.bones['upper_arm.R']
        pose_upper_arm_R.rotation_mode = 'XYZ'
        pose_upper_arm_R.rotation_euler = (0, 0, m.radians(-29))
        pose_upper_arm_R.rotation_mode = 'QUATERNION'
        pose_upper_arm_L = rig.pose.bones['upper_arm.L']
        pose_upper_arm_L.rotation_mode = 'XYZ'
        pose_upper_arm_L.rotation_euler = (0, 0, m.radians(29))
        pose_upper_arm_L.rotation_mode = 'QUATERNION'
        pose_forearm_R = rig.pose.bones['forearm.R']
        pose_forearm_R.rotation_mode = 'XYZ'
        pose_forearm_R.rotation_euler = (0, 0, m.radians(-4))
        pose_forearm_R.rotation_mode = 'QUATERNION'
        pose_forearm_L = rig.pose.bones['forearm.L']
        pose_forearm_L.rotation_mode = 'XYZ'
        pose_forearm_L.rotation_euler = (0, 0, m.radians(4))
        pose_forearm_L.rotation_mode = 'QUATERNION'
        pose_thigh_R = rig.pose.bones['thigh.R']
        pose_thigh_R.rotation_mode = 'XYZ'
        pose_thigh_R.rotation_euler = (0, 0, m.radians(3))
        pose_thigh_R.rotation_mode = 'QUATERNION'
        pose_foot_R = rig.pose.bones['foot.R']
        pose_foot_R.rotation_mode = 'XYZ'
        pose_foot_R.rotation_euler = (0, 0, m.radians(4))
        pose_foot_R.rotation_mode = 'QUATERNION'
        pose_thigh_L = rig.pose.bones['thigh.L']
        pose_thigh_L.rotation_mode = 'XYZ'
        pose_thigh_L.rotation_euler = (0, 0, m.radians(-3))
        pose_thigh_L.rotation_mode = 'QUATERNION'
        pose_foot_L = rig.pose.bones['foot.L']
        pose_foot_L.rotation_mode = 'XYZ'
        pose_foot_L.rotation_euler = (0, 0, m.radians(-4))
        pose_foot_L.rotation_mode = 'QUATERNION'

        # Apply the actual pose to the rest pose
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=False)

        # Change mode to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        upper_arm_R = rig.data.edit_bones['upper_arm.R']
        upper_arm_L = rig.data.edit_bones['upper_arm.L']
        forearm_R = rig.data.edit_bones['forearm.R']
        forearm_L = rig.data.edit_bones['forearm.L']

        # Calculate the length of the upper_arms as the average distance between the shoulder and elbow empties
        # Get global position of elbow empties
        right_elbow_glob_pos = bpy.data.objects['right_elbow'].matrix_world.translation
        left_elbow_glob_pos = bpy.data.objects['left_elbow'].matrix_world.translation
        # Get average distance
        upper_arm_length = (m.dist(right_shoulder_glob_pos, right_elbow_glob_pos) + m.dist(left_shoulder_glob_pos,
                                                                                           left_elbow_glob_pos)) / 2
        # Move the upper_arm tail in the x axis
        upper_arm_R.tail[0] = upper_arm_R.head[0] - upper_arm_length
        upper_arm_L.tail[0] = upper_arm_L.head[0] + upper_arm_length

        # Calculate the length of the forearms as the average distance between the elbow and wrist empties
        # Get global position of wrist empties
        right_wrist_glob_pos = bpy.data.objects['right_wrist'].matrix_world.translation
        left_wrist_glob_pos = bpy.data.objects['left_wrist'].matrix_world.translation
        # Get average distance
        forearm_length = (m.dist(right_elbow_glob_pos, right_wrist_glob_pos) + m.dist(left_elbow_glob_pos,
                                                                                      left_wrist_glob_pos)) / 2

        # Calculate the x axis offset of the current forearm tail x position and the forearm head x position plus the calculated forearm length
        # This is to move the forearm tail and all the hand bones
        forearm_tail_x_offset = (forearm_R.head[0] - forearm_length) - forearm_R.tail[0]

        # Move forearms tail and its children by the x offset
        forearm_R.tail[0] += forearm_tail_x_offset
        for bone in forearm_R.children_recursive:
            if not bone.use_connect:
                bone.head[0] += forearm_tail_x_offset
                bone.tail[0] += forearm_tail_x_offset
            else:
                bone.tail[0] += forearm_tail_x_offset

        forearm_L.tail[0] -= forearm_tail_x_offset
        for bone in forearm_L.children_recursive:
            if not bone.use_connect:
                bone.head[0] -= forearm_tail_x_offset
                bone.tail[0] -= forearm_tail_x_offset
            else:
                bone.tail[0] -= forearm_tail_x_offset

        ### Adjust the position of the neck, head and face bones ###
        spine_001 = rig.data.edit_bones['spine.001']
        spine_004 = rig.data.edit_bones['spine.004']
        nose = rig.data.edit_bones['nose']

        # Set spine.004 bone head position equal to the spine.001 tail
        spine_004.head = (spine_001.tail[0], spine_001.tail[1], spine_001.tail[2])

        # Calculate the distance between the neck_center empty and the head_center empty
        # This distance will be the length of the spine.004 (neck) bone
        # Get head_center global position
        head_center_glob_pos = bpy.data.objects['head_center'].matrix_world.translation
        # Get distance to trunk_center empty
        spine_004_length = m.dist(head_center_glob_pos, neck_center_glob_pos)

        # Change spine.004 tail position values
        spine_004.tail[1] = spine_004.head[1]
        spine_004.tail[2] = spine_004.head[2] + spine_004_length

        # Change the parent of the face bone for the spine.004 bone
        face = rig.data.edit_bones['face']
        face.parent = spine_004
        face.use_connect = False

        # Remove spine.005 and spine.006 bones
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.005'])
        rig.data.edit_bones.remove(rig.data.edit_bones['spine.006'])

        # Calculate the y and z offset of the nose bone tail to the spine.004 bone tail
        # Get nose empty global position
        nose_glob_pos = bpy.data.objects['nose'].matrix_world.translation
        # Get the distance between nose empty and head_center empty
        nose_to_head_center = m.dist(nose_glob_pos, head_center_glob_pos)

        nose_y_offset = (spine_004.tail[1] - nose_to_head_center) - nose.tail[1]
        nose_z_offset = nose_glob_pos[2] - nose.tail[2]

        # Move the face bone on the z axis using the calculated offset
        face.head[2] += nose_z_offset
        face.tail[2] += nose_z_offset

        # Move on the y and z axis the children bones from the face bone using the calculated offsets
        for bone in face.children_recursive:
            if not bone.use_connect:
                bone.head[1] += nose_y_offset
                bone.tail[1] += nose_y_offset
                bone.head[2] += nose_z_offset
                bone.tail[2] += nose_z_offset
            else:
                bone.tail[1] += nose_y_offset
                bone.tail[2] += nose_z_offset

        # Move the face bone head to align it horizontally
        face.head[1] = spine_004.tail[1]
        face.head[2] = face.tail[2]
        face.tail[1] = face.head[1] - nose_to_head_center / 2

        # Rename spine.004 to neck
        rig.data.edit_bones['spine.004'].name = "neck"

        # Rotate the spine and neck bones to complete the TPOSE
        bpy.ops.object.mode_set(mode='POSE')

        pose_spine = rig.pose.bones['spine']
        pose_spine.rotation_mode = 'XYZ'
        pose_spine.rotation_euler = (m.radians(4), 0, 0)
        pose_spine.rotation_mode = 'QUATERNION'
        pose_spine_001 = rig.pose.bones['spine.001']
        pose_spine_001.rotation_mode = 'XYZ'
        pose_spine_001.rotation_euler = (m.radians(-12), 0, 0)
        pose_spine_001.rotation_mode = 'QUATERNION'
        pose_neck = rig.pose.bones['neck']
        pose_neck.rotation_mode = 'XYZ'
        pose_neck.rotation_euler = (m.radians(7), 0, 0)
        pose_neck.rotation_mode = 'QUATERNION'

        # Apply the actual pose to the rest pose
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=False)

        # Change mode to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

    ### Add bone constrains ###
    print('Adding bone constraints...')

    # Change to pose mode
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    #
    # # Define the hand bones damped track target as the hand middle empty if they were already added
    # try:
    #     right_hand_middle_name = bpy.data.objects['right_hand_middle'].name
    #     # Right Hand Middle Empty exists. Use hand middle as target
    #     hand_damped_track_target = 'hand_middle'
    # except:
    #     # Hand middle empties do not exist. Use hand_index as target
    #     hand_damped_track_target = 'index'

    # Define the hands LOCKED_TRACK target empty based on the add_fingers_constraints parameter
    if add_fingers_constraints:
        hand_locked_track_target = 'hand_thumb_cmc'
    else:
        hand_locked_track_target = 'thumb'

    # Create each constraint
    for bone in BONES_CONSTRAINTS:

        # If it is a finger bone amd add_fingers_constraints is False continue with the next bone
        if not add_fingers_constraints and len(
                [finger_part for finger_part in ['palm', 'thumb', 'index', 'middle', 'ring', 'pinky'] if
                 finger_part in bone]) > 0:
            continue

        for cons in BONES_CONSTRAINTS[bone]:
            # Add new constraint determined by type
            if not use_limit_rotation and cons['type'] == 'LIMIT_ROTATION':
                continue
            else:
                bone_cons = rig.pose.bones[bone].constraints.new(cons['type'])

                # Define aditional parameters based on the type of constraint
            if cons['type'] == 'LIMIT_ROTATION':
                bone_cons.use_limit_x = cons['use_limit_x']
                bone_cons.min_x = m.radians(cons['min_x'])
                bone_cons.max_x = m.radians(cons['max_x'])
                bone_cons.use_limit_y = cons['use_limit_y']
                bone_cons.min_y = m.radians(cons['min_y'])
                bone_cons.max_y = m.radians(cons['max_y'])
                bone_cons.use_limit_z = cons['use_limit_z']
                bone_cons.min_z = m.radians(cons['min_z'])
                bone_cons.max_z = m.radians(cons['max_z'])
                bone_cons.owner_space = cons['owner_space']
                pass
            elif cons['type'] == 'COPY_LOCATION':
                bone_cons.target = bpy.data.objects[cons['target']]
            elif cons['type'] == 'LOCKED_TRACK':
                bone_cons.target = bpy.data.objects[cons['target']]
                bone_cons.track_axis = cons['track_axis']
                bone_cons.lock_axis = cons['lock_axis']
                bone_cons.influence = cons['influence']
            elif cons['type'] == 'DAMPED_TRACK':
                bone_cons.target = bpy.data.objects[cons['target']]
                bone_cons.track_axis = cons['track_axis']
            elif cons['type'] == 'IK':
                bone_cons.target = bpy.data.objects[cons['target']]
                bone_cons.pole_target = bpy.data.objects[cons['pole_target']]
                bone_cons.chain_count = cons['chain_count']
                bone_cons.pole_angle = cons['pole_angle']

    ### Bake animation to the rig ###
    # Get the empties ending frame
    ending_frame = int(bpy.data.actions[0].frame_range[1])
    # Bake animation
    bpy.ops.nla.bake(frame_start=1, frame_end=ending_frame, bake_types={'POSE'})

    # Change back to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')