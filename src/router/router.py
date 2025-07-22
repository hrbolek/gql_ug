import strawberry
import aiohttp
import graphql
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from graphql.language.ast import DocumentNode, ObjectTypeDefinitionNode, FieldDefinitionNode, NamedTypeNode, NonNullTypeNode, ListTypeNode
from typing import List, Optional

from uoishelpers.cmds.utils_sdl_2 import build_query_page, build_query_scalar, explain_graphql_query
def unwrap_type(type_node):
    while isinstance(type_node, (NonNullTypeNode, ListTypeNode)):
        type_node = type_node.type
    if isinstance(type_node, NamedTypeNode):
        return type_node
    return None

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

        payload = {
            "query": query,
            "variables": variables or {}
        }

        async with aiohttp.ClientSession() as session:
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

        query = ""
        if "Page" in field.name.value:
            query = build_query_page(ast, field.name.value)
            query = explain_graphql_query(ast, query)
        if "ById" in field.name.value:
            query = build_query_scalar(ast, field.name.value)
            query = explain_graphql_query(ast, query)

        # Vytvoříme handler pro endpoint
        async def handler(request: Request, out_type=out_type_def, query=query):
            jsondata = {}
            if query:
                auth_cookie = request.cookies.get('authorization')
                jsondata = await graphQLClient(query=query, authorization=auth_cookie)
                

            # Sestavíme jednoduchý HTML s info o poli typu
            fields = out_type.fields or []
            field_list = "".join(f"<li>{f.name.value}</li>" for f in fields)
            html = f"""
            <html>
                <head><title>{out_type.name.value} info</title></head>
                <body>
                    <h1>Type: {out_type.name.value}</h1>
                    <ul>{field_list}</ul>
                    <pre>{query}<pre>
                    <pre>{jsondata}<pre>
                </body>
            </html>
            """
            return HTMLResponse(content=html)

        # Endpoint pojmenujeme podle jména výstupního typu (malá písmena)
        path = f"/{out_type_name.lower()}"
        router.add_api_route(path, handler, methods=["GET"], name=out_type_name)

    return router
