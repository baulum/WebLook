![GitHub All Releases](https://img.shields.io/github/downloads/baulum/WebLook/total?style=flat-square)


### Benutzerhandbuch – WebLook: WebUntis zu Outlook Tool

**WebLook** ist Ihr Tool, um Stundenpläne aus WebUntis automatisch in Outlook (oder andere Kalender) zu importieren und bei Bedarf eine Abwesenheitsnotiz (Out-of-Office) zu erstellen. Zusätzlich bietet es jetzt einen **Ausbilder-Modus**. Diese Anleitung hilft Ihnen, schnell loszulegen.

---

## 1. Starten des Programms
1. Öffnen Sie die `.exe`-Datei.  
2. Navigieren Sie im Hauptmenü über die **Seitenleiste**:
   - **Start Menü**: Übersicht und Anweisungen
   - **Stundenplan**: Abruf und Import von WebUntis
   - **Einstellungen**: Persönliche Daten und Programmeinstellungen

---

## 2. Einstellungen
Vor dem Abrufen Ihres Stundenplans sollten alle relevanten Daten eingegeben werden:

- **Name**, **E-Mail**, **WebUntis-Zugangsdaten**
- **Betrieb**, **Stadt**, **Klasse**, **Schulnummer**
- **Wochenanzahl** und **Speicherpfad** für die .ics-Datei
- **Ausbilder-Modus**: Aktivieren Sie diesen Modus, um reduzierte Stundenplan-Daten für Ausbilder zu generieren.
- **Debugging-Modus**: Für detaillierte Protokolle bei Problemen

**Speichern** Sie die Angaben, bevor Sie fortfahren.

---

## 3. Stundenplan abrufen
1. **Nutze DEFAULTS**: Automatische Übernahme aller gespeicherten Daten und direkter Abruf.  
   - **Ausgeschaltet**: Manuelle Eingabe von Stadt, Schule, Klasse usw.
2. **Schulen laden**: Wählen Sie Ihre Schule aus der Liste.
3. **Klasse eingeben**: Automatisch übernommen oder manuell ergänzen.
4. **Wochenanzahl festlegen**: Standard ist 4.
5. **Abrufen**: Starten Sie den Abruf; eine **ICS-Datei** wird erstellt und gespeichert.

---

## 4. Ausbilder-Modus
Wenn der **Ausbilder-Modus** in den Einstellungen aktiviert ist:
- **Reduzierte Kalenderdaten**: Nur die Zeiten, in denen der Azubi in der Schule ist, werden im Kalender eingetragen.
- **Nächster Arbeitstag**: Der nächste reguläre Arbeitstag des Azubis wird automatisch in die Termine aufgenommen.
- **Ausbildungsübersicht**: Dieser Modus hilft Ausbildern, die Präsenzzeiten ihrer Azubis effizient zu planen.

---

## 5. Kalenderimport in Outlook
- Nach dem Abruf erscheint eine **MessageBox**, ob die .ics-Datei in Outlook geöffnet werden soll:
  - **Ja**: Outlook öffnet und importiert die Datei automatisch.
  - **Nein**: Die Datei wird gespeichert und kann später manuell in Outlook importiert werden.

---

## 6. Out-of-Office (OOF)
Wenn aktiviert, erstellt WebLook eine automatische Abwesenheitsnotiz für den Stundenplanzeitraum. Sie sehen den Text vor dem Abruf und können ihn anpassen.

---

## 7. Fehlersuche
- Überprüfen Sie:
  - **Internetverbindung**
  - **Richtige Daten** (Adresse, Klasse, Schulnummer)
  - **Speicherpfad und Berechtigungen**
- Aktivieren Sie den **Debugging-Modus** für detaillierte Protokolle.

---

**WebLook** macht den Stundenplan-Import einfach und schnell – jetzt auch mit **Ausbilder-Modus** für eine noch effizientere Planung. Halten Sie die Anwendung aktuell, um von neuen Funktionen zu profitieren!