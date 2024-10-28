import pandas as pd

# Path to the input Excel file
input_file = './file_data.xlsx'  # Replace with your file path

# Load the Excel file into a DataFrame
df = pd.read_excel(input_file)

# Ensure that there are at least two columns
if df.shape[1] < 2:
    raise ValueError("The input file must contain at least two columns.")

# Get the names of the first and second columns
field1 = df.columns[0]
field2 = df.columns[1]
new_field = 'MergedField'

# Merge the first and second fields into a new field
df[new_field] = df[field1].astype(str) + df[field2].astype(str)

# Save the updated DataFrame to a new Excel file
output_file = 'output_file.xlsx'  # Replace with your desired output file path
df.to_excel(output_file, index=False)

print(f"New field '{new_field}' added and saved to {output_file}")
