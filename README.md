**Benutzerhandbuch – WebLook: Ihr WebUntis-zu-Outlook-Tool**

Herzlich willkommen zu **WebLook – Number one WebUntis to Outlook Tool!** Mit diesem Programm können Sie Ihren Stundenplan aus WebUntis abrufen und automatisch in Outlook (oder andere Kalender-Programme) integrieren sowie optional eine Abwesenheitsnotiz (Out-of-Office) erstellen lassen. Im Folgenden finden Sie eine kurze Anleitung zur Verwendung.

---

## 1. Programmstart und Hauptmenü

- **Starten Sie das Programm** per Doppelklick auf die entsprechende `.exe`-Datei (Name kann variieren).
- Nach dem Start öffnet sich das **Hauptmenü** (Reiter „Start Menü“).  
  Dort finden Sie eine kurze Übersicht und Anweisungen:  
  1) *Stundenplan abrufen*  
  2) *Einstellungen*  
  3) *Schließen Sie das Fenster*, um das Programm zu beenden

Links in der **Seitenleiste** sehen Sie die drei Hauptbereiche:
1. **Start Menü** (Hauptmenü)
2. **Stundenplan**
3. **Einstellungen**

---

## 2. Einstellungen vornehmen

Bevor Sie Ihren Stundenplan abrufen, sollten Sie sicherstellen, dass Ihre persönlichen Daten und Programmeinstellungen korrekt hinterlegt sind. Gehen Sie hierfür auf den Reiter **„Einstellungen“**.

Dort finden Sie folgende Felder:

1. **Name**  
   *Tragen Sie hier Ihren Namen ein (z. B. „Max Mustermann“).*

2. **Email**  
   *Ihre E-Mail-Adresse, die für die Out-of-Office-Nachricht verwendet werden soll.*

3. **Username**  
   *WebUntis Benutzername.*

4. **Passwort**  
   *WebUntis Passwort.*

5. **Betrieb**  
   *Name des Unternehmens oder der Einrichtung, in der Sie arbeiten.*

6. **Stadt/Adresse**  
   *Ort oder Adresse der Schule/Einrichtung (wird für die Schul-Suche verwendet).*

7. **Klasse**  
   *Die Klassenbezeichnung, z. B. „10A“. (Vermeide „10 A“)*

8. **Schulnummer**  
   *Die Index-Nummer der Schule (erscheint, wenn man Schulen lädt) (z. B. „**#1** – Staatl. Berufsschule I …“ --> **1**). Hier*

10. **Wochen**  
   *Anzahl der Wochen, für die der Stundenplan abgefragt werden soll (z. B. 4).*

11. **Dateipfad**  
   *Datei- bzw. Ordnerpfad, wo die erzeugte Kalenderdatei (.ics Datei) gespeichert wird.*  
   *Sie können den Pfad über das kleine Dateisymbol ändern.*

12. **Debugging**  
   *Wenn aktiviert, zeigt das Programm detailliertere Protokollausgaben an.*  
   *Diese Option ist für Entwickler nützlich.*

Wenn Sie alle Angaben gemacht haben, **klicken Sie auf „Speichern“**, damit Ihre Einstellungen übernommen werden.

---

## 3. Stundenplan abrufen

Wechseln Sie nun zum Reiter **„Stundenplan“**, um Ihren Plan aus WebUntis zu importieren und eine entsprechende Kalenderdatei zu erstellen.

1. **Nutzung der Voreinstellungen**  
   Oben sehen Sie den Schalter **„Nutze DEFAULTS (klicken zum Umschalten)“**.  
   - **Eingeschaltet**: Sobald Sie diese Option aktivieren, werden alle notwendigen Daten (wie Stadt, Schule, Klasse etc.) automatisch aus den Einstellungen übernommen, und der Stundenplan wird **sofort geladen**, ohne dass weitere Eingaben erforderlich sind.  
   - **Ausgeschaltet**: Wenn Sie die DEFAULTS nicht nutzen möchten, können Sie alle Felder manuell ausfüllen (z. B. Stadt, Schule, Klasse etc.).  

2. **Stadt/Adresse**  
   Wenn Sie die DEFAULTS deaktiviert haben, geben Sie hier die gewünschte Stadt ein. Stellen Sie sicher, dass die Adresse korrekt ist, da diese für die Verbindung mit WebUntis benötigt wird.

3. **Schulen laden**  
   Klicken Sie auf **„Schulen laden“**, um die verfügbaren Schulen zu sehen. Wählen Sie dann die richtige Schule aus der Liste aus (z. B. „#1 – Staatl. Berufsschule I …“).  
   - Die Zahl vor der Schule (z. B. „#1“) entspricht der Schulnummer, die auch in den Einstellungen sichtbar ist.

4. **Klasse (Kurzname)**  
   Wenn die DEFAULTS aktiviert sind, wird Ihre Klasse automatisch übernommen (z. B. „IT10D“).  
   - Deaktivieren Sie die DEFAULTS, um eine Klasse manuell einzugeben.  
   - Wenn Sie hier etwas ändern, wird der eingegebene Klassenname vorübergehend genutzt, ohne die gespeicherten Einstellungen zu überschreiben.

5. **Anzahl Wochen (1–25)**  
   Wählen Sie die Anzahl der Wochen aus, für die der Stundenplan abgerufen werden soll (Standard: 4).

6. **Out Of Office Notiz erstellen?**  
   Aktivieren Sie dieses Kontrollkästchen, wenn das Programm automatisch eine Abwesenheitsnotiz in Outlook erstellen soll, die Ihrer E-Mail-Adresse zugeordnet ist.  

   - Im Textfeld unten sehen Sie, für welchen Zeitraum die Out-of-Office-Nachricht erstellt wird und wie sie inhaltlich aussieht.  
   - Dieser Text lässt sich bei Bedarf in den Einstellungen (bzw. im Quellcode) anpassen.

7. **Stundenplan abrufen!**  
   - Klicken Sie auf diese Schaltfläche, um den Plan bei WebUntis abzuholen.  
   - Wenn die DEFAULTS aktiviert sind, wird dieser Schritt automatisch durchgeführt, und der Stundenplan wird geladen.  
   - Das Programm zeigt anschließend in einem Textausgabefeld an, wie viele Stunden gefunden wurden und für welchen Zeitraum.  
   - Im letzten Schritt wird eine **ICS-Datei** erstellt und im *Dateipfad* gespeichert, den Sie unter „Einstellungen“ angegeben haben.

8. **Erfolgreicher Abruf**  
   - Sobald das Programm meldet, dass die Datei erstellt wurde, können Sie diese ICS-Datei im Explorer auffinden.  
   - Sie können die Datei in Outlook (oder einem anderen Kalender-Programm) importieren. 

---

### Zusätzliche Hinweise
- **DEFAULTS aktivieren**: Perfekt für Nutzer, die ihre Daten bereits in den Einstellungen gespeichert haben und keine zusätzlichen Anpassungen vornehmen möchten.  
- **DEFAULTS deaktivieren**: Ideal für Nutzer, die individuelle Eingaben machen möchten oder müssen (z. B. für abweichende Städte oder Klassen).

---

## 4. Abwesenheitsnotiz (Out-of-Office)

Wenn Sie die Option „Out Of Office“ beim Abruf des Stundenplans ausgewählt haben, versucht das Programm:
- Ihren Outlook-Client so zu konfigurieren, dass im angegebenen Zeitraum eine automatische Abwesenheitsnotiz eingerichtet wird.  
- Inhalt der Notiz: Eine generische Höflichkeitsformel, wann Sie wieder erreichbar sind usw.

### Hinweis
Abhängig von Ihrer Outlook-Version und IT-Infrastruktur (z. B. Exchange-Server), kann das automatische Einrichten der Abwesenheitsnotiz eingeschränkt sein.  
Sollte die Funktion nicht wie gewünscht arbeiten, aktivieren Sie ggf. das Debugging und überprüfen Sie die Protokollausgabe, oder richten Sie die Abwesenheitsnotiz manuell in Outlook ein.

---

## 5. Import in Outlook

Nachdem der Stundenplan abgerufen und die .ics-Datei erstellt wurde, erscheint eine **MessageBox**, in der Sie gefragt werden, ob die .ics-Datei **automatisch in Outlook geöffnet** werden soll.

- **Klicken Sie auf „Ja“**, um Outlook direkt zu starten und die .ics-Datei zu öffnen.  
  In Outlook müssen Sie dann nur noch auf **„Importieren“** klicken, um den Stundenplan in Ihren Outlook-Kalender zu übernehmen.

- **Klicken Sie auf „Nein“**, wird die .ics-Datei lediglich gespeichert (siehe Pfad unter „Einstellungen“).  
  Falls Sie zu einem späteren Zeitpunkt importieren möchten, können Sie folgende Schritte in Outlook ausführen:
  1. Öffnen Sie Outlook.  
  2. Wählen Sie **Datei** → **Öffnen und exportieren** → **Importieren/Exportieren**.  
  3. Wählen Sie **„iCalendar (ICS) oder vCalendar-Datei (VCS) importieren“**.  
  4. Navigieren Sie zum Speicherort der .ics-Datei, wählen Sie diese aus und klicken Sie auf **„Importieren“**.

In beiden Fällen ist Ihr Stundenplan nach der Bestätigung direkt in Ihrem Outlook-Kalender sichtbar.

---

## 6. Fehlersuche und Debugging

- Bei Problemen prüfen Sie bitte zuerst:
  1. **Internetverbindung** (für WebUntis-Zugriff nötig).  
  2. **Richtige Schreibweise** von Stadt/Adresse, Schulnummer und Klassenbezeichnung.  
  3. **Korrekter Pfad** zur ICS-Datei.  
  4. **Lese-/Schreibrechte** in dem gewählten Verzeichnis.
- Aktivieren Sie **Debugging** in den Einstellungen, um ausführlichere Log-Informationen zu erhalten.  
- Das Ausgabefeld auf der Seite „Stundenplan“ zeigt Ihnen ebenfalls relevante Meldungen (z. B. gefundene Stunden, Kalenderdatei erstellt usw.). 

---

## 7. Programm beenden

- Um das Programm zu schließen, klicken Sie auf das **X**-Symbol im rechten oberen Fensterrand und schließen Sie das Fenster.  
- Es ist kein spezielles Abmeldeverfahren nötig.

---

## 8. Zusammenfassung

Mit **WebLook** können Sie schnell und bequem Ihren WebUntis-Stundenplan in eine Outlook-kompatible Kalenderdatei umwandeln. Zusätzlich bietet das Tool die Möglichkeit, automatisch eine Abwesenheitsnotiz (Out-of-Office) für den betreffenden Zeitraum einzurichten. Beachten Sie die kurzen Einrichtungsschritte unter „Einstellungen“, passen Sie bei Bedarf den Ausgabepfad für die ICS-Datei an und importieren Sie diese anschließend in Outlook.

---

## 9. Zukünftige Funktionen (Coming Soon)

In zukünftigen Versionen von **WebLook** werden folgende Erweiterungen integriert:

### 9.1 Ausbilder-Modus
- **Gezielter Stundenplan-Abruf für Ausbilder:** Ein Ausbilder kann über diesen Modus sehen, wann der Azubi in der Schule ist.  
- **Reduzierte Stundenplan-Daten:** Statt des gesamten Stundenplans werden lediglich die Zeiträume eingetragen, in denen der Azubi nicht im Betrieb anwesend ist.  
- **Termin-Details:** Im automatisch erstellten Termin wird zusätzlich der **nächste reguläre Arbeitstag** des Azubis vermerkt, damit der Ausbilder direkt sieht, ab wann der Azubi wieder im Betrieb verfügbar ist.

### 9.2 Login-Funktion
- **Erweiterte Authentifizierung:** Da nicht alle Schulen einen öffentlichen WebUntis-Stundenplan anbieten, wird es eine Login-Funktion geben.  
- **Zugriff auf geschützte Stundenpläne:** Mit den entsprechenden Login-Daten können Nutzer auf die Stundenpläne von Schulen zugreifen, die eine Anmeldung erfordern.  
- **Sichere Datenhaltung:** Die Login-Informationen werden verschlüsselt gespeichert und nur für den Abruf der Stundenplandaten verwendet.

Diese Funktionen befinden sich derzeit in Entwicklung und werden Ihnen in einer der kommenden Versionen von **WebLook** zur Verfügung gestellt. Bitte halten Sie das Programm aktuell oder schauen Sie regelmäßig nach Updates, um vom **Ausbilder-Modus** und der **Login-Funktion** profitieren zu können.

**Wir wünschen viel Erfolg bei der Nutzung von WebLook!**  
