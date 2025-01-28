import os
import requests
import zipfile
import shutil

class Updater:
    def __init__(self,
                 local_version_file: str,
                 remote_version_url: str,
                 remote_zip_url: str,
                 target_path: str,  # Pfad, in dem die Update-Dateien installiert werden sollen.
                 download_path: str = "./update_download.zip",
                 extract_path: str = "./update_temp",
                output_method = print):
        """
        :param local_version_file: Pfad zur lokalen version.txt (z.B. "./version.txt").
        :param remote_version_url: URL zum raw-Inhalt der version.txt in deinem GitHub-Repo.
                                   Beispiel: "https://raw.githubusercontent.com/USER/REPO/BRANCH/version.txt"
        :param remote_zip_url: URL zum ZIP-Archiv deines Projekts (z.B. ein Release-ZIP auf GitHub).
        :param download_path: Temporärer Dateiname/ -pfad zum Herunterladen des ZIP-Archivs.
        :param extract_path: Temporärer Ordner, in dem das Archiv entpackt wird.
        """
        self.local_version_file = local_version_file
        self.remote_version_url = remote_version_url
        self.remote_zip_url = remote_zip_url
        self.target_path = target_path
        self.download_path = download_path
        self.extract_path = extract_path
        self.output_method = output_method

    def get_local_version(self) -> str:
        """
        Liest die lokale Version aus der version.txt
        """
        if not os.path.exists(self.local_version_file):
            # Wenn keine lokale Version existiert, 0.0.0 annehmen (oder Exception werfen)
            return "0.0.0"

        with open(self.local_version_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    def get_remote_version(self) -> str:
        """
        Lädt die Versionsnummer aus der version.txt auf GitHub (raw) herunter.
        """
        response = requests.get(self.remote_version_url, timeout=10)
        response.raise_for_status()  # wirft eine Exception bei Fehler
        return response.text.strip()

    def compare_versions(self, local_version: str, remote_version: str) -> bool:
        """
        Vergleicht die Versionen. Gibt True zurück, wenn remote_version > local_version ist.
        Hier ein einfacher Vergleich über die semantischen Versionsteile (major.minor.patch).
        """
        def parse_version(ver: str):
            return list(map(int, ver.split(".")))

        local_parts = parse_version(local_version)
        remote_parts = parse_version(remote_version)

        # Beispielhafter Vergleich: remote > local, wenn an erster ungleicher Stelle remote größer ist
        for l, r in zip(local_parts, remote_parts):
            if r > l:
                return True
            elif r < l:
                return False

        # Falls z. B. "1.0.0" und "1.0.0" oder das Format anders lang ist
        return len(remote_parts) > len(local_parts)

    def download_zip(self) -> None:
        """
        Lädt die ZIP-Datei vom GitHub-Repo herunter und speichert sie unter `download_path`.
        """
        self.output_method("Lade Update ZIP herunter...")
        response = requests.get(self.remote_zip_url, stream=True, timeout=30)
        response.raise_for_status()

        with open(self.download_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        self.output_method(f"ZIP-Datei wurde als '{self.download_path}' gespeichert.")

    def extract_zip(self) -> None:
        """
        Entpackt die heruntergeladene ZIP-Datei in einen temporären Ordner.
        """
        self.output_method("Entpacke ZIP-Datei...")
        if not os.path.exists(self.extract_path):
            os.makedirs(self.extract_path)

        with zipfile.ZipFile(self.download_path, 'r') as zip_ref:
            zip_ref.extractall(self.extract_path)
        self.output_method(f"ZIP-Datei wurde in '{self.extract_path}' entpackt.")

    def replace_files(self, source_dir: str, target_dir: str) -> None:
        """
        Ersetzt alle Dateien aus dem entpackten Ordner in das Zielverzeichnis.
        Achtung: Dabei können lokale Änderungen überschrieben werden.
        """
        self.output_method(f"Kopiere Dateien aus '{source_dir}' nach '{target_dir}'...")
        for root, dirs, files in os.walk(source_dir):
            rel_path = os.path.relpath(root, source_dir)
            dest_path = os.path.join(target_dir, rel_path)

            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_path, file)
                shutil.copy2(src_file, dst_file)
        self.output_method("Dateien wurden erfolgreich aktualisiert.")

    def cleanup(self) -> None:
        """
        Löscht die temporären Download- und Extraktionsdateien/-ordner.
        """
        if os.path.exists(self.download_path):
            os.remove(self.download_path)
        if os.path.exists(self.extract_path):
            shutil.rmtree(self.extract_path)

    def check_for_update(self) -> bool:
        """
        Führt die komplette Update-Logik aus:
        1. Versionsvergleich (lokal vs. remote)
        2. Herunterladen und Ersetzen von Dateien, falls nötig

        :return: True, wenn ein Update ausgeführt wurde, sonst False.
        """
        local_ver = self.get_local_version()
        remote_ver = self.get_remote_version()

        self.output_method(f"Lokale Version: {local_ver}, Remote Version: {remote_ver}")

        if self.compare_versions(local_ver, remote_ver):
            self.output_method("Eine neue Version ist verfügbar! Starte Update...")
            try:
                self.download_zip()
                self.extract_zip()

                # Hier musst du ggf. den entpackten Ordner finden.
                # Oft sind Repos in einen Unterordner entpackt, z.B. "REPO_NAME-main".
                # Beispielhaft gehen wir davon aus, dass alles direkt unter extract_path liegt:
                source_dir = self.extract_path  # oder genauer Pfad, z. B. os.path.join(self.extract_path, "MEINREPO-main")
                target_dir = self.target_path
                self.replace_files(source_dir, target_dir)
                self.output_method("Update erfolgreich abgeschlossen!")
                return True
            finally:
                # Temporäre Dateien/Ordner aufräumen
                self.cleanup()
        else:
            self.output_method("Keine neuere Version gefunden, kein Update nötig.")
        return False


if __name__ == "__main__":
    # Beispiel-Aufruf:
    updater = Updater(
        local_version_file="./assets/version.txt",
        remote_version_url="https://raw.githubusercontent.com/baulum/WebLook/main/assets/version.txt",
        remote_zip_url="https://github.com/baulum/WebLook/archive/refs/heads/main.zip",
        target_path="./",
        download_path="update_download.zip",
        extract_path="update_temp",
        output_method=print  # für Debugzwecke: Ausgabe der Update-Ausgaben
    )
    updater.check_for_update()
