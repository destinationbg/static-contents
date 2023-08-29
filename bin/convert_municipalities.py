import json
import os
import shutil
import yaml

# Constants
INPUT_JSON_FILE = "data/ek_obst.json"
OUTPUT_FOLDER = "../4.localities/2.municipalities"
DESCRIPTION_PLACEHOLDER = "..."
REGIONS_JSON_FILE = "data/municipalities_by_region.json"

# Function to check if a file exists and is readable.


def file_exists(filepath):
    if not os.path.exists(filepath):
        print(f"File '{filepath}' does not exist.")
        return False
    if not os.path.isfile(filepath):
        print(f"Given path '{filepath}' is not a file.")
        return False
    return True

# Function to replace spaces and parentheses with hyphens


def clean_string(text):
    text = text.replace(' ', '-').replace('(', '').replace(')', '')
    return text.lower()

# Function to validate JSON data


def validate_json_data(item):
    required_fields = ["name", "name_en", "ekatte", "obshtina"]
    for field in required_fields:
        if field not in item:
            return False
    return True

# Function to format names based on the municipality code


def format_names(name_bg, name_en, slug_original, combined):
    if combined == "byala-rse04":
        slug_original = "byala-ruse"
        name_bg = f"Община {name_bg} (обл. Русе)"
        name_en = f"{name_en} Municipality (Ruse Province)"
    elif combined == "byala-var05":
        slug_original = "byala-varna"
        name_bg = f"Община {name_bg} (обл. Варна)"
        name_en = f"{name_en} Municipality (Varna Province)"
    else:
        slug_original = slug_original
        name_bg = f"Община {name_bg}"
        name_en = f"{name_en} Municipality"
    return name_bg, name_en, slug_original


try:
    # Check for file existence
    if not file_exists(REGIONS_JSON_FILE) or not file_exists(INPUT_JSON_FILE):
        raise Exception(
            f"One of the required files ('{INPUT_JSON_FILE}' or '{REGIONS_JSON_FILE}') does not exist or is not accessible.")

    # Read the JSON file containing region information
    with open(REGIONS_JSON_FILE, "r", encoding="utf-8") as regions_file:
        regions_data = json.load(regions_file)

    # Read the JSON file
    with open(INPUT_JSON_FILE, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    # Check the integrity of the loaded regions_data and data from JSON files
    if not isinstance(regions_data, list):
        raise Exception(f"Data in '{REGIONS_JSON_FILE}' is not a list.")

    if not all(isinstance(item, dict) for item in regions_data):
        raise Exception(
            f"All entries in '{REGIONS_JSON_FILE}' should be dictionaries.")

    if not isinstance(data, list):
        raise Exception(f"Data in '{INPUT_JSON_FILE}' is not a list.")

    if not all(isinstance(item, dict) for item in data):
        raise Exception(
            f"All entries in '{INPUT_JSON_FILE}' should be dictionaries.")

    # Create the "2.municipalities" folder if it doesn't exist
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
        slug_original = clean_string(item["name_en"])
        ekatte = item["ekatte"]
        code = item["obshtina"]
        slug = clean_string(name_en)
        combined = f"{slug}-{code.lower()}"

        # Find the region for the municipality
        region = None
        for entry in regions_data:
            if combined in entry["municipalities"]:
                region = entry["region"]
                break

        if region is None:
            print(f"Region not found for {name_en}.")
            continue

        # Format names based on the municipality code
        name_bg_formatted, name_en_formatted, slug_original = format_names(
            name_bg, name_en, slug_original, combined)

        # Create the YAML data
        yaml_data = {
            "slug": slug_original,
            "ekatte": ekatte,
            "code": code,
            "locale": {
                "bg": {
                    "name": name_bg_formatted,
                    "description": DESCRIPTION_PLACEHOLDER
                },
                "en": {
                    "name": name_en_formatted,
                    "description": DESCRIPTION_PLACEHOLDER
                }
            },
            "region": region
        }

        # Generate the YAML filename
        yaml_filename = f"{combined}.yml"

        # Write the YAML data to the file in the "2.municipalities" folder
        yaml_filepath = os.path.join(OUTPUT_FOLDER, yaml_filename)
        with open(yaml_filepath, "w", encoding="utf-8") as yaml_file:
            yaml.dump(yaml_data, yaml_file, default_flow_style=False,
                      allow_unicode=True, sort_keys=False)

    print(
        f"Created YAML files for 'Municipality' ({OUTPUT_FOLDER}) based on the EKATTE data.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
