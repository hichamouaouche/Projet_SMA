<#
Rename pictures in the `picture/` folder to safe filenames:
- remove accents
- replace spaces and non-alphanumerics with hyphens
- collapse multiple hyphens
- lowercase the filename

Usage:
  powershell -ExecutionPolicy Bypass -File .\scripts\rename_pictures.ps1

This script will skip files when the target name already exists.
#>

$folder = Join-Path $PSScriptRoot '..\picture'
if (-not (Test-Path $folder)) {
    Write-Error "Folder not found: $folder"
    exit 1
}

Get-ChildItem -Path $folder -File | ForEach-Object {
    $orig = $_.Name
    # remove diacritics
    $decomposed = $orig.Normalize([System.Text.NormalizationForm]::FormD)
    $noAccents = [regex]::Replace($decomposed, '\p{Mn}', '')
    # replace invalid chars with hyphen (keep dot and underscore)
    $safe = $noAccents -replace '[^A-Za-z0-9\._-]', '-'
    $safe = $safe -replace '-+', '-'
    $safe = $safe.Trim('-').ToLowerInvariant()

    if ($orig -ne $safe) {
        $src = $_.FullName
        $dst = Join-Path $_.DirectoryName $safe
        if (Test-Path $dst) {
            Write-Host "Target already exists, skipping: $dst"
            return
        }
        try {
            Rename-Item -LiteralPath $src -NewName $safe -ErrorAction Stop
            Write-Host "Renamed: $orig -> $safe"
        } catch {
            Write-Error "Failed to rename $orig : $_"
        }
    } else {
        Write-Host "Already safe: $orig"
    }
}

Write-Host "Done. If you updated `README.md` to reference the new names, images should appear on GitHub after commit/push."