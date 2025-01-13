# WebLook: WebUntis to Outlook Tool

## Description
**WebLook** is a Python application that integrates WebUntis timetables with Outlook. It fetches timetables, generates ICS calendar files, and allows users to open them in Outlook. The tool includes a configuration menu to customize settings like class, school number, and debugging.

## Features
- Fetch timetables from WebUntis.
- Generate and open ICS calendar files in Outlook.
- Modify class, school number, and debugging settings.
- User-friendly text-based menus.

## Prerequisites
- Python 3.x
- Required libraries: `requests`, `python-dotenv`
  ```bash
  pip install requests python-dotenv

## Configuration
### Configuration File (`config.env`)
Stores settings like:
- **STANDARD_KLASSE**: Default class.
- **STANDARD_SCHULNUMMER**: School number.
- **DEBUGGING**: Flag for debugging mode.

If the file doesn't exist, it will be created automatically with default values.

### Default Configuration
```ini
STANDARD_KLASSE=None
STANDARD_SCHULNUMMER=None
DEBUGGING=True
```

## Usage
### Starting the Tool
To run the tool, simply execute `start.bat` on Windows, or run the following command:
```bash
python weblook.py
```

### Main Menu
Options:
1. **Fetch Timetable**: Generate an ICS file for the selected class and school.
2. **Settings**: Update configuration (class, school number, debugging).
3. **Exit**: Close the program.

### Fetching Timetable
- Enter city, select school, and class, then fetch the timetable for the next three weeks.
- The `.ics` file will be saved and optionally opened in Outlook.

## Debugging
Enable debugging by setting `DEBUGGING=True` in `config.env`. Debug info will be printed to the console.

## License
This project is open-source under the MIT License.

## Troubleshooting
- Ensure correct city, school number, and class are entered.
- Check internet connection if data fetching fails.
- Ensure `.ics` files open correctly in Outlook.

```

This version is shorter and includes the instruction to run the `start.bat` file to launch the tool.
