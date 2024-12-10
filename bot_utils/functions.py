from utils import query_pdfs,get_distinct_field

# calling function
def query_distinct_value_of_field_all_report(field_name):
    def eliminate_duplicates(file_list):
        normalized_files = {}
        
        for file in file_list:
            normalized_name = file.split('/')[-1]
            normalized_name = normalized_name.lower()
            
            if normalized_name not in normalized_files:
                normalized_files[normalized_name] = file
        
        return list(normalized_files.values())
    
    result = eliminate_duplicates(get_distinct_field(field=field_name,collection_name="PDF_test_6"))
    # print(result)
    return {
        "objects":result,
        "count":len(result)
    }
    # return result

def get_group_of_biostratigraphy(group_by="Well_name"):
    filter = {"Report_type":"Biostratigraphy"}
    result = query_pdfs(
        query="",  # No specific query string since we're only using a filter
        where=filter,
        n_results=100,  # Adjust to ensure you retrieve all relevant documents
        n_top=100,  # Retrieve up to 100 top results
        COLLECTION_NAME="PDF_test_6",
        group_by=group_by
    )
    return set(result)

def get_information_in_biostratigraphy(keyword="",well_name="15/9-F-1"):
    filter={"$and": [
        {"Report_type": 'Biostratigraphy'},
        {"Well_name": well_name},
        # {"Filename": "FWR_completion.pdf"},
        # {"Page_num":"5"}
    ]}
    result = query_pdfs(
        query=keyword,  # No specific query string since we're only using a filter
        where=filter,
        n_results=50,  # Adjust to ensure you retrieve all relevant documents
        n_top=10,  # Retrieve up to 100 top results
        STRICT_MODE=True,
        COLLECTION_NAME="PDF_test_6",
    )
    return (result)

def get_group_of_petrophysical(group_by="Filename"):
    filter = {"Report_type":"petropysical"}
    result = query_pdfs(
        query="",  # No specific query string since we're only using a filter
        where=filter,
        n_results=100,  # Adjust to ensure you retrieve all relevant documents
        n_top=100,  # Retrieve up to 100 top results
        COLLECTION_NAME="PDF_test_6",
        group_by=group_by
    )
    print(result)
    return set(result)

def get_information_in_petrophysical(well_name="",keyword=""):
    if well_name in ["15/9-F-15","15/9-F-10","15/9-F-1\n15/9-F-1 A\n15/9-F-1 B"]:
        filter={"$and": [
            {"Report_type": 'petropysical'},
            {"Well_name": well_name},
            # {"Filename": "FWR_completion.pdf"},
            # {"Page_num":"5"}
        ]}
    elif well_name:
        filter={"$and": [
            {"Report_type": 'petropysical'},
            {"Well_name": "15/9-F-1\n15/9-F-1 A\n15/9-F-1 B"},
            # {"Filename": "FWR_completion.pdf"},
            # {"Page_num":"5"}
        ]}
    else:
        filter = {"Report_type":"petropysical"}
    result = query_pdfs(
        
        query=keyword,  
        where=filter,
        n_results=50,  
        n_top=10,  
        STRICT_MODE=True,
        COLLECTION_NAME="PDF_test_6",
    )
    print(result)
    return (result)

def summary_of_petrophysical_result(well_name="15/9-F-1"):
    query_result = query_pdfs(
        query=f"Summary {well_name}",
        # query=f"TD of 15/9-F-1 was 3632 m MD RKB (Smith Bank Fm.).",
        
        where={"Report_type": 'petropysical'},
        # where={"$and": [
        #     {"Report_type": 'petropysical'},
        #     # {"Filename":"PETROPHYSICAL_REPORT_1.PDF"},
        #     {"Page_num":"4"}
        # ]},
        STRICT_MODE=True,
        COLLECTION_NAME='PDF_test_6',n_results=2000,n_top=5)
    return query_result

def summary_hole_record(well_name="15/9-F-12"):
    query_result = query_pdfs(
        # query="include hole record and casing record",
        query="hole record",
        where={"$and": [
            {"Report_type": 'drilling and measurements for end of well report'},
            {"Filename": "DRILLING_REPORT_1.PDF"},
            # {"Page_num":"5"}
        ]},
        COLLECTION_NAME='PDF_test_6',n_results=30,n_top=5)
    return query_result

def final_well_report_list_bha(well_name="15/9-F-4"):
    query_result = query_pdfs(
        # query="include hole record and casing record",
        query="BHA NO:",
        # where={
        #     # "Report_type":'final well report',
        #     "Well_name":'15/9-F-4'
        # },
        where={"$and": [
            {"Report_type": 'final well report'},
            {"Well_name": well_name},
            {"Description":"None"},
            {"Filename": "FWR_completion.pdf"},
            # {"Page_num":"5"}
        ]},
        STRICT_MODE=True,
        COLLECTION_NAME='PDF_test_6',n_results=50,n_top=10)
    return query_result

def well_report_get_main_result_of_test_of_well(test_no='1',well_name='15/9-19A'):
    query_result = query_pdfs(
        # query="include hole record and casing record",
        query=f"Main results",
        where={
            # "Report_type":'final well report',
            "Well_name":well_name
        },
        # where={"$and": [
        #     {"Report_type": 'final well report, completion FWR'},
        #     {"Well_name": '15/9-F-4'},
        #     {"Filename": "FWR_completion.pdf"},
        #     # {"Page_num":"5"}
        # ]},
        STRICT_MODE=True,
        COLLECTION_NAME='PDF_test_6',n_results=100,n_top=5)
    return query_result

def get_information_among_all_reports(keyword=""):
    query_result = query_pdfs(
        query=keyword,
        n_results=100,
        n_top=10,
        STRICT_MODE=True,
        COLLECTION_NAME='PDF_test_6'
    )
    return query_result

def get_function_response(function_name,function_args):
    # if function_name == "query_overall":
    #     query_text = function_args["query_text"]    
    #     function_response = query_overall(
    #         query_text=query_text,
    #     )
    if function_name == "get_all_fields_among_files":
        field_name = function_args["field_name"]
        function_response = query_distinct_value_of_field_all_report(
            field_name=field_name
        )
    elif function_name == "get_group_of_biostratigraphy":
        group_by = function_args["group_by"]
        function_response = get_group_of_biostratigraphy(
            group_by=group_by
        )
    elif function_name == "get_group_of_petrophysical":
        group_by = function_args["group_by"]
        function_response = get_group_of_petrophysical(
            group_by=group_by
        )
    elif "summary_of_petrophysical_result" in function_name:
        well_name = function_args["well_name"]
        function_response = summary_of_petrophysical_result(
            well_name=well_name
        )
    elif function_name == "summary_hole_record":
        well_name = function_args["well_name"]
        function_response = summary_hole_record(
            well_name=well_name
        )
    elif function_name == "final_well_report_list_bha":
        well_name = function_args["well_name"]
        function_response = final_well_report_list_bha(
            well_name=well_name
        )
    elif function_name == "well_report_get_main_result_of_test_of_well":
        test_no = function_args["test_no"]
        well_name = function_args["well_name"]
        function_response = well_report_get_main_result_of_test_of_well(
            test_no=test_no,
            well_name=well_name
        )
    elif function_name == "get_information_in_biostratigraphy":
        keyword = function_args["keyword"]
        well_name = function_args["well_name"]
        function_response = get_information_in_biostratigraphy(
            keyword=keyword,
            well_name=well_name
        )
    elif function_name == "get_information_in_petrophysical":
        keyword = function_args["keyword"]
        well_name = function_args["well_name"]
        function_response = get_information_in_petrophysical(
            keyword=keyword,
            well_name=well_name
        )  
    elif function_name == "get_information_among_all_reports":
        keyword = function_args["keyword"]
        function_response = get_information_among_all_reports(
            keyword=keyword 
        )
    return function_response 