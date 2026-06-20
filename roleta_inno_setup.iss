; Inno Setup Script for "Roleta Química"
; Compile com Inno Setup 6.x Unicode.
; Deixe este .iss na raiz do projeto:
; C:\Users\PICHAU\Desktop\Quimica-com-cafe

#define MyAppName "Roleta Química do Café"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Devilsir"
#define MyAppURL "https://github.com/devilsir/Quimica-com-cafe/"
#define MyAppExeName "Roleta_Quimica.exe"
#define MyDistFolder "dist\Roleta_Quimica"
#define MyIconFile "icone.ico"

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
OutputBaseFilename=Roleta_Quimica_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ChangesEnvironment=no
SetupIconFile={#MyIconFile}
UsePreviousAppDir=yes
CloseApplications=yes
CloseApplicationsFilter={#MyAppExeName}

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

; Garantia extra: copia assets/sons/configs da raiz do projeto também
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "sons\*"; DestDir: "{app}\sons"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "configs\*"; DestDir: "{app}\configs"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent; Tasks: startafterinstall

[UninstallDelete]
Type: filesandordirs; Name: "{app}\configs\exports"
