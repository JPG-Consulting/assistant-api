#!/usr/bin/env python3
import argparse
import logging
import signal
import subprocess
import sys
import time

import requests

logger = logging.getLogger(__name__)

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
    # Defaults align with Piper PCM output: 16kHz, mono, S16_LE.
    parser.add_argument("--sample-rate", type=int, default=16000, help="PCM sample rate for playback")
    parser.add_argument("--channels", type=int, default=1, help="PCM channel count for playback")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--no-server", action="store_true", help="Do not start or stop the API server")
    parser.add_argument("text", help="Text to speak")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # This manual test intentionally supports PCM playback only.
    if args.format != "pcm":
        parser.error("Only pcm playback is supported by this test")

    server_cmd = [
        sys.executable,
        "-m",
        "assistant_api.main",
        "--host",
        args.host,
        "--port",
        str(args.port),
    ]

    server = None
    try:
        if not args.no_server:
            server = subprocess.Popen(
                server_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            wait_for_server(f"http://{args.host}:{args.port}/v1/audio/speech")

        payload = {
            "input": args.text,
            "format": args.format,
        }
        if args.model:
            payload["model"] = args.model
        if args.voice:
            payload["voice"] = args.voice

        requested_voice = args.voice or "server default"
        logger.info("Requested voice: %s", requested_voice)
        logger.info("Requested audio format: %s", args.format)
        logger.info(
            "PCM playback spec: S16_LE %s Hz %s channel(s)",
            args.sample_rate,
            args.channels,
        )

        r = requests.post(
            f"http://{args.host}:{args.port}/v1/audio/speech",
            json=payload,
            stream=True,
        )
        r.raise_for_status()

        logger.info("Starting ALSA playback...")
        aplay = subprocess.Popen(
            [
                "aplay",
                "-D",
                args.device,
                "-f",
                "S16_LE",
                "-r",
                str(args.sample_rate),
                "-c",
                str(args.channels),
            ],
            stdin=subprocess.PIPE,
        )

        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                aplay.stdin.write(chunk)

        aplay.stdin.close()
        aplay.wait()

    finally:
        if server is not None:
            server.send_signal(signal.SIGTERM)
            server.wait(timeout=5)

if __name__ == "__main__":
    main()
