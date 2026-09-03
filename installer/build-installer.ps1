[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$installerDirectory = Split-Path -Parent $PSCommandPath
$projectDirectory = Split-Path -Parent $installerDirectory
$manifestPath = Join-Path $projectDirectory 'fusion_addin\SegmentJoinPilot\SegmentJoinPilot.manifest'
$scriptPath = Join-Path $installerDirectory 'SegmentJoinPilot.iss'
$compilerCandidates = @(
    (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'),
    (Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe')
)
$compiler = $compilerCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not $compiler) {
    throw 'Inno Setup 6 was not found. Install it from https://jrsoftware.org/isinfo.php.'
}

$manifestText = Get-Content -LiteralPath $manifestPath -Raw
$manifestVersionMatch = [regex]::Match($manifestText, '"version"\s*:\s*"([^"]+)"')
if (-not $manifestVersionMatch.Success) {
    throw "No version was found in $manifestPath."
}
$manifestVersion = $manifestVersionMatch.Groups[1].Value
$versionDefinition = Select-String -LiteralPath $scriptPath -Pattern '^#define MyAppVersion "([^"]+)"$'
if (-not $versionDefinition -or $versionDefinition.Matches[0].Groups[1].Value -ne $manifestVersion) {
    throw "Installer and manifest versions do not match. Expected $manifestVersion."
}

& $compiler $scriptPath
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup failed with exit code $LASTEXITCODE."
}

$outputPath = Join-Path $installerDirectory "dist\SegmentJoinPilot-Setup-$manifestVersion.exe"
if (-not (Test-Path -LiteralPath $outputPath)) {
    throw "Installer output was not created: $outputPath"
}

Write-Output "Created $outputPath"
