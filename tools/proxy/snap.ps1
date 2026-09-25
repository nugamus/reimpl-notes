# Capture the running original game's window to a PNG, even when it is behind other
# windows (PrintWindow with PW_RENDERFULLCONTENT). Reference images for the engine.
#   powershell -ExecutionPolicy Bypass -File tools\proxy\snap.ps1 out.png [process]
# [process] defaults to the original game; pass scummvm to capture the engine.
Add-Type @'
using System;using System.Runtime.InteropServices;
public class Q{[DllImport("user32.dll")]public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);
[DllImport("user32.dll")]public static extern bool GetWindowRect(IntPtr h,out RECT r);
[DllImport("user32.dll")]public static extern bool SetProcessDPIAware();
public struct RECT{public int L,T,R,B;}}
'@
[Q]::SetProcessDPIAware() | Out-Null
Add-Type -AssemblyName System.Drawing
$names = if ($args[1]) { $args[1] } else { 'MissionMonet', 'MissionD' }
$p = Get-Process $names -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { 'game not running'; exit 1 }
$h = $p.MainWindowHandle
$r = New-Object Q+RECT; [Q]::GetWindowRect($h, [ref]$r) | Out-Null
$b = New-Object Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T)
$g = [Drawing.Graphics]::FromImage($b); $dc = $g.GetHdc()
[Q]::PrintWindow($h, $dc, 2) | Out-Null
$g.ReleaseHdc($dc); $b.Save($args[0]); "saved $($args[0]) ($($r.R - $r.L)x$($r.B - $r.T), includes title bar)"
