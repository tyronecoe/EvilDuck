#!/usr/bin/env python3
"""Actual composed dashboard in Linux Chromium with fully inert HTTP fixtures.

No device/server is contacted: every request is fulfilled or aborted by the
browser context. POSTs below are captured mock requests, never device actions.
"""
import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import pathlib
import re
import sys
from email.parser import BytesParser
from email.policy import default as email_policy
from urllib.parse import parse_qs, urlsplit

from playwright.async_api import async_playwright

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
ORIGIN = "http://evilduck.test"
AUTH = "synthetic-browser-auth"
RAW_ERROR = "SYNTHETIC_RAW_DIAGNOSTIC_MUST_NOT_RENDER_ON_HOME_" * 100


def raw_literals(source):
    found = re.findall(r'static const char (\w+)\[\] PROGMEM = R"rawliteral\((.*?)\)rawliteral";', source, re.S)
    result = dict(found)
    assert len(result) == len(found)
    for name in ["INDEX_HTML", "SETTINGS_HTML", "STYLE_CSS", "INDEX_JS", "SETTINGS_JS"]:
        assert name in result, name
    return result


def fields(request):
    content_type = request.headers.get("content-type", "")
    data = request.post_data_buffer or b""
    if content_type.startswith("multipart/form-data"):
        message = BytesParser(policy=email_policy).parsebytes(
            b"Content-Type: " + content_type.encode() + b"\r\nMIME-Version: 1.0\r\n\r\n" + data)
        return {part.get_param("name", header="content-disposition"):
                part.get_payload(decode=True).decode("utf-8") for part in message.iter_parts()}
    return {key: values[-1] for key, values in parse_qs(data.decode(), keep_blank_values=True).items()}


class Fixture:
    def __init__(self, literals):
        self.literals = literals
        self.calls = []
        self.unexpected = []
        self.errors = []
        self.auth_ok = True
        self.denied_paths = set()
        self.led_state = 0
        self.trace_enabled = False
        self.trial_active = False
        self.timing = 500
        self.hold_diagnostics = False
        self.diagnostics_gate = asyncio.Event()
        self.diagnostics_gate.set()
        self.diagnostics_started = asyncio.Event()
        self.hold_timing = False
        self.timing_gate = asyncio.Event()
        self.timing_gate.set()
        self.timing_started = asyncio.Event()
        self.status = dict(snapshotKind="request-capture", routeBRequestId="41", routeBPhase=0,
                           routeBOwned=False, routeBReason=1, routeBCapsMs=500, routeBLine=0,
                           routeBErrorCode=0, running=False, ssid="INERT FIXTURE AP", channel=1,
                           autorunEnabled=False, autorunScript="", hid=True, sdReady=False,
                           storage=False, storageRequested=False, storageState="disabled")

    def mutations(self):
        return [row for row in self.calls if row["method"] not in ("GET", "HEAD")]

    async def route(self, route):
        request = route.request
        address = urlsplit(request.url)
        path, method = address.path, request.method
        if address.scheme + "://" + address.netloc != ORIGIN:
            self.unexpected.append(dict(method=method, url="external-request-blocked"))
            return await route.abort()
        resources = {"/": ("INDEX_HTML", "text/html"), "/index.html": ("INDEX_HTML", "text/html"),
                     "/settings.html": ("SETTINGS_HTML", "text/html"), "/style.css": ("STYLE_CSS", "text/css"),
                     "/index.js": ("INDEX_JS", "application/javascript"), "/settings.js": ("SETTINGS_JS", "application/javascript")}
        if method == "GET" and path in resources:
            name, mime = resources[path]
            return await route.fulfill(status=200, content_type=mime, body=self.literals[name])
        if path == "/favicon.ico":
            return await route.fulfill(status=204, body="")
        body = fields(request) if method == "POST" else {}
        self.calls.append(dict(method=method, path=path, query=address.query,
                               authenticated=request.headers.get("x-duck-password") == AUTH,
                               field_names=sorted(body), timing_mode=body.get("mode") if path == "/caps-timing" else None))
        if not self.auth_ok or path in self.denied_paths or request.headers.get("x-duck-password") != AUTH:
            return await route.fulfill(status=401, content_type="text/plain", body=RAW_ERROR)
        if path in ("/led-test", "/caps-trial", "/hid-trace") and method == "GET":
            self.diagnostics_started.set()
            if self.hold_diagnostics:
                await self.diagnostics_gate.wait()
        if path == "/status" and method == "GET":
            value = self.status
        elif path in ("/list", "/library") and method == "GET":
            value = []
        elif path == "/exec/log" and method == "GET":
            return await route.fulfill(status=200, content_type="text/plain", body="No synthetic log entries.")
        elif path == "/led-test/data" and method == "GET":
            return await route.fulfill(status=200, content_type="text/plain", body="EVILDUCK TEST 123")
        elif (path, method) in [("/led-test", "GET"), ("/led-test/start", "POST"),
                                ("/led-test/stop", "POST"), ("/led-test/clear", "POST")]:
            if method == "POST":
                self.led_state = {"/led-test/start": 1, "/led-test/stop": 3, "/led-test/clear": 0}.get(path, self.led_state)
            value = dict(state=self.led_state, integrity=False, feedback="unknown", observed=False,
                         connected=False, reports=0, callbacks=0, buildId="SYNTHETIC", bootMarker="fixture")
        elif (path, method) in [("/caps-trial", "GET"), ("/caps-trial/start", "POST")]:
            if method == "POST" and path == "/caps-trial/start":
                self.trial_active = True
                self.status.update(routeBOwned=True, routeBPhase=6, running=True)
            value = dict(active=self.trial_active, requestId="41", owned=self.trial_active,
                         phase=6 if self.trial_active else 0, reason=0 if self.trial_active else 1,
                         trialId="41", requestedMs=0, buildId="SYNTHETIC")
        elif (path, method) in [("/hid-trace", "GET"), ("/hid-trace/enable", "POST"),
                                ("/hid-trace/disable", "POST")]:
            if method == "POST":
                self.trace_enabled = path == "/hid-trace/enable"
            value = dict(enabled=self.trace_enabled, first=0, latest=0, more=False, events=[],
                         windowUs=120000000, overwritten=0, clockErrors=0, buildId="SYNTHETIC")
        elif path == "/caps-timing":
            captured = self.timing
            if method == "GET":
                self.timing_started.set()
                if self.hold_timing:
                    await self.timing_gate.wait()
            elif method == "POST":
                assert body.get("mode") in ["standard", "mac"]
                self.timing = 500 if body["mode"] == "mac" else 5
                captured = self.timing
            value = dict(selectedMs=captured, requestCapsMs=500, owned=False, requestId="41",
                         lifetime="RAM until reboot; future admissions only", snapshotKind="request-capture")
        elif path == "/settings" and method == "GET":
            value = dict(ssid="INERT FIXTURE AP", channel=1, password_configured=True,
                         web_password_configured=True, password="synthetic-stale-ap-secret",
                         web_password="synthetic-stale-web-secret", stealth=False, hidden_ap=False,
                         disable_led=False, led_color="#112233", autorun_delay_min=0, autorun_delay_max=0)
        elif path == "/settings" and method == "POST":
            assert "password" not in body and "web_password" not in body, "Unrelated settings save disclosed replacement fields"
            return await route.fulfill(status=200, content_type="text/plain", body="OK (synthetic settings save)")
        elif path == "/stop" and method == "POST":
            owned = self.status["routeBOwned"]
            self.status.update(routeBOwned=False, routeBPhase=0, routeBReason=2, running=False)
            self.trial_active = False
            value = dict(engine="routeb", requestId="41", wasOwned=owned)
            # Intentionally do not alter LED receiver/trace: script STOP is separate.
            return await route.fulfill(status=202, content_type="application/json", body=json.dumps(value))
        else:
            self.unexpected.append(dict(method=method, path=path))
            return await route.abort()
        return await route.fulfill(status=200 if method == "GET" or not path.endswith("/start") else 202,
                                   content_type="application/json", body=json.dumps(value))


class Run:
    def __init__(self, browser, literals, output):
        self.browser, self.literals, self.output = browser, literals, output
        self.results = []
        self.assertions = 0

    def check(self, condition, message):
        self.assertions += 1
        if not condition:
            raise AssertionError(message)

    async def page(self, *, width=1280, height=900, mobile=False, fixture=None, path="/index.html"):
        fixture = fixture or Fixture(self.literals)
        context = await self.browser.new_context(viewport=dict(width=width, height=height),
                                                 is_mobile=mobile, has_touch=mobile,
                                                 service_workers="block", accept_downloads=False)
        await context.add_init_script("sessionStorage.setItem('duckPw', " + json.dumps(AUTH) + ");")
        await context.route("**/*", fixture.route)
        page = await context.new_page()
        page.set_default_timeout(5000)
        page.on("pageerror", lambda error: fixture.errors.append(str(error)))
        await page.goto(ORIGIN + path, wait_until="load")
        return context, page, fixture

    async def settle(self, page):
        await page.wait_for_timeout(100)

    async def unique_ids(self, page):
        ids = await page.locator("[id]").evaluate_all("nodes => nodes.map(n => n.id)")
        self.check(len(ids) == len(set(ids)), "Duplicate DOM IDs")

    async def stop_reachable(self, page):
        buttons = page.locator(".execution-strip button[onclick='stopScript()']")
        self.check(await buttons.count() > 0, "Global STOP control absent")
        visible = []
        for button in await buttons.all():
            if await button.is_visible():
                box = await button.bounding_box()
                if box and box["y"] >= -1 and box["y"] + box["height"] <= (await page.evaluate("innerHeight")) + 1:
                    visible.append(button)
        self.check(bool(visible), "No global STOP in viewport")
        button = visible[-1]
        self.check((await button.bounding_box())["height"] >= 44, "STOP target shorter than 44 px")
        self.check(await button.evaluate("e => {const r=e.getBoundingClientRect(), at=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); return at===e || e.contains(at);}"), "STOP is occluded")
        return button

    async def safe_fixture(self, fixture):
        self.check(not fixture.unexpected, "Unexpected or external request")
        self.check(not fixture.errors, "Uncaught browser JavaScript error")
        self.check(all(row["authenticated"] for row in fixture.calls), "API request omitted authentication")

    async def group(self, name, callback):
        before = self.assertions
        try:
            await callback()
            self.results.append(dict(name=name, status="PASS", assertions=self.assertions-before))
        except Exception as error:
            self.results.append(dict(name=name, status="FAIL", assertions=self.assertions-before,
                                     diagnostic=type(error).__name__ + ": " + str(error)))

    async def layout(self, width, height, mobile):
        context, page, fixture = await self.page(width=width, height=height, mobile=mobile)
        try:
            await page.wait_for_selector("#tab-dashboard:not([hidden])")
            await self.settle(page)
            await self.unique_ids(page)
            self.check(await page.locator("#tab-dashboard h2").first.inner_text() == "Status", "Home does not lead with Status")
            self.check(not await page.locator("#tab-diagnostics").is_visible(), "Diagnostics initially visible")
            self.check(await page.locator("#capsTimingMode").count() == 0, "Caps timing still on Home")
            for panel in ["ledTestResult", "capsTrialResult", "hidTraceResult"]:
                self.check(await page.locator("#"+panel).evaluate("e => Boolean(e.closest('#tab-diagnostics'))"), "Diagnostic outside Diagnostics view")
            self.check(await page.locator(".execution-strip").evaluate("e => Boolean(e.compareDocumentPosition(document.querySelector('.tabbar')) & Node.DOCUMENT_POSITION_FOLLOWING)"), "Navigation precedes STOP strip")
            for tab in ["dashboard", "scripts", "library", "logs", "diagnostics", "dashboard"]:
                await page.locator(".tabbtn[data-tab='"+tab+"']").click()
                self.check(await page.locator("#tab-"+tab).is_visible(), "Requested tab not visible")
                self.check(await page.locator(".tabpanel:visible").count() == 1, "Multiple tab panels visible")
            await page.locator(".tabbtn[data-tab='diagnostics']").click()
            details = page.locator("#tab-diagnostics details")
            self.check(await details.count() == 3, "Expected three collapsible diagnostic panels")
            for detail in await details.all():
                await detail.locator("summary").click()
            for button in await page.locator("#tab-diagnostics button").all():
                self.check(await button.evaluate("e => e.form===null"), "Diagnostic control accidentally submits a form")
            self.check(await page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "Expanded Diagnostics has page-wide horizontal overflow")
            await page.locator(".tabbtn[data-tab='dashboard']").click()
            self.check(not fixture.mutations(), "Navigation or panel expansion caused an action")
            self.check(await page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "Page-wide horizontal overflow")
            await page.screenshot(path=str(self.output / ("home-" + str(width) + ".png")), full_page=True)
            await page.locator(".tabbtn[data-tab='diagnostics']").click()
            await page.screenshot(path=str(self.output / ("diagnostics-" + str(width) + ".png")), full_page=True)
            await page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
            await self.stop_reachable(page)
            await self.safe_fixture(fixture)
        finally:
            await context.close()

    async def activity_and_stop(self):
        fixture = Fixture(self.literals)
        fixture.led_state = 1
        fixture.trace_enabled = True
        fixture.trial_active = True
        fixture.status.update(routeBOwned=True, routeBPhase=6, running=True)
        context, page, fixture = await self.page(width=390, height=844, mobile=True, fixture=fixture)
        try:
            await page.wait_for_function("/receiv|LED/i.test(document.getElementById('diagnosticsActivity').textContent)")
            indicator = await page.locator("#diagnosticsActivity").inner_text()
            self.check("trace" in indicator.lower(), "Active trace hidden from global indicator")
            self.check(not await page.locator("#tab-diagnostics").is_visible(), "Activity requires open Diagnostics")
            self.check(not fixture.mutations(), "Active-indicator polling mutated diagnostic state")
            before = len(fixture.mutations())
            stop = await self.stop_reachable(page)
            await stop.click()
            await page.wait_for_function("/Cancel|No active|Stopped/i.test(document.getElementById('stopResult').textContent)")
            self.check([r["path"] for r in fixture.mutations()[before:]] == ["/stop"], "STOP also changed diagnostic state")
            self.check(fixture.led_state == 1 and fixture.trace_enabled, "Script STOP falsely stopped receiver/trace")
            await self.safe_fixture(fixture)
        finally:
            await context.close()

    async def authentication(self):
        fixture = Fixture(self.literals)
        fixture.auth_ok = False
        context, page, fixture = await self.page(width=320, height=640, mobile=True, fixture=fixture)
        try:
            await page.wait_for_function("/auth|password|401/i.test(document.body.innerText)")
            self.check(RAW_ERROR[:80] not in await page.inner_text("body"), "Raw authentication body rendered on Home")
            self.check(len(await page.locator("#diagnosticsActivity").inner_text()) < 250, "Unbounded diagnostic error on Home")
            self.check(not fixture.mutations(), "Failed authentication caused mutation")
            await self.stop_reachable(page)
            await self.safe_fixture(fixture)
        finally:
            await context.close()
        fixture = Fixture(self.literals)
        fixture.auth_ok = False
        context, page, fixture = await self.page(path="/settings.html", fixture=fixture)
        try:
            await page.wait_for_function("/auth|401/i.test(document.getElementById('capsTimingResult').textContent)")
            self.check(await page.locator("#password").input_value() == "" and await page.locator("#web_password").input_value() == "", "Settings authentication error prefilled a secret")
            self.check(RAW_ERROR[:80] not in await page.inner_text("body"), "Raw authentication body rendered in Settings")
            self.check(not fixture.mutations(), "Settings authentication error caused action")
            await self.stop_reachable(page)
            await self.safe_fixture(fixture)
        finally:
            await context.close()

    async def control_wiring(self):
        context, page, fixture = await self.page()
        try:
            await page.locator(".tabbtn[data-tab='diagnostics']").click()
            for detail in await page.locator("#tab-diagnostics details").all():
                await detail.locator("summary").click()
            expected = [("ledAction('start')", "/led-test/start"), ("ledAction('stop')", "/led-test/stop"),
                        ("ledAction('clear')", "/led-test/clear"), ("hidTrace('enable')", "/hid-trace/enable"),
                        ("hidTrace('disable')", "/hid-trace/disable")]
            for handler, path in expected:
                before = len(fixture.mutations())
                await page.locator('button[onclick="'+handler+'"]').click()
                for _ in range(40):
                    if len(fixture.mutations()) > before:
                        break
                    await page.wait_for_timeout(25)
                self.check([row["path"] for row in fixture.mutations()[before:]] == [path], "Explicit diagnostic handler lost or duplicated")
                await self.settle(page)
            for handler, path in [("ledAction('')", "/led-test"), ("capsTrial(false)", "/caps-trial"), ("hidTrace('')", "/hid-trace")]:
                before = len([row for row in fixture.calls if row["path"] == path and row["method"] == "GET"])
                writes = len(fixture.mutations())
                await page.locator('button[onclick="'+handler+'"]').click()
                for _ in range(40):
                    if len([row for row in fixture.calls if row["path"] == path and row["method"] == "GET"]) > before:
                        break
                    await page.wait_for_timeout(25)
                self.check(len([row for row in fixture.calls if row["path"] == path and row["method"] == "GET"]) > before,
                           "Explicit diagnostic refresh lost its read-only handler")
                self.check(len(fixture.mutations()) == writes, "Diagnostic refresh mutated state")
            async def accept(dialog):
                await dialog.accept()
            page.once("dialog", accept)
            before = len(fixture.mutations())
            await page.locator("button[onclick='capsTrial(true)']").click()
            await page.wait_for_function("document.getElementById('capsTrialResult').textContent.includes('41')")
            self.check([row["path"] for row in fixture.mutations()[before:]] == ["/caps-trial/start"], "Caps trial start wiring changed")
            await page.locator("button[onclick='viewLedData(false)']").click()
            await page.wait_for_function("document.getElementById('ledTestText').textContent==='EVILDUCK TEST 123'")
            self.check(await page.locator("button[onclick='viewLedData(true)']").count() == 1, "Download control detached")
            await self.safe_fixture(fixture)
        finally:
            await context.close()

    async def delayed_diagnostic(self):
        fixture = Fixture(self.literals)
        fixture.hold_diagnostics = True
        fixture.diagnostics_gate.clear()
        context, page, fixture = await self.page(fixture=fixture)
        try:
            await asyncio.wait_for(fixture.diagnostics_started.wait(), 5)
            reads = len([r for r in fixture.calls if r["path"] in ["/led-test", "/caps-trial", "/hid-trace"]])
            for tab in ["diagnostics", "dashboard", "diagnostics", "scripts", "dashboard"]:
                await page.locator(".tabbtn[data-tab='"+tab+"']").click()
            self.check(len([r for r in fixture.calls if r["path"] in ["/led-test", "/caps-trial", "/hid-trace"]]) == reads,
                       "Navigation created overlapping diagnostic requests")
            statuses = len([r for r in fixture.calls if r["path"] == "/status"])
            await page.locator("#tab-dashboard button[onclick='refreshStatus()']").click()
            for _ in range(40):
                if len([r for r in fixture.calls if r["path"] == "/status"]) > statuses:
                    break
                await page.wait_for_timeout(25)
            self.check(len([r for r in fixture.calls if r["path"] == "/status"]) > statuses,
                       "Delayed Diagnostics blocked execution status progress")
            await (await self.stop_reachable(page)).click()
            await page.wait_for_function("/No active|Stop requested/i.test(document.getElementById('stopResult').textContent)")
            self.check([r["path"] for r in fixture.mutations()] == ["/stop"], "Delayed diagnostics blocked or duplicated STOP")
            fixture.diagnostics_gate.set()
            await self.settle(page)
            await self.safe_fixture(fixture)
        finally:
            fixture.diagnostics_gate.set()
            await context.close()

    async def settings(self):
        context, page, fixture = await self.page(width=390, height=844, mobile=True, path="/settings.html")
        try:
            await page.wait_for_function("document.getElementById('capsTimingMode').value==='mac'")
            await self.unique_ids(page)
            self.check(await page.locator("#password").input_value() == "", "AP secret prefilled")
            self.check(await page.locator("#web_password").input_value() == "", "Web secret prefilled")
            self.check(not fixture.mutations(), "Settings load changed config/timing")
            text = await page.locator("#capsTimingResult").inner_text()
            self.check("500" in text and "RAM" in text and "future" in text.lower(), "Timing lifetime/current value not truthful")
            await page.locator("#capsTimingMode").select_option("standard")
            await self.settle(page)
            self.check(not fixture.mutations(), "Changing timing dropdown applied automatically")
            apply = page.locator("button[onclick='capsTiming(true)']")
            await apply.click()
            await page.wait_for_function("document.getElementById('capsTimingResult').textContent.includes('5ms') || document.getElementById('capsTimingResult').textContent.includes('5 ms')")
            self.check(len(fixture.mutations()) == 1 and fixture.mutations()[0]["path"] == "/caps-timing" and fixture.mutations()[0]["timing_mode"] == "standard", "Explicit timing apply was not exactly once")
            await page.locator("#ssid").fill("INERT FIXTURE AP")
            await page.locator("#channel").fill("6")
            await page.locator("button[onclick='saveSettings()']").click()
            await page.wait_for_function("document.getElementById('log').textContent.includes('OK')")
            writes = fixture.mutations()
            self.check(len(writes) == 2 and writes[-1]["path"] == "/settings", "Unrelated save changed Caps timing")
            self.check("password" not in writes[-1]["field_names"] and "web_password" not in writes[-1]["field_names"], "Blank replacements submitted")
            await page.screenshot(path=str(self.output / "settings-390.png"), full_page=True)
            await page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
            await self.stop_reachable(page)
            self.check(await page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "Settings horizontal overflow")
            await self.safe_fixture(fixture)
        finally:
            await context.close()

    async def pending_timing(self):
        fixture = Fixture(self.literals)
        fixture.hold_timing = True
        fixture.timing_gate.clear()
        context, page, fixture = await self.page(path="/settings.html", fixture=fixture)
        try:
            await asyncio.wait_for(fixture.timing_started.wait(), 5)
            await page.locator("#capsTimingMode").select_option("standard")
            fixture.timing_gate.set()
            await self.settle(page)
            self.check(await page.locator("#capsTimingMode").input_value() == "standard", "Pending timing GET overwrote owner edit")
            self.check(not fixture.mutations(), "Pending timing read wrote config")
            await page.locator("button[onclick='capsTiming(true)']").click()
            await page.wait_for_timeout(100)
            self.check(len(fixture.mutations()) == 1 and fixture.mutations()[0]["timing_mode"] == "standard", "Edited selection not applied once")
            await self.safe_fixture(fixture)
        finally:
            fixture.timing_gate.set()
            await context.close()


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=pathlib.Path)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    parser.add_argument("--chromium", default="/usr/bin/chromium", type=pathlib.Path)
    args = parser.parse_args()
    assert not args.output_dir.exists(), "Use a fresh evidence directory"
    assert not args.output_dir.resolve().is_relative_to(ROOT), "Evidence must be outside tracked repository"
    args.output_dir.mkdir(parents=True)
    original = args.source.read_bytes()
    literals = raw_literals(original.decode())
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=str(args.chromium), headless=True,
                                                   args=["--no-sandbox", "--disable-dev-shm-usage"])
        run = Run(browser, literals, args.output_dir)
        for width, height, mobile in [(1280, 900, False), (320, 640, True), (390, 844, True)]:
            await run.group("layout-navigation-"+str(width), lambda w=width,h=height,m=mobile:run.layout(w,h,m))
        await run.group("hidden-active-diagnostics-and-script-stop", run.activity_and_stop)
        await run.group("authentication-errors-compact", run.authentication)
        await run.group("explicit-diagnostic-control-wiring-inert-only", run.control_wiring)
        await run.group("delayed-diagnostics-no-overlap-stop-responsive", run.delayed_diagnostic)
        await run.group("settings-private-replacements-and-explicit-timing", run.settings)
        await run.group("pending-timing-read-retains-owner-selection", run.pending_timing)
        result = dict(counts={name:sum(row["status"]==name for row in run.results) for name in ["PASS","FAIL"]},
                      assertions=run.assertions, results=run.results,
                      source=str(args.source), source_sha256=hashlib.sha256(original).hexdigest(),
                      browser=dict(engine="Chromium", version=browser.version, executable=str(args.chromium),
                                   platform="Linux", playwright=importlib.metadata.version("playwright")),
                      profiles=[dict(width=w,height=h,mobile=m,touch=m) for w,h,m in [(1280,900,False),(320,640,True),(390,844,True)]],
                      other_environments="Native High Sierra/newer macOS/Windows/Android/iOS and Firefox/WebKit not tested",
                      real_network_requests=False, real_device_operations=False, payloads_executed=False,
                      scope="Actual embedded HTML/CSS/JS with intercepted inert HTTP; mobile viewport/touch emulation is not physical OS/browser evidence")
        assert args.source.read_bytes() == original, "Source changed during browser test"
        (args.output_dir / "results.json").write_text(json.dumps(result, indent=2)+"\n")
        await browser.close()
    print(json.dumps(result, indent=2))
    return bool(result["counts"]["FAIL"])


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
