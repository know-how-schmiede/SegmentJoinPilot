# SegmentJoinPilot Timeline

Diese Datei enthält die kompakte chronologische Übersicht aller freigegebenen und begonnenen Projektversionen. Ausführliche Implementierungsdetails, Testanleitungen und Testergebnisse werden weiterhin im [`IMPLEMENTATION_LOG.md`](IMPLEMENTATION_LOG.md) geführt.

## 2026-09-02 — Version 0.3.1

Status: Implementiert, Fusion-Test ausstehend.

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
