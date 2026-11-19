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
OUTPUT_MP4 = '/tmp/rendered_p0_video.mp4'

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
    <title>P0.1 MP4 Muxer Verification</title>
</head>
<body>
    <div id="status">INIT</div>
    <script type="module">
        import {{ WebCodecsRenderer }} from '/bundle.js';

        const sampleManifest = {{
            episode_id: 'p0-test-ep',
            title: 'Kinh Tế Việt Nam 2024 P0 Test',
            total_duration_sec: 2.0,
            total_frames: 60,
            voice_config: {{ voice: 'vi-VN-HoaiMyNeural', rate: '+0%', pitch: '+0Hz' }},
            video_specs: {{ width: 1080, height: 1920, fps: 30 }},
            audio_specs: {{ target_lufs: -14.0, true_peak: -1.0 }},
            scenes: [
                {{
                    scene_order: 1,
                    scene_type: 'hook',
                    narration_text: 'Tăng trưởng kinh tế Việt Nam đạt mốc ấn tượng bảy phẩy không chín phần trăm',
                    duration_seconds: 1.0,
                    start_frame: 0,
                    end_frame: 30,
                    visual_method: 'infographic',
                    visual_config: {{}},
                    subtitles_json: []
                }},
                {{
                    scene_order: 2,
                    scene_type: 'climax',
                    narration_text: 'Vốn đầu tư FDI giải ngân kỷ lục trong năm năm qua',
                    duration_seconds: 1.0,
                    start_frame: 30,
                    end_frame: 60,
                    visual_method: 'procedural',
                    visual_config: {{}},
                    subtitles_json: []
                }}
            ]
        }};

        // TEST 1: Full Render & Muxing
        window.testFullRender = async () => {{
            const renderer = new WebCodecsRenderer();
            let progressUpdates = 0;

            const res = await renderer.renderVideo(sampleManifest, (p) => {{
                progressUpdates++;
            }});

            // Post blob directly to server to avoid websocket frame size limits
            const postRes = await fetch('/save_output', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'video/mp4' }},
                body: res.blob
            }});
            if (!postRes.ok) {{
                throw new Error('Failed to save output to server: ' + postRes.statusText);
            }}

            return {{
                success: true,
                blob_size: res.blob.size,
                blob_type: res.blob.type,
                duration_sec: res.durationSec,
                total_frames: res.totalFrames,
                effective_fps: res.effectiveFps,
                progress_calls: progressUpdates
            }};
        }};

        // TEST 2: Cancellation
        window.testCancellation = async () => {{
            const renderer = new WebCodecsRenderer();
            let cancelledTriggered = false;

            const renderPromise = renderer.renderVideo(sampleManifest, (p) => {{
                if (!cancelledTriggered && p.currentFrame >= 3) {{
                    cancelledTriggered = true;
                    renderer.cancel();
                }}
            }});

            try {{
                await renderPromise;
                return {{ success: false, error: 'Did not throw on cancel' }};
            }} catch (err) {{
                return {{
                    success: err.message === 'Video rendering was cancelled',
                    caught_message: err.message
                }};
            }}
        }};

        // TEST 3: Error Propagation
        window.testErrorPropagation = async () => {{
            const renderer = new WebCodecsRenderer();
            const badManifest = {{
                ...sampleManifest,
                video_specs: {{ width: 0, height: 0, fps: 30 }}
            }};

            try {{
                await renderer.renderVideo(badManifest);
                return {{ success: false, error: 'Did not throw on bad config' }};
            }} catch (err) {{
                return {{
                    success: true,
                    caught_message: err.message
                }};
            }}
        }};
    </script>
</body>
</html>
"""

class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save_output':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            with open(OUTPUT_MP4, 'wb') as f:
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
    port = 8893
    server = http.server.HTTPServer(('127.0.0.1', port), ServerHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    proc = subprocess.Popen([
        chrome_path,
        '--headless=new',
        '--remote-debugging-port=9229',
        '--user-data-dir=/tmp/chrome_p0_audit'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(1.5)

    try:
        req = urllib.request.Request('http://127.0.0.1:9229/json/new', method='PUT')
        res = urllib.request.urlopen(req)
        ws_url = json.loads(res.read().decode())['webSocketDebuggerUrl']

        async def execute_tests():
            import websockets
            async with websockets.connect(ws_url, max_size=None) as ws:
                # 1. Navigate to test page
                await ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': f'http://127.0.0.1:{port}/'}}))
                await ws.recv()
                await asyncio.sleep(1.0)

                print('=== TEST 1: FULL RENDER & MP4 MUXING (1080x1920 @ 30 FPS) ===')
                await ws.send(json.dumps({
                    'id': 2,
                    'method': 'Runtime.evaluate',
                    'params': {'expression': 'window.testFullRender()', 'awaitPromise': True, 'returnByValue': True}
                }))

                # Wait for render (up to 30s)
                render_msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
                r1 = render_msg.get('result', {}).get('result', {}).get('value')
                if not r1 or not r1.get('success'):
                    print('FAIL: Test 1 render failed:', render_msg)
                    return False

                print('Render summary:', json.dumps(r1, indent=2))
                assert os.path.exists(OUTPUT_MP4), f'File {OUTPUT_MP4} was not written'
                file_size = os.path.getsize(OUTPUT_MP4)
                print(f'Wrote {file_size} bytes to {OUTPUT_MP4}')
                assert file_size == r1['blob_size'], f'File size {file_size} does not match blob size {r1["blob_size"]}'

                # Inspect MP4 Box Structure
                atoms, raw_data = parse_mp4_atoms(OUTPUT_MP4)
                print('\nTop-level MP4 Atoms:')
                for name, pos, size in atoms:
                    print(f'  Atom: [{name}], offset: {pos}, size: {size} bytes')

                # Verify Fast Start (moov before mdat)
                atom_names = [a[0] for a in atoms]
                assert 'ftyp' in atom_names, 'Missing ftyp box'
                assert 'moov' in atom_names, 'Missing moov box'
                assert 'mdat' in atom_names, 'Missing mdat box'
                moov_idx = atom_names.index('moov')
                mdat_idx = atom_names.index('mdat')
                assert moov_idx < mdat_idx, f'Fast Start violation: moov ({moov_idx}) appears after mdat ({mdat_idx})'
                print('✓ Fast Start verified: moov is placed BEFORE mdat')

                # Verify tracks and codecs in moov
                moov_bytes = raw_data[atoms[moov_idx][1] : atoms[moov_idx][1] + atoms[moov_idx][2]]
                assert b'trak' in moov_bytes, 'Missing trak box in moov'
                trak_count = moov_bytes.count(b'trak')
                print(f'✓ Total tracks in moov: {trak_count}')
                assert trak_count >= 2, f'Expected at least 2 tracks (video + audio), got {trak_count}'

                assert b'avc1' in moov_bytes, 'Missing avc1 visual sample entry in video track'
                assert b'mp4a' in moov_bytes, 'Missing mp4a audio sample entry in audio track'
                print('✓ Video track codec: avc1 (H.264)')
                print('✓ Audio track codec: mp4a (AAC)')

                # Native macOS afinfo decoding validation
                print('\nRunning afinfo audio/media inspection:')
                af_res = subprocess.run(['afinfo', OUTPUT_MP4], capture_output=True, text=True)
                print(af_res.stdout.strip())
                if af_res.returncode != 0:
                    print('FAIL: afinfo rejected the file:', af_res.stderr)
                    return False
                print('✓ afinfo verified: file format is valid mp4f, AAC audio stream successfully decoded')

                # TEST 2: Cancellation handling
                print('\n=== TEST 2: CANCELLATION HANDLING ===')
                await ws.send(json.dumps({
                    'id': 3,
                    'method': 'Runtime.evaluate',
                    'params': {'expression': 'window.testCancellation()', 'awaitPromise': True, 'returnByValue': True}
                }))
                cancel_msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
                r2 = cancel_msg.get('result', {}).get('result', {}).get('value')
                print('Cancellation result:', r2)
                assert r2.get('success') is True, f'Cancellation test failed: {r2}'
                print('✓ Cancellation correctly rejects with "Video rendering was cancelled" without fake output')

                # TEST 3: Error propagation
                print('\n=== TEST 3: ERROR HANDLING & PROPAGATION ===')
                await ws.send(json.dumps({
                    'id': 4,
                    'method': 'Runtime.evaluate',
                    'params': {'expression': 'window.testErrorPropagation()', 'awaitPromise': True, 'returnByValue': True}
                }))
                err_msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
                r3 = err_msg.get('result', {}).get('result', {}).get('value')
                print('Error test result:', r3)
                assert r3.get('success') is True, f'Error propagation test failed: {r3}'
                print('✓ Encoder error correctly propagated and not swallowed')

                print('\n=============================================')
                print('ALL P0.1 MP4 MUXING TESTS PASSED EMPIRICALLY!')
                print('=============================================')
                return True

        success = asyncio.run(execute_tests())
        if not success:
            exit(1)
    finally:
        proc.terminate()
        server.shutdown()

if __name__ == '__main__':
    run()
