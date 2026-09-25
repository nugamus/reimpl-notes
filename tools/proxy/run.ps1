# Launch the game windowed and in the background, without stealing focus.
#   powershell -ExecutionPolicy Bypass -File tools\proxy\run.ps1 [-Exe MissionD.exe]
# Click the game window when you want to play; switching away later does not pause it.
#
# How (tools/proxy/README.md, "Windowed and background"):
# - The startup dialog (portrait, OK/Exit) is the game's resource passed to Video4x_Init
#   (4xvideo.dll 0x10001005). Its dialog procedure (0x10001a20) sets fullscreen = 1 on
#   WM_INITDIALOG but still accepts the stock 4X "Window" command 0x3f7, which selects
#   h3d's windowed mode (DDSCL_NORMAL, no exclusive mode, no surface loss on focus change).
#   OK is control 0x3f3 (1011). Both are posted as the WM_COMMANDs the buttons would send.
# - MONET_BACKGROUND=1 makes the h3d proxy swallow focus-loss messages, so the game's own
#   window procedure (MissionMonet.exe 0x00416650) never clears its "active" flag.
# - The process starts with SW_SHOWMINNOACTIVE and tools/proxy/patch_exe.py makes the game
#   window SW_SHOWNOACTIVATE; nothing here calls SetForegroundWindow.
param([string]$Exe = 'MissionMonet.exe', [string]$Run = 'C:\MonetRun', [int]$TimeoutSec = 180)

Add-Type @'
using System;using System.Runtime.InteropServices;using System.Text;
public class U{
  public delegate bool P(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(P p, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr h, int id);
  [DllImport("user32.dll")] public static extern bool LockSetForegroundWindow(uint code);
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)] public struct SI {
    public int cb; public string r, d, t; public int x, y, w, h, xc, yc, fill, flags; public short show, r2;
    public IntPtr r3, i, o, e; }
  [StructLayout(LayoutKind.Sequential)] public struct PI { public IntPtr hp, ht; public int pid, tid; }
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] static extern bool CreateProcess(
    string app, string cmd, IntPtr pa, IntPtr ta, bool inherit, int flags, IntPtr env, string dir, ref SI si, out PI pi);
  // STARTF_USESHOWWINDOW + SW_SHOWMINNOACTIVE: Windows applies it to the process's first
  // shown window (the startup dialog), so nothing appears in front or takes focus.
  public static int Start(string exe, string dir){
    var si = new SI(); si.cb = Marshal.SizeOf(si); si.flags = 1; si.show = 7; PI pi;
    if (!CreateProcess(exe, null, IntPtr.Zero, IntPtr.Zero, false, 0, IntPtr.Zero, dir, ref si, out pi))
      throw new System.ComponentModel.Win32Exception();
    return pi.pid; }
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

$WM_COMMAND = 0x0111; $ID_WINDOWED = 0x3f7; $ID_OK = 0x3f3
$env:MONET_BACKGROUND = '1'
# Launched from a terminal you are typing in, this script and the game inherit the right
# to take the foreground: the dialog then activates on creation and the game window when the
# dialog closes. LSFW_LOCK drops that right until you next click or press Alt.
[U]::LockSetForegroundWindow(1) | Out-Null
$p = Get-Process -Id ([U]::Start((Join-Path $Run $Exe), $Run))
$deadline = (Get-Date).AddSeconds($TimeoutSec)
$confirmed = $false
while ((Get-Date) -lt $deadline -and -not $p.HasExited -and -not $confirmed) {
    $dlg = [U]::FindWindowOf($p.Id, '#32770')
    if ($dlg -ne [IntPtr]::Zero -and [U]::GetDlgItem($dlg, $ID_OK) -ne [IntPtr]::Zero) {
        [U]::PostMessage($dlg, $WM_COMMAND, [IntPtr]$ID_WINDOWED, [IntPtr]::Zero) | Out-Null
        [U]::PostMessage($dlg, $WM_COMMAND, [IntPtr]$ID_OK, [U]::GetDlgItem($dlg, $ID_OK)) | Out-Null
        Start-Sleep -Seconds 1
        $confirmed = ([U]::FindWindowOf($p.Id, '#32770') -eq [IntPtr]::Zero)
    }
    Start-Sleep -Milliseconds 200
}
if ($p.HasExited) { "game exited early (code $($p.ExitCode))"; exit 1 }
if (-not $confirmed) { "no startup dialog confirmed within $TimeoutSec s (pid $($p.Id))"; exit 2 }

# The game only runs while its "active" flag is set; set it without activating the window.
$main = [IntPtr]::Zero
for ($i = 0; $i -lt 50 -and $main -eq [IntPtr]::Zero; $i++) {
    Start-Sleep -Milliseconds 200
    $main = [U]::FindWindowOf($p.Id, 'Monet - The Mystery of the Orangerie Museum')
}
if ($main -ne [IntPtr]::Zero) { [U]::PostMessage($main, 0x001C, [IntPtr]1, [IntPtr]::Zero) | Out-Null }   # WM_ACTIVATEAPP(TRUE)
"started $Exe pid $($p.Id), windowed, background"
