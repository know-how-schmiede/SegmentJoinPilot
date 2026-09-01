# SegmentJoinPilot – Codex Project Plan

## Auftrag

Implementiere auf Basis eines von Fusion erzeugten leeren Python-Add-ins das Projekt SegmentJoinPilot. Das Add-in teilt einen ausgewählten Volumenkörper mit einer Konstruktionsebene und erzeugt an ausgewählten Skizzenpunkten separate Verbinderkörper sowie toleranzbehaftete Vertiefungen in beiden entstandenen Segmenten.

Diese Datei beschreibt den gewünschten Zielzustand. Vor Änderungen muss Codex die tatsächlich erzeugte Add-in-Struktur, vorhandene Dateien und die verwendete Fusion-API-Version untersuchen. Bestehende Autodesk-Start-/Stop-Logik soll erhalten bleiben und schrittweise erweitert werden.

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

## Entwicklungsphasen

### Phase 0 – Bestand aufnehmen

- Leeres Fusion-Add-in untersuchen
- Manifest, Entry Points, Command-Framework und Ressourcenpfade dokumentieren
- Add-in unverändert starten und stoppen
- Minimalen Smoke-Test festhalten

### Phase 1 – Command und Auswahl

- Toolbar-Befehl mit gelieferten Icons registrieren
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
- Versionsnummern, Changelog und Release-Paket vorbereiten

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
- Nach jeder Phase Syntax- beziehungsweise Importtests ausführen, soweit außerhalb von Fusion möglich.
- Keine API-Methoden erfinden; unsichere Fusion-API-Aufrufe anhand der installierten Dokumentation oder offizieller Autodesk-Dokumentation prüfen.
- Keine Benutzerdateien oder vorhandenen Änderungen überschreiben.
- Noch nicht implementierte Funktionen im Dialog nicht als funktionsfähig darstellen.
- Jede Phase mit geändertem Verhalten, Tests und bekannten Einschränkungen dokumentieren.

