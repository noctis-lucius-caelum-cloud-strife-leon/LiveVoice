#define MyAppName "LiveVoice"
#define MyAppVersion "0.1.0"
#define MyAppExeName "LiveVoice.exe"

[Setup]
AppId={{BEE5C746-889B-49E7-A192-2E7C2B887D4A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=output
OutputBaseFilename=LiveVoice-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist\LiveVoice\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\LiveVoice"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\LiveVoice"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch LiveVoice"; Flags: nowait postinstall skipifsilent
