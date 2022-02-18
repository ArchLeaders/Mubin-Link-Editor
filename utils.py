import bpy
import json
import os
import random
import traceback
import typing
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
        bpy.types.Scene.nodes_index = IntProperty(name = "nodes_index", default = 0)

        bpy.types.Scene.ignore = CollectionProperty(type=ParamProperties)
        bpy.types.Scene.ignore_index = IntProperty(name = "ignore_index", default = 0)

        # get nodes
        nodes = []
        categories = RegisterHelper.data('nodes')

        # register/assign nodes
        for category in categories:
            collect = []
            for item in categories[category]:
                scale = (1, 1, 1)
                cls = categories[category][item].replace('-static', '')
                collect.append(NodeItem(cls, label=item, settings={
                    'definition': repr(item),
                    'scale': repr(scale)
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

    def get_random(type = hex):
        i = '0123456789'
        name = (
            random.choice(i) +
            random.choice(i) +
            random.choice(i) +
            random.choice(i) +
            random.choice(i) +
            random.choice(i) +
            random.choice(i) +
            random.choice(i)
        )

        return type(int(name))

# - - - - - - - - - -
# NODE HELPERS
# - - - - - - - - - -

class NodeHelper:
    """Various helpers for node parameters"""

    hash_id = 0

    def import_actor_merged(actor, scale = (1, 1, 1)):
        """Import an actor and merge it into one object"""
        exp = RegisterHelper.data('config')['exported']
        bpy.ops.wm.collada_import(filepath=f'{exp}\\{actor["BfresName"]}\\{actor["ModelName"]}.dae')

        # clean up model
        imported = bpy.context.selected_objects
        for obj in imported:
            bpy.context.view_layer.objects.active = obj
            if obj.type == 'ARMATURE':
                mb = obj.matrix_basis
                if hasattr(obj.data, 'transform'):
                    obj.data.transform(mb)
                for child in obj.children:
                    child.matrix_local = mb @ child.matrix_local
                obj.matrix_basis.identity()
                bpy.data.objects.remove(obj)
            else:
                for mat in obj.material_slots:
                    print(mat.name, obj.name)
                    obj.active_material_index = 0
                    bpy.data.materials.remove(mat.material)
                    bpy.ops.object.material_slot_remove()
        
        bpy.ops.object.join()
        obj = bpy.context.selected_objects[0]
        obj.modifiers.clear()
        obj.name = actor["ModelName"]

        # get material
        mat = bpy.data.materials.get("basic")
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name="basic")
            mat.diffuse_color = [152/255, 158/255, 189/255, 1.0]
            mat.metallic = 0.3
            mat.roughness = 0.1

        # set material
        obj.data.materials.append(mat)

        return obj

    def import_void(name, scale = (1, 1, 1)):
        bpy.ops.mesh.primitive_cube_add(scale=scale)
        mesh = bpy.context.selected_objects[0]
        mesh.name = name

        # get material
        mat = bpy.data.materials.get("void")
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name="void")
            mat.diffuse_color = [189/255, 175/255, 132/255, 0.5]
            mat.metallic = 0.0
            mat.roughness = 1.0

        # set material
        mesh.data.materials.append(mat)
        
        return mesh

    def get_json(data, definition: str = None):
        json_data = {}
        try:
            if not definition == None:
                if 'LinksToObj' in data:
                    for link in data['LinksToObj']:
                        if link['DefinitionName'] != definition:
                            continue
                        if '!Parameters' in link:
                            for param in link['!Parameters']:
                                if 'params' not in json_data:
                                    json_data['params'] = {}
                                json_data['params'][param] = link['!Parameters'][param]
                                return json_data

            else:
                if '!Parameters' in data:
                    for param in data['!Parameters']:
                        if 'params' not in json_data:
                            json_data['params'] = {}
                        json_data['params'][param] = data['!Parameters'][param]
            
            json_data['scale'] = (1, 1, 1)
            if 'Scale' in data:
                if type(data['Scale']) == list:
                    json_data['scale'] = (
                        float(data['Scale'][0]),
                        float(data['Scale'][1]),
                        float(data['Scale'][2]),
                    )
                else:
                    json_data['scale'] = (
                        float(data['Scale']),
                        float(data['Scale']),
                        float(data['Scale']),
                    )

        except:
            print(traceback.format_exc())

        return json_data

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

    def construct_template(base: bpy.types.NodeLink, tree: bpy.types.NodeTree):

        json_data = {
            'name': tree.name,
            'actors': []
        }

        def parse(value):
            """Parses a value and returns IS type and formatted value"""
            fmt = value.lower()

            # boolean
            if fmt == 'true' or fmt == 'false':
                return {
                    'type': 208,
                    'value': bool(fmt == 'true')
                }
            
            try:
                # float
                if value.contains('.'):
                    # trigger except if it's not a valid float
                    float(value)
                    return {
                        'type': 210,
                        'value': float(value)
                    }

                # int
                else:
                    # trigger except if it's not a valid float
                    int(value)
                    return {
                        'type': 209,
                        'value': int(value)
                    }
            except:
                # str
                return {
                    'type': 160,
                    'value': value
                }

        def format_vector(vector: typing.List[float], compare: bool = True) -> dict:
            """Returns a IS formatted vector"""
            json_data = []
            static_first = vector[0]
            first = vector[0]

            for value in vector:
                if value == first:
                    first = value
                else:
                    first = 0

                json_data.append(
                    {
                        'type': 210,
                        'value': value
                    }
                )

            if first == static_first and compare:
                json_data = {
                    'type': 210,
                    'value': first
                }

            return json_data

        def build_params(params: bpy.types.Node):
            """Returns a IS formatted parameter list"""
            json_data = {}

            for param in params:
                json_data[param.name] = parse(param.value)

            return json_data
        
        def constructor(base: bpy.types.NodeLink):
            """Adds every sub actor to the output json"""
            for node in base.outputs[0].links:
                links = None
                node = node.to_node
                self = NodeHelper.hash_id

                # iterate the links to objects
                for link in node.outputs[0].links:
                    links = []
                    link = link.to_node
                    for dummy in link.outputs[0].links:
                        # update hash id
                        NodeHelper.hash_id = NodeHelper.hash_id + 1
                        links.append({
                            '!Parameters': build_params(link.params),
                            'DefinitionName': {
                                'type': 160,
                                'value': link.definition
                            },
                            'DestUnitHashId': {
                                'type': 211,
                                'value': f'{{ID{NodeHelper.hash_id}}}'
                            }
                        })

                        constructor(link)

                json_data['actors'].append(
                    {
                        '!Parameters': build_params(node.params),
                        'HashId': {
                            'type': 211,
                            'value': f'{{ID{self}}}'
                        },
                        'LinksToObj': links,
                        'Rotate': format_vector(node.ref_object.rotation_euler),
                        'Scale': format_vector(node.ref_object.scale),
                        "SRTHash": {
                            "type": 209,
                            "value": 0
                        },
                        'Translate': format_vector(node.ref_object.location, False),
                        'UnitConfigName': {
                            'type': 160,
                            'value': node.definition
                        }
                    }
                )

        # construct base
        constructor(base)
        return json_data
