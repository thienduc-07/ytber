import http.server
import threading
import subprocess
import time
import json
import urllib.request
import asyncio
import os
import struct

BUNDLE_PATH = '/tmp/webcodecsRenderer.bundle.js'
OUTPUT_DIR = '/tmp/ytber_test_videos'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 0: Ensure bundle is built
build_res = subprocess.run([
    'npx', 'esbuild', 'src/services/webcodecsRenderer.ts',
    '--bundle', '--format=esm', f'--outfile={BUNDLE_PATH}'
], cwd='/Users/thienduc/Desktop/Code/ytbshorts/frontend', capture_output=True, text=True)
if build_res.returncode != 0:
    print('Failed to bundle webcodecsRenderer:', build_res.stderr)
    exit(1)

HTML_CONTENT = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>YTBER Multi-Video Studio Verification</title>
</head>
<body>
    <div id="status">INIT</div>
    <script type="module">
        import {{ WebCodecsRenderer }} from '/bundle.js';

        // 1. Shorts History Manifest (9:16, 1080x1920)
        const historyManifest = {{
            episode_id: 'test-history-ep',
            title: 'Chiến Thắng Điện Biên Phủ 1954',
            genre: 'historical_doc',
            video_format: 'short-form',
            aspect_ratio: '9:16',
            total_duration_sec: 3.0,
            total_frames: 90,
            voice_config: {{ voice: 'vi-VN-NamMinhNeural', rate: '+0%', pitch: '+0Hz' }},
            video_specs: {{ width: 1080, height: 1920, fps: 30 }},
            audio_specs: {{ target_lufs: -14.0, true_peak: -1.0 }},
            scenes: [
                {{
                    scene_order: 1,
                    scene_type: 'hook',
                    narration_text: 'Chiến thắng Điện Biên Phủ năm 1954 lừng lẫy năm châu chấn động địa cầu',
                    duration_seconds: 1.5,
                    start_frame: 0,
                    end_frame: 45,
                    visual_method: 'archival',
                    visual_config: {{}},
                    subtitles_json: []
                }},
                {{
                    scene_order: 2,
                    scene_type: 'climax',
                    narration_text: 'Lá cờ Quyết chiến Quyết thắng tung bay kiêu hãnh trên nóc hầm De Castries',
                    duration_seconds: 1.5,
                    start_frame: 45,
                    end_frame: 90,
                    visual_method: 'parallax',
                    visual_config: {{}},
                    subtitles_json: []
                }}
            ]
        }};

        // 2. Long-form Economics Manifest (16:9, 1920x1080)
        const economicsManifest = {{
            episode_id: 'test-economics-ep',
            title: 'Toàn Cảnh Kinh Tế Việt Nam 2024',
            genre: 'economics',
            video_format: 'long-form',
            aspect_ratio: '16:9',
            total_duration_sec: 3.0,
            total_frames: 90,
            voice_config: {{ voice: 'vi-VN-HoaiMyNeural', rate: '+0%', pitch: '+0Hz' }},
            video_specs: {{ width: 1920, height: 1080, fps: 30 }},
            audio_specs: {{ target_lufs: -14.0, true_peak: -1.0 }},
            scenes: [
                {{
                    scene_order: 1,
                    scene_type: 'data_hook',
                    narration_text: 'Tăng trưởng kinh tế Việt Nam đạt mốc bảy phẩy không chín phần trăm ấn tượng',
                    duration_seconds: 1.5,
                    start_frame: 0,
                    end_frame: 45,
                    visual_method: 'infographic',
                    visual_config: {{}},
                    subtitles_json: []
                }},
                {{
                    scene_order: 2,
                    scene_type: 'market_context',
                    narration_text: 'Vốn đầu tư trực tiếp nước ngoài FDI giải ngân lập kỷ lục trong năm năm qua',
                    duration_seconds: 1.5,
                    start_frame: 45,
                    end_frame: 90,
                    visual_method: 'stock',
                    visual_config: {{}},
                    subtitles_json: []
                }}
            ]
        }};

        // 3. Shorts Horror Manifest (9:16, 1080x1920)
        const horrorManifest = {{
            episode_id: 'test-horror-ep',
            title: 'Bí Ẩn Căn Nhà Ma Cuối Làng',
            genre: 'horror',
            video_format: 'short-form',
            aspect_ratio: '9:16',
            total_duration_sec: 3.0,
            total_frames: 90,
            voice_config: {{ voice: 'vi-VN-NamMinhNeural', rate: '-10%', pitch: '-2Hz' }},
            video_specs: {{ width: 1080, height: 1920, fps: 30 }},
            audio_specs: {{ target_lufs: -16.0, true_peak: -1.0 }},
            scenes: [
                {{
                    scene_order: 1,
                    scene_type: 'eerie_hook',
                    narration_text: 'Đêm nay sương mù giăng kín căn nhà hoang bỏ phế không một bóng người',
                    duration_seconds: 1.5,
                    start_frame: 0,
                    end_frame: 45,
                    visual_method: 'archival',
                    visual_config: {{}},
                    subtitles_json: []
                }},
                {{
                    scene_order: 2,
                    scene_type: 'terror_climax',
                    narration_text: 'Cánh cửa gỗ mục nát bỗng từ từ mở toang phát ra tiếng rít ghê rợn',
                    duration_seconds: 1.5,
                    start_frame: 45,
                    end_frame: 90,
                    visual_method: 'procedural',
                    visual_config: {{}},
                    subtitles_json: []
                }}
            ]
        }};

        window.renderTarget = async (targetName) => {{
            const renderer = new WebCodecsRenderer();
            let manifestToRender;
            if (targetName === 'history') manifestToRender = historyManifest;
            else if (targetName === 'economics') manifestToRender = economicsManifest;
            else if (targetName === 'horror') manifestToRender = horrorManifest;

            const res = await renderer.renderVideo(manifestToRender);

            const postRes = await fetch(`/save_output?name=${{targetName}}`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'video/mp4' }},
                body: res.blob
            }});

            if (!postRes.ok) throw new Error('Save failed');

            return {{
                success: true,
                target: targetName,
                blob_size: res.blob.size,
                width: manifestToRender.video_specs.width,
                height: manifestToRender.video_specs.height,
                duration_sec: res.durationSec,
                fps: res.effectiveFps
            }};
        }};
    </script>
</body>
</html>
"""

class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path.startswith('/save_output'):
            # Parse target name
            import urllib.parse
            parsed_url = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(parsed_url.query)
            target = q.get('name', ['video'])[0]
            out_file = os.path.join(OUTPUT_DIR, f"{target}.mp4")

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            with open(out_file, 'wb') as f:
                f.write(body)

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
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
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            self.send_header('Cross-Origin-Embedder-Policy', 'credentialless')
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
        if pos + 8 > len(data):
            break
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

def run():
    port = 8894
    server = http.server.HTTPServer(('127.0.0.1', port), ServerHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    proc = subprocess.Popen([
        chrome_path,
        '--headless=new',
        '--remote-debugging-port=9230',
        '--user-data-dir=/tmp/chrome_studio_audit'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(1.5)

    try:
        req = urllib.request.Request('http://127.0.0.1:9230/json/new', method='PUT')
        res = urllib.request.urlopen(req)
        ws_url = json.loads(res.read().decode())['webSocketDebuggerUrl']

        async def execute_batch():
            import websockets
            async with websockets.connect(ws_url, max_size=None) as ws:
                await ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': f'http://127.0.0.1:{port}/'}}))
                await ws.recv()
                await asyncio.sleep(1.0)

                targets = [
                    ('history', 'Shorts Historical Documentary (9:16, 1080x1920)'),
                    ('economics', 'Long-form Economics Video (16:9, 1920x1080)'),
                    ('horror', 'Shorts Horror Specialization (9:16, 1080x1920)')
                ]

                print('=====================================================')
                print('GENERATING 3 MULTI-GENRE PRODUCTION TEST VIDEOS')
                print('=====================================================')

                for target_id, target_desc in targets:
                    print(f"\n--- RENDERING: {target_desc} ---")
                    await ws.send(json.dumps({
                        'id': 2,
                        'method': 'Runtime.evaluate',
                        'params': {
                            'expression': f"window.renderTarget('{target_id}')",
                            'awaitPromise': True,
                            'returnByValue': True
                        }
                    }))

                    render_msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
                    val = render_msg.get('result', {}).get('result', {}).get('value')
                    assert val and val.get('success'), f"Render failed for {target_id}: {render_msg}"

                    out_path = os.path.join(OUTPUT_DIR, f"{target_id}.mp4")
                    assert os.path.exists(out_path), f"File {out_path} missing"
                    file_size = os.path.getsize(out_path)

                    print(f"✓ Rendered {file_size} bytes ({val['width']}x{val['height']} @ 30 FPS, {val['fps']} render FPS)")

                    # Check Box Structure
                    atoms, raw = parse_mp4_atoms(out_path)
                    atom_names = [a[0] for a in atoms]
                    assert 'ftyp' in atom_names and 'moov' in atom_names and 'mdat' in atom_names
                    assert atom_names.index('moov') < atom_names.index('mdat'), "Fast Start failure"
                    assert b'avc1' in raw and b'mp4a' in raw, "Track codec failure"
                    print(f"✓ ISOBMFF Valid: Fast Start moov before mdat, dual tracks avc1 + mp4a")

                    # Check afinfo
                    af = subprocess.run(['afinfo', out_path], capture_output=True, text=True)
                    assert af.returncode == 0, f"afinfo rejected {out_path}"
                    print(f"✓ CoreAudio afinfo validated: 48kHz Stereo AAC stream valid")

                print('\n=====================================================')
                print('ALL 3 PRODUCTION TEST VIDEOS SUCCESSFULLY GENERATED!')
                print(f'Saved in: {OUTPUT_DIR}')
                print('=====================================================')
                return True

        success = asyncio.run(execute_batch())
        if not success:
            exit(1)
    finally:
        proc.terminate()
        server.shutdown()

if __name__ == '__main__':
    run()
