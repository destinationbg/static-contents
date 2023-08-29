import json
import os
import yaml

# Constants
INPUT_JSON_FILE = "data/ek_atte.json"
CITIES_FOLDER = "../4.localities/3.cities"
VILLAGES_FOLDER = "../4.localities/4.villages"
MUNICIPALITIES_OF_CITIES_FILE = 'data/auto-generated/municipalities_of_cities.json'
MUNICIPALITIES_OF_VILLAGES_FILE = 'data/auto-generated/municipalities_of_villages.json'
DESCRIPTION_PLACEHOLDER = "..."

# Check if a file exists


def file_exists(filepath):
    return os.path.isfile(filepath)

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


# Check if input and reference JSON files exist
if not file_exists(INPUT_JSON_FILE) or not file_exists(MUNICIPALITIES_OF_CITIES_FILE) or not file_exists(MUNICIPALITIES_OF_VILLAGES_FILE):
    print("One or more necessary JSON files are missing. Please ensure they are in the correct path.")
    exit(1)

# Function to format names based on the municipality code


# Load municipalities_of_cities.json
with open(MUNICIPALITIES_OF_CITIES_FILE, 'r', encoding='utf-8') as f:
    cities_data = json.load(f)

# Create a mapping dictionary for cities
city_municipality_mapping = {
    item["city"]: item["municipality"][0] for item in cities_data}

# Load municipalities_of_villages.json
with open(MUNICIPALITIES_OF_VILLAGES_FILE, 'r', encoding='utf-8') as f:
    villages_data = json.load(f)

# Create a mapping dictionary
village_municipality_mapping = {
    item["village"]: item["municipality"][0] for item in villages_data}


def format_names(name_bg, name_en, t_v_m, slug_original, combined):
    if t_v_m == "с.":
        if combined in village_municipality_mapping:
            municipality_bg = village_municipality_mapping[combined]['bg'].replace(
                'Община ', '').strip()
            municipality_en = village_municipality_mapping[combined]['en'].replace(
                ' Municipality', '').strip()

            slug_original = f"{clean_string(combined).split('-')[0]}-{clean_string(municipality_en).lower()}"
            name_bg = f"Село {name_bg} (общ. {municipality_bg})"
            name_en = f"{name_en} Village ({municipality_en} Municipality)"
        else:
            name_bg = f"Село {name_bg}"
            name_en = f"{name_en} Village"
    elif t_v_m == "гр.":
        if combined in city_municipality_mapping:
            province_bg = city_municipality_mapping[combined]['bg'].split(
                " (обл. ")[1].replace(')', '').strip()
            province_en = city_municipality_mapping[combined]['en'].split(
                " (")[1].replace(' Province)', '').strip()

            slug_original = f"{clean_string(combined).split('-')[0]}-{clean_string(province_en).lower()}"
            name_bg = f"Град {name_bg} (обл. {province_bg})"
            name_en = f"{name_en} City ({province_en} Province)"
        else:
            name_bg = f"Град {name_bg}"
            name_en = f"{name_en} City"

    return name_bg, name_en, slug_original


try:
    # Read the JSON file
    with open(INPUT_JSON_FILE, "r", encoding="utf-8") as ekatte_json_file:
        data = json.load(ekatte_json_file)

    # Check if municipalities data was loaded correctly
    if not cities_data or not villages_data:
        print("Error: Failed to load municipalities data.")
        exit(1)

    # Create the "3.cities" and "4.villages" folders if they don't exist
    os.makedirs(CITIES_FOLDER, exist_ok=True)
    os.makedirs(VILLAGES_FOLDER, exist_ok=True)

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
        t_v_m = item["t_v_m"]
        combined = f"{slug}-{code.lower()}"

        # Format names based on the city/village code
        name_bg_formatted, name_en_formatted, slug_original = format_names(
            name_bg, name_en, t_v_m, slug_original, combined)

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
            }
        }

        # Determine the folder based on "t_v_m" value
        OUTPUT_FOLDER = CITIES_FOLDER if t_v_m == "гр." else VILLAGES_FOLDER

        # Generate the YAML filename
        yaml_filename = f"{combined}.yml"

        # Write the YAML data to the file in the appropriate folder
        yaml_filepath = os.path.join(OUTPUT_FOLDER, yaml_filename)
        with open(yaml_filepath, "w", encoding="utf-8") as yaml_file:
            yaml.dump(yaml_data, yaml_file, default_flow_style=False,
                      allow_unicode=True, sort_keys=False)

    print(
        f"Updated YAML files for 'Cities' ({CITIES_FOLDER}) and 'Villages' ({VILLAGES_FOLDER}) based on the found duplicated data.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
