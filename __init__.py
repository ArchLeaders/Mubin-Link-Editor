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

# intall required packages
from .setup import init

init()

import bpy

from bpy.utils import register_class as reg_cls, unregister_class as unreg_cls
from nodeitems_utils import register_node_categories, unregister_node_categories
from bpy.app.handlers import persistent

from .registry import classes
from .utils import RegisterHelper

bl_info = {
    "name": "Mubin Link Node Editor",
    "author": "Marcus Smith",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}


def register():
    # Register classes
    try:
        for cls in classes:
            reg_cls(cls)

        register_node_categories(
            "BOTWMUBINEDITOR_NODETREE", RegisterHelper.construct_nodes()
        )
    except:
        unregister()
        register()


def unregister():
    # Unregister classes
    unregister_node_categories("BOTWMUBINEDITOR_NODETREE")

    for cls in classes:
        unreg_cls(cls)


@persistent
def load_handler(dummy):
    bpy.ops.nodes.sync()
    bpy.ops.ignore.sync()


bpy.app.handlers.load_post.append(load_handler)
