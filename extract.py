from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.chunker import HierarchicalChunker
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.datamodel.base_models import InputFormat
import json
import os
import glob

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
if __name__ == "__main__":
    pdf_files = glob.glob('pdf/*.pdf') + glob.glob('pdf/*.PDF')

    for pdf_file in pdf_files:
        try:
            result = converter.convert(pdf_file)
            
            output_filename = os.path.basename(pdf_file)
            output_filename = os.path.splitext(output_filename)[0] + '.json'
            output_path = os.path.join('parsed', output_filename)
            
            with open(output_path, 'w') as f:
                json.dump(result.document.export_to_dict(), f, indent=4, ensure_ascii=False)
                
            print(f"Successfully processed: {pdf_file}")
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")