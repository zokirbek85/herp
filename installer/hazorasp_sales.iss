; Inno Setup skripti: Hazorasp Sales Management uchun Windows o'rnatuvchi.
; Compile: "C:\Users\Zalman\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer\hazorasp_sales.iss
; Natija: installer\output\HazoraspSalesManagement-Setup-<versiya>.exe

#define MyAppName "Hazorasp Sales Management"
#define MyAppVersion "0.2.0"
#define MyAppPublisher "Hazorasp Tekstil MCHJ"
#define MyAppExeName "HazoraspSalesManagement.exe"

[Setup]
AppId={{C9A4D8F2-3B1E-4A6C-9F0D-7E2B5C8A1D63}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=output
OutputBaseFilename=HazoraspSalesManagement-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Ish stolida belgicha yaratish"; GroupDescription: "Qo'shimcha belgichalar:"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
