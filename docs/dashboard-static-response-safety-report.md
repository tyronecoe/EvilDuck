# Dashboard empty-JavaScript response — source-only repair

**SOURCE-ONLY — NOT TARGET-BUILT — NOT INSTALLED OR HARDWARE-VERIFIED.**

Local branch: `routeb-dashboard-static-response-safety`, from
`e692435a7c70dbc0d917bbff733c57900cf7d57c`. No commit, push, package or target
firmware build was performed. All 2,437 pre-existing tracked files/modes, published
images and recovery artifacts remain unchanged. The maintained fix is an additive
patch/manifest/preparer, applied only to a new scratch composition.

## What the owner evidence establishes

The owner reports macOS High Sierra 10.13.6 and Chrome **116.0.5845.187**, including
a fresh Incognito attempt. The actual browser Network capture shows:

```text
GET http://192.168.4.1/index.js
HTTP 200 OK
Content-Type: application/javascript
Content-Length: 0
```

The Response tab reports no response data. The password field's change handler
raises `ReferenceError: saveDuckPw is not defined`; both status labels remain at
their initial Checking values. This establishes an empty script response during
that browser load. An empty script cannot define the password/status handlers.
It does not establish an incorrect saved password. The favicon's independent 503
is the existing unsupported-path refusal and is not the authentication failure.

A separate owner-operated read-only request returned the full expected script:
**31,932 bytes**, SHA-256
`7fb8068beb12564dc4e5146e8b6b0a9b719b78caf3f4d94cd0f2b8a2c04baf39`.
Thus the resource can be served intact in isolation; that result does not override
the browser's observed empty response. The earlier 31,933-byte ELF resource length
includes its C terminator, which must not be included in the HTTP body.

Chrome 116 supports the JavaScript syntax used here. Earlier cached-page/storage
runtime failure hypotheses can reproduce Checking, but leave top-level function
declarations defined. They do not by themselves explain this ReferenceError.
The initial iPhone symptom remains owner-reported; the detailed Network evidence
is from the Mac. No repeated password, keyboard or Caps campaign is required.

## Source mechanism and confidence boundary

The actual build's dependency is ESP Async WebServer **3.12.1**, with Arduino ESP32
**3.3.0**. Its ESP32 `send_P(..., const char*)` forwards to ordinary `send()`.
Without a template callback, this creates `AsyncBasicResponse`, which assigns the
entire resource to a heap-backed `String`. Arduino `WString` invalidates that
String when its allocation fails. The response can retain code 200 and default
content length zero. This path is bound to the actual candidate's dependency
source/object hashes, rather than an unrelated SDK snapshot.

Controlled tests compiled the actual unchanged `WString` and verbatim selected
SDK response/factory/fill functions. A deterministic allocator quota reproduces
the old empty-200 behavior with simultaneous CSS/JavaScript copies. The new
streaming path preserves both complete resources under the same simulated quota.

**Confirmed:** the owner observed an empty JavaScript response; the old response
code has a reproducible allocation-failure path yielding that symptom.
**Strongly supported inference:** full-resource allocation pressure during a page
load triggered the owner failure. Actual ESP32 heap state was not measured, and
the mock does not prove the physical trigger. Other severe memory or transport
problems are not universally excluded.

## Minimal source change

[The patch](../tests/dashboard_response_safety/application.patch) changes only
eleven constant-resource sends inside composed `webserver.cpp::handleStatic`:

```cpp
// Before: selects the whole-body String copy on this SDK.
req->send_P(200, "application/javascript", INDEX_JS);

// After: selects the SDK's streaming AsyncProgmemResponse.
req->send(200, "application/javascript",
          reinterpret_cast<const uint8_t *>(INDEX_JS), sizeof(INDEX_JS) - 1);
```

The nine static arrays have static lifetime. Explicit byte pointers and bounded
lengths select the existing SDK streaming implementation without a template
processor or terminating NUL. The patch adds no second HTTP implementation and
does not remove the need for smaller response/header/TCP allocations.

Exactly **one of 201 composed source files changes; 200 are unchanged**. All
resource bytes, MIME types, statuses and twelve portable URI aliases are preserved.
The eleventh substitution is the same error-page transport in the inactive
legacy fallback; no legacy platform acceptance is claimed.

No authentication, password storage, settings semantics, STOP, keyboard runtime,
H1 opt-in, lease, LED/EDR1, USB identity, partitions or storage safeguards change.
The favicon/unknown-path 503 behavior is intentionally preserved. This repair does
not include cache versioning, extra JavaScript startup fallbacks or unrelated UI
features.

## Fresh software checks

| Suite | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| Native actual-handler/SDK response tests | 33 | 0 | 976 |
| Browser using SDK-reconstructed bodies | 3 | 0 | 26 |
| Composition and fail-closed source/SDK controls | 7 | 0 | 32 |
| **Total** | **43** | **0** | **1,034** |

ASan, UBSan and leak detection are clean for the native run; stderr is empty.
Native checks cover every alias and all nine literal bodies, explicit overload
selection, exact lengths/MIME/status/body bytes, overlapping CSS/JS responses,
zero-capacity reads/backpressure, chunk boundaries, EOF, independent cursors and
cancellation, simulated allocation quotas and unknown-path refusal. The old
empty-response control remains a passing expected-failure reproduction.

The browser fixture consumes byte-identical files reconstructed by actual SDK
`_fillBuffer`; its receipt is bound to the native receipt/hash. All requests are
intercepted and inert. It reproduces the empty-script symptom, then verifies
handler availability, manual synthetic credential change, authenticated status,
initial editor Save/Run refusal and blank settings replacement fields. It sends
no actual settings/script/STOP mutations. This is Linux Chromium 151 fixture
evidence, not native Chrome 116 or iPhone acceptance.

Scope controls reject wrong source, double application, symlinks, changed/missing
SDK files, edited manifests and output overwrite. The preparer checks full
inventories and zero-fuzz/no-offset application. Source outside `handleStatic`
and the other 200 files remains exact. Existing interpreter/keyboard/privacy test
receipts remain historical; they were not rerun or added to these fresh totals.

Native HTTP base/header/object allocation/transport and allocator limits are
mocked; actual WString, selected forwarding/constructor/fill code and the composed
handler/resources are used. Initial native fixture setup/extraction issues and a
missing default Playwright browser installation are preserved in scratch evidence.
The final browser run uses the existing `/usr/bin/chromium`; no firmware fix was
changed to make those harness setup issues pass.

[Combined results/inventory](dashboard-static-response-safety-results.json) ·
[Native receipt](dashboard-static-response-safety-native.json) ·
[Browser receipt](dashboard-static-response-safety-browser.json) ·
[Scope receipt](dashboard-static-response-safety-scope.json).

## Reproduction and target-build boundary

From the repository, use fresh output paths:

```bash
python3 -B tests/dashboard_response_safety/prepare_sources.py \
  --from-composed /workspace/scratch/editor-build-integration/build-v2-uninstalled/candidate/EvilDuckS3 \
  --output /workspace/scratch/dashboard-response-safety/reproduce/EvilDuckS3

python3 -B tests/dashboard_response_safety/test_native.py \
  --source /workspace/scratch/dashboard-response-safety/reproduce/EvilDuckS3 \
  --output /workspace/scratch/dashboard-response-safety/reproduce-native \
  --results /workspace/scratch/dashboard-response-safety/reproduce-native.json

python3 -B tests/dashboard_response_safety/test_browser.py \
  --source /workspace/scratch/dashboard-response-safety/reproduce/EvilDuckS3 \
  --native-output /workspace/scratch/dashboard-response-safety/reproduce-native \
  --native-results /workspace/scratch/dashboard-response-safety/reproduce-native.json \
  --output /workspace/scratch/dashboard-response-safety/reproduce-browser \
  --results /workspace/scratch/dashboard-response-safety/reproduce-browser.json
```

The maintained [preparer](../tests/dashboard_response_safety/prepare_sources.py)
chains the exact reviewed H1/privacy/dashboard/editor composition. Its manifest
pins six core/library inputs; native verification additionally pins the response
class declaration header. These developer checks run in the existing cloud SDK
environment, not on the owner's Mac.

**Historical normal builders do not automatically select this new overlay.**
Target integration, a distinct build identity, clean approved-profile compilation,
linked response-path/resource verification and a new guarded review package are
still required. No binary size/RAM delta or new installable artifact is claimed.
The installed application has not been changed by this work and still needs a
replacement image before benefiting from the repair.

The exact mandatory source/text-v2 rollback remains **1,413,200 bytes**, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It remains older firmware without Privacy Fix 1 or the later dashboard/editor
repairs. The prior e825 candidate and all published packages are unchanged;
reinstalling that same package does not install this new source repair.

After a future separately approved installation, the smallest owner check is a
fresh full-page load with nonempty `index.js` and the expected body hash, followed
by normal password entry and observed status. Mac and iPhone observations remain
separate. No payload, settings save, owner-file overwrite or old keyboard/lock
acceptance repeat is needed for this transport repair.
