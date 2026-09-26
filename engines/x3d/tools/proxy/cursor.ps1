# Print the running original's cursor state: mode, image name, bar name, and the app mode.
#   powershell -ExecutionPolicy Bypass -File tools\proxy\cursor.ps1
# MissionMonet.exe: [0x0046ec14] is the cursor; +4 mode (0 normal, 1 holding, 2 blinking),
# +8 kind, +0x2c image name, +0x4a bar name, +0x4d0/+0x4d8 the stash (E-0183, E-0210).
# [0x0046ec04] is the app; +0x47c app mode. Shipping build only.
Add-Type @'
using System;using System.Runtime.InteropServices;
public class M{
  [DllImport("kernel32.dll")] public static extern IntPtr OpenProcess(int a, bool i, int pid);
  [DllImport("kernel32.dll")] public static extern bool ReadProcessMemory(IntPtr h, IntPtr a, byte[] b, int n, out int r);
  public static byte[] Read(IntPtr h, long a, int n){ var b = new byte[n]; int r; ReadProcessMemory(h, (IntPtr)a, b, n, out r); return b; }
}
'@
$p = Get-Process MissionMonet -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { 'game not running'; exit 1 }
$h = [M]::OpenProcess(0x10, $false, $p.Id)   # PROCESS_VM_READ
$u32 = { param($a) [BitConverter]::ToUInt32([M]::Read($h, $a, 4), 0) }
$str = { param($a) ([Text.Encoding]::ASCII.GetString([M]::Read($h, $a, 30)) -split "`0")[0] }
$c = & $u32 0x0046ec14
$app = & $u32 0x0046ec04
"mode=$(& $u32 ($c + 4)) kind=$(& $u32 ($c + 8)) image=$(& $str ($c + 0x2c)) bar=$(& $str ($c + 0x4a)) stash=$(& $u32 ($c + 0x4d0)):$(& $str ($c + 0x4d8)) appmode=$(& $u32 ($app + 0x47c))"
# In U00 (game [0x0046ec18] +0x160 = 0) also the tutorial state (E-0201): gauge = scene +0x148,
# +4 running, +0x10 state (u16); unit +0x6d8 onStone, +0x6e4 moved, +0x6e8 turned, +0x6f0 glassesTaken,
# +0x6fc nearMonet, +0x700 spaceSeen, +0x704 started.
$scene = & $u32 0x00442640
if ($scene -and ([BitConverter]::ToUInt16([M]::Read($h, (& $u32 0x0046ec18) + 0x160, 2), 0) -eq 0)) {
    $g = & $u32 ($scene + 0x148)
    $f = foreach ($o in 0x6d8, 0x6e4, 0x6e8, 0x6f0, 0x6fc, 0x700, 0x704) { & $u32 ($scene + $o) }
    "U00 gauge run=$(& $u32 ($g + 4)) state=$([BitConverter]::ToUInt16([M]::Read($h, $g + 0x10, 2), 0)) onStone,moved,turned,glasses,nearMonet,space,started=$($f -join ',')"
}
