import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import net from 'node:net';
import {createProxy} from '../proxy.mjs';

const token = 'a'.repeat(64);
async function listen(server) {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  return server.address().port;
}
function request(port, headers = {}, method = 'GET', body = '') {
  return new Promise((resolve, reject) => {
    const req = http.request({host: '127.0.0.1', port, path: '/status', method, headers}, res => {
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => resolve({status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks).toString()}));
    });
    req.on('error', reject); req.end(body);
  });
}
async function close(server) {
  server.closeAllConnections();
  await new Promise(resolve => server.close(resolve));
}

test('rejects missing/wrong credentials and browser origins before opening USB', async () => {
  let connections = 0;
  const proxy = createProxy({token, connect: async () => { connections++; throw Error('must not connect'); }});
  const port = await listen(proxy);
  try {
    for (const headers of [{}, {Authorization: 'Bearer wrong'}, {Authorization: `Bearer ${token}`, Origin: 'https://example.org'}, {Authorization: `Bearer ${token}`, Origin: 'null'}]) {
      assert.equal((await request(port, headers)).status, 403);
    }
    assert.equal(connections, 0);
  } finally { await close(proxy); }
});

test('authorised requests retain method/body and strip credentials and CORS', async () => {
  let seen;
  const device = http.createServer((req, res) => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      seen = {method: req.method, body, headers: req.headers};
      res.writeHead(200, {'Access-Control-Allow-Origin': '*'});
      res.end(JSON.stringify({value: {ready: true}}));
    });
  });
  const devicePort = await listen(device);
  const proxy = createProxy({token, connect: async () => {
    const socket = net.connect(devicePort, '127.0.0.1');
    await new Promise((resolve, reject) => { socket.once('connect', resolve); socket.once('error', reject); });
    return socket;
  }});
  const port = await listen(proxy);
  try {
    const result = await request(port, {Authorization: `Bearer ${token}`}, 'POST', '{"text":"private example"}');
    assert.equal(result.status, 200);
    assert.deepEqual(JSON.parse(result.body), {value: {ready: true}});
    assert.equal(result.headers['x-balta-tech-proxy'], '0.4');
    assert.equal(result.headers['access-control-allow-origin'], undefined);
    assert.equal(seen.headers.authorization, undefined);
    assert.equal(seen.method, 'POST');
    assert.equal(seen.body, '{"text":"private example"}');
  } finally { await close(proxy); await close(device); }
});

test('reports USB failure without leaking device/error details', async () => {
  const proxy = createProxy({token, connect: async () => { throw Error('private device identifier'); }});
  const port = await listen(proxy);
  try {
    const result = await request(port, {Authorization: `Bearer ${token}`});
    assert.equal(result.status, 502);
    assert.equal(result.body, '');
  } finally { await close(proxy); }
});

test('the Python transport completes authenticated reads and writes through the proxy', async () => {
  const {execFile} = await import('node:child_process');
  const {fileURLToPath} = await import('node:url');
  const device = http.createServer((req, res) => {
    req.resume();
    req.on('end', () => { res.writeHead(200); res.end(JSON.stringify({value: {ready: true, method: req.method}})); });
  });
  const devicePort = await listen(device);
  const proxy = createProxy({token, connect: async () => {
    const socket = net.connect(devicePort, '127.0.0.1');
    await new Promise((resolve, reject) => { socket.once('connect', resolve); socket.once('error', reject); });
    return socket;
  }});
  const port = await listen(proxy);
  const code = "import os,json; from wda_client import WDAClient; c=WDAClient('http://127.0.0.1:'+os.environ['TEST_PORT'],token=os.environ['TEST_TOKEN']); print(json.dumps([c.request('GET','/status'),c.request('POST','/example',{'text':'sample'})])); c.close()";
  try {
    const output = await new Promise((resolve, reject) => execFile('python3', ['-c', code], {
      timeout: 10000,
      env: {PATH: process.env.PATH, PYTHONPATH: fileURLToPath(new URL('../../server', import.meta.url)), TEST_PORT: String(port), TEST_TOKEN: token},
    }, (error, stdout) => error ? reject(error) : resolve(stdout)));
    assert.deepEqual(JSON.parse(output).map(item => item.value.method), ['GET', 'POST']);
  } finally { await close(proxy); await close(device); }
});


test('reuses one USB connection for authenticated reads and writes', async () => {
  let opened=0;
  const seen=[];
  const device=http.createServer((req,res) => {
    req.resume();req.on('end',()=>{seen.push(req.method);res.end('{"value":true}');});
  });
  const devicePort=await listen(device);
  const proxy=createProxy({token,connect:async()=>{
    opened++;
    const socket=net.connect(devicePort,'127.0.0.1');
    await new Promise((resolve,reject)=>{socket.once('connect',resolve);socket.once('error',reject);});
    return socket;
  }});
  const port=await listen(proxy);
  try {
    for(const method of ['GET','POST','GET']) assert.equal((await request(port,{Authorization:`Bearer ${token}`},method)).status,200);
    assert.equal(opened,1);
    assert.deepEqual(seen,['GET','POST','GET']);
    assert.equal((await request(port)).status,403);
    assert.equal(opened,1);
  } finally {await close(proxy);await close(device);}
});

test('an interrupted mutation is not replayed and the next request can reconnect',async()=>{
  let writes=0,opened=0;
  const device=http.createServer((req,res)=>{
    req.resume();req.on('end',()=>{
      if(req.method==='POST'){writes++;req.socket.destroy();}
      else res.end('{"value":true}');
    });
  });
  const devicePort=await listen(device);
  const proxy=createProxy({token,connect:async()=>{
    opened++;const socket=net.connect(devicePort,'127.0.0.1');
    await new Promise((resolve,reject)=>{socket.once('connect',resolve);socket.once('error',reject);});return socket;
  }});
  const port=await listen(proxy);
  try {
    assert.equal((await request(port,{Authorization:`Bearer ${token}`},'POST','{}')).status,502);
    assert.equal(writes,1);
    assert.equal((await request(port,{Authorization:`Bearer ${token}`})).status,200);
    assert.equal(opened,2);
    assert.equal(writes,1);
  } finally {await close(proxy);await close(device);}
});
