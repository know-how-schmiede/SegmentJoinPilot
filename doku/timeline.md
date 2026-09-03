# SegmentJoinPilot Timeline

Diese Datei enthält die kompakte chronologische Übersicht aller freigegebenen und begonnenen Projektversionen. Ausführliche Implementierungsdetails, Testanleitungen und Testergebnisse werden weiterhin im [`IMPLEMENTATION_LOG.md`](IMPLEMENTATION_LOG.md) geführt.

## 2026-09-03 — Version 0.4.4

Status: Implementiert; Fusion-Test und Freigabe stehen aus.

- Manifest und `version.py` auf `0.4.4` aktualisiert.
- Tiefenzugabe mit `0,30 mm` Standardwert ergänzt.
- Aus jedem Socket-Profil zwei einseitige Werkzeugkörper für Segment A und B erzeugt.
- Werkzeugtiefe als halbe Verbinderlänge plus Tiefenzugabe berechnet.
- Werkzeugkörper und Extrusionsfeatures stabil benannt sowie in Namensprüfung und Rollback aufgenommen.
- Noch keine Schnitte in den Segmentkörpern erzeugt.

## 2026-09-03 — Version 0.4.3

Status: In Fusion getestet und vom Projektverantwortlichen freigegeben.

- Manifest und `version.py` auf `0.4.3` aktualisiert.
- Fit-Gruppe mit radialem Spiel pro Seite und `0,20 mm` Standardwert ergänzt.
- Pro ausgewähltem Verbinder ein konzentrisches, separat benanntes Socket-Profil erzeugt.
- Socket-Durchmesser aus Verbinderdurchmesser plus zweimal radialem Spiel berechnet.
- Namensprüfung und Rollback auf Socket-Profil-Sketches erweitert.
- Noch keine Socket-Extrusion und keine Schnitte in den Segmenten erzeugt.

## 2026-09-03 — Version 0.4.2

Status: In Fusion getestet und vom Projektverantwortlichen freigegeben.

- Manifest und `version.py` auf `0.4.2` aktualisiert.
- Eingabe für die Gesamtlänge mit `12 mm` Standardwert ergänzt.
- Ausgewählte Rundprofile symmetrisch zur Schnittfläche extrudiert.
- Pro ausgewähltem Punkt einen separat benannten Verbinderkörper erzeugt.
- Vorabprüfung auf bestehende Profil-, Körper- und Feature-Namen ergänzt.
- Vollständigen Rollback für Profil-Sketches und Verbinderextrusionen umgesetzt.
- Noch keine toleranzbehafteten Taschen, Fasen oder Anschnitte erzeugt.

## 2026-09-03 — Version 0.4.1

Status: In Fusion getestet und vom Projektverantwortlichen freigegeben.

- Manifest und `version.py` auf `0.4.1` aktualisiert.
- Erkannte Positionspunkte als einzeln aktivierbare Kandidaten im Dialog ergänzt.
- Benutzergezeichnete Einzelpunkte und Geometrie-Eckpunkte gemeinsam als Kandidaten angeboten.
- Mindestens einen aktivierten Kandidaten für die Profilerzeugung vorausgesetzt.
- Für jeden aktivierten Kandidaten ein separat nummeriertes rundes Profil-Sketch erzeugt.
- Vorabprüfung auf Namenskollisionen und vollständigen Rollback bei Fehlern ergänzt.
- Checkbox-Auswertung nach dem ersten Fusion-Test korrigiert und aktivierte Punkte im Modellfenster markiert.
- Nach dem zweiten Fusion-Test nicht interaktive, verschachtelte Eingaben entfernt und die Bildmarkierungen durch rote Kreuzmarkierungen ersetzt.
- Nach dem dritten Fusion-Test die Grafikmarkierung durch Fusions native Auswahlhervorhebung ersetzt und die Checkbox-Auswertung zusätzlich an die Eingabevalidierung gekoppelt.
- Interne Command-ID erneuert, damit Fusion den zwischengespeicherten Zwischenstand des Dialogs sicher verwirft.
- Lesbare Liste der aktivierten Kandidatennummern und ihrer lokalen Koordinaten ergänzt.
- Native Hilfsauswahl wieder entfernt, nachdem sie beim Validieren alle Kandidaten reaktivieren konnte; Profilerzeugung ausschließlich an Checkbox-Zustand gekoppelt.
- Verbliebenen Fehler in der Profilerzeugung korrigiert: Statt aller erkannten Punkte wird jetzt tatsächlich die ausgewählte Kandidatenmenge verarbeitet und protokolliert.
- Rote Kreuzmarkierungen für die ausgewählten Punkte wiederhergestellt und über eine eindeutig benannte, bei jeder Aktualisierung bereinigte Grafikgruppe gegen veraltete Markierungen abgesichert.
- Noch keine Extrusion oder Taschengeometrie erzeugt.

## 2026-09-02 — Version 0.4.0

Status: In Fusion getestet und nach Korrektur der Punktfilterung freigegeben.

- Manifest und `version.py` auf `0.4.0` aktualisiert.
- Connector-Gruppe im Modus `Set Point` ergänzt.
- Profilform `Round` und Durchmesser mit `6 mm` Standardwert ergänzt.
- Separates Profil-Sketch ohne projizierte Flächenkanten angelegt.
- Ersten erkannten Positionspunkt in das Koordinatensystem des Profil-Sketches übertragen.
- Rundes Profil am ersten Positionspunkt erzeugt und stabil benannt.
- Rollback bei fehlgeschlagener Profilerzeugung und Schutz vor doppeltem Profil ergänzt.
- Nach Fusion-Test automatisch übernommene Schnittflächen-Eckpunkte aus der Positionsauswahl ausgeschlossen.
- Unsichtbare, von Fusion automatisch aus der Auflagefläche übernommene Skizzengeometrie ausdrücklich herausgefiltert.
- Freie Punkte und Eckpunkte ausschließlich benutzergezeichneter Geometrie weiterhin zugelassen.
- Noch keine Extrusion oder Taschengeometrie erzeugt.
- Als Folgeschritt festgehalten: Erkannte Punkte werden einzeln an- und abwählbar; eigene Punkte und eine diagonale Zweipunktauswahl bei vier Rechteckecken werden unterstützt.

## 2026-09-02 — Version 0.3.10

Status: In Fusion getestet und freigegeben.

- Manifest und `version.py` auf `0.3.10` aktualisiert.
- Lokale X/Y-Koordinaten jedes Positionspunkts beibehalten.
- Positionspunkte mit der kontextabhängigen Fusion-Skizzentransformation in Modellkoordinaten überführt.
- Modellkoordinaten X/Y/Z zusammen mit den lokalen Skizzenkoordinaten ausgegeben.
- Fehlerbehandlung für eine fehlgeschlagene Koordinatentransformation ergänzt.
- Noch keine Verbinder- oder Taschengeometrie erzeugt.

## 2026-09-02 — Version 0.3.9

Status: In Fusion getestet und freigegeben.

- Manifest und `version.py` auf `0.3.9` aktualisiert.
- Erkennung von freien Skizzenpunkten auf Kurvenendpunkte und gemeinsam verwendete Eckpunkte erweitert.
- Damit insbesondere die vier Eckpunkte eines gezeichneten Rechtecks als Positionen zugelassen.
- Skizzenursprung und Referenzpunkte weiterhin ausgeschlossen.
- Englische Oberfläche und interne Bezeichnungen auf den allgemeineren Begriff `position points` umgestellt.
- Noch keine Verbinder- oder Gegenstückgeometrie erzeugt.

## 2026-09-02 — Version 0.3.8

Status: In Fusion getestet und freigegeben.

- Manifest und `version.py` auf `0.3.8` aktualisiert.
- Punktmodus in `Set Point` umbenannt.
- Nach erfolgreichem Split automatisch die neu erzeugte Positionsskizze ausgewählt und zur Bearbeitung geöffnet.
- Blockierenden Erfolgsdialog durch eine Fusion-Statusmeldung und einen Log-Eintrag ersetzt.
- Ende der Skizzenbearbeitung über den Fusion-Befehl `SketchStop` erkannt.
- SegmentJoinPilot nach `Finish Sketch` automatisch erneut gestartet.
- Modus `Set Point` und zugehörige Positionsskizze beim Neustart automatisch vorbelegt.
- Anzahl der gesetzten eigenständigen Punkte unmittelbar angezeigt.
- Noch keine Verbinder- oder Gegenstückgeometrie erzeugt.

## 2026-09-02 — Version 0.3.7

Status: In Fusion getestet und nach den Auswahlkorrekturen freigegeben.

- Zwei Betriebsmodi für neue Split-Operationen und die Prüfung vorhandener Positionsskizzen ergänzt.
- Auswahlgrenzen beim Moduswechsel dynamisch angepasst, damit ausgeblendete Pflichtfelder die OK-Schaltfläche nicht blockieren.
- Eigenständige, nicht referenzierte Skizzenpunkte erfasst.
- Skizzenursprung und mit Kurven verbundene Punkte ausgeschlossen.
- Fusion-Rückgabewert `None` für die Verbindungen eigenständiger Punkte berücksichtigt.
- Auswahl des vollständigen Sketch-Objekts über den Fusion-Browser dokumentiert.
- Direkte Modellauswahl eines sichtbaren Skizzenpunkts ergänzt und dessen übergeordnete Positionsskizze automatisch ermittelt.
- Sichtbarkeit neu erzeugter Positionsskizzen ausdrücklich aktiviert.
- Punktanzahl und lokale X/Y-Koordinaten ausgegeben.
- Keine Geometrieänderung im Prüfmodus.

## 2026-09-02 — Version 0.3.6

Status: In Fusion getestet und freigegeben.

- Manifest und `version.py` auf `0.3.6` aktualisiert.
- Zyklische Vorbedingung einer bereits vorhandenen Positionsskizze nach Fusion-Test entfernt.
- Leere Positionsskizze nach dem Split automatisch auf der größten Schnittfläche von Segment A erzeugt.
- Skizze nach dem Schema `SJP_PositionSketch_NNN` benannt.
- Split und Positionsskizze gemeinsam als `SJP_Operation_NNN` gruppiert.
- Gruppen- und Skizzenbereinigung in den Fehler-Rollback aufgenommen.
- Noch keine Skizzenpunkte oder Verbinder erzeugt.

## 2026-09-02 — Version 0.3.5

Status: Nach Entfernung des nicht unterstützten Ein-Feature-Gruppierungsversuchs in Fusion getestet und freigegeben.

- Manifest und `version.py` auf `0.3.5` aktualisiert.
- Ursprünglichen Versuch dokumentiert, das einzelne Split-Feature als `SJP_Operation_NNN` zu gruppieren.
- Fusion-Fehler erkannt: Timeline-Gruppen benötigen mindestens zwei Features.
- Nicht unterstützten Ein-Feature-Gruppierungsversuch entfernt, damit der gültige Split erhalten bleibt.
- Künftigen Gruppennamen und die übereinstimmende Operationsnummer reserviert.
- Tatsächliche Gruppenerstellung auf den ersten späteren Schritt mit mindestens zwei echten Operations-Features verschoben.

## 2026-09-02 — Version 0.3.4

Status: In Fusion getestet und nach Korrektur des InputChanged-Fehlers freigegeben.

- Manifest und `version.py` auf `0.3.4` aktualisiert.
- Component-lokale, fortlaufende Operationsnummer ermittelt.
- Split-Feature nach dem Schema `SJP_Split_NNN` benannt.
- Ergebniskörper als `SJP_Segment_A_NNN` und `SJP_Segment_B_NNN` benannt.
- Kollisionen mit bereits vorhandenen SegmentJoinPilot-Operationen vermieden.
- Vergebene Namen in die englische Erfolgsmeldung aufgenommen.
- Fehler im `InputChangedEventHandler` behoben, indem die Validierungsanzeige in dieselbe `Split`-Eingabegruppe wie die Auswahlfelder verschoben wurde.

## 2026-09-02 — Version 0.3.3

Status: In Fusion getestet und freigegeben.

- Manifest und `version.py` auf `0.3.3` aktualisiert.
- Beide Split-Ergebnisse anhand ihrer Schwerpunktlage relativ zur Ebenennormalen als Segment A und B zugeordnet.
- Segment A als negative und Segment B als positive Seite der Schnittebene definiert.
- Neu entstandene planare Schnittflächen geometrisch über Parallelität und Koplanarität erkannt.
- Mehrere getrennte Schnittflächen pro Segment berücksichtigt.
- Rollback bei nicht eindeutiger Seitenzuordnung oder fehlenden Schnittflächen ergänzt.
- Seitenzuordnung und Anzahl der erkannten Schnittflächen in der Erfolgsmeldung ausgegeben.

## 2026-09-02 — Version 0.3.2

Status: In Fusion getestet und freigegeben.

- Manifest und `version.py` auf `0.3.2` aktualisiert.
- Ausgewählten Solid-Körper mit der gewählten Konstruktionsebene geteilt.
- Ergebnis direkt über das erzeugte Split-Feature ermittelt.
- Genau zwei Solid-Ergebniskörper als Erfolgskriterium festgelegt.
- Automatisches Entfernen eines unvollständigen oder unerwarteten Split-Features ergänzt.
- Englische Erfolgs- und Fehlermeldungen hinzugefügt.

## 2026-09-02 — Version 0.3.1

Status: In Fusion getestet und freigegeben.

- Manifest und `version.py` auf `0.3.1` aktualisiert.
- Zerstörungsfreie Prüfung ergänzt, ob die gewählte Konstruktionsebene den Solid-Körper schneidet.
- Dynamische englische Validierungsmeldung für gültige und ungültige Schnitte hinzugefügt.
- OK-Schaltfläche bei einer Ebene außerhalb des Körpers deaktiviert.
- Zusätzliche Sicherheitsprüfung beim Bestätigen des Dialogs ergänzt.
- In diesem Schritt werden keine Geometrie- oder Timeline-Änderungen vorgenommen.

## 2026-09-02 — Version 0.3.0

Status: Durch Freigabe des nächsten Schritts bestätigt.

- Manifest und `version.py` auf `0.3.0` aktualisiert.
- Englische Auswahlgruppe `Split` ergänzt.
- Pflichtauswahl für genau einen Solid-BRep-Körper hinzugefügt.
- Pflichtauswahl für genau eine Konstruktionsebene hinzugefügt.
- Auswahltypen über die Fusion-Filter `SolidBodies` und `ConstructionPlanes` eingeschränkt.
- OK-Schaltfläche bis zum Vorliegen beider gültiger Auswahlen deaktiviert.
- Erfolgsmeldung mit den Namen der ausgewählten Objekte ergänzt.
- In diesem Schritt werden weiterhin keine Geometrie- oder Timeline-Änderungen vorgenommen.

## 2026-09-02 — Version 0.2.0

Status: In Fusion getestet und freigegeben.

- Manifest und `version.py` auf `0.2.0` aktualisiert.
- Autodesk-Beispielicons durch das cyan-blau-orange SegmentJoinPilot-Markenicon ersetzt.
- PNG-Ressourcen in 16 × 16, 32 × 32 und 64 × 64 Pixeln erstellt.
- Generischen `ACME`-Namespace und geerbte Template-Command-ID ersetzt.
- Falsche generische SVG-Ressourcen nach Fusion-Tests entfernt.
- Manifest-Icon auf das Marken-PNG umgestellt.
- Persistente Fusion-Icon-Zuordnung durch eine neue Command-ID und einen neuen Ressourcenpfad invalidiert.

## 2026-09-02 — Version 0.1.0

Status: In Fusion getestet und freigegeben.

- Zentrale Versionsdatei `version.py` eingeführt.
- Manifest-Version auf `0.1.0` gesetzt.
- SegmentJoinPilot als einzelner Befehl unter `Solid > Create` registriert.
- Versionsnummer im Menüeintrag und Dialogtitel angezeigt.
- Autodesk-Beispiel-Paletten aus dem Add-in-Startpfad entfernt.
- Einfachen englischen Prüfdialog ohne Geometriefunktion hinzugefügt.

## Pflege

- Eine neue Version wird nur nach ausdrücklicher Versionsvorgabe des Projektverantwortlichen begonnen.
- Neue Versionseinträge werden unmittelbar unter der Einleitung eingefügt, sodass die neueste Version immer zuerst steht.
- Zu jeder Version werden Datum, Status und die wesentlichen Änderungen in dieser Datei ergänzt.
- Technische Einzelheiten und Fusion-Testprotokolle verbleiben im `IMPLEMENTATION_LOG.md`.
