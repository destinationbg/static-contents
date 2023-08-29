import os
import re
import yaml
import json


def find_duplicates(folder_path, output_file, pattern, entity_type):
    """Finds and writes duplicated entities to a specified output file."""
    entity_files = {}

    for filename in os.listdir(folder_path):
        if filename.endswith(".yml"):
            match = re.match(pattern, filename)
            if match:
                entity_name = match.group(1)
                if entity_name in entity_files:
                    entity_files[entity_name].append(filename)
                else:
                    entity_files[entity_name] = [filename]

    duplicates = {k: sorted(v) for k, v in entity_files.items() if len(v) > 1}

    if not duplicates:
        print(f"No duplicates found for '{entity_type}'.")
        return

    script_directory = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(script_directory, output_file), 'w') as f:
        for entity_name in sorted(duplicates.keys()):
            for filename in duplicates[entity_name]:
                f.write(filename + '\n')

    print(
        f"Duplicated entities of '{entity_type}' names exported successfully ({output_file}).")


def process_localities(locality_file, locality_type):
    result = []

    if not os.path.exists(locality_file):
        print(f"The file {locality_file} does not exist!")
        return result

    with open(locality_file, 'r') as f:
        localities = f.readlines()

    if not localities:
        print(f"No localities found in {locality_file}.")
        return result

    with open(locality_file, 'r') as f:
        localities = f.readlines()

    for locality in localities:
        locality = locality.strip()
        locality_name_without_extension = os.path.splitext(locality)[0]
        suffix = locality_name_without_extension.split('-')[-1]

        municipality_file = [f for f in os.listdir(
            municipalities_folder_path) if f.endswith(suffix + '.yml')]

        if municipality_file:
            municipality_path = os.path.join(
                municipalities_folder_path, municipality_file[0])
            with open(municipality_path, 'r') as m_file:
                data = yaml.safe_load(m_file)
                municipality_bg_name = data['locale']['bg']['name']
                municipality_en_name = data['locale']['en']['name']

                locality_data = {
                    locality_type: locality_name_without_extension,
                    "municipality": [
                        {
                            "bg": municipality_bg_name,
                            "en": municipality_en_name
                        }
                    ]
                }

                result.append(locality_data)

    return result


def save_to_file(data, output_file, locality_type):
    script_directory = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(script_directory, output_file), 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print(
        f"Municipalities for '{locality_type}' saved successfully ({output_file}).")


if __name__ == "__main__":
    # Parameters for cities
    city_folder_path = '../4.localities/3.cities'
    city_output_file = 'data/auto-generated/duplicated_cities.txt'
    city_pattern = r"^(.+)-[a-zA-Z]{3}\d{2}\.yml$"

    # Parameters for villages
    village_folder_path = '../4.localities/4.villages'
    village_output_file = 'data/auto-generated/duplicated_villages.txt'
    village_pattern = r"^(.+)-[a-zA-Z]{3}\d{2}\.yml$"

    # Paths
    municipalities_folder_path = '../4.localities/2.municipalities'

    # Check if folders exist
    if not os.path.exists(municipalities_folder_path):
        print(
            f"The municipalities folder {municipalities_folder_path} does not exist!")
        exit()

    if not os.path.exists(city_folder_path):
        print(f"The city folder {city_folder_path} does not exist!")
        exit()

    if not os.path.exists(village_folder_path):
        print(f"The village folder {village_folder_path} does not exist!")
        exit()

    # Call the function for cities and villages
    find_duplicates(city_folder_path, city_output_file, city_pattern, 'city')
    find_duplicates(village_folder_path, village_output_file,
                    village_pattern, 'village')

    # Process cities
    cities_result = process_localities(city_output_file, 'city')
    if cities_result:
        save_to_file(
            cities_result, 'data/auto-generated/municipalities_of_cities.json', 'cities')
    else:
        print("No processed city data to save.")

    # Process villages
    villages_result = process_localities(village_output_file, 'village')
    if villages_result:
        save_to_file(
            villages_result, 'data/auto-generated/municipalities_of_villages.json', 'villages')
    else:
        print("No processed village data to save.")
