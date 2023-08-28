import json
import os
import yaml

# Constants
INPUT_JSON_FILE = "data/ek_atte.json"
CITIES_FOLDER = "../4.localities/3.cities"
VILLAGES_FOLDER = "../4.localities/4.villages"
DESCRIPTION_PLACEHOLDER = "..."

# Function to replace spaces and parentheses with hyphens


def clean_string(text):
    text = text.replace(' ', '-').replace('(', '').replace(')', '')
    return text.lower()

# Function to validate JSON data


def validate_json_data(item):
    required_fields = ["name", "name_en", "ekatte", "obshtina", "t_v_m"]
    for field in required_fields:
        if field not in item:
            return False
    return True

# Function to format names based on the municipality code


def format_names(name_bg, name_en, t_v_m):
    if t_v_m == "с.":
        name_bg = f"Село {name_bg}"
        name_en = f"{name_en} Village"
    elif t_v_m == "гр.":
        name_bg = f"Град {name_bg}"
        name_en = f"{name_en} City"
    else:
        name_bg = f"{name_bg}"
        name_en = f"{name_en}"
    return name_bg, name_en


try:
    # Read the JSON file
    with open(INPUT_JSON_FILE, "r", encoding="utf-8") as ekatte_json_file:
        data = json.load(ekatte_json_file)

    # Create the "3.cities" folder if it doesn't exist
    os.makedirs(CITIES_FOLDER, exist_ok=True)

    # Create the "4.villages" folder if it doesn't exist
    os.makedirs(VILLAGES_FOLDER, exist_ok=True)

    # Process the JSON data
    for item in data:
        if not validate_json_data(item):
            print(f"Skipping invalid data: {item}")
            continue

        name_bg = item["name"]
        name_en = item["name_en"]
        ekatte = item["ekatte"]
        code = item["obshtina"]
        slug = clean_string(name_en)
        t_v_m = item["t_v_m"]

        # Format names based on the municipality code
        name_bg_formatted, name_en_formatted = format_names(
            name_bg, name_en, t_v_m)

        # Create the YAML data
        yaml_data = {
            "slug": clean_string(slug),
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
            }
        }

        # Determine the folder based on "t_v_m" value
        OUTPUT_FOLDER = CITIES_FOLDER if t_v_m == "гр." else VILLAGES_FOLDER

        # Generate the YAML filename
        yaml_filename = f"{slug}-{code.lower()}.yml"

        # Write the YAML data to the file in the appropriate folder
        yaml_filepath = os.path.join(OUTPUT_FOLDER, yaml_filename)
        with open(yaml_filepath, "w", encoding="utf-8") as yaml_file:
            yaml.dump(yaml_data, yaml_file, default_flow_style=False,
                      allow_unicode=True, sort_keys=False)

    print("YAML files created successfully for 'Cities' and 'Villages' categories.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
