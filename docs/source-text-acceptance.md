# Source/text portability acceptance — review only

Candidate: **ROUTEB-SOURCE-TEXT-PORTABILITY-v1**. No installation or physical testing is authorized by this sheet. Keep owner-accepted `ROUTEB-PAYLOAD-RESTART-v1` and exact rollback. Use High Sierra10.13.6, Python3.8, blank TextEdit, Caps off, recorded input source/build/request and explicit Route B selection; keep STOP accessible and autorun disabled. One explicit Start per trial, no automatic replay. No LED helper or protocol change is needed.

## 1. Byte-verified leading BOM through the supported file path

Editor paste can remove the marker and **cannot prove this trial**. After separate owner authorization for fixture storage and testing, confirm the candidate build ID on the dashboard, connect the Mac to the known EvilDuck dashboard network, ensure execution is idle, and use this Python3.8 snippet in Terminal. It creates a new Desktop evidence folder, writes only a generated harmless fixture, prompts privately for the dashboard password, refuses an existing remote filename, saves via authenticated `POST /script`, and downloads via authenticated `GET /script?s=...`. It never invokes `/run`, sends HID or starts a script.

The existing API has no atomic create-if-absent operation: keep other editors/clients idle, use the generated unique filename and stop on ambiguity rather than retrying a write. The preflight refuses a name already visible before save.

The reviewed source uses **X-Duck-Password**, not HTTP Basic authentication. Do not put the password in an argument, URL, shell variable, screenshot or log. The existing dashboard is plain HTTP; use the known local AP, not an untrusted network. The snippet refuses redirects and performs no retries. Authentication contention/HTTP409 must stop the attempt rather than silently replay it.

```bash
python3 - <<'PY'
import datetime, getpass, hashlib, pathlib, tempfile
import urllib.error, urllib.parse, urllib.request

base = 'http://192.168.4.1'
folder = pathlib.Path(tempfile.mkdtemp(prefix='source-text-bom-',
                                      dir=str(pathlib.Path.home() / 'Desktop')))
name = folder.name + '.txt'
payload = b'\xef\xbb\xbfDELAY 5000\nSTRINGLN 111bom\n'
fixture = folder / name
fixture.write_bytes(payload)
assert fixture.read_bytes() == payload and payload[:3] == bytes([239, 187, 191])

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(NoRedirect)
password = getpass.getpass('Dashboard password (not saved): ')
if not password:
    raise SystemExit('Missing password; no request sent')
headers = {'X-Duck-Password': password}
url = base + '/script?' + urllib.parse.urlencode({'s': name})
try:
    try:
        with opener.open(urllib.request.Request(url, headers=headers), timeout=10):
            raise SystemExit('Remote filename already exists; nothing overwritten')
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise SystemExit('Preflight HTTP %d; stop, no retry' % error.code)
    data = urllib.parse.urlencode({'name': name, 'content': payload}).encode('ascii')
    post_headers = dict(headers, **{'Content-Type': 'application/x-www-form-urlencoded'})
    with opener.open(urllib.request.Request(base + '/script', data=data,
                                           headers=post_headers), timeout=10) as response:
        if response.status != 200:
            raise SystemExit('Save did not return HTTP200; stop')
    with opener.open(urllib.request.Request(url, headers=headers), timeout=10) as response:
        received = response.read()
except urllib.error.HTTPError as error:
    raise SystemExit('HTTP %d; stop, no retry' % error.code)
except urllib.error.URLError:
    raise SystemExit('Network/tooling error; stop, no retry')
finally:
    password = ''
    headers.clear()

(folder / 'readback.bin').write_bytes(received)
if received != payload or received[:3] != bytes([239, 187, 191]):
    raise SystemExit('Byte mismatch; preserve evidence and DO NOT RUN')
print('EXACT_BYTE_READBACK_PASS')
print('UTC:', datetime.datetime.now(datetime.timezone.utc).isoformat())
print('Filename:', name)
print('Bytes:', len(received), 'Prefix:', received[:3].hex())
print('SHA-256:', hashlib.sha256(received).hexdigest())
print('Evidence folder:', folder)
print('Manual CLI command after separate approval: routeb ' + name)
PY
```

Preserve the output and generated local/readback files. This is HTTP/source-byte evidence, not a firmware application readback. Credentials stay out of those files; assigning an empty variable is not a secure-memory-erasure claim.

Only after `EXACT_BYTE_READBACK_PASS`, use the existing local USB CDC CLI to enter the printed **`routeb <filename>`** command once. This is the verified explicit engine path; do not assume the ordinary web Run button selects it. Switch focus to blank TextEdit during the existing five-second DELAY. Expect exactly `111bom` and a newline, then Completed for that request. Preserve the screenshot and request/status. Do not edit or resave the device script between readback and Start. This full path is HTTP save/readback → storage FileSource → explicit Route B compiler/runtime; it tests the adapter, not just a component compiler.

## 2. Inline aliases and unchanged block behavior

```ducky
STRING_PYTHON 111join
STRINGLN_HTML 222line
STRINGLN_BASH
333block
END_STRINGLN
REPEAT 2 STRINGLN_RUBY 444repeat
```

Expect four lines: `111join222line`, `333block`, `444repeat`, `444repeat`; associate with Completed. No Python/HTML/Bash/Ruby is executed. Do not append END_STRING/END_STRINGLN to inline operands: those tokens would be literal text under this extension. All fourteen aliases and boundary cases remain automated rather than requiring fourteen physical trials.

## 3. STOP/restart recovery and malformed rejection

```ducky
STRING_PYTHON a
HOLD SHIFT
DELAY 3000
RESTART_PAYLOAD
```

Observe two lowercase `a` characters, then STOP during the second delay. Require Cancelled and normal harmless manual lowercase afterward. This is scoped evidence, not a general host key-release guarantee. For a separate negative Start, use the retained malformed block `STRINGLN_PYTHON`, `111BAD`, `END_STRING` on three lines. Require compile rejection with blank TextEdit and record actual line/code/request.

Leave missing receipt/boot/session identifiers unknown. Missing evidence is UNVERIFIED; a demonstrated host/tool limitation is PLATFORM-LIMITED, not universal failure. Preserve partial evidence without automatic retries, timing changes or firmware changes. No Windows prerequisite or broad Caps campaign is needed.
