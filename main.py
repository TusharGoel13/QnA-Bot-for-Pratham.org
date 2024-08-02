import subprocess

def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command {' '.join(command)} failed with error:\n{result.stderr}")
        return False
    else:
        print(f"Command {' '.join(command)} succeeded.")
        return True

# Install the required packages
if run_command(["pip", "install", "-r", "requirements.txt"]):
    # Execute the web scraper file
    if run_command(["python", "web_scraper.py"]):
        # Execute the data transformation file
        if run_command(["python", "data_transform.py"]):
            # Run the Streamlit app
            run_command(["streamlit", "run", "app.py"])
        else:
            print("Data transformation script failed. Aborting.")
    else:
        print("Web scraper script failed. Aborting.")
else:
    print("Package installation failed. Aborting.")
