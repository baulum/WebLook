import sys
import os
import re
import json
import base64
import datetime
import subprocess
import urllib.parse
import requests

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QTextCursor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QTextEdit, QSpinBox,
    QMessageBox, QScrollArea, QFrame, QStyle, QGridLayout, QSizePolicy, QComboBox, QCheckBox, QFileDialog
)


# -----------------------------
# Original Helper Functions
# (Modified to remove console input, replaced with PyQt usage)
# -----------------------------

def read_config_env(file_path='config.env'):
    config = {}
    script_directory = os.path.dirname(os.path.abspath(sys.argv[0])) 
    default_path = os.path.join(script_directory, "kalender")

    default_settings = {
        "Name": "None",
        "Email": "None",
        "Betrieb": "None",
        "Stadt/Adresse": "None",
        "Klasse": "None",
        "Schulnummer": "None",
        "Wochen": "4",
        "Dateipfad": default_path,	
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
        print(f"An error occurred reading config.env: {e}")
    return config

def update_config_env(key, value, file_path='config.env'):
    config = read_config_env(file_path)
    config[key] = str(value)
    with open(file_path, 'w') as file:
        for k, v in config.items():
            file.write(f"{k}={v}\n")

def generate_sleek_session():
    current_time = datetime.datetime.utcnow().isoformat() + "Z"
    sleek_session_dict = {"init": current_time}
    sleek_session_str = str(sleek_session_dict)
    sleek_session_encoded = urllib.parse.quote(sleek_session_str)
    return f"_sleek_session={sleek_session_encoded}"

def get_cookies(server, loginName, debug_mode=False):
    url = f"https://{server}/WebUntis/?school={loginName}"
    headers = {
        "accept": "application/json, text/plain, */*",
        "referer": "https://webuntis.com/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    try:
        session = requests.Session()
        response = session.get(url, headers=headers)
        cookies = response.cookies.get_dict()
        jsessionid = cookies.get('JSESSIONID')
        traceid = cookies.get('traceId')
        if debug_mode:
            print("Cookies:", cookies)
        return jsessionid, traceid
    except Exception as e:
        print(f"Error getting cookies: {e}")
        return None, None

def get_headers(tenant_id, schoolname, server, login_name, jsession_id, trace_id):
    sleek_session = generate_sleek_session()
    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'priority': 'u=1, i',
        'referer': f'https://{server}/WebUntis',
        'cookie': (
            f'schoolname="_{schoolname}"; Tenant-Id="{tenant_id}"; traceId={trace_id}; '
            f'JSESSIONID={jsession_id}; _sleek_session={sleek_session}'
        ),
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'tenant-id': f'{tenant_id}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    return headers

def get_class_id_headers(tenant_id, schoolname, server, login_name, jsession_id, trace_id):
    sleek_session = generate_sleek_session()
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "anonymous-school": f"{login_name}",
        "cookie": (
            f'schoolname="_{schoolname}"; Tenant-Id="{tenant_id}"; traceId={trace_id}; '
            f'JSESSIONID={jsession_id}; _sleek_session={sleek_session}'
        ),
        "priority": "u=1, i",
        "referer": f"https://{server}/timetable-new/class",
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    return headers

def get_start_of_week(date_str):
    if isinstance(date_str, datetime.datetime):
        date_str = date_str.strftime("%Y-%m-%d")
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    start_of_week = date - datetime.timedelta(days=date.weekday())
    return start_of_week.strftime("%Y-%m-%d")

def fetch_timetable_data(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Anfrage: {e}")
        return None
    except ValueError as e:
        print(f"Fehler beim Parsen von JSON: {e}")
        return None

def get_school_days_subjects_teachers(json_data, debug_mode=False):
    date_to_day = {
        0: 'Montag',
        1: 'Dienstag',
        2: 'Mittwoch',
        3: 'Donnerstag',
        4: 'Freitag',
        5: 'Samstag',
        6: 'Sonntag',
    }
    element_periods = json_data['data']['result']['data'].get('elementPeriods')
    if element_periods is None:
        element_periods = json_data['data']['result']['data'].get('elements', {})

    school_days_subjects_teachers = []

    for _, periods in element_periods.items():
        for period in periods:
            date = period['date']
            date_str = str(date)
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:])
            lesson_date = datetime.date(year, month, day)
            day_of_week = lesson_date.weekday()
            school_day = date_to_day[day_of_week]

            lesson_code = period.get('studentGroup', '')
            if '_' in lesson_code:
                parts = lesson_code.split('_', 1)
                subject = parts[0]
                teacher_part = parts[1] if len(parts) > 1 else 'Unbekannt'
                teacher_parts = teacher_part.split("_")
                teacher = teacher_parts[-1] if len(teacher_parts) > 1 else teacher_part
            else:
                subject = lesson_code
                teacher = 'Unbekannt'

            cellState = period.get("cellState", '')
            is_exam = (cellState == "EXAM")
            is_additional = (cellState == "ADDITIONAL")

            start_time = period.get('startTime', 0)
            end_time = period.get('endTime', 0)
            start_hour = start_time // 100
            start_minute = start_time % 100
            end_hour = end_time // 100
            end_minute = end_time % 100

            if debug_mode:
                print(f"Processed: {subject}, cellState={cellState}")

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

def get_next_workday(date_obj):
    next_day = date_obj + datetime.timedelta(days=1)
    while next_day.weekday() > 4:  # 5=Sat, 6=Sun
        next_day += datetime.timedelta(days=1)
    return next_day

# def create_ics_file_for_week(school_days_subjects_teachers, schoolname, output_dir="kalender", school_data=None,
#     name="", betrieb="", email="", debug_log_func=print):
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#     #print(school_data)

#     schoolname = school_data.get('loginSchool', "Schule").lower()
#     sorted_lessons = sorted(school_days_subjects_teachers, key=lambda x: (x["lesson_date"], x["start_time"]))
#     filename = f"{schoolname}_stundenplan_woche.ics"
#     file_path = os.path.join(output_dir, filename)
#     debug_log_func(f"Anzahl gefundener Stunden: {len(sorted_lessons)}")

#     if len(sorted_lessons) > 0:
#           # could be user-chosen in GUI if desired
#         ics_content = [
#             "BEGIN:VCALENDAR",
#             "VERSION:2.0",
#             "CALSCALE:GREGORIAN"
#         ]

#         earliest_date = min(lesson["lesson_date"] for lesson in sorted_lessons)
#         latest_date = max(lesson["lesson_date"] for lesson in sorted_lessons)
#         start_date_ics = earliest_date.strftime("%Y%m%d")
#         end_date_ics = (latest_date + datetime.timedelta(days=1)).strftime("%Y%m%d")
#         next_workday_dt = get_next_workday(latest_date)
#         next_workday_str = next_workday_dt.strftime("%d.%m.%Y")
#         first_lesson_dt = datetime.datetime.combine(sorted_lessons[0]["lesson_date"], sorted_lessons[0]["start_time"])
#         creation_date = first_lesson_dt.strftime("%Y%m%dT%H%M%S")

#         for lesson in sorted_lessons:
#             event_start = datetime.datetime.combine(lesson["lesson_date"], lesson["start_time"]).strftime("%Y%m%dT%H%M%S")
#             event_end = datetime.datetime.combine(lesson["lesson_date"], lesson["end_time"]).strftime("%Y%m%dT%H%M%S")
#             event_description = f"{lesson['subject']} - {lesson['teacher']}"

#             if lesson["is_exam"]:
#                 summary_line = f"Prüfung {lesson['subject']}"
#                 description_line = f"{event_description} Prüfung!"
#             elif lesson["is_additional"]:
#                 summary_line = f"Ersatzstunde {lesson['subject']}"
#                 description_line = f"{event_description} Ersatz!"
#             else:
#                 summary_line = lesson["subject"]
#                 description_line = event_description

#             ics_content.extend([
#                 "BEGIN:VEVENT",
#                 f"DTSTART:{event_start}",
#                 f"DTEND:{event_end}",
#                 f"SUMMARY:{summary_line}",
#                 f"DESCRIPTION:{description_line}",
#                 f"LOCATION:{lesson['teacher']}",
#                 "STATUS:CONFIRMED",
#                 "END:VEVENT"
#             ])

#         # OOF event if create_oof is True
#         if create_oof:
#             display_name = school_data.get("displayName", "Schule") if school_data else "Schule"
#             address = school_data.get("address", "Unbekannte Adresse") if school_data else "Unbekannte Adresse"
#             oof_description = (
#                 "Sehr geehrte Damen und Herren,\\n\\n"
#                 f"leider bin ich derzeit außer Haus. Sie können mich ab dem {next_workday_str} "
#                 "wieder erreichen.\\n\\n"
#                 f"Viele Grüße,\\n\\n{name}\\n{betrieb}\\n\\n{email}\\n\\n"
#             )

#             debug_log_func(f"""Alles klar. Das ist die Out Of Office Notiz: 
# {oof_description}""")

#             oof_location = f"{display_name} ({address})"
#             ics_content.extend([
#                 "BEGIN:VEVENT",
#                 "CLASS:PUBLIC",
#                 f"CREATED:{creation_date}",
#                 f"DESCRIPTION:{oof_description}",
#                 f"DTEND;VALUE=DATE:{end_date_ics}",
#                 f"DTSTART;VALUE=DATE:{start_date_ics}",
#                 f"LOCATION:{oof_location}",
#                 "PRIORITY:5",
#                 "SEQUENCE:0",
#                 "SUMMARY;LANGUAGE=de:Berufsschule",
#                 "TRANSP:OPAQUE",
#                 "X-MICROSOFT-CDO-BUSYSTATUS:OOF",
#                 "X-MICROSOFT-CDO-IMPORTANCE:1",
#                 "X-MICROSOFT-CDO-DISALLOW-COUNTER:FALSE",
#                 "X-MS-OLK-AUTOFILLLOCATION:FALSE",
#                 "X-MS-OLK-CONFTYPE:0",
#                 "END:VEVENT"
#             ])

#         ics_content.append("END:VCALENDAR")

#         with open(file_path, 'w', encoding='utf8') as ics_file:
#             ics_file.write("\n".join(ics_content))

#         debug_log_func(f"ICS-Datei erstellt: {file_path}")
#         return file_path
#     else:
#         debug_log_func("Keine Stunden gefunden.")
#         return None


def create_ics_file_for_week(school_days_subjects_teachers, schoolname, output_dir="kalender", school_data=None,
        name="", betrieb="", email="", debug_log_func=print):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Sort lessons by (date, start_time)
    sorted_lessons = sorted(
        school_days_subjects_teachers, 
        key=lambda x: (x["lesson_date"], x["start_time"])
    )
    schoolname = school_data.get('loginSchool', "Schule")
    filename = f"{schoolname.lower()}_stundenplan_woche.ics"
    file_path = os.path.join(output_dir, filename)
    debug_log_func(f"Anzahl gefundener Stunden: {len(sorted_lessons)}")

    if len(sorted_lessons) == 0:
        debug_log_func("Keine Stunden gefunden.")
        return None
    # ----------------------------------------------------------------
    # 1) Build the ICS header
    # ----------------------------------------------------------------
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN"
    ]

    # For lesson VEVENT creation below
    first_lesson_dt = datetime.datetime.combine(
        sorted_lessons[0]["lesson_date"],
        sorted_lessons[0]["start_time"]
    )
    creation_date = first_lesson_dt.strftime("%Y%m%dT%H%M%S")

    # ----------------------------------------------------------------
    # 2) Create VEVENTS for *all lessons*
    # ----------------------------------------------------------------

    for lesson in sorted_lessons:
        event_start = datetime.datetime.combine(
            lesson["lesson_date"], 
            lesson["start_time"]
        ).strftime("%Y%m%dT%H%M%S")

        event_end = datetime.datetime.combine(
            lesson["lesson_date"], 
            lesson["end_time"]
        ).strftime("%Y%m%dT%H%M%S")

        event_description = f"{lesson['subject']} - {lesson['teacher']}"

        # Decide summary and description lines
        if lesson["is_exam"]:
            summary_line     = f"Prüfung {lesson['subject']}"
            description_line = f"{event_description} Prüfung!"
        elif lesson["is_additional"]:
            summary_line     = f"Ersatzstunde {lesson['subject']}"
            description_line = f"{event_description} Ersatz!"
        else:
            summary_line     = lesson["subject"]
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

    # ----------------------------------------------------------------
    # 3) Identify consecutive blocks of days for separate OOF events
    # ----------------------------------------------------------------
    # Gather all unique dates (ignore times).
    unique_days = sorted(set(lesson["lesson_date"] for lesson in sorted_lessons))

    if create_oof and unique_days:
        # Group those days into consecutive blocks
        blocks = []
        current_block = [unique_days[0]]
        for day in unique_days[1:]:
            # If difference is more than 1 day, start a new block
            if (day - current_block[-1]).days > 1:
                blocks.append(current_block)
                current_block = [day]
            else:
                current_block.append(day)
        # Append the final block
        blocks.append(current_block)

        # Access info from school_data if needed
        display_name = school_data.get("displayName", "Schule") if school_data else "Schule"
        address      = school_data.get("address", "Unbekannte Adresse") if school_data else "Unbekannte Adresse"

        # ----------------------------------------------------------------
        # 4) Create an OOF VEVENT for *each* block
        # ----------------------------------------------------------------
        for block in blocks:
            block_earliest = min(block)
            block_latest   = max(block)

            # ICS for a full-day event goes until the next day
            start_date_ics = block_earliest.strftime("%Y%m%d")
            end_date_ics   = (block_latest + datetime.timedelta(days=1)).strftime("%Y%m%d")

            # Next workday (if you use it in the message)
            next_workday_dt = get_next_workday(block_latest)
            next_workday_str = next_workday_dt.strftime("%d.%m.%Y")

            # Build the OOF description
            oof_description = (
                "Sehr geehrte Damen und Herren,\\n\\n"
                f"leider bin ich derzeit außer Haus. Sie können mich ab dem {next_workday_str} "
                "wieder erreichen.\\n\\n"
                f"Viele Grüße,\\n\\n{name}\\n{betrieb}\\n\\n{email}\\n\\n"
            )
            
            debug_log_func(
                f"OOF-Block: {block_earliest} → {block_latest} | "
                f"Nächster Arbeitstag: {next_workday_str}"
                f"""
                OOF-Notiz: {oof_description.strip()}"""
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
                "X-MICROSOFT-CDO-DISALLOW-COUNTER:FALSE",
                "X-MS-OLK-AUTOFILLLOCATION:FALSE",
                "X-MS-OLK-CONFTYPE:0",
                "END:VEVENT"
            ])

    # ----------------------------------------------------------------
    # Finalize
    # ----------------------------------------------------------------
    ics_content.append("END:VCALENDAR")

    with open(file_path, 'w', encoding='utf8') as ics_file:
        ics_file.write("\n".join(ics_content))

    debug_log_func(f"ICS-Datei erstellt: {file_path}")
    return file_path

def open_ics_with_default_app(ics_file_path):
    if not os.path.exists(ics_file_path):
        print(f"Die Datei {ics_file_path} existiert nicht.")
        return
    try:
        if os.name == "nt":
            os.startfile(ics_file_path)
        else:
            subprocess.run(["open", ics_file_path])
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

def get_schools(city, debug_mode=False):
    url = "https://mobile.webuntis.com/ms/schoolquery2"
    payload = (
        '{"id":"wu_schulsuche-1736413279181","method":"searchSchool","params":[{"search":"'
        + city
        + '"}],"jsonrpc":"2.0"}'
    )
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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    response = requests.post(url, headers=header, data=payload)
    response.raise_for_status()
    json_resp = response.json()
    schools = json_resp["result"]["schools"]
    
    school_data = []
    for s in schools:
        if debug_mode:
            print("Found school:", s)
        login_name = s["loginName"].lower()
        encoded_bytes = base64.b64encode(login_name.encode('utf-8'))
        login_base64 = encoded_bytes.decode('utf-8')
        school_data.append({
            "displayName": s["displayName"],
            "address": s["address"],
            "serverUrl": s["serverUrl"],
            "tenantId": s["tenantId"],
            "server": s["server"],
            "loginName": login_base64,
            "loginSchool": s["loginName"]
        })
    return school_data

def get_classes(server, school, jsession_id, trace_id, debug_mode=False):
    api_url = f"https://{server}/WebUntis/api/rest/view/v1/timetable/filter?resourceType=CLASS&timetableType=STANDARD"
    response = requests.get(
        api_url,
        headers=get_class_id_headers(
            tenant_id=school["tenantId"],
            schoolname=school["loginName"],
            server=school["server"],
            login_name=school["loginSchool"],
            jsession_id=jsession_id,
            trace_id=trace_id
        )
    )
    if response.status_code != 200:
        return None, response.text
    data = response.json()
    classes = data["classes"]
    class_data = []
    for c in classes:
        cinfo = c["class"]
        class_data.append({
            "id": cinfo["id"],
            "shortName": cinfo["shortName"],
            "longName": cinfo["longName"],
            "displayName": cinfo["displayName"]
        })
    return class_data, None

def fetch_data_for_next_weeks(
    school,
    class_id,
    week_count,
    headers,
    debug_mode=False,
    debug_log_func=print
):
    current_date = datetime.datetime.now()
    start_of_current_week = get_start_of_week(current_date)
    weeks_to_fetch = [start_of_current_week]
    for i in range(1, week_count):
        date_plus_weeks = current_date + datetime.timedelta(weeks=i)
        start_of_next_week = get_start_of_week(date_plus_weeks)
        weeks_to_fetch.append(start_of_next_week)

    if debug_mode:
        debug_log_func(f"Weeks to fetch: {weeks_to_fetch}")

    all_school_days = []
    server = school["server"]

    for week_start in weeks_to_fetch:
        api_url = (
            f"https://{server}/WebUntis/api/public/timetable/weekly/data"
            f"?elementType=1&elementId={class_id}&date={week_start}&formatId=2&filter.departmentId=-1"
        )
        debug_log_func(f"Hole Daten für Woche: {week_start}")
        timetable_data = fetch_timetable_data(api_url, headers)
        if timetable_data:
            results = get_school_days_subjects_teachers(timetable_data, debug_mode)
            all_school_days.extend(results)

    return all_school_days


# -----------------------------
# PyQt5 GUI Implementation
# -----------------------------


class MainWindow(QMainWindow):
    """A QMainWindow with a sidebar and a central stacked widget
       to display different pages (Main Menu, Settings, Fetch Timetable)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebLook - Number one WebUntis to Outlook Tool!")
        self.resize(1000, 600)

        # Load config
        self.config_data = read_config_env()

        # Central widget with a horizontal layout: [Sidebar | StackedWidget]
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # Create sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar, 1)

        # Create stacked widget
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 5)

        # Create pages
        self.main_menu_page = MainMenuPage(self.config_data, self)
        self.fetch_page = FetchTimetablePage(self.config_data, self)
        self.settings_page = SettingsPage(self.config_data, self)
        

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_menu_page)   # index 0
        # Changed the order of the nav bar to main-->fetch-->settings
        

        self.stacked_widget.addWidget(self.settings_page)    # index 1

        self.stacked_widget.addWidget(self.fetch_page)       # index 2
        

        # Set central widget
        self.setCentralWidget(central_widget)

        # Apply a style sheet for a modern look
        self.setStyleSheet(self.load_stylesheet())

    def create_sidebar(self):
        """Create a vertical sidebar with nav buttons."""
        frame = QFrame()
        frame.setObjectName("sidebar")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(10)

        # Title or big label
        brand_label = QLabel("WebLook")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        brand_label.setFont(font)
        brand_label.setStyleSheet("color: white; margin:20px;")
        layout.addWidget(brand_label, 0, Qt.AlignHCenter)

        # Nav Buttons
        btn_main_menu = QPushButton("Start Menü")
        btn_main_menu.setIcon(QIcon("./assets/icons/inverted/main_menu_inverted.png"))
        btn_main_menu.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(btn_main_menu)

        btn_fetch = QPushButton("Stundenplan")
        btn_fetch.setIcon(QIcon("./assets/icons/inverted/timetable_inverted.png"))
        btn_fetch.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        layout.addWidget(btn_fetch)

        btn_settings = QPushButton("Einstellungen")
        btn_settings.setIcon(QIcon("./assets/icons/inverted/setting_inverted.png"))
        btn_settings.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(btn_settings)

        layout.addStretch()  # push everything up

        return frame

    def load_stylesheet(self):
        return """
        /* Main Window background */
        QMainWindow {
            background-color: #2B2B2B;
        }

        /* Sidebar remains #333, as before */
        #sidebar {
            background-color: #333;
        }

        /* Style the navigation buttons on sidebar */
        QPushButton {
            background-color: #444;
            color: white;
            border: none;
            padding: 10px;
            text-align: left;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #555;
        }

        QMessageBox {
            background-color: #333;
            color: #ddd;
            text-align: center;
        }

        /* Make all labels text a light color */
        QLabel {
            color: #ddd;
            font-size: 14px;
        }

        /* Ensure the stacked widget / central pages also have a dark background */
        QStackedWidget {
            background-color: #2B2B2B;
        }

        /* Specifically style your SettingsPage (or any other "central page") */
        #settingsPage {
            background-color: #2B2B2B; /* same dark color */
        }

        QCheckBox {
            background-color: #555;
            color: #fff;
            padding: 5px;
            font-size: 14px;
            min-height: 23px;
        }

        /* Dark background for scroll area contents */
        QScrollArea {
            background: #2B2B2B;
        }
        QScrollArea QWidget {
            background: #2B2B2B;
            color: #ddd;
        }

        /* Spinbox, LineEdits, TextEdits, etc. */
        QSpinBox {
            background-color: #555;
            color: #fff;
            /*padding: 5px;*/
            font-size: 14px;
            min-height: 23px;
        }
        QLineEdit {
            background-color: #555;
            color: #fff;
            border: 1px solid #777;
            padding: 5px;
        }
        QTextEdit {
            background-color: #222;
            color: #ccc;
            border: 1px solid #555;
            font-size: 13px;
        }
         /* ComboBox: dunkles Design, selbe Höhe wie Buttons */
        QComboBox {
            background-color: #555;
            color: #fff;
            border: 1px solid #777;
            padding: 5px;
            font-size: 14px;
            min-height: 23px; /* Anpassen, falls der Button höher/niedriger ist */
        }
        /* Drop-down-Button innen in der ComboBox */
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px; /* Breite des Pfeil-Bereichs */
            border-left: 1px solid #777;
            background-color: #444;
        }
        /* Das ausklappbare Menü */
        QComboBox QAbstractItemView {
            background-color: #2B2B2B;
            color: #fff;
            selection-background-color: #555;
            selection-color: #fff;
        }
        """



class MainMenuPage(QWidget):
    """Represents the main menu page."""
    def __init__(self, config_data, parent=None):
        super().__init__(parent)
        self.setObjectName("mainMenuPage")
        self.config_data = config_data
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Willkommen zu WebLook - Hauptmenü")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title, 0, Qt.AlignTop)

        desc = QLabel("")
        layout.addWidget(desc)

        # Add a placeholder label or something
        info = QLabel("Nutzen Sie die Seitenleiste, um zu navigieren:\n\n1) Stundenplan abrufen\n2) Einstellungen\n3) Schließen Sie das Fenster, um das Programm zu beenden")
        layout.addWidget(info)
        layout.addStretch()


class SettingsPage(QWidget):
    """Represents the settings page. Allows editing config.env values."""
    def __init__(self, config_data, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self.config_data = config_data

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        # Container widget inside scroll
        container = QWidget()
        scroll.setWidget(container)
        grid = QGridLayout(container)
        grid.setSpacing(10)
        container.setLayout(grid)

        title = QLabel("Einstellungen")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        grid.addWidget(title, 0, 0, 1, 2)

        self.entries = {}
        row = 1
        settings_keys = [
            "Name", "Email", "Betrieb",
            "Stadt/Adresse", "Klasse",
            "Schulnummer", "Wochen", "Dateipfad", "Debugging"
        ]
        for key in settings_keys:
            label = QLabel(key)
            label.setMinimumWidth(120)
            grid.addWidget(label, row, 0, 1, 1)
            if not key == "Debugging":
                line_edit = QLineEdit()
                val = self.config_data.get(key, "")
                line_edit.setText(val)
                self.entries[key] = line_edit
                grid.addWidget(line_edit, row, 1, 1, 1)
            if key == "Dateipfad":
                browse_btn = QPushButton()
                browse_btn.setIcon(QIcon("./assets/icons/inverted/browse_inverted.png"))
                browse_btn.clicked.connect(self.getFolder)
                grid.addWidget(browse_btn, row, 2, 1, 1)

            if key == "Debugging":
                self.check_box = QCheckBox()
                #self.check_box.setText("Debugging ein/ausschalten")
                val = self.config_data.get(key, False)
                if val.lower() == "true":
                    self.check_box.setChecked(True)
                    self.check_box.setText("Debugging ist eingeschaltet")
                else:
                    self.check_box.setChecked(False)
                    self.check_box.setText("Debugging ist ausgeschaltet")
                #self.entries[key] = self.check_box
                grid.addWidget(self.check_box, row, 1, 1, 1)
            row += 1
        self.check_box.clicked.connect(self.change_debug)
        btn_save = QPushButton("Speichern")
        btn_save.setIcon(QIcon("./assets/icons/inverted/save_inverted.png"))
        btn_save.clicked.connect(self.save_settings)
        grid.addWidget(btn_save, row, 0, 1, 2)
        self.refresh()

    def change_debug(self, checked):
        if self.check_box.isChecked():
            update_config_env("Debugging", "True")
            self.check_box.setText("Debugging ist eingeschaltet")
            self.refresh()
            print("Debugging changed to True")
        else:
            update_config_env("Debugging", "False")
            self.check_box.setText("Debugging ist ausgeschaltet")
            self.refresh()
            print("Debugging changed to False")
    def getFolder(self):
        save_file_path = str(QFileDialog.getExistingDirectory(None, "Ordner auswählen", directory=self.config_data["Dateipfad"]))
        if save_file_path:
            update_config_env("Dateipfad", save_file_path)
            self.refresh() # Refresh the entries form config.env
            QMessageBox.information(self, "Erfolgreich", "Der Standard Speicherort wurde geändert")

        #print(file_path)
    def refresh(self):
        """Refresh entries with latest config."""
        self.config_data = read_config_env()
        for key, line_edit in self.entries.items():
            val = self.config_data.get(key, "")
            line_edit.setText(val)

    def save_settings(self):
        for key, line_edit in self.entries.items():
            new_val = line_edit.text().strip()
            update_config_env(key, new_val)
            read_config_env(file_path="./config.env")
        QMessageBox.information(self, "Einstellungen", "Die Einstellungen wurden erfolgreich gespeichert!")
        self.refresh()


class FetchTimetablePage(QWidget):
    def __init__(self, config_data, parent=None):
        super().__init__(parent)
        self.config_data = config_data

        layout = QVBoxLayout(self)
        title = QLabel("Stundenplan abrufen")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # 1) Checkbox bzw. Button zum Umschalten Defaults
        self.use_defaults = False
        self.toggle_defaults_button = QPushButton("Nutze KEINE Defaults (klicken zum Umschalten)")
        self.toggle_defaults_button.clicked.connect(self.toggle_defaults)
        layout.addWidget(self.toggle_defaults_button)

        # 2) Stadt-Eingabe
        city_layout = QHBoxLayout()
        city_label = QLabel("Stadt/Adresse:")
        city_label.setToolTip("Wenn die Eingabe der Stadt zu Fehlern führt geben sie die Adresse der Schule ein(Ohne PLZ und Ort)")
        self.city_edit = QLineEdit()
        self.city_edit.setToolTip("Wenn die Eingabe der Stadt zu Fehlern führt geben sie die Adresse der Schule ein(Ohne PLZ und Ort)")
        city_layout.addWidget(city_label)
        city_layout.addWidget(self.city_edit)
        layout.addLayout(city_layout)

        # 3) Button „Schulen laden“, sowie ComboBox für Schulnummer
        load_schools_layout = QHBoxLayout()
        self.load_schools_btn = QPushButton("Schulen laden")
        self.load_schools_btn.setToolTip("Lädt die Schulen in die Box rechts neben an. Bitte aus der Liste eine Schule auswählen")
        self.load_schools_btn.clicked.connect(self.on_load_schools_clicked)
        load_schools_layout.addWidget(self.load_schools_btn)

        self.schools_combo = QComboBox()
        # Vorerst leer, füllen wir dynamisch
        load_schools_layout.addWidget(self.schools_combo)
        layout.addLayout(load_schools_layout)

        # 4) Klassennamen-Eingabe
        class_layout = QHBoxLayout()
        self.class_label = QLabel("Klasse (Kurzname):")
        self.class_edit = QLineEdit()
        class_layout.addWidget(self.class_label)
        class_layout.addWidget(self.class_edit)
        layout.addLayout(class_layout)

        # 5) Wochen
        weeks_layout = QHBoxLayout()
        weeks_label = QLabel("Anzahl Wochen (1-15):")
        self.weeks_spin = QSpinBox()
        self.weeks_spin.setRange(1, 15)
        self.weeks_spin.setValue(1)
        weeks_layout.addWidget(weeks_label)
        weeks_layout.addWidget(self.weeks_spin)
        layout.addLayout(weeks_layout)

        # 6) Create Out Of Office CheckBox
        create_oof_layout = QHBoxLayout()
        self.create_oof_box = QCheckBox("Out Of Office")
        create_oof_label = QLabel("Out Of Office Notiz erstellen?: ")
        create_oof_layout.addWidget(create_oof_label)
        create_oof_layout.addWidget(self.create_oof_box)
        layout.addLayout(create_oof_layout)

        #creat_oof_layout.setText("Out Of Office Notiz erstellen?")

        # 6) Fetch Button
        self.fetch_btn = QPushButton("Stundenplan abrufen!")
        self.fetch_btn.clicked.connect(self.run_fetch)
        layout.addWidget(self.fetch_btn)

        # 7) Log Text
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.setLayout(layout)
        self.refresh()

    def toggle_defaults(self):
        self.use_defaults = not self.use_defaults
        if self.use_defaults:
            self.refresh()
            self.toggle_defaults_button.setText("Nutze DEFAULTS (klicken zum Umschalten)")
            self.city_edit.setText(self.config_data.get("Stadt/Adresse", ""))
            self.class_edit.setText(self.config_data.get("Klasse", ""))
            self.weeks_spin.setValue(int(self.config_data.get("Wochen", "1")))
            self.load_schools_btn.click()
        else:
            self.refresh()
            self.toggle_defaults_button.setText("Nutze KEINE Defaults (klicken zum Umschalten)")
            self.city_edit.clear()
            self.class_edit.clear()
            self.weeks_spin.setValue(1)
            self.schools_combo.clear()

    def on_load_schools_clicked(self):
        """Lädt Schulen der eingegebenen Stadt und füllt die ComboBox."""
        self.log_text.clear()
        debug_mode = (self.config_data.get("Debugging", "False").lower() == "true")
        
        # Falls man Defaults nutzen möchte, Laden der Standardstadt etc.
        if self.use_defaults:
            city = self.config_data.get("Stadt/Adresse", "None")
            if not city or city == "None":
                QMessageBox.warning(self, "Keine Default-Stadt", "Bitte Stadt/Adresse im config.env setzen oder Defaults deaktivieren.")
                return
        else:
            city = self.city_edit.text().strip()
            if not city:
                QMessageBox.warning(self, "Stadt fehlt", "Bitte geben Sie eine Stadt ein.")
                return

        self.debug_log(f"Suche Schulen für Stadt: {city}")
        try:
            schools = get_schools(city, debug_mode)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Schulen: {str(e)}")
            return

        self.schools_combo.clear()
        if not schools:
            self.debug_log("Keine Schulen gefunden.")
            return

        # Merken für später
        self.found_schools = schools

        # Schulen in ComboBox eintragen: "#Index – displayName (address)"
        for idx, school in enumerate(schools):
            display = f"#{idx} – {school['displayName']} ({school['address']})"
            self.schools_combo.addItem(display, idx)  # data=idx
        
        if self.use_defaults:
                schulnummer = int(self.config_data.get("Schulnummer"))
                #print(schulnummer)
                self.schools_combo.setCurrentIndex(schulnummer) # set index of school combo to default

        self.debug_log(f"{len(schools)} Schulen gefunden und ComboBox gefüllt.")

    def debug_log(self, msg):
        self.log_text.append(msg)

    def refresh(self):
        self.config_data = read_config_env()

    def run_fetch(self):

        """Hauptfunktion zum Stundenplan-Abruf; verwendet die derzeit gewählten Einstellungen."""
        self.debug_log("Starte Stundenplan-Abruf...")
        debug_mode = (self.config_data.get("Debugging", "False").lower() == "true")

        # 1) Standardwerte & Felder
        name = self.config_data.get("Name", "None")
        email = self.config_data.get("Email", "None")
        betrieb = self.config_data.get("Betrieb", "None")
        std_schulnummer = self.config_data.get("Schulnummer", "None")
        std_klasse = self.config_data.get("Klasse", "None")

        if name in ["None", ""] or email in ["None", ""] or betrieb in ["None", ""]:
            QMessageBox.warning(self, "Fehlende Angaben", "Bitte Name, Email und Betrieb in Settings eintragen.")
            return

        week_count = self.weeks_spin.value()

        # 2) Schule aus ComboBox
        # Falls user Defaults nutzt, aber man trotzdem die ComboBox füllen will
        # => Dann sollte user "Schulen laden" gedrückt haben. Hier prüfen wir:
        if not hasattr(self, 'found_schools') or len(self.found_schools) == 0:
            QMessageBox.information(self, "Keine Schule ausgewählt", "Bitte zuerst auf 'Schulen laden' klicken und eine Schule auswählen.")
            return

        selected_index = self.schools_combo.currentIndex()
        if selected_index < 0:
            QMessageBox.warning(self, "Keine Schule", "Bitte wählen Sie eine Schule aus der Liste.")
            return

        # mapping index -> actual school
        school = self.found_schools[selected_index]
        self.debug_log(f"Ausgewählte Schule: {school['displayName']}")

        # 3) Klasse
        if self.use_defaults:
            if not std_klasse == self.class_edit.text().strip():
                class_short = self.class_edit.text().strip()
            else:
                class_short = std_klasse
            if not class_short or class_short == "None":
                QMessageBox.warning(self, "Klasse fehlt", "Klasse ist nicht gesetzt oder leer.")
                return
        else:
            class_short = self.class_edit.text().strip()
            if not class_short:
                QMessageBox.warning(self, "Klasse fehlt", "Bitte einen Klassennamen (Kurzname) eingeben.")
                return

        # 4) Cookies holen etc.
        jsession_id, trace_id = get_cookies(school["server"], school["loginSchool"], debug_mode)
        if not jsession_id:
            self.debug_log("Fehler: Konnte keine Session-Cookies erhalten.")
            return

        headers = get_headers(
            tenant_id=school["tenantId"],
            schoolname=school["loginName"],
            server=school["server"],
            login_name=school["loginSchool"],
            jsession_id=jsession_id,
            trace_id=trace_id
        )

        # 5) Klassen-Liste
        class_list, error_msg = get_classes(school["server"], school, jsession_id, trace_id, debug_mode)
        if error_msg:
            self.debug_log(f"Fehler bei get_classes: {error_msg}")
            return

        matching_class = next((c for c in class_list if c["shortName"] == class_short), None)
        if not matching_class:
            self.debug_log(f"Klasse '{class_short}' nicht gefunden.")
            return

        class_id = matching_class["id"]
        self.debug_log(f"Klasse {matching_class['displayName']} (ID={class_id}) wird geladen...")

        # 6) Wochen-Daten
        all_days = fetch_data_for_next_weeks(school, class_id, week_count, headers, debug_mode, debug_log_func=self.debug_log)
        if not all_days:
            self.debug_log("Keine Stunden gefunden.")
            return

        # 7) ICS generieren

        global create_oof

        if self.create_oof_box.isChecked():
            create_oof = True
        else:
            create_oof = False
        ics_path = create_ics_file_for_week(all_days, school["loginName"], self.config_data.get("Dateipfad"), school, name, betrieb, email, debug_log_func=self.debug_log)
        if ics_path:
            #self.debug_log(f"ICS-Datei erstellt: {ics_path}")
            ret = QMessageBox.question(self, "Öffnen?", "Soll die .ics-Datei in Ihrem Kalender geöffnet werden?", QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.Yes:
                open_ics_with_default_app(ics_path)
        if debug_mode:
            ret = QMessageBox.question(self, "Builden?","Soll diese Version gebuildet werden?", QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.Yes:
                self.debug_log("Version wird gebaut...")
                if os.path.exists("./dist/WebLook.exe"):
                    os.remove("./dist/WebLook.exe")

                script_directory = os.path.dirname(os.path.abspath(sys.argv[0])) 
                icon_path = os.path.join(script_directory, "assets/icons/normal/webuntisscraper.ico")
                #print(icon_path)
                os.system(f'pyinstaller main.py --onefile --name WebLook --icon "{icon_path}"')
                # check if build was successful
                if not os.path.exists("./dist/WebLook.exe"):
                    print("Build failed.")
                else:
                    #Copy Assets to build directory
                    assets_path = script_directory + "/assets"
                    build_assets_path = script_directory + "/dist/assets"
                    if not os.path.exists(build_assets_path):
                        os.makedirs(build_assets_path)
                        os.system(f'xcopy "{assets_path}" "{build_assets_path}" /e /h /s')
                    print("Build successful.")
                        
        


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
