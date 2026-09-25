# Send input to the running original game without focusing it (posted window messages).
#   powershell -ExecutionPolicy Bypass -File tools\proxy\send.ps1 -Text "Name" -Enter
#   ... -Key 0x26 -HoldMs 2000          virtual key (0x26 = Up) held for 2 s
#   ... -ClickX 320 -ClickY 240         left click at client coordinates
# The game reads keys and mouse from window messages in the shipping build; MissionD also
# uses DirectInput, which posted messages do not reach.
param([string]$Text = '', [switch]$Enter, [int]$Key = -1, [int]$HoldMs = 100,
      [int]$ClickX = -1, [int]$ClickY = -1)
Add-Type @'
using System;using System.Runtime.InteropServices;
public class I{[DllImport("user32.dll")]public static extern bool PostMessage(IntPtr h,uint m,IntPtr w,IntPtr l);}
'@
$p = Get-Process MissionMonet, MissionD -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { 'game not running'; exit 1 }
$h = $p.MainWindowHandle
function Tap($vk, $ms) {
    [I]::PostMessage($h, 0x0100, [IntPtr]$vk, [IntPtr]1) | Out-Null        # WM_KEYDOWN
    Start-Sleep -Milliseconds $ms
    [I]::PostMessage($h, 0x0101, [IntPtr]$vk, [IntPtr]0xC0000001) | Out-Null   # WM_KEYUP
}
foreach ($c in $Text.ToCharArray()) { [I]::PostMessage($h, 0x0102, [IntPtr][int]$c, [IntPtr]1) | Out-Null; Start-Sleep -Milliseconds 60 }
if ($Enter) { Tap 0x0D 80 }
if ($Key -ge 0) { Tap $Key $HoldMs }
if ($ClickX -ge 0) {
    $l = [IntPtr](($ClickY -shl 16) -bor $ClickX)
    [I]::PostMessage($h, 0x0200, [IntPtr]0, $l) | Out-Null; Start-Sleep -Milliseconds 100   # WM_MOUSEMOVE
    [I]::PostMessage($h, 0x0201, [IntPtr]1, $l) | Out-Null; Start-Sleep -Milliseconds 100   # WM_LBUTTONDOWN
    [I]::PostMessage($h, 0x0202, [IntPtr]0, $l) | Out-Null                                  # WM_LBUTTONUP
}
