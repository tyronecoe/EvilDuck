#!/usr/bin/env python3
"""Actual composed static routes + pinned SDK response code; native mocks only.

WString allocations alone receive a deterministic quota. HTTP base, header
handling, response-object allocation and transport are mocks. This is not a
complete ESP32 heap, TCP or actual HTTP-stack simulation, nor a firmware build.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = pathlib.Path(__file__).resolve().parent / "native"
WORKSPACE = pathlib.Path("/workspace")
CORE = WORKSPACE / "scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/cores/esp32"
SDK = WORKSPACE / "tooling/arduino/user/libraries/ESP_Async_WebServer/src"
BASELINE = WORKSPACE / "scratch/editor-build-integration/build-v2-uninstalled/candidate/EvilDuckS3"
PINS = {
    CORE / "WString.cpp": "26d0f9519e50e7a78b66fc46be4cf4f6b8d7ed825ce70c1596bd424d975d8107",
    CORE / "WString.h": "4ae882b44440656ef99c685087e03e5102b36c217f15b1c8c4954c926bad100e",
    SDK / "WebResponses.cpp": "12055aa687cd0f6f719b65057c7a1d203baf6f0ef88e96b3fb4909ac68d0e6f8",
    SDK / "WebRequest.cpp": "3ca1c44ffef44e4fd7d8e900857e797469cd336bf846f2a9af61e02a0956e7ad",
    SDK / "ESPAsyncWebServer.h": "25db7c8fb30943307b28b181722187a65576f6ee778eeb99e29b1ef8db7915ba",
    SDK / "WebResponseImpl.h": "b90de8322a97af18e8cd6817b7a5c27999c6a5e0097f23ecd77a4e167d9ced75",
    BASELINE / "webserver.cpp": "02b1bed01526935e7c8ec1857dfc910221dda3977efc47185eafbc796e4a22f9",
    BASELINE / "webfiles.h": "df10d10fd612ecb8be37c0c8e3a092720af463870814cab1c649e8a70304e445",
}
EXPECTED_FIXED = "98bb1d99e2098c29b962285ec4760d1ab3ed0d6d656cceed55d138fba1e7455c"
EXPECTED_RESOURCES = {"INDEX_HTML", "SETTINGS_HTML", "TERMINAL_HTML", "CREDITS_HTML", "ERROR404_HTML",
                      "STYLE_CSS", "INDEX_JS", "SETTINGS_JS", "TERMINAL_JS"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def function(source, signature):
    """Extract a selected brace-balanced function from SHA-pinned C++ sources."""
    assert source.count(signature) == 1, signature
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--results", required=True, type=pathlib.Path)
    args = parser.parse_args()
    assert not args.output.exists() and not args.results.exists(), "Preserve earlier evidence; use fresh paths"
    assert not args.output.resolve().is_relative_to(ROOT), "Native output belongs outside repository"
    manifest_path = ROOT / "tests/dashboard_response_safety/source-manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest["after"] == [{"file": "webserver.cpp", "sha256": EXPECTED_FIXED}]
    source_bytes = {n: (args.source/n).read_bytes() for n in ["webserver.cpp", "webfiles.h"]}
    assert digest(source_bytes["webserver.cpp"]) == EXPECTED_FIXED
    assert digest(source_bytes["webfiles.h"]) == PINS[BASELINE/"webfiles.h"]
    for row in manifest["after"] + manifest["unchanged"]:
        assert digest((args.source/row["file"]).read_bytes()) == row["sha256"], row["file"]
    for path, expected in PINS.items():
        assert digest(path.read_bytes()) == expected, str(path)
    args.output.mkdir(parents=True)
    (args.output/"served").mkdir()
    for path in FIXTURES.iterdir():
        assert path.is_file()
        shutil.copyfile(path, args.output/path.name)
    for name in ["WString.cpp", "WString.h"]:
        shutil.copyfile(CORE/name, args.output/name)
    (args.output/"webfiles.h").write_bytes(source_bytes["webfiles.h"])

    sdk_response = (SDK/"WebResponses.cpp").read_text()
    sdk_request = (SDK/"WebRequest.cpp").read_text()
    sdk_header = (SDK/"ESPAsyncWebServer.h").read_text()
    constructor_signatures = [
        "AsyncBasicResponse::AsyncBasicResponse(int code, const char *contentType, const char *content)",
        "AsyncProgmemResponse::AsyncProgmemResponse(int code, const char *contentType, const uint8_t *content, size_t len, AwsTemplateProcessor callback)",
        "size_t AsyncProgmemResponse::_fillBuffer(uint8_t *data, size_t len)"]
    body_functions = [function(sdk_response, s) for s in constructor_signatures]
    request_signatures = [
        "AsyncWebServerResponse *AsyncWebServerRequest::beginResponse(int code, const char *contentType, const char *content, AwsTemplateProcessor callback)",
        "AsyncWebServerResponse *\n  AsyncWebServerRequest::beginResponse(int code, const char *contentType, const uint8_t *content, size_t len, AwsTemplateProcessor callback)"]
    body_functions += [function(sdk_request, s) for s in request_signatures]
    inline_signatures = [
        "void send(int code, const char *contentType = asyncsrv::empty, const char *content = asyncsrv::empty, AwsTemplateProcessor callback = nullptr)",
        "void send(int code, const String &contentType, const char *content = asyncsrv::empty, AwsTemplateProcessor callback = nullptr)",
        "void send(int code, const char *contentType, const uint8_t *content, size_t len, AwsTemplateProcessor callback = nullptr)",
        "void send(int code, const String &contentType, const uint8_t *content, size_t len, AwsTemplateProcessor callback = nullptr)",
        "void send_P(int code, const String &contentType, const uint8_t *content, size_t len, AwsTemplateProcessor callback = nullptr)",
        "void send_P(int code, const String &contentType, PGM_P content, AwsTemplateProcessor callback = nullptr)",
        "AsyncWebServerResponse *beginResponse(int code, const String &contentType, const uint8_t *content, size_t len, AwsTemplateProcessor callback = nullptr)"]
    # The char send_P declaration appears in separate ESP32/ESP8266 branches;
    # extract the ESP32 branch specifically, preserving its body verbatim.
    char_overload = sdk_header.index(inline_signatures[5])
    branch = sdk_header.rindex("#ifndef ESP8266\n", 0, char_overload)
    esp32_header = sdk_header[branch:].split("#else\n", 1)[0]
    inlines = [function(esp32_header if "PGM_P" in s else sdk_header, s) for s in inline_signatures]
    (args.output/"actual_sdk.inc").write_text("\n\n".join(body_functions)+"\n")
    (args.output/"request_inline.inc").write_text("\n\n".join(inlines)+"\n")
    before = function((BASELINE/"webserver.cpp").read_text(), "static void handleStatic(AsyncWebServerRequest *req)")
    after = function(source_bytes["webserver.cpp"].decode(), "static void handleStatic(AsyncWebServerRequest *req)")
    # Verifies no edits besides the eleven explicitly bounded overload selections.
    translated = re.sub(r'req->send_P\((\d+), ("[^"]+"), ([A-Z0-9_]+)\);',
                        r'req->send(\1, \2, reinterpret_cast<const uint8_t *>(\3), sizeof(\3) - 1);', before)
    assert translated == after and before.count("req->send_P(") == 11
    assert (BASELINE/"webserver.cpp").read_bytes().replace(before.encode(), after.encode(), 1) == source_bytes["webserver.cpp"], "Source outside static handler changed"
    (args.output/"actual_handlers.inc").write_text(before.replace("handleStatic(", "handleStaticBaseline(", 1)+"\n\n"+after+"\n")
    literals = dict(re.findall(r'static const char (\w+)\[\] PROGMEM = R"rawliteral\((.*?)\)rawliteral";', source_bytes["webfiles.h"].decode(), re.S))
    assert set(literals) == EXPECTED_RESOURCES

    flags = ["-std=c++17", "-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
             "-ffunction-sections", "-fdata-sections", "-I", str(args.output)]
    commands = [
        ["g++"]+flags+["-include", str(args.output/"hooks.h"), "-c", "WString.cpp", "-o", "WString.o"],
        ["g++"]+flags+["probe.cpp", "WString.o", "-Wl,--gc-sections", "-no-pie", "-o", "native-probe"]]
    for i, command in enumerate(commands):
        run = subprocess.run(command, cwd=args.output, text=True, capture_output=True)
        (args.output/("compile-"+str(i)+".stdout.txt")).write_text(run.stdout)
        (args.output/("compile-"+str(i)+".stderr.txt")).write_text(run.stderr)
        assert run.returncode == 0, run.stderr
    env = dict(os.environ, ASAN_OPTIONS="detect_leaks=1:halt_on_error=1", UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1")
    command = [str(args.output/"native-probe"), str(args.output/"served")]
    run = subprocess.run(command, cwd=args.output, env=env, text=True, capture_output=True, timeout=60)
    (args.output/"run.stdout.jsonl").write_text(run.stdout)
    (args.output/"run.stderr.txt").write_text(run.stderr)
    assert run.returncode == 0 and not run.stderr, run.stderr
    rows = [json.loads(line) for line in run.stdout.splitlines()]
    summary = rows.pop()
    assert summary["summary"] and summary["FAIL"] == 0 and summary["PASS"] == len(rows)
    assert summary["WString_live_allocations"] == 0
    served = {}
    for name, literal in literals.items():
        path = args.output/"served"/(name+".bin")
        data = path.read_bytes()
        assert data == literal.encode(), name
        served[name] = dict(file=str(path), bytes=len(data), sha256=digest(data))
    assert len(served) == 9
    for name, data in source_bytes.items():
        assert (args.source/name).read_bytes() == data, "Source changed during verification"
    assert manifest_path.read_bytes() == manifest_bytes
    result = dict(status="PASS", counts={"PASS":len(rows), "FAIL":0}, assertions=summary["assertions"],
                  results=rows, source=str(args.source), source_hashes={n:digest(v) for n,v in source_bytes.items()},
                  input_pins={str(p):s for p,s in PINS.items()},
                  test_inputs={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [pathlib.Path(__file__)]+sorted(FIXTURES.iterdir())},
                  source_manifest_sha256=digest(manifest_bytes),
                  verbatim_extractions={"SDK_response_and_factory_functions":{s:digest(v.encode()) for s,v in zip(constructor_signatures+request_signatures,body_functions)},
                                        "SDK_request_inline_functions":{s:digest(v.encode()) for s,v in zip(inline_signatures,inlines)},
                                        "baseline_handler_sha256":digest(before.encode()), "fixed_handler_sha256":digest(after.encode())},
                  portable_aliases=12, resources=9, served=served,
                  sanitizers=dict(ASan="PASS",UBSan="PASS",leaks="PASS",stderr_empty=True),
                  mocks=["HTTP base/header/transport and object allocation", "deterministic WString-only allocator quota", "native PROGMEM memcpy mapping"],
                  limitations="No actual TCP/HTTP-stack execution, ESP32 heap measurement, target compile or physical proof; host WString layout can differ from ESP32",
                  commands=commands+[command], firmware_built=False, hardware_access=False,
                  real_network_requests=False, credentials_used=False)
    args.results.parent.mkdir(parents=True,exist_ok=True)
    args.results.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"counts":result["counts"],"assertions":result["assertions"],"served":served},indent=2))


if __name__ == "__main__":
    main()
