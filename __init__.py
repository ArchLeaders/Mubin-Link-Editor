import bpy
from . import config as _

from bpy.utils import register_class as reg_cls, unregister_class as unreg_cls
from bpy.app.handlers import persistent
from nodeitems_utils import register_node_categories, unregister_node_categories

bl_info = {
    "name": "Mubin Link Node Editor",
    "author": "ArchLeaders",
    "description": "",
    "blender": (2, 29, 0),
    "version": (0, 0, 2),
    "location": "",
    "warning": "",
    "category": "BOTW",
}


def register():

    # Register classes
    try:

        # [] MLE classes
        for _class in []:
            reg_cls(_class)

        # [] = Generated nodes list
        register_node_categories("BOTWMUBINLINKEDITOR_NODETREE", [])

    except:
        unregister()
        register()


def unregister():

    # Unregister classes
    unregister_node_categories("BOTWMUBINLINKEDITOR_NODETREE")

    # [] MLE classes
    for cls in []:
        unreg_cls(cls)


@persistent
def load_handler(_):
    bpy.ops.nodes.sync()
    bpy.ops.ignore.sync()


bpy.app.handlers.load_post.append(load_handler)
