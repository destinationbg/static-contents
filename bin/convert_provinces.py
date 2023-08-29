import json
import os
import shutil
import yaml

# Constants
INPUT_JSON_FILE = "data/ek_obl.json"
OUTPUT_FOLDER = "../4.localities/1.provinces"
DESCRIPTION_PLACEHOLDER = "..."

# Function to convert a string to kebab-case


def clean_string(text):
    text = text.replace(' ', '-').replace('(', '').replace(')', '')
    return text.lower()

# Function to validate JSON data


def validate_json_data(item):
    required_fields = ["name", "name_en", "ekatte", "oblast"]
    for field in required_fields:
        if field not in item:
            return False
    return True


try:
    # Check if INPUT_JSON_FILE exists
    if not os.path.exists(INPUT_JSON_FILE):
        print(f"Error: {INPUT_JSON_FILE} not found!")
        exit()

    # Read the JSON file
    with open(INPUT_JSON_FILE, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    # Create the "1.provinces" folder if it doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Delete all files and subdirectories inside the OUTPUT_FOLDER
    for filename in os.listdir(OUTPUT_FOLDER):
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath)
        except Exception as e:
            print(f"Failed to delete {filepath}. Reason: {e}")

    # Process the JSON data
    for item in data:
        if not validate_json_data(item):
            print(f"Skipping invalid data: {item}")
            continue

        name_bg = item["name"]
        name_en = item["name_en"]
        ekatte = item["ekatte"]
        code = item["oblast"]
        slug = clean_string(name_en)

        # Create the YAML data
        yaml_data = {
            "slug": clean_string(slug),
            "ekatte": ekatte,
            "code": code,
            "locale": {
                "bg": {
                    "name": f"Област {name_bg}",
                    "description": DESCRIPTION_PLACEHOLDER
                },
                "en": {
                    "name": f"{name_en} Province",
                    "description": DESCRIPTION_PLACEHOLDER
                }
            }
        }

        # Generate the YAML filename
        yaml_filename = f"{slug}-{code.lower()}.yml"

        # Write the YAML data to the file in the "1.provinces" folder
        yaml_filepath = os.path.join(OUTPUT_FOLDER, yaml_filename)
        with open(yaml_filepath, "w", encoding="utf-8") as yaml_file:
            yaml.dump(yaml_data, yaml_file, default_flow_style=False,
                      allow_unicode=True, sort_keys=False)

    print(
        f"Created YAML files for 'Province' ({OUTPUT_FOLDER}) based on the EKATTE data.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
