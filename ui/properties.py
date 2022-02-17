from bpy.types import PropertyGroup, UIList
from bpy.props import StringProperty

class ParamProperties(PropertyGroup):
    value: StringProperty(name='Value', maxlen=1024, default='Value')

class MLE_UL_Params(UIList):
    """List of parameters for an actor or actor link"""
    bl_idname = 'MLE_UL_Params'

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.emboss = 'NONE'

            row = layout.row(align=True)
            row.scale_x = 0.9
            row.label(text='', icon='KEYINGSET')
            row.scale_x = 0.0
            row.prop(item, 'name', text='')
            row.scale_x = 0.9
            row.label(icon='RIGHTARROW')
            row.scale_x = 0.0
            row.prop(item, 'value', text='')

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            row.label(text='', icon='KEYINGSET')