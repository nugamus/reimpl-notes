# Tracing proxies for the engine DLLs. 32-bit only — the game is x86, and the naked
# thunks in the generated sources are x86 inline assembly.
#
#   python engines/x3d/tools/proxy/gen_proxy.py
#   cmake -S engines/x3d/tools/proxy -B build/proxy -A Win32
#   cmake --build build/proxy --config Release
#
# Then copy the game install, rename x3d.dll to x3d_orig.dll, and drop the built x3d.dll
# in beside it. Never edit the originals in place.

cmake_minimum_required(VERSION 3.20)
project(monet_proxy C)

if(NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "32-bit build required; configure with -A Win32")
endif()

set(GENERATED "${CMAKE_CURRENT_SOURCE_DIR}/generated")

foreach(dll x3d h3d)
  if(NOT EXISTS "${GENERATED}/${dll}_proxy.c")
    message(FATAL_ERROR "${GENERATED}/${dll}_proxy.c missing; run engines/x3d/tools/proxy/gen_proxy.py")
  endif()

  add_library(${dll}_proxy SHARED "${GENERATED}/${dll}_proxy.c")
  set_target_properties(${dll}_proxy PROPERTIES
    OUTPUT_NAME ${dll}
    PREFIX ""
    LINK_FLAGS "/DEF:\"${GENERATED}/${dll}.def\"")

  if(MSVC)
    # C4731: the naked thunks manipulate ESP deliberately.
    # C4409: MSVC flags inline asm in a naked function that never returns normally; that
    # is the whole design — the tail jump transfers control to the real implementation.
    target_compile_options(${dll}_proxy PRIVATE /W3 /wd4731 /wd4409)
    # fopen/_snprintf are deliberate: the proxy must stay ANSI-C simple and loadable
    # into a 2000-era process without pulling in the secure-CRT variants.
    target_compile_definitions(${dll}_proxy PRIVATE _CRT_SECURE_NO_WARNINGS)
  endif()
endforeach()

# Selftest: a fake x3d_orig.dll plus a driver that calls through the real proxy and checks
# both the return values and the trace. Everything lands in the same output directory,
# because the proxy resolves x3d_orig.dll relative to itself.
enable_testing()

add_library(fake_x3d SHARED "${CMAKE_CURRENT_SOURCE_DIR}/test/fake_x3d.c")
set_target_properties(fake_x3d PROPERTIES
  OUTPUT_NAME x3d_orig
  PREFIX ""
  LINK_FLAGS "/DEF:\"${CMAKE_CURRENT_SOURCE_DIR}/test/fake_x3d.def\"")

add_executable(proxy_selftest "${CMAKE_CURRENT_SOURCE_DIR}/test/proxy_selftest.c")
add_dependencies(proxy_selftest x3d_proxy fake_x3d)
if(MSVC)
  target_compile_definitions(proxy_selftest PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

add_test(NAME proxy_selftest COMMAND proxy_selftest)
