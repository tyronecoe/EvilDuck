#!/usr/bin/env python3
"""Actual composed script-editor safety checks with intercepted inert HTTP only.

All names and source are synthetic. No board, owner file, HID, firmware compiler,
installer or external server is used. Mock Save/Run/Delete requests are captured
in memory and never reach a device. Baseline negative evidence is recorded by the
unchanged script_storage_audit/test_editor_error.py separately.
"""
import argparse
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
import pathlib
import sys
from urllib.parse import parse_qs, urlsplit

from playwright.async_api import async_playwright

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / "tests/dashboard_cleanup/test_browser.py"
PARENT_SHA = "3713fa15a9d5ca9fa1bfe1fbfe4fde337af1b662c67c79921efe74aa05ce6166"
assert hashlib.sha256(PARENT.read_bytes()).hexdigest() == PARENT_SHA
spec = importlib.util.spec_from_file_location("editor_safety_inert_fixture", PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
A, C = "audit-a.duck", "audit-b.duck"
TEXT_A = "REM Synthetic editor fixture A; never executed.\n"
TEXT_B = "REM Synthetic editor fixture B; never executed.\n"


def wire(text):
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")


class Plan:
    def __init__(self, *, status=200, body=TEXT_A, mime="text/plain", abort=False, hold=False):
        self.status, self.body, self.mime, self.abort = status, body, mime, abort
        self.started = asyncio.Event()
        self.gate = asyncio.Event()
        if not hold:
            self.gate.set()


class Fixture(B.Fixture):
    def __init__(self, literals):
        super().__init__(literals)
        self.plans = {A: Plan(body=TEXT_A), C: Plan(body=TEXT_B)}
        self.saves, self.runs, self.deletes = [], [], []
        self.save_gate = asyncio.Event()
        self.save_gate.set()
        self.save_started = asyncio.Event()
        self.save_status, self.save_mime, self.save_body, self.save_abort = 200, "text/plain", None, False

    async def route(self, route):
        request = route.request
        address = urlsplit(request.url)
        path, method = address.path, request.method
        if address.scheme + "://" + address.netloc != B.ORIGIN:
            return await super().route(route)
        query = parse_qs(address.query)
        special = (path, method) in [("/list", "GET"), ("/library", "GET"),
                   ("/script/load", "POST"), ("/script", "GET"), ("/script", "POST"),
                   ("/run", "GET"), ("/delete", "POST")]
        if not special:
            if method not in ("GET", "HEAD") and path != "/stop":
                self.unexpected.append(dict(method=method, path=path, reason="Forbidden action"))
                return await route.abort()
            return await super().route(route)
        body = B.fields(request) if method == "POST" else {}
        authenticated = request.headers.get("x-duck-password") == B.AUTH
        self.calls.append(dict(method=method, path=path, query=address.query,
                               authenticated=authenticated, field_names=sorted(body),
                               selected_name=body.get("name", query.get("s", [None])[0])))
        if not authenticated:
            return await route.fulfill(status=401, content_type="text/plain", body="Synthetic auth refusal")
        if path == "/list" or path == "/library" and "s" not in query:
            return await route.fulfill(status=200, content_type="application/json", body=json.dumps([A, C]))
        if path in ("/script/load", "/script", "/library") and (method == "GET" or path == "/script/load"):
            name = body.get("name") if method == "POST" else query.get("s", [""])[0]
            plan = self.plans.get(name, Plan(status=404, body="Synthetic not found"))
            plan.started.set()
            await plan.gate.wait()
            if plan.abort:
                return await route.abort("failed")
            return await route.fulfill(status=plan.status, content_type=plan.mime, body=plan.body)
        if path == "/script":
            self.saves.append(body)
            self.save_started.set()
            await self.save_gate.wait()
            if self.save_abort:
                return await route.abort("failed")
            return await route.fulfill(status=self.save_status, content_type=self.save_mime,
                                       body="Saved to " + body.get("name", "") if self.save_body is None else self.save_body)
        if path == "/run":
            self.runs.append(query)
            return await route.fulfill(status=202, content_type="application/json",
                                       body=json.dumps(dict(engine="routeb", requestId="41", state="queued")))
        self.deletes.append(body)
        return await route.fulfill(status=200, content_type="text/plain", body="Deleted inert fixture only")


class Suite:
    def __init__(self, browser, literals, output):
        self.browser, self.literals, self.output = browser, literals, output
        self.results, self.assertions = [], 0

    def check(self, value, message):
        self.assertions += 1
        if not value:
            raise AssertionError(message)

    async def page(self):
        fixture = Fixture(self.literals)
        run = B.Run(self.browser, self.literals, self.output)
        context, page, fixture = await run.page(fixture=fixture)
        await page.locator(".tabbtn[data-tab='scripts']").click()
        return context, page, fixture

    async def close(self, context, page, fixture):
        for plan in fixture.plans.values():
            plan.gate.set()
        fixture.save_gate.set()
        await page.wait_for_timeout(75)
        self.check(not fixture.unexpected, "Unexpected/external/forbidden request")
        self.check(not fixture.errors, "Uncaught actual JavaScript error")
        self.check(all(row["authenticated"] for row in fixture.calls), "API request omitted authentication")
        await context.close()

    async def group(self, name, callback):
        before = self.assertions
        try:
            await asyncio.wait_for(callback(), 15)
            self.results.append(dict(name=name, status="PASS", assertions=self.assertions-before))
        except Exception as error:
            self.results.append(dict(name=name, status="FAIL", assertions=self.assertions-before,
                                     diagnostic=type(error).__name__ + ": " + str(error)))

    async def direct_actions_blocked(self, page, fixture):
        writes, runs = len(fixture.saves), len(fixture.runs)
        await page.evaluate("async () => { await saveScript(); await runEditorScript(); }")
        self.check(len(fixture.saves) == writes, "Handler guard allowed a Save")
        self.check(len(fixture.runs) == runs, "Handler guard allowed an editor Run")

    async def blank_guard(self):
        context, page, fixture = await self.page()
        try:
            await self.direct_actions_blocked(page, fixture)
            await page.locator("#editorName").fill("forged-selection.duck")
            await page.evaluate("document.getElementById('editorBody').value='REM Cannot forge a successful load.'")
            await self.direct_actions_blocked(page, fixture)
        finally:
            await self.close(context, page, fixture)

    async def failed_load(self, status=409, *, mime="text/plain", body=None, abort=False):
        context, page, fixture = await self.page()
        try:
            fixture.plans[A] = Plan(status=status, body="SYNTHETIC_SERVER_ERROR_NOT_SOURCE" if body is None else body,
                                    mime=mime, abort=abort)
            await page.evaluate("name => openEditor(name)", A)
            text = await page.locator("#editorBody").input_value()
            self.check(text == "", "Failed initial selection changed the source buffer")
            self.check("SYNTHETIC_SERVER_ERROR_NOT_SOURCE" not in text, "Server error body inserted as source")
            self.check(not text.startswith("REM Load failed:"), "Generated failure placeholder inserted as source")
            self.check(not fixture.saves and not fixture.runs, "Loading caused a write/run")
            await self.direct_actions_blocked(page, fixture)
            buttons = page.locator("#tab-scripts button[onclick='saveScript()'], #tab-scripts button[onclick='runEditorScript()']")
            self.check(await buttons.count() == 2 and all([await b.is_disabled() for b in await buttons.all()]),
                       "Failed selection did not disable both action controls")
            if status == 409 and not abort and body is None and mime == "text/plain":
                await page.screenshot(path=str(self.output / "blocked-409-synthetic-editor.png"), full_page=True)
        finally:
            await self.close(context, page, fixture)

    async def retry(self):
        context, page, fixture = await self.page()
        try:
            fixture.plans[A] = Plan(status=409, body="Synthetic refused")
            await page.evaluate("name => openEditor(name)", A)
            await self.direct_actions_blocked(page, fixture)
            fixture.plans[A] = Plan(body=TEXT_A)
            await page.evaluate("loadScript()")
            self.check(await page.locator("#editorBody").input_value() == TEXT_A, "Retry did not load valid source")
            await page.evaluate("saveScript()")
            self.check(fixture.saves == [dict(name=A, content=wire(TEXT_A), storage="spiffs")], "Retry Save had wrong identity/content")
            self.check(not fixture.runs, "Retry unexpectedly ran source")
        finally:
            await self.close(context, page, fixture)

    async def ordinary(self):
        context, page, fixture = await self.page()
        try:
            await page.locator("#scripts .li").filter(has_text=A).get_by_role("button", name="Edit", exact=True).click()
            await page.wait_for_function("document.getElementById('editorBody').value === " + json.dumps(TEXT_A))
            edit = TEXT_A + "REM Explicit synthetic edit.\n"
            await page.locator("#editorBody").fill(edit)
            await page.evaluate("saveScript()")
            self.check(fixture.saves == [dict(name=A, content=wire(edit), storage="spiffs")], "Ordinary edit saved wrong content/path")
            await page.evaluate("runEditorScript()")
            self.check(len(fixture.saves) == 2 and fixture.saves[-1] == fixture.saves[0], "Editor Run did not retain ordinary save semantics")
            self.check(fixture.runs == [dict(engine=["routeb"], s=[A])], "Editor Run admission wrong or duplicated")
        finally:
            await self.close(context, page, fixture)

    async def identity_change(self, destination=False):
        context, page, fixture = await self.page()
        try:
            await page.evaluate("name => openEditor(name)", A)
            if destination:
                await page.locator("#editorStorage").select_option("sd")
            else:
                await page.locator("#editorName").fill(C)
            await self.direct_actions_blocked(page, fixture)
        finally:
            await self.close(context, page, fixture)

    async def new_script(self):
        context, page, fixture = await self.page()
        try:
            await page.evaluate("newScript()")
            await page.locator("#editorName").fill("intentional-new.duck")
            body = "REM Intentional synthetic new file.\n"
            await page.locator("#editorBody").fill(body)
            await page.evaluate("saveScript()")
            self.check(fixture.saves == [dict(name="intentional-new.duck", content=wire(body), storage="spiffs")], "Explicit New did not authorize intentional creation")
            self.check(not fixture.runs, "New automatically ran source")
        finally:
            await self.close(context, page, fixture)

    async def failed_then_new(self):
        context, page, fixture = await self.page()
        try:
            fixture.plans[A] = Plan(status=409)
            await page.evaluate("name => openEditor(name)", A)
            await page.evaluate("newScript()")
            await page.locator("#editorName").fill("new-after-failure.duck")
            await page.locator("#editorBody").fill("REM Intentional new after failed selection.\n")
            await page.evaluate("saveScript()")
            self.check(len(fixture.saves) == 1 and fixture.saves[0]["name"] == "new-after-failure.duck", "Failed state poisoned explicit New")
            self.check("Load failed" not in fixture.saves[0]["content"], "New reused diagnostic placeholder")
        finally:
            await self.close(context, page, fixture)

    async def out_of_order(self, no_abort=False):
        context, page, fixture = await self.page()
        try:
            if no_abort:
                await page.evaluate("window.AbortController=undefined")
            old = fixture.plans[A] = Plan(body=TEXT_A, hold=True)
            first = asyncio.create_task(page.evaluate("name => openEditor(name)", A))
            await asyncio.wait_for(old.started.wait(), 3)
            await self.direct_actions_blocked(page, fixture)
            await page.evaluate("name => openEditor(name)", C)
            old.gate.set()
            await first
            self.check(await page.locator("#editorName").input_value() == C, "Stale load rebound current filename")
            self.check(await page.locator("#editorBody").input_value() == TEXT_B, "Stale load replaced current source")
            await page.evaluate("saveScript()")
            self.check(fixture.saves == [dict(name=C, content=wire(TEXT_B), storage="spiffs")], "Racing load caused cross-file Save")
        finally:
            await self.close(context, page, fixture)

    async def new_while_loading(self):
        context, page, fixture = await self.page()
        try:
            old = fixture.plans[A] = Plan(body=TEXT_A, hold=True)
            first = asyncio.create_task(page.evaluate("name => openEditor(name)", A))
            await asyncio.wait_for(old.started.wait(), 3)
            await page.evaluate("newScript()")
            await page.locator("#editorName").fill("new-cancels-read.duck")
            await page.locator("#editorBody").fill("REM Explicit newer document.\n")
            old.gate.set()
            await first
            self.check(await page.locator("#editorName").input_value() == "new-cancels-read.duck", "Old load replaced explicit New identity")
            self.check(await page.locator("#editorBody").input_value() == "REM Explicit newer document.\n", "Old load replaced New text")
            await page.evaluate("saveScript()")
            self.check(len(fixture.saves) == 1 and fixture.saves[0]["name"] == "new-cancels-read.duck", "New document saved as old selection")
        finally:
            await self.close(context, page, fixture)

    async def dirty_switch_cancel(self):
        context, page, fixture = await self.page()
        try:
            await page.evaluate("name => openEditor(name)", A)
            draft = TEXT_A + "REM Unsaved synthetic draft.\n"
            await page.locator("#editorBody").fill(draft)
            await page.evaluate("() => { window.__choices=[]; window.confirm=m=>{window.__choices.push(m);return false;}; }")
            await page.evaluate("name => openEditor(name)", C)
            self.check(await page.evaluate("window.__choices.length") == 1, "Dirty selection switch lacked explicit decision")
            self.check(await page.locator("#editorName").input_value() == A, "Cancelled switch changed bound name")
            self.check(await page.locator("#editorBody").input_value() == draft, "Cancelled switch discarded draft")
            await page.evaluate("saveScript()")
            self.check(fixture.saves == [dict(name=A, content=wire(draft), storage="spiffs")], "Cancelled switch saved draft under wrong name")
        finally:
            await self.close(context, page, fixture)

    async def dirty_failed_switch_restore(self):
        context, page, fixture = await self.page()
        try:
            await page.evaluate("name => openEditor(name)", A)
            draft = TEXT_A + "REM Retain on failed switch.\n"
            await page.locator("#editorBody").fill(draft)
            await page.evaluate("() => { window.__choices=[];window.confirm=m=>{window.__choices.push(m);return true;}; }")
            fixture.plans[C] = Plan(status=409, body="Synthetic switch refused")
            await page.evaluate("name => openEditor(name)", C)
            self.check(await page.evaluate("window.__choices.length") == 1, "Dirty switch bypassed decision")
            self.check(await page.locator("#editorBody").input_value() == draft, "Failed switch lost unsaved buffer")
            self.check(await page.locator("#editorBody").is_editable() is False, "Failed buffer remains editable as wrong identity")
            await self.direct_actions_blocked(page, fixture)
            restore = page.locator("#editorRestore")
            self.check(await restore.is_visible(), "Preserved draft lacks explicit Restore path")
            await restore.click()
            self.check(await page.locator("#editorName").input_value() == A, "Restore did not return original identity")
            self.check(await page.locator("#editorBody").input_value() == draft, "Restore changed draft contents")
            await page.evaluate("saveScript()")
            self.check(fixture.saves == [dict(name=A, content=wire(draft), storage="spiffs")], "Restored draft saved as failed target")
        finally:
            await self.close(context, page, fixture)

    async def dirty_new_decision(self):
        context, page, fixture = await self.page()
        try:
            await page.evaluate("name => openEditor(name)", A)
            draft = TEXT_A + "REM Draft before explicit New.\n"
            await page.locator("#editorBody").fill(draft)
            await page.evaluate("() => { window.__choices=[];window.confirm=m=>{window.__choices.push(m);return false;}; }")
            await page.evaluate("newScript()")
            self.check(await page.evaluate("window.__choices.length") == 1, "New discarded unsaved content without a decision")
            self.check(await page.locator("#editorName").input_value() == A and await page.locator("#editorBody").input_value() == draft,
                       "Cancelled New changed original draft or identity")
            await page.evaluate("window.confirm=()=>true")
            await page.evaluate("newScript()")
            await page.locator("#editorName").fill("deliberate-new.duck")
            await page.locator("#editorBody").fill("REM Explicitly replacing editor document.\n")
            await page.evaluate("saveScript()")
            self.check(len(fixture.saves) == 1 and fixture.saves[0]["name"] == "deliberate-new.duck", "Explicit New decision did not create intended document")
        finally:
            await self.close(context, page, fixture)

    async def timeout(self):
        context, page, fixture = await self.page()
        try:
            pending = fixture.plans[A] = Plan(hold=True)
            load = asyncio.create_task(page.evaluate("name => openEditor(name)", A))
            await asyncio.wait_for(pending.started.wait(), 3)
            await self.direct_actions_blocked(page, fixture)
            await asyncio.wait_for(load, 6)
            self.check(await page.locator("#editorStatus").get_attribute("data-state") == "load-failed", "Timed-out load did not fail closed")
            await self.direct_actions_blocked(page, fixture)
            pending.gate.set()
            await page.wait_for_timeout(100)
            self.check(await page.locator("#editorStatus").get_attribute("data-state") == "load-failed", "Late timed-out response reactivated selection")
        finally:
            await self.close(context, page, fixture)

    async def double_click(self):
        context, page, fixture = await self.page()
        try:
            pending = fixture.plans[A] = Plan(hold=True)
            first = asyncio.create_task(page.evaluate("name => openEditor(name)", A))
            await asyncio.wait_for(pending.started.wait(), 3)
            second = asyncio.create_task(page.evaluate("name => openEditor(name)", A))
            await page.wait_for_timeout(100)
            await self.direct_actions_blocked(page, fixture)
            pending.gate.set()
            await asyncio.gather(first, second)
            self.check(await page.locator("#editorName").input_value() == A and await page.locator("#editorBody").input_value() == TEXT_A,
                       "Repeated selection lost latest valid binding")
            self.check(len([x for x in fixture.calls if x["path"] == "/script/load"]) <= 2, "Double selection retried automatically")
            self.check(not fixture.saves and not fixture.runs, "Double selection caused action")
        finally:
            await self.close(context, page, fixture)

    async def rapid_three(self):
        context, page, fixture = await self.page()
        try:
            first_plan = fixture.plans[A] = Plan(body=TEXT_A, hold=True)
            second_plan = fixture.plans[C] = Plan(status=409, body="Synthetic stale error", hold=True)
            third = "audit-c.duck"
            third_text = "REM Latest third synthetic selection.\n"
            fixture.plans[third] = Plan(body=third_text)
            first = asyncio.create_task(page.evaluate("name=>openEditor(name)", A))
            await asyncio.wait_for(first_plan.started.wait(), 3)
            second = asyncio.create_task(page.evaluate("name=>openEditor(name)", C))
            await asyncio.wait_for(second_plan.started.wait(), 3)
            await page.evaluate("name=>openEditor(name)", third)
            second_plan.gate.set()
            first_plan.gate.set()
            await asyncio.gather(first, second)
            self.check(await page.locator("#editorName").input_value() == third and await page.locator("#editorBody").input_value() == third_text,
                       "Late earlier success/error overwrote newest selection")
            await page.evaluate("saveScript()")
            self.check(fixture.saves == [dict(name=third, content=wire(third_text), storage="spiffs")], "Rapid selection caused cross-file write")
        finally:
            await self.close(context, page, fixture)

    async def pending_save_controls(self):
        context, page, fixture = await self.page()
        try:
            await page.evaluate("name=>openEditor(name)", A)
            fixture.save_gate.clear()
            pending = asyncio.create_task(page.evaluate("saveScript()"))
            await asyncio.wait_for(fixture.save_started.wait(), 3)
            await page.evaluate("async name=>{await saveScript();await runEditorScript();await openEditor(name);newScript();}", C)
            self.check(len(fixture.saves) == 1 and not fixture.runs, "Pending Save allowed duplicate write/run")
            self.check(await page.locator("#editorName").input_value() == A, "Selection changed while write pending")
            self.check(not any(row["path"] == "/script/load" and row.get("selected_name") == C for row in fixture.calls), "Write-pending handler started another load")
            fixture.save_gate.set()
            await pending
            self.check(fixture.saves == [dict(name=A, content=wire(TEXT_A), storage="spiffs")], "Pending write changed captured source")
        finally:
            await self.close(context, page, fixture)

    async def pending_run_tamper(self):
        context, page, fixture = await self.page()
        try:
            await page.evaluate("name=>openEditor(name)", A)
            fixture.save_gate.clear()
            pending = asyncio.create_task(page.evaluate("runEditorScript()"))
            await asyncio.wait_for(fixture.save_started.wait(), 3)
            await page.evaluate("name=>{document.getElementById('editorName').value=name;document.getElementById('editorBody').value='REM Direct stale tamper';}", C)
            fixture.save_gate.set()
            await pending
            self.check(fixture.saves == [dict(name=A, content=wire(TEXT_A), storage="spiffs")], "Pending editor Run changed in-flight save")
            self.check(not fixture.runs, "Late Save acknowledgement ran a rebound/stale selection")
            await self.direct_actions_blocked(page, fixture)
        finally:
            await self.close(context, page, fixture)

    async def legitimate_error_comment(self):
        context, page, fixture = await self.page()
        try:
            body = "REM Load failed: this is deliberate synthetic source text.\n"
            fixture.plans[A] = Plan(body=body)
            await page.evaluate("name=>openEditor(name)", A)
            await page.evaluate("saveScript()")
            self.check(fixture.saves == [dict(name=A, content=wire(body), storage="spiffs")], "Safety relies on banning harmless comment text")
        finally:
            await self.close(context, page, fixture)

    async def cancelled_switch_invalidates_pending_load(self):
        context, page, fixture = await self.page()
        try:
            await page.evaluate("name=>openEditor(name)", A)
            draft = TEXT_A + "REM Keep this original unsaved draft.\n"
            await page.locator("#editorBody").fill(draft)
            await page.evaluate("() => {window.confirm=()=>true;}")
            waiting = fixture.plans[C] = Plan(body=TEXT_B, hold=True)
            pending = asyncio.create_task(page.evaluate("name=>openEditor(name)", C))
            await asyncio.wait_for(waiting.started.wait(), 3)
            await page.evaluate("() => {window.__choices=[];window.confirm=m=>{window.__choices.push(m);return false;};}")
            await page.evaluate("name=>openEditor(name)", "audit-c.duck")
            waiting.gate.set()
            await pending
            self.check(await page.evaluate("window.__choices.length") == 1, "Cancelling third selection did not ask about original draft")
            self.check(await page.locator("#editorName").input_value() == A and await page.locator("#editorBody").input_value() == draft,
                       "Older pending load reactivated after a cancelled selection restored the original draft")
            await page.evaluate("saveScript()")
            self.check(fixture.saves == [dict(name=A, content=wire(draft), storage="spiffs")], "Cancelled selection caused pending B to steal A's draft")
        finally:
            await self.close(context, page, fixture)

    async def namespace_aliases(self):
        context, page, fixture = await self.page()
        try:
            for requested, canonical, volume in [("SD/folder.duck", "SD/folder.duck", "spiffs"),
                                                  ("SD:folder/item.duck", "sd:folder/item.duck", "sd"),
                                                  ("/sd/folder/item.duck", "sd:folder/item.duck", "sd")]:
                fixture.plans[canonical] = Plan(body=TEXT_A)
                await page.evaluate("name=>openEditor(name)", requested)
                self.check(await page.locator("#editorName").input_value() == canonical and await page.locator("#editorStorage").input_value() == volume,
                           "UI canonicalization changed storage namespace for " + requested)
                await page.evaluate("saveScript()")
                self.check(fixture.saves[-1] == dict(name=canonical, content=wire(TEXT_A), storage=volume), "Alias Save target does not match supported namespace")
            self.check(len(fixture.saves) == 3, "Canonical alias Save duplicated or omitted")
        finally:
            await self.close(context, page, fixture)

    async def unconfirmed_save_no_run(self, status=200, mime="text/plain", body=None, abort=False, timeout=False):
        context, page, fixture = await self.page()
        try:
            await page.evaluate("name=>openEditor(name)", A)
            fixture.save_status, fixture.save_mime, fixture.save_body, fixture.save_abort = status, mime, body, abort
            if timeout:
                fixture.save_gate.clear()
            await asyncio.wait_for(page.evaluate("runEditorScript()"), 6)
            self.check(fixture.saves == [dict(name=A, content=wire(TEXT_A), storage="spiffs")], "Unconfirmed Save was retried or changed source/target")
            self.check(not fixture.runs, "Unconfirmed Save was followed by Run")
            self.check(await page.locator("#editorBody").input_value() == TEXT_A, "Save error became editable source")
        finally:
            await self.close(context, page, fixture)

    async def crlf_clean_switch(self):
        context, page, fixture = await self.page()
        try:
            fixture.plans[A] = Plan(body=TEXT_A.replace("\n", "\r\n"))
            await page.evaluate("name=>openEditor(name)", A)
            self.check(await page.locator("#editorBody").input_value() == TEXT_A, "Textarea did not retain equivalent normalized source")
            await page.evaluate("() => {window.__choices=[];window.confirm=m=>{window.__choices.push(m);return true;};}")
            await page.evaluate("name=>openEditor(name)", C)
            self.check(await page.evaluate("window.__choices.length") == 0, "Clean CRLF load was misclassified as unsaved edits")
            self.check(await page.locator("#editorName").input_value() == C and await page.locator("#editorBody").input_value() == TEXT_B,
                       "Clean CRLF selection did not switch normally")
            self.check(not fixture.saves and not fixture.runs, "Normal selection switch caused action")
        finally:
            await self.close(context, page, fixture)

    async def unsupported_mixed_prefix(self):
        context, page, fixture = await self.page()
        try:
            for name in ["Sd:unknown.duck", "sD:unknown.duck"]:
                before = len([x for x in fixture.calls if x["path"] in ["/script/load", "/script"]])
                await page.evaluate("name=>openEditor(name)", name)
                self.check(len([x for x in fixture.calls if x["path"] in ["/script/load", "/script"]]) == before,
                           "Unsupported mixed-case prefix was silently reinterpreted")
                await self.direct_actions_blocked(page, fixture)
            self.check(not fixture.saves and not fixture.runs, "Invalid namespace produced action")
        finally:
            await self.close(context, page, fixture)

    async def delete_auth(self):
        context, page, fixture = await self.page()
        try:
            await page.evaluate("window.confirm = () => false")
            await page.evaluate("name => delScript(name)", A)
            self.check(not fixture.deletes, "Cancelled deletion sent a request")
            await page.evaluate("window.confirm = () => true")
            await page.evaluate("name => delScript(name)", A)
            self.check(fixture.deletes == [dict(s=A)], "Explicit mock deletion identity wrong")
            self.check(all(row["authenticated"] for row in fixture.calls if row["path"] == "/delete"), "Deletion lost authentication")
        finally:
            await self.close(context, page, fixture)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.output_dir.exists() and not args.output_dir.resolve().is_relative_to(ROOT)
    args.output_dir.mkdir(parents=True)
    data = args.source.read_bytes()
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path="/usr/bin/chromium", headless=True,
                                                   args=["--no-sandbox", "--disable-dev-shm-usage"])
        suite = Suite(browser, B.raw_literals(data.decode()), args.output_dir)
        await suite.group("no-selection-direct-handler-guards", suite.blank_guard)
        for status in [401, 404, 409, 500, 503]:
            await suite.group("load-http-"+str(status), lambda status=status: suite.failed_load(status))
        await suite.group("load-network-failure", lambda: suite.failed_load(abort=True))
        await suite.group("load-malformed-response-mime", lambda: suite.failed_load(status=200, mime="application/json", body='{"error":"not source"}'))
        await suite.group("load-empty-response", lambda: suite.failed_load(status=200, body=""))
        await suite.group("failed-load-deliberate-retry-success", suite.retry)
        await suite.group("ordinary-edit-save-editor-run", suite.ordinary)
        await suite.group("loaded-name-change-cannot-cross-file-save", suite.identity_change)
        await suite.group("loaded-destination-change-cannot-cross-volume-save", lambda: suite.identity_change(True))
        await suite.group("intentional-new-creation", suite.new_script)
        await suite.group("failed-selection-then-explicit-new", suite.failed_then_new)
        await suite.group("stale-out-of-order-responses", suite.out_of_order)
        await suite.group("explicit-new-supersedes-pending-load", suite.new_while_loading)
        await suite.group("dirty-switch-cancel-preserves-original-draft", suite.dirty_switch_cancel)
        await suite.group("dirty-failed-switch-explicit-original-restore", suite.dirty_failed_switch_restore)
        await suite.group("dirty-new-explicit-decision", suite.dirty_new_decision)
        await suite.group("load-deadline-and-late-response", suite.timeout)
        await suite.group("double-selection-no-automatic-action", suite.double_click)
        await suite.group("rapid-three-selections-stale-success-error", suite.rapid_three)
        await suite.group("pending-save-no-duplicate-or-selection-switch", suite.pending_save_controls)
        await suite.group("pending-run-direct-dom-tamper-guard", suite.pending_run_tamper)
        await suite.group("legitimate-error-like-comment-is-source", suite.legitimate_error_comment)
        await suite.group("load-malformed-nul-source", lambda: suite.failed_load(status=200, body="REM Bad\x00response\n"))
        await suite.group("load-unexpected-204-status", lambda: suite.failed_load(status=204, body=""))
        await suite.group("stale-response-without-abortcontroller", lambda: suite.out_of_order(True))
        await suite.group("cancelled-switch-cancels-older-load-and-restores-draft", suite.cancelled_switch_invalidates_pending_load)
        await suite.group("supported-namespace-aliases-and-uppercase-spiffs-folder", suite.namespace_aliases)
        for status in [401, 409, 500]:
            await suite.group("save-http-"+str(status)+"-blocks-run", lambda status=status: suite.unconfirmed_save_no_run(status=status))
        await suite.group("invalid-save-acknowledgement-blocks-run", lambda: suite.unconfirmed_save_no_run(body="Synthetic acknowledgement for another file"))
        await suite.group("invalid-save-response-mime-blocks-run", lambda: suite.unconfirmed_save_no_run(mime="application/json", body='{"saved":true}'))
        await suite.group("save-network-error-blocks-run", lambda: suite.unconfirmed_save_no_run(abort=True))
        await suite.group("save-deadline-blocks-run-no-automatic-retry", lambda: suite.unconfirmed_save_no_run(timeout=True))
        await suite.group("clean-crlf-load-switch-does-not-invent-unsaved-edits", suite.crlf_clean_switch)
        await suite.group("unsupported-mixedcase-prefix-no-silent-reinterpretation", suite.unsupported_mixed_prefix)
        await suite.group("existing-authenticated-deletion-confirmation", suite.delete_auth)
        version = browser.version
        await browser.close()
    assert args.source.read_bytes() == data
    result = dict(counts={state: sum(row["status"] == state for row in suite.results) for state in ["PASS", "FAIL"]},
                  assertions=suite.assertions, results=suite.results, source=str(args.source),
                  source_sha256=hashlib.sha256(data).hexdigest(), parent_browser_fixture_sha256=PARENT_SHA,
                  browser=dict(engine="Chromium", version=version, platform="Linux", playwright=importlib.metadata.version("playwright")),
                  real_network_requests=False, device_access=False, real_saves_or_deletes=False,
                  real_runs_or_hid=False, owner_sources_read=False,
                  scope="Actual embedded UI with inert HTTP; no native High Sierra/iPhone or hardware acceptance")
    (args.output_dir / "results.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
    return bool(result["counts"]["FAIL"])


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
