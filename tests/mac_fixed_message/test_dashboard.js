#!/usr/bin/env node
'use strict';
/* Executes three retained embedded dashboard functions in a mock VM. Not a browser test. */
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const crypto = require('crypto');

const PIN = {
  provenance: 'retained caps-stop-build-release/candidate/EvilDuckS3/webfiles.h',
  source_sha256: '2774ff015739423be2959cc22a745816f0b6bc4c38eccd3d3dfc697ebcd3606d',
  functions: {
    duckHeaders: 'db272f482b40fe5826543387dbc191021a5cf9f3503d4fb52a447c302be910cf',
    controlFetch: '382e79d169f638dda83c8bfa2be93e0ffa8de3aab312fc424c3316ca47ae5ee2',
    viewLedData: 'cb43252f92b2e7c944e87ce763d28be0c2fd31c1e17cabe5e2ac9cdd3e2e4443'
  }
};
const MESSAGE = 'EVILDUCK TEST 123';
const digest = value => crypto.createHash('sha256').update(value).digest('hex');
let assertions = 0;
const check = (condition, description) => {
  ++assertions;
  assert.ok(condition, description);
};
function section(source, begin, end) {
  const start = source.indexOf(begin);
  const stop = source.indexOf(end, start);
  check(start >= 0 && stop > start, 'exact embedded function boundaries exist');
  return source.slice(start, stop);
}
function prepare(code, response, password = 'synthetic-test-only') {
  const calls = [], links = [], blobs = [], revoked = [], timers = new Map();
  let timerId = 0;
  const node = {textContent: ''};
  const context = {
    document: {
      getElementById: id => {
        check(id === 'ledTestText', 'only expected fixed-message DOM node accessed');
        return node;
      },
      createElement: tag => {
        check(tag === 'a', 'only download anchor created');
        const link = {clicks: 0, click() { ++this.clicks; }};
        links.push(link);
        return link;
      }
    },
    sessionStorage: {
      getItem: key => {
        check(key === 'duckPw', 'existing session authentication field used');
        return password;
      }
    },
    fetch: async (url, options) => {
      calls.push({url, options});
      if (response instanceof Error) throw response;
      return {
        ok: response.status >= 200 && response.status < 300,
        status: response.status,
        headers: {get: name => {
          check(name === 'Content-Type', 'wrapper reads response MIME field');
          return response.type;
        }},
        text: async () => response.body
      };
    },
    Blob: class {
      constructor(parts, options) {
        this.parts = parts;
        this.type = options.type;
        blobs.push(this);
      }
    },
    URL: {
      createObjectURL: blob => {
        check(blobs.includes(blob), 'download uses generated fixed-message blob');
        return 'blob:synthetic-fixed-message';
      },
      revokeObjectURL: url => revoked.push(url)
    },
    setTimeout: (callback, delay) => {
      const id = ++timerId;
      timers.set(id, {callback, delay});
      return id;
    },
    clearTimeout: id => timers.delete(id),
    JSON, Error, Promise
  };
  vm.createContext(context);
  vm.runInContext(code, context, {timeout: 1000});
  return {context, node, calls, links, blobs, revoked, timers};
}
async function exercise(code, response, download, shouldPass, password) {
  const fixture = prepare(code, response, password);
  await vm.runInContext('viewLedData(' + JSON.stringify(download) + ')', fixture.context,
                        {timeout: 1000});
  check(fixture.calls.length === 1, 'one GET attempt; no retry');
  const call = fixture.calls[0];
  check(call.url === '/led-test/data', 'existing authenticated fixed-data endpoint only');
  check(!call.options.method || call.options.method === 'GET', 'no receiver mutation');
  check(call.options.headers['X-Duck-Password'] === (password === '' ? undefined : 'synthetic-test-only'),
        'existing duckHeaders authentication is forwarded');
  check(!Object.prototype.hasOwnProperty.call(fixture.node, 'innerHTML'), 'response is never interpreted as markup');
  if (shouldPass) {
    check(fixture.node.textContent === MESSAGE, 'exact fixed message displayed');
    check(Buffer.byteLength(fixture.node.textContent, 'utf8') === 17, 'displayed message is exactly seventeen bytes');
    check(fixture.links.length === (download ? 1 : 0), 'download occurs only when explicitly requested');
    if (download) {
      check(fixture.blobs.length === 1, 'one download blob');
      check(fixture.blobs[0].parts.length === 1 && fixture.blobs[0].parts[0] === MESSAGE,
            'download contains exact message only');
      check(fixture.blobs[0].type === 'text/plain', 'download MIME type is text/plain');
      check(fixture.links[0].download === 'evilduck-fixed-test.txt', 'fixed safe download filename');
      check(fixture.links[0].clicks === 1, 'one local download activation');
      check(fixture.timers.size === 1, 'request timer cleared; only object-URL cleanup remains');
      const timer = [...fixture.timers.values()][0];
      check(timer.delay === 1000, 'bounded object-URL cleanup scheduled');
      timer.callback();
      check(fixture.revoked.length === 1 && fixture.revoked[0] === fixture.links[0].href,
            'object URL revoked');
    } else {
      check(fixture.blobs.length === 0 && fixture.timers.size === 0, 'view has no file output or residual timer');
    }
  } else {
    check(fixture.node.textContent.startsWith('No verified data: '), 'failure is visible and is not success');
    check(fixture.node.textContent !== MESSAGE, 'invalid response never produces verified text');
    check(fixture.links.length === 0 && fixture.blobs.length === 0, 'invalid response cannot download');
    check(fixture.timers.size === 0, 'request timer cleaned on failure');
  }
  return fixture;
}

(async () => {
  if (process.argv.length !== 3) throw new Error('Usage: node tests/mac_fixed_message/test_dashboard.js /path/to/retained/candidate/EvilDuckS3/webfiles.h');
  const raw = fs.readFileSync(process.argv[2]);
  check(digest(raw) === PIN.source_sha256, 'retained composed dashboard source identity');
  const source = raw.toString('utf8');
  const functions = {
    duckHeaders: section(source, 'function duckHeaders(){', '\n\nlet statusPollInFlight='),
    controlFetch: section(source, 'async function controlFetch(url,options){', '\nasync function stopScript(){'),
    viewLedData: section(source, 'async function viewLedData(download){', '\nlet capsTrialPending=')
  };
  for (const [name, value] of Object.entries(functions)) {
    check(digest(value) === PIN.functions[name], name + ' exact source identity');
  }
  const code = Object.values(functions).join('\n');
  const cases = [
    ['valid_view', {status: 200, type: 'text/plain; charset=utf-8', body: MESSAGE}, false, true],
    ['valid_download', {status: 200, type: 'TEXT/PLAIN', body: MESSAGE}, true, true],
    ['wrong_json_type', {status: 200, type: 'application/json', body: MESSAGE}, true, false],
    ['wrong_html_type', {status: 200, type: 'text/html', body: MESSAGE}, false, false],
    ['missing_type', {status: 200, type: '', body: MESSAGE}, true, false],
    ['wrong_text', {status: 200, type: 'text/plain', body: 'EVILDUCK TEST 124'}, false, false],
    ['newline', {status: 200, type: 'text/plain', body: MESSAGE + '\n'}, true, false],
    ['crlf', {status: 200, type: 'text/plain', body: MESSAGE + '\r\n'}, true, false],
    ['bom', {status: 200, type: 'text/plain', body: '\ufeff' + MESSAGE}, true, false],
    ['nul', {status: 200, type: 'text/plain', body: MESSAGE + '\0'}, false, false],
    ['busy_even_with_exact_body', {status: 409, type: 'text/plain', body: MESSAGE}, true, false],
    ['auth_failure', {status: 401, type: 'text/plain', body: 'Unauthorized'}, false, false],
    ['html_in_body', {status: 200, type: 'text/plain', body: '<script>alert(1)</script>'}, true, false],
    ['network_error', new Error('Synthetic network refusal'), true, false]
  ];
  for (const [_name, response, download, expected] of cases) {
    await exercise(code, response, download, expected);
  }
  await exercise(code, {status: 401, type: 'text/plain', body: 'Unauthorized'}, false, false, '');
  console.log(JSON.stringify({PASS: cases.length + 1, FAIL: 0, assertions,
    scope: 'Actual retained dashboard functions in Node VM; no browser, iPhone, native Mac, USB or hardware validation',
    source_path: PIN.provenance, source_sha256: PIN.source_sha256, function_sha256: PIN.functions,
    cases: cases.map(row => row[0]).concat('no_saved_password')}, null, 2));
})().catch(error => {
  console.error('Dashboard regression failed: ' + error.message);
  process.exitCode = 1;
});
