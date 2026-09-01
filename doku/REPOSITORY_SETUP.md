# Repository Setup

## Suggested GitHub repository details

**Repository name:** `SegmentJoinPilot`

**Short description:**

> Fusion add-in for splitting 3D models and creating customizable, FDM-ready alignment connectors.

**Suggested topics:**

```text
autodesk-fusion fusion-360 fusion-api python add-in 3d-printing fdm cad maker connector dowel model-splitting
```

The repository can be created as public or private. A private repository does not cause a technical problem for development. Public visibility is only required when the project should be openly distributed and discovered.

## Recommended initialization

When creating the repository on GitHub, leave automatic README, `.gitignore`, and license generation disabled if this starter package will be copied into the repository first. This avoids an unnecessary first merge conflict.

After cloning the empty repository:

1. Copy the contents of this starter folder into the repository root.
2. Create the empty Fusion Python add-in through Fusion.
3. Copy the generated add-in folder into `src/`, or adapt the layout after inspecting Fusion's generated structure.
4. Copy the supplied icon sizes into the command resource folder used by the generated add-in.
5. Give Codex the repository path and instruct it to read `docs/CODEX_PROJECT_PLAN.md` before implementation.
6. Add an open-source license before publishing the first release.

## Suggested first commits

```text
docs: add initial project concept and development plan
chore: add SegmentJoinPilot brand assets
chore: add empty Fusion add-in scaffold
feat: register SegmentJoinPilot command
```

## Branch and release strategy

For the initial solo-development phase, a lightweight workflow is sufficient:

- `main`: stable and startable state
- short-lived feature branches for geometry changes
- semantic version tags beginning with `v0.1.0`
- GitHub Releases containing the installable add-in folder or ZIP

Suggested milestones:

- `v0.1.0`: command, selection, and single body split
- `v0.2.0`: round connectors and sockets
- `v0.3.0`: additional connector profiles and fit presets
- `v0.4.0`: preview, validation, and error handling
- `v1.0.0`: documented and tested single-plane workflow

## Issue labels

```text
bug
enhancement
geometry
fusion-api
user-interface
documentation
testing
good-first-issue
needs-test-model
```

## Legal and naming notes

- Use `SegmentJoinPilot` as the project and product name.
- Use `for Autodesk Fusion` only as a descriptive phrase.
- Do not reproduce Autodesk or Fusion logos in project artwork.
- Include the independent-project trademark notice from the README.
- Before commercial distribution or trademark registration, perform a formal DPMA/EUIPO trademark search.

