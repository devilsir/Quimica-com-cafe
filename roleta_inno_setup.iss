
; Inno Setup Script for "Roleta Química" (Unicode)
; Save this file as UTF-8 (with BOM recommended).
; Compile with Inno Setup 6.x (Unicode).

#define MyAppName        "Roleta Química do café"
#define MyAppVersion     "1.0.0"
#define MyAppPublisher   "Devilsir"
#define MyAppURL         "https://github.com/devilsir/Quimica-com-cafe/"
#define MyAppExeName     "Roleta_Quimica.exe"    
#define MyDistFolder     "dist\Roleta_Quimica"  ; pasta gerada pelo PyInstaller (COLLECT name)
#define MyIconFile       "icone.ico"             

[Setup]
AppId={{BFEE0C13-EA9D-4C3F-B444-D42977096211}}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename={#MyAppName}_Setup_v{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ChangesEnvironment=no
SetupIconFile={#MyIconFile}
UsePreviousAppDir=yes

[Languages]
Name: "ptbr"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startafterinstall"; Description: "Executar {#MyAppName} ao concluir"; GroupDescription: "Opções"; Flags: checkedonce


[Dirs]
Name: "{app}\assets"
Name: "{app}\sons"
Name: "{app}\configs"; Permissions: users-modify
Name: "{app}\configs\exports"; Permissions: users-modify


[Files]
; Copia tudo da pasta gerada pelo PyInstaller
Source: "{#MyDistFolder}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs


Source: "assets\*";  DestDir: "{app}\assets";  Flags: ignoreversion recursesubdirs createallsubdirs
Source: "sons\*";    DestDir: "{app}\sons";    Flags: ignoreversion recursesubdirs createallsubdirs
Source: "configs\*"; DestDir: "{app}\configs"; Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent; Tasks: startafterinstall

[UninstallDelete]
Type: filesandordirs; Name: "{app}\configs\exports\*"

