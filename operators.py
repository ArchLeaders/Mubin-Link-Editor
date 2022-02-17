import traceback
import bpy
import json

from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator, Context, NodeTree
from nodeitems_utils import register_node_categories, unregister_node_categories
from pathlib import Path

from .utils import Clipboard, NodeHelper, RegisterHelper

# - - - - - - - - - -
# MLE_EXPORTER
# - - - - - - - - - -

class MLE_EXPORTER_OT_ExportTemplate(Operator, ExportHelper):
    """Export the connected node tree as Json to be ued in Ice-Spear"""
    bl_idname = 'json.export'
    bl_label = 'Export Json'

    filename_ext = '.json'
    filter_glob: StringProperty( default='*.json', options={'HIDDEN'} )

    def execute(self, context: Context):
        if not Path(str(self.filepath)).suffix.lower() == '.json':
            self.filepath = f'{self.filepath}.json'

        # Get node stuff and export
        node_tree: NodeTree = context.space_data.edit_tree
        for node in node_tree.nodes:
            if node.name == 'Export':
                for node_out in node.outputs:
                    for node_link in node_out.links:
                        print(node_link.to_node.actor_name)


        return {'FINISHED'}

class MLE_EXPORTER_OT_SaveTemplate(Operator):
    """Saves the node setup as a template in the Ice-Spear data directory."""
    bl_idname = 'json.save_template'
    bl_label = 'Save Template'

    def execute(self, context: Context):
        # Get node stuff and export
        node_tree: NodeTree = context.space_data.edit_tree
        for node in node_tree.nodes:
            if node.name == 'Export':
                for node_out in node.outputs:
                    for node_link in node_out.links:
                        print(node_link.to_node.actor_name)


        return {'FINISHED'}

# - - - - - - - - - -
# MLE_PARAMS
# - - - - - - - - - -

class MLE_PARAMS_OT_Add(Operator):
    bl_idname = 'params.add'
    bl_label = 'Add'

    def execute(self, context):
        node = []
        try:
            node = context.active_node
        except:
            self.report({'ERROR'}, f'Select a node to edit')
            return {'CANCELLED'}
        
        value = node.params.add()
        value.name = 'Key'
        return {'FINISHED'}
        ...

class MLE_PARAMS_OT_Remove(Operator):
    bl_idname = 'params.remove'
    bl_label = 'Remove'

    def execute(self, context):
        node = []
        try:
            node = context.active_node
        except:
            self.report({'ERROR'}, f'Select a node to edit')
            return {'CANCELLED'}

        if not len(node.params) > 0:
            return {'CANCELLED'}

        node.params.remove(node.params_index)
        node.params_index = min(max(0, node.params_index - 1), len(node.params) - 1)
        return {'FINISHED'}

class MLE_PARAMS_OT_MoveItem(Operator):
    bl_idname = 'params.move'
    bl_label = 'Move'

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    def move_index(self, context):
        # get selected
        node = node = context.active_node

        # add/subtract index
        list_length = len(node.params) - 1
        new_index = node.params_index + (-1 if self.direction == 'UP' else 1)
        node.params_index = max(0, min(new_index, list_length))

    def execute(self, context):
        node = []
        try:
            node = context.active_node
        except:
            self.report({'ERROR'}, f'Select a node to edit')
            return {'CANCELLED'}

        if not len(node.params) > 0:
            return {'CANCELLED'}

        neighbor = node.params_index + (-1 if self.direction == 'UP' else 1)
        node.params.move(neighbor, node.params_index)
        self.move_index(context)

        return{'FINISHED'}

class MLE_PARAMS_OT_Clear(Operator):
    bl_idname = 'params.clear'
    bl_label = 'Clear'

    def execute(self, context):
        node = []

        try:
            node = context.active_node
        except:
            self.report({'ERROR'}, f'Select a node to edit')
            return {'CANCELLED'}

        node.params.clear()
        return {'FINISHED'}

class MLE_PARAMS_OT_Load(Operator):
    """Loads the default parameters for the selected actor"""
    bl_idname = 'params.load'
    bl_label = 'Load'

    def execute(self, context):
        # get selected node
        node = []
        try:
            node = context.active_node
        except:
            self.report({'ERROR'}, f'Select a node to edit')
            return {'CANCELLED'}

        node.params.clear()

        load_results = {}
        errno = f'Parameters for {node.definition} could not be found.'
        if node.bl_idname == 'actor':
            load_results = NodeHelper.load_actor_data(node.definition)
        elif node.bl_idname == 'link':
            errno = f'Parameters for {node.definition} could not be found in {node.inputs[0].links[0].from_node.definition}.'
            load_results = NodeHelper.load_actor_data(node.inputs[0].links[0].from_node.definition, node.definition)

        if load_results == {} or load_results == None:
            self.report({'ERROR'}, errno)
            return {'CANCELLED'}

        for key in load_results:
            param = node.params.add()
            param.name = str(key)
            param.value = str(load_results[key])

        return {'FINISHED'}

class MLE_PARAMS_OT_Copy(Operator):
    """Copies the parameters to the clipboard as Json"""
    bl_idname = 'params.copy'
    bl_label = 'Copy'

    def execute(self, context):
        # get selected node
        node = []
        try:
            node = context.active_node
        except:
            self.report({'ERROR'}, f'Select a node to edit')
            return {'CANCELLED'}

        # get clipborad data
        json_data = {}
        for param in node.params:
            json_data[param.name] = param.value

        if json_data == {}:
            self.report({'WARNING'}, f'Parameters were empty!')
            return {'CANCELLED'}

        Clipboard.set(json.dumps(json_data, indent=4))
        self.report({'INFO'}, f'Json copied to clipboard')
        return {'FINISHED'}

class MLE_PARAMS_OT_Import(Operator):
    """Imports json data from the clipboard and sets the parameters with it"""
    bl_idname = 'params.import'
    bl_label = 'Import'

    def execute(self, context):
        # get selected node
        node = []
        try:
            node = context.active_node
        except:
            self.report({'ERROR'}, f'Select a node to edit')
            return {'CANCELLED'}

        # clear current
        node.params.clear()

        # get clipborad data
        json_data = {}
        try:
            json_data = json.loads(Clipboard.get().strip())
        except:
            self.report({'ERROR'}, f'Clipboard did not contain valid Json data')
            return {'CANCELLED'}

        # attempt to read the clipboard data
        try:
            for key in json_data:
                # parse Ice-Spear json data
                if 'UnitConfigName' in json_data:
                    set = False
                    # set actor values
                    if node.bl_idname == 'actor':
                        # set parameters
                        set = True
                        if '!Parameters' in json_data:
                            for sub_key in json_data['!Parameters']:
                                if str(sub_key) in RegisterHelper.data('ignore'):
                                    self.report({'WARNING'}, f'{str(sub_key)} was ignored')
                                    continue

                                param = node.params.add()
                                param.name = str(sub_key)
                                try:
                                    param.value = str(json_data['!Parameters'][sub_key]['value'])
                                except:
                                    param.value = str(json.dumps(json_data['!Parameters'][sub_key]))

                        # set name and defenition
                        node.definition = str(json_data['UnitConfigName']['value'])
                        node.label = str(json_data['UnitConfigName']['value'])

                    elif node.bl_idname == 'link':
                        if 'LinksToObj' in json_data:
                            for link in json_data['LinksToObj']:
                                # look for link defenition
                                if link['DefinitionName']['value'] != node.defenition:
                                    continue

                                # set link parameters
                                if '!Parameters' in link:
                                    for sub_key in link['!Parameters']:
                                        set = True
                                        param = node.params.add()
                                        param.name = str(sub_key)
                                        param.value = str(json_data['LinksToObj'][link]['!Parameters'][sub_key]['value'])
                    
                    # return results
                    if not set: self.report({'WARNING'}, f'No link for \'{node.defenition}\' could be found!')
                    return {'FINISHED'}

                # parse Ice-Spear parameters
                elif 'value' in json_data[key]:
                    param = node.params.add()
                    param.name = str(key)
                    param.value = str(json_data[key]['value'])

                # parse MLE parameters
                else:
                    param = node.params.add()
                    param.name = str(key)
                    param.value = str(json_data[key])
        except:
            print(traceback.format_exc())
            self.report({'ERROR'}, f'Json data was not in the correct format')
            return {'CANCELLED'}

        return {'FINISHED'}

# - - - - - - - - - -
# MLE_NODES
# - - - - - - - - - -

class MLE_NODES_OT_Save(Operator):
    bl_idname = 'nodes.save'
    bl_label = 'Save'

    def execute(self, context):
        col = RegisterHelper.data('nodes')
        new_col = {}

        # save static
        for group in col:
            for item in col[group]:
                if str(col[group][item]).endswith('-static'):
                    if group not in new_col:
                        new_col[group] = {}
                    new_col[group][item] = col[group][item]

        # save json
        for param in context.scene.nodes:
            if param.name not in new_col:
                new_col[param.name] = {}
            new_col[param.name][param.value] = 'actor'

        RegisterHelper.data('nodes', write=True, write_data=new_col)
        unregister_node_categories('BOTWMUBINEDITOR_NODETREE')
        register_node_categories('BOTWMUBINEDITOR_NODETREE', RegisterHelper.construct_nodes())
        return {'FINISHED'}

class MLE_NODES_OT_Sync(Operator):
    bl_idname = 'nodes.sync'
    bl_label = 'Sync'

    def execute(self, context):
        categories = RegisterHelper.data('nodes')
        context.scene.nodes.clear()

        # register/assign nodes
        for category in categories:
            for item in categories[category]:
                if not str(categories[category][item]).endswith('-static'):
                    node = context.scene.nodes.add()
                    node.name = category
                    node.value = item

        return {'FINISHED'}
        ...

class MLE_NODES_OT_Add(Operator):
    bl_idname = 'nodes.add'
    bl_label = 'Add'

    def execute(self, context):
        value = context.scene.nodes.add()
        value.name = 'Actor'
        return {'FINISHED'}
        ...

class MLE_NODES_OT_Remove(Operator):
    bl_idname = 'nodes.remove'
    bl_label = 'Remove'

    def execute(self, context):
        context.scene.nodes.remove(context.scene.nodes_index)
        context.scene.nodes_index = min(max(0, context.scene.nodes_index - 1), len(context.scene.nodes) - 1)
        return {'FINISHED'}

class MLE_NODES_OT_MoveItem(Operator):
    bl_idname = 'nodes.move'
    bl_label = 'Move'

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    def move_index(self, context):
        # add/subtract index
        list_length = len(context.scene.nodes) - 1
        new_index = context.scene.nodes_index + (-1 if self.direction == 'UP' else 1)
        context.scene.nodes_index = max(0, min(new_index, list_length))

    def execute(self, context):
        neighbor = context.scene.nodes_index + (-1 if self.direction == 'UP' else 1)
        context.scene.nodes.move(neighbor, context.scene.nodes_index)
        self.move_index(context)

        return{'FINISHED'}

class MLE_NODES_OT_Clear(Operator):
    bl_idname = 'nodes.clear'
    bl_label = 'Clear'

    def execute(self, context):
        context.scene.nodes.clear()
        return {'FINISHED'}

# - - - - - - - - - -
# MLE_IGNORE
# - - - - - - - - - -

class MLE_IGNORE_OT_Save(Operator):
    bl_idname = 'ignore.save'
    bl_label = 'Save'

    def execute(self, context):
        bpy.ops.script.reload()

        return {'FINISHED'}

class MLE_IGNORE_OT_Sync(Operator):
    bl_idname = 'ignore.sync'
    bl_label = 'Sync'

    def execute(self, context):
        ignored = RegisterHelper.data('ignore')
        context.scene.ignore.clear()

        # register/assign nodes
        for item in ignored:
            node = context.scene.ignore.add()
            node.name = item

        return {'FINISHED'}
        ...

class MLE_IGNORE_OT_Add(Operator):
    bl_idname = 'ignore.add'
    bl_label = 'Add'

    def execute(self, context):
        value = context.scene.ignore.add()
        value.name = 'Value'
        return {'FINISHED'}
        ...

class MLE_IGNORE_OT_Remove(Operator):
    bl_idname = 'ignore.remove'
    bl_label = 'Remove'

    def execute(self, context):
        context.scene.ignore.remove(context.scene.ignore_index)
        context.scene.ignore_index = min(max(0, context.scene.ignore_index - 1), len(context.scene.ignore) - 1)
        return {'FINISHED'}

class MLE_IGNORE_OT_MoveItem(Operator):
    bl_idname = 'ignore.move'
    bl_label = 'Move'

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    def move_index(self, context):
        # add/subtract index
        list_length = len(context.scene.ignore) - 1
        new_index = context.scene.ignore_index + (-1 if self.direction == 'UP' else 1)
        context.scene.ignore_index = max(0, min(new_index, list_length))

    def execute(self, context):
        neighbor = context.scene.ignore_index + (-1 if self.direction == 'UP' else 1)
        context.scene.ignore.move(neighbor, context.scene.ignore_index)
        self.move_index(context)

        return{'FINISHED'}

class MLE_IGNORE_OT_Clear(Operator):
    bl_idname = 'ignore.clear'
    bl_label = 'Clear'

    def execute(self, context):
        context.scene.ignore.clear()
        return {'FINISHED'}