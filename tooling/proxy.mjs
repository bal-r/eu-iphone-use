// Require a private capability, reject browser origins, and connect only over USB.
import http from 'node:http';
import {timingSafeEqual} from 'node:crypto';

export function createProxy({token, connect}) {
  if (!/^[a-f0-9]{64}$/.test(token)) throw new Error('Invalid local capability.');
  const expected = Buffer.from(`Bearer ${token}`);
  // One serial USB HTTP connection per proxy. Node drops closed sockets from
  // the pool; failed requests are reported once and are never replayed here.
  const agent = new http.Agent({keepAlive: true, maxSockets: 1, maxFreeSockets: 1, timeout: 5000});
  agent.createConnection = (_options, callback) => {
    Promise.resolve().then(connect).then(socket => {
      socket.setNoDelay?.(true);
      callback(null, socket);
    }, () => callback(new Error('USB unavailable')));
  };
  const server = http.createServer(async (request, response) => {
    response.setHeader('X-Balta-Tech-Proxy', '0.4');
    const provided = Buffer.from(request.headers.authorization ?? '');
    if (request.headers.origin !== undefined || provided.length !== expected.length || !timingSafeEqual(provided, expected)) {
      response.writeHead(403, {'Content-Type': 'text/plain', 'Connection': 'keep-alive'});
      response.end('Local authorization required.'); request.resume(); return;
    }
    if (!['GET', 'POST', 'DELETE'].includes(request.method) || !request.url.startsWith('/') || request.url.startsWith('//')) {
      response.writeHead(400); response.end(); request.resume(); return;
    }
    let upstream;
    let finished = false;
    const fail = () => {
      if (finished) return;
      finished = true;
      upstream?.destroy();
      if (!response.headersSent) response.writeHead(502);
      response.end();
    };
    try {
      const headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Connection': 'keep-alive'};
      if (request.headers['content-length']) headers['Content-Length'] = request.headers['content-length'];
      upstream = http.request({host: '127.0.0.1', path: request.url, method: request.method, headers, agent}, incoming => {
        response.writeHead(incoming.statusCode ?? 502, {'Content-Type': 'application/json', 'Cache-Control': 'no-store'});
        let received = 0;
        incoming.on('data', chunk => { received += chunk.length; if (received > 25 * 1024 * 1024) fail(); });
        incoming.on('error', fail); incoming.pipe(response);
      });
      upstream.on('socket', assigned => assigned.resume());
      upstream.on('error', fail); upstream.setTimeout(20000, fail);
      request.on('error', fail);
      let sent = 0;
      request.on('data', chunk => { sent += chunk.length; if (sent > 1024 * 1024) fail(); });
      response.on('close', () => { if (!response.writableFinished) upstream.destroy(); });
      request.pipe(upstream);
    } catch { fail(); }
  });
  server.on('close', () => agent.destroy());
  server.maxConnections = 32;
  server.headersTimeout = 5000;
  server.requestTimeout = 30000;
  return server;
}
