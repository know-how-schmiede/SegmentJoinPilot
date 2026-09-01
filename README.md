<p align="center">
  <img src="images/SegmentJoinPilot-readme-banner.png" alt="SegmentJoinPilot – Split. Align. Print.">
</p>

<p align="center">
  <strong>English</strong> | <a href="README-DE.md">Deutsch</a>
</p>

# SegmentJoinPilot

SegmentJoinPilot is an open-source Autodesk Fusion add-in for splitting large 3D models into printable segments and creating matching alignment connectors at user-defined positions.

The add-in is intended for makers, educators, model builders, and FDM users who need to divide models because of build-volume limits, print orientation, maintenance, assembly, or surface-quality requirements.

> Project status: Planning / initial development

## Planned workflow

1. Create or select a construction plane at the desired split position.
2. Select the solid body that should be divided.
3. Let SegmentJoinPilot split the body into separate segments.
4. Place sketch points on the generated section face.
5. Select the connector shape, dimensions, insertion depth, clearance, and lead-in.
6. Generate matching sockets in both segments and retain the connectors as separate bodies.
7. Keep all generated features organized and named in the Fusion timeline.

## Planned connector shapes

- Round
- D-shaped
- Oval
- Rectangular with rounded corners
- Hexagonal

Additional connector types may be added after the core workflow is stable.

## Planned features

- Split one solid body with a selected construction plane
- Support multiple connector positions per section face
- FDM-oriented fit presets and custom clearance
- Symmetric or asymmetric insertion depths
- Chamfered or tapered lead-ins
- Separate connector bodies
- Matching pockets on both sides of the split
- Live preview before committing changes
- Consistent names for bodies, sketches, and features
- A dedicated timeline group for each operation
- Validation of wall thickness, connector spacing, and invalid geometry
- Multi-plane and multi-segment processing in a later release

## Initial FDM clearance presets

Clearance is defined per side. A round 8.0 mm connector with 0.20 mm clearance per side therefore produces an 8.4 mm socket.

| Preset | Clearance per side | Total dimensional difference | Intended use |
|---|---:|---:|---|
| Press fit | 0.05–0.10 mm | 0.10–0.20 mm | Calibrated printers and test coupons |
| Tight | 0.10–0.15 mm | 0.20–0.30 mm | Accurate FDM prints |
| Standard | 0.20 mm | 0.40 mm | Recommended default |
| Loose | 0.25–0.30 mm | 0.50–0.60 mm | Easy assembly or larger parts |
| Custom | User defined | Calculated | Material- and printer-specific settings |

These values are starting points, not universal guarantees. Printer calibration, material, layer height, orientation, and connector size all affect the final fit.

## Repository structure

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

Installation instructions will be added when the first testable release is available. During development, the generated Fusion add-in folder will be registered through Fusion's **Scripts and Add-Ins** dialog.

## Development principles

- Use the Autodesk Fusion API and Python.
- Keep geometry generation separate from command-dialog and Fusion API code where practical.
- Store dimensions internally in a consistent unit system and convert explicitly at API boundaries.
- Validate selections and geometry before creating permanent features.
- Avoid relying on unstable face or body indices.
- Store add-in metadata with Fusion attributes so generated operations can be identified later.
- Keep the first release focused on one body, one split plane, and multiple connectors.

## Contributing

The project is in its planning stage. Bug reports, test models, fit-test results, documentation corrections, and focused feature proposals will be welcome once the initial implementation is published.

## Trademark notice

Autodesk and Fusion are trademarks or registered trademarks of Autodesk, Inc. SegmentJoinPilot is an independent project and is not affiliated with or endorsed by Autodesk, Inc.

## License

A project license should be selected before the first public release. The MIT License is a practical default for a permissive open-source Fusion add-in.
