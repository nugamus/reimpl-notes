# Send input to the running original game without focusing it (posted window messages).
#   powershell -ExecutionPolicy Bypass -File tools\proxy\send.ps1 -Text "Name" -Enter
#   ... -Key 0x26 -HoldMs 2000          virtual key (0x26 = Up) held for 2 s
#   ... -ClickX 320 -ClickY 240         left click at game coordinates (640x480)
#   ... -Process scummvm                 drive the engine instead
# The game reads keys and mouse from window messages in the shipping build; MissionD also
# uses DirectInput, which posted messages do not reach.
param([string]$Text = '', [switch]$Enter, [int]$Key = -1, [int]$HoldMs = 100,
      [int]$ClickX = -1, [int]$ClickY = -1, [string]$Process = '')
Add-Type @'
using System;using System.Runtime.InteropServices;
public class I{[DllImport("user32.dll")]public static extern bool PostMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
  [StructLayout(LayoutKind.Sequential)] public struct R { public int l, t, r, b; }
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out R r);
  [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr c);
  [DllImport("user32.dll")] public static extern uint MapVirtualKey(uint code, uint type);}
'@
$names = if ($Process) { $Process } else { 'MissionMonet', 'MissionD' }
$p = Get-Process $names -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { 'game not running'; exit 1 }
$h = $p.MainWindowHandle
function Tap($vk, $ms) {
    # lParam carries the scan code: SDL (the engine) maps most keys by it
    $sc = [int64][I]::MapVirtualKey($vk, 0) -shl 16
    if (($vk -ge 0x21 -and $vk -le 0x28) -or $vk -eq 0x2D -or $vk -eq 0x2E) { $sc += 0x1000000 }   # extended key
    [I]::PostMessage($h, 0x0100, [IntPtr]$vk, [IntPtr](1 + $sc)) | Out-Null        # WM_KEYDOWN
    Start-Sleep -Milliseconds $ms
    [I]::PostMessage($h, 0x0101, [IntPtr]$vk, [IntPtr](0xC0000001 + $sc)) | Out-Null   # WM_KEYUP
}
foreach ($c in $Text.ToCharArray()) { [I]::PostMessage($h, 0x0102, [IntPtr][int]$c, [IntPtr]1) | Out-Null; Start-Sleep -Milliseconds 60 }
if ($Enter) { Tap 0x0D 80 }
if ($Key -ge 0) { Tap $Key $HoldMs }
if ($ClickX -ge 0) {
    # A DPI-unaware game window reads posted coordinates in its logical client size (512x384
    # at 125% scaling) and scales them to its 640x480 frame; ask for that size the same way.
    [I]::SetThreadDpiAwarenessContext([IntPtr]-1) | Out-Null   # DPI_AWARENESS_CONTEXT_UNAWARE
    $r = New-Object I+R; [I]::GetClientRect($h, [ref]$r) | Out-Null
    $x = [int]($ClickX * $r.r / 640); $y = [int]($ClickY * $r.b / 480)
    $l = [IntPtr](($y -shl 16) -bor $x)
    [I]::PostMessage($h, 0x0200, [IntPtr]0, $l) | Out-Null; Start-Sleep -Milliseconds 100   # WM_MOUSEMOVE
    [I]::PostMessage($h, 0x0201, [IntPtr]1, $l) | Out-Null; Start-Sleep -Milliseconds 100   # WM_LBUTTONDOWN
    [I]::PostMessage($h, 0x0202, [IntPtr]0, $l) | Out-Null                                  # WM_LBUTTONUP
}
