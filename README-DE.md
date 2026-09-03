<p align="center">
  <img src="images/SegmentJoinPilot-readme-banner.png" alt="SegmentJoinPilot – Split. Align. Print.">
</p>

<p align="center">
  <a href="README.md">English</a> | <strong>Deutsch</strong>
</p>

# SegmentJoinPilot

SegmentJoinPilot ist ein quelloffenes Autodesk-Fusion-Add-in, das große 3D-Modelle in druckbare Segmente teilt und an benutzerdefinierten Positionen passende Ausrichtungsverbinder erzeugt.

Das Add-in richtet sich an Maker, Lehrende, Modellbauer und FDM-Anwender, die Modelle aufgrund von Bauraumgrenzen, Druckausrichtung, Wartung, Montage oder Anforderungen an die Oberflächenqualität aufteilen müssen.

> Projektstatus: Planung / frühe Entwicklung

## Geplanter Arbeitsablauf

1. Eine Konstruktionsebene an der gewünschten Trennposition erstellen oder auswählen.
2. Den zu teilenden Volumenkörper auswählen.
3. SegmentJoinPilot den Körper in einzelne Segmente teilen lassen.
4. Skizzenpunkte auf der erzeugten Schnittfläche platzieren.
5. Form, Abmessungen, Einstecktiefe, Spiel und Einführung der Verbinder festlegen.
6. Passende Aufnahmen in beiden Segmenten erzeugen und die Verbinder als separate Körper beibehalten.
7. Alle erzeugten Elemente in der Fusion-Zeitleiste strukturiert und eindeutig benannt ablegen.

## Geplante Verbinderformen

- Rund
- D-förmig
- Oval
- Rechteckig mit abgerundeten Ecken
- Sechseckig

Weitere Verbindertypen können ergänzt werden, sobald der grundlegende Arbeitsablauf stabil ist.

## Geplante Funktionen

- Einen Volumenkörper mit einer ausgewählten Konstruktionsebene teilen
- Mehrere Verbinderpositionen pro Schnittfläche unterstützen
- FDM-orientierte Passungsvorgaben und benutzerdefiniertes Spiel
- Symmetrische oder asymmetrische Einstecktiefen
- Gefaste oder konische Einführungen
- Separate Verbinderkörper
- Passende Aufnahmen auf beiden Seiten der Trennung
- Live-Vorschau vor dem Anwenden der Änderungen
- Einheitliche Namen für Körper, Skizzen und Elemente
- Eine eigene Zeitleistengruppe für jeden Vorgang
- Prüfung von Wandstärke, Verbinderabstand und ungültiger Geometrie
- Verarbeitung mehrerer Ebenen und Segmente in einer späteren Version

## Erste Vorgaben für FDM-Spiel

Das Spiel wird pro Seite angegeben. Ein runder Verbinder mit 8,0 mm Durchmesser und 0,20 mm Spiel pro Seite ergibt daher eine Aufnahme mit 8,4 mm Durchmesser.

| Vorgabe | Spiel pro Seite | Gesamte Maßdifferenz | Verwendungszweck |
|---|---:|---:|---|
| Presspassung | 0,05–0,10 mm | 0,10–0,20 mm | Kalibrierte Drucker und Testkörper |
| Eng | 0,10–0,15 mm | 0,20–0,30 mm | Präzise FDM-Drucke |
| Standard | 0,20 mm | 0,40 mm | Empfohlene Voreinstellung |
| Locker | 0,25–0,30 mm | 0,50–0,60 mm | Einfache Montage oder größere Bauteile |
| Benutzerdefiniert | Benutzerdefiniert | Berechnet | Material- und druckerspezifische Einstellungen |

Diese Werte sind Ausgangspunkte und keine allgemeingültigen Garantien. Druckerkalibrierung, Material, Schichthöhe, Ausrichtung und Verbindergröße beeinflussen die tatsächliche Passung.

## Repository-Struktur

```text
SegmentJoinPilot/
├── README.md
├── README-DE.md
├── LICENSE
├── doku/
├── fusion_addin/
├── images/
└── installer/
```

## Installation

Unter Windows Autodesk Fusion schließen und `SegmentJoinPilot-Setup-0.5.1.exe` ausführen. Der Installer kopiert das Add-in ohne Administratorrechte nach `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\SegmentJoinPilot`. Anschließend Fusion neu starten und bei Bedarf **Dienstprogramme > Skripte und Zusatzmodule** öffnen.

Für die Entwicklung kann der Ordner `fusion_addin/SegmentJoinPilot` weiterhin manuell über den Fusion-Dialog **Skripte und Zusatzmodule** registriert werden. Die reproduzierbare Erstellung des Installers ist in [`installer/README.md`](installer/README.md) beschrieben.

## Entwicklungsgrundsätze

- Autodesk Fusion API und Python verwenden.
- Geometrieerzeugung nach Möglichkeit vom Befehlsdialog und Fusion-API-Code trennen.
- Abmessungen intern in einem einheitlichen Einheitensystem speichern und an API-Grenzen ausdrücklich umrechnen.
- Auswahl und Geometrie prüfen, bevor dauerhafte Elemente erzeugt werden.
- Keine instabilen Flächen- oder Körperindizes verwenden.
- Add-in-Metadaten in Fusion-Attributen speichern, damit erzeugte Vorgänge später identifiziert werden können.
- Die erste Version auf einen Körper, eine Trennebene und mehrere Verbinder konzentrieren.

## Mitwirken

Das Projekt befindet sich in der Planungsphase. Fehlerberichte, Testmodelle, Ergebnisse von Passungstests, Dokumentationskorrekturen und konkrete Funktionsvorschläge sind willkommen, sobald die erste Implementierung veröffentlicht ist.

## Markenhinweis

Autodesk und Fusion sind Marken oder eingetragene Marken von Autodesk, Inc. SegmentJoinPilot ist ein unabhängiges Projekt und weder mit Autodesk, Inc. verbunden noch von Autodesk, Inc. unterstützt.

## Lizenz

Vor der ersten öffentlichen Veröffentlichung sollte eine Projektlizenz ausgewählt werden. Die MIT-Lizenz ist eine sinnvolle Standardwahl für ein freizügiges quelloffenes Fusion-Add-in.
