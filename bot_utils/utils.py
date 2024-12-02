import re
import json

def parse_function_call(input_string):
    pattern = r'<function=(\w+)>(.*?)</function>'
    match = re.match(pattern, input_string)
    
    if match:
        function_name = match.group(1)
        
        try:
            params_str = match.group(2).strip().strip('"')
            params = json.loads(params_str)
            return {
                "function_name":function_name,
                "function_args":params
            }
            # return function_name, params
        except json.JSONDecodeError:
            return function_name, match.group(2).strip()
    
    return None, None

def clean_and_parse_json(json_string):
    
    try:
        cleaned_string = json_string.replace('\n', '').replace('\\n', '\n')
        
        parsed_dict = json.loads(cleaned_string)
        
        return parsed_dict
    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f'RAW RESPONSE: \n',json_string)
        return {}
# print(parse_function_call('<function=query_distinct_value_of_field>{"field_name": "Filename"}"</function>'))