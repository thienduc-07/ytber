import http.server
import threading
import subprocess
import time
import json
import urllib.request
import asyncio
import os
import struct

OUTPUT_DIR = '/tmp/ytber_audit_videos'
os.makedirs(OUTPUT_DIR, exist_ok=True)
BUNDLE_PATH = '/tmp/webcodecsRenderer.bundle.js'

# Ensure bundle exists
build_res = subprocess.run([
    'npx', 'esbuild', 'src/services/webcodecsRenderer.ts',
    '--bundle', '--format=esm', f'--outfile={BUNDLE_PATH}'
], cwd='/Users/thienduc/Desktop/Code/ytbshorts/frontend', capture_output=True, text=True)
if build_res.returncode != 0:
    print('Failed to bundle webcodecsRenderer:', build_res.stderr)
    exit(1)

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>WebCodecs Video Audit</title></head>
<body>
    <div id="status">INIT</div>
    <script type="module">
        import { WebCodecsRenderer } from '/bundle.js';

        window.renderCustomManifest = async function(manifest, targetName) {
            const renderer = new WebCodecsRenderer();
            const res = await renderer.renderVideo(manifest);
            const postRes = await fetch(`/save_output?name=${targetName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'video/mp4' },
                body: res.blob
            });
            if (!postRes.ok) throw new Error('Save failed');
            return {
                success: true,
                target: targetName,
                blob_size: res.blob.size,
                width: manifest.video_specs.width,
                height: manifest.video_specs.height,
                duration_sec: res.durationSec,
                fps: res.effectiveFps,
                total_frames: res.totalFrames
            };
        };
    </script>
</body>
</html>
"""

class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.startswith('/save_output'):
            import urllib.parse
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            target = q.get('name', ['video'])[0]
            out_file = os.path.join(OUTPUT_DIR, f"{target}.mp4")
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            with open(out_file, 'wb') as f:
                f.write(body)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            self.send_header('Cross-Origin-Embedder-Policy', 'credentialless')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        elif self.path == '/bundle.js':
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            self.end_headers()
            with open(BUNDLE_PATH, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *args): pass

def parse_mp4_atoms(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    pos = 0
    atoms = []
    while pos < len(data):
        if pos + 8 > len(data): break
        size, btype = struct.unpack('>I4s', data[pos:pos+8])
        name = btype.decode('ascii', errors='ignore')
        if size == 0:
            atoms.append((name, pos, len(data) - pos))
            break
        elif size == 1:
            size = struct.unpack('>Q', data[pos+8:pos+16])[0]
        atoms.append((name, pos, size))
        pos += size
    return atoms, data

def run_tests():
    port = 8896
    server = http.server.HTTPServer(('127.0.0.1', port), ServerHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    proc = subprocess.Popen([
        chrome_path,
        '--headless=new',
        '--remote-debugging-port=9232',
        '--user-data-dir=/tmp/chrome_audit_p2'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(1.5)

    try:
        req = urllib.request.Request('http://127.0.0.1:9232/json/new', method='PUT')
        res = urllib.request.urlopen(req)
        ws_url = json.loads(res.read().decode())['webSocketDebuggerUrl']

        async def execute_all():
            import websockets
            async with websockets.connect(ws_url, max_size=None) as ws:
                await ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': f'http://127.0.0.1:{port}/'}}))
                await ws.recv()
                await asyncio.sleep(1.0)

                test_cases = [
                    {
                        'id': 'video_30s_916',
                        'name': '1. 30-second 9:16 video (1080x1920)',
                        'manifest': {
                            'episode_id': 'audit-30s-916',
                            'title': 'Audit 30s 9:16',
                            'genre': 'historical_doc',
                            'video_format': 'short-form',
                            'aspect_ratio': '9:16',
                            'total_duration_sec': 30.0,
                            'total_frames': 900,
                            'voice_config': {'voice': 'vi-VN-NamMinhNeural', 'rate': '+0%', 'pitch': '+0Hz'},
                            'video_specs': {'width': 1080, 'height': 1920, 'fps': 30},
                            'audio_specs': {'target_lufs': -14.0, 'true_peak': -1.0},
                            'scenes': [
                                {'scene_order': 1, 'scene_type': 'hook', 'narration_text': 'Phần một: Giới thiệu biến cố lịch sử.', 'duration_seconds': 10.0, 'visual_method': 'archival'},
                                {'scene_order': 2, 'scene_type': 'escalation', 'narration_text': 'Phần hai: Diễn biến chiến dịch khốc liệt.', 'duration_seconds': 10.0, 'visual_method': 'map'},
                                {'scene_order': 3, 'scene_type': 'resolution', 'narration_text': 'Phần ba: Kết cục và bài học lịch sử.', 'duration_seconds': 10.0, 'visual_method': 'infographic'}
                            ]
                        }
                    },
                    {
                        'id': 'video_60s_916',
                        'name': '2. 60-second 9:16 video (1080x1920)',
                        'manifest': {
                            'episode_id': 'audit-60s-916',
                            'title': 'Audit 60s 9:16',
                            'genre': 'horror',
                            'video_format': 'short-form',
                            'aspect_ratio': '9:16',
                            'total_duration_sec': 60.0,
                            'total_frames': 1800,
                            'voice_config': {'voice': 'vi-VN-NamMinhNeural', 'rate': '+0%', 'pitch': '+0Hz'},
                            'video_specs': {'width': 1080, 'height': 1920, 'fps': 30},
                            'audio_specs': {'target_lufs': -14.0, 'true_peak': -1.0},
                            'scenes': [
                                {'scene_order': 1, 'scene_type': 'eerie_hook', 'narration_text': 'Đêm định mệnh tại ngôi làng hoang phế.', 'duration_seconds': 15.0, 'visual_method': 'archival'},
                                {'scene_order': 2, 'scene_type': 'suspense_build', 'narration_text': 'Những tiếng động kỳ quái xuất hiện.', 'duration_seconds': 15.0, 'visual_method': 'archival'},
                                {'scene_order': 3, 'scene_type': 'shock_reveal', 'narration_text': 'Bóng đen hiện hình trong gương vỡ.', 'duration_seconds': 15.0, 'visual_method': 'archival'},
                                {'scene_order': 4, 'scene_type': 'abrupt_end', 'narration_text': 'Không còn ai có thể thoát ra ngoài.', 'duration_seconds': 15.0, 'visual_method': 'archival'}
                            ]
                        }
                    },
                    {
                        'id': 'video_60s_169',
                        'name': '3. 60-second 16:9 video (1920x1080)',
                        'manifest': {
                            'episode_id': 'audit-60s-169',
                            'title': 'Audit 60s 16:9',
                            'genre': 'economics',
                            'video_format': 'long-form',
                            'aspect_ratio': '16:9',
                            'total_duration_sec': 60.0,
                            'total_frames': 1800,
                            'voice_config': {'voice': 'vi-VN-NamMinhNeural', 'rate': '+0%', 'pitch': '+0Hz'},
                            'video_specs': {'width': 1920, 'height': 1080, 'fps': 30},
                            'audio_specs': {'target_lufs': -14.0, 'true_peak': -1.0},
                            'scenes': [
                                {'scene_order': 1, 'scene_type': 'market_overview', 'narration_text': 'Tổng quan thị trường tài chính toàn cầu.', 'duration_seconds': 20.0, 'visual_method': 'infographic'},
                                {'scene_order': 2, 'scene_type': 'data_deepdive', 'narration_text': 'Phân tích dòng vốn và tỷ giá đồng bạc.', 'duration_seconds': 20.0, 'visual_method': 'infographic'},
                                {'scene_order': 3, 'scene_type': 'strategic_outlook', 'narration_text': 'Dự báo xu hướng đầu tư tương lai.', 'duration_seconds': 20.0, 'visual_method': 'infographic'}
                            ]
                        }
                    },
                    {
                        'id': 'video_multiscene',
                        'name': '4. Multi-scene transition video (5 scenes)',
                        'manifest': {
                            'episode_id': 'audit-multiscene',
                            'title': 'Multi-scene transitions',
                            'genre': 'science',
                            'video_format': 'short-form',
                            'aspect_ratio': '9:16',
                            'total_duration_sec': 25.0,
                            'total_frames': 750,
                            'voice_config': {'voice': 'vi-VN-NamMinhNeural', 'rate': '+0%', 'pitch': '+0Hz'},
                            'video_specs': {'width': 1080, 'height': 1920, 'fps': 30},
                            'audio_specs': {'target_lufs': -14.0, 'true_peak': -1.0},
                            'scenes': [
                                {'scene_order': 1, 'scene_type': 'intro', 'narration_text': 'Khám phá vũ trụ bao la.', 'duration_seconds': 5.0, 'visual_method': 'map'},
                                {'scene_order': 2, 'scene_type': 'phenomenon', 'narration_text': 'Sự hình thành của lỗ đen.', 'duration_seconds': 5.0, 'visual_method': 'infographic'},
                                {'scene_order': 3, 'scene_type': 'analysis', 'narration_text': 'Bẻ cong không thời gian.', 'duration_seconds': 5.0, 'visual_method': 'map'},
                                {'scene_order': 4, 'scene_type': 'experiment', 'narration_text': 'Sóng hấp dẫn được phát hiện.', 'duration_seconds': 5.0, 'visual_method': 'infographic'},
                                {'scene_order': 5, 'scene_type': 'conclusion', 'narration_text': 'Bước tiến mới của nhân loại.', 'duration_seconds': 5.0, 'visual_method': 'archival'}
                            ]
                        }
                    }
                ]

                results = {}
                for tc in test_cases:
                    print(f"Executing test: {tc['name']}...")
                    t_start = time.time()
                    m_json = json.dumps(tc['manifest'])
                    await ws.send(json.dumps({
                        'id': 10,
                        'method': 'Runtime.evaluate',
                        'params': {
                            'expression': f"window.renderCustomManifest({m_json}, '{tc['id']}')",
                            'awaitPromise': True,
                            'returnByValue': True
                        }
                    }))
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=120))
                    val = msg.get('result', {}).get('result', {}).get('value')
                    elapsed = time.time() - t_start

                    out_path = os.path.join(OUTPUT_DIR, f"{tc['id']}.mp4")
                    file_size = os.path.getsize(out_path) if os.path.exists(out_path) else 0

                    # Parse atoms
                    atoms, raw = parse_mp4_atoms(out_path)
                    atom_names = [a[0] for a in atoms]

                    # Check afinfo
                    af = subprocess.run(['afinfo', out_path], capture_output=True, text=True)

                    results[tc['id']] = {
                        'name': tc['name'],
                        'success': val.get('success') if val else False,
                        'size_bytes': file_size,
                        'duration_sec': val.get('duration_sec') if val else None,
                        'total_frames': val.get('total_frames') if val else None,
                        'render_fps': val.get('fps') if val else None,
                        'wall_time_sec': round(elapsed, 2),
                        'atoms': atom_names,
                        'fast_start': ('moov' in atom_names and 'mdat' in atom_names and atom_names.index('moov') < atom_names.index('mdat')),
                        'tracks': ('avc1' in str(raw) and 'mp4a' in str(raw)),
                        'afinfo_valid': (af.returncode == 0)
                    }
                    print(f" -> Result for {tc['id']}: {results[tc['id']]}")

                print("\n================ FINAL PHASE 2 RESULTS ================")
                print(json.dumps(results, indent=2))
                with open('/tmp/phase2_results.json', 'w') as f:
                    json.dump(results, f, indent=2)

        asyncio.run(execute_all())
    finally:
        proc.terminate()
        server.shutdown()

if __name__ == '__main__':
    run_tests()
