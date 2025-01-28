import sys
import os
import re
import json
import base64
import datetime
import time
import subprocess
import urllib.parse
import requests
import warnings
import holidays
import zipfile
import shutil


from PyQt5.QtCore import Qt, QSize, pyqtSignal
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
ausbilder_modus = False
last_created_ics = None


def write_log(log_text, path="logs.log"):
    """
    Schreibt den übergebenen Text als Log in eine Datei.
    
    :param log_text: Der zu protokollierende Text.
    :param path: Pfad zur Log-Datei (Standard: logs.log).
    """
    zeitstempel = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    eintrag = f"[{zeitstempel}] {log_text}\n"
    
    with open(path, "a+", encoding="utf-8") as datei:
        datei.write(eintrag)

def read_config_env(file_path='config.env'):
    config = {}
    script_directory = os.path.dirname(os.path.abspath(sys.argv[0])) 
    default_path = os.path.join(script_directory, "kalender")

    default_settings = {
        "Name": "None",
        "Email": "None",
        "Username":"None",
        "Passwort": "None",
        "Betrieb": "None",
        "Stadt/Adresse": "None",
        "Klasse": "None",
        "Schulnummer": "None",
        "Wochen": "4",
        "Dateipfad": default_path, 
        "Debugging": "False",
        "Ausbildermodus":"False"
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
        write_log(f"An error occurred reading config.env: {e}")
        
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
            write_log(f"Cookies: {cookies}")
        return jsessionid, traceid
    except Exception as e:
        write_log(f"Error getting cookies: {e}")
        return None, None

def get_headers(tenant_id, schoolname, server, login_name, jsession_id, trace_id, method, xcsrf_token=None):
    """
    Existing function for building various headers. We'll still use it
    for 'get_classes(...)' or other calls to keep your code unchanged.
    """
    sleek_session = generate_sleek_session()

    if method == "get_headers":
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

    elif method == "get_class_id_headers":
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

    elif method == 'get_login_headers':
        headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": f'schoolname="_{schoolname}"; Tenant-Id="{tenant_id}"; traceId={trace_id}; JSESSIONID={jsession_id}; _sleek_session={sleek_session}',
            "origin": f"https://{server}",
            "priority": "u=1, i",
            "referer": f"https://{server}/WebUntis/",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "tenant-id": f"{tenant_id}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "x-csrf-token": f"{xcsrf_token}"
        }
        return headers

    elif method == 'get_x_csrf_headers':
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        }
        return headers

def get_x_crsf_token(server, loginName, school, jsession_id, trace_id, debug_mode=False):

    """
    If your instance needs an X-CSRF token, we fetch it from the HTML.
    Some installations may skip this.
    """


    headers = get_headers(
        tenant_id=school["tenantId"],
        schoolname=school["loginName"],
        server=school["server"],
        login_name=school["loginSchool"],
        jsession_id=jsession_id,
        trace_id=trace_id,
        method="get_x_csrf_headers"
    )
    url = f"https://{server}/WebUntis/?school={loginName}#/basic/login"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_content = response.text
        csrf_token_pattern = r'"csrfToken":\s*"([^"]+)"'
        match = re.search(csrf_token_pattern, html_content)
        if match:
            csrf_token = match.group(1)
            if debug_mode:
                write_log(f"CSRF Token: {csrf_token}")
            return csrf_token
        else:
            write_log("CSRF Token not found (possibly not required).")
    else:
        write_log(f"Failed to fetch login page, status code: {response.status_code}")
    return None

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
        write_log(f"Fehler bei der Anfrage: {e}")
        return None
    except ValueError as e:
        write_log(f"Fehler beim Parsen von JSON: {e}")
        return None


import datetime

def get_school_days_subjects_teachers(json_data, debug_mode=False):
    """
    Parses the returned JSON for timetable data and supports both 'elementPeriods' and 'elements'.
    """
    date_to_day = {
        0: 'Montag',
        1: 'Dienstag',
        2: 'Mittwoch',
        3: 'Donnerstag',
        4: 'Freitag',
        5: 'Samstag',
        6: 'Sonntag',
    }

    try:
        result_data = json_data.get("data", {}).get("result", {}).get("data", {})
        element_periods = result_data.get('elementPeriods', {})
        elements = result_data.get('elements', [])
    except KeyError:
        if debug_mode:
            error_message = json_data.get("data", {}).get("error", {}).get("data", {}).get("messageKey", "Unknown error")
            write_log(f"Fehler: {error_message}")
        return []

    # Create a lookup for element IDs to their names (like teachers or subjects)
    element_lookup = {elem['id']: elem['name'] for elem in elements}

    school_days_subjects_teachers = []

    # Process periods
    for _, periods in element_periods.items():
        for period in periods:
            date = period['date']
            year, month, day = int(str(date)[:4]), int(str(date)[4:6]), int(str(date)[6:])
            lesson_date = datetime.date(year, month, day)
            day_of_week = lesson_date.weekday()
            school_day = date_to_day[day_of_week]

            # Extract lesson code, teacher, and subject
            lesson_code = period.get('lessonCode', '')
            teacher_ids = [elem['id'] for elem in period['elements'] if elem['type'] == 5]
            subject_ids = [elem['id'] for elem in period['elements'] if elem['type'] == 3]
            # Lookup teacher and subject names using studentGroup

            teacher_names = [element_lookup[tid] for tid in teacher_ids if tid in element_lookup]
            subject_names = [element_lookup[sid] for sid in subject_ids if sid in element_lookup]


            try:
                parts = period["studentGroup"].split('_')
                if not teacher_names:
                    teacher_names = [parts[-1]]
                elif not subject_names:
                    subject_names = [parts[0]]
            except Exception as e:
                teacher_names = ["Unbekannt"]
                if debug_mode:
                    write_log(f"Error parsing studentGroup: {e}")
            

            cell_state = period.get("cellState", '')
            is_exam = (cell_state == "EXAM")
            is_additional = (cell_state == "ADDITIONAL")

            start_time = period.get('startTime', 0)
            end_time = period.get('endTime', 0)
            start_hour = start_time // 100
            start_minute = start_time % 100
            end_hour = end_time // 100
            end_minute = end_time % 100

            # if debug_mode:
            #     (f"Processed: Subjects={subject_names}, Teachers={teacher_names}, cellState={cell_state}")


            school_days_subjects_teachers.append({
                "lesson_date": lesson_date,
                "school_day": school_day,
                "subjects": subject_names,
                "teachers": teacher_names,
                "is_exam": is_exam,
                "is_additional": is_additional,
                "start_time": datetime.time(start_hour, start_minute),
                "end_time": datetime.time(end_hour, end_minute),
            })
    return school_days_subjects_teachers






# def get_school_days_subjects_teachers(json_data, debug_mode=False):
#     """
#     As in your existing code, parse the returned JSON for timetable data.
#     """
#     date_to_day = {
#         0: 'Montag',
#         1: 'Dienstag',
#         2: 'Mittwoch',
#         3: 'Donnerstag',
#         4: 'Freitag',
#         5: 'Samstag',
#         6: 'Sonntag',
#     }
#     try:
#         if json_data["data"]["result"]:
#             element_periods = json_data['data']['result']['data'].get('elementPeriods')
#             if element_periods is None:
#                 element_periods = json_data['data']['result']['data'].get('elements', {})
#     except KeyError:
#         if debug_mode:
#             print("Fehler:" + json_data["data"]["error"]["data"].get("messageKey"))
#         return []
        

#     school_days_subjects_teachers = []

#     for _, periods in element_periods.items():
#         for period in periods:
#             #print(period)
#             date = period['date']
#             date_str = str(date)
#             year = int(date_str[:4])
#             month = int(date_str[4:6])
#             day = int(date_str[6:])
#             lesson_date = datetime.date(year, month, day)
#             day_of_week = lesson_date.weekday()
#             school_day = date_to_day[day_of_week]

#             lesson_code = period.get('studentGroup', '')
#             if '_' in lesson_code:
#                 parts = lesson_code.split('_', 1)
#                 subject = parts[0]
#                 teacher_part = parts[1] if len(parts) > 1 else 'Unbekannt'
#                 teacher_parts = teacher_part.split("_")
#                 teacher = teacher_parts[-1] if len(teacher_parts) > 1 else teacher_part
#             else:
#                 subject = lesson_code
#                 teacher = 'Unbekannt'

#             cellState = period.get("cellState", '')
#             is_exam = (cellState == "EXAM")
#             is_additional = (cellState == "ADDITIONAL")

#             start_time = period.get('startTime', 0)
#             end_time = period.get('endTime', 0)
#             start_hour = start_time // 100
#             start_minute = start_time % 100
#             end_hour = end_time // 100
#             end_minute = end_time % 100

#             if debug_mode:
#                 print(f"Processed: {subject}, cellState={cellState}")

#             school_days_subjects_teachers.append({
#                 "lesson_date": lesson_date,
#                 "school_day": school_day,
#                 "subject": subject,
#                 "teacher": teacher,
#                 "is_exam": is_exam,
#                 "is_additional": is_additional,
#                 "start_time": datetime.time(start_hour, start_minute),
#                 "end_time": datetime.time(end_hour, end_minute),
#             })
#     return school_days_subjects_teachers

def get_next_workday(date_obj, holiday_dates, school_days):
    """
    Finds the next workday that is not a weekend, holiday, or school day.

    :param date_obj: The starting date (datetime.date)
    :param holiday_dates: A set of holidays (set of datetime.date)
    :param school_days: A set of known school days (set of datetime.date)
    :return: The next workday date (datetime.date)
    """
    next_day = date_obj + datetime.timedelta(days=1)
    while (
        next_day.weekday() > 4  # Skip weekends (5=Sat, 6=Sun)
        or next_day in holiday_dates  # Skip holidays
        or next_day in school_days  # Skip school days
    ):
        next_day += datetime.timedelta(days=1)
    return next_day

def create_ics_file_for_week(
    school_days_subjects_teachers,
    schoolname,
    output_dir="kalender",
    school_data=None,
    name="",
    betrieb="",
    email="",
    student_name_path="",
    student_name="",
    debug_log_func=write_log,
    create_oof=False,
    ausbilder_modus=False,
    oof_custom_text="",  # Editable custom text for OOF messages
    country="DE",  # Default to Germany for holidays
    prov=None,     # Optional province code (e.g., "BY" for Bavaria)
    state=None     # Optional state code
):
    """
    Create an ICS (iCalendar) file with the given school schedule data, including holidays and OOF events.
    """
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Sort lessons by (date, start_time)
    sorted_lessons = sorted(
        school_days_subjects_teachers, 
        key=lambda x: (x["lesson_date"], x["start_time"])
    )
    
    # Determine the school name
    schoolname = school_data.get('loginSchool', "Schule") if school_data else "Schule"
    
    debug_log_func(f"Anzahl gefundener Stunden: {len(sorted_lessons)}")

    # If no lessons are found, exit early
    if len(sorted_lessons) == 0:
        debug_log_func("Keine Stunden gefunden.")
        return None

    # Initialize ICS content
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN"
    ]

    # Determine ICS creation date based on the first lesson
    first_lesson_dt = datetime.datetime.combine(
        sorted_lessons[0]["lesson_date"],
        sorted_lessons[0]["start_time"]
    )
    creation_date = first_lesson_dt.strftime("%Y%m%dT%H%M%S")
    


    # Gather all school days from lessons
    school_days = {lesson["lesson_date"] for lesson in sorted_lessons}

    # Generate holidays using the holidays library
    min_date = sorted_lessons[0]["lesson_date"]
    max_date = sorted_lessons[-1]["lesson_date"]
    year_range = {min_date.year, max_date.year}
    holiday_dates = set()
    for year in year_range:
        country_holidays = holidays.country_holidays(country, prov=prov, state=state, years=year, language="DE")
        holiday_dates.update(country_holidays.keys())

    # Identify all dates within the range
    total_days = (max_date - min_date).days + 1
    all_dates = {min_date + datetime.timedelta(days=i) for i in range(total_days)}

    # Identify non-school days: weekends and holidays
    non_school_days = {day for day in all_dates if day.weekday() > 4 or day in holiday_dates}

    # Add VEVENT for each holiday
    for hday in sorted(non_school_days):
        if hday in holiday_dates:
            holiday_name = country_holidays.get(hday, "Feiertag")
            dtstart_holiday = hday.strftime("%Y%m%d")
            dtend_holiday = (hday + datetime.timedelta(days=1)).strftime("%Y%m%d")
            ics_content.extend([
                "BEGIN:VEVENT",
                f"DTSTART;VALUE=DATE:{dtstart_holiday}",
                f"DTEND;VALUE=DATE:{dtend_holiday}",
                f"SUMMARY:Feiertag ({holiday_name})",
                f"DESCRIPTION:Feiertag - {holiday_name}",
                "STATUS:CONFIRMED",
                "TRANSP:TRANSPARENT",
                "END:VEVENT"
            ])
            debug_log_func(f"Feiertag hinzugefügt: {hday} ({holiday_name})")

    # Add VEVENT for each lesson
    # for lesson in sorted_lessons:
    #     #if debug_mode:
    #     print(lesson)
    #     event_start_dt = datetime.datetime.combine(
    #         lesson["lesson_date"],
    #         lesson["start_time"]
    #     )
    #     event_end_dt = datetime.datetime.combine(
    #         lesson["lesson_date"],
    #         lesson["end_time"]
    #     )
    #     event_start = event_start_dt.strftime("%Y%m%dT%H%M%S")
    #     event_end = event_end_dt.strftime("%Y%m%dT%H%M%S")
    #     event_description = f"{lesson['subjects']} - {lesson['teachers']}"
        

    #     # Determine summary and description based on lesson type
    #     if lesson.get("is_exam"):
    #         summary_line = f"Prüfung {lesson['subject']}"
    #         description_line = f"{event_description} Prüfung!"
    #     elif lesson.get("is_additional"):
    #         summary_line = f"Ersatzstunde {lesson['subject']}"
    #         description_line = f"{event_description} Ersatz!"
    #     else:
    #         summary_line = lesson["subject"]
    #         description_line = event_description

    #     # Append the VEVENT
    #     ics_content.extend([
    #         "BEGIN:VEVENT",
    #         f"DTSTART:{event_start}",
    #         f"DTEND:{event_end}",
    #         f"SUMMARY:{summary_line}",
    #         f"DESCRIPTION:{description_line}",
    #         f"LOCATION:{lesson['teacher']}",
    #         "STATUS:CONFIRMED",
    #         "END:VEVENT"
    #     ])
    #print("ausbildermodus:" + str(ausbilder_modus))
    if not ausbilder_modus:
        for lesson in sorted_lessons:
            # if debug_mode:
            #     print(lesson)
            event_start_dt = datetime.datetime.combine(
                lesson["lesson_date"],
                lesson["start_time"]
            )
            event_end_dt = datetime.datetime.combine(
                lesson["lesson_date"],
                lesson["end_time"]
            )
            event_start = event_start_dt.strftime("%Y%m%dT%H%M%S")
            event_end = event_end_dt.strftime("%Y%m%dT%H%M%S")

            # Combine multiple subjects and teachers into a single string
            subjects = ", ".join(lesson.get("subjects", []))  # Fallback to an empty list if 'subjects' is missing
            teachers = ", ".join(lesson.get("teachers", []))  # Fallback to an empty list if 'teachers' is missing
            event_description = f"{subjects} - {teachers}"

            # Determine summary and description based on lesson type
            if lesson.get("is_exam"):
                summary_line = f"Prüfung {subjects}"
                description_line = f"{event_description} Prüfung!"
            elif lesson.get("is_additional"):
                summary_line = f"Ersatzstunde {subjects}"
                description_line = f"{event_description} Ersatz!"
            else:
                summary_line = subjects
                description_line = event_description

            # Append the VEVENT
            ics_content.extend([
                "BEGIN:VEVENT",
                f"DTSTART:{event_start}",
                f"DTEND:{event_end}",
                f"SUMMARY:{summary_line}",
                f"DESCRIPTION:{description_line}",
                f"LOCATION:{teachers}",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ])


    # Create OOF blocks for consecutive school days
    if create_oof:
        # Sort school days to process them in order
        sorted_school_days = sorted(school_days)
        blocks = []
        current_block = []

        for day in sorted_school_days:
            if not current_block:
                current_block = [day]
            else:
                if (day - current_block[-1]).days == 1:
                    current_block.append(day)
                else:
                    blocks.append(current_block)
                    current_block = [day]
        if current_block:
            blocks.append(current_block)

        # Retrieve display information from school_data
        display_name = school_data.get("displayName", "Schule") if school_data else "Schule"
        address = school_data.get("address", "Unbekannte Adresse") if school_data else "Unbekannte Adresse"

        for block in blocks:
            block_earliest = min(block)
            block_latest = max(block)

            # Calculate the next workday after the last school day in the block
            next_workday_dt = get_next_workday(block_latest, holiday_dates=holiday_dates, school_days=school_days)
            next_workday_str = next_workday_dt.strftime("%d.%m.%Y")
            if not ausbilder_modus:
                oof_description = (
                    "Sehr geehrte Damen und Herren,\\n\\n"
                    f"leider bin ich derzeit außer Haus. Sie können mich ab dem {next_workday_str}"
                    "wieder erreichen.\\n\\n"
                    f"Viele Grüße,\\n\\n{name}\\n{betrieb}\\n\\n{email}\\n\\n"
                )
                print_description = (
                    "\nSehr geehrte Damen und Herren,\n\n"
                    f"leider bin ich derzeit außer Haus. Sie können mich ab dem {next_workday_str}"
                    "wieder erreichen.\n\n"
                    f"Viele Grüße,\n\n{name}\n{betrieb}\n\n{email}\n\n"
                )
            else:
                oof_description = (
                    "Sehr geehrte Damen und Herren,\\n\\n"
                    f"Der Azubi ({student_name}) ist zur Zeit an der {display_name}! "
                    f"Er/Sie ist ab dem {next_workday_str} wieder erreichbar.\\n\\n"
                    f"Viele Grüße,\\n\\n{name}\\n{betrieb}\\n\\n{email}\\n\\n"
                )
                print_description = (
                    "\nSehr geehrte Damen und Herren,\n\n"
                    f"Der Azubi ({student_name}) ist zur Zeit an der {display_name}! "
                    f"Er/Sie ist ab dem {next_workday_str} wieder erreichbar.\n\n"
                    f"Viele Grüße,\n\n{name}\n{betrieb}\n\n{email}\n\n"
                )
            # Define the OOF event's start and end dates (inclusive)
            dtstart_oof = block_earliest.strftime("%Y%m%d")
            dtend_oof = (block_latest + datetime.timedelta(days=1)).strftime("%Y%m%d")
            if not ausbilder_modus:
                # Append the OOF VEVENT
                ics_content.extend([
                    "BEGIN:VEVENT",
                    "CLASS:PUBLIC",
                    f"CREATED:{creation_date}",
                    f"DESCRIPTION:{oof_description}",
                    f"DTEND;VALUE=DATE:{dtend_oof}",
                    f"DTSTART;VALUE=DATE:{dtstart_oof}",
                    f"LOCATION:",
                    f"SUMMARY;LANGUAGE=de:{display_name} ({address})",
                    "TRANSP:OPAQUE",
                    "STATUS:CONFIRMED",
                    "X-MICROSOFT-CDO-BUSYSTATUS:OOF",
                    "X-MICROSOFT-CDO-IMPORTANCE:1",
                    "X-MICROSOFT-CDO-DISALLOW-COUNTER:FALSE",
                    "X-MS-OLK-AUTOFILLLOCATION:FALSE",
                    "X-MS-OLK-CONFTYPE:0",
                    "END:VEVENT"
                ])
            else:
                # Append the OOF VEVENT
                ics_content.extend([
                    "BEGIN:VEVENT",
                    "CLASS:PUBLIC",
                    f"CREATED:{creation_date}",
                    f"DESCRIPTION:{oof_description}",
                    f"DTEND;VALUE=DATE:{dtend_oof}",
                    f"DTSTART;VALUE=DATE:{dtstart_oof}",
                    f"LOCATION:",
                    f"SUMMARY;LANGUAGE=de: Azubi {student_name} - {display_name}",
                    "TRANSP:OPAQUE",
                    "STATUS:CONFIRMED",
                    "X-MICROSOFT-CDO-BUSYSTATUS:FREE",
                    "X-MICROSOFT-CDO-IMPORTANCE:1",
                    "X-MICROSOFT-CDO-DISALLOW-COUNTER:FALSE",
                    "X-MS-OLK-AUTOFILLLOCATION:FALSE",
                    "X-MS-OLK-CONFTYPE:0",
                    "END:VEVENT"
                ])
            # Debug information
            # debug_log_func(
            #     f"OOF-Block: {block_earliest} → {block_latest} | "
            #     f"Nächster Arbeitstag: {next_workday_str}"
            # )
            # if debug_mode:
            #     debug_log_func(
            #         f"\nOOF-Notiz: {formatted_oof_description}"
            #     )
            if debug_mode:
                debug_log_func(
                    f"<p>OOF-Block: {block_earliest} → {block_latest} | "
                    f"Nächster Arbeitstag: {next_workday_str}</p>"
                )
                debug_log_func(f"{print_description}")
    
    creation_date_dt = datetime.datetime.strptime(str(creation_date), "%Y%m%dT%H%M%S")

    # Format the datetime object into the desired format
    formatted_creation_date = creation_date_dt.strftime("%Y-%m-%d")
    # Close the ICS calendar
    ics_content.append("END:VCALENDAR")
    if not ausbilder_modus:
        filename = f"{name}_{schoolname.lower()}_stundenplan_woche_{formatted_creation_date}_{block_latest}.ics"
    else:
        filename = f"{student_name_path}_{schoolname.lower()}_azubi_abwesenheiten_der_wochen_{formatted_creation_date}-{block_latest}.ics"
    file_path = os.path.join(output_dir, filename)

    # Write the ICS content to the file
    with open(file_path, 'w', encoding='utf8') as ics_file:
        ics_file.write("\n".join(ics_content))

    debug_log_func(f"ICS-Datei erstellt: {file_path}")

    global last_created_ics
    last_created_ics = file_path

    return file_path



def open_ics_with_default_app(ics_file_path):
    if not os.path.exists(ics_file_path):
        QMessageBox.warning(f"Die Datei {ics_file_path} existiert nicht.")
        return
    try:
        if os.name == "nt":
            os.startfile(ics_file_path)
        else:
            subprocess.run(["open", ics_file_path])
    except Exception as e:
        write_log(f"Ein Fehler ist aufgetreten: {e}")


def get_schools(city, debug_mode=False):
    """
    No changes needed; returns a list of possible schools for the given city.
    """
    url = "https://mobile.webuntis.com/ms/schoolquery2"
    payload = (
        '{"id":"wu_schulsuche","method":"searchSchool","params":[{"search":"'
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
            write_log(f"Found school: {s}")
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

# def get_classes(server, school, jsession_id, trace_id, debug_mode=False):
#     """
#     Same as before: gets a list of classes from the /api/rest/view/v1/timetable/filter endpoint.
#     We will call it after we've done the new form-based login, so we have a valid JSESSIONID + traceId.
#     """
#     my_api_url = ""
#     api_url = f"https://{server}/WebUntis/api/rest/view/v1/timetable/filter?resourceType=CLASS&timetableType=STANDARD"
#     response = requests.get(
#         api_url,
#         headers=get_headers(
#             tenant_id=school["tenantId"],
#             schoolname=school["loginName"],
#             server=school["server"],
#             login_name=school["loginSchool"],
#             jsession_id=jsession_id,
#             trace_id=trace_id,
#             method="get_class_id_headers"
#         )
#     )
#     if response.status_code != 200:
#         return None, response.json()
#     data = response.json()
#     classes = data["classes"]
#     class_data = []
#     for c in classes:
#         cinfo = c["class"]
#         class_data.append({
#             "id": cinfo["id"],
#             "shortName": cinfo["shortName"],
#             "longName": cinfo["longName"],
#             "displayName": cinfo["displayName"]
#         })
#     if debug_mode:
#         print("Class data:", class_data)
#     return class_data, None
def get_classes(server, school, session, debug_mode=False):
    api_url = f"https://{server}/WebUntis/api/rest/view/v1/timetable/filter?resourceType=CLASS&timetableType=STANDARD"
    if debug_mode:
        write_log(f"Schoolname: " + school["loginName"])
        write_log(f"login_name: " + school["loginSchool"])
    headers = get_headers(
        tenant_id=school["tenantId"],
        schoolname=school["loginName"],
        server=school["server"],
        login_name=school["loginSchool"],
        jsession_id=session.cookies.get("JSESSIONID"),
        trace_id=session.cookies.get("TraceId"),
        method="get_class_id_headers"
    )

    try:
        response = session.get(api_url, headers=headers)
        if debug_mode:
            write_log(f"get_classes response: {response.status_code}, {response.text}")

        if response.status_code != 200:
            return None, f"HTTP {response.status_code}: {response.json().get('errorMessage', 'Unknown error')}"

        data = response.json()
        classes = data.get("classes", [])
        class_data = [
            {
                "id": c["class"]["id"],
                "shortName": c["class"]["shortName"],
                "longName": c["class"]["longName"],
                "displayName": c["class"]["displayName"]
            }
            for c in classes
        ]

        if debug_mode:
            write_log("Class data: {class_data}")

        return class_data, None

    except Exception as e:
        if debug_mode:
            write_log(f"Error in get_classes: {e}")
        return None, str(e)



def fetch_data_for_next_weeks(
    school,
    week_count,
    headers,
    class_id=None,
    debug_mode=False,
    debug_log_func=write_log,
    student_id=None,
):
    """
    Original approach to fetch multiple weeks. We pass in 'headers' which include our cookies.
    """
    current_date = datetime.datetime.now()
    start_of_current_week = get_start_of_week(current_date)
    weeks_to_fetch = [start_of_current_week]
    for i in range(1, week_count):
        date_plus_weeks = current_date + datetime.timedelta(weeks=i)
        start_of_next_week = get_start_of_week(date_plus_weeks)
        weeks_to_fetch.append(start_of_next_week)

    if debug_mode:
        debug_log_func(f"Weeks to fetch: {weeks_to_fetch}")
        write_log(f"ClassID: {class_id}")
    all_school_days = []
    server = school["server"]

    for week_start in weeks_to_fetch:
        api_url = (
            f"https://{server}/WebUntis/api/public/timetable/weekly/data"
            f"?elementType=1&elementId={class_id}&date={week_start}&formatId=2&filter.departmentId=-1"
        )
        #
        if student_id is not None:
            api_url = f"https://{server}/WebUntis/api/public/timetable/weekly/data?elementType=5&elementId={student_id}&date={week_start}&formatId=10"
            #api_url = f"https://{server}/WebUntis/api/public/timetable/weekly/data?elementType=5&elementId={student_id}&date={week_start}&formatId=10&filter.departmentId=-1"
        if debug_mode:
            debug_log_func(f"Hole Daten für Woche: {week_start}")
            write_log(f"Accessing Api-Endpoint: {api_url}")
        timetable_data = fetch_timetable_data(api_url, headers)
        if timetable_data:
            results = get_school_days_subjects_teachers(timetable_data, debug_mode)
            all_school_days.extend(results)

    return all_school_days




# -----------------------------
# Updater Implementation
# -----------------------------

class Updater:
    def __init__(self,
                 local_version_file: str,
                 remote_version_url: str,
                 remote_zip_url: str,
                 target_path: str,
                 download_path: str = "./update_download.zip",
                 extract_path: str = "./update_temp",
                 output_method=print):
        """
        :param local_version_file: Pfad zur lokalen version.txt (z.B. "./version.txt").
        :param remote_version_url: URL zum raw-Inhalt der version.txt in deinem GitHub-Repo.
        :param remote_zip_url: URL zum ZIP-Archiv deines Projekts (z.B. ein Release-ZIP auf GitHub).
        :param target_path: (Nicht mehr genutzt in dieser Variante.)
        :param download_path: Temporäre ZIP-Datei, in die heruntergeladen wird.
        :param extract_path: Temporärer Ordner (falls du es doch noch brauchst).
        :param output_method: Methode zur Konsolen-/Logausgabe (default: print).
        """
        self.local_version_file = local_version_file
        self.remote_version_url = remote_version_url
        self.remote_zip_url = remote_zip_url
        self.target_path = target_path
        self.download_path = download_path
        self.extract_path = extract_path
        self.output_method = output_method

    def get_local_version(self):
        """Liest die lokale Version aus der version.txt"""
        if not os.path.exists(self.local_version_file):
            return "0.0.0"
        with open(self.local_version_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    def get_remote_version(self):
        """Lädt die Versionsnummer aus der version.txt auf GitHub (raw) herunter."""
        response = requests.get(self.remote_version_url, timeout=10)
        response.raise_for_status()
        return response.text.strip()

    def compare_versions(self, local_version: str, remote_version: str):
        """
        Vergleicht die Versionen. Gibt True zurück, wenn remote_version > local_version ist.
        Beispielhafter Vergleich über major.minor.patch.
        """
        def parse_version(ver: str):
            return list(map(int, ver.split(".")))

        local_parts = parse_version(local_version)
        remote_parts = parse_version(remote_version)

        for l, r in zip(local_parts, remote_parts):
            if r > l:
                return True
            elif r < l:
                return False
        # Falls beide Versionen gleich lang sind, ist remote größer,
        # wenn es mehr Stellen hat (z. B. 1.0.0 vs 1.0.0.1)
        return len(remote_parts) > len(local_parts)

    def download_zip(self):
        """Lädt die ZIP-Datei vom GitHub-Repo herunter in self.download_path."""
        self.output_method("Lade Update-ZIP herunter...")
        response = requests.get(self.remote_zip_url, stream=True, timeout=30)
        response.raise_for_status()

        with open(self.download_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        self.output_method(f"ZIP-Datei wurde als '{self.download_path}' gespeichert.")

    def check_for_update(self) -> bool:
        """
        Prüft, ob ein Update verfügbar ist. Wenn remote > local:
          1) ZIP herunterladen
          2) In den Download-Ordner entpacken:
             "<Benutzer-Download-Ordner>/WebLook_v<REMOTE_VERSION>"
          3) Diesen neuen Ordner öffnen (Explorer/Finder/xdg-open)
        """
        local_ver = self.get_local_version()
        remote_ver = self.get_remote_version()

        self.output_method(f"Lokale Version: {local_ver}, Remote Version: {remote_ver}")

        if self.compare_versions(local_ver, remote_ver):
            # Meldung an den User, dass ein Update verfügbar ist
            QMessageBox.information(
                None,
                "Update verfügbar",
                f"Eine neuere Version ({remote_ver}) wurde gefunden.\n"
                "Das Update wird jetzt heruntergeladen.",
                QMessageBox.Ok
            )

            # 1) ZIP herunterladen
            self.download_zip()

            # 2) Zielordner im Downloads-Verzeichnis
            #    z. B. "C:/Users/<Benutzer>/Downloads/WebLook_v1.0.0"
            user_home = os.path.expanduser("~")
            downloads_folder = os.path.join(user_home, "Downloads")
            folder_name = f"WebLook_v{remote_ver}"

            target_folder = os.path.join(downloads_folder, folder_name)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            # ZIP-Datei entpacken
            with zipfile.ZipFile(self.download_path, 'r') as zip_ref:
                zip_ref.extractall(target_folder)

            subdir_path = os.path.join(target_folder, "WebLook-main")
            if os.path.isdir(subdir_path):
                # Alle Dateien/Unterordner in WebLook-main
                for item in os.listdir(subdir_path):
                    src = os.path.join(subdir_path, item)
                    dst = os.path.join(target_folder, item)
                    shutil.move(src, dst)
                # Jetzt den leeren Ordner entfernen
                shutil.rmtree(subdir_path)

            self.output_method(f"Update entpackt in: {target_folder}")

            # Aufräumen: heruntergeladene ZIP entfernen
            if os.path.exists(self.download_path):
                os.remove(self.download_path)

            # 3) Ordner öffnen
            #    Windows: explorer <path>
            #    macOS: open <path>
            #    Linux: xdg-open <path>
            open_cmd = []
            if os.name == 'nt':
                open_cmd = ['explorer', target_folder]
            elif sys.platform == 'darwin':
                open_cmd = ['open', target_folder]
            else:
                # Linux / andere Unix-Systeme
                open_cmd = ['xdg-open', target_folder]

            try:
                subprocess.Popen(open_cmd)
            except Exception as e:
                self.output_method(f"Konnte Ordner nicht öffnen: {e}")

            QMessageBox.information(
                None,
                "Update fertig",
                f"Der entpackte Ordner wurde in Ihrem Explorer/Finder geöffnet.\n"
                f"Pfad: {target_folder}",
                QMessageBox.Ok
            )

            return True
        else:
            self.output_method("Keine neuere Version gefunden, Update nicht nötig.")
            return False


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
        
        #self.fetch_page.log_text.setVisible(True)
        
        
        self.settings_page = SettingsPage(self.config_data, self)
        self.stacked_widget.currentChanged.connect(self.on_page_switch)
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_menu_page)   # index 0
        self.stacked_widget.addWidget(self.settings_page)    # index 1
        self.stacked_widget.addWidget(self.fetch_page)       # index 2
        
        # Set central widget
        self.setCentralWidget(central_widget)

        # Apply a style sheet for a modern look
        self.setStyleSheet(self.load_stylesheet())

        self.update()

    # def update(self):
    #     updater = Updater(
    #         local_version_file="./assets/version.txt",
    #         remote_version_url="https://raw.githubusercontent.com/baulum/WebLook/main/assets/version.txt",
    #         remote_zip_url="https://github.com/baulum/WebLook/archive/refs/heads/main.zip",
    #         target_path="./",
    #         download_path="update_download.zip",
    #         extract_path="update_temp",
    #         output_method=print  # für Debugzwecke: Ausgabe der Update-Ausgaben
    #     )
    #     updater.check_for_update()
        
    def update(self):
        updater = Updater(
            local_version_file=local_version_file,
            remote_version_url="https://raw.githubusercontent.com/baulum/WebLook/main/assets/version.txt",
            remote_zip_url="https://github.com/baulum/WebLook/archive/refs/heads/main.zip",
            target_path=" ",
            download_path="update_download.zip",
            extract_path="update_temp",
            output_method=print  # für Debugzwecke: Ausgabe der Update-Ausgaben
        )
        is_update = updater.check_for_update()
        if is_update:
             sys.exit(0)


    def on_page_switch(self, index):
        """Refresh the fetch page when it becomes visible."""
        if self.stacked_widget.currentWidget() == self.fetch_page:
            self.fetch_page.refresh()

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
        info = QLabel("Nutzen Sie die Seitenleiste, um zu navigieren:\n\n1) Stundenplan abrufen\n2) Einstellungen\n")
        layout.addWidget(info)
        layout.addStretch()


class SettingsPage(QWidget):
    """Represents the settings page. Allows editing config.env values."""
    #global ausbilder_modus
    def __init__(self, config_data, parent=None):
        global debug_mode
        #global ausbilder_modus
        debug_mode = False
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self.config_data = config_data

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

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
            "Name", "Email", "Username", "Passwort", "Betrieb",
            "Stadt/Adresse", "Klasse",
            "Schulnummer", "Wochen", "Dateipfad", "Debugging", "Ausbildermodus"
        ]
        for key in settings_keys:
            label = QLabel(key)
            label.setMinimumWidth(120)
            grid.addWidget(label, row, 0, 1, 1)
            if not key == "Debugging" or not key == "Ausbildermodus":
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
            if key == "Passwort":
                self.password_edit = QLineEdit()
                self.password_edit.setEchoMode(QLineEdit.Password)
                self.show_pass_btn = QPushButton()
                self.pass_is_visible = False
                self.show_pass_btn.setIcon(QIcon("./assets/icons/inverted/show_inverted.png"))
                grid.addWidget(self.password_edit, row, 1, 1, 1)
                grid.addWidget(self.show_pass_btn, row, 2, 1, 1)
            if key == "Debugging":
                self.check_box = QCheckBox()
                val = self.config_data.get(key, False)
                if val.lower() == "true":
                    self.check_box.setChecked(True)
                    self.check_box.setText("Debugging ist eingeschaltet")
                else:     
                    self.check_box.setChecked(False)
                    self.check_box.setText("Debugging ist ausgeschaltet")
                grid.addWidget(self.check_box, row, 1, 1, 1)

            if key == "Ausbildermodus":
                self.ausbilder_check_box = QCheckBox()
                val = self.config_data.get(key, False)
                if val.lower() == "true":
                    
                    self.ausbilder_check_box.setChecked(True)
                    
                    self.ausbilder_check_box.setText("Ausbildermodus ist eingeschaltet")
                else:
                        
                    self.ausbilder_check_box.setChecked(False)
                    self.ausbilder_check_box.setText("Ausbildermodus ist ausgeschaltet")
                grid.addWidget(self.ausbilder_check_box, row, 1, 1, 1)
            row += 1
        #global debug_mode
        self.btn_save = QPushButton("Speichern")
        self.btn_save.setIcon(QIcon("./assets/icons/inverted/save_inverted.png"))
        self.show_pass_btn.clicked.connect(self.change_pass_visible)
        self.check_box.clicked.connect(self.change_debug)
        self.ausbilder_check_box.clicked.connect(self.change_ausbilder_modus)
        self.btn_save.clicked.connect(self.save_settings)
        grid.addWidget(self.btn_save, row, 0, 1, 2)
        self.refresh()

    def change_ausbilder_modus(self):
        if self.ausbilder_check_box.isChecked():
            update_config_env("Ausbildermodus", "True")
            self.ausbilder_check_box.setText("Ausbildermodus ist eingeschaltet")    
 
            ausbilder_modus = True
            if debug_mode:   
                write_log("Ausbildermodus changed to True")
            self.refresh()
        else:
            update_config_env("Ausbildermodus", "False")
            self.ausbilder_check_box.setText("Ausbildermodus ist ausgeschaltet")
            ausbilder_modus = False
            if debug_mode: 
                write_log("Ausbildermodus changed to False")
            self.refresh()

    def change_pass_visible(self):
        """Toggle password visibility."""
        self.pass_is_visible = not self.pass_is_visible  # Toggle visibility
        if self.pass_is_visible:
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.show_pass_btn.setIcon(QIcon("./assets/icons/inverted/hide_inverted.png"))
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.show_pass_btn.setIcon(QIcon("./assets/icons/inverted/show_inverted.png"))
        if debug_mode:
            write_log("Password visibility changed")

    def change_debug(self, checked):
        global debug_mode
        if self.check_box.isChecked():
            update_config_env("Debugging", "True")
            self.check_box.setText("Debugging ist eingeschaltet")      
            debug_mode = True  
            write_log("Debugging changed to True")
        else:
            update_config_env("Debugging", "False")
            self.check_box.setText("Debugging ist ausgeschaltet")
            debug_mode = False  
            write_log("Debugging changed to False")
        self.refresh()
        
        # Check if the parent exists and has fetch_page
        parent = self.parent()
        if parent and hasattr(parent, 'fetch_page'):
            parent.fetch_page.refresh()
        # else:
        #     print("Parent or fetch_page not found. Unable to refresh.")


    def getFolder(self):
        save_file_path = str(QFileDialog.getExistingDirectory(None, "Ordner auswählen", directory=self.config_data["Dateipfad"]))
        if save_file_path:
            update_config_env("Dateipfad", save_file_path)
            self.refresh()
            QMessageBox.information(self, "Erfolgreich", "Der Standard Speicherort wurde geändert")

    def refresh(self):
        """Refresh entries with latest config."""
        self.config_data = read_config_env()
        for key, line_edit in self.entries.items():
            val = self.config_data.get(key, "")
            line_edit.setText(val)
            if key == "Passwort":
                self.password_edit.setText(val)

    def save_settings(self):
        #print(self.password_edit.text())
        for key, line_edit in self.entries.items():
            new_val = line_edit.text().strip() 
            if key == "Passwort":
                new_val = self.password_edit.text()
            update_config_env(key, new_val)
            #read_config_env(file_path="./config.env")
            #if debug_mode:
            #print(key + ": " + new_val)
        QMessageBox.information(self, "Einstellungen", "Die Einstellungen wurden erfolgreich gespeichert!")
        self.refresh()





class FetchTimetablePage(QWidget):
    def __init__(self, config_data, parent=None):
        super().__init__(parent)
        self.config_data = config_data
        self.log_text_visible = False
        #ausbilder_modus = self.config_data["Ausbildermodus"]
        #print(ausbilder_modus)
        self.main_layout = QVBoxLayout(self)
        title = QLabel("Stundenplan abrufen")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        self.main_layout.addWidget(title)

        # Debug Mode Configuration
        self.debug_mode = self.config_data.get("Debugging", "False").lower() == "true"
        # 1) Checkbox / Button to toggle defaults
        self.use_defaults = False
        self.toggle_defaults_button = QPushButton("Defaults herunterladen")
        self.toggle_defaults_button.clicked.connect(self.fetch_defaults)
        self.main_layout.addWidget(self.toggle_defaults_button)

        # 2) City input
        city_layout = QHBoxLayout()
        city_label = QLabel("Stadt/Adresse:")
        city_label.setToolTip("Wenn die Eingabe der Stadt zu Fehlern führt geben sie die Adresse der Schule ein(Ohne PLZ und Ort)")
        self.city_edit = QLineEdit()
        self.city_edit.setToolTip("Wenn die Eingabe der Stadt zu Fehlern führt geben sie die Adresse der Schule ein(Ohne PLZ und Ort)")
        city_layout.addWidget(city_label)
        city_layout.addWidget(self.city_edit)
        self.main_layout.addLayout(city_layout)

        # 3) "Load schools" button, plus combobox
        load_schools_layout = QHBoxLayout()
        self.load_schools_btn = QPushButton("Schulen laden")
        self.load_schools_btn.setToolTip("Lädt die Schulen in die Box rechts neben an. Bitte aus der Liste eine Schule auswählen")
        self.load_schools_btn.clicked.connect(lambda: self.on_load_schools_clicked(defaults=False))
        load_schools_layout.addWidget(self.load_schools_btn)

        self.schools_combo = QComboBox()
        load_schools_layout.addWidget(self.schools_combo)
        self.main_layout.addLayout(load_schools_layout)

        # 4) Class name
        class_layout = QHBoxLayout()
        self.class_label = QLabel("Klasse (Kurzname):")
        self.class_edit = QLineEdit()
        class_layout.addWidget(self.class_label)
        class_layout.addWidget(self.class_edit)
        self.main_layout.addLayout(class_layout)

        # 5) Weeks
        weeks_layout = QHBoxLayout()
        weeks_label = QLabel("Anzahl Wochen (1-25):")
        self.weeks_spin = QSpinBox()
        self.weeks_spin.setRange(1, 25)
        self.weeks_spin.setValue(1)
        weeks_layout.addWidget(weeks_label)
        weeks_layout.addWidget(self.weeks_spin)
        self.main_layout.addLayout(weeks_layout)

        # 6) Out Of Office
        create_oof_layout = QHBoxLayout()
        self.create_oof_box = QCheckBox("Out Of Office")
        self.create_oof_box.setChecked(True)
        create_oof_label = QLabel("Out Of Office Notiz erstellen?: ")
        create_oof_layout.addWidget(create_oof_label)
        create_oof_layout.addWidget(self.create_oof_box)
        

        # # 6) Fetch Button
        # self.fetch_btn = QPushButton("Stundenplan abrufen!")
        # self.fetch_btn.clicked.connect(self.run_fetch)
        # layout.addWidget(self.fetch_btn)

        # 6) Fetch Button
        fetch_button_layout = QHBoxLayout()

        # Stundenplan abrufen Button
        self.fetch_btn = QPushButton("Stundenplan abrufen!")
        self.fetch_btn.clicked.connect(self.run_fetch)
        fetch_button_layout.addWidget(self.fetch_btn)

        # Letzte Datei öffnen Button
        self.open_last_file_btn = QPushButton("Letzte Datei öffnen")
        self.open_last_file_btn.setIcon(QIcon("./assets/icons/inverted/browse_inverted.png"))
        self.open_last_file_btn.clicked.connect(self.open_last_created_file)
        fetch_button_layout.addWidget(self.open_last_file_btn)

        # Add the horizontal layout to the main layout
        self.main_layout.addLayout(fetch_button_layout)

        # 7) Log text. Display only when Dubigging is enabled
        debug_mode = (self.config_data.get("Debugging", "False").lower() == "true")

        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.main_layout.addWidget(self.log_text)
        self.log_text.setVisible(False)

        
        self.main_layout.addWidget(self.log_text)

        self.setLayout(self.main_layout)
        self.refresh()

    def increment_version_txt(self, version_file_path: str) -> str:
        """
        Liest eine Version im Format MAJOR.MINOR.PATCH aus der version.txt, erhöht den Patch-Stand.
        Wenn Patch == 10, dann Patch wieder 0 und Minor + 1.
        (Optional: Falls Minor == 10, Minor wieder 0 und Major + 1)
        
        Schreibt die neue Version zurück in die Datei und gibt sie als String zurück.
        """
        # 1) Aktuelle Version aus version.txt lesen
        if not os.path.exists(version_file_path):
            # Falls die Datei nicht existiert, starten wir z.B. bei "1.0.0"
            local_version = "1.0.0"
        else:
            with open(version_file_path, "r", encoding="utf-8") as f:
                local_version = f.read().strip()
                if not local_version:
                    # Falls die Datei leer ist, ebenfalls mit 1.0.0 starten
                    local_version = "1.0.0"
        
        # 2) Parse die Version in drei Teile (Major, Minor, Patch)
        major_str, minor_str, patch_str = local_version.split(".")
        major = int(major_str)
        minor = int(minor_str)
        patch = int(patch_str)
        
        # 3) Patch um 1 erhöhen
        patch += 1
        
        # 4) Wenn Patch == 10 → Patch = 0 und Minor + 1
        if patch == 10:
            patch = 0
            minor += 1
            # Optional: Wenn Minor == 10, dann Minor = 0 und Major + 1
            if minor == 10:
                minor = 0
                major += 1
        
        # 5) Neue Version zusammenbauen
        new_version = f"{major}.{minor}.{patch}"
        
        # 6) Neue Version in version.txt zurückschreiben
        with open(version_file_path, "w", encoding="utf-8") as f:
            f.write(new_version)
            QMessageBox.information(self, "Version", f'Die {version_file_path} wurde auf "{new_version}" gesetzt')
        return new_version

    def toggle_debug_log_visibility(self):
        """Show or hide log_text based on debug_mode."""
        self.log_text.setVisible(self.debug_mode)

    def open_last_created_file(self):
        global last_created_ics
        if last_created_ics and os.path.exists(last_created_ics):
            open_ics_with_default_app(last_created_ics)
        else:
            QMessageBox.information(self, "Keine Datei", "Es wurde keine Datei gefunden oder die Datei existiert nicht.")

    def fetch_defaults(self):
        #Added automatic loading of the timables
        self.refresh()
        self.toggle_defaults_button.setText("Nutze DEFAULTS")
        self.city_edit.setText(self.config_data.get("Stadt/Adresse", ""))
        self.class_edit.setText(self.config_data.get("Klasse", ""))
        self.weeks_spin.setValue(int(self.config_data.get("Wochen", "1")))
        self.on_load_schools_clicked(defaults=True)
        self.fetch_btn.click()
        self.use_defaults = True
        # if self.use_defaults:
            
        # else:
        #     self.refresh()
        #     self.toggle_defaults_button.setText("Nutze KEINE Defaults (klicken zum Umschalten)")
        #     self.city_edit.clear()
        #     self.class_edit.clear()
        #     self.weeks_spin.setValue(1)
        #     self.schools_combo.clear()

    def on_load_schools_clicked(self, defaults):
        #self.log_text.clear()
        debug_mode = (self.config_data.get("Debugging", "False").lower() == "true")
        
        if defaults:
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

        self.found_schools = schools
        school_amount = len(schools)
        for idx, school in enumerate(schools):
            display = f"#{idx} – {school['displayName']} ({school['address']})"
            self.schools_combo.addItem(display, idx)
        
        if defaults:
            schulnummer = int(self.config_data.get("Schulnummer", "0"))
            self.debug_log(f"Schulnummer aus config.env gelesen: {schulnummer}")
            self.schools_combo.setCurrentIndex(schulnummer)
        if school_amount == 1:
            self.schools_combo.setCurrentIndex(0)  # Select first school if only one is found.
        
        self.debug_log(f"{len(schools)} Schulen gefunden und ComboBox gefüllt.")

    def debug_log(self, msg):
        self.log_text.append(msg)

    def refresh(self):
        self.config_data = read_config_env()
        debug_mode = self.config_data.get("Debugging", "False").lower() == "true"
        self.toggle_log_text(debug_mode)

    def toggle_log_text(self, show):
        """Show or hide the log_text textbox."""
        self.log_text_visible = show
        self.log_text.setVisible(show)
    
    def debug_log(self, msg):
        """Log a debug message if debug_mode is enabled."""
        if self.log_text_visible:
            self.log_text.append(msg)

    

    def run_fetch(self):
        """
        Main function to fetch schedule data, perform authentication, and generate ICS files.
        """
        try:
            global debug_mode
            ausbilder_modus = (self.config_data.get("Ausbildermodus", "False").lower() == "true")
            debug_mode = self.config_data.get("Debugging", "False").lower() == "true"
            if debug_mode:
                self.debug_log("DebugMode: " + str(debug_mode))
            self.refresh()
            self.debug_log("Starte Stundenplan-Abruf...")

            # Debug mode check
            if debug_mode:
                self.debug_log("Debugging-Modus aktiviert.")

            # Validate basic config
            name = self.config_data.get("Name", "").strip()
            email = self.config_data.get("Email", "").strip()
            username = self.config_data.get("Username", "").strip()
            password = self.config_data.get("Passwort", "").strip()
            betrieb = self.config_data.get("Betrieb", "").strip()

            if not name or not email or not betrieb:
                QMessageBox.warning(self, "Fehlende Angaben", "Bitte Name, Email und Betrieb in Settings eintragen.")
                return

            week_count = self.weeks_spin.value()

            # Validate selected school
            if not hasattr(self, 'found_schools') or not self.found_schools:
                QMessageBox.information(self, "Keine Schule ausgewählt", "Bitte zuerst auf 'Schulen laden' klicken und eine Schule auswählen.")
                return

            selected_index = self.schools_combo.currentIndex()
            if selected_index < 0:
                QMessageBox.warning(self, "Keine Schule", "Bitte wählen Sie eine Schule aus der Liste.")
                return

            school = self.found_schools[selected_index]
            self.debug_log(f"Ausgewählte Schule: {school['displayName']}")

            # Validate class short name
            class_short = self.class_edit.text().strip()
            if not class_short:
                QMessageBox.warning(self, "Klasse fehlt", "Bitte einen Klassennamen (Kurzname) eingeben.")
                return

            # Initialize session
            session = requests.Session()
            student_info = None  # Initialize student_info as None to handle cases where login fails
            class_id = None # Initialize class_id as None to handle cases where the login is working properly
            student_id = None # Initialize student_id as None to handle cases where login fails

            # Step 1: Perform initial GET request
            init_url = f"https://{school['server']}/WebUntis/?school={school['loginSchool']}"
            r1 = session.get(init_url)
            if debug_mode:
                self.debug_log(f"Initial GET status: {r1.status_code}, Cookies: {session.cookies.get_dict()}")

            jsession_id = session.cookies.get("JSESSIONID")
            trace_id = session.cookies.get("traceId")
            tenant_id = session.cookies.get("Tenant-Id", school.get("tenantId", ""))
            loginName=school["loginSchool"]
            # Fetch CSRF token
            xcrsf_token = get_x_crsf_token(
                server=school["server"],
                loginName=loginName,
                school=school,
                jsession_id=jsession_id,
                trace_id=trace_id,
                debug_mode=debug_mode,
            )

            # Step 2: Perform login
            post_url = f"https://{school['server']}/WebUntis/j_spring_security_check"
            login_params = {
                "school": school["loginSchool"],
                "j_username": username,
                "j_password": password,
                "token": ""
            }
            headers = get_headers(
                tenant_id=tenant_id,
                schoolname=school["loginName"],
                login_name=school["loginSchool"],
                server=school["server"],
                jsession_id=jsession_id,
                trace_id=trace_id,
                xcsrf_token=xcrsf_token,
                method="get_login_headers"
            )

            r2 = session.post(post_url, params=login_params, headers=headers)
            if debug_mode:
                self.debug_log(f"Login POST status: {r2.status_code}, Cookies: {session.cookies.get_dict()}, Data: {r2.json()}")

            # Handle login errors
            data = r2.json()
            if "loginError" in data:
                error_msg = data.get("loginError", "Unbekannter Fehler")
                self.debug_log(f"Login Fehler: {error_msg}. Versuche öffentlichen Login.")
                QMessageBox.critical(self, "Login Fehler", "Login fehlgeschlagen. Zugangsdaten überprüfen.\n Versuche öffentlichen Login!")

                # Step 5: Fetch class list only after login failure
                class_list, error_msg = get_classes(
                    server=school["server"],
                    school={**school, "tenantId": tenant_id},
                    session=session,
                    debug_mode=debug_mode
                )

                if debug_mode:
                    self.debug_log(f"Class list returned: {class_list}, Error: {error_msg}")

                if error_msg:
                    self.debug_log(f"Fehler beim Abrufen der Klassenliste: {error_msg}")
                    QMessageBox.warning(self, "Fehler", f"Konnte keine Klassenliste abrufen: {error_msg}")
                    return

                if not class_list:
                    self.debug_log("Klassenliste ist leer.")
                    QMessageBox.warning(self, "Fehler", "Es wurden keine Klassen gefunden.")
                    return

                # Find matching class
                if debug_mode:
                    self.debug_log(f"Looking for class_short='{class_short}' in class_list: {class_list}")
                matching_class = next((c for c in class_list if c["shortName"] == class_short), None)

                if not matching_class:
                    self.debug_log(f"Klasse '{class_short}' nicht in Klassenliste gefunden: {class_list}")
                    QMessageBox.warning(self, "Fehler", f"Klasse '{class_short}' wurde nicht gefunden.")
                    return

                class_id = matching_class["id"]
                if debug_mode:
                    self.debug_log(f"ClassID: {class_id}")

                # Validate class_id before fetching timetable
                if not class_id:
                    QMessageBox.warning(self, "Fehler", "Keine gültige Klassen-ID gefunden. Stundenplan kann nicht abgerufen werden.")
                    return
            else:
                # Step 3: Fetch bearer token
                bearer_url = f'https://{school["server"]}/WebUntis/api/token/new'
                r3 = session.get(bearer_url, headers=headers)
                bearer_token = r3.text.strip()

                # Login succeeded, fetch student info
                student_info_url = f'https://{school["server"]}/WebUntis/api/rest/view/v1/app/data'
                student_headers = headers | {"Authorization": f"Bearer {bearer_token}"}
                r4 = session.get(student_info_url, headers=student_headers)
                try:
                    student_info = r4.json()
                    
                    if debug_mode:    
                        self.debug_log("StudentInfo: " + str(student_info)[:300])
                    student_name = student_info['user']['person']['displayName']
                    student_name_path = "_".join(student_name.split(" "))
                    self.debug_log(f"Student Name: {student_info['user']['person']['displayName']}, ID: {student_info['user']['person']['id']}")
                except Exception as e:
                    self.debug_log(f"Fehler beim Abrufen der Studentendaten: {e}")
                    student_info = None

                # Determine class ID only if not already set
                if student_info:
                    student_id = student_info["user"]["person"]["id"]
                else:
                    student_id = None

            # Step 6: Fetch timetable data (use class_id if student_id is not available)
            if debug_mode:

                self.debug_log(f"StudentID: {student_id} ClassID: {class_id}")


            all_days = fetch_data_for_next_weeks(
                school={**school, "tenantId": tenant_id},
                class_id=class_id,
                student_id=student_info["user"]["person"]["id"] if student_info and "user" in student_info else None,
                week_count=week_count,
                headers=headers,
                debug_mode=debug_mode,
                debug_log_func=self.debug_log
            )

            if not all_days:
                self.debug_log("Keine Stunden gefunden.")
                return

            # Step 7: Generate ICS file
            ics_path = create_ics_file_for_week(
                school_days_subjects_teachers=all_days,
                schoolname=school["loginName"],
                output_dir=self.config_data.get("Dateipfad", "./"),
                school_data=school,
                name=name,
                student_name_path=student_name_path,
                student_name=student_name,
                betrieb=betrieb,
                email=email,
                ausbilder_modus=ausbilder_modus,
                debug_log_func=self.debug_log,
                create_oof=self.create_oof_box.isChecked()
            )

            if ics_path:
                ret = QMessageBox.question(self, "Öffnen?", "ICS-Datei erfolgreich erstellt.\nICS-Datei öffnen?", QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    open_ics_with_default_app(ics_path)

            if debug_mode:
                version_control(self=self)
                        

        except Exception as e:
            self.debug_log(f"Ein Fehler ist aufgetreten: {e}")
            QMessageBox.critical(self, "Fehler", "Ein unerwarteter Fehler ist aufgetreten. Siehe Log für Details.")
def version_control(self):
    ret = QMessageBox.question(
        self,
        "Builden?",
        "Soll diese Version gebuildet werden?",
        QMessageBox.Yes | QMessageBox.No
    )
    if ret == QMessageBox.Yes:
        self.debug_log("Version wird gebaut...")
        if os.path.exists("./dist/WebLook.exe"):
            os.remove("./dist/WebLook.exe")

        script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        icon_path = os.path.join(script_directory, "assets/icons/normal/webuntisscraper.ico")
        # Increment version in dist/assets/version.txt
        updated_version = self.increment_version_txt(version_file_path=dist_version_file)            
        # Increment version in version.txt
        updated_version = self.increment_version_txt(version_file_path=local_version_file)
        
        # Execute PyInstaller to build the WebLook executable
        os.system(f'pyinstaller main.py --onefile --noconsole --hidden-import=holidays.countries --name WebLook --icon "{icon_path}"')
        # Execute PyInstaller to build the updater executable
                    
        if not os.path.exists("./dist/WebLook.exe"):
                QMessageBox.critical(self, "Fehler","Build failed.")
        else:
            # Copy assets to the build directory
            assets_path = os.path.join(script_directory, "assets")
            build_assets_path = os.path.join(script_directory, "dist", "assets")
            if not os.path.exists(build_assets_path):
                os.makedirs(build_assets_path)
                os.system(f'xcopy "{assets_path}" "{build_assets_path}" /e /h /s /Y')
                QMessageBox.information(self, "Erfolgreich", "Build successful.")

    ret = QMessageBox.question(
        self,
        "Push to Github?",
        "Soll diese Version auf Github gepusht werden?",
        QMessageBox.Yes | QMessageBox.No
    )
    if ret == QMessageBox.Yes:
        push_to_github(self, updated_version, script_directory)

def push_to_github(self, version, repo_path):
    """
    Commits and pushes the latest build (and version file) to GitHub.
    Make sure your local Git is configured with the correct remote and credentials.
    """
    # Move into the repository directory to run Git commands
    original_path = os.getcwd()
    try:
        os.chdir(repo_path)
        
        # Stage all changes; or you can selectively add only what you want (e.g., version.txt, dist/)
        os.system("git add .")
        
        # Commit with a message that includes the version
        os.system(f'git commit -m "Build version {version}"')
        
        # Push to remote (change 'origin' and branch name if needed)
        os.system("git push origin main")
        
        self.debug_log(f"Pushed build version {version} to GitHub.")
    finally:
        # Change back to the original working directory
        os.chdir(original_path)


def main():
    global local_version_file
    local_version_file= "./assets/version.txt"
    global dist_version_file
    dist_version_file= "./dist/assets/version.txt"
    ".dis/assets/version.txt"
    warnings.filterwarnings("ignore", category=DeprecationWarning, module='PyQt5')
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()