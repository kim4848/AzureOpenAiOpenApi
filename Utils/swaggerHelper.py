import requests
import json
import yaml
import jsonref
from interfaces import FunctionDefinition,Tool

def _openapi_to_tools(openapi_spec)->list[Tool]:
    functions = []  # List[FunctionDefinition]
    functions2 = []

    for path, methods in openapi_spec["paths"].items():
        for method, spec_with_ref in methods.items():
            # 1. Resolve JSON references.
            spec = jsonref.replace_refs(spec_with_ref)

            # 2. Extract a name for the functions.
            function_name = spec.get("operationId")

            # 3. Extract a description and parameters.
            desc = spec.get("description") or spec.get("summary", "")

            schema = {"type": "object", "properties": {}}

            req_body = (
                spec.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema")
            )
            if req_body:
                schema["properties"]["requestBody"] = req_body

            params = spec.get("parameters", [])
            if params:
                param_properties = {
                    param["name"]: param["schema"]
                    for param in params
                    if "schema" in param
                }
                schema["properties"]= {
                    
                    **param_properties,
                }

            functions.append(
                {"type": "function", "function": {"name": function_name, "description": desc, "parameters": schema,"endpoint":path,"method":method}}
            )
            f=FunctionDefinition(name=function_name, description=desc, parameters=schema, endpoint=path, method=method)
            
            t=Tool( function=f)
            functions2.append(t)

    
    return functions


def _read_swagger_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        try:
            # Try to parse as JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to parse as YAML
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                print(f"Failed to parse content as YAML: {e}")
    else:
        print(f"Failed to fetch content from URL. Status code: {response.status_code}")

def GetFunctions(url)->list[Tool]:
    swagger_content = _read_swagger_from_url(url)
   
    if swagger_content:
        functions=_openapi_to_tools(swagger_content)
     
        return functions  