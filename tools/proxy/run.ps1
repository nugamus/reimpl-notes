# Launch the game from the run folder and auto-confirm the startup dialog (portrait, OK/Exit).
#   powershell -ExecutionPolicy Bypass -File tools\proxy\run.ps1 [-Exe MissionD.exe] [-Foreground]
#
# Default is background mode: MONET_BACKGROUND=1 makes the h3d proxy swallow focus-loss
# messages, so the game keeps running behind other windows (tools/proxy/README.md), and
# the window is never brought to the front. -Foreground restores the original behaviour:
# the dialog and game get focus, and the game minimises and pauses when it loses focus.
#
# The dialog's OK button has control ID 1011 (not IDOK); this posts the same
# WM_COMMAND(1011, button) a click sends.
param([string]$Exe = 'MissionMonet.exe', [string]$Run = 'C:\MonetRun', [int]$TimeoutSec = 180,
      [switch]$Background, [int]$Width = 0, [int]$Height = 0)

Add-Type @'
using System;using System.Runtime.InteropServices;using System.Text;
public class U{
  public delegate bool P(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(P p, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern IntPtr FindWindowEx(IntPtr p, IntPtr a, string c, string t);
  [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
  public static IntPtr FindWindowOf(int pid, string cls){
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => {
      int id; GetWindowThreadProcessId(h, out id);
      var c = new StringBuilder(128); GetClassName(h, c, 128);
      if (id == pid && c.ToString() == cls && IsWindowVisible(h)) { found = h; return false; }
      return true; }, IntPtr.Zero);
    return found; }
}
'@

$Foreground = -not $Background
$env:MONET_BACKGROUND = if ($Background) { '1' } else { '0' }
$p = Start-Process -FilePath (Join-Path $Run $Exe) -WorkingDirectory $Run -PassThru
$deadline = (Get-Date).AddSeconds($TimeoutSec)
$confirmed = $false
while ((Get-Date) -lt $deadline -and -not $p.HasExited -and -not $confirmed) {
    $dlg = [U]::FindWindowOf($p.Id, '#32770')
    $ok = if ($dlg -ne [IntPtr]::Zero) { [U]::FindWindowEx($dlg, [IntPtr]::Zero, 'Button', 'OK') } else { [IntPtr]::Zero }
    if ($ok -ne [IntPtr]::Zero) {
        # Foreground mode: a real click hands the game focus, and dgVoodoo's DDraw.dll
        # crashes (c000041d) if Direct3D is set up while the game is merely in the background.
        if ($Foreground) { [U]::SetForegroundWindow($dlg) | Out-Null }
        Start-Sleep -Milliseconds 300
        [U]::PostMessage($dlg, 0x0111, [IntPtr][U]::GetDlgCtrlID($ok), $ok) | Out-Null   # WM_COMMAND
        Start-Sleep -Seconds 1
        $confirmed = ([U]::FindWindowOf($p.Id, '#32770') -eq [IntPtr]::Zero)
    }
    Start-Sleep -Milliseconds 200
}
if ($p.HasExited) { "game exited early (code $($p.ExitCode))"; exit 1 }
if (-not $confirmed) { "no startup dialog confirmed within $TimeoutSec s (pid $($p.Id))"; exit 2 }

# Wait for the main game window, then size it (dgVoodoo scales the 640x480 image into it).
$main = [IntPtr]::Zero
for ($i = 0; $i -lt 50 -and $main -eq [IntPtr]::Zero; $i++) {
    Start-Sleep -Milliseconds 200
    $main = [U]::FindWindowOf($p.Id, 'Monet - The Mystery of the Orangerie Museum')
}
if ($main -ne [IntPtr]::Zero) {
    [U]::ShowWindow($main, 4) | Out-Null                                       # SW_SHOWNOACTIVATE
    if ($Width -gt 0) { [U]::SetWindowPos($main, [IntPtr]::Zero, 40, 40, $Width, $Height, 0x0014) | Out-Null }   # NOZORDER|NOACTIVATE; resizing can lose DirectDraw surfaces
    if ($Foreground) { [U]::SetForegroundWindow($main) | Out-Null }
    else { [U]::PostMessage($main, 0x001C, [IntPtr]1, [IntPtr]::Zero) | Out-Null }   # WM_ACTIVATEAPP(TRUE): sets the game's active flag
}
"started $Exe pid $($p.Id), background=$(-not $Foreground)"
