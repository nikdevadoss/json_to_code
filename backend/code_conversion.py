import csv
import json

def processKey(key_data):
    key_dict = {}

    for key, value in key_data.items():
        if key.startswith('Text Area') and '\u2028' in value:
            shape_type, description = value.split('\u2028', 1)
            key_dict[shape_type] = description.strip()
    return key_dict

def lucidchart_csv_to_json(csv_filepath):
    pages = {}
    group_ids = set()

    # First pass: Identify group IDs and initialize page structures
    with open(csv_filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            page_id = row['Page ID']
            if page_id not in pages:
                pages[page_id] = {'shapes': [], 'lines': [], 'texts': [], 'other': [], 'groups': [], 'key': ""}

            # Identify group IDs
            if row['Group']:
                group_ids.add(row['Group'])


    # Second pass: Categorize elements
    with open(csv_filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            page_id = row['Page ID']
            element_id = row['Id']
            
            # Categorize as line, shape, text, or other
            if element_id in group_ids:
                pages[page_id]['groups'].append(row)
            elif row['Line Source'] and row['Line Destination']:
                pages[page_id]['lines'].append(row)
            elif 'Flowchart' in row['Shape Library']:
                pages[page_id]['shapes'].append(row)
            # Add more conditions as necessary for texts
            elif row['Name'] == 'Diagram key':
                pages[page_id]['key'] = processKey(row)
            else:
                pages[page_id]['other'].append(row)

    return list(pages.values())

# Path to your CSV file
csv_file_path = 'simple.csv'

file_name = csv_file_path.split('.csv')[0]

# Convert to JSON
json_data = lucidchart_csv_to_json(csv_file_path)

# Print or save the JSON data
print(json.dumps(json_data, indent=4))
# Optionally, write to a JSON file
with open(file_name + '.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=4)
