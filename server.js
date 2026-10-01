/**
 * ╔══════════════════════════════════════════════════════════════╗
 * ║     MultiVision AI — Smart City Dashboard REST API Server    ║
 * ║     Port: 3008  |  Node.js Built-in HTTP + REST Endpoints   ║
 * ╚══════════════════════════════════════════════════════════════╝
 */

const http = require('http');
const fs   = require('fs');
const path = require('path');
const url  = require('url');
const os   = require('os');

const PORT = 3008;
const HOST = '0.0.0.0';
const ROOT = __dirname;

// In-Memory Live State
let systemIncidents = [
  { id: 1, type: 'fire', title: '🔥 Yangın Tespiti (Depo A)', location: 'Sanayi Bölgesi CAM-01', time: '11:14', status: 'CRITICAL', coords: [41.0137, 28.9550] },
  { id: 2, type: 'traffic', title: '🚦 Aşırı Trafik Yoğunluğu', location: 'Atatürk Cad. Kavşak 3', time: '11:02', status: 'WARNING', coords: [41.0250, 28.9750] },
  { id: 3, type: 'security', title: '⚠️ İzinsiz Giriş Şüphesi', location: 'Güney Kapısı CAM-04', time: '10:58', status: 'WARNING', coords: [40.9950, 28.9600] }
];

let camerasList = [
  { id: 'CAM-01', name: 'Sanayi Depo A', ip: '192.168.1.101', status: 'ALARM', fps: 29.8, res: '1920x1080', model: 'YOLOv8-fire.pt', confidence: 0.92, coords: [41.0137, 28.9550] },
  { id: 'CAM-02', name: 'Ana Giriş Kapısı', ip: '192.168.1.102', status: 'LIVE', fps: 30.0, res: '1920x1080', model: 'YOLOv8s.pt', confidence: 0.88, coords: [41.0082, 28.9784] },
  { id: 'CAM-03', name: 'Otopark B Bölgesi', ip: '192.168.1.103', status: 'LIVE', fps: 29.5, res: '1920x1080', model: 'YOLOv8s.pt', confidence: 0.84, coords: [41.0200, 28.9890] },
  { id: 'CAM-04', name: 'Kuzey Kapısı', ip: '192.168.1.104', status: 'LIVE', fps: 25.0, res: '1280x720', model: 'YOLOv8n.pt', confidence: 0.79, coords: [40.9950, 28.9600] }
];

// ── MIME Types ────────────────────────────────────────────────────
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.mp4':  'video/mp4',
  '.webm': 'video/webm',
  '.svg':  'image/svg+xml',
  '.ico':  'image/x-icon',
};

// ── Request Handler ───────────────────────────────────────────────
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  let pathname    = decodeURIComponent(parsedUrl.pathname);

  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // ── REST API ENDPOINTS ─────────────────────────────────────────
  if (pathname.startsWith('/api/')) {
    res.setHeader('Content-Type', 'application/json; charset=utf-8');

    if (pathname === '/api/system-status') {
      const freeMem = os.freemem();
      const totalMem = os.totalmem();
      const usedMemPct = Math.round(((totalMem - freeMem) / totalMem) * 100);
      const cpus = os.cpus();

      res.writeHead(200);
      res.end(JSON.stringify({
        status: 'OK',
        uptime: Math.round(process.uptime()),
        memory: { totalMB: Math.round(totalMem / 1024 / 1024), usedPct: usedMemPct },
        cpu: { cores: cpus.length, model: cpus[0].model },
        activeCameras: camerasList.filter(c => c.status !== 'OFFLINE').length,
        totalIncidents: systemIncidents.length,
        timestamp: new Date().toISOString()
      }));
      return;
    }

    if (pathname === '/api/cameras') {
      res.writeHead(200);
      res.end(JSON.stringify({ cameras: camerasList }));
      return;
    }

    if (pathname === '/api/incidents') {
      res.writeHead(200);
      res.end(JSON.stringify({ incidents: systemIncidents }));
      return;
    }

    if (pathname === '/api/trigger-alert' && (req.method === 'POST' || req.method === 'GET')) {
      const type = parsedUrl.query.type || 'fire';
      const newIncident = {
        id: Date.now(),
        type: type,
        title: type === 'fire' ? '🔥 ACİL YANGIN ALARMI (Test)' : '⚠️ GÜVENLİK İHLALİ',
        location: 'Sistem Test Bölgesi',
        time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
        status: 'CRITICAL',
        coords: [41.0150, 28.9600]
      };
      systemIncidents.unshift(newIncident);
      if (type === 'fire') {
        camerasList[0].status = 'ALARM';
      }

      res.writeHead(200);
      res.end(JSON.stringify({ success: true, incident: newIncident, totalIncidents: systemIncidents.length }));
      return;
    }

    if (pathname === '/api/clear-alerts' && (req.method === 'POST' || req.method === 'GET')) {
      systemIncidents = systemIncidents.filter(i => i.status !== 'CRITICAL');
      camerasList[0].status = 'LIVE';
      res.writeHead(200);
      res.end(JSON.stringify({ success: true, message: 'Tüm kritik alarmlar temizlendi.' }));
      return;
    }

    res.writeHead(404);
    res.end(JSON.stringify({ error: 'API Endpoint Not Found' }));
    return;
  }

  // ── STATIC FILE SERVING ─────────────────────────────────────────
  if (pathname === '/' || pathname === '/index' || pathname === '/index.html') {
    pathname = '/dashboard.html';
  }

  const filePath = path.join(ROOT, pathname);
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('403 Forbidden');
    return;
  }

  const ext = path.extname(filePath).toLowerCase();
  const mimeType = MIME[ext] || 'application/octet-stream';

  fs.stat(filePath, (err, stat) => {
    if (err || !stat.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end('<h1>404 Sayfa Bulunamadı</h1>');
      return;
    }

    // Range request support for video streaming
    const isVideo = ['.mp4', '.webm', '.avi', '.mov'].includes(ext);
    if (isVideo && req.headers.range) {
      const range = req.headers.range;
      const parts = range.replace(/bytes=/, '').split('-');
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : stat.size - 1;
      const chunkSize = end - start + 1;

      res.writeHead(206, {
        'Content-Range': `bytes ${start}-${end}/${stat.size}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': chunkSize,
        'Content-Type': mimeType,
      });
      fs.createReadStream(filePath, { start, end }).pipe(res);
    } else {
      const headers = { 'Content-Type': mimeType, 'Cache-Control': 'no-cache' };
      if (isVideo) {
        headers['Accept-Ranges'] = 'bytes';
        headers['Content-Length'] = stat.size;
      }
      res.writeHead(200, headers);
      fs.createReadStream(filePath).pipe(res);
    }
  });
});

server.listen(PORT, HOST, () => {
  console.log(`\n🚀 MultiVision AI Server & REST API Running on http://localhost:${PORT}\n`);
});
