# WebLook: WebUntis to Outlook Tool

## Description
The **WebLook** is a Python application designed to integrate WebUntis timetables with Outlook. It fetches a user's timetable from WebUntis, generates a calendar (.ics) file, and allows users to open this file in Outlook. This tool also includes a configuration menu for updating the settings and fetching timetables for specific schools and classes.

## Features
- Fetch timetables from WebUntis.
- Generate ICS calendar files from WebUntis timetable data.
- Open generated ICS files in Outlook.
- Update configuration settings for school class and debugging options.
- User-friendly text-based menus for interacting with the tool.

## Prerequisites
Before running the script, ensure that you have the following dependencies installed:
- Python 3.x
- `requests` library for HTTP requests
- `datetime` module for handling date and time
- `urllib` for URL encoding
- `json` for parsing and manipulating JSON data
- `os` for file and system operations
- `base64` for base64 encoding
- `python-dotenv` for managing environment variables (optional but recommended)
- `subprocess` for interacting with system processes

Install the required dependencies using pip:
```bash
pip install requests python-dotenv
```

## Configuration
### Configuration File (`config.env`)
The configuration file `config.env` is used to store important settings:
- **STANDARD_KLASSE**: The default class to fetch timetables for.
- **STANDARD_SCHULNUMMER**: The school number to use for WebUntis.
- **DEBUGGING**: A flag to enable or disable debugging.

If `config.env` does not exist, it will be created automatically with default values. You can modify the settings through the **Settings Menu** of the application.

### Default Configuration
```ini
STANDARD_STADT=None
STANDARD_KLASSE=None
STANDARD_SCHULNUMMER=None
DEBUGGING=True
```

### Environment Variables
- You can create a `.env` file with any necessary credentials or settings.

## Usage
### Running the Tool
To run the tool, simply execute the Python script:

```bash
python webllook.py
```

### Main Menu
Upon starting the program, you'll be presented with the main menu options:
1. **Fetch Timetable**: Fetch the timetable for a specified school and class and generate an ICS file.
2. **Settings**: Access the settings menu to view and update configurations.
3. **Exit**: Exit the program.

### Settings Menu
The settings menu provides the following options:
1. **View Current Settings**: Displays the current configuration settings.
2. **Update STANDARD_KLASSE**: Update the default class used to fetch the timetable.
3. **Update STANDARD_SCHULNUMMER**: Update the school number used for WebUntis.
4. **Update DEBUGGING**: Enable or disable debugging mode (default is `True`).
5. **Back to Main Menu**: Return to the main menu.

### Fetching Timetable
- When you select **Fetch Timetable**, the program will ask you for the city where the school is located and will display a list of available schools.
- You will need to select a school, input the class name, and the program will fetch the timetable for the next three weeks.
- The timetable will be saved as an `.ics` file, and you will be prompted if you want to open it in Outlook.

### ICS File
- The generated `.ics` file contains the schedule for the next three weeks. This file can be opened with any calendar application like Outlook.
- The file is named `<schoolname>_stundenplan_woche.ics`.

## Functions

### Main Functions:
- `display_main_menu()`: Displays the main menu of the application.
- `display_settings_menu()`: Displays the settings menu where users can manage configurations.
- `read_config_env()`: Reads the configuration from the `config.env` file.
- `update_config_env()`: Updates the configuration settings in the `config.env` file.
- `fetch_timetable()`: Fetches the timetable for the specified class and generates the ICS file.
- `fetch_data_for_next_weeks()`: Fetches timetable data for the next three weeks.
- `create_ics_file_for_week()`: Creates an ICS file for the week based on the fetched timetable data.
- `open_ics_with_default_app()`: Opens the generated ICS file with the default calendar application (e.g., Outlook).
- `get_schools()`: Retrieves available schools based on a city name.
- `get_class_id_headers()`: Retrieves headers required for fetching class information.
- `get_cookies()`: Retrieves cookies for WebUntis authentication.
- `get_headers()`: Retrieves headers for API requests.

### Helper Functions:
- `get_start_of_week()`: Calculates the start date of the week based on a given date.
- `generate_sleek_session()`: Generates a unique session identifier.
- `get_class_id_headers()`: Retrieves headers for class data.
- `get_classes_from_text()`: Fetches class information from WebUntis.
- `fetch_timetable_data()`: Makes an API request to fetch timetable data for a specific week.
- `get_school_days_subjects_teachers()`: Extracts school days, subjects, and teacher information from timetable data.

## Debugging
To enable debugging mode, update the `DEBUGGING` field in the `config.env` file to `True`. In debugging mode, additional information about the HTTP requests, responses, and errors will be printed to the console.

## License
This project is open-source and available under the MIT License.

## Acknowledgements
This tool interacts with the WebUntis API for fetching school timetables. All API interactions are done through public endpoints provided by WebUntis.

## Troubleshooting
- Ensure that the correct city, school number, and class name are entered when prompted.
- If the program fails to fetch data, check your internet connection and ensure WebUntis is accessible.
- If the ICS file does not open in Outlook, ensure that your system has an application set to open `.ics` files.

