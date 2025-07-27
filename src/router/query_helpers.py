import json

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
    ListValueNode,
    InlineFragmentNode,
    ObjectValueNode,
    ObjectFieldNode
)

clsmap = {
    "document": DocumentNode,
    "operation_definition": OperationDefinitionNode,
    "field": FieldNode,
    "selection_set": SelectionSetNode,
    "name": NameNode,
    "argument": ArgumentNode,
    "variable": VariableNode,
    "fragment_definition": FragmentDefinitionNode,
    "named_type": NamedTypeNode,
    "name": NameNode,
    "variable_definition": VariableDefinitionNode,
    "variable": VariableNode,
    "non_null_type": NonNullTypeNode,
    "string_value": StringValueNode,
    "int_value": IntValueNode,
    "null_value": NullValueNode,
    "list_type": ListTypeNode,
    "inline_fragment": InlineFragmentNode,
    "list_value": ListValueNode,
    "object_value": ObjectValueNode,
    "object_field": ObjectFieldNode
    # další typy AST uzlů
}
def fromDict(node: dict):
    kind = node.get("kind", None)
    assert kind is not None, f"found node without kind {node}"
    cls = clsmap[kind]
    params = {}
    for key, value in node.items():
        if isinstance(value, list):
            params[key] = [fromDict(item) for item in value]
        elif isinstance(value, dict):
            params[key] = fromDict(value)
        else:
            params[key] = value
    return cls(**params)

def unwrap_type_ast(type_node):
    kind = type_node['kind']
    # print(f"unwrap_type_ast({type_node})[{kind}] * {kind == 'named_type'}")
    
    if kind == 'named_type':
        # print(f"unwrap_type_ast.return {type_node['name']['value']}")
        return type_node['name']['value']
    elif kind in ('non_null_type', 'list_type'):
        return unwrap_type_ast(type_node['type'])
    else:
        return None
    
def find_field(fields, name):
    return next((f for f in fields if f['name']['value'] == name), None)

def find_return_type(ast_doc, field_ast, field_name):
    """
    - ast_doc: celý AST dokument
    - field_ast: AST typu (např. objekt typu Query nebo jiný objekt),
                ve kterém hledáme pole `field_name`
    - field_name: název pole, jehož návratový typ chceme najít

    Vrací jméno návratového typu pole nebo None
    """
    if not field_ast or 'fields' not in field_ast:
        # print(f"find_return_type {field_name} :(")
        return None

    fields = field_ast['fields']
    # print(f"find_return_type.fields {field_name}@{fields}")
    for f in fields:
        if f.get('name', {}).get('value') == field_name:
            # print(f"found {f}")
            # máme pole, rozbalíme typ
            return unwrap_type_ast(f['type'])

    # Pokud pole nenajdeme v daném typu, můžeme zkusit vyhledat typ v ast_doc a rekurzivně pokračovat,
    # ale to záleží na tom, jak chceš hluboko hledat. Pro jednoduchost vrátíme None.
    return None

def is_scalar_type(ast_doc, type_ast):
    # Rozbalíme na základní typ
    type_name = unwrap_type_ast(type_ast)
    if not type_name:
        return False

    # Najdeme definici typu v ast_doc
    for defn in ast_doc.get('definitions', []):
        if defn.get('kind') in ('scalar_type_definition', 'scalar_type_extension'):
            if defn.get('name', {}).get('value') == type_name:
                return True

    # Některé běžné built-in scalars (pokud nejsou v ast_doc explicitně)
    builtin_scalars = {"Int", "Float", "String", "Boolean", "ID"}
    if type_name in builtin_scalars:
        return True

    return False

def is_object_type(ast_doc, type_ast):
# Rozbalíme typ na základní jméno
    type_name = unwrap_type_ast(type_ast)
    if not type_name:
        return False

    # Hledáme v definicích typů AST ObjectTypeDefinition nebo ObjectTypeExtension
    for defn in ast_doc.get('definitions', []):
        if defn.get('kind') in ('ObjectTypeDefinition', 'ObjectTypeExtension'):
            if defn.get('name', {}).get('value') == type_name:
                return True

    return False

def is_object_type(ast_doc, type_ast):
    type_name = unwrap_type_ast(type_ast)
    if not type_name:
        return False
    for defn in ast_doc.get('definitions', []):
        if defn.get('kind') in ('object_type_definition', 'object_type_extension'):
            if defn.get('name', {}).get('value') == type_name:
                return True
    return False

def is_list_of_objects(ast_doc, type_ast):
    """
    Rozhodne, jestli type_ast je List[Object!], tj.:
    - type_ast.kind == 'ListType'
    - jeho typ je NonNullType
    - a ten NonNullType obsahuje NamedType odpovídající Object typu
    """

    if type_ast['kind'] != 'non_null_type':
        return False
    type_ast = type_ast['type']
    if type_ast['kind'] != 'list_type':
        return False

    # Vezmeme typ prvků listu
    inner_type = type_ast['type']

    # Musí být NonNullType
    if inner_type['kind'] != 'non_null_type':
        return False

    # A NonNullType musí mít NamedType, který je Object typ
    named_type = inner_type['type']
    if named_type['kind'] != 'named_type':
        return False

    type_name = named_type['name']['value']

    # Zkontrolujeme, jestli typ je Object
    for defn in ast_doc.get('definitions', []):
        if defn.get('kind') in ('object_type_definition', 'object_type_extension'):
            if defn.get('name', {}).get('value') == type_name:
                return True

    return False

def has_only_optional_params(field_ast):
    # Zkontroluje, jestli field nemá povinné parametry (non-null bez defaultu)
    params = field_ast.get('arguments', [])
    for p in params:
        # předpokládáme, že non-null typ je typ s kind == 'NonNullType' a nemá default
        if p.get('type', {}).get('kind') == 'non_null_type' and 'defaultValue' not in p:
            return False
    return True
    
def find_type_def(ast_doc, type_name):
    definitions = ast_doc.get('definitions', [])
    result = next(filter(lambda dfn: dfn.get("kind", None) == "object_type_definition" and dfn["name"]["value"]==type_name, definitions), None)
    return result

def find_input_type_def(ast_doc, type_name):
    definitions = ast_doc.get('definitions', [])
    result = next(filter(lambda dfn: dfn.get("kind", None) == "input_object_type_definition" and dfn["name"]["value"]==type_name, definitions), None)
    return result

def find_union_def(ast_doc, type_name):
    definitions = ast_doc.get('definitions', [])
    result = next(filter(lambda dfn: dfn.get("kind", None) == "union_type_definition" and dfn["name"]["value"]==type_name, definitions), None)
    return result

def create_fragment_for_scalars(ast_doc, field_name, field_return_type_name):
    # najde jen ty fieldy, ktere vraci typy oznacene jako skalary
    # ignoruje fieldy, ktere maji povinne parametry

    type_def = find_type_def(ast_doc, field_return_type_name)
    # Najdeme definici typu podle jména

    if not type_def:
        # Typ nenalezen, prázdný fragment
        return {
            "kind": "fragment_definition",
            "name": {"kind": "name", "value": f"{field_return_type_name}LinkFragment"},
            "type_condition": {"kind": "named_type", "name": {"kind": "name", "value": field_return_type_name}},
            "selection_set": {"kind": "selection_set", "selections": [
                {
                    "kind": "field",
                    "name": {"kind": "name", "value": "__typename"}
                }                    
            ]}
        }

    fragment_fields = [{
        "kind": "field",
        "name": {"kind": "name", "value": "__typename"}
    }]

    for field in type_def.get('fields', []):
        if is_scalar_type(ast_doc, field['type']) and has_only_optional_params(field):
            fragment_fields.append({
                "kind": "field",
                "name": field['name']
            })

    return {
        "kind": "fragment_definition",
        "name": {"kind": "name", "value": f"{field_return_type_name}LinkFragment"},
        "type_condition": {"kind": "named_type", "name": {"kind": "name", "value": field_return_type_name}},
        "selection_set": {
            "kind": "selection_set",
            "selections": fragment_fields
        }
    }


def create_fragment_for_objects(ast_doc, field_name, field_return_type_name):
    # najde jen ty fieldy, ktere vraci typy oznacene jako Object
    # ignoruje fieldy, ktere maji povinne parametry
    # vystup je jako ast
    # Rozbalíme typ na NamedType AST uzel

    type_def = find_type_def(ast_doc, field_return_type_name)

    if not type_def:
        # Typ nenalezen, prázdný fragment
        return {
            "kind": "fragment_definition",
            "name": {"kind": "name", "value": f"{field_return_type_name}MediumFragment"},
            "type_condition": {"kind": "named_type", "name": {"kind": "name", "value": field_return_type_name}},
            "selection_set": {"kind": "selection_set", "selections": [
                {
                    "kind": "field",
                    "name": {"kind": "name", "value": "__typename"}
                }
            ]}
        }

    fragment_fields = [{
        "kind": "field",
        "name": {"kind": "name", "value": "__typename"}
    }]
    fragment_fields.extend(
        build_selection_set_ext(ast_doc, field_return_type_name)
    )
    # for field in type_def.get('fields', []):
    #     if is_object_type(ast_doc, field['type']) and has_only_optional_params(field):
    #         fragment_fields.append({
    #             "kind": "field",
    #             "name": field['name']
    #         })

    return {
        "kind": "fragment_definition",
        "name": {"kind": "name", "value": f"{field_return_type_name}MediumFragment"},
        "type_condition": {"kind": "named_type", "name": {"kind": "name", "value": field_return_type_name}},
        "selection_set": {
            "kind": "selection_set",
            "selections": fragment_fields
        }
    }

def iter_vectors_with_optional_params(ast_doc, field_name, field_return_type_name):
    # Rozbalíme typ na NamedType AST uzel
    type_def = find_type_def(ast_doc, field_return_type_name)
    # allowed_params = {"skip", "limit", "where"}

    for field in type_def.get('fields', []):
        print(f"iter_vectors_with_optional_params.{field_return_type_name} => {field}")
        if is_list_of_objects(ast_doc, field['type']) and has_only_optional_params(field):
            defn = {
                "kind": "field",
                "name": field['name']
            }    
            yield defn

def build_selection_set(ast_doc, field_return_type_name):
    type_def = find_type_def(ast_doc, field_return_type_name)
    selections = [{
        "kind": "field",
        "name": {"kind": "name", "value": "__typename"}
    }]
    for field in type_def.get('fields', []):
        field_type = field["type"]
        field_type_name = unwrap_type_ast(field_type)
        # field_type_name = field["type"]["name"]["value"]
        field_type = find_type_def(ast_doc, field_type_name)

        arguments = field["arguments"]
        mandatory_arguments = [
            argument 
            for argument in arguments 
            if is_mandatory_argument(argument)
        ]            
        if len(mandatory_arguments) != 0:
            continue
        if field_type is None:
            selections.append(
                {
                    "kind": "field",
                    "name": field['name']
                }
            )
        continue
        # selection = {
        #     "kind": "field",
        #     "name": {
        #         "kind": "name",
        #         "value": f'{field["name"]["value"]}'
        #     },
        #     "selection_set": {
        #         "kind": "selection_set",
        #         "selections": [
        #             {
        #                 "kind": "field",
        #                 "name": {"kind": "name", "value": "__typename"}
        #             }
        #         ]
        #     }
        # }
        # selections.append(selection)
    return selections

def is_non_null_type(type_node):
    # Vrací True, pokud je top-level typ NonNullType (i když je zabalený v listu)
    kind = type_node.get("kind")
    if kind == "non_null_type":
        return True
    elif kind == "list_type":
        # pokud je list_type, zkus zkontrolovat jeho typ rekurzivně
        return is_non_null_type(type_node.get("type", {}))
    else:
        return False    
    
def is_mandatory_argument(arg):
    # Je argument povinný?
    # Povinný = top-level non_null_type + default_value není definováno nebo je None / null_value

    default_value = arg.get('default_value')
    # print(f"default_value={default_value}")
    if default_value is None:
        return True
    return False
    # is_non_null = is_non_null_type(arg.get('type', {}))

    # has_default = default_value is not None and not (
    #     isinstance(default_value, dict) and default_value.get('kind') == 'null_value'
    # )

    # return is_non_null and not has_default        
    
def build_selection_set_ext(ast_doc, field_return_type_name):
    type_def = find_type_def(ast_doc, field_return_type_name)
    selections = []
    for field in type_def.get('fields', []):
        field_name = field["name"]["value"]
        field_type = field["type"]
        field_type_name = unwrap_type_ast(field_type)
        # field_type_name = field["type"]["name"]["value"]
        arguments = field["arguments"]
        mandatory_arguments = [
            argument 
            for argument in arguments 
            if is_mandatory_argument(argument)
        ]

        field_type = find_type_def(ast_doc, field_type_name)
        if field_type is None:
            
            if not mandatory_arguments:
                selections.append(
                    {
                        "kind": "field",
                        "name": field['name']
                    }
                )
            continue
        # print(f"build_selection_set_ext.mandatory_arguments@{field['name']['value']}={mandatory_arguments}\narguments\n\t{arguments}")
        
        if mandatory_arguments:
            selection = {
                "kind": "field",
                "name": {
                    "kind": "name",
                    "value": f'{field["name"]["value"]}'
                },
                "selection_set": {
                    "kind": "selection_set",
                    "selections": [
                        {
                            "kind": "field",
                            "name": {"kind": "name", "value": "__typename"}
                        }
                    ]
                }
            }
        else:
            selection = {
                "kind": "field",
                "name": {
                    "kind": "name",
                    "value": f'{field["name"]["value"]}'
                },
                "selection_set": {
                    "kind": "selection_set",
                    "selections": build_selection_set(ast_doc, field_type_name)
                }
            }
        selections.append(selection)
    return selections

def typename_already_present(selections):
    return any(sel['kind'] == 'field' and sel['name']['value'] == '__typename' for sel in selections)


def buildQuery(ast, field_name):
    operation_def = None
    # print(f"field_name: {field_name}")
    definitions = ast.get('definitions', [])
    schema_definition = next(filter(lambda dfn: dfn.get("kind", None) == "schema_definition", definitions), None) 
    # print(f"schema_definition: {schema_definition}")
    query_type = next(filter(lambda dfn: dfn.get("operation") == "query", schema_definition["operation_types"]), None)
    query_type_name = query_type["type"]["name"]["value"]
    # print(f"definitions: {definitions}")
    query_type_def = next(filter(lambda dfn: dfn.get("kind", None) == "object_type_definition" and dfn["name"]["value"]==query_type_name, definitions), None)
    # print(f"query_type_def: {query_type_def}")
    operation_def = query_type_def
    # for defn in definitions:
    #     if defn.get('kind') == 'OperationDefinition' and defn.get('operation') == 'query':
    #         operation_def = defn
    #         break
    # for defn in definitions:
    #     if defn.get('kind') == 'ObjectTypeDefinition' and defn.get('name', {}).get('value') == 'Query':
    #         operation_def = defn
    if operation_def is None:
        print(f"operation_def not found")
        return None  # žádná query operace v dokumentu
    

    # def build_read_query(ast_doc, field_name):
    ast_doc = ast
    field_return_type_ast = find_return_type(ast_doc, operation_def, field_name)
    if not field_return_type_ast:
        print(f"field_name {field_name} not found")
        return None
    else:
        print(f"field_name {field_name} found {field_return_type_ast}")

    ast_scalars_fragment = create_fragment_for_scalars(ast_doc, field_name, field_return_type_ast)
    # print(f"field_name {field_name} ast_scalars_fragment {ast_scalars_fragment}")
    ast_objects_fragment = create_fragment_for_objects(ast_doc, field_name, field_return_type_ast)
    # print(f"field_name {field_name} ast_objects_fragment {ast_objects_fragment}")

    selections = [] # selection_set
    # print(f"ast_scalars_fragment {list(ast_scalars_fragment.keys())}")
    ast_scalars_fragment_selections = ast_scalars_fragment["selection_set"]["selections"]
    ast_objects_fragment_selections = ast_objects_fragment["selection_set"]["selections"]
    selections = [*ast_scalars_fragment_selections, *ast_objects_fragment_selections]
    selectionsmap = {
        selection["name"]["value"]: selection for selection in selections
    }
    selections = list(selectionsmap.values())
    # selections = [
    #     {
    #         "kind": "field",
    #         "name": {"kind": "name", "value": "__typename"}
    #     }                    
    # ]
    field_def = next(filter(lambda field: field["name"]["value"]==field_name, query_type_def["fields"]), None) 
    field_def_arguments = field_def["arguments"]
    variables = [
        {
            "kind": "variable_definition",
            "description": argument.get("description", None),
            "variable": {
                "kind": "variable",
                "name": {
                    "kind": "name",
                    "value": argument["name"]["value"]
                }
            },
            "type": argument["type"],
            "default_value": argument["default_value"],
            "directives": []
        } for argument in field_def_arguments
    ]
    arguments = [
        {
            "kind": "argument",
            "name": {
                "kind": "name",
                "value": argument["name"]["value"]
            },
            "value": {
                "kind": "variable",
                "name": {
                    "kind": "name",
                    "value": argument["name"]["value"]
                }
            }
        } for argument in field_def_arguments
    ]
    root_field = {
        "kind": "field",
        "directives": [],
        "name": {
            "kind": "name",
            "value": f"{field_name}"
        },
        "arguments": arguments,
        "selection_set": {
            "kind": "selection_set",
            "selections": selections
        }
    }
    query_document = {
        "kind": "document",
        "definitions": [
            {
                "kind": "operation_definition",
                "operation": OperationType.QUERY,
                "name": {"kind": "name", "value": f"Read{field_name}"},
                "variable_definitions": variables,
                "selection_set": {
                    "kind": "selection_set",
                    "selections": [root_field]
                }
            },
            # ast_scalars_fragment,
            # ast_objects_fragment
            # případně fragmenty pro vektory, pokud je vytvoříš
        ]
    }
    
    print(f"query_document = \n{json.dumps(query_document, default=str, indent=4)}")
    result = fromDict(query_document)
    return result

def buildMutation(ast, field_name):
    operation_def = None
    # print(f"field_name: {field_name}")
    definitions = ast.get('definitions', [])
    schema_definition = next(filter(lambda dfn: dfn.get("kind", None) == "schema_definition", definitions), None) 
    # print(f"schema_definition: {schema_definition}")
    query_type = next(filter(lambda dfn: dfn.get("operation") == "mutation", schema_definition["operation_types"]), None)
    query_type_name = query_type["type"]["name"]["value"]
    # print(f"definitions: {definitions}")
    query_type_def = next(filter(lambda dfn: dfn.get("kind", None) == "object_type_definition" and dfn["name"]["value"]==query_type_name, definitions), None)
    print(f"query_type_def: {query_type_def}")
    operation_def = query_type_def
    # for defn in definitions:
    #     if defn.get('kind') == 'OperationDefinition' and defn.get('operation') == 'query':
    #         operation_def = defn
    #         break
    # for defn in definitions:
    #     if defn.get('kind') == 'ObjectTypeDefinition' and defn.get('name', {}).get('value') == 'Query':
    #         operation_def = defn
    if operation_def is None:
        print(f"operation_def not found")
        return None  # žádná query operace v dokumentu
    

    # def build_read_query(ast_doc, field_name):
    ast_doc = ast
    field_return_type_ast = find_return_type(ast_doc, operation_def, field_name)
    print(f"Mutation.{field_name} -> {field_return_type_ast}")
    field_return_type_ast = find_union_def(ast_doc, field_return_type_ast)
    print(f"Mutation.{field_name} -> {field_return_type_ast}")
    if not field_return_type_ast:
        print(f"field_name {field_name} not found")
        return None
    else:
        print(f"field_name {field_name} found {field_return_type_ast}")

    assert field_return_type_ast["kind"] == "union_type_definition", f"mutation must return union type\n{field_return_type_ast}"
    union_types = field_return_type_ast["types"]

    error_type_name = next((t["name"]["value"] for t in union_types if ("Error" in t["name"]["value"])), None)
    model_type_name = next((t["name"]["value"] for t in union_types if ("Error" not in t["name"]["value"])), None)


    # error_type = next((dfn for  dfn in definitions if (dfn["kind"] == "object_type_definition" and dfn["name"]["value"] == error_type_name)))
    # model_type = next((dfn for  dfn in definitions if (dfn["kind"] == "object_type_definition" and dfn["name"]["value"] == model_type_name)))

    error_ast_scalars_fragment = create_fragment_for_scalars(ast_doc, field_name, error_type_name)
    model_ast_scalars_fragment = create_fragment_for_scalars(ast_doc, field_name, model_type_name)
    # print(f"field_name {field_name} ast_scalars_fragment {ast_scalars_fragment}")
    model_ast_objects_fragment = create_fragment_for_objects(ast_doc, field_name, model_type_name)
    # print(f"field_name {field_name} ast_objects_fragment {ast_objects_fragment}")

    # print(f"ast_scalars_fragment {list(ast_scalars_fragment.keys())}")
    selectionsModel = [
        *model_ast_scalars_fragment["selection_set"]["selections"],
        *model_ast_objects_fragment["selection_set"]["selections"],
    ]
    selections = [
        {
            "kind": "inline_fragment",
            "directives": [],
            "type_condition": {
                "kind": "named_type",
                "name": {
                    "kind": "name",
                    "value": error_type_name
                }
            },
            "selection_set": error_ast_scalars_fragment["selection_set"]
        },
        {
            "kind": "inline_fragment",
            "directives": [],
            "type_condition": {
                "kind": "named_type",
                "name": {
                    "kind": "name",
                    "value": model_type_name
                }
            },
            "selection_set": {
                "kind": "selection_set",
                "selections": selectionsModel
            }
        },
    ]

    field_def = next(filter(lambda field: field["name"]["value"]==field_name, query_type_def["fields"]), None) 
    field_def_arguments = field_def["arguments"]
    first_argument = field_def_arguments[0]
    first_argument_type_name = unwrap_type_ast(first_argument["type"])
    first_argument_type = find_input_type_def(ast_doc, first_argument_type_name)
    variables = [
        {
            "kind": "variable_definition",
            "description": argument.get("description", None),
            "variable": {
                "kind": "variable",
                "name": {
                    "kind": "name",
                    "value": argument["name"]["value"]
                }
            },
            "type": argument["type"],
            "default_value": argument["default_value"],
            "directives": []
        } for argument in first_argument_type["fields"]
    ]
    arguments = [
        {
            "kind": "argument",
            "name": {
                "kind": "name",
                "value": "user"
            },
            "value": {
                "kind": "object_value",
                "fields": [
                    {
                        "kind": "object_field",
                        "name": {
                            "kind": "name",
                            "value": argument["name"]["value"]
                        },
                        "value": {
                            "kind": "variable",
                            "name": {
                                "kind": "name",
                                "value": argument["name"]["value"]
                            }
                        }
                    }
                    for argument in first_argument_type["fields"] 
                ]
            }
        }
    ]
    root_field = {
        "kind": "field",
        "directives": [],
        "name": {
            "kind": "name",
            "value": f"{field_name}"
        },
        "arguments": arguments,
        "selection_set": {
            "kind": "selection_set",
            "selections": selections
        }
    }

    mutation_document = {
        "kind": "document",
        "definitions": [
            {
                "kind": "operation_definition",
                "operation": OperationType.MUTATION,
                "name": {"kind": "name", "value": f"Read{field_name}"},
                "variable_definitions": variables,
                "selection_set": {
                    "kind": "selection_set",
                    "selections": [root_field]
                }
            },
        ]
    }
    result = fromDict(mutation_document)
    return result
