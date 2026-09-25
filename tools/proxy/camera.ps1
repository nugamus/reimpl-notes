# Print the running original's camera as the engine's start_camera value (x,y,z,yaw,pitch).
#   powershell -ExecutionPolicy Bypass -File tools\proxy\camera.ps1
# MissionMonet.exe: [0x00442640] is the current scene, scene +0x14c its camera, camera +0x14
# the position and +0x34 / +0x38 the angles a, e (E-0041). Shipping build only.
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
$scene = [BitConverter]::ToUInt32([M]::Read($h, 0x00442640, 4), 0)
$cam = [BitConverter]::ToUInt32([M]::Read($h, $scene + 0x14c, 4), 0)
$pos = [M]::Read($h, $cam + 0x14, 12)
$ang = [M]::Read($h, $cam + 0x34, 8)
$f = { param($b, $o) [BitConverter]::ToSingle($b, $o).ToString('R', [Globalization.CultureInfo]::InvariantCulture) }
"$(& $f $pos 0),$(& $f $pos 4),$(& $f $pos 8),$(& $f $ang 0),$(& $f $ang 4)"
