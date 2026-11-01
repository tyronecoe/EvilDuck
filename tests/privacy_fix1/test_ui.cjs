// Execute actual composed SETTINGS_JS only: mocked DOM/HTTP, no browser/network/HID.
'use strict';
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

if (process.argv.length !== 3) throw new Error('Usage: node test_ui.cjs <composed-webfiles.h>');
const source = fs.readFileSync(process.argv[2], 'utf8');
function embedded(name) {
  const marker = `static const char ${name}[] PROGMEM = R"rawliteral(`;
  assert.strictEqual(source.split(marker).length, 2, `unique ${name}`);
  const tail = source.split(marker)[1];
  assert.ok(tail.includes(')rawliteral";'), `complete ${name}`);
  return tail.split(')rawliteral";')[0];
}
const script = embedded('SETTINGS_JS');
const html = embedded('SETTINGS_HTML');
let assertions = 0;
const results = [];
function check(value, message) { ++assertions; assert.ok(value, message); }
function equal(actual, expected, message) { ++assertions; assert.strictEqual(actual, expected, message); }
const auth = 'synthetic-auth-only';
const savedAP = 'synthetic-old-ap-secret';
const savedWeb = 'synthetic-old-web-secret';
const newAP = 'synthetic-new-ap-secret';
const newWeb = 'synthetic-new-web-secret';
const config = {
  ssid: 'Synthetic AP', password_configured: true, web_password_configured: true,
  // Old/stale responses must not repopulate either replacement field.
  password: savedAP, web_password: savedWeb,
  channel: 6, stealth: true, hidden_ap: false, disable_led: false,
  led_color: '#112233', autorun_delay_min: 1, autorun_delay_max: 3,
};

async function environment(settings = config) {
  const ids = ['log', 'ssid', 'password', 'channel', 'stealth', 'hidden_ap',
    'disable_led', 'led_color', 'web_password', 'autorun_delay_min', 'autorun_delay_max'];
  const elements = Object.fromEntries(ids.map(id => [id, {
    value: '', checked: false, placeholder: '', textContent: '', scrollTop: 0,
    scrollHeight: 0, listeners: [], addEventListener(name, callback) { this.listeners.push([name, callback]); },
  }]));
  const calls = [], timers = [], storageWrites = [], blockedDeviceCalls = [];
  const storage = new Map([['duckPw', auth]]);
  const replies = [];
  class FormDataMock {
    constructor() { this.rows = []; }
    append(name, value) { this.rows.push([String(name), String(value)]); }
  }
  const forbidden = name => () => { blockedDeviceCalls.push(name); throw new Error('Device access forbidden'); };
  const context = {
    document: { getElementById(id) { if (!(id in elements)) throw new Error('Unexpected DOM element'); return elements[id]; } },
    FormData: FormDataMock,
    sessionStorage: {
      getItem: key => storage.get(key) || null,
      setItem: (key, value) => { storageWrites.push([key, value]); storage.set(key, value); },
    },
    fetch: async (url, options) => {
      calls.push({url, options});
      if (calls.length === 1) {
        equal(url, '/settings', 'automatic load accesses settings only');
        return {ok: true, status: 200, json: async () => settings};
      }
      if (!replies.length) throw new Error('Unexpected extra HTTP request');
      const next = replies.shift();
      if (next.error) throw next.error;
      return {ok: next.status >= 200 && next.status < 300, status: next.status, text: async () => next.text};
    },
    setTimeout: (callback, delay) => { timers.push({callback, delay}); return timers.length; },
    clearTimeout: () => {},
    navigator: {hid: {requestDevice: forbidden('hid')}, usb: {requestDevice: forbidden('usb')}},
    Keyboard: {press: forbidden('keyboard')},
  };
  vm.createContext(context);
  vm.runInContext(script, context, {filename: 'actual-SETTINGS_JS'});
  // Let the actual bottom-of-script loadSettings() settle before assertions.
  await new Promise(resolve => setImmediate(resolve));
  equal(calls.length, 1, 'one initial read and no automatic write');
  return {
    elements, calls, timers, storageWrites, blockedDeviceCalls,
    run: code => vm.runInContext(code, context),
    reply: (status = 200, text = 'OK') => replies.push({status, text}),
    reject: () => replies.push({error: new Error('synthetic-offline')}),
    body: () => Object.fromEntries(calls.at(-1).options.body.rows),
  };
}

function noSecretsLogged(e, extra = []) {
  for (const value of [savedAP, savedWeb, newAP, newWeb, auth, ...extra]) {
    check(!e.elements.log.textContent.includes(value), 'no credential appears in settings log');
  }
}
function saveRequest(e) {
  const last = e.calls.at(-1);
  equal(last.url, '/settings', 'save accesses settings only');
  equal(last.options.method, 'POST', 'save uses POST');
  equal(last.options.headers['X-Duck-Password'], auth, 'save preserves existing authentication');
  equal(e.timers.length, 0, 'no scheduled retry or unsolicited action');
  equal(e.blockedDeviceCalls.length, 0, 'no keyboard/HID/USB access');
}
async function group(name, fn) {
  const before = assertions;
  try { await fn(); results.push({name, status: 'PASS', assertions: assertions - before}); }
  catch (error) { results.push({name, status: 'FAIL', assertions: assertions - before, message: error.message}); throw error; }
}

(async () => {
  await group('stale-secret-fields-not-preloaded', async () => {
    const e = await environment();
    equal(e.elements.password.value, '', 'AP replacement remains blank');
    equal(e.elements.web_password.value, '', 'web replacement remains blank');
    check(e.elements.password.placeholder.includes('leave blank'), 'AP configured guidance');
    check(e.elements.web_password.placeholder.includes('leave blank'), 'web configured guidance');
    equal(e.calls[0].options.headers['X-Duck-Password'], auth, 'load authenticates');
    equal(e.storageWrites.length, 0, 'load does not overwrite authentication');
    noSecretsLogged(e);
  });
  await group('unconfigured-placeholders', async () => {
    const e = await environment({...config, password_configured: false, web_password_configured: false});
    check(e.elements.password.placeholder.startsWith('Enter a new'), 'AP unconfigured guidance');
    check(e.elements.web_password.placeholder.startsWith('Enter a new'), 'web unconfigured guidance');
    equal(e.elements.password.value, '', 'unconfigured AP remains blank');
    equal(e.elements.web_password.value, '', 'unconfigured web remains blank');
  });
  await group('unrelated-save-omits-secrets', async () => {
    const e = await environment();
    e.elements.channel.value = '11';
    e.reply(); await e.run('saveSettings()');
    const body = e.body();
    check(!Object.hasOwn(body, 'password') && !Object.hasOwn(body, 'web_password'), 'both replacements omitted');
    equal(body.channel, '11', 'unrelated setting is saved');
    equal(body.ssid, config.ssid, 'SSID preserved');
    equal(body.stealth, '1', 'boolean setting preserved');
    equal(e.calls.length, 2, 'exactly one explicit save');
    saveRequest(e); noSecretsLogged(e);
  });
  for (const [name, ap, web] of [
    ['ap-only-replacement', newAP, ''], ['web-only-replacement', '', newWeb],
    ['both-replacements', newAP, newWeb], ['empty-replacements-preserve', '', ''],
  ]) {
    await group(name, async () => {
      const e = await environment();
      e.elements.password.value = ap; e.elements.web_password.value = web;
      e.reply(); await e.run('saveSettings()');
      const body = e.body();
      equal(Object.hasOwn(body, 'password'), Boolean(ap.length), 'AP replacement presence');
      equal(Object.hasOwn(body, 'web_password'), Boolean(web.length), 'web replacement presence');
      if (ap) equal(body.password, ap, 'AP exact replacement');
      if (web) equal(body.web_password, web, 'web exact replacement');
      equal(e.elements.password.value, '', 'successful save clears AP replacement');
      equal(e.elements.web_password.value, '', 'successful save clears web replacement');
      equal(e.calls.length, 2, 'single explicit save');
      saveRequest(e); noSecretsLogged(e);
    });
  }
  await group('replacement-whitespace-preserved', async () => {
    const e = await environment();
    const ap = '  synthetic-ap-with-spaces  ', web = '  synthetic-web-with-spaces  ';
    e.elements.password.value = ap; e.elements.web_password.value = web;
    e.reply(); await e.run('saveSettings()');
    equal(e.body().password, ap, 'AP replacement is not trimmed');
    equal(e.body().web_password, web, 'web replacement is not trimmed');
    noSecretsLogged(e, [ap, web]);
  });
  await group('failed-save-retains-input-and-reports-error', async () => {
    for (const status of [400, 401, 409, 503]) {
      const e = await environment();
      e.elements.password.value = newAP; e.elements.web_password.value = newWeb;
      const message = `Synthetic request refused (${status})`;
      e.reply(status, message); await e.run('saveSettings()');
      equal(e.elements.password.value, newAP, 'failed save retains AP replacement');
      equal(e.elements.web_password.value, newWeb, 'failed save retains web replacement');
      check(e.elements.log.textContent.includes(message), 'failure is displayed');
      check(!e.elements.log.textContent.includes('OK'), 'failure never displayed as success');
      equal(e.calls.length, 2, 'no automatic retry after refusal');
      saveRequest(e); noSecretsLogged(e);
    }
  });
  await group('network-failure-has-no-retry-or-false-success', async () => {
    const e = await environment();
    e.elements.password.value = newAP; e.elements.web_password.value = newWeb;
    e.reject();
    let rejected = false;
    try { await e.run('saveSettings()'); } catch (error) { rejected = error.message === 'synthetic-offline'; }
    check(rejected, 'transport rejection remains an explicit failure');
    equal(e.elements.password.value, newAP, 'network error retains AP replacement');
    equal(e.elements.web_password.value, newWeb, 'network error retains web replacement');
    equal(e.calls.length, 2, 'no network retry');
    equal(e.elements.log.textContent, '', 'no false success');
    saveRequest(e); noSecretsLogged(e);
  });
  await group('following-save-does-not-replay-replacement', async () => {
    const e = await environment();
    e.elements.password.value = newAP;
    e.reply(); await e.run('saveSettings()');
    e.elements.channel.value = '7';
    e.reply(); await e.run('saveSettings()');
    check(!Object.hasOwn(e.body(), 'password') && !Object.hasOwn(e.body(), 'web_password'), 'next save carries no old replacement');
    equal(e.body().channel, '7', 'next unrelated save proceeds');
    equal(e.calls.length, 3, 'two explicit saves only');
    noSecretsLogged(e);
  });
  await group('replacement-ui-labels-and-no-device-activity', async () => {
    check(!html.includes('empty = off'), 'misleading blank-disables label removed');
    check(html.includes('Replace AP password (leave blank to keep existing)'), 'AP replacement label');
    check(html.includes('Replace Web UI password (leave blank to keep existing)'), 'web replacement label');
    const e = await environment();
    equal(e.blockedDeviceCalls.length, 0, 'settings initialization never accesses devices');
    equal(e.timers.length, 0, 'settings initialization schedules no action');
  });
  console.log(JSON.stringify({PASS: results.length, FAIL: 0, assertions, results,
    scope: 'actual composed SETTINGS_JS in Node VM with mocked DOM/FormData/HTTP; no native browser, network or hardware'}));
})().catch(error => {
  console.log(JSON.stringify({PASS: results.filter(row => row.status === 'PASS').length,
    FAIL: results.filter(row => row.status === 'FAIL').length || 1, assertions, results,
    error: error.message, scope: 'actual composed SETTINGS_JS with mocks'}));
  process.exitCode = 1;
});
