; setup.iss
[Setup]
AppName=ImageCompressor
AppVersion=1.0
DefaultDirName={autopf}\ImageCompressor
DefaultGroupName=ImageCompressor
OutputBaseFilename=ImageCompressor-Setup-v1.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
; 我们由 PyInstaller 生成的 exe 文件将被打包进去
Source: "dist\ImageCompressor.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 创建开始菜单和桌面快捷方式
Name: "{group}\ImageCompressor"; Filename: "{app}\ImageCompressor.exe"
Name: "{commondesktop}\ImageCompressor"; Filename: "{app}\ImageCompressor.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:";