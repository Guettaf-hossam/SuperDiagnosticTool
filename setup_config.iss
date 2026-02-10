; Inno Setup Configuration for Super Diagnostic Tool
; Author: Hossam Guettaf
; Professional Windows Installer Setup Script

[Setup]
AppName=Super Diagnostic Tool
AppVersion=2.0
AppPublisher=Hossam Guettaf - Open Source
AppPublisherURL=https://github.com/Guettaf-hossam/SuperDiagnosticTool
AppSupportURL=https://github.com/Guettaf-hossam/SuperDiagnosticTool/issues
DefaultDirName={autopf}\SuperDiagnosticTool
DefaultGroupName=Super Diagnostic Tool
OutputDir=Installers
OutputBaseFilename=SuperDiagnosticTool_Setup
Compression=lzma2/max
SolidCompression=yes
SetupIconFile=
UninstallDisplayIcon={app}\SuperDiagnosticTool.exe
UninstallDisplayName=Super Diagnostic Tool
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
DisableWelcomePage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\SuperDiagnosticTool.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Super Diagnostic Tool"; Filename: "{app}\SuperDiagnosticTool.exe"
Name: "{group}\Uninstall Super Diagnostic Tool"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Super Diagnostic Tool"; Filename: "{app}\SuperDiagnosticTool.exe"; Tasks: desktopicon

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
