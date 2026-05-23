$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$AppScript = Join-Path $ProjectRoot "scripts\AcademicRAG_App.ps1"
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "Academic-RAG PDF Importer.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($ShortcutPath)
$shortcut.TargetPath = (Get-Command powershell).Source
$shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$AppScript`""
$shortcut.WorkingDirectory = $ProjectRoot
$shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,70"
$shortcut.Description = "Drag PDFs into Academic-RAG and rebuild the local RAG index."
$shortcut.Save()

Write-Host "Created shortcut: $ShortcutPath"
