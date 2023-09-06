from freemocap_adapter.blender_user_interface.operators._add_body_mesh import FMC_ADAPTER_OT_add_body_mesh
from freemocap_adapter.blender_user_interface.operators._add_rig import FMC_ADAPTER_OT_add_rig
from freemocap_adapter.blender_user_interface.operators._adjust_empties import FMC_ADAPTER_OT_adjust_empties
from freemocap_adapter.blender_user_interface.operators._download_sample_data import FMC_ADAPTER_download_sample_data
from freemocap_adapter.blender_user_interface.operators._export_fbx import FMC_ADAPTER_OT_export_fbx
from freemocap_adapter.blender_user_interface.operators._load_freemocap_data import FMC_ADAPTER_load_freemocap_data
from freemocap_adapter.blender_user_interface.operators._reduce_bone_length_dispersion import \
    FMC_ADAPTER_OT_reduce_bone_length_dispersion
from freemocap_adapter.blender_user_interface.operators._reduce_shakiness import FMC_ADAPTER_OT_reduce_shakiness


BLENDER_OPERATORS = [#FMC_ADAPTER_download_sample_data,
                     FMC_ADAPTER_load_freemocap_data,
                     FMC_ADAPTER_OT_adjust_empties,
                     FMC_ADAPTER_OT_reduce_bone_length_dispersion,
                     FMC_ADAPTER_OT_reduce_shakiness,
                     FMC_ADAPTER_OT_add_rig,
                     FMC_ADAPTER_OT_add_body_mesh,
                     FMC_ADAPTER_OT_export_fbx,
                     ]
