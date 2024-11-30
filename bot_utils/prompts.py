
# SYSTEM_PROMPT =  """
#     You are a helpful assistant that can access external functions. 
#     The responses from these function calls will be appended to this dialogue. 
#     Please provide responses based on the information from these function calls and send it to tool_calls.
    
#     User will ask you for information in pdf files.
#     The relevant information for the question can be found in text, table, or picture. 
#     The table/picture which titled relevant to user question can provide details about the information they want to know.
#     If you say 'this information can be found in table/picture on page ...', you have to specify WHAT PAGE of WHAT FILENAME (.pdf).
#     The function will return you queries (which are likely to contain the information user need, link to table, link to pictures,...). Your job is extract relevant and tell user about it.
    
#     ### FORMAT OF ANSWER
#     Alway response in this format of json for every user question, do not ADD ANYTHING outside the json.
#     ```
#     {
#         "response":"...", (this is your main response for user question.)
#         "link":"..." (link_to_table or link_to_picture that likely gives user information. You have to ENSURE THE INFORMATION USER NEED IS IN THIS TABLE/PICTURE VIA IT'S DESCRIPTION, ELSE JUST LEAVE THIS BLANK LIKE ''.)
#     }
#     ```
    
#     ### WARNING
#     If the field `response` already have information and not like `your information is in table/picture below`, then just leave `link` blank.
#     Don't tell users you will do function calling.
#     Don't include tool_calls.append(...) or anything about tool_call in your response
#     """
# # pass
SYSTEM_PROMPT = """
        You are a specialized PDF information extraction assistant with the following key responsibilities:

        ### Core Objectives
        - Accurately extract and synthesize information from PDF documents in response to user queries
        - Precisely locate and reference specific pages, tables, or images containing relevant information
        - Provide clear, concise, and structured responses

        ### Response Guidelines
        1. Always respond in a strict JSON format with two key fields:
        ```
        {
            "response": "Detailed, informative answer to the user's query",
            "link": "Direct linke to table or picture (if provided in query)"
        }
        ```
        2. Response Requirements:


        - `response` must directly address the user's question
        - If information is found in a specific table or image, explicitly mention:

            - The exact page number
            - The filename
            - A clear description of where the information is located


        - If the full answer requires referencing a table/image, structure the response as:
        "Detailed information can be found in [description] on page [X] of [filename]."


        3. Link Guidelines:
        - Link can be "" if no link_to_table/link_to_picture provided in the query.
        - Ensure the resource linked genuinely contains the table/picture.

        ### Critical Constraints

        - Never discuss the mechanism of function calls or tool interactions
        - Do not include any text outside the JSON structure
        - Prioritize accuracy and specificity in information extraction
        - If information cannot be definitively found, acknowledge this within the response

        ### Handling Complex Queries

        - Break down complex queries into retrievable components
        - Cross-reference multiple document sections if needed
        - Provide context and source details for extracted information
"""
TOOLS = [
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "query_overall",
    #         "description": "Function to get query result from chroma database from your query text. No well_name and report_type needed (because you do not know about them).",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "query_text": {
    #                     "type": "string",
    #                     "description": "Your main query to get information. You should pass the entire question here.",
    #                 },
    #             },
    #             "required": ["query_text"],
    #         },
    #     }, 
    # },
    {
        "type": "function",
        "function": {
            "name": "query_distinct_value_of_field",
            "description": "Function to get query every distinct value of a field in the collection",
            "parameters": {
                "type": "object",
                "properties": {
                    "field_name": {
                        "type": "string",
                        # "description": "The name of the field you want to get distinct value",
                        "enum":["Filename","Report_type","Well_name","Type","Link_to_table","Link_to_picture"]
                    },
                },
                "required": ["field_name"],
            },
        }, 
    },
    {
        "type": "function",
        "function": {
            "name": "get_group_of_biostratigraphy",
            "description": "Function to get distinct of values of fields (for example files and wells) which is a kind of biostratigraphy report",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_by": {
                        "type": "string",
                        # "description": "The name of the field you want to get distinct value",
                        "enum":["Filename","Well_name"]
                    },
                },
                "required": [],
            },
        }, 
    },
    {
        "type": "function",
        "function": {
            "name": "get_group_of_petropysical",
            "description": "Function to get distinct of values of fields (for example files and wells) which is a kind of petrophysical report",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_by": {
                        "type": "string",
                        # "description": "The name of the field you want to get distinct value",
                        "enum":["Filename","Well_name"]
                    },
                },
                "required": [],
            },
        }, 
    },
    {
        "type": "function",
        "function": {
            "name": "summary_of_petrophysical_result",
            "description": "Function to get summary of petrophysical result of a well.",
            "parameters": {
                "type": "object",
                "properties": {
                    "well_name": {
                        "type": "string",
                        # "description": "The name of the field you want to get distinct value",
                        "enum":["15/9-F-1"]
                    },
                },
                "required": [],
            },
        }, 
    },
    {
        "type": "function",
        "function": {
            "name": "summary_hole_record",
            "description": "Function to get hole record of a well.",
            "parameters": {
                "type": "object",
                "properties": {
                    "well_name": {
                        "type": "string",
                        # "description": "The name of the field you want to get distinct value",
                        "enum":["15/9-F-12"]
                    },
                },
                "required": [],
            },
        }, 
    },
    {
        "type": "function",
        "function": {
            "name": "final_well_report_list_bha",
            "description": "Function to get information of BHA.",
            "parameters": {
                "type": "object",
                "properties": {
                    "well_name": {
                        "type": "string",
                        # "description": "The name of the field you want to get distinct value",
                        "enum":["15/9-F-4"]
                    },
                },
                "required": [],
            },
        }, 
    },
    {
        "type": "function",
        "function": {
            "name": "well_report_get_main_result_of_test_of_well",
            "description": "Function to get main result of a test performing on a well",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_no":{
                        "type":"string",
                        "enum":["1","2A","2B"]
                    },
                    "well_name": {
                        "type": "string",
                        # "description": "The name of the field you want to get distinct value",
                        "enum":["15/9-19A"]
                    },
                },
                "required": [],
            },
        }, 
    },
    {
        "type": "function",
        "function": {
            "name": "get_information_in_biostratigraphy",
            "description": "Function to information of a keyword in biostratigraphy report about a well. The keyword can be `Introduction`, `Abstract`, some name,... that a report can contain.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword":{
                        "type":"string",
                        "description":"keyword or information that user want to know about"
                        # "enum":["1","2A","2B"]
                    },
                    "well_name": {
                        "type": "string",
                        # "description": "The name of the field you want to get distinct value",
                        "enum":["15/9-F-1","15/9-F-10"]
                    },
                },
                "required": [],
            },
        }, 
    },
    
]






