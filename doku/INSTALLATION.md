# SegmentJoinPilot installieren

Diese Anleitung gilt für Version **0.6.2** und beschreibt den Windows-Installer sowie die manuelle Installation unter Windows und macOS.

## Vorbereitung

1. Autodesk Fusion einmal starten, anschließend vollständig schließen.
2. Den Installer bzw. den Quellcode der gewünschten Version aus den [GitHub-Releases](https://github.com/know-how-schmiede/SegmentJoinPilot/releases) herunterladen. Für die manuelle Installation das ZIP vollständig entpacken.
3. Bei einem Update eigene Änderungen am Add-in außerhalb des Installationsordners sichern. Den bisherigen Installationspfad bei Bedarf zuvor im Fusion-Dialog **Skripte und Zusatzmodule** nachsehen.

## Windows: mit Installer

1. `SegmentJoinPilot-Setup-0.6.2.exe` unter dem Windows-Benutzer ausführen, der Fusion verwendet. Administratorrechte sind nicht erforderlich.
2. Den vorgeschlagenen Zielordner prüfen. Je nach Fusion-Installation kommt einer dieser Pfade infrage; `%APPDATA%` lässt sich direkt in die Adresszeile des Explorers eingeben:

   ```text
   %APPDATA%\Autodesk\Autodesk Fusion\API\AddIns\SegmentJoinPilot
   %APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\SegmentJoinPilot
   ```

   Der Installer sucht zuerst vorhandene `API\AddIns`-Ordner, danach die Fusion-Produktordner. Bei Gleichstand bevorzugt er `Autodesk Fusion`; ohne vorhandenen Ordner schlägt er ebenfalls diesen Pfad vor. **Wenn beide Verzeichnisse vorhanden sind, ist die Erkennung nicht eindeutig:** den von Fusion verwendeten Pfad wählen oder das Add-in anschließend manuell registrieren. Der vollständige Zielpfad muss mit `SegmentJoinPilot` enden.
3. Installation abschließen und Fusion neu starten.
4. Das Add-in wie unter **In Fusion aktivieren** beschrieben starten.

Ab 0.6.2 löscht der Installer keine Add-in-Kopie im jeweils anderen Fusion-Pfad mehr. Frühere Installer installierten ausschließlich unter `Autodesk Fusion 360` und entfernten die Kopie unter `Autodesk Fusion`. Falls das Add-in dadurch verschwunden ist, Version 0.6.2 im passenden Pfad installieren.

## Windows: von Hand

1. Im entpackten Download den Ordner `fusion_addin/SegmentJoinPilot` öffnen.
2. Den **gesamten Ordner `SegmentJoinPilot`** einschließlich aller Unterordner in das passende `API\AddIns`-Verzeichnis aus dem vorherigen Abschnitt kopieren. Nicht das gesamte Repository und nicht nur die Python-Datei kopieren.
3. Die Struktur prüfen:

   ```text
   API/AddIns/SegmentJoinPilot/
     SegmentJoinPilot.py
     SegmentJoinPilot.manifest
     version.py
     commands/
     lib/
     ... weitere mitgelieferte Dateien und Ordner
   ```

4. Fusion neu starten und das Add-in aktivieren.

Alternativ den vollständigen Add-in-Ordner an einem dauerhaften Ort ablegen und über **Skripte und Zusatzmodule > Zusatzmodule > +** als vorhandenes Add-in hinzufügen. Den Ordner `SegmentJoinPilot` auswählen; falls die Fusion-Version eine Datei verlangt, `SegmentJoinPilot.py` darin wählen. Den registrierten Ordner danach nicht verschieben. Autodesk beschreibt sowohl die Standardpfade als auch die [Registrierung an einem anderen Speicherort](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UsingSamplesFromGitHub_UM.htm).

## macOS: von Hand — nicht getestet

**Diese macOS-Installationsanleitung wurde nicht getestet, da kein Mac zur Verfügung steht. Auch die Funktion des Add-ins unter macOS wurde hier nicht praktisch geprüft.** Der Windows-Installer (`.exe`) ist dafür nicht geeignet.

1. Fusion schließen und das Quellcode-ZIP der gewünschten Version entpacken.
2. Im Finder **Gehe zu > Gehe zum Ordner …** öffnen (`Umschalt + Command + G`). Den von Autodesk dokumentierten Benutzerpfad eingeben:

   ```text
   ~/Library/Application Support/Autodesk/Autodesk Fusion/API/AddIns
   ```

   Falls die lokale Installation noch den Produktordner `Autodesk Fusion 360` verwendet, diesen entsprechenden Pfad prüfen:

   ```text
   ~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns
   ```

3. Den vollständigen Ordner `fusion_addin/SegmentJoinPilot` aus dem Download nach `AddIns` kopieren. Fehlende `API`-/`AddIns`-Unterordner können im passenden Benutzerpfad angelegt werden. Die Ordnerstruktur muss der oben gezeigten entsprechen.
4. Fusion starten und das Add-in aktivieren. Wird es nicht gefunden, den kopierten Ordner über **Zusatzmodule > +** registrieren. Alternativ direkt einen dauerhaften Ordner verwenden.

`~` bezeichnet den eigenen Benutzerordner; die Library kann im Finder verborgen sein. Die Grundlage für den Standardpfad ist die [Autodesk-Anleitung für Windows und macOS](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UsingSamplesFromGitHub_UM.htm).

## In Fusion aktivieren

1. **Dienstprogramme > Skripte und Zusatzmodule** öffnen, je nach Oberfläche auch über die Suche mit `S` erreichbar (englisch: **Utilities > Scripts and Add-Ins**).
2. Den Reiter **Zusatzmodule / Add-Ins** wählen und `SegmentJoinPilot` auswählen. Falls nötig, mit **+** hinzufügen.
3. **Ausführen / Run** wählen. Für automatisches Laden **Beim Start ausführen / Run on Startup** aktivieren. Im ausgelieferten Manifest ist der automatische Start zunächst deaktiviert.
4. In einer Konstruktion im Bereich **Volumenkörper > Erstellen** nach **SegmentJoinPilot 0.6.2** suchen.

Die Verwaltung über den Zusatzmodule-Dialog ist in der [Autodesk-Hilfe](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MANAGE-SCRIPTS-ADD-INS.htm) beschrieben.

## Kurze Fehlerhilfe

| Problem | Was prüfen bzw. tun? |
| --- | --- |
| Add-in erscheint nicht in der Liste | Reiter **Zusatzmodule** statt **Skripte** wählen, Fusion neu starten, beide Fusion-Pfade prüfen und den vollständigen Add-in-Ordner über **+** registrieren. |
| Add-in ist gelistet, aber kein Befehl sichtbar | **Ausführen** anklicken, eine Konstruktion öffnen und unter **Volumenkörper > Erstellen** suchen. Für künftige Starts **Beim Start ausführen** aktivieren. |
| Nach dem Update erscheint noch die alte Version oder das Add-in doppelt | In den Eintragsdetails die Pfade prüfen. Fusion schließen, alte Kopien außerhalb beider `AddIns`-Ordner sichern und nur die gewünschte Kopie registrieren bzw. starten. Ein Update ersetzt nur Dateien im gewählten Zielordner. |
| Meldung „The script and manifest do not have the same name as the folder“ | Ordner muss `SegmentJoinPilot` heißen und direkt `SegmentJoinPilot.py` sowie `SegmentJoinPilot.manifest` enthalten. Eine zusätzliche ZIP-Ordnerebene entfernen; vollständige Unterordner beibehalten. Siehe [Autodesk-Fehlerbeschreibung](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Failed-to-add-script-The-script-and-manifest-do-not-have-the-same-name-as-the-folder-error-in-Fusion.html). |
| Fehlende Python-Module oder Ressourcen beim Start | Vollständiges Paket derselben Version erneut installieren. Das Add-in innerhalb von Fusion starten; ein Start mit normalem Python außerhalb von Fusion findet die Fusion-API `adsk` nicht. |
| Zugriff verweigert beim Installieren | Fusion schließen, unter dem eigenen Benutzer installieren und einen beschreibbaren Benutzerpfad wählen. |
| `Create Group Feature Error: At least 2 features needed for a group` oder `InternalValidationError: res >= 0` | Diese Fehler wurden während früherer Entwicklungstests dokumentiert und korrigiert. Auf 0.6.2 aktualisieren und alte geladene Kopien ausschließen. Bei erneutem Auftreten vollständige Meldung und Arbeitsschritte melden; siehe [Implementierungsprotokoll](IMPLEMENTATION_LOG.md). |
| Verbindererzeugung scheitert wegen fehlender aktueller Fläche / Skizzenebene | Version 0.6.1 hat die Ermittlung der aktuellen Trennfläche korrigiert; 0.6.2 enthält diese Änderung. Der Fusion-Praxistest dieser Korrektur steht laut Projektprotokoll noch aus. Zugehörige Segmentkörper und Positionsskizze prüfen und den vollständigen Traceback melden, falls der Fehler bleibt. |

Für einen [Fehlerbericht](https://github.com/know-how-schmiede/SegmentJoinPilot/issues) bitte Betriebssystem, Fusion-Version, Add-in-Version, Installationspfad, genaue Schritte und vollständige Fehlermeldung angeben. Bei Installerproblemen hilft das Setup-Protokoll: Der Installer aktiviert Logging; die Datei liegt normalerweise als `Setup Log … .txt` im Windows-Temp-Ordner (`%TEMP%`).

## Update und Entfernen

Vor jedem Update Fusion schließen. Beim Installer den bisherigen aktiven Pfad bewusst prüfen; bei manueller Installation die alte Kopie außerhalb des Add-in-Pfads sichern und durch den vollständigen neuen Ordner ersetzen. Keine Versionen mischen.

Eine Installer-Installation über die Windows-Einstellungen unter **Apps > Installierte Apps > SegmentJoinPilot** deinstallieren. Manuell installierte Kopien nach dem Beenden von Fusion aus ihrem jeweiligen Add-in-Ordner entfernen. Weitere Kopien in anderen Pfaden werden vom Installer nicht automatisch bereinigt.
