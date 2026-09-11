#define MyAppName "SegmentJoinPilot"
#define MyAppVersion "0.6.2"
#define MyAppPublisher "know-how-schmiede"
#define MyAppURL "https://github.com/know-how-schmiede/SegmentJoinPilot"
#define MyAppSource "..\fusion_addin\SegmentJoinPilot"

[Setup]
AppId={{9A2E3607-11BB-49EA-B226-7290392A3AB8}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={code:GetDefaultAddInDir}
UsePreviousAppDir=no
DisableDirPage=no
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename={#MyAppName}-Setup-{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#MyAppName} {#MyAppVersion}
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Files]
Source: "{#MyAppSource}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: ".vscode\*,__pycache__\*,*.pyc,*.pyo"

[Messages]
english.BeveledLabel=For Autodesk Fusion
german.BeveledLabel=Für Autodesk Fusion

[CustomMessages]
english.FusionRestart=Restart Autodesk Fusion after installation. The add-in will then appear in Utilities > Scripts and Add-Ins.
german.FusionRestart=Starten Sie Autodesk Fusion nach der Installation neu. Das Add-in erscheint anschließend unter Dienstprogramme > Skripte und Zusatzmodule.

[Run]
Filename: "{app}"; Description: "{cm:OpenAddInFolder}"; Flags: postinstall shellexec skipifsilent unchecked

[CustomMessages]
english.OpenAddInFolder=Open the installed add-in folder
german.OpenAddInFolder=Installierten Add-in-Ordner öffnen

[Code]
function GetDefaultAddInDir(Param: String): String;
var
  FusionRoot, Fusion360Root, SelectedRoot: String;
begin
  FusionRoot := ExpandConstant('{userappdata}\Autodesk\Autodesk Fusion');
  Fusion360Root := ExpandConstant('{userappdata}\Autodesk\Autodesk Fusion 360');
  { Prefer an existing API directory, then a product directory.
    If both exist, prefer the current product name. The user can override it. }
  if DirExists(FusionRoot + '\API\AddIns') then
    SelectedRoot := FusionRoot
  else if DirExists(Fusion360Root + '\API\AddIns') then
    SelectedRoot := Fusion360Root
  else if DirExists(FusionRoot) then
    SelectedRoot := FusionRoot
  else if DirExists(Fusion360Root) then
    SelectedRoot := Fusion360Root
  else
    SelectedRoot := FusionRoot;
  Result := SelectedRoot + '\API\AddIns\{#MyAppName}';
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    MsgBox(ExpandConstant('{cm:FusionRestart}'), mbInformation, MB_OK);
end;
