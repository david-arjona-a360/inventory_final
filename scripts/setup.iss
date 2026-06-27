; ==============================================================================
; Inno Setup Script — Inventory Manager
; ==============================================================================
; Compile with:  ISCC.exe setup.iss
; Or via build pipeline:  .\scripts\build.ps1
; ==============================================================================

#define MyAppName      "Inventory Manager"
#define MyAppVersion   "1.0.0"
#define MyAppPublisher "a360incPanama"
#define MyAppURL       ""
#define MyAppExeName   "launcher.exe"

; Source paths are relative to this .iss file's directory.
; Staging directory is created by build.ps1 Phase 3.
#define StagingDir     "..\release\staging"
#define OutputDir      "..\release"
#define OutputFilename MyAppName + "_Setup_v" + MyAppVersion

; ---------------------------------------------------------------------------
; Setup section — installer metadata and behaviour
; ---------------------------------------------------------------------------
[Setup]
; Unique identifier for this app (change for your own app)
AppId={{E8A3B2C1-4D5F-4A6E-9B7C-8D2E1F3A4B5C}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Target folder — Program Files on 64-bit systems
DefaultDirName={autopf}\{#MyAppName}

; Use "All Users" mode — installs for every Windows user
PrivilegesRequired=admin

; Disable the "Select Program Group" page (we create shortcuts explicitly)
DisableProgramGroupPage=yes

; Output
OutputDir={#OutputDir}
OutputBaseFilename={#OutputFilename}

; Compression
Compression=lzma2/max
SolidCompression=yes

; UI
WizardStyle=modern
WizardResizable=no

; Installer icon (optional — uses Inno Setup default if file missing)
SetupIconFile=..\Theme\installer_icon.ico

; Uninstall
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Version info in installer properties
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName}
VersionInfoVersion={#MyAppVersion}

; ---------------------------------------------------------------------------
; Languages
; ---------------------------------------------------------------------------
[Languages]
Name: "english";   MessagesFile: "compiler:Default.isl"
Name: "spanish";   MessagesFile: "compiler:Languages\Spanish.isl"

; ---------------------------------------------------------------------------
; Tasks — user-selectable options during install
; ---------------------------------------------------------------------------
[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

; ---------------------------------------------------------------------------
; Files — everything that goes into the install directory
; ---------------------------------------------------------------------------
; With --onedir, staging contains launcher.exe + python3*.dll + all .pyd/.dll + data dirs.
; All files must be in the same directory so Windows finds the DLLs.
[Files]
Source: "{#StagingDir}\*";    DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; ---------------------------------------------------------------------------
; Icons — Start Menu + Desktop shortcuts
; ---------------------------------------------------------------------------
[Icons]
Name: "{autoprograms}\{#MyAppName}";                 Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}";                  Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; ---------------------------------------------------------------------------
; Run — optional post-install launch
; ---------------------------------------------------------------------------
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: postinstall nowait skipifsilent unchecked

; ---------------------------------------------------------------------------
; Uninstall — clean up config files left by the app
; ---------------------------------------------------------------------------
[UninstallRun]
; Remove the first-run config so the user sees onboarding again after reinstall
Filename: "{cmd}"; Parameters: "/c if exist ""{localappdata}\InsumosApp\config.json"" del ""{localappdata}\InsumosApp\config.json"""; Flags: runhidden
