from bpy.types import NodeTree


class MubinLinkEditor_NodeTree(NodeTree):
    """Node editor for editing and viewing BotW Map Unit linked actors."""

    bl_label = "Mubin Link Editor"
    bl_icon = "MOD_PARTICLE_INSTANCE"


class REF_MubinLinkEditor_NodeTree:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "MubinLinkEditor_NodeTree"
