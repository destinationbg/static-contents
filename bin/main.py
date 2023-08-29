import subprocess


def run_script(script_name):
    """Run a python script and print its output."""
    result = subprocess.run(['python3', script_name],
                            capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Errors from {script_name}:\n{result.stderr}")


scripts = ['convert_provinces.py', 'convert_municipalities.py',
           'convert_entries.py', 'find_duplicates.py', 'update_entries.py']

for script in scripts:
    print(f"[STARTING '{script}']\n")
    run_script(script)
    print(f"{'-'*30}\n")
