from tika import parser

# Initialize Tika by connecting to the Tika server (if needed)
from tika import tika
# tika.initVM()

# Path to your file
file_path = 'f:\Web-Devops.docx'

# Parse the file using Tika
parsed = parser.from_file(file_path, "http://localhost:9998")

# Get the metadata from the parsed content

metadata = parsed.get('metadata', {})

# Debug: Print all metadata keys and values
print("All Metadata:")
for key, value in metadata.items():
    print(f"{key}: {value}")

# Extract creation and modification dates using various possible keys
created_date = (
    metadata.get('meta:creation-date') or
    metadata.get('Creation-Date') or
    metadata.get('dcterms:created') or
    metadata.get('created') or
    'N/A'
)

modified_date = (
    metadata.get('Last-Modified') or
    metadata.get('Last_Modified') or
    metadata.get('dcterms:modified') or
    metadata.get('modified') or
    'N/A'
)

print(f"\nExtracted Dates:\nCreated Date: {created_date}\nModified Date: {modified_date}")
        
# Extract the created and modified dates
# created_date = metadata.get('meta:creation-date', 'N/A')
# modified_date = metadata.get('Last-Modified', 'N/A')

# Print the extracted dates
print(f"Created Date: {created_date}")
print(f"Modified Date: {modified_date}")
