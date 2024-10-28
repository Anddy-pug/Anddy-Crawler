import os
import pandas as pd

# Directory to crawl
directory = './'

# List to store file details
file_data = []

# Crawl through the directory and collect file names, sizes, and directories
for root, dirs, files in os.walk(directory):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        file_size = int(os.path.getsize(file_path) / 1024)  # File size in KB as an integer
        file_data.append({
            "File Name": file_name,
            "File Size (KB)": file_size,
            "File Directory": root
        })

# Convert to DataFrame
df = pd.DataFrame(file_data)

# Export to Excel
output_file = 'file_data.xlsx'
df.to_excel(output_file, index=False)

print(f"Data exported successfully to {output_file}")
