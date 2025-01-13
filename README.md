Here's the `README.md` in German for easy copying:

```markdown
# WebLook - Das WebUntis zu Outlook Tool

**WebLook** ist ein praktisches Tool, mit dem du deinen Stundenplan von WebUntis in Outlook importieren kannst. Es ermöglicht dir, den Stundenplan für die nächsten drei Wochen herunterzuladen und als ICS-Datei zu speichern, die dann in Outlook geöffnet werden kann.

## Funktionen

- **Stundenplan abrufen**: Holt den Stundenplan für die nächsten drei Wochen und erstellt eine ICS-Datei.
- **Einstellungen**: Ermöglicht das Bearbeiten von verschiedenen Einstellungen wie der Klasse, der Schulnummer, der Stadt und dem Debugging-Modus.
- **Debugging-Modus**: Schaltet den Debugging-Modus ein oder aus, um detaillierte Ausgaben bei der Fehlerbehebung zu erhalten.

## Anforderungen

- Python 3.x
- Die folgenden Python-Bibliotheken:
  - `requests`
  - `datetime`
  - `urllib.parse`
  - `json`
  - `os`
  - `base64`
  - `python-dotenv`
  - `subprocess`

## Installation

1. Klone das Repository oder lade die Dateien herunter:
   ```bash
   git clone https://github.com/dein-repository-link/WebLook.git
   ```

2. Installiere die erforderlichen Python-Pakete:
   ```bash
   pip install -r requirements.txt
   ```

3. Erstelle eine `.env`-Datei oder bearbeite die `config.env`, um deine Einstellungen zu speichern.

## Verwendung

1. **Starten der Anwendung**:
   ```bash
   python weblook.py
   ```

2. **Menüoptionen**:
   - **1. Stundenplan abrufen**: Lädt den Stundenplan für die nächsten drei Wochen herunter.
   - **2. Einstellungen**: Zeigt das Einstellungsmenü an, in dem du die `STANDARD_KLASSE`, `STANDARD_SCHULNUMMER`, `STANDARD_STADT` und `DEBUGGING` ändern kannst.
   - **3. Beenden**: Beendet das Programm.

3. **Einstellungen anpassen**:
   Du kannst die folgenden Parameter im Einstellungsmenü ändern:
   - **STANDARD_KLASSE**: Die Standardklasse, deren Stundenplan du abrufen möchtest.
   - **STANDARD_SCHULNUMMER**: Die Schulnummer, die für den Abruf des Stundenplans erforderlich ist.
   - **STANDARD_STADT**: Die Stadt, in der sich die Schule befindet.
   - **DEBUGGING**: Setze auf `True`, um detaillierte Debugging-Informationen zu erhalten, oder auf `False`, um den Debugging-Modus zu deaktivieren.

4. **Stundenplan abrufen**:
   Wenn du die Option zum Abrufen des Stundenplans auswählst, wirst du nach der Stadt und der Schulnummer gefragt. Anschließend wird der Stundenplan heruntergeladen und als ICS-Datei erstellt.

5. **ICS-Datei in Outlook öffnen**:
   Nach dem Abrufen des Stundenplans hast du die Möglichkeit, die erstellte ICS-Datei direkt in Outlook zu öffnen.

## Konfigurationsdatei

Die Einstellungen werden in der Datei `config.env` gespeichert. Hier kannst du die Werte für die folgenden Variablen festlegen:

- **STANDARD_KLASSE**: Die Standardklasse (z. B. "10A").
- **STANDARD_SCHULNUMMER**: Die Schulnummer.
- **STANDARD_STADT**: Die Stadt, in der sich die Schule befindet.
- **DEBUGGING**: Setze auf `True`, um den Debugging-Modus zu aktivieren oder auf `False`, um ihn zu deaktivieren.

Ein Beispiel für die `config.env`-Datei:

```
STANDARD_KLASSE=10A
STANDARD_SCHULNUMMER=12345
STANDARD_STADT=Ingolstadt
DEBUGGING=True
```

Wenn die Datei nicht existiert, wird sie automatisch mit den Standardwerten erstellt.

## Fehlerbehebung

- **Fehler bei der Verbindung zu WebUntis**: Stelle sicher, dass die Schulnummer und die Stadt korrekt sind.
- **Fehler beim Erstellen der ICS-Datei**: Überprüfe, ob der Ordner für die Ausgabe vorhanden ist oder ob er mit den richtigen Berechtigungen erstellt werden kann.

## Mitwirkende

- [Dein Name](https://github.com/dein-username)

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE) Datei für Details.
```
