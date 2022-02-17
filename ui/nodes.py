import bpy
from bpy.types import Node
from .properties import ParamProperties
from .node_tree import REF_MubinLinkEditor_NodeTree

class Actor(Node, REF_MubinLinkEditor_NodeTree):
    """Basic Actor"""
    bl_idname = 'actor'
    bl_label = 'Actor'
    bl_icon = 'SPHERE'
    bl_width_default = 240.0
    bl_width_min = 160.0

    definition: bpy.props.StringProperty(name='', default='LinkTagAnd')
    hash_id: bpy.props.StringProperty(
        name='',
        description='The dummy actor\'s HashID as a decimal.\nThis value will not be used in the exported JSON')

    scale: bpy.props.FloatVectorProperty(
        name='',
        default=(1, 1, 1),
        max=1000,
        min=0,
        description='XYZ (Y is UP) | Leave as 0, 0, 0 for automatic placement'
    )
    rotation: bpy.props.FloatVectorProperty(
        name='',
        default=(0, 0, 0),
        max=360,
        min=0,
        description='XYZ (Y is UP) | Leave as 0, 0, 0 for automatic placement'
    )
    translate: bpy.props.FloatVectorProperty(
        name='',
        default=(0, 0, 0),
        max=5000,
        min=-5000,
        description='XYZ (Y is UP) | Leave as 0, 0, 0 for automatic placement'
    )

    ref_object: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name='Reference Object',
        description='Link an object to use it\'s transform values.\n' +
            'Note: It you apply the objects transform, all values will be set to (0, 0, 0)'
    )

    params: bpy.props.CollectionProperty(type=ParamProperties)
    params_index: bpy.props.IntProperty(name='Params Index', default=0)
    
    def init(self, context):
        self.inputs.new('NodeSocketString', "Linked HashID")
        self.outputs.new('NodeSocketShader', "Link to Object(s)")

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print(f'Copying from node {node} . . .')

    # Free function to clean up on removal.
    def free(self):
        print(f'Removing node {self} . . .')

    # Properties on the node and in the properties panel
    def draw_buttons(self, context, layout):
        layout.label(text='Actor Name')
        layout.prop(self, 'definition')
        layout.label(text='Hash Identifier')
        layout.prop(self, 'hash_id')

    # Properties only in the properties panel
    def draw_buttons_ext(self, context, layout):
        # Actor Name
        layout.label(text='Actor Name')
        layout.prop(self, 'definition', icon='OUTLINER_DATA_GP_LAYER')
        layout.separator()


        # Params
        layout.label(text='Parameters')
        row = layout.row()
        row.template_list("MLE_UL_Params", "Params", self, "params", self, "params_index")

        col = row.column()

        col.ui_units_x = 1.0
        sub_col = col.column(align=True)
        sub_col.operator('params.add', text='', icon='ADD')
        sub_col.operator('params.remove', text='', icon='REMOVE')
        sub_col.separator(factor=1.8)

        sub_col.operator('params.move', text='', icon='TRIA_UP').direction = 'UP'
        sub_col.operator('params.move', text='', icon='TRIA_DOWN').direction = 'DOWN'
        sub_col.separator(factor=1.8)

        sub_col.operator('params.clear', text='', icon='PANEL_CLOSE')


        # Param controls
        row = layout.row(align=True)
        row.operator('params.load')
        row.operator('params.copy')
        row.operator('params.import')
        layout.separator()


        # Transform
        layout.label(text='Transforms')

        row = layout.row()

        col = row.column()
        col.label(text='Scale', icon='OBJECT_ORIGIN')
        col.prop(self, 'scale')

        col = row.column()
        col.label(text='Rotation', icon='EMPTY_AXIS')
        col.prop(self, 'rotation')

        col = row.column()
        col.label(text='Translate', icon='EMPTY_ARROWS')
        col.prop(self, 'translate')

        layout.prop(self, 'ref_object', icon='OBJECT_DATA', text='')

        layout.separator()

        # Hash ID
        layout.label(text='Hash Identifier')
        layout.prop(self, 'hash_id', icon='COPY_ID')

class Link(Node):
    """Simple node to link two actors with a signal"""
    bl_idname = 'link'
    bl_label = 'Link'
    bl_icon = 'LINK_BLEND'
    bl_width_default = 160.0
    bl_width_min = 60.0
    
    definition: bpy.props.StringProperty(name='', default='BasicSig')
    params: bpy.props.CollectionProperty(type=ParamProperties)
    params_index: bpy.props.IntProperty(name='Params Index', default=0)

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Input')
        self.outputs.new('NodeSocketString', 'Output')

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print(f'Copying from node {node} . . .')

    # Free function to clean up on removal.
    def free(self):
        print(f'Removing node {self} . . .')

    # Properties on the node and in the properties panel
    def draw_buttons(self, context, layout):
        layout.label(text='Signal Type')
        layout.prop(self, 'definition')

    # Properties only in the properties panel
    def draw_buttons_ext(self, context, layout):
        layout.label(text='Signal Type')
        layout.prop(self, 'definition')
        layout.label(text='Parameters')

        row = layout.row()
        row.template_list("MLE_UL_Params", "Params", self, "params", self, "params_index")
        col = row.column()
        col.ui_units_x = 1.0

        sub_col = col.column(align=True)
        sub_col.operator('params.add', text='', icon='ADD')
        sub_col.operator('params.remove', text='', icon='REMOVE')

        sub_col.separator(factor=1.8)
        sub_col.operator('params.move', text='', icon='TRIA_UP').direction = 'UP'
        sub_col.operator('params.move', text='', icon='TRIA_DOWN').direction = 'DOWN'

        sub_col.separator(factor=1.8)
        sub_col.operator('params.clear', text='', icon='PANEL_CLOSE')

        row = layout.row(align=True)
        row.operator('params.load')
        row.operator('params.copy')
        row.operator('params.import')

class Template(Node):
    """Path to the output json file"""
    bl_idname = 'template'
    bl_label = 'Exporter'
    bl_icon = 'CURRENT_FILE'
    bl_width_default = 120.0
    bl_width_min = 100.0
    
    definition: bpy.props.StringProperty(name='', default='NULL_VALUE')

    template_name: bpy.props.StringProperty(
        name='',
        default='Template Name',
        description='The name of the template seen in Ice-Spear'
    )

    overwrite: bpy.props.BoolProperty(
        name='Overwrite',
        default=True,
        description='Overwrite an existing template with the same name'
    )

    def init(self, context):
        self.outputs.new('NodeSocketString', 'Nodes')

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print(f'Copying from node {node} . . .')

    # Free function to clean up on removal.
    def free(self):
        print(f'Removing node {self} . . .')

    # Properties on the node and in the properties panel
    def draw_buttons(self, context, layout):
        layout.prop(self, 'overwrite')
        layout.operator('json.save_template')
        layout.operator('json.export')

    # Properties only in the properties panel
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, 'overwrite')
        layout.operator('json.save_template')
        layout.operator('json.export')