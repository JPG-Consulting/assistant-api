#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time
import requests
import signal

def wait_for_server(url, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code < 500:
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("Server did not become ready")

def main():
    parser = argparse.ArgumentParser(description="Play streaming TTS audio to an ALSA device")
    parser.add_argument("-D", "--device", required=True, help="ALSA output device (aplay -D)")
    parser.add_argument("--format", default="pcm", choices=["pcm", "mp3", "opus"], help="Audio format")
    parser.add_argument("--model", default=None, help="Model identifier")
    parser.add_argument("--voice", default=None, help="Voice identifier")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("text", help="Text to speak")
    args = parser.parse_args()

    server_cmd = [
        sys.executable,
        "-m",
        "assistant_api.main",
        "--host",
        args.host,
        "--port",
        str(args.port),
    ]

    server = subprocess.Popen(server_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_for_server(f"http://{args.host}:{args.port}/v1/audio/speech")

        payload = {
            "input": args.text,
            "format": args.format,
        }
        if args.model:
            payload["model"] = args.model
        if args.voice:
            payload["voice"] = args.voice

        r = requests.post(
            f"http://{args.host}:{args.port}/v1/audio/speech",
            json=payload,
            stream=True,
        )
        r.raise_for_status()

        if args.format != "pcm":
            raise RuntimeError("Only pcm playback is supported by this test")

        aplay = subprocess.Popen(
            ["aplay", "-D", args.device, "-f", "S16_LE"],
            stdin=subprocess.PIPE,
        )

        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                aplay.stdin.write(chunk)

        aplay.stdin.close()
        aplay.wait()

    finally:
        server.send_signal(signal.SIGTERM)
        server.wait(timeout=5)

if __name__ == "__main__":
    main()
