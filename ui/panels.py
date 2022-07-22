from bpy.types import Panel
from ..utils import MLEBase


class MLE_SETTINGS_PT_Nodes(Panel, MLEBase):
    """Toolset for generating a string value from parameter key value pairs"""

    bl_category = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_label = "Nodes"

    def draw(self, context):
        row = self.layout.row()
        row.template_list(
            "MLE_UL_Params",
            "Nodes",
            context.scene,
            "nodes",
            context.scene,
            "nodes_index",
        )
        col = row.column()
        col.ui_units_x = 1.0

        sub_col = col.column(align=True)
        sub_col.operator("nodes.add", text="", icon="ADD")
        sub_col.operator("nodes.remove", text="", icon="REMOVE")

        sub_col.separator(factor=1.8)
        sub_col.operator("nodes.move", text="", icon="TRIA_UP").direction = "UP"
        sub_col.operator("nodes.move", text="", icon="TRIA_DOWN").direction = "DOWN"

        sub_col.separator(factor=1.8)
        sub_col.operator("nodes.clear", text="", icon="PANEL_CLOSE")

        row = self.layout.row(align=True)
        row.operator("nodes.save")
        row.operator("nodes.sync")


class MLE_SETTINGS_PT_Ignored(Panel, MLEBase):
    """Toolset for generating a string value from parameter key value pairs"""

    bl_category = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_label = "Ignored"

    def draw(self, context):
        row = self.layout.row()
        row.template_list(
            "UI_UL_list",
            "Ignore",
            context.scene,
            "ignore",
            context.scene,
            "ignore_index",
        )
        col = row.column()
        col.ui_units_x = 1.0

        sub_col = col.column(align=True)
        sub_col.operator("ignore.add", text="", icon="ADD")
        sub_col.operator("ignore.remove", text="", icon="REMOVE")

        sub_col.separator(factor=1.8)
        sub_col.operator("ignore.move", text="", icon="TRIA_UP").direction = "UP"
        sub_col.operator("ignore.move", text="", icon="TRIA_DOWN").direction = "DOWN"

        sub_col.separator(factor=1.8)
        sub_col.operator("ignore.clear", text="", icon="PANEL_CLOSE")

        row = self.layout.row(align=True)
        row.operator("ignore.save")
        row.operator("ignore.sync")
