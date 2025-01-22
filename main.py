
import requests
import re
import datetime
import urllib.parse
import json
import os
import base64
from termcolor import colored
#from dotenv import load_dotenv, find_dotenv
import subprocess

def display_main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(colored(r"""
        
    █     █░▓█████  ▄▄▄▄    ██▓     ▒█████   ▒█████   ██ ▄█▀
    ▓█░ █ ░█░▓█   ▀ ▓█████▄ ▓██▒    ▒██▒  ██▒▒██▒  ██▒ ██▄█▒ 
    ▒█░ █ ░█ ▒███   ▒██▒ ▄██▒██░    ▒██░  ██▒▒██░  ██▒▓███▄░ 
    ░█░ █ ░█ ▒▓█  ▄ ▒██░█▀  ▒██░    ▒██   ██░▒██   ██░▓██ █▄ 
    ░░██▒██▓ ░▒████▒░▓█  ▀█▓░██████▒░ ████▓▒░░ ████▓▒░▒██▒ █▄
    ░ ▓░▒ ▒  ░░ ▒░ ░░▒▓███▀▒░ ▒░▓  ░░ ▒░▒░▒░ ░ ▒░▒░▒░ ▒ ▒▒ ▓▒
    ▒ ░ ░   ░ ░  ░▒░▒   ░ ░ ░ ▒  ░  ░ ▒ ▒░   ░ ▒ ▒░ ░ ░▒ ▒░
    ░   ░     ░    ░    ░   ░ ░   ░ ░ ░ ▒  ░ ░ ░ ▒  ░ ░░ ░ 
        ░       ░  ░ ░          ░  ░    ░ ░      ░ ░  ░  ░   
                        ░                                  
                                                                
    """, "red"))
    print("Welcome to the WebLook --- Number one WebUntis to Outlook Tool!")
    print("1. Fetch Timetable")
    print("2. Settings")
    print("3. Exit")

def display_settings_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Settings Menu:")
    print("1. View current settings")
    print("2. Update Name")
    print("3. Update Email")
    print("4. Update Betrieb")
    print("5. Update Stadt")
    print("6. Update Klasse")
    print("7. Update Schulnummer")
    print("8. Update Debugging")
    print("9. Back to Main Menu - Press 9 or Enter")

def read_config_env(file_path='config.env'):
    config = {}
    default_settings = {
        "NAME": "None",
        "EMAIL": "None",
        "BETRIEB": "None",
        "Stadt" : "None",
        "Klasse": "None",
        "Schulnummer": "None",
        "Debugging": "False"
    }

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            for key, value in default_settings.items():
                file.write(f"{key}={value}\n")
        config = default_settings.copy()
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return config

def update_config_env(key, value, file_path='config.env'):
    config = read_config_env(file_path)
    config[key] = value
    with open(file_path, 'w') as file:
        for k, v in config.items():
            file.write(f"{k}={v}\n")

def settings_menu():
    while True:
        display_settings_menu()
        choice = input("Please select an option: ")
        
        if choice == '1':
            config = read_config_env()
            print("\nCurrent Settings:")
            for key, value in config.items():
                print(f"{key} = {value}")
            input("\nPress Enter to return to the menu...")

        elif choice == '2':
            new_value = input("Enter new name: ")
            update_config_env('NAME', new_value)
            print("Name updated successfully!")
            input("\nPress Enter to return to the menu...")

        elif choice == '3':
            new_value = input("Enter new Email: ")
            update_config_env('EMAIL', new_value)
            print("Email updated successfully!")
            input("\nPress Enter to return to the menu...")
        elif choice == '4':
            new_value = input("Enter new Betrieb: ")
            update_config_env('BETRIEB', new_value)
            print("Email updated successfully!")
            input("\nPress Enter to return to the menu...")
        
        elif choice == '5':
            new_value = input("Enter new value for STADT: ")
            update_config_env('Stadt', new_value)
            print("STADT updated successfully!")
            input("\nPress Enter to return to the menu...")
        
        elif choice == '6':
            new_value = input("Enter new value for KLASSE: ")
            update_config_env('Klasse', new_value)
            print("KLASSE updated successfully!")
            input("\nPress Enter to return to the menu...")
        
        elif choice == '7':
            new_value = input("Enter new value for SCHULNUMMER: ")
            update_config_env('Schulnummer', new_value)
            print("SCHULNUMMER updated successfully!")
            input("\nPress Enter to return to the menu...")
        
        elif choice == '8':
            config = read_config_env()
            debugging = config.get('Debugging', 'False')
            

            if debugging.lower() == 'true':
                new_value = False
            elif debugging.lower() == 'false':
                new_value = True
            elif debugging.lower() == '':
                new_value = False
            #new_value = input("Enter new value for Debugging (True/False): ")
            update_config_env('Debugging', new_value)
            print("Debugging updated successfully!")
            print(f"Debugging = {new_value}")
            input("\nPress Enter to return to the menu...")
        
        elif choice == '9' or choice == '':
            break
        
        else:
            print("Invalid choice, please try again.")
            input("\nPress Enter to return to the menu...")
            
def fetch_timetable():
    
    config = read_config_env()
    debugging = config.get("Debugging", False)
    global name
    global email
    global betrieb
    global standard_klasse
    global standard_schulnummer
    global standard_stadt
    global debug_mode
    global jsessionid
    global traceid
    global headers
    global school
    global is_default_usage
    

    name = config.get("NAME", "None")
    email = config.get("EMAIL", "None")
    betrieb = config.get("BETRIEB", "None")
    standard_stadt = config.get("Stadt", "None")
    standard_klasse = config.get("Klasse", "None")
    standard_schulnummer = config.get("Schulnummer", "None")
    jsessionid = ""
    traceid = ""
    # Example logic based on configuration
    if debugging.lower() == 'true':
        print("Der Debugging Modus ist aktiviert.")
        debug_mode = True
    else:
        #print("Der Debugging Modus ist deaktiviert.")
        debug_mode = False
    
    # is default usage

    if name == "None" or name == "":
        choice = input("Bitte gib deinen Namen ein: ")
        name = choice
        update_config_env('NAME', choice)
    if email == "None" or email == "":
        choice = input("Bitte gib deine Email ein: ")
        email = choice
        update_config_env('EMAIL', choice)
    if betrieb == "None" or betrieb == "":
        choice = input("Bitte geben Sie den Namen ihres Arbeitsbetriebs ein: ")
        betrieb = choice
        update_config_env('BETRIEB', choice)
    print()
    while True:
        choice = input("Sollen die Standardeinstellungen verwendet werden? (Y/N): ").strip().lower()
        if choice == "y":
            is_default_usage = True
            break
        elif choice == "n":
            is_default_usage = False
            break
        else:
            print("Ungültige Eingabe! Bitte nur 'Y' oder 'N' angeben.")
        
    #get_cookies()
    # if standard_stadt == "None" or standard_stadt == "" or is_default_usage == False: 
    #     city = str(input("Bitte geben Sie die Stadt der Schule ein z.B Ingolstadt: "))
    #     choiche = ""
    #     if standard_stadt == "None" or standard_stadt == "":


    #         while True:
    #             choiche = input("Soll die Stadt als Standard gespeichert werden? (Y/N): ")
    #             if choiche == "y":
    #                 is_default_usage = True
    #                 break
    #             elif choiche == "n":
    #                 is_default_usage = False
    #                 break
    #             else:
    #                 print("Ungültige Eingabe! Bitte nur 'Y' oder 'N' angeben.")

    #     if choiche.lower() == 'y':
    #         update_config_env('Stadt', city)
    #         print("Standard Stadt gespeichert.")
    # elif is_default_usage:
    #     city = standard_stadt

    if standard_stadt == "None" or standard_stadt.strip() == "" or not is_default_usage:
        # Stadt einlesen
        while True:
            city = input("Bitte geben Sie die Stadt der Schule ein (z.B. Ingolstadt): ").strip()
            if city:
                # Stadt ist nicht leer
                break
            else:
                print("Bitte geben Sie einen gültigen Stadtnamen ein.")

        # Wenn im Code bisher keine Standardstadt konfiguriert ist, kann der Nutzer wählen,
        # ob diese neue Stadt als Standard gespeichert werden soll.
        if standard_stadt == "None" or standard_stadt.strip() == "":
            while True:
                choice = input("Soll die Stadt als Standard gespeichert werden? (Y/N): ").strip().lower()
                if choice == "y":
                    # Nutzer möchte diese Stadt als Standard speichern
                    update_config_env("Stadt", city)
                    print("Standard-Stadt gespeichert.")
                    is_default_usage = True
                    break
                elif choice == "n":
                    # Nutzer möchte diese Stadt nicht als Standard speichern
                    is_default_usage = False
                    break
                else:
                    print("Ungültige Eingabe! Bitte nur 'Y' oder 'N' angeben.")

    else:
        # Standardwerte werden verwendet, also nehmen wir standard_stadt
        city = standard_stadt

    school = get_schools(city=city)
    if school:
        login_name = school["loginSchool"]
    else:
        print("Es konnte keine Schule gefunden werden.")
        input("Press enter to continue...")
        return
    headers = get_headers(tenant_id=school["tenantId"], schoolname=school["loginName"], server=school["server"], login_name=login_name)
    class_id = get_classes_from_text(school)
    if (class_id is not None):

        while True:
            try:
                week_count = int(input("Von wie vielen Wochen sollen die Stundenpläne heruntergeladen werden (1-15)?: ").strip())
                if 1 <= week_count <= 15:
                    # Gültiger Wert, Schleife verlassen
                    break
                else:
                    print("Ungültige Anzahl von Wochen. Bitte gib eine Zahl zwischen 1 und 15 ein.")
            except ValueError:
                # Falls der Input nicht in eine ganze Zahl umgewandelt werden kann
                print("Fehlerhafte Eingabe. Bitte gib eine ganze Zahl zwischen 1 und 15 ein.")


        
        global_file_path = f"./{school['loginName']}_Stundenplan_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.ics"
        print(f"Stundenplan für {login_name} wird heruntergeladen und im ICS-Format gespeichert. Datei: {global_file_path}")
        
        # Abrufen der Stundenpläne für die nächsten x Wochen
        # TODO: Implementieren Sie die Methode fetch_data_for_next_weeks() hier
         

        school_days_subjects_teachers = fetch_data_for_next_weeks(school=school, class_id=class_id, week_count=week_count)
        create_ics_file_for_week(school_days_subjects_teachers, schoolname=login_name, school_data=school)
        open_in_outlook = input("Soll die Datei in Outlook geöffnet werden? (Y/N): ")
        if open_in_outlook.lower() == 'y':
            open_ics_with_default_app(global_file_path)
        elif open_in_outlook.lower() == 'n':
            print("Die Datei wurde nicht geöffnet.")
        else:
            print("Ungültige Eingabe, die Datei wurde nicht geöffnet.")
        
    else:
        print("Kein Stundenplan gefunden.") 
        
    #print(school["loginName"])
    x_crsf_token = get_x_crsf_token(server=school["server"], loginName=login_name, school=school)
    
    if debug_mode:
        choice = input("Should this version be built? (Y/N): ")
        if choice.lower() == 'y':
            # start build.bat
            os.system("build.bat")
            # check if build was successful
            if not os.path.exists(".\dist\WebLook.exe"):
                print("Build failed.")
            else:
                print("Build successful.")
        
    input("\nPress Enter to continue...")
    
        
    

    

# Funktion zum Abrufen von Daten für x Wochen
def fetch_data_for_next_weeks(school, class_id, week_count):
    # Hole das aktuelle Datum
    current_date = datetime.datetime.now()
    start_of_current_week = get_start_of_week(current_date)
    # Generate the start dates for the specified number of weeks
    weeks_to_fetch = [start_of_current_week]
    for i in range(1, week_count):
        start_of_next_week = get_start_of_week((current_date + datetime.timedelta(weeks=i)).strftime("%Y-%m-%d"))
        weeks_to_fetch.append(start_of_next_week)

    # weeks_to_fetch now contains the start dates for the requested number of weeks
    if debug_mode:
        print(weeks_to_fetch)


    all_school_days = []
    server = school["server"]
    for week_start in weeks_to_fetch:
        api_url = f"https://{server}/WebUntis/api/public/timetable/weekly/data?elementType=1&elementId={class_id}&date={week_start}&formatId=2&filter.departmentId=-1"
        print(f"Hole Daten für die Woche, die am {week_start} beginnt...")

        timetable_data = fetch_timetable_data(api_url, headers)
        
        if timetable_data:
            school_days_subjects_teachers = get_school_days_subjects_teachers(timetable_data)
            all_school_days.extend(school_days_subjects_teachers)
    
    return all_school_days

def get_next_workday(date_obj):
    next_day = date_obj + datetime.timedelta(days=1)
    while next_day.weekday() > 4:  # 5=Sat, 6=Sun
        next_day += datetime.timedelta(days=1)
    return next_day

def create_ics_file_for_week(school_days_subjects_teachers, schoolname, output_dir="kalender", school_data=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    sorted_lessons = sorted(school_days_subjects_teachers, key=lambda x: (x["lesson_date"], x["start_time"]))
    filename = f"{schoolname}_stundenplan_woche.ics"
    file_path = os.path.join(output_dir, filename)
    print(f"Anzahl gefundener Stunden: {len(sorted_lessons)}")
    if len(sorted_lessons) > 0:
        choice = input("Soll eine Out Of Office Notiz erstellt werden? (Y/N): ")
        create_oof = (choice.lower() == "y")

        ics_content = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "CALSCALE:GREGORIAN"
        ]

        

        if sorted_lessons:
            earliest_date = min(lesson["lesson_date"] for lesson in sorted_lessons)
            latest_date = max(lesson["lesson_date"] for lesson in sorted_lessons)
        else:
            earliest_date = datetime.date.today()
            latest_date = earliest_date

        # ICS date strings
        start_date_ics = earliest_date.strftime("%Y%m%d")
        end_date_ics = (latest_date + datetime.timedelta(days=1)).strftime("%Y%m%d")

        next_workday_dt = get_next_workday(latest_date)
        next_workday_str = next_workday_dt.strftime("%d.%m.%Y")

        # Creation date/time for ICS
        if sorted_lessons:
            first_lesson_dt = datetime.datetime.combine(sorted_lessons[0]["lesson_date"], sorted_lessons[0]["start_time"])
            creation_date = first_lesson_dt.strftime("%Y%m%dT%H%M%S")
        else:
            creation_date = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

        # Add lesson events
        for lesson in sorted_lessons:
            event_start = datetime.datetime.combine(lesson["lesson_date"], lesson["start_time"]).strftime("%Y%m%dT%H%M%S")
            event_end = datetime.datetime.combine(lesson["lesson_date"], lesson["end_time"]).strftime("%Y%m%dT%H%M%S")
            event_description = f"{lesson['subject']} - {lesson['teacher']}"

            if lesson["is_exam"]:
                summary_line = f"Prüfung {lesson['subject']}"
                description_line = f"{event_description} Prüfung!"
            elif lesson["is_additional"]:
                summary_line = f"Ersatzstunde {lesson['subject']}"
                description_line = f"{event_description} Prüfung!"
            else:
                summary_line = lesson["subject"]
                description_line = event_description

            ics_content.extend([
                "BEGIN:VEVENT",
                f"DTSTART:{event_start}",
                f"DTEND:{event_end}",
                f"SUMMARY:{summary_line}",
                f"DESCRIPTION:{description_line}",
                f"LOCATION:{lesson['teacher']}",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ])

        # OOF Event
        if create_oof:
            display_name = school_data.get("displayName", "Schule") if school_data else "Schule"
            address = school_data.get("address", "Unbekannte Adresse") if school_data else "Unbekannte Adresse"
            # Build multiline description with embedded newlines.
            # Each line is separated by \n. 
            oof_description = (
                "Sehr geehrte Damen und Herren,\\n\\n"
                "leider bin ich derzeit außer Haus. Sie können mich ab dem "
                f"{next_workday_str} wieder erreichen.\\n\\n"
                "Viele Grüße,\\n\\n"
                f"{name}\\n"
                f"{betrieb}\\n\\n"
                f"{email}\\n\\n"
            )
            oof_location = f"{display_name} ({address})"
            
            ics_content.extend([
                "BEGIN:VEVENT",
                "CLASS:PUBLIC",
                f"CREATED:{creation_date}",
                f"DESCRIPTION:{oof_description}",
                f"DTEND;VALUE=DATE:{end_date_ics}",
                f"DTSTART;VALUE=DATE:{start_date_ics}",
                f"LOCATION:{oof_location}",
                "PRIORITY:5",
                "SEQUENCE:0",
                "SUMMARY;LANGUAGE=de:Berufsschule",
                "TRANSP:OPAQUE",
                "X-MICROSOFT-CDO-BUSYSTATUS:OOF",
                "X-MICROSOFT-CDO-IMPORTANCE:1",
                "X-MICROSOFT-DISALLOW-COUNTER:FALSE",
                "X-MS-OLK-AUTOFILLLOCATION:FALSE",
                "X-MS-OLK-CONFTYPE:0",
                "END:VEVENT"
            ])

        ics_content.append("END:VCALENDAR")

        # Write file
        with open(file_path, 'w', encoding='utf8') as ics_file:
            ics_file.write("\n".join(ics_content))

        print(f"ICS-Datei für die Woche erstellt: {file_path}")

        # If you use a global variable to store the file path
        global global_file_path
        global_file_path = file_path
    else:
        print("Keine Stunden gefunden.")

def open_ics_with_default_app(ics_file_path):
    # Check if the .ics file exists
    if not os.path.exists(ics_file_path):
        print(f"Die Datei {ics_file_path} existiert nicht.")
        return
    
    # Open the .ics file using the default application (usually Outlook)
    try:
        subprocess.run(["start", ics_file_path], shell=True)
        print(f"Die .ics Datei {ics_file_path} wurde geöffnet.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
    
# Funktion, um den Beginn der Woche zu ermitteln
def get_start_of_week(date_str):
    
    if isinstance(date_str, datetime.datetime):
        date_str = date_str.strftime("%Y-%m-%d")  # Convert datetime to string
    
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    start_of_week = date - datetime.timedelta(days=date.weekday())  # Montag der angegebenen Woche
    return start_of_week.strftime("%Y-%m-%d")


def generate_sleek_session():
    # Get the current time in UTC format
    current_time = datetime.datetime.utcnow().isoformat() + "Z"
    
    # Create the dictionary with the 'init' timestamp
    sleek_session_dict = {"init": current_time}
    
    # Convert the dictionary to a string
    sleek_session_str = str(sleek_session_dict)
    
    # URL-encode the string
    sleek_session_encoded = urllib.parse.quote(sleek_session_str)
    
    # Return the generated __sleek_session cookie value
    return f"_sleek_session={sleek_session_encoded}"

def get_headers(tenant_id, schoolname, server, login_name):
    #print(schoolname)
    jsession_id, trace_id = get_cookies(server=server, loginName=login_name)
    sleek_session = generate_sleek_session()
    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'priority': 'u=1, i',
        'referer': f'https://{server}/WebUntis',
        'cookie': f'schoolname="_{schoolname}"; Tenant-Id="{tenant_id}"; schoolname="_{schoolname}"; Tenant-Id="{tenant_id}"; schoolname="_{schoolname}"; Tenant-Id="{tenant_id}"; traceId={trace_id}; JSESSIONID={jsession_id}; _sleek_session={sleek_session}',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'tenant-id': f'{tenant_id}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    return headers

def get_x_crsf_headers(tenant_id, schoolname, server, login_name):
    #print(schoolname)
    
    jsession_id, trace_id = get_cookies(server=server, loginName=login_name)
    sleek_session = generate_sleek_session()
    if debug_mode:
        print("TenantID: " + tenant_id)
        print("jsession: " + jsession_id)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'priority': 'u=1, i',
        'referer': f'https://{server}/WebUntis',
        'cookie': f'JSESSIONID={jsession_id}; schoolname="_{schoolname}"; Tenant-Id="{tenant_id}"; traceId={trace_id}; _sleek_session={sleek_session}',
        'referer': 'https://webuntis.com/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0'
    }
    return headers
def get_class_id_headers(tenant_id, schoolname, server, login_name):
    
    jsession_id = jsessionid #get_cookies(server=server, loginName=login_name)
    trace_id = traceid #get_cookies(server=server, loginName=login_name)
    sleek_session = generate_sleek_session()
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "anonymous-school": f"{login_name}",
        "cookie": f"c0261b8e8a54040ba4c7dca9e81e3a451e98f870; schoolname=\"_{schoolname}\"; Tenant-Id=\"{tenant_id}\"; traceId={trace_id}; JSESSIONID={jsession_id}; _sleek_session={sleek_session}",
        "priority": "u=1, i",
        "referer": f"https://{server}/timetable-new/class",
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
        #"cookie": f"c0261b8e8a54040ba4c7dca9e81e3a451e98f870; schoolname=\"_{schoolname}\"; Tenant-Id=\"{tenant_id}\"; traceId={trace_id}; JSESSIONID={jsession_id}; _sleek_session={sleek_session}",
        
    return headers


def get_x_crsf_token(server, loginName, school):
    url = f"https://{server}/WebUntis/?school={loginName}#/basic/login"
    headers = get_x_crsf_headers(tenant_id=school["tenantId"], schoolname=school["loginName"], server=school["server"], login_name=school["loginSchool"])
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_content = response.text
        with open("./file.txt", "w") as f:
            f.write(html_content)
        # Define the pattern to extract the CSRF token
        csrf_token_pattern = r'"csrfToken":\s*"([^"]+)"'

        # Search for the CSRF token using regex
        match = re.search(csrf_token_pattern, html_content)

        if match:
            csrf_token = match.group(1)
            if debug_mode:
                print(f"CSRF Token: {csrf_token}")
            return csrf_token
        else:
            print("CSRF Token not found")
    else:
        print(f"Failed to fetch page, status code: {response.status_code}")


def get_cookies(server, loginName):
    
    #school["loginName"]
    url = f"https://{server}/WebUntis/?school={loginName}"
    if debug_mode:
        print(url)
    headers = {
        "accept": "application/json, text/plain, */*",
        "referer": "https://webuntis.com/",
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    try:
        session = requests.Session()
        response = session.get(url, headers=headers)
        cookies = response.cookies.get_dict()
        jsessionid = cookies.get('JSESSIONID')
        traceid = cookies.get('traceId')

        if debug_mode:
            print(f"Cookies: {cookies}")
            print(f"JSESSIONID: {jsessionid}")
            print(f"traceId: {traceid}")

        return jsessionid, traceid
    except Exception as e:
        print(f"Error getting cookies: {e}")
        return None, None

def get_classes_from_text(school):
    server = school["server"]

    session = requests.Session()
    # API URL to get classes information
    api_url = f"https://{server}/WebUntis/api/rest/view/v1/timetable/filter?resourceType=CLASS&timetableType=STANDARD"
    response = requests.get(api_url, headers=get_class_id_headers(tenant_id=school["tenantId"], schoolname=school["loginName"], server=school["server"], login_name=school["loginSchool"]))
    data = response.json()
    #print(data)
    if response.status_code == 200:
        classes = data["classes"]
        #class_data = data["classes"]
        #print(class_data)
        previous_class_name = ""
        # Collect class information
        
        class_data = []
        for class_group in classes:
        #for class_group in class_data:
            class_info = {
                "id": class_group["class"]["id"],
                "shortName": class_group["class"]["shortName"],
                "longName": class_group["class"]["longName"],
                "displayName": class_group["class"]["displayName"]
            }
            class_data.append(class_info)
            current_class_name = class_info["displayName"]
            # Print class information
            if standard_klasse == "None"  or standard_klasse == "" or is_default_usage == False:
                print(f"""Anzeigename: {current_class_name}
                """)
                
        
        if standard_klasse == "None"or standard_klasse == "" or is_default_usage == False:
            class_short_name = input("Bitte geben Sie den Klassennamen (Kurzname) ein: ")
            if standard_klasse == "None" or standard_klasse == "":
                choiche = input("Soll der Klassennamen als Standard gespeichert werden? (Y/N):")
            if choiche.lower() == "y":
                update_config_env("Klasse", class_short_name)
                print("Standard Klassenname gespeichert.")
        else:
            class_short_name = standard_klasse.strip()
        # Search for class by 'shortName'
        matching_class = next((cls for cls in class_data if cls["shortName"] == class_short_name), None)
        if debug_mode:
            print(class_data)
        if matching_class:
            print(f"Alles klar. {matching_class['displayName']} wurde ausgewählt.")
            return matching_class["id"]
        else:
            print("Klassennamen ungültig oder nicht gefunden. Bitte versuchen Sie es erneut.")
            return None
    else:
        print(f"{data['errorCode']}: {data['errorMessage']}")
        return None

def get_schools(city):
    url = "https://mobile.webuntis.com/ms/schoolquery2"
    payload = '{"id":"wu_schulsuche-1736413279181","method":"searchSchool","params":[{"search":"' + city + '"}],"jsonrpc":"2.0"}'
    header = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://webuntis.com",
        "priority": "u=1, i",
        "referer": "https://webuntis.com/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    response = requests.post(url, headers=header, data=payload)
    response.raise_for_status()  # Wenn der Statuscode nicht 2xx ist, eine HTTPError auslösen
    json = response.json()
    schools = json["result"]["schools"]
    counter = 0
    school_data = []
    for school in schools:
        if debug_mode:
            print(school)
        login_name = school["loginName"].lower()
        encoded_bytes = base64.b64encode(login_name.encode('utf-8'))
        login_base64 = encoded_bytes.decode('utf-8')

        school_data.append({
            "displayName": school["displayName"],
            "address": school["address"],
            "serverUrl": school["serverUrl"],
            "tenantId": school["tenantId"],
            "server": school["server"],
            "loginName": login_base64,
            "loginSchool": school["loginName"]
        })
        school_data[counter]["displayName"]
        if standard_schulnummer == "None" or standard_schulnummer == "" or is_default_usage == False:
            print(f"""
                Nr.{counter}
                Anzeigename: {school_data[counter]["displayName"]}
                Addresse: {school_data[counter]["address"]}
                Server: {school_data[counter]["server"]}
                Tenant ID: {school_data[counter]["tenantId"]}

            """)
        #print("Server URL: " + school_urls[counter])
        counter += 1
    if standard_schulnummer == "None"  or standard_schulnummer == "" or is_default_usage == False:
        school_number = int(input("Bitte geben sie die Schulnummer ein: "))
        if standard_schulnummer == "None" or standard_schulnummer == "":
            choice = input("Soll diese Schulnummer als Standard gespeichert werden? (Y/N): ")
        if choice.lower() == "y":
            update_config_env('Schulnummer', school_number)
            print("Standard Schulnummer gespeichert.")
        #eingaben überprüfen
        if 0 <= school_number < counter:
            print(f"Alles klar. {school_data[school_number]['displayName']} wurde ausgewählt.")
            return school_data[school_number]
        else:
            print("Schulnummer ungültig. Bitte versuchen Sie es erneut.")
            return None
        # except ValueError:
        #     print("Keine gültige Zahl. Bitte versuchen Sie es erneut.")
        #     return None
    else:
        print(f"Alles klar. {school_data[int(standard_schulnummer)]['displayName']} wurde aus den Default Settings ausgewählt")
        return school_data[int(standard_schulnummer)]
        
    

# Funktion zum Abrufen der Stundenplandaten von der API
def fetch_timetable_data(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Wenn der Statuscode nicht 2xx ist, eine HTTPError auslösen
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Anfrage: {e}")
        return None
    except ValueError as e:
        print(f"Fehler beim Parsen von JSON: {e}")
        return None

# Funktion zum Abrufen von Schultagen, Fächern und Lehrern aus den Stundenplandaten
def get_school_days_subjects_teachers(json_data):
    # Mapping von Datum auf Wochentag
    date_to_day = {
        0: 'Montag',
        1: 'Dienstag',
        2: 'Mittwoch',
        3: 'Donnerstag',
        4: 'Freitag',
        5: 'Samstag',
        6: 'Sonntag',
    }
    # Hole die elementPeriods aus der Antwort
    element_periods = json_data['data']['result']['data']['elementPeriods']
    if element_periods is None:
        element_periods = json_data['data']['result']['data']['elements']
    # Hole die elementGroups aus der Antwort
    with open("json_output.txt","w") as file:
        file.write(json.dumps(json_data, indent=4))

    #print(element_periods)l
    school_days_subjects_teachers = []

    # Iteriere über jede Stundenzeile für das jeweilige Element
    for element_id, periods in element_periods.items():
        print()
        for period in periods:
            
            date = period['date']
            # Konvertiere das Datum (YYYYMMDD) in ein datetime-Objekt
            date_str = str(date)
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:])
            lesson_date = datetime.date(year, month, day)

            # Bestimme den Wochentag (0=Montag, 1=Dienstag, ..., 6=Sonntag)
            day_of_week = lesson_date.weekday()

            # Mappe die Wochentagsnummer auf den Wochentagnamen
            school_day = date_to_day[day_of_week]

            # Extrahiere das Fach und den Lehrer
            lesson_code = period.get('studentGroup', '')
            #print(lesson_code)
            if '_' in lesson_code:
                parts = lesson_code.split('_', 1)
                subject = parts[0]  # Alles vor dem ersten '_'
                teacher = parts[1] if len(parts) > 1 else 'Unbekannt'  # Alles nach dem ersten '_'
                teacher = teacher.split("_")[1]
            else:
                subject = lesson_code
                teacher = 'Unbekannt'  # Falls keine Lehrerinformation vorhanden ist
            
            cellState = period.get("cellState", '')
            is_exam = False
            is_additional = False
            if debug_mode:
                print(f"{subject} : {cellState}")
            if cellState == "EXAM":
                is_exam = True
            elif cellState == "ADDITIONAL":
                is_additional = True
            else:
                is_additional = False
                is_exam = False
                #print("Set is_additional to: ", is_additional)

            # Bestimme die Stunde und Minute, um die korrekte Startzeit zu berechnen
            start_time = period.get('startTime', 0)  
            end_time = period.get('endTime', 0)

            # Umwandlung der startTime und endTime in Stunden und Minuten
            start_hour = start_time // 100
            start_minute = start_time % 100
            end_hour = end_time // 100
            end_minute = end_time % 100
            #if is_additional is None or is_additional == "":
                #print(is_additional)
            # Füge den Schultag, das Datum, das Fach, den Lehrer und die Uhrzeiten zur Liste hinzu
            school_days_subjects_teachers.append({
                "lesson_date": lesson_date,
                "school_day": school_day,
                "subject": subject,
                "teacher": teacher,
                "is_exam": is_exam,
                "is_additional": is_additional,
                "start_time": datetime.time(start_hour, start_minute),
                "end_time": datetime.time(end_hour, end_minute),
            })

    return school_days_subjects_teachers

def main():
    
    while True:
        display_main_menu()
        choice = input("Please select an option: ")
        
        if choice == '1':
            fetch_timetable()
        
        elif choice == '2':
            settings_menu()
        
        elif choice == '3':
            print("Exiting WebLook. See you soon!")
            break
        
        else:
            print("Invalid choice, please try again.")
            input("\nPress Enter to return to the menu...")
        

if __name__ == "__main__":
    main()
