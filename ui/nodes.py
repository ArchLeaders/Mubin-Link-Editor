import bpy
from bpy.types import Node
from .properties import ParamProperties
from .node_tree import REF_MubinLinkEditor_NodeTree


class Actor(Node, REF_MubinLinkEditor_NodeTree):
    """Basic Actor"""

    bl_idname = "actor"
    bl_label = "Actor"
    bl_icon = "SPHERE"
    bl_width_default = 240.0
    bl_width_min = 160.0

    definition: bpy.props.StringProperty(name="", default="LinkTagAnd")
    scale: bpy.props.FloatVectorProperty(name="scale", default=(1, 1, 1))

    ref_object: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Reference Object",
        description="Link an object to use it's transform values in the exported template",
    )

    params: bpy.props.CollectionProperty(type=ParamProperties)
    params_index: bpy.props.IntProperty(name="Params Index", default=0)

    def init(self, context):
        self.inputs.new("NodeSocketString", "HashID 1")
        self.outputs.new("NodeSocketShader", "Link to Object(s)")

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        bpy.ops.params.load()
        print(f"Copying from node {node} . . .")

    # Free function to clean up on removal.
    def free(self):
        try:
            bpy.data.objects.remove(self.ref_object)
        except:
            None
        print(f"Removing node {self} . . .")

    # Properties on the node and in the properties panel
    def draw_buttons(self, context, layout):
        layout.label(text="Actor Name")
        layout.prop(self, "definition")
        # row = layout.row(align=True)
        # row.operator('params.load')
        # row.operator('params.import')
        layout.label(text="Transform Object")
        if self.ref_object != None:
            layout.box().label(text=self.ref_object.name, icon="OBJECT_ORIGIN")
        else:
            layout.box().label(text="No Linked Object!", icon="OBJECT_ORIGIN")
        # layout.prop(self, 'ref_object', icon='OBJECT_ORIGIN', text='')

        last_input = self.inputs[len(self.inputs) - 1]
        sec_last_input = self.inputs[len(self.inputs) - 2]

        if last_input.is_linked:
            self.inputs.new("NodeSocketString", f"HashID {len(self.inputs) + 1}")
        elif len(self.inputs) > 1 and not sec_last_input.is_linked:
            self.inputs.remove(last_input)

    # Properties only in the properties panel
    def draw_buttons_ext(self, context, layout):
        # Actor Name
        layout.label(text="Actor Name")
        layout.prop(self, "definition", icon="OUTLINER_DATA_GP_LAYER")
        layout.separator()

        # Params
        layout.label(text="Parameters")
        row = layout.row()
        row.template_list(
            "MLE_UL_Params", "Params", self, "params", self, "params_index"
        )

        col = row.column()

        col.ui_units_x = 1.0
        sub_col = col.column(align=True)
        sub_col.operator("params.add", text="", icon="ADD")
        sub_col.operator("params.remove", text="", icon="REMOVE")
        sub_col.separator(factor=1.8)

        sub_col.operator("params.move", text="", icon="TRIA_UP").direction = "UP"
        sub_col.operator("params.move", text="", icon="TRIA_DOWN").direction = "DOWN"
        sub_col.separator(factor=1.8)

        sub_col.operator("params.clear", text="", icon="PANEL_CLOSE")

        # Param controls
        row = layout.row(align=True)
        row.operator("params.load")
        row.operator("params.copy")
        row.operator("params.import")
        layout.separator()

        # Transform
        layout.label(text="Transform Object (DO NOT CHANGE)")
        layout.prop(self, "ref_object", icon="OBJECT_ORIGIN", text="")
        layout.separator()


class Link(Node):
    """Simple node to link two actors with a signal"""

    bl_idname = "link"
    bl_label = "Link"
    bl_icon = "LINK_BLEND"
    bl_width_default = 160.0
    bl_width_min = 60.0

    definition: bpy.props.StringProperty(name="", default="BasicSig")
    params: bpy.props.CollectionProperty(type=ParamProperties)
    params_index: bpy.props.IntProperty(name="Params Index", default=0)

    def init(self, context):
        self.inputs.new("NodeSocketShader", "Input 1")
        self.outputs.new("NodeSocketString", "Output")

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print(f"Copying from node {node} . . .")

    # Free function to clean up on removal.
    def free(self):
        print(f"Removing node {self} . . .")

    # Properties on the node and in the properties panel
    def draw_buttons(self, context, layout):
        layout.label(text="Signal Type")
        layout.prop(self, "definition")

        last_input = self.inputs[len(self.inputs) - 1]
        sec_last_input = self.inputs[len(self.inputs) - 2]

        if last_input.is_linked:
            self.inputs.new("NodeSocketShader", f"Input {len(self.inputs) + 1}")
        elif len(self.inputs) > 1 and not sec_last_input.is_linked:
            self.inputs.remove(last_input)

    # Properties only in the properties panel
    def draw_buttons_ext(self, context, layout):
        layout.label(text="Signal Type")
        layout.prop(self, "definition")
        layout.label(text="Parameters")

        row = layout.row()
        row.template_list(
            "MLE_UL_Params", "Params", self, "params", self, "params_index"
        )
        col = row.column()
        col.ui_units_x = 1.0

        sub_col = col.column(align=True)
        sub_col.operator("params.add", text="", icon="ADD")
        sub_col.operator("params.remove", text="", icon="REMOVE")

        sub_col.separator(factor=1.8)
        sub_col.operator("params.move", text="", icon="TRIA_UP").direction = "UP"
        sub_col.operator("params.move", text="", icon="TRIA_DOWN").direction = "DOWN"

        sub_col.separator(factor=1.8)
        sub_col.operator("params.clear", text="", icon="PANEL_CLOSE")

        row = layout.row(align=True)
        row.operator("params.load")
        row.operator("params.copy")
        row.operator("params.import")


class Template(Node):
    """Path to the output json file"""

    bl_idname = "template"
    bl_label = "Exporter"
    bl_icon = "CURRENT_FILE"
    bl_width_default = 120.0
    bl_width_min = 100.0

    definition: bpy.props.StringProperty(name="", default="NULL_VALUE")

    template_name: bpy.props.StringProperty(
        name="",
        default="Template Name",
        description="The name of the template seen in Ice-Spear",
    )

    overwrite: bpy.props.BoolProperty(
        name="Overwrite",
        default=True,
        description="Overwrite an existing template with the same name",
    )

    def init(self, context):
        self.outputs.new("NodeSocketString", "Nodes")

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print(f"Copying from node {node} . . .")

    # Free function to clean up on removal.
    def free(self):
        print(f"Removing node {self} . . .")

    # Properties on the node and in the properties panel
    def draw_buttons(self, context, layout):
        layout.prop(self, "overwrite")
        layout.operator("template.save")
        layout.operator("template.export")
        layout.separator()
        layout.operator("template.isolate")

    # Properties only in the properties panel
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "overwrite")
        layout.operator("template.save")
        layout.operator("template.export")
        layout.separator()
        layout.operator("template.isolate")
