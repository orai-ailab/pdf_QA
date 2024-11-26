from utils import query_pdfs,get_distinct_field

# calling function
def query_distinct_value_of_field(field_name):
    def eliminate_duplicates(file_list):
        normalized_files = {}
        
        for file in file_list:
            normalized_name = file.split('/')[-1]
            normalized_name = normalized_name.lower()
            
            if normalized_name not in normalized_files:
                normalized_files[normalized_name] = file
        
        return list(normalized_files.values())
    
    result = eliminate_duplicates(get_distinct_field(field=field_name,collection_name="PDF_test_3"))
    return result

def get_group_of_biostratigraphy(group_by="Well_name"):
    filter = {"Report_type":"Biostratigraphy"}
    result = query_pdfs(
        query="",  # No specific query string since we're only using a filter
        where=filter,
        n_results=100,  # Adjust to ensure you retrieve all relevant documents
        n_top=100,  # Retrieve up to 100 top results
        COLLECTION_NAME="PDF_test_3",
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
        n_results=20,  # Adjust to ensure you retrieve all relevant documents
        n_top=5,  # Retrieve up to 100 top results
        COLLECTION_NAME="PDF_test_3",
    )
    return (result)

def get_group_of_petropysical(group_by="Filename"):
    filter = {"Report_type":"petropysical"}
    result = query_pdfs(
        query="",  # No specific query string since we're only using a filter
        where=filter,
        n_results=100,  # Adjust to ensure you retrieve all relevant documents
        n_top=100,  # Retrieve up to 100 top results
        COLLECTION_NAME="PDF_test_3",
        group_by=group_by
    )
    
    return set(result)

def summary_of_petrophysical_result(well_name="15/9-F-1"):
    query_result = query_pdfs(
        query=f"summary the petrophysical result of Well named {well_name}",
        where={"$and": [{"Report_type": 'petropysical'},{"Filename": "PETROPHYSICAL_REPORT_1.PDF"}]},
        COLLECTION_NAME='PDF_test_3',n_results=30,n_top=5)
    return query_result

def summary_hole_record(well_name="15/9-F-12"):
    query_result = query_pdfs(
        # query="include hole record and casing record",
        query="hole record",
        where={"$and": [
            {"Report_type": 'drilling and measurements for end of well report'},
            {"Filename": "pdf/DRILLING_REPORT_1.pdf"},
            # {"Page_num":"5"}
        ]},
        COLLECTION_NAME='PDF_test_3',n_results=30,n_top=5)
    return query_result

def final_well_report_list_bha(well_name="15/9-F-4"):
    query_result = query_pdfs(
        # query="include hole record and casing record",
        query="list let me know how many BHA runs",
        # where={
        #     # "Report_type":'final well report',
        #     "Well_name":'15/9-F-4'
        # },
        where={"$and": [
            {"Report_type": 'final well report, completion FWR'},
            {"Well_name": well_name},
            {"Filename": "FWR_completion.pdf"},
            # {"Page_num":"5"}
        ]},
        COLLECTION_NAME='PDF_test_3',n_results=50,n_top=10)
    return query_result

def well_report_get_main_result_of_test_of_well(test_no='1',well_name='15/9-19A'):
    query_result = query_pdfs(
        # query="include hole record and casing record",
        query=f"Main results of Test {test_no} of well name {well_name}",
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
        COLLECTION_NAME='PDF_test_3',n_results=100,n_top=10)
    return query_result

def query_overall(query_text=""):
    result = query_pdfs(
        query=query_text,
        COLLECTION_NAME='PDF_test_3',
        n_results=3
    )
    # print('QUERY RESULT: ',query_result)
    # print('WHERE: ',{"$and": [{"report_type": report_type},{"well_name": well_name}]})
    return result





def get_function_response(function_name,function_args):
    if function_name == "fc_query":
        query_text = function_args["query_text"]
        report_type = function_args.get("report_type",None)
        well_name = function_args.get("well_name",None)
    
        function_response = fc_query(
            query_text=query_text,
            report_type=report_type,
            well_name=well_name
        )
    elif function_name == "query_distinct_value_of_field":
        field_name = function_args["field_name"]
        function_response = query_distinct_value_of_field(
            field_name=field_name
        )
    elif function_name == "get_group_of_biostratigraphy":
        group_by = function_args["group_by"]
        function_response = get_group_of_biostratigraphy(
            group_by=group_by
        )
    elif function_name == "get_group_of_petropysical":
        group_by = function_args["group_by"]
        function_response = get_group_of_petropysical(
            group_by=group_by
        )
    elif function_name == "summary_of_petrophysical_result":
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
    return function_response 