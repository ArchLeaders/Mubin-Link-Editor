import bpy
import json
import os
import traceback
import yaml

from nodeitems_utils import NodeCategory, NodeItem
from bpy.props import IntProperty, CollectionProperty
from pathlib import Path
from oead import byml, yaz0

from .ui.properties import ParamProperties

# - - - - - - - - - -
# MLE BASE CLASSES
# - - - - - - - - - -

class MLEBase:
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'MubinLinkEditor_NodeTree'

class MLECategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'MubinLinkEditor_NodeTree'

# - - - - - - - - - -
# CLIPBOARD DATA
# - - - - - - - - - -

class Clipboard:
    def set(content: str):
        bpy.context.window_manager.clipboard = content

    def get():
        return bpy.context.window_manager.clipboard

# - - - - - - - - - -
# REGISTER HELPERS
# - - - - - - - - - -

class RegisterHelper:
    """Various helpers for registering bpy elements"""

    def construct_nodes():
        # add node/ignore lists
        bpy.types.Scene.nodes = CollectionProperty(type=ParamProperties)
        bpy.types.Scene.nodes_index = IntProperty(name = "NAME__nodes_index", default = 0)

        bpy.types.Scene.ignore = CollectionProperty(type=ParamProperties)
        bpy.types.Scene.ignore_index = IntProperty(name = "NAME__ignore_index", default = 0)

        # get nodes
        nodes = []
        categories = RegisterHelper.data('nodes')

        # register/assign nodes
        for category in categories:
            collect = []
            for item in categories[category]:
                collect.append(NodeItem(categories[category][item].replace('-static', ''), label=item, settings={
                    'definition': repr(item)
                }))
            
            nodes.append(MLECategory(category.upper(), category, items=collect))
        
        return nodes
    
    def data(set: str = 'config', type: str = 'json', write: bool = False, write_data = {}):
        if write:
            if type.lower() == 'json':
                Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_link_editor\\{set}.json').write_text(json.dumps(write_data, indent=4))
            elif set.lower() == 'yaml':
                yaml.dump(write_data, Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_link_editor\\{set}.json').open())
        else:
            if type.lower() == 'json':
                return json.loads(Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_link_editor\\{set}.json').read_text())
            elif set.lower() == 'yaml':
                return yaml.load(Path(f'{os.environ["LOCALAPPDATA"]}\\mubin_link_editor\\{set}.yml').open())

# - - - - - - - - - -
# NODE HELPERS
# - - - - - - - - - -

class NodeHelper:
    """Various helpers for node parameters"""

    def get_json(data, definition: str = None):
        try:
            json_data = {}
            if not definition == None:
                if 'LinksToObj' in data:
                    for link in data['LinksToObj']:
                        print(link['DefinitionName'], definition)
                        if link['DefinitionName'] != definition:
                            continue
                        if '!Parameters' in link:
                            for param in link['!Parameters']:
                                json_data[param] = link['!Parameters'][param]
                                return json_data

            else:
                if '!Parameters' in data:
                    for param in data['!Parameters']:
                        json_data[param] = data['!Parameters'][param]
                    return json_data
        except:
            print(traceback.format_exc())

    def load_actor_data(name: str, definition: str = None):
        fields = [ 'MainField', 'AocField' ]
        letters = 'ABCDEFGHIJ'
        numbers = '12345678'
        types = ['Static', 'Dynamic']

        aoc_dir = '_nx'
        if RegisterHelper.data('..\\bcml\\settings')['wiiu']:
            aoc_dir = ''
        aoc_dir = RegisterHelper.data('..\\bcml\\settings')[f'dlc_dir{aoc_dir}']

        for field in fields:
            for let in letters:
                for num in numbers:
                    for type in types:
                        file = Path(f'{aoc_dir}\\Map\\{field}\\{let}-{num}\\{let}-{num}_{type}.smubin')

                        byml_data = byml.from_binary(yaz0.decompress(file.read_bytes()))
                        for obj in byml_data['Objs']:
                            if 'UnitConfigName' in obj:
                                if obj['UnitConfigName'] != name:
                                    continue

                                json_data = NodeHelper.get_json(obj, definition)

                                if json_data == None:
                                    continue

                                return json_data
        return None
