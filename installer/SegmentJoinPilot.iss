#define MyAppName "SegmentJoinPilot"
#define MyAppVersion "0.5.2"
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
DefaultDirName={userappdata}\Autodesk\Autodesk Fusion 360\API\AddIns\{#MyAppName}
UsePreviousAppDir=no
DisableDirPage=yes
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

[InstallDelete]
Type: filesandordirs; Name: "{userappdata}\Autodesk\Autodesk Fusion\API\AddIns\{#MyAppName}"

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
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    MsgBox(ExpandConstant('{cm:FusionRestart}'), mbInformation, MB_OK);
end;
