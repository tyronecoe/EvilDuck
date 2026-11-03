#!/usr/bin/env python3
"""Inert reproduction of failed-load editor text being submitted by Save.

This is an audit reproducer, not a safety regression PASS. Every request is
intercepted; the synthetic source is never executed, and Save reaches only a
mock endpoint. A real device, owner script and external HTTP server are not used.
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
spec = importlib.util.spec_from_file_location("storage_audit_inert_browser", PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
NAME = "audit-only-source.duck"
SOURCE = "REM Synthetic audit control; never executed.\n"


class EditorFixture(B.Fixture):
    def __init__(self, literals, load_status):
        super().__init__(literals)
        self.load_status = load_status
        self.saved = []

    async def route(self, route):
        request = route.request
        address = urlsplit(request.url)
        path, method = address.path, request.method
        if address.scheme + "://" + address.netloc != B.ORIGIN:
            return await super().route(route)
        if (path, method) in [("/list", "GET"), ("/script/load", "POST"), ("/script", "POST")]:
            body = B.fields(request) if method == "POST" else {}
            authenticated = request.headers.get("x-duck-password") == B.AUTH
            self.calls.append(dict(method=method, path=path, authenticated=authenticated,
                                   field_names=sorted(body)))
            if not authenticated:
                return await route.fulfill(status=401, content_type="text/plain", body="Synthetic unauthorized")
            if path == "/list":
                return await route.fulfill(status=200, content_type="application/json", body=json.dumps([NAME]))
            if path == "/script/load":
                if body != {"name": NAME}:
                    self.unexpected.append(dict(method=method, path=path, reason="Wrong synthetic load body"))
                    return await route.abort()
                return await route.fulfill(status=self.load_status, content_type="text/plain",
                                           body=SOURCE if self.load_status == 200 else "Route B owns storage")
            self.saved.append(body)
            return await route.fulfill(status=200, content_type="text/plain", body="Saved to synthetic fixture only")
        if method not in ("GET", "HEAD"):
            # Even an accidental Run, STOP, diagnostic, settings or upload request
            # is blocked here, rather than fulfilled by the inherited fixture.
            self.unexpected.append(dict(method=method, path=path, reason="Forbidden non-read request"))
            return await route.abort()
        return await super().route(route)


async def exercise(browser, literals, output, load_status):
    fixture = EditorFixture(literals, load_status)
    run = B.Run(browser, literals, output)
    context, page, fixture = await run.page(fixture=fixture)
    assertions = 0

    def check(value, message):
        nonlocal assertions
        assertions += 1
        if not value:
            raise AssertionError(message)

    try:
        await page.locator(".tabbtn[data-tab='scripts']").click()
        await page.locator("#scripts .li").filter(has_text=NAME).get_by_role("button", name="Edit", exact=True).click()
        if load_status == 409:
            expected = "REM Load failed: HTTP 409: Route B owns storage\nREM File: " + NAME
            await page.wait_for_function("document.getElementById('editorBody').value.startsWith('REM Load failed:')")
        else:
            expected = SOURCE
            await page.wait_for_function("document.getElementById('editorBody').value === " + json.dumps(SOURCE))
        editor = await page.locator("#editorBody").input_value()
        check(editor == expected, "Unexpected actual editor text after load response")
        check(not fixture.saved, "Loading caused an automatic save")
        save = page.locator("#tab-scripts button[onclick='saveScript()']")
        check(await save.count() == 1 and await save.is_enabled(), "Cannot exercise existing explicit Save")
        await save.click()  # Mock storage only; no device is contacted.
        await page.wait_for_function("document.getElementById('log').textContent.includes('Saved to synthetic fixture only')")
        check(len(fixture.saved) == 1, "Expected exactly one mocked Save; no retry")
        submission = fixture.saved[0]
        expected_wire = expected.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
        check(submission == {"name": NAME, "content": expected_wire, "storage": "spiffs"},
              "Submitted body did not match multipart newline serialization and target: " + repr(submission))
        check(all(row["authenticated"] for row in fixture.calls), "Authentication header omitted")
        check(not fixture.unexpected, "Unexpected or external request")
        check(not fixture.errors, "Uncaught actual JavaScript error")
        check([row["path"] for row in fixture.calls if row["method"] == "POST"] == ["/script/load", "/script"],
              "Unexpected action, fallback or duplicate request")
        check(not any(row["path"].startswith(("/run", "/stop", "/send", "/upload")) for row in fixture.calls),
              "Execution, STOP, payload or upload endpoint was contacted")
        await page.screenshot(path=str(output / ("load-" + str(load_status) + "-explicit-mock-save.png")), full_page=True)
        return dict(name="failed-load-placeholder-explicit-save" if load_status == 409 else "successful-load-save-control",
                    classification="OBSERVED_DEFECT" if load_status == 409 else "CONTROL_CONFIRMED",
                    load_http_status=load_status, assertions=assertions, editor_text=editor,
                    submitted_content=submission["content"], requested_name=NAME,
                    multipart_newline_serialization="Textarea LF serialized as CRLF in multipart/form-data",
                    exactly_one_mock_save=True, no_automatic_save=True,
                    api_requests=fixture.calls, unexpected_requests=fixture.unexpected,
                    browser_errors=fixture.errors)
    finally:
        await context.close()


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--chromium", type=pathlib.Path, default=pathlib.Path("/usr/bin/chromium"))
    args = parser.parse_args()
    assert not args.output_dir.exists(), "Keep earlier receipts; use fresh evidence output"
    assert not args.output_dir.resolve().is_relative_to(ROOT), "Evidence must stay outside the source repository"
    args.output_dir.mkdir(parents=True)
    source = args.source.read_bytes()
    result = dict(source=str(args.source), source_sha256=hashlib.sha256(source).hexdigest(),
                  browser_fixture_sha256=PARENT_SHA, real_network_requests=False, hardware=False,
                  owner_sources_read=False, scripts_executed=False, real_saves=False,
                  scope="Actual composed embedded UI in intercepted Linux Chromium; no native Mac or device proof",
                  results=[], harness_failures=[])
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=str(args.chromium), headless=True,
                                                   args=["--no-sandbox", "--disable-dev-shm-usage"])
        result["browser"] = dict(engine="Chromium", version=browser.version, platform="Linux",
                                 playwright=importlib.metadata.version("playwright"))
        literals = B.raw_literals(source.decode())
        for status in [409, 200]:
            try:
                result["results"].append(await exercise(browser, literals, args.output_dir, status))
            except Exception as error:
                result["harness_failures"].append(dict(load_http_status=status,
                    error=type(error).__name__ + ": " + str(error)))
        await browser.close()
    assert args.source.read_bytes() == source, "Source changed during reproduction"
    result["classification"] = "HARNESS_ERROR" if result["harness_failures"] else "OBSERVED_DEFECT"
    result["assertions"] = sum(row["assertions"] for row in result["results"])
    result["counts"] = {label: sum(row["classification"] == label for row in result["results"])
                        for label in ["OBSERVED_DEFECT", "CONTROL_CONFIRMED"]}
    result["counts"]["HARNESS_ERROR"] = len(result["harness_failures"])
    result["interpretation"] = ("Harness errors prevent a completed audit classification; inspect preserved receipt."
                                if result["harness_failures"] else
                                "Explicit Save can submit a failed-load error placeholder as replacement source; "
                                "this confirms a UI data-loss risk, not an observed device overwrite. "
                                "Exit zero means the audit reproduction completed, not safe behavior PASS.")
    (args.output_dir / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return bool(result["harness_failures"])


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
