// Require a private capability, reject browser origins, and connect only over USB.
import http from 'node:http';
import {timingSafeEqual} from 'node:crypto';

export function createProxy({token, connect}) {
  if (!/^[a-f0-9]{64}$/.test(token)) throw new Error('Invalid local capability.');
  const expected = Buffer.from(`Bearer ${token}`);
  const server = http.createServer(async (request, response) => {
    response.setHeader('X-Balta-Tech-Proxy', '0.4');
    const provided = Buffer.from(request.headers.authorization ?? '');
    if (request.headers.origin !== undefined || provided.length !== expected.length || !timingSafeEqual(provided, expected)) {
      response.writeHead(403, {'Content-Type': 'text/plain', 'Connection': 'close'});
      response.end('Local authorization required.'); request.resume(); return;
    }
    if (!['GET', 'POST', 'DELETE'].includes(request.method) || !request.url.startsWith('/') || request.url.startsWith('//')) {
      response.writeHead(400); response.end(); request.resume(); return;
    }
    let upstream, agent, socket;
    const fail = () => {
      upstream?.destroy(); socket?.destroy(); agent?.destroy();
      if (!response.headersSent) response.writeHead(502);
      response.end();
    };
    try {
      socket = await connect();
      if (request.destroyed) { socket.destroy(); return; }
      agent = new http.Agent({keepAlive: false});
      agent.createConnection = () => socket;
      const headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Connection': 'close'};
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
      response.on('close', () => { upstream.destroy(); socket.destroy(); agent.destroy(); });
      request.pipe(upstream);
    } catch { fail(); }
  });
  server.maxConnections = 32;
  server.headersTimeout = 5000;
  server.requestTimeout = 30000;
  return server;
}
