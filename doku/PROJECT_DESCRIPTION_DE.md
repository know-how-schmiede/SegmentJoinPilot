# SegmentJoinPilot – Projektbeschreibung

## Projektidee

SegmentJoinPilot ist ein Add-in für Autodesk Fusion, mit dem sich Volumenkörper an benutzerdefinierten Konstruktionsebenen in druckbare Segmente aufteilen lassen. Auf den entstandenen Schnittflächen erzeugt das Add-in an zuvor gesetzten Skizzenpunkten passende Verbindungselemente und Vertiefungen.

Das Add-in richtet sich vor allem an Anwender von FDM-3D-Druckern. Typische Anwendungsfälle sind Modelle, die größer als der Bauraum des Druckers sind, wegen ihrer Druckausrichtung geteilt werden müssen oder für Transport, Wartung und Montage zerlegbar bleiben sollen.

## Kernnutzen

Fusion kann Körper bereits mit Ebenen teilen. Der eigentliche Mehrwert von SegmentJoinPilot besteht deshalb in einem vollständigen, reproduzierbaren Arbeitsablauf:

- Körper kontrolliert aufteilen
- Schnittflächen zuverlässig zuordnen
- mehrere Verbindungspunkte pro Schnitt verwalten
- druckgerechte Verbindungsgeometrien erzeugen
- toleranzbehaftete Gegenformen in beiden Segmenten erstellen
- separate Dübelkörper behalten
- alle Operationen nachvollziehbar benennen und gruppieren

## Vorgesehener Arbeitsablauf

### Phase 1: Körper teilen

Der Anwender erstellt eine Konstruktionsebene und wählt anschließend im Add-in den zu teilenden Körper sowie die Ebene aus. Das Add-in prüft, ob die Ebene den Körper tatsächlich schneidet, und erzeugt zwei neue Segmente.

### Phase 2: Positionen festlegen

Auf der neuen Schnittfläche wird eine Skizze erstellt. Jeder gültige Skizzenpunkt kennzeichnet die Mittelachse eines Verbinders. Mehrere Punkte auf einer Schnittfläche sind ausdrücklich vorgesehen.

### Phase 3: Verbinder konfigurieren

Im Dialog wählt der Benutzer:

- Verbinderform
- Durchmesser beziehungsweise Breite und Höhe
- Gesamtlänge
- Einstecktiefe auf Seite A und B
- seitliches Spiel pro Seite
- zusätzliche Tiefentoleranz
- Einführfase oder kurzen konischen Anschnitt
- Eckradius bei polygonalen Formen
- alle oder nur ausgewählte Skizzenpunkte

### Phase 4: Geometrie erzeugen

Das Add-in erzeugt für jeden Punkt einen separaten Verbinder. Aus toleranzbehafteten Werkzeugkopien werden die passenden Vertiefungen in beide Segmente geschnitten. Der ursprüngliche Verbinder bleibt als eigener Körper erhalten.

### Phase 5: Organisation

Körper, Skizzen und Features erhalten konsistente Namen. Alle Features eines Vorgangs werden in einer Timeline-Gruppe zusammengefasst. Zusätzlich speichert das Add-in Attribute zur späteren Identifikation.

## Empfohlener Funktionsumfang der ersten Version

Die erste Version sollte bewusst begrenzt bleiben:

- ein Volumenkörper
- eine Konstruktionsebene
- zwei entstehende Segmente
- beliebig viele Verbindungspositionen auf dieser Schnittfläche
- runde, D-förmige, ovale, rechteckige und sechseckige Verbinder
- separate Verbinderkörper
- Vertiefungen auf beiden Seiten
- einstellbare FDM-Toleranz
- Einführfase
- Live-Vorschau
- Timeline-Gruppe und nachvollziehbare Benennung

Mehrere Schnittebenen in einem einzigen Vorgang sind für eine spätere Version vorgesehen. Bis dahin kann derselbe Befehl nacheinander auf bereits erzeugte Segmente angewendet werden.

## Geometrische Anforderungen

### Ausrichtung

Die Achse eines Verbinders folgt immer der Normalen der Schnittfläche. Das gilt auch für schräg im Raum liegende Ebenen. Globale X-, Y- oder Z-Richtungen dürfen nicht als feste Extrusionsrichtung angenommen werden.

### Prismatische Verbinder

Der tragende Bereich bleibt prismatisch und maßhaltig. An beiden Enden sollte eine kurze Einführfase oder ein konischer Anschnitt erzeugt werden. Eine vollständig konische Form ist nicht als Standard vorgesehen, weil Einstecktiefe und Flächenkontakt dadurch ungenauer werden.

### FDM-Toleranzen

Das Spiel wird im Dialog pro Seite angegeben. Empfohlener Standardwert: 0,20 mm pro Seite. Zusätzlich sollte die Tasche in axialer Richtung etwa 0,2 bis 0,5 mm tiefer sein als der jeweils eingesteckte Teil des Verbinders.

Die Werte sind Startwerte. Eine spätere Kalibrierfunktion mit druckbaren Testkörpern wäre sinnvoll.

## Spätere Erweiterungen

- mehrere Schnittebenen in einem Vorgang
- unterschiedliche Verbinder an einzelnen Punkten
- automatische Verteilung von Verbindern
- Mindestwandstärken- und Kollisionsprüfung
- angeformte Zapfen statt separater Dübel
- Magnettaschen
- Schraubverbindungen und Gewindeeinsätze
- Schwalbenschwanz- und Puzzle-Verbindungen
- Export der Segmente und Verbinder als STL oder 3MF
- Bearbeiten bereits erzeugter SegmentJoinPilot-Operationen
- FDM-Passungsassistent mit Kalibrierkörper

## Abgrenzung

SegmentJoinPilot ersetzt keine allgemeine Baugruppen- oder Fügesimulation. Das Add-in automatisiert die druckgerechte Aufteilung und geometrische Vorbereitung von Modellen für die spätere physische Montage.

