# SegmentJoinPilot – Codex Project Plan

## Auftrag

Implementiere auf Basis eines von Fusion erzeugten leeren Python-Add-ins das Projekt SegmentJoinPilot. Das Add-in teilt einen ausgewählten Volumenkörper mit einer Konstruktionsebene und erzeugt an ausgewählten Skizzenpunkten separate Verbinderkörper sowie toleranzbehaftete Vertiefungen in beiden entstandenen Segmenten.

Diese Datei beschreibt den gewünschten Zielzustand. Vor Änderungen muss Codex die tatsächlich erzeugte Add-in-Struktur, vorhandene Dateien und die verwendete Fusion-API-Version untersuchen. Bestehende Autodesk-Start-/Stop-Logik soll erhalten bleiben und schrittweise erweitert werden.

## Verbindliche Projektvorgaben

- Das Add-in und alle sichtbaren Oberflächentexte werden zunächst in Englisch entwickelt.
- Die Architektur muss eine spätere Lokalisierung nach Deutsch, Französisch, Spanisch und Polnisch ermöglichen. Sichtbare Texte dürfen deshalb nicht unnötig über die Programmlogik verteilt werden.
- Der Befehl wird im Fusion-Arbeitsbereich `Solid` im Menü beziehungsweise Toolbar-Panel `Create` angezeigt.
- Für das Add-in werden eigenständige, zum Funktionsumfang und zur Marke passende Icons in allen von Fusion benötigten Größen erstellt und eingebunden.
- Die Versionsnummer wird zentral in `version.py` gepflegt und sowohl in der Titelzeile des Dialogfensters als auch im Menüeintrag angezeigt.
- Die Versionsangabe der `*.manifest`-Datei muss bei jeder freigegebenen Versionsänderung mit `version.py` übereinstimmen.
- Eine neue Versionsnummer wird ausschließlich nach ausdrücklicher Vorgabe des Projektverantwortlichen begonnen. Codex darf die Versionsnummer nicht selbstständig erhöhen.
- Jede funktionale Änderung wird als kleiner, einzeln prüfbarer Schritt umgesetzt. Nach jedem Schritt folgt ein Test in Fusion und die Bestätigung des Projektverantwortlichen, bevor der nächste Schritt begonnen wird.
- Alle umgesetzten Änderungen, Fusion-Testschritte, Testergebnisse und bekannten Einschränkungen werden im Ordner `doku/` dokumentiert.

## MVP-Abnahmekriterien

Der MVP gilt als abgeschlossen, wenn:

1. Ein einzelner Solid-BRep-Körper und eine ihn schneidende Konstruktionsebene ausgewählt werden können.
2. Der Körper reproduzierbar in genau zwei Solid-Körper geteilt wird.
3. Eine Skizze auf der Schnittfläche gewählt werden kann.
4. Mindestens ein und beliebig viele gültige Skizzenpunkte verarbeitet werden.
5. Runde, D-förmige, ovale, abgerundet rechteckige und sechseckige Verbinder erzeugt werden können.
6. Alle Verbinder entlang der lokalen Flächennormalen ausgerichtet sind.
7. Für beide Segmente passende, toleranzbehaftete Taschen erzeugt werden.
8. Die Verbinder als separate Körper erhalten bleiben.
9. Standard- und benutzerdefinierte Toleranzen funktionieren.
10. Eine Vorschau ohne dauerhafte Timeline-Reste möglich ist.
11. Abbruch und ungültige Eingaben keine halbfertige Geometrie hinterlassen.
12. Erzeugte Features konsistent benannt und in einer Timeline-Gruppe organisiert werden.

## Nicht Bestandteil des MVP

- mehrere Schnittebenen in einem Dialoglauf
- automatische Verbinderpositionierung
- Magnet-, Schraub- oder Schwalbenschwanzverbindungen
- STL-/3MF-Stapelexport
- nachträgliches parametrisches Bearbeiten eines abgeschlossenen Vorgangs
- Unterstützung von Mesh-Körpern

## Vorgeschlagene Architektur

Die genauen Modulnamen dürfen an das erzeugte Fusion-Gerüst angepasst werden.

```text
src/
├── SegmentJoinPilot.py             # Add-in entry points: run(context), stop(context)
├── version.py                      # Zentrale, vom Projektverantwortlichen freigegebene Version
├── commands/
│   └── create_segment_join/
│       ├── entry.py                # Command registration and event handlers
│       ├── dialog.py               # Inputs, visibility rules and validation messages
│       ├── preview.py              # Temporary preview lifecycle
│       └── execute.py              # Transaction-like orchestration
├── core/
│   ├── models.py                   # Typed settings and operation result objects
│   ├── validation.py               # Selection and dimensional checks
│   ├── units.py                    # Explicit unit conversion
│   ├── naming.py                   # Stable feature/body naming
│   └── attributes.py               # Fusion attribute schema
├── geometry/
│   ├── split_body.py               # Split operation and result identification
│   ├── section_faces.py            # Detect faces created by the split
│   ├── profiles.py                 # 2D connector profile construction
│   ├── connectors.py               # Connector solid generation
│   ├── sockets.py                  # Clearance tools and pocket cuts
│   └── transforms.py               # Local plane coordinate systems
└── resources/
    └── create_segment_join/
        ├── 16x16.png
        ├── 32x32.png
        └── 64x64.png
```

## Datenmodell

Mindestens folgende Einstellungen sollten in einer eigenen Datenklasse zusammengefasst werden:

```python
ConnectorSettings(
    shape,
    width,
    height,
    total_length,
    insertion_depth_a,
    insertion_depth_b,
    radial_clearance,
    depth_clearance,
    corner_radius,
    lead_in_type,
    lead_in_length,
    selected_point_ids,
)
```

Keine Geometriefunktion sollte Werte direkt aus Dialogelementen lesen. Der Event Handler überführt die Eingaben zuerst in ein validiertes Einstellungsobjekt.

## Befehlsdialog

### Gruppe „Split"

- Auswahl eines Solid-Körpers
- Auswahl einer Konstruktionsebene
- optionaler Name des Vorgangs

### Gruppe „Positions"

- Auswahl einer Skizze auf der Schnittfläche
- Liste oder Anzahl erkannter Skizzenpunkte
- Umschaltung zwischen allen und ausgewählten Punkten
- Automatisch erkannte Punkte sind zunächst auswählbare Kandidaten und keine zwingend zu verarbeitende Menge.
- Einzelne Kandidaten können vor der Geometrieerzeugung gezielt aktiviert oder deaktiviert werden.
- Der Benutzer kann zusätzlich eigene freie Punkte in der Positionsskizze anlegen und auswählen.
- Für typische Vierpunkt-Anordnungen, etwa die Ecken eines Rechtecks, muss eine diagonale Zweipunktauswahl möglich sein.
- Die endgültige Auswahl muss im Dialog eindeutig erkennbar sein und darf nur diese Punkte an die Connector-Pipeline übergeben.

### Gruppe „Connector"

- Form: Round, D-shaped, Oval, Rounded Rectangle, Hexagon
- Breite beziehungsweise Durchmesser
- Höhe für ovale oder rechteckige Formen
- Gesamtlänge
- Einstecktiefe A und B
- Eckradius, nur wenn für die Form relevant
- Einführfase oder konischer Anschnitt

### Gruppe „Fit"

- Press Fit
- Tight
- Standard
- Loose
- Custom
- Spiel pro Seite
- Tiefenzugabe

### Gruppe „Output"

- separate Verbinderkörper erzeugen, im MVP standardmäßig aktiv
- Vorschau aktivieren

Dialogelemente, die für eine Form nicht benötigt werden, sollen dynamisch ausgeblendet oder deaktiviert werden.

## Geometrie-Pipeline

1. Aktives Design und Root Component prüfen.
2. Körper, Ebene und Skizze validieren.
3. Prüfen, ob die Ebene den Körper tatsächlich schneidet.
4. SplitBodyFeature erzeugen.
5. Die beiden Ergebnis-Solids erfassen, ohne fragile Indexannahmen zu verwenden.
6. Die neu entstandenen planaren Schnittflächen geometrisch über Ebene, Punktabstand und Normalenrichtung bestimmen.
7. Ein lokales 2D-Koordinatensystem auf der Schnittfläche aufbauen.
8. Jeden Skizzenpunkt in dieses System übertragen.
9. Das gewählte 2D-Profil erzeugen.
10. Entlang der Flächennormalen einen separaten prismatischen Verbinder erstellen.
11. Einführfasen oder kurze konische Anschnitte anbringen.
12. Für Seite A und B jeweils eine toleranzbehaftete Werkzeuggeometrie erstellen.
13. Taschen aus beiden Segmenten schneiden; Werkzeugkopien anschließend entfernen.
14. Originalverbinder behalten und benennen.
15. Features und Körper gruppieren und Attribute speichern.

## Robustheit

- Keine dauerhaften Referenzen über Listenindex oder automatisch generierte Namen aufbauen.
- Planare Schnittflächen über Geometrie und Toleranzen identifizieren.
- Für persistente Metadaten Fusion Attributes verwenden.
- Vor Boolean-Operationen prüfen, ob Werkzeug und Zielkörper sich tatsächlich schneiden.
- Bei mehreren Punkten jeden Fehler mit Punktnummer und Ursache melden.
- Wenn ein Vorgang teilweise fehlschlägt, alle in diesem Vorgang erzeugten Elemente kontrolliert zurückrollen oder löschen.
- Preview-Geometrie darf nach Eingabeänderung, Abbruch oder Dialogende keine Artefakte hinterlassen.

## Benennung und Attribute

Beispielnamen:

```text
SJP_Operation_001
SJP_Segment_A_001
SJP_Segment_B_001
SJP_PositionSketch_001
SJP_Connector_001_01
SJP_Connector_001_02
SJP_Socket_A_001_01
SJP_Socket_B_001_01
```

Attributgruppe: `SegmentJoinPilot`

Empfohlene Attribute:

- `schemaVersion`
- `operationId`
- `role` (`segment`, `connector`, `socket`, `positionSketch`)
- `connectorIndex`
- `shape`
- `clearance`

## Wiederverwendbarer Installer- und Distributionsstandard

Dieser Abschnitt ist bewusst projektübergreifend formuliert und soll bei weiteren
Autodesk-Fusion-Plug-ins als Ausgangsbasis verwendet werden.

### Windows-Installer

- Für Windows wird vorzugsweise ein reproduzierbares Inno-Setup-Skript unter
  `installer/<PluginName>.iss` angelegt.
- Ein Buildskript unter `installer/build-installer.ps1` prüft vor dem Kompilieren,
  dass Installer, `version.py` und `*.manifest` dieselbe freigegebene Version verwenden.
- Die fertige, versionsgebundene EXE wird unter
  `installer/dist/<PluginName>-Setup-<Version>.exe` erzeugt.
- Der Installer wird nur nach ausdrücklicher Aufforderung des Projektverantwortlichen
  kompiliert beziehungsweise neu gebaut. Eine Versionsänderung oder funktionale
  Änderung allein ist keine Freigabe zum Erzeugen einer neuen EXE.
- Ohne ausdrücklichen Build-Auftrag dürfen Installer-Definition und dokumentierte
  Versionsangaben vorbereitet werden; vorhandene Dateien unter `installer/dist/`
  bleiben jedoch unverändert.
- Die Inno-Setup-`AppId` bleibt über alle Versionen desselben Plug-ins stabil, damit
  Updates und Deinstallation derselben Anwendung zugeordnet werden.
- Eine normale Einzelplatzinstallation erfolgt benutzerbezogen mit
  `PrivilegesRequired=lowest`; ein Benutzername oder ein absolutes `C:\Users\...`
  darf niemals fest im Installer stehen.
- Für den benutzerbezogenen Basisordner wird die Inno-Setup-Konstante
  `{userappdata}` verwendet. Sie wird auf jedem Rechner für das Konto aufgelöst,
  unter dem das Setup ausgeführt wird.
- Das Setup muss unter demselben Windows-Konto ausgeführt werden, unter dem Fusion
  verwendet wird. Umgeleitete AppData-Verzeichnisse in Firmenumgebungen werden durch
  `{userappdata}` grundsätzlich unterstützt, sofern dort Schreibrechte bestehen.

### Fusion-Add-in-Pfad

- Der konkrete automatisch durchsuchte Add-in-Pfad ist vor dem Release auf einer
  realen Zielinstallation zu prüfen. Je nach Fusion-Installation beziehungsweise
  Produktgeneration können insbesondere diese Ordner vorkommen:

  ```text
  %APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns
  %APPDATA%\Autodesk\Autodesk Fusion\API\AddIns
  ```

- Ein auf dem Entwicklungsrechner funktionierender Pfad darf nicht ungeprüft als
  universell gültig angenommen werden. Zusätzlich kann Fusion in den API-Einstellungen
  einen benutzerdefinierten Standardpfad verwenden.
- Der robuste Zielzustand für weitere Installer ist: vorhandene bekannte Fusion-Pfade
  erkennen, den tatsächlich verwendeten Pfad bevorzugen und bei keiner oder mehreren
  eindeutigen Erkennungen eine sichtbare Zielauswahl anbieten.
- Bis eine automatische Erkennung implementiert ist, verwendet jedes Projekt den auf
  seiner Zielinstallation bestätigten Pfad und dokumentiert die bekannte Einschränkung.
- Wird ein fehlerhafter Zielpfad in einem späteren Installer korrigiert, muss geprüft
  werden, ob Inno Setup den alten Pfad aus einer vorherigen Installation übernimmt.
  Bei einer bewusst erzwungenen Pfadkorrektur ist beispielsweise
  `UsePreviousAppDir=no` zu setzen oder eine kontrollierte Migration umzusetzen.
- Veraltete Installationsordner dürfen nur mit einem exakt auf Plug-in-Name und
  bekanntes Altverzeichnis begrenzten Cleanup entfernt werden. Übergeordnete
  `AddIns`- oder Autodesk-Verzeichnisse dürfen niemals rekursiv gelöscht werden.
- Der Plug-in-Ordner muss direkt die gleichnamige Python-Einstiegsdatei und das
  gleichnamige Manifest enthalten; eine versehentliche zusätzliche Verzeichnisebene
  verhindert die automatische Erkennung durch Fusion.

### Paketinhalt und Git

- Der Installer enthält nur die für Fusion erforderlichen Laufzeitdateien. Mindestens
  `.vscode`, `__pycache__`, `*.pyc`, `*.pyo`, lokale Logs und temporäre Builddateien
  werden ausgeschlossen.
- Installer-Quellen, Buildskripte und Buildanleitungen werden versioniert.
- Generierte Binärdateien und Logs werden in `.gitignore` explizit ausgeschlossen,
  beispielsweise mit `installer/dist/` und `installer/*.log`.
- Falls eine allgemeine Python-`.gitignore` `*.manifest` ausschließt, wird das benötigte
  Fusion-Manifest gezielt wieder aufgenommen, zum Beispiel mit
  `!fusion_addin/<PluginName>/<PluginName>.manifest`.
- Nach jeder `.gitignore`-Änderung wird mit `git check-ignore` geprüft, dass die EXE
  ignoriert wird, Installer- und Buildskript aber weiterhin versionierbar sind.
- Für jede fertige EXE werden Dateigröße und SHA-256-Prüfsumme dokumentiert.
- Vor öffentlicher Verteilung ist eine Authenticode-Signatur zu empfehlen. Ohne
  Signatur kann Windows SmartScreen trotz technisch korrektem Installer warnen.

### Installer-Abnahmetest

1. Fusion schließen und Installation ohne Administratorrechte ausführen.
2. Den tatsächlichen Zielpfad und die Verzeichnisstruktur kontrollieren.
3. Fusion neu starten und prüfen, dass das Plug-in automatisch gefunden wird.
4. Mindestens einen vollständigen Plug-in-Arbeitsablauf ausführen.
5. Ein Update über eine vorhandene ältere Version testen; dabei Zielpfad und
   verbleibende Altdateien prüfen.
6. Über Windows-Einstellungen deinstallieren und ausschließlich die installierten
   Plug-in-Dateien als entfernt bestätigen.
7. Den Test nach Möglichkeit mit einem zweiten Windows-Benutzerkonto oder auf einem
   zweiten Rechner wiederholen.
8. Sonderfälle dokumentieren: benutzerdefinierter Fusion-API-Pfad, umgeleitetes
   AppData, fehlende Schreibrechte und parallele Fusion-Installationen.

## Entwicklungsphasen

Die folgenden Phasen sind eine Reihenfolge, keine zusammenhängenden Implementierungsblöcke. Jeder Aufzählungspunkt ist als eigener Arbeitsschritt zu behandeln: implementieren, außerhalb von Fusion prüfen, in `doku/` dokumentieren, in Fusion testen und erst nach Bestätigung fortfahren.

### Phase 0 – Bestand aufnehmen

- Leeres Fusion-Add-in untersuchen
- Manifest, Entry Points, Command-Framework und Ressourcenpfade dokumentieren
- Aktuelle Versionsnummer in Add-in und `*.manifest` erfassen, ohne sie zu ändern
- Add-in unverändert starten und stoppen
- Minimalen Smoke-Test festhalten

### Phase 1 – Command und Auswahl

- Passende Add-in-Icons entwerfen, in den erforderlichen Fusion-Größen exportieren und unter `resources/` ablegen
- Toolbar-Befehl im Arbeitsbereich `Solid` unter `Create` mit den neuen Icons registrieren
- `version.py` als einzige Versionsquelle für den Python-Code einführen
- Version in der englischen Dialog-Titelzeile und im englischen Menüeintrag anzeigen
- Konsistenz zwischen `version.py` und der Versionsangabe in der `*.manifest`-Datei prüfen und dokumentieren
- Körper- und Ebenenauswahl implementieren
- Eingaben validieren und verständliche Fehlermeldungen anzeigen

### Phase 2 – Körper teilen

- SplitBodyFeature erzeugen
- Ergebnis-Segmente und Schnittflächen robust erkennen
- Namensschema und Timeline-Gruppe einführen

### Phase 3 – Runder Verbinder

- Skizzenpunkte erfassen
- lokale Transformation implementieren
- runden Verbinder und beide Taschen erzeugen
- Standardtoleranz und Tiefenzugabe unterstützen

### Phase 4 – Weitere Profile

- D-Form
- Oval
- abgerundetes Rechteck
- Sechseck
- Eingabeabhängigkeiten und Profiltests ergänzen

### Phase 5 – Vorschau und Fehlerbehandlung

- Vorschau-Lebenszyklus implementieren
- Abbruch- und Rollback-Verhalten testen
- Kollisionen, Außenkontur und Mindestabstände prüfen

### Phase 6 – Qualität und Release

- Testmodelle und reproduzierbare manuelle Tests ergänzen
- Installation dokumentieren
- Reproduzierbaren Windows-Installer und Buildskript nach dem Installerstandard dieses Plans erstellen
- Automatisch durchsuchten Fusion-Add-in-Pfad auf der Zielinstallation verifizieren
- Installation, Update und Deinstallation auf mindestens einer realen Fusion-Installation testen
- Installer-Buildausgaben ignorieren und Versionierbarkeit der Installer-Quellen mit `git check-ignore` prüfen
- SHA-256-Prüfsumme erzeugen und Signaturstatus dokumentieren
- Englische Oberflächentexte auf Vollständigkeit und zentrale Ablage prüfen
- Lokalisierungsstruktur für die späteren Sprachen Deutsch, Französisch, Spanisch und Polnisch vorbereiten, ohne diese Übersetzungen vorzeitig umzusetzen
- Changelog und Release-Paket vorbereiten
- Eine neue, vom Projektverantwortlichen vorgegebene Versionsnummer gleichzeitig in `version.py` und `*.manifest` eintragen und die Konsistenz testen

### Phase 7 – Mehrfachschnitte

- mehrere Ebenen verwalten
- Schnittreihenfolge definieren
- betroffene Teilkörper je Ebene bestimmen
- Verbindungen getrennt pro Schnittstelle verwalten

## Teststrategie

### Automatisierbare Tests außerhalb von Fusion

- Toleranzberechnung
- Preset-Auflösung
- Einheitenkonvertierung
- Namensvergabe
- Dialogmodell und Validierungsregeln
- 2D-Profilparameter, soweit ohne Fusion-Geometrie darstellbar

### Manuelle Fusion-Tests

- Würfel mit mittigem Schnitt
- schräger Schnitt
- dünnwandiger Körper
- konkave Schnittfläche
- mehrere Punkte nahe der Außenkontur
- Punkt außerhalb der gültigen Schnittfläche
- sehr kleiner und sehr großer Verbinder
- Abbruch während der Vorschau
- Änderung eines vorgelagerten Features und Neuberechnung
- metrisches und imperiales Dokument

### FDM-Passungstest

Für jede Preset-Stufe soll ein kleiner Kalibrierkörper gedruckt werden. Ergebnisse werden mit Drucker, Material, Düse, Schichthöhe, Ausrichtung und tatsächlich passender Toleranz dokumentiert.

## Arbeitsregeln für Codex

- Zuerst vorhandene Projektanweisungen und Add-in-Dateien lesen.
- Kleine, überprüfbare Änderungen vornehmen.
- Immer nur einen Arbeitsschritt umsetzen; nach jedem Schritt Syntax- beziehungsweise Importtests ausführen, soweit außerhalb von Fusion möglich.
- Nach jedem Arbeitsschritt einen konkreten Fusion-Test beschreiben und auf das Testergebnis beziehungsweise die Freigabe des Projektverantwortlichen warten, bevor der nächste Schritt umgesetzt wird.
- Keine API-Methoden erfinden; unsichere Fusion-API-Aufrufe anhand der installierten Dokumentation oder offizieller Autodesk-Dokumentation prüfen.
- Keine Benutzerdateien oder vorhandenen Änderungen überschreiben.
- Noch nicht implementierte Funktionen im Dialog nicht als funktionsfähig darstellen.
- Alle sichtbaren Texte der ersten Version auf Englisch verfassen und für die spätere Lokalisierung zentral verwalten.
- Keine Versionsnummer ohne ausdrückliche Anweisung des Projektverantwortlichen beginnen oder erhöhen.
- Jeden Arbeitsschritt mit geändertem Verhalten, Fusion-Testanleitung, Testergebnis und bekannten Einschränkungen unter `doku/` dokumentieren.
