<#
.SYNOPSIS
    Full build pipeline: PyInstaller (onedir) -> staging -> Inno Setup installer.
.DESCRIPTION
    Phase 1 — Build  : Run PyInstaller (--onedir, --noupx) to produce launcher.exe + runtime files
    Phase 2 — Sign   : Code-sign the executable (requires a code signing certificate)
    Phase 3 — Stage  : Copy everything from dist\launcher\ into release\staging\
    Phase 4 — Package: Compile Inno Setup .iss into a ready-to-ship Setup.exe
.PARAMETER SkipBuild
    Skip the PyInstaller build and use existing dist\launcher\ directory.
.PARAMETER SkipPackage
    Stop after staging (do not run Inno Setup).
.PARAMETER CertificatePath
    Path to the code signing certificate (.pfx) for signing the executable.
    If omitted, signing is skipped with a warning.
.PARAMETER CertificatePassword
    Password for the code signing certificate.
.EXAMPLE
    .\scripts\build.ps1                               # Build + sign + stage + package
    .\scripts\build.ps1 -SkipBuild                     # Sign + stage + package only
    .\scripts\build.ps1 -SkipPackage -CertificatePath mycert.pfx -CertificatePassword mypass
#>

param(
    [switch]$SkipBuild,
    [switch]$SkipPackage,
    [string]$CertificatePath = "",
    [string]$CertificatePassword = ""
)

$ErrorActionPreference = "Stop"

# ── Paths ──────────────────────────────────────────────────────────────────────
$ProjectRoot    = Resolve-Path "$PSScriptRoot\.."
$DistDir        = Join-Path $ProjectRoot "dist"
$BuildDir       = Join-Path $ProjectRoot "build"
$SpecFile       = Join-Path $ProjectRoot "launcher.spec"
$StagingDir     = Join-Path $ProjectRoot "release\staging"
$ReleaseDir     = Join-Path $ProjectRoot "release"
$SetupIss       = Join-Path $PSScriptRoot "setup.iss"

$AppName        = "Inventory Manager"
$AppVersion     = "1.0.0"
$ExeName        = "launcher.exe"
$InstallerName  = "${AppName}_Setup_v${AppVersion}.exe"

# ── Pre-flight checks ──────────────────────────────────────────────────────────
Write-Host "=== Inventory Manager Build Pipeline ===" -ForegroundColor Cyan
Write-Host "Project root : $ProjectRoot"
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not on PATH. Install Python 3.10+ and try again."
}

# ────────────────────────────────────────────────────────────────────────────────
# PHASE 1 — Build executable with PyInstaller (--onedir mode)
# ────────────────────────────────────────────────────────────────────────────────
if (-not $SkipBuild) {
    Write-Host "=== Phase 1: Build EXE ===" -ForegroundColor Green

    # 1a. Clean previous build artifacts
    Write-Host "  -> Removing previous build artifacts..."
    if (Test-Path $BuildDir)           { Remove-Item -Recurse -Force $BuildDir }
    if (Test-Path (Join-Path $DistDir "launcher")) { Remove-Item -Recurse -Force (Join-Path $DistDir "launcher") }

    # 1b. Run PyInstaller using the spec file (contains all config:
    #     --onedir, --windowed, strip=True, upx=False, excludes, optimize=1,
    #     icon, data dirs, hidden imports).
    #     Using the spec file preserves our custom hardening settings
    #     that CLI args cannot express (excludes, strip on COLLECT, etc.).
    Write-Host "  -> Running PyInstaller via $SpecFile ..."
    $proc = Start-Process -FilePath "python" -ArgumentList @("-m", "PyInstaller", $SpecFile, "--clean") -NoNewWindow -Wait -PassThru
    if ($proc.ExitCode -ne 0) {
        throw "PyInstaller failed with exit code $($proc.ExitCode). Check output above."
    }

    # 1c. Verify the output directory was created
    $exeDir = Join-Path $DistDir "launcher"
    $exePath = Join-Path $exeDir $ExeName
    if (-not (Test-Path $exePath)) {
        throw "PyInstaller completed but $exePath was not found."
    }
    Write-Host "  -> EXE built: $exePath" -ForegroundColor Yellow
    Write-Host ""
}
else {
    Write-Host "=== Phase 1: SKIPPED (--SkipBuild) ===" -ForegroundColor Gray
    Write-Host ""
}

# ────────────────────────────────────────────────────────────────────────────────
# PHASE 2 — Code-sign the executable (reduces Defender ML weight significantly)
# ────────────────────────────────────────────────────────────────────────────────
if ($CertificatePath -and (Test-Path $CertificatePath)) {
    Write-Host "=== Phase 2: Sign EXE ===" -ForegroundColor Green

    $exeDir = Join-Path $DistDir "launcher"
    $exePath = Join-Path $exeDir $ExeName
    if (-not (Test-Path $exePath)) {
        throw "EXE not found at $exePath. Run without -SkipBuild first."
    }

    $signtool = "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe"
    if (-not (Test-Path $signtool)) {
        # Fallback: try to find signtool in common locations
        $signtool = Get-ChildItem -Path "${env:ProgramFiles(x86)}\Windows Kits" -Recurse -Filter "signtool.exe" | Select-Object -First 1 -ExpandProperty FullName
    }
    if (-not $signtool) {
        Write-Warning "signtool.exe not found. Install Windows SDK or Windows Driver Kit."
        Write-Warning "Skipping code signing."
    }
    else {
        $signArgs = @(
            "sign"
            "/fd", "SHA256"
            "/a"
            "/f", "`"$CertificatePath`""
            "/p", "`"$CertificatePassword`""
            "/tr", "http://timestamp.digicert.com"
            "/td", "SHA256"
            "`"$exePath`""
        )
        Write-Host "  -> Signing $exePath ..."
        & $signtool $signArgs
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  -> Signed successfully." -ForegroundColor Yellow
        }
        else {
            Write-Warning "Signing failed with exit code $LASTEXITCODE. Continuing unsigned."
        }
    }
    Write-Host ""
}
else {
    if (-not $SkipBuild) {
        Write-Host "=== Phase 2: SKIPPED (no -CertificatePath provided) ===" -ForegroundColor Gray
        Write-Host "  -> To sign the executable, pass: -CertificatePath <path> -CertificatePassword <pw>"
        Write-Host ""
    }
}

# ────────────────────────────────────────────────────────────────────────────────
# PHASE 3 — Stage (copy entire onedir runtime into staging)
# ────────────────────────────────────────────────────────────────────────────────
Write-Host "=== Phase 3: Stage ===" -ForegroundColor Green

# 3a. Verify source directory exists
$sourceDir = Join-Path $DistDir "launcher"
if (-not (Test-Path $sourceDir)) {
    throw "Source directory not found at $sourceDir. Run without -SkipBuild first."
}

# 3b. Clean and create staging directory
Write-Host "  -> Creating staging directory: $StagingDir"
if (Test-Path $StagingDir) { Remove-Item -Recurse -Force $StagingDir }
New-Item -ItemType Directory -Path $StagingDir -Force | Out-Null

# 3c. Copy EVERYTHING from dist\launcher\ into staging
#     With --onedir, this includes launcher.exe + python3*.dll + all .pyd + .dll + data dirs
Write-Host "  -> Copying all runtime files from $sourceDir ..."
Copy-Item -Path "$sourceDir\*" -Destination $StagingDir -Recurse -Force

# 3d. Validate staging contains the required files
$stagedExe = Join-Path $StagingDir $ExeName
if (-not (Test-Path $stagedExe)) {
    throw "Staging validation failed: $stagedExe missing."
}
Write-Host "  -> Staging contents ($((Get-ChildItem -Recurse $StagingDir | Measure-Object).Count) files):" -ForegroundColor Yellow
Get-ChildItem -Recurse $StagingDir | ForEach-Object { Write-Host "     $($_.FullName)" }

Write-Host "  -> Staging complete: $StagingDir" -ForegroundColor Yellow
Write-Host ""

# ────────────────────────────────────────────────────────────────────────────────
# PHASE 4 — Package (Inno Setup installer)
# ────────────────────────────────────────────────────────────────────────────────
if (-not $SkipPackage) {
    Write-Host "=== Phase 4: Package ===" -ForegroundColor Green

    # 4a. Locate Inno Setup compiler
    $isccPaths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
        "${env:ProgramFiles(x86)}\Inno Setup 5\ISCC.exe"
        "${env:ProgramFiles}\Inno Setup 5\ISCC.exe"
        "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe"
    )
    $iscc = $null
    foreach ($p in $isccPaths) {
        if (Test-Path $p) { $iscc = $p; break }
    }
    if (-not $iscc) {
        Write-Warning "Inno Setup compiler (ISCC.exe) not found."
        Write-Warning "Download from https://jrsoftware.org/isdl.php and install it."
        Write-Warning "Then re-run: .\scripts\build.ps1 -SkipBuild"
        throw "ISCC.exe not found. Install Inno Setup first."
    }

    # 4b. Clean previous installer
    $prevInstaller = Join-Path $ReleaseDir $InstallerName
    if (Test-Path $prevInstaller) { Remove-Item -Force $prevInstaller }

    # 4c. Compile installer
    Write-Host "  -> Compiling installer via Inno Setup..."
    Write-Host "     ISCC  : $iscc"
    Write-Host "     Script: $SetupIss"
    & $iscc $SetupIss /Q
    if ($LASTEXITCODE -ne 0) {
        throw "Inno Setup compilation failed with exit code $LASTEXITCODE."
    }

    # 4d. Verify installer exists
    if (-not (Test-Path $prevInstaller)) {
        throw "Installer not found at expected path: $prevInstaller"
    }
    Write-Host "  -> Installer created: $prevInstaller" -ForegroundColor Yellow
}
else {
    Write-Host "=== Phase 4: SKIPPED (--SkipPackage) ===" -ForegroundColor Gray
}

# ── Done ────────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== Build pipeline complete ===" -ForegroundColor Cyan
Write-Host "  Staging  : $StagingDir"
Write-Host "  Installer: $ReleaseDir\$InstallerName"
