import {readFileSync} from 'node:fs';
import iosDevice from 'appium-ios-device';
import {createProxy} from './proxy.mjs';

const [udid, localArgument = '18100', deviceArgument = '8100', tokenFile] = process.argv.slice(2);
if (!/^[A-Za-z0-9-]{8,64}$/.test(udid ?? '') || !tokenFile) throw new Error('A device and private token file are required.');
function port(value) {
  if (!/^\d+$/.test(value)) throw new Error('Ports must be integers.');
  const number = Number(value);
  if (number < 1024 || number > 65535) throw new Error('Ports must be 1024-65535.');
  return number;
}
const localPort = port(localArgument);
const devicePort = port(deviceArgument);
const server = createProxy({token: readFileSync(tokenFile, 'utf8').trim(),
  connect: () => iosDevice.utilities.connectPort(udid, devicePort)});
server.listen(localPort, '127.0.0.1', () => console.log(`Private USB proxy listening at 127.0.0.1:${localPort}`));
server.on('error', () => { console.error('Local USB proxy failed.'); process.exitCode = 1; stop(); });
function stop() {
  server.closeAllConnections();
  server.close(() => process.exit(process.exitCode ?? 0));
  setTimeout(() => process.exit(process.exitCode ?? 0), 1000).unref();
}
process.on('SIGINT', stop);
process.on('SIGTERM', stop);
