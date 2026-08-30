/* Stand-in for the real x3d.dll, used only to prove the proxy thunks are transparent.
 *
 * Built as x3d_orig.dll and placed beside the proxy, so the proxy loads this instead of
 * the engine. Each function checks the arguments it was handed and returns a value
 * derived from them, so a thunk that disturbs the stack or the registers shows up as a
 * wrong answer rather than as a plausible one.
 *
 * Two calling conventions are covered deliberately: the real engine's convention is
 * unknown, and the point of a tail jump is that it does not need to be known. */

#include <windows.h>

/* __cdecl, four arguments: caller cleans the stack. */
int __cdecl X3d_Camera_Get_Fov(int a, int b, int c, int d)
{
    if (a != 11 || b != 22 || c != 33 || d != 44)
        return -1;
    return 1000 + a + b + c + d;
}

/* __stdcall, four arguments: callee cleans the stack. If the thunk left anything behind,
   the caller's frame is corrupt once this returns. */
int __stdcall X3d_Camera_Get_Name(int a, int b, int c, int d)
{
    if (a != 11 || b != 22 || c != 33 || d != 44)
        return -1;
    return 2000 + a + b + c + d;
}

/* Eight arguments: pushes the return address far enough up the stack that an off-by-one
   in the thunk's [esp + 36] would read an argument instead. */
int __stdcall X3d_Camera_Get_Matrix(int a, int b, int c, int d, int e, int f, int g,
                                    int h)
{
    if (a != 1 || b != 2 || c != 3 || d != 4 || e != 5 || f != 6 || g != 7 || h != 8)
        return -1;
    return 3000 + a + b + c + d + e + f + g + h;
}

/* Floating point, returned in ST(0): the thunk must not have disturbed the x87 stack. */
double __cdecl X3d_Camera_Get_Polar(double x)
{
    return x * 2.0 + 0.5;
}

BOOL WINAPI DllMain(HINSTANCE self, DWORD reason, LPVOID reserved)
{
    (void)self;
    (void)reason;
    (void)reserved;
    return TRUE;
}
