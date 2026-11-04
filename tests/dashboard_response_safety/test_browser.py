#!/usr/bin/env python3
"""Inert browser checks using bodies reconstructed by the actual SDK native probe.

No request reaches a board or outside server. Passwords are synthetic fixture
values. No script, settings save, STOP, upload, delete, installer or HID is run.
"""
import argparse
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
import pathlib
import sys
from urllib.parse import urlsplit

from playwright.async_api import async_playwright

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / "tests/dashboard_cleanup/test_browser.py"
PARENT_SHA = "3713fa15a9d5ca9fa1bfe1fbfe4fde337af1b662c67c79921efe74aa05ce6166"
assert hashlib.sha256(PARENT.read_bytes()).hexdigest() == PARENT_SHA
spec = importlib.util.spec_from_file_location("static_response_browser_fixture", PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)


class Fixture(B.Fixture):
    def __init__(self, literals, empty_script=False):
        super().__init__(literals)
        self.empty_script = empty_script

    async def route(self, route):
        address = urlsplit(route.request.url)
        path = address.path
        if address.scheme + "://" + address.netloc == B.ORIGIN:
            if path == "/index.js" and self.empty_script:
                return await route.fulfill(status=200, content_type="application/javascript", body=b"")
            if path == "/favicon.ico":
                # Preserve the actual unrelated profile refusal, rather than
                # quietly making the old favicon error the proposed repair.
                return await route.fulfill(status=503, content_type="text/plain",
                                           body="Dynamic filesystem responses disabled in Route B candidate")
        return await super().route(route)


async def run(args):
    source = args.source / "webfiles.h"
    native_raw = args.native_results.read_bytes()
    native = json.loads(native_raw)
    assert native["status"] == "PASS" and native["counts"]["FAIL"] == 0
    assert native["source_hashes"]["webfiles.h"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert native["source_hashes"]["webserver.cpp"] == hashlib.sha256((args.source / "webserver.cpp").read_bytes()).hexdigest()
    raw = B.raw_literals(source.read_text())
    literals, resources = {}, {}
    for name, text in raw.items():
        body_file = args.native_output / "served" / (name + ".bin")
        if not body_file.exists():
            continue
        body = body_file.read_bytes()
        assert body == text.encode("utf-8"), "Native streaming body mismatch: " + name
        recorded = native["served"][name]
        assert body_file.resolve() == pathlib.Path(recorded["file"]).resolve()
        assert recorded["bytes"] == len(body) and recorded["sha256"] == hashlib.sha256(body).hexdigest()
        literals[name] = body.decode("utf-8")
        resources[name] = dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
    assert len(literals) == 9, "Require all nine actual native-reconstructed resources"
    assert not args.output.exists() and not args.results.exists(), "Use fresh evidence paths"
    args.output.mkdir(parents=True)
    results, assertions = [], 0

    def check(value, message):
        nonlocal assertions
        assertions += 1
        if not value:
            raise AssertionError(message)

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=str(args.browser_executable), headless=True,
                                          args=["--no-sandbox", "--disable-dev-shm-usage"])
        version = browser.version

        async def page(empty_script=False, seeded=False):
            fixture = Fixture(literals, empty_script)
            context = await browser.new_context(service_workers="block", accept_downloads=False)
            if seeded:
                await context.add_init_script("sessionStorage.setItem('duckPw', " + json.dumps(B.AUTH) + ");")
            await context.route("**/*", fixture.route)
            view = await context.new_page()
            view.set_default_timeout(5000)
            view.on("pageerror", lambda error: fixture.errors.append(str(error)))
            await view.goto(B.ORIGIN + "/", wait_until="load")
            return context, view, fixture

        async def clean(context, fixture, expected_errors=False):
            check(not fixture.unexpected, "Unexpected or outside request")
            check(not fixture.mutations(), "Browser verification sent a mutation")
            if not expected_errors:
                check(not fixture.errors, "Uncaught JavaScript error")
            await context.close()

        async def group(name, callback):
            start = assertions
            try:
                await asyncio.wait_for(callback(), 15)
                results.append(dict(name=name, status="PASS", assertions=assertions-start))
            except Exception as error:
                results.append(dict(name=name, status="FAIL", assertions=assertions-start,
                                    diagnostic=type(error).__name__ + ": " + str(error)))

        async def empty_control():
            context, view, fixture = await page(empty_script=True)
            try:
                await view.wait_for_timeout(200)
                check(await view.evaluate("typeof window.saveDuckPw") == "undefined", "Empty control defined handler")
                check(await view.locator("#chipRunning").inner_text() == "Checking…", "Empty control did not remain pending")
                await view.locator("#duckPw").fill(B.AUTH)
                await view.locator("#duckPw").blur()
                await view.wait_for_timeout(100)
                check(any("saveDuckPw is not defined" in e for e in fixture.errors), "Control failed to reproduce owner error")
                check(not any(c["path"] == "/status" for c in fixture.calls), "Empty script started status polling")
            finally:
                await clean(context, fixture, expected_errors=True)

        async def password_and_status():
            context, view, fixture = await page()
            try:
                await view.wait_for_function("document.getElementById('chipRunning').textContent === 'Sign in required'")
                check(await view.locator("#duckPw").input_value() == "", "Fixture unexpectedly seeded password")
                for name in ["saveDuckPw", "refreshStatus", "stopScript", "loadScript", "saveScript", "runEditorScript"]:
                    check(await view.evaluate("name => typeof window[name]", name) == "function", "Missing handler: " + name)
                await view.locator("#duckPw").fill(B.AUTH)
                await view.locator("#duckPw").blur()
                await view.wait_for_function("document.getElementById('chipRunning').textContent === 'Idle'")
                check(any(c["path"] == "/status" and c["authenticated"] for c in fixture.calls), "No authenticated status after field change")
                check("Checking" not in await view.locator("#runResult").inner_text(), "Execution label stuck")
                check(await view.locator("#editorSave").is_disabled(), "Empty editor became writable")
                check(await view.locator("#editorRun").is_disabled(), "Empty editor became runnable")
            finally:
                await clean(context, fixture)

        async def settings():
            context, view, fixture = await page(seeded=True)
            try:
                await view.goto(B.ORIGIN + "/settings.html", wait_until="load")
                await view.wait_for_function("document.getElementById('password').placeholder.indexOf('Configured') >= 0")
                check(await view.locator("#password").input_value() == "", "AP replacement populated")
                check(await view.locator("#web_password").input_value() == "", "Web replacement populated")
                check(await view.evaluate("typeof window.stopScript") == "function", "Settings STOP handler missing")
            finally:
                await clean(context, fixture)

        await group("empty_200_control_reproduces_owner_symptom", empty_control)
        await group("streamed_resources_manual_password_change_and_status", password_and_status)
        await group("streamed_settings_keeps_replacements_blank", settings)
        await browser.close()

    counts = dict(PASS=sum(r["status"] == "PASS" for r in results), FAIL=sum(r["status"] == "FAIL" for r in results))
    receipt = dict(scope="Linux Chromium inert fixture using actual SDK-reconstructed resource bytes",
                   counts=counts, assertions=assertions, results=results, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   resources=resources, browser=version, playwright=importlib.metadata.version("playwright"),
                   native_receipt_sha256=hashlib.sha256(native_raw).hexdigest(),
                   native_receipt=str(args.native_results),
                   browser_executable=str(args.browser_executable),
                   hardware=False, external_requests=False, owner_credentials=False, firmware_build=False,
                   mutations=False, native_High_Sierra_or_iPhone_verification=False)
    args.results.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(dict(counts=counts, assertions=assertions, results=results), indent=2))
    return int(counts["FAIL"] != 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["source", "native-output", "native-results", "output", "results"]:
        parser.add_argument("--" + name, type=pathlib.Path, required=True)
    parser.add_argument("--browser-executable", type=pathlib.Path, default=pathlib.Path("/usr/bin/chromium"))
    return asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
