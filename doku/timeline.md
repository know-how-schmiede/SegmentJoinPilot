# SegmentJoinPilot Timeline

Diese Datei enthält die kompakte chronologische Übersicht aller freigegebenen und begonnenen Projektversionen. Ausführliche Implementierungsdetails, Testanleitungen und Testergebnisse werden weiterhin im [`IMPLEMENTATION_LOG.md`](IMPLEMENTATION_LOG.md) geführt.

## 2026-09-02 — Version 0.3.5

Status: Implementiert, Fusion-Test ausstehend.

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
