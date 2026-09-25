# Install (or -Uninstall) the Indeo 4/5 Video for Windows codecs the cutscene AVIs need
# (IV41, IV50). Only the original game uses these; the ScummVM engine has its own decoders.
# Needs admin:
#   powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList '-ExecutionPolicy Bypass -File <this> -Src C:\MonetRun\codecs'"
#
# Source: the game CD's own Intel/Ligos installer (Indeo\iv5setup.exe), extracted with
# unshield. Only the two decoders are installed, not the rest of that package.
#   ir41_32.ax   Ligos Indeo Video 4.51.16.03    sha256 cf21a54c8b6608f0a056c7ff528cd01c7c6530bf77496fff1cbbdf2004bce577
#   ir50_32.dll  Ligos Indeo Video 5.11.15.2.56  sha256 9a2a7470f334ef1a09277b442332cf15e714711555c9b7d13b24ea9a59401910
# The game is 32-bit, so the files go to SysWOW64 and the 32-bit Drivers32 key.
param([string]$Src = 'C:\MonetRun\codecs', [switch]$Uninstall)
$ErrorActionPreference = 'Stop'
$log = Join-Path $env:TEMP 'monet-indeo-install.log'
Start-Transcript -Path $log -Force | Out-Null
$key = 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows NT\CurrentVersion\Drivers32'
$dst = Join-Path $env:WINDIR 'SysWOW64'
$codecs = @{ 'vidc.iv41' = @('ir41_32.ax', 'cf21a54c8b6608f0a056c7ff528cd01c7c6530bf77496fff1cbbdf2004bce577');
             'vidc.iv50' = @('ir50_32.dll', '9a2a7470f334ef1a09277b442332cf15e714711555c9b7d13b24ea9a59401910') }
foreach ($name in $codecs.Keys) {
    $file, $hash = $codecs[$name]
    if ($Uninstall) {
        Remove-ItemProperty -Path $key -Name $name -ErrorAction SilentlyContinue
        Remove-Item (Join-Path $dst $file) -ErrorAction SilentlyContinue
        "removed $name"
        continue
    }
    $from = Join-Path $Src $file
    if ((Get-FileHash $from -Algorithm SHA256).Hash -ne $hash) { throw "$file hash mismatch, refusing to install" }
    Copy-Item $from (Join-Path $dst $file) -Force
    New-ItemProperty -Path $key -Name $name -Value $file -PropertyType String -Force | Out-Null
    "installed $name = $file"
}
Stop-Transcript | Out-Null
