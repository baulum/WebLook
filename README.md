### WebLook – German  User Guide

**Version**: 1.1  
**Stand**: 2025-01-20

---

## Inhaltsverzeichnis
1. [Einleitung](#einleitung)  
2. [Voraussetzungen und Installation](#voraussetzungen-und-installation)  
3. [Erster Start](#erster-start)  
4. [Hauptmenü](#hauptmenü)  
5. [Stundenplan abrufen](#stundenplan-abrufen)  
6. [Einstellungen](#einstellungen)  
7. [ICS-Datei und Out-of-Office erstellen](#ics-datei-und-out-of-office-erstellen)  
8. [Bekannte Probleme & Tipps](#bekannte-probleme--tipps)  
9. [Kontakt & Support](#kontakt--support)  

---

## 1. Einleitung
**WebLook** ist ein einfaches Konsolenprogramm, das Ihnen ermöglicht, Stundenpläne von *WebUntis* abzurufen, als ICS-Datei zu generieren und bei Bedarf direkt in Outlook (oder einem anderen Kalenderprogramm) zu öffnen. Darüber hinaus bietet WebLook die Möglichkeit, eine Out-of-Office-Nachricht (Abwesenheitsnotiz) in die erstellte Kalenderdatei einzufügen.

---

## 2. Voraussetzungen und Installation
1. **Python 3**: Stellen Sie sicher, dass auf Ihrem System Python 3 installiert ist.  
2. **Abhängigkeiten**: Das Skript nutzt folgende Python-Bibliotheken:
   - `requests`  
   - `termcolor`
   - `pyinstaller`  
   - `datetime` (Teil der Standardbibliothek)  
   - `subprocess` (Teil der Standardbibliothek)  
   - `os`, `json`, `re`, `base64`, `urllib.parse` (alle Teil der Standardbibliothek)  

   Um fehlende Pakete zu installieren (z.B. `requests`, `termcolor`, `pyinstaller`), verwenden Sie:
   ```bash
   pip install -r requirements.txt
   ```

3. **Dateistruktur**:  
   - Hauptskript: `main.py` (oder wie auch immer Sie die Datei benannt haben)  
   - Eine Konfigurationsdatei `config.env` (falls nicht vorhanden, wird sie automatisch angelegt).  

---

## 3. Erster Start
1. **Skript ausführen**:  
   ```bash
   start.bat
   ```
2. Nach dem Start erscheint ein *ASCII-Art*-Logo sowie das **Hauptmenü** mit den Optionen:
   1. Fetch Timetable  
   2. Settings  
   3. Exit  

---

## 4. Hauptmenü
Im Hauptmenü werden Ihnen drei Optionen angezeigt:  

1. **Fetch Timetable**  
   - Hier rufen Sie den Stundenplan von *WebUntis* ab.  

2. **Settings**  
   - Verwalten Sie Ihre Konfiguration wie *Name*, *E-Mail* oder *Standardwerte* (z.B. Stadt, Klasse).  

3. **Exit**  
   - Beendet das Programm.  

Wählen Sie die gewünschte Option durch Eingabe der entsprechenden Zahl (1, 2 oder 3).

---

## 5. Stundenplan abrufen
Wählen Sie dazu im Hauptmenü die Option **1. Fetch Timetable**.

1. **Nutzerdaten abfragen**  
   - Falls noch nicht in der `config.env` hinterlegt, fragt das Programm Ihren Namen, Ihre E-Mail-Adresse und Ihren Betriebsnamen ab.  
   - Anschließend können Sie entscheiden, ob Sie *Standardeinstellungen* verwenden möchten.  

2. **Angabe der Stadt**  
   - Geben Sie den Namen der Stadt ein, in der Ihre Schule liegt (z.B. *Ingolstadt*).  
   - Sie werden gefragt, ob diese Stadt als Standard gespeichert werden soll. Bei *Y* wird dieser Wert fortan automatisch genutzt.  

3. **Schulauswahl**  
   - Nach Eingabe der Stadt wird eine Liste mit allen gefundenen Schulen angezeigt.  
   - Sie wählen eine **Schulnummer** (Index aus der Liste), die zur gewünschten Schule passt.  
   - Sie können diese Schulnummer ebenfalls als Standard speichern.  

4. **Klasse auswählen**  
   - Das Programm listet alle gefundenen Klassen auf.  
   - Geben Sie den Kurznamen Ihrer Klasse an (z.B. `10A`).  
   - Auch hier können Sie den Klassennamen als Standard speichern.  

5. **Zeitraum festlegen**  
   - Sie werden gefragt, wie viele **Wochen** im Voraus Sie den Stundenplan abrufen möchten.  
   - Zum Beispiel `2` (für die nächsten 2 Wochen).  

6. **ICS-Datei erstellen**  
   - Das Programm erzeugt eine einzige `.ics`-Datei mit allen Stunden der gewählten Wochen.  
   - Anschließend fragt das Programm, ob Sie die Datei direkt in Outlook oder einer anderen Standard-Kalenderanwendung öffnen möchten.  
   - Nach Bestätigung wird `.ics` mit dem Standardprogramm geöffnet.  

---

## 6. Einstellungen
Wählen Sie im Hauptmenü die Option **2. Settings**, um Ihre Konfiguration einzusehen oder zu ändern. Das Einstellungsmenü bietet folgende Unterpunkte:

1. **View current settings**: Zeigt die aktuellen Werte (NAME, EMAIL, BETRIEB, STADT, KLASSE, SCHULNUMMER, DEBUGGING) an.  
2. **Update Name**: Ändert den gespeicherten Namen (z.B. *Max Mustermann*).  
3. **Update Email**: Ändert die gespeicherte E-Mail-Adresse.  
4. **Update Betrieb**: Ändert den Namen Ihres Betriebs.  
5. **Update STANDARD_STADT**: Setzt die Stadt, in der Ihre Schule liegt.  
6. **Update STANDARD_KLASSE**: Speichert den Klassennamen als Standard.  
7. **Update STANDARD_SCHULNUMMER**: Speichert die gewählte Schulnummer als Standard.  
8. **Update DEBUGGING**: Schaltet den Debug-Modus ein/aus (*True* / *False*).  
9. **Back to Main Menu**: Kehrt ins Hauptmenü zurück.

**Hinweise**:  
- Änderungen werden sofort in die `config.env` geschrieben.  
- Debugging-Modus: Wenn *True*, werden zusätzliche Log-Ausgaben im Terminal angezeigt (z.B. API-URLs, Cookies etc.).

---

## 7. ICS-Datei und Out-of-Office erstellen
Während des Vorgangs **Stundenplan abrufen** werden Sie nach dem Generieren der ICS-Datei gefragt, ob Sie eine *Out Of Office (OOF)*-Notiz erstellen möchten.  

- **Wenn ja** (*Y*):  
  - Das Programm fügt in die `.ics`-Datei einen **zusätzlichen Kalendereintrag** mit **Abwesenheitsinformationen** hinzu.  
  - Diese Informationen enthalten eine mehrzeilige Nachricht, Ihren Namen, E-Mail und ggf. Betriebsdaten.  

- **Wenn nein** (*N*):  
  - Die `.ics`-Datei enthält ausschließlich Ihre Unterrichtstermine.

Durch Öffnen der `.ics`-Datei in Outlook oder einem anderen Kalenderprogramm werden die OOF-Daten (und der Termin) in Ihrem Kalender angezeigt.

---

## 8. Bekannte Probleme & Tipps
1. **Keine Schule gefunden**: Wenn für Ihre Stadt keine Schulen erscheinen, überprüfen Sie die Schreibweise und Internetverbindung.  
2. **Ungültige Klasse**: Achten Sie auf den exakten Kurznamen (z.B. `10A`, `FI10a` etc.).  
3. **ICS-Datei öffnet sich nicht in Outlook**:  
   - Unter Windows kann es nötig sein, `.ics`-Dateien manuell mit Outlook zu verknüpfen.  
4. **Fehlermeldungen beim Anfordern von Daten**:  
   - Prüfen Sie, ob `DEBUGGING=True` gesetzt ist, um zusätzliche Hinweise zu sehen (z.B. falsche Schul-ID, Netzwerkfehler).  
