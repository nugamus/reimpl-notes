/* Prove the generated naked thunks are transparent, before anyone puts them in front of
 * the game.
 *
 * Loads the built proxy (which in turn loads fake_x3d.c as x3d_orig.dll), calls through
 * it under two calling conventions and with a floating-point return, and checks both the
 * returned values and the trace the proxy wrote. A thunk that miscounts the stack returns
 * -1 from the fake, or corrupts the caller's frame, or logs the wrong export name.
 *
 * Exit code 0 on success; prints each failure and returns 1. */

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int(__cdecl *fn_cdecl4)(int, int, int, int);
typedef int(__stdcall *fn_stdcall4)(int, int, int, int);
typedef int(__stdcall *fn_stdcall8)(int, int, int, int, int, int, int, int);
typedef double(__cdecl *fn_double)(double);

static int failures;

static void check(int ok, const char *what)
{
    printf("%s %s\n", ok ? "ok  " : "FAIL", what);
    if (!ok)
        failures++;
}

/* Directory this executable lives in, with a trailing separator. */
static void own_dir(char *out, size_t cap)
{
    DWORD n = GetModuleFileNameA(NULL, out, (DWORD)cap);
    while (n > 0 && out[n - 1] != '\\' && out[n - 1] != '/')
        n--;
    out[n] = 0;
}

int main(void)
{
    char dir[MAX_PATH], proxy_path[MAX_PATH], trace_path[MAX_PATH], env[MAX_PATH + 16];
    char line[512];
    HMODULE proxy;
    fn_cdecl4 fov;
    fn_stdcall4 name;
    fn_stdcall8 matrix;
    fn_double polar;
    FILE *fh;
    int seen_fov = 0, seen_name = 0, seen_matrix = 0, seen_polar = 0, calls = 0, seen_run = 0, i;
    volatile int guard_before = 0x5a5a5a5a;
    volatile int guard_after = (int)0xa5a5a5a5;
    double d;

    own_dir(dir, sizeof(dir));
    _snprintf(proxy_path, sizeof(proxy_path), "%sx3d.dll", dir);
    _snprintf(trace_path, sizeof(trace_path), "%sproxy_selftest.trace", dir);
    proxy_path[sizeof(proxy_path) - 1] = 0;
    trace_path[sizeof(trace_path) - 1] = 0;

    /* The proxy reads this in DllMain, so it must be set before the library loads. */
    _snprintf(env, sizeof(env), "MONET_TRACE=%s", trace_path);
    env[sizeof(env) - 1] = 0;
    _putenv(env);
    _putenv("MONET_TRACE_RAW=1");   /* first pass: one line per run of identical calls */
    DeleteFileA(trace_path);

    proxy = LoadLibraryA(proxy_path);
    if (!proxy) {
        printf("FAIL cannot load %s (error %lu)\n", proxy_path,
               (unsigned long)GetLastError());
        return 1;
    }

    fov = (fn_cdecl4)GetProcAddress(proxy, "X3d_Camera_Get_Fov");
    name = (fn_stdcall4)GetProcAddress(proxy, "X3d_Camera_Get_Name");
    matrix = (fn_stdcall8)GetProcAddress(proxy, "X3d_Camera_Get_Matrix");
    polar = (fn_double)GetProcAddress(proxy, "X3d_Camera_Get_Polar");
    check(fov && name && matrix && polar, "all four exports resolve through the proxy");
    if (failures)
        return 1;

    /* 1000 + 11 + 22 + 33 + 44. A wrong answer means the arguments were disturbed; -1
       specifically means the fake saw the wrong values. */
    check(fov(11, 22, 33, 44) == 1110, "__cdecl, 4 args, arguments arrive intact");
    check(name(11, 22, 33, 44) == 2110, "__stdcall, 4 args, arguments arrive intact");
    check(matrix(1, 2, 3, 4, 5, 6, 7, 8) == 3036,
          "__stdcall, 8 args, deep stack arrives intact");

    d = polar(2.25);
    check(d == 5.0, "double argument and ST(0) return survive the thunk");

    /* Same export, same call site, three times: the trace must collapse it to one line. */
    for (i = 0; i < 3; i++)
        fov(11, 22, 33, 44);

    /* If a __stdcall thunk mismatched the stack cleanup, these locals would have been
       clobbered by the calls above. */
    check(guard_before == 0x5a5a5a5a && guard_after == (int)0xa5a5a5a5,
          "caller's frame intact after stdcall returns");

    /* The proxy flushes and closes the trace in DLL_PROCESS_DETACH. */
    FreeLibrary(proxy);

    fh = fopen(trace_path, "r");
    if (!fh) {
        printf("FAIL no trace written to %s\n", trace_path);
        return 1;
    }
    while (fgets(line, sizeof(line), fh)) {
        if (line[0] == '#')
            continue;
        calls++;
        if (strstr(line, "x3d.dll!X3d_Camera_Get_Fov"))
            seen_fov = 1;
        if (strstr(line, "X3d_Camera_Get_Fov") && strstr(line, " x3\n"))
            seen_run = 1;
        if (strstr(line, "x3d.dll!X3d_Camera_Get_Name"))
            seen_name = 1;
        if (strstr(line, "x3d.dll!X3d_Camera_Get_Matrix"))
            seen_matrix = 1;
        if (strstr(line, "x3d.dll!X3d_Camera_Get_Polar"))
            seen_polar = 1;
        if (!strstr(line, "ret=0x")) {
            printf("FAIL trace line lacks a return address: %s", line);
            failures++;
        }
    }
    fclose(fh);

    check(calls == 5, "one line per call, repeated calls collapsed into one");
    check(seen_run, "three calls from one site logged as a single ' x3' line");
    check(seen_fov && seen_name && seen_matrix && seen_polar,
          "each call logged under its own export name");

    /* Second pass, frame mode (the default): with no X3d_Render the calls form one open
       frame, written at unload, one line per call site with its count. */
    _putenv("MONET_TRACE_RAW=0");
    DeleteFileA(trace_path);
    proxy = LoadLibraryA(proxy_path);
    fov = (fn_cdecl4)GetProcAddress(proxy, "X3d_Camera_Get_Fov");
    name = (fn_stdcall4)GetProcAddress(proxy, "X3d_Camera_Get_Name");
    for (i = 0; i < 2; i++) {
        fov(11, 22, 33, 44);
        name(11, 22, 33, 44);
    }
    FreeLibrary(proxy);
    calls = seen_run = 0;
    fh = fopen(trace_path, "r");
    while (fh && fgets(line, sizeof(line), fh)) {
        if (line[0] == '#')
            continue;
        calls++;
        if (strstr(line, " x2\n"))
            seen_run++;
    }
    if (fh)
        fclose(fh);
    check(calls == 2 && seen_run == 2, "frame mode groups alternating calls per call site");

    printf("%s (%d failure(s))\n", failures ? "FAILED" : "proxy selftest ok", failures);
    return failures ? 1 : 0;
}
