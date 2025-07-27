import os
import json
import uuid
import strawberry
import aiohttp
import graphql
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from graphql.language.ast import (
    DocumentNode, 
    ObjectTypeDefinitionNode, 
    FieldDefinitionNode, 
    NamedTypeNode, 
    NonNullTypeNode, 
    ListTypeNode,
    FieldNode,
    SelectionSetNode,
    OperationDefinitionNode,
    NameNode,
    OperationType,
    SelectionNode,
    StringValueNode,
    ArgumentNode,
    VariableDefinitionNode,
    VariableNode,
    FragmentDefinitionNode,
    IntValueNode,
    NullValueNode, 
    ListValueNode
)
from graphql.language import print_ast
from typing import List, Optional

from uoishelpers.cmds.utils_sdl_2 import build_query_page, build_query_scalar, explain_graphql_query
def unwrap_type(type_node):
    while isinstance(type_node, (NonNullTypeNode, ListTypeNode)):
        type_node = type_node.type
    if isinstance(type_node, NamedTypeNode):
        return type_node
    return None

def HTML(query, data):
    script_dir = os.path.dirname(os.path.abspath(__file__))  # složka, kde je tento .py soubor
    template_path = os.path.join(script_dir, "template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        result = f.read()
    result = result.replace('`data`', json.dumps(data))
    result = result.replace('`query`', f'`{query}`')
    return result

# def buildQuery(ast, field_name):
#     # Najdeme definici operace typu 'query'
#     with open("ast.json", "w", encoding="utf-8") as f:
#         json.dump(ast, f, default=str, indent=4)

#     operation_def = None
#     print(f"field_name: {field_name}")
#     definitions = ast.get('definitions', [])
#     schema_definition = next(filter(lambda dfn: dfn.get("kind", None) == "schema_definition", definitions), None) 
#     # print(f"schema_definition: {schema_definition}")
#     query_type = next(filter(lambda dfn: dfn.get("operation") == "query", schema_definition["operation_types"]), None)
#     query_type_name = query_type["type"]["name"]["value"]
#     # print(f"definitions: {definitions}")
#     query_type_def = next(filter(lambda dfn: dfn.get("kind", None) == "object_type_definition" and dfn["name"]["value"]==query_type_name, definitions), None)
#     # print(f"query_type_def: {query_type_def}")
#     operation_def = query_type_def
#     # for defn in definitions:
#     #     if defn.get('kind') == 'OperationDefinition' and defn.get('operation') == 'query':
#     #         operation_def = defn
#     #         break
#     # for defn in definitions:
#     #     if defn.get('kind') == 'ObjectTypeDefinition' and defn.get('name', {}).get('value') == 'Query':
#     #         operation_def = defn
#     if operation_def is None:
#         print(f"operation_def not found")
#         return None  # žádná query operace v dokumentu
    
#     def unwrap_type_ast(type_node):
#         kind = type_node['kind']
#         # print(f"unwrap_type_ast({type_node})[{kind}] * {kind == 'named_type'}")
        
#         if kind == 'named_type':
#             # print(f"unwrap_type_ast.return {type_node['name']['value']}")
#             return type_node['name']['value']
#         elif kind in ('non_null_type', 'list_type'):
#             return unwrap_type_ast(type_node['type'])
#         else:
#             return None
        
#     def find_field(fields, name):
#         return next((f for f in fields if f['name']['value'] == name), None)
    
#     def find_return_type(ast_doc, field_ast, field_name):
#         """
#         - ast_doc: celý AST dokument
#         - field_ast: AST typu (např. objekt typu Query nebo jiný objekt),
#                     ve kterém hledáme pole `field_name`
#         - field_name: název pole, jehož návratový typ chceme najít

#         Vrací jméno návratového typu pole nebo None
#         """
#         if not field_ast or 'fields' not in field_ast:
#             # print(f"find_return_type {field_name} :(")
#             return None

#         fields = field_ast['fields']
#         # print(f"find_return_type.fields {field_name}@{fields}")
#         for f in fields:
#             if f.get('name', {}).get('value') == field_name:
#                 # print(f"found {f}")
#                 # máme pole, rozbalíme typ
#                 return unwrap_type_ast(f['type'])

#         # Pokud pole nenajdeme v daném typu, můžeme zkusit vyhledat typ v ast_doc a rekurzivně pokračovat,
#         # ale to záleží na tom, jak chceš hluboko hledat. Pro jednoduchost vrátíme None.
#         return None

#     def is_scalar_type(ast_doc, type_ast):
#         # Rozbalíme na základní typ
#         type_name = unwrap_type_ast(type_ast)
#         if not type_name:
#             return False

#         # Najdeme definici typu v ast_doc
#         for defn in ast_doc.get('definitions', []):
#             if defn.get('kind') in ('ScalarTypeDefinition', 'ScalarTypeExtension'):
#                 if defn.get('name', {}).get('value') == type_name:
#                     return True

#         # Některé běžné built-in scalars (pokud nejsou v ast_doc explicitně)
#         builtin_scalars = {"Int", "Float", "String", "Boolean", "ID"}
#         if type_name in builtin_scalars:
#             return True

#         return False

#     def is_object_type(ast_doc, type_ast):
#     # Rozbalíme typ na základní jméno
#         type_name = unwrap_type_ast(type_ast)
#         if not type_name:
#             return False

#         # Hledáme v definicích typů AST ObjectTypeDefinition nebo ObjectTypeExtension
#         for defn in ast_doc.get('definitions', []):
#             if defn.get('kind') in ('ObjectTypeDefinition', 'ObjectTypeExtension'):
#                 if defn.get('name', {}).get('value') == type_name:
#                     return True

#         return False

#     def is_object_type(ast_doc, type_ast):
#         type_name = unwrap_type_ast(type_ast)
#         if not type_name:
#             return False
#         for defn in ast_doc.get('definitions', []):
#             if defn.get('kind') in ('object_type_definition', 'object_type_extension'):
#                 if defn.get('name', {}).get('value') == type_name:
#                     return True
#         return False
    
#     def is_list_of_objects(ast_doc, type_ast):
#         """
#         Rozhodne, jestli type_ast je List[Object!], tj.:
#         - type_ast.kind == 'ListType'
#         - jeho typ je NonNullType
#         - a ten NonNullType obsahuje NamedType odpovídající Object typu
#         """

#         if type_ast['kind'] != 'non_null_type':
#             return False
#         type_ast = type_ast['type']
#         if type_ast['kind'] != 'list_type':
#             return False

#         # Vezmeme typ prvků listu
#         inner_type = type_ast['type']

#         # Musí být NonNullType
#         if inner_type['kind'] != 'non_null_type':
#             return False

#         # A NonNullType musí mít NamedType, který je Object typ
#         named_type = inner_type['type']
#         if named_type['kind'] != 'named_type':
#             return False

#         type_name = named_type['name']['value']

#         # Zkontrolujeme, jestli typ je Object
#         for defn in ast_doc.get('definitions', []):
#             if defn.get('kind') in ('object_type_definition', 'object_type_extension'):
#                 if defn.get('name', {}).get('value') == type_name:
#                     return True

#         return False

#     def has_only_optional_params(field_ast):
#         # Zkontroluje, jestli field nemá povinné parametry (non-null bez defaultu)
#         params = field_ast.get('arguments', [])
#         for p in params:
#             # předpokládáme, že non-null typ je typ s kind == 'NonNullType' a nemá default
#             if p.get('type', {}).get('kind') == 'non_null_type' and 'defaultValue' not in p:
#                 return False
#         return True
        
#     def find_type_def(ast_doc, type_name):
#         definitions = ast_doc.get('definitions', [])
#         result = next(filter(lambda dfn: dfn.get("kind", None) == "object_type_definition" and dfn["name"]["value"]==type_name, definitions), None)
#         return result

#     def create_fragment_for_scalars(ast_doc, field_name, field_return_type_name):
#         # najde jen ty fieldy, ktere vraci typy oznacene jako skalary
#         # ignoruje fieldy, ktere maji povinne parametry

#         type_def = find_type_def(ast_doc, field_return_type_name)
#         # Najdeme definici typu podle jména

#         if not type_def:
#             # Typ nenalezen, prázdný fragment
#             return {
#                 "kind": "fragment_definition",
#                 "name": {"kind": "name", "value": f"{field_return_type_name}LinkFragment"},
#                 "type_condition": {"kind": "named_type", "name": {"kind": "name", "value": field_return_type_name}},
#                 "selection_set": {"kind": "selection_set", "selections": [
#                     {
#                         "kind": "field",
#                         "name": {"kind": "name", "value": "__typename"}
#                     }                    
#                 ]}
#             }

#         fragment_fields = [{
#             "kind": "field",
#             "name": {"kind": "name", "value": "__typename"}
#         }]

#         for field in type_def.get('fields', []):
#             if is_scalar_type(ast_doc, field['type']) and has_only_optional_params(field):
#                 fragment_fields.append({
#                     "kind": "field",
#                     "name": field['name']
#                 })

#         return {
#             "kind": "fragment_definition",
#             "name": {"kind": "name", "value": f"{field_return_type_name}LinkFragment"},
#             "type_condition": {"kind": "named_type", "name": {"kind": "name", "value": field_return_type_name}},
#             "selection_set": {
#                 "kind": "selection_set",
#                 "selections": fragment_fields
#             }
#         }


#     def create_fragment_for_objects(ast_doc, field_name, field_return_type_name):
#         # najde jen ty fieldy, ktere vraci typy oznacene jako Object
#         # ignoruje fieldy, ktere maji povinne parametry
#         # vystup je jako ast
#         # Rozbalíme typ na NamedType AST uzel

#         type_def = find_type_def(ast_doc, field_return_type_name)

#         if not type_def:
#             # Typ nenalezen, prázdný fragment
#             return {
#                 "kind": "fragment_definition",
#                 "name": {"kind": "name", "value": f"{field_return_type_name}MediumFragment"},
#                 "type_condition": {"kind": "named_type", "name": {"kind": "name", "value": field_return_type_name}},
#                 "selection_set": {"kind": "selection_set", "selections": [
#                     {
#                         "kind": "field",
#                         "name": {"kind": "name", "value": "__typename"}
#                     }
#                 ]}
#             }

#         fragment_fields = [{
#             "kind": "field",
#             "name": {"kind": "name", "value": "__typename"}
#         }]
#         fragment_fields.extend(
#             build_selection_set_ext(ast_doc, field_return_type_name)
#         )
#         # for field in type_def.get('fields', []):
#         #     if is_object_type(ast_doc, field['type']) and has_only_optional_params(field):
#         #         fragment_fields.append({
#         #             "kind": "field",
#         #             "name": field['name']
#         #         })

#         return {
#             "kind": "fragment_definition",
#             "name": {"kind": "name", "value": f"{field_return_type_name}MediumFragment"},
#             "type_condition": {"kind": "named_type", "name": {"kind": "name", "value": field_return_type_name}},
#             "selection_set": {
#                 "kind": "selection_set",
#                 "selections": fragment_fields
#             }
#         }

#     def iter_vectors_with_optional_params(ast_doc, field_name, field_return_type_name):
#         # Rozbalíme typ na NamedType AST uzel
#         type_def = find_type_def(ast_doc, field_return_type_name)
#         # allowed_params = {"skip", "limit", "where"}

#         for field in type_def.get('fields', []):
#             print(f"iter_vectors_with_optional_params.{field_return_type_name} => {field}")
#             if is_list_of_objects(ast_doc, field['type']) and has_only_optional_params(field):
#                 defn = {
#                     "kind": "field",
#                     "name": field['name']
#                 }    
#                 yield defn

#     def build_selection_set(ast_doc, field_return_type_name):
#         type_def = find_type_def(ast_doc, field_return_type_name)
#         selections = [{
#             "kind": "field",
#             "name": {"kind": "name", "value": "__typename"}
#         }]
#         for field in type_def.get('fields', []):
#             field_type = field["type"]
#             field_type_name = unwrap_type_ast(field_type)
#             # field_type_name = field["type"]["name"]["value"]
#             field_type = find_type_def(ast_doc, field_type_name)

#             arguments = field["arguments"]
#             mandatory_arguments = [
#                 argument 
#                 for argument in arguments 
#                 if is_mandatory_argument(argument)
#             ]            
#             if len(mandatory_arguments) != 0:
#                 continue
#             if field_type is None:
#                 selections.append(
#                     {
#                         "kind": "field",
#                         "name": field['name']
#                     }
#                 )
#             continue
#             # selection = {
#             #     "kind": "field",
#             #     "name": {
#             #         "kind": "name",
#             #         "value": f'{field["name"]["value"]}'
#             #     },
#             #     "selection_set": {
#             #         "kind": "selection_set",
#             #         "selections": [
#             #             {
#             #                 "kind": "field",
#             #                 "name": {"kind": "name", "value": "__typename"}
#             #             }
#             #         ]
#             #     }
#             # }
#             # selections.append(selection)
#         return selections
    
#     def is_non_null_type(type_node):
#         # Vrací True, pokud je top-level typ NonNullType (i když je zabalený v listu)
#         kind = type_node.get("kind")
#         if kind == "non_null_type":
#             return True
#         elif kind == "list_type":
#             # pokud je list_type, zkus zkontrolovat jeho typ rekurzivně
#             return is_non_null_type(type_node.get("type", {}))
#         else:
#             return False    
        
#     def is_mandatory_argument(arg):
#         # Je argument povinný?
#         # Povinný = top-level non_null_type + default_value není definováno nebo je None / null_value

#         default_value = arg.get('default_value')
#         # print(f"default_value={default_value}")
#         if default_value is None:
#             return True
#         return False
#         # is_non_null = is_non_null_type(arg.get('type', {}))

#         # has_default = default_value is not None and not (
#         #     isinstance(default_value, dict) and default_value.get('kind') == 'null_value'
#         # )

#         # return is_non_null and not has_default        
        
#     def build_selection_set_ext(ast_doc, field_return_type_name):
#         type_def = find_type_def(ast_doc, field_return_type_name)
#         selections = []
#         for field in type_def.get('fields', []):
#             field_name = field["name"]["value"]
#             field_type = field["type"]
#             field_type_name = unwrap_type_ast(field_type)
#             # field_type_name = field["type"]["name"]["value"]
#             arguments = field["arguments"]
#             mandatory_arguments = [
#                 argument 
#                 for argument in arguments 
#                 if is_mandatory_argument(argument)
#             ]

#             field_type = find_type_def(ast_doc, field_type_name)
#             if field_type is None:
                
#                 if not mandatory_arguments:
#                     selections.append(
#                         {
#                             "kind": "field",
#                             "name": field['name']
#                         }
#                     )
#                 continue
#             # print(f"build_selection_set_ext.mandatory_arguments@{field['name']['value']}={mandatory_arguments}\narguments\n\t{arguments}")
            
#             if mandatory_arguments:
#                 selection = {
#                     "kind": "field",
#                     "name": {
#                         "kind": "name",
#                         "value": f'{field["name"]["value"]}'
#                     },
#                     "selection_set": {
#                         "kind": "selection_set",
#                         "selections": [
#                             {
#                                 "kind": "field",
#                                 "name": {"kind": "name", "value": "__typename"}
#                             }
#                         ]
#                     }
#                 }
#             else:
#                 selection = {
#                     "kind": "field",
#                     "name": {
#                         "kind": "name",
#                         "value": f'{field["name"]["value"]}'
#                     },
#                     "selection_set": {
#                         "kind": "selection_set",
#                         "selections": build_selection_set(ast_doc, field_type_name)
#                     }
#                 }
#             selections.append(selection)
#         return selections

#     def typename_already_present(selections):
#         return any(sel['kind'] == 'field' and sel['name']['value'] == '__typename' for sel in selections)

#     # def build_read_query(ast_doc, field_name):
#     ast_doc = ast
#     field_return_type_ast = find_return_type(ast_doc, operation_def, field_name)
#     if not field_return_type_ast:
#         print(f"field_name {field_name} not found")
#         return None
#     else:
#         print(f"field_name {field_name} found {field_return_type_ast}")

#     ast_scalars_fragment = create_fragment_for_scalars(ast_doc, field_name, field_return_type_ast)
#     # print(f"field_name {field_name} ast_scalars_fragment {ast_scalars_fragment}")
#     ast_objects_fragment = create_fragment_for_objects(ast_doc, field_name, field_return_type_ast)
#     # print(f"field_name {field_name} ast_objects_fragment {ast_objects_fragment}")

#     clsmap = {
#         "document": DocumentNode,
#         "operation_definition": OperationDefinitionNode,
#         "field": FieldNode,
#         "selection_set": SelectionSetNode,
#         "name": NameNode,
#         "argument": ArgumentNode,
#         "variable": VariableNode,
#         "fragment_definition": FragmentDefinitionNode,
#         "named_type": NamedTypeNode,
#         "name": NameNode,
#         "variable_definition": VariableDefinitionNode,
#         "variable": VariableNode,
#         "non_null_type": NonNullTypeNode,
#         "string_value": StringValueNode,
#         "int_value": IntValueNode,
#         "null_value": NullValueNode,
#         "list_type": ListTypeNode
#         # další typy AST uzlů
#     }
#     def fromDict(node: dict):
#         kind = node.get("kind", None)
#         assert kind is not None, f"found node without kind {node}"
#         cls = clsmap[kind]
#         params = {}
#         for key, value in node.items():
#             if isinstance(value, list):
#                 params[key] = [fromDict(item) for item in value]
#             elif isinstance(value, dict):
#                 params[key] = fromDict(value)
#             else:
#                 params[key] = value
#         return cls(**params)


#     # Příprava selectionSet - začneme s poli scalars a objects
#     selections = [] # selection_set
#     # print(f"ast_scalars_fragment {list(ast_scalars_fragment.keys())}")
#     ast_scalars_fragment_selections = ast_scalars_fragment["selection_set"]["selections"]
#     ast_objects_fragment_selections = ast_objects_fragment["selection_set"]["selections"]
#     selections = [*ast_scalars_fragment_selections, *ast_objects_fragment_selections]
#     selectionsmap = {
#         selection["name"]["value"]: selection for selection in selections
#     }
#     selections = list(selectionsmap.values())
#     # selections = [
#     #     {
#     #         "kind": "field",
#     #         "name": {"kind": "name", "value": "__typename"}
#     #     }                    
#     # ]
#     field_def = next(filter(lambda field: field["name"]["value"]==field_name, query_type_def["fields"]), None) 
#     field_def_arguments = field_def["arguments"]

#     {
#         "kind": "variable_definition",
#         "variable": {
#             "kind": "variable",
#             "name": {
#                 "kind": "name",
#                 "value": "id"
#             }
#         },
#         "type": {
#             "kind": "non_null_type",
#             "type": {
#                 "kind": "named_type",
#                 "name": {
#                     "kind": "name",
#                     "value": "ID"
#                 }
#             }
#         },
#         "default_value": None,
#         "directives": []
#     }

#     variables = [
#         {
#             "kind": "variable_definition",
#             "description": argument.get("description", None),
#             "variable": {
#                 "kind": "variable",
#                 "name": {
#                     "kind": "name",
#                     "value": argument["name"]["value"]
#                 }
#             },
#             "type": argument["type"],
#             "default_value": argument["default_value"],
#             "directives": []
#         } for argument in field_def_arguments
#     ]
#     arguments = [
#         {
#             "kind": "argument",
#             "name": {
#                 "kind": "name",
#                 "value": argument["name"]["value"]
#             },
#             "value": {
#                 "kind": "variable",
#                 "name": {
#                     "kind": "name",
#                     "value": argument["name"]["value"]
#                 }
#             }
#         } for argument in field_def_arguments
#     ]
#     root_field = {
#         "kind": "field",
#         "directives": [],
#         "name": {
#             "kind": "name",
#             "value": f"{field_name}"
#         },
#         "arguments": arguments,
#         "selection_set": {
#             "kind": "selection_set",
#             "selections": selections
#         }
#     }
#     query_document = {
#         "kind": "document",
#         "definitions": [
#             {
#                 "kind": "operation_definition",
#                 "operation": OperationType.QUERY,
#                 "name": {"kind": "name", "value": f"Read{field_name}"},
#                 "variable_definitions": variables,
#                 "selection_set": {
#                     "kind": "selection_set",
#                     "selections": [root_field]
#                 }
#             },
#             # ast_scalars_fragment,
#             # ast_objects_fragment
#             # případně fragmenty pro vektory, pokud je vytvoříš
#         ]
#     }

#     # query_document = {
#     #     "kind": "document",
#     #     "definitions": [
#     #         {
#     #             "kind": "operation_definition",
#     #             "name": {
#     #                 "kind": "name",
#     #                 "value": "GetUser"
#     #             },
#     #             "directives": [],
#     #             "variable_definitions": [
#     #                 {
#     #                     "kind": "variable_definition",
#     #                     "variable": {
#     #                         "kind": "variable",
#     #                         "name": {
#     #                             "kind": "name",
#     #                             "value": "id"
#     #                         }
#     #                     },
#     #                     "type": {
#     #                         "kind": "non_null_type",
#     #                         "type": {
#     #                             "kind": "named_type",
#     #                             "name": {
#     #                                 "kind": "name",
#     #                                 "value": "ID"
#     #                             }
#     #                         }
#     #                     },
#     #                     # "default_value": null,
#     #                     "directives": []
#     #                 }
#     #             ],
#     #             "selection_set": {
#     #                 "kind": "selection_set",
#     #                 "selections": [
#     #                     {
#     #                         "kind": "field",
#     #                         "directives": [],
#     #                         # "alias": null,
#     #                         "name": {
#     #                             "kind": "name",
#     #                             "value": "user"
#     #                         },
#     #                         "arguments": [
#     #                             {
#     #                                 "kind": "argument",
#     #                                 "name": {
#     #                                     "kind": "name",
#     #                                     "value": "id"
#     #                                 },
#     #                                 "value": {
#     #                                     "kind": "variable",
#     #                                     "name": {
#     #                                         "kind": "name",
#     #                                         "value": "id"
#     #                                     }
#     #                                 }
#     #                             }
#     #                         ],
#     #                         "selection_set": {
#     #                             "kind": "selection_set",
#     #                             "selections": [
#     #                                 {
#     #                                     "kind": "field",
#     #                                     "directives": [],
#     #                                     # "alias": null,
#     #                                     "name": {
#     #                                         "kind": "name",
#     #                                         "value": "id"
#     #                                     },
#     #                                     "arguments": [],
#     #                                     # "selection_set": null
#     #                                 }
#     #                             ]
#     #                         }
#     #                     }
#     #                 ]
#     #             },
#     #             "operation": OperationType.QUERY
#     #         }
#     #     ]
#     # }
    
#     print(f"query_document = \n{json.dumps(query_document, default=str, indent=4)}")
#     result = fromDict(query_document)
#     return result
#     allowed_args = ['skip', 'limit', 'where']
#     for vector_field in iter_vectors_with_optional_params(ast_doc, field_name, field_return_type_ast):
#         # Pro každé vektorové pole vytvoříme Field s argumenty
#         print(f"vector_field {vector_field}")
#         args = []
#         field_basename = vector_field['name']['value']
#         for arg_name in allowed_args:
#             args.append({
#                 "kind": "argument",
#                 "name": {"kind": "name", "value": arg_name},
#                 "value": {
#                     "kind": "variable",
#                     "name": {"kind": "name", "value": f"{field_basename}_{arg_name}"}
#                 }
#             })

#         # Vytvoříme selectionSet, např. jen __typename + nebo můžeme vytvořit fragment (zjednoduším __typename)
#         selection_set = {
#             "kind": "selection_set",
#             "selections": [
#                 {
#                     "kind": "field",
#                     "name": {"kind": "name", "value": "__typename"}
#                 }
#             ]
#         }

#         selections.append({
#             "kind": "field",
#             "name": {"kind": "name", "value": field_basename},
#             "arguments": args,
#             "selectionSet": selection_set
#         })        

#     # Vytvoříme root field
#     root_field = {
#         "kind": "field",
#         "name": {"kind": "name", "value": field_name},
#         "selectionSet": {
#             "kind": "selection_set",
#             "selections": selections
#         }
#     }

#     # Celý query dokument
#     query_document = {
#         "kind": "document",
#         "definitions": [
#             {
#                 "kind": "operation_definition",
#                 "operation": "query",
#                 "name": {"kind": "name", "value": f"Read{field_name.capitalize()}"},
#                 "selectionSet": {
#                     "kind": "selection_set",
#                     "selections": [root_field]
#                 }
#             },
#             ast_scalars_fragment,
#             ast_objects_fragment
#             # případně fragmenty pro vektory, pokud je vytvoříš
#         ]
#     }
#     result = fromDict(query_document)
#     return result

from .query_helpers import buildQuery, buildMutation
def create_router_from_schema(schema: strawberry.schema.Schema) -> APIRouter:
    sdl = schema.as_str()
    directive_text = "directive @key(fields: String!) on OBJECT | INTERFACE"
    sdl = directive_text + "\n" + sdl
    ast = graphql.language.parse(sdl)
    router = APIRouter()

    # Najdeme Query typ
    query_type_def: Optional[ObjectTypeDefinitionNode] = None
    for defn in ast.definitions:
        if isinstance(defn, ObjectTypeDefinitionNode) and defn.name.value == "Query":
            query_type_def = defn
            break
    if query_type_def is None:
        raise ValueError("No Query type found in SDL")

    # Sestavíme mapu typů pro rychlý lookup definice typu podle jména
    type_map = {d.name.value: d for d in ast.definitions if isinstance(d, ObjectTypeDefinitionNode)}

    async def graphQLClient(query, variables={}, authorization=None):
        print(f"graphQLClient.authorization={authorization}")
        url = "http://localhost:8000/gql"  # nahraď URL tvým GraphQL endpointem
    
        headers = {
            "Content-Type": "application/json",
            "authorization": authorization  # například "Bearer <token>"
        }
        cookies = {
            "authorization": authorization  # například "Bearer <token>"
        }
        payload = {
            "query": query,
            "variables": json.loads(json.dumps(variables, default=str)) or {}
        }

        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                resp.raise_for_status()  # vyhodí chybu, pokud status není 200
                data = await resp.json()
                return data
            
    # Pro každé pole v Query přidáme endpoint podle výstupního typu
    for field in query_type_def.fields or []:
        out_type_name = unwrap_type(field.type).name.value
        if not out_type_name:
            continue

        # Najdeme definici výstupního typu
        out_type_def = type_map.get(out_type_name)
        if not out_type_def:
            continue
        # operation_id = f"{type_name}_ui_{type_name.lower()}_get"
        # print(f"ast: {ast}")
        builded_query = buildQuery(ast.to_dict(), field.name.value)
        # print(f"builded_query {field.name.value} => \n{json.dumps(builded_query, indent=4)}")
        builded_query_str = graphql.print_ast(builded_query)
        # print(f"builded_query {field.name.value} => \n{builded_query_str}")
        builded_query_str = explain_graphql_query(ast, builded_query_str)
        print(f"builded_query {field.name.value} => \n{builded_query_str}")
        # if builded_query:
        #     builded_query_str = graphql.print_ast(builded_query)
        #     print(f"builded_query {field.name.value} => \n{builded_query_str}")
        # query = ""
        # if "Page" in field.name.value:
        #     query = build_query_page(ast, field.name.value)
        #     query = explain_graphql_query(ast, query)
        # if "ById" in field.name.value:
        #     query = build_query_scalar(ast, field.name.value)
        #     query = explain_graphql_query(ast, query)
        query = builded_query_str
        def visualise_list(data: list):
            attributes = {}
            for row in data:
                # print(f"row = {row}")
                for key in row.keys():
                    # print(f"key = {key}")
                    attributes[key] = ""
            
            attributes_list = list(attributes.keys())
            attributes_list.append("link")
            # print(f"attributes_list: {attributes_list}")
            results = [
                visualise_dict(row, attributes_list, table_mode=True) for row in data
            ]
            headers = [f"<th>{attribute_name}</th>" for attribute_name in attributes_list]
            html = f'<table class="table"><tr>{" ".join(headers)}</tr>{" ".join(results)}</table>'
            # return ""
            return html
        
        def compute_dict(data: dict):
            result_dict = {}
            type_name = data.get("__typename", None)
            if type_name:
                type_name = type_name.lower()

            id = data.get("id", None)
            name = data.get("name", None) or id or "unknown"
            link = f'<a href="../{type_name}/{id}">{name}</a>' if type_name else f'{name}'

            result_dict["link"] = link
            for attribute_name, attribute_value in data.items():

                if attribute_name == "name":
                    attribute_value = link
                    
                if attribute_name == "id" and name == "unknown":
                    attribute_value = link
                    
                if isinstance(attribute_value, dict):
                    attribute_value = visualise_dict(attribute_value)
                elif isinstance(attribute_value, list):
                    attribute_value = visualise_list(attribute_value)
                    # attribute_value = f"{attribute_value}"
                result_dict[attribute_name] = attribute_value

            return result_dict
        
        def visualise_dict(data: dict, attrs=[], table_mode=False):
            result = ""
            if table_mode:
                result_dict = compute_dict(data)
                result += f'''<tr>'''
                for attribute_name in attrs:
                    attribute_value = result_dict[attribute_name]
                    result += f'''<td>{attribute_value}</td>'''
                result += f'''</tr>'''
                return result
            
            result_dict = compute_dict(data)
            result = ""
            for attribute_name in result_dict.keys():
                attribute_value = result_dict[attribute_name]
                result += f'''<div class="row">
                        <div class="col-2"><b>{attribute_name}</b></div>
                        <div class="col-10">{attribute_value}</div>
                    </div>'''
            return result

        async def handle_scalar(request: Request, id: uuid.UUID, out_type=out_type_def, query=query):
            jsondata = {}
            result = {}
            variables = {"id": id}
            if query:
                auth_cookie = request.cookies.get('authorization')
                jsondata = await graphQLClient(query=query, variables=variables, authorization=auth_cookie)
                data = jsondata.get("data", None)
                # assert data is not None, "got no data"
                if data:
                    # assert results is not None, "got no result"
                    result = next(iter(data.values()), None)
#             fields = out_type.fields or []
#             field_dict = {f.name.value: unwrap_type(field.type).name.value.lower() for f in fields}
                
#             visual = visualise_dict(result)

#             html = f"""
#             <html>
#                 <head>
#                 <title>{out_type.name.value} info</title>
#                   <meta charset="utf-8">
#   <meta name="viewport" content="width=device-width, initial-scale=1">
#   <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
#   <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
#                 </head>
#                 <body>
#                     <div class="container">
#                     <h1>Type: {out_type.name.value}</h1>     
#                     {visual}              
#                     <pre>{query}</pre>
#                     <pre>{json.dumps(result, indent=4)}</pre>
#                     </div>
#                 </body>
#             </html>
#             """
            html = HTML(query, result)
            
            return HTMLResponse(content=html)

        # Vytvoříme handler pro endpoint
        async def handle_page(request: Request, out_type=out_type_def, query=query):
            jsondata = {}
            results = []
            if query:
                auth_cookie = request.cookies.get('authorization')
                jsondata = await graphQLClient(query=query, authorization=auth_cookie)
                data = jsondata.get("data", None)
                # assert data is not None, "got no data"
                if data:
                    # assert results is not None, "got no result"
                    results = next(iter(data.values()), None)
            resultstr = [f"<tr><td><a href='./{result['id']}'>{result['name']}</a></td><td>{result['name']}</td></tr>" for result in results]
            jsonstr = json.dumps(jsondata, indent=4)
            # Sestavíme jednoduchý HTML s info o poli typu
            fields = out_type.fields or []
            field_list = "".join(f"<li>{f.name.value}</li>" for f in fields)
            html = f"""
            <html>
                <head>
                <title>{out_type.name.value} Page</title>
                  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
                </head>
                <body>
                    <h1>Type: {out_type.name.value}</h1>
                    
                    <table class="table">
                        {resultstr}
                    </table>
                    <pre>{query}<pre>
                    <pre>{jsonstr}<pre>
                    <pre>{json.dumps(results, indent=4)}<pre>
                    <ul>{field_list}</ul>
                </body>
            </html>
            """
            # html = HTML(query, data)
            return HTMLResponse(content=html)

        # Endpoint pojmenujeme podle jména výstupního typu (malá písmena)
        
        if "Page" in field.name.value:
            path = f"/{out_type_name.lower()}/_"
            router.add_api_route(path, handle_page, methods=["GET"], name=out_type_name)
            
        if "ById" in field.name.value:
            path = f"/{out_type_name.lower()}/{{id}}"
            router.add_api_route(path, handle_scalar, methods=["GET"], name=out_type_name)

    builded_query = buildMutation(ast.to_dict(), "userInsert")
    print(f"builded_query {field.name.value} => \n{json.dumps(builded_query, default=str, indent=4)}")
    builded_query_str = graphql.print_ast(builded_query)
    # print(f"builded_query {field.name.value} => \n{builded_query_str}")
    builded_query_str = explain_graphql_query(ast, builded_query_str)
    print(f"builded_query {field.name.value} => \n{builded_query_str}")
    return router
