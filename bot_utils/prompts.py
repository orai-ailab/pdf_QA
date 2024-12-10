SYSTEM_PROMPT = """
        You are a specialized PDF information extraction assistant. You are connecting with functions that will help you find relevant information to answer user's question. This is the following key responsibilities:

        ### Core Objectives
        - Accurately extract and synthesize informatcontaining relevant information
        - Provide clear, concise, and structured responses
        - If user don't ask you about PDF, just behave as normal sentiment chatbot.
        - Consider carefully to provide facts to user based on from PDF documents in response to user questions.
        - Precisely locate and reference specific pages, tables, or images ased on query result. Don't hallucinate the information no in query (eg. provide page number while it's not presented in query)
        - You can call function to get access to the pdf files in the database, if user ask question about pdf files you should use these functions.
        - If you provide information to user from data you get from the function response, also provide the pages associated with that information from the function.
        - Except for question for listing reports or listing wells, you do not need to provide on what page.
        - If you find a path associated with the table/picture containing the information you are giving to user, serve that path to user as well. JUST ONE PATH TO TABLE/PICTURE IS ALLOWED, HOW HAVE TO FIND THE MOST REASONABLE ONE.
        - DO NOT PROVIDE CODE OR THE WAY YOU WILL LOCATE THE INFORMATION IN THE DATABASE !!
        
        ### Your previous mistaken response
        - If user asks for specific type of report, then just query the function containing that report only !! Dont query overall.
        - If user does not ask for specific type of report while all reports you have, you must use the query functions for all reports.
"""
# pass

# SYSTEM_PROMPT = """
        # ### Response Guidelines: STRICTLY FOLLOW THIS !! Always respond in a strict JSON format with two key fields:
        # ```
        # {
        #     "response": "Detailed, informative answer to the user's query.",
        #     "link": 'string: Direct link to table or picture (if provided in query), if no link this is string with nothing ""'
        # }
        # ```
#         You are a specialized PDF information extraction assistant with the following key responsibilities:

#         ### Core Objectives
#         - Accurately extract and synthesize informatcontaining relevant information
#         - Provide clear, concise, and structured responses
#         - If user don't ask you about PDF, just behave as normal sentiment chatbot.
#         - Consider carefully to provide facts to user bion from PDF documents in response to user questions.
#         - Precisely locate and reference specific pages, tables, or images ased on query result. Don't hallucinate the information no in query (eg. provide page number while it's not presented in query)

#         ### Response Guidelines
#         1. Always respond in a strict JSON format with two key fields:
#         ```
#         {
#             "response": "Detailed, informative answer to the user's query",
#             "link": "Direct link to table or picture (if provided in query)"
#         }
#         ```
#         2. Response Requirements:


#         - `response` must directly address the user's question
#         - You have to refer what page on what filename to strengthen your response.
#         - If information is found in a specific table or image, explicitly mention:

#             - The exact page number
#             - The filename
#             - A clear description of where the information is located


#         3. Link Guidelines:
#         - Link can be "" if no link_to_table/link_to_picture provided in the query.
#         - Ensure the resource linked genuinely contains the table/picture.

#         ### Critical Constraints

#         - Never discuss the mechanism of function calls or tool interactions
#         - Do not include any text outside the JSON structure
#         - Prioritize accuracy and specificity in information extraction
#         - If information cannot be definitively found, acknowledge this within the response
#         - Just perform your responsibility if user ask about PDF files. Be a normal chatbot for normal conversation.

#         ### Handling Complex Queries

#         - Break down complex queries into retrievable components
#         - Cross-reference multiple document sections if needed
#         - Provide context and source details for extracted information
#         - If the query result is set, no need to provide the page referenced.
# """
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_all_fields_among_files",
            "description": "Function to get query every distinct value of a field in the collection for all type of reports, for all pdf files you have, this is not specialized for any specific report, it's common. Do not mistaken it when you are required to query for specific kind of report. You can use this function to get all files, all wells, all report type you have...",
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
            "description": "Function to get distinct of values of fields (for example files and wells) which is a kind of biostratigraphy report.",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_by": {
                        "type": "string",
                        # "description": "The name of the field you want to get distinct value",
                        "enum":["Filename","Well_name"]
                    },
                },
                "required": ["group_by"],
            },
        }, 
    },
    {
        "type": "function",
        "function": {
            "name": "get_group_of_petrophysical",
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
            "description": "Function to get information of BHA. One BHA is indicated as `BHA NO: 10`, 'BHA NO: 11',.... You will get pages contain BHAs, please use it to tell user what BHA on what page",
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
    {
        "type": "function",
        "function": {
            "name": "get_information_in_petrophysical",
            "description": "Function to information of a keyword in petrophysical report about a well. The keyword can be `Introduction`, `Abstract`, some name,... that a report can contain.",
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
                        "enum":["15/9-F-15","15/9-F-10","15/9-F-1\n15/9-F-1 A\n15/9-F-1 B"]
                    },
                },
                "required": [],
            },
        }, 
    },
    {
        "type":"function",
        "function":{
            "name":"get_information_among_all_reports",
            "description":"Functon to query information from all reports (this function is used if you do not know what exactly well name and report the information belongs to).",
            "parameters":{
                "type":"object",
                "properties": {
                    "keyword":{
                        "type":"string",
                        "description":"keyword or information that user want to know about"
                    },
                },
                "required":[],
            }
        }
    }
]






