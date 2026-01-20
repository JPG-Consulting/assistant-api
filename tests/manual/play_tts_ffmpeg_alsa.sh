#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  play_tts_ffmpeg_alsa.sh [--host HOST] [--port PORT] [--voice VOICE] [--no-server] <alsa_device> <format> <text>

Required arguments:
  alsa_device   ALSA output device passed to aplay (-D)
  format        mp3 or opus
  text          Text to speak (quote if it contains spaces)

Optional arguments:
  --host        Server host (default: 127.0.0.1)
  --port        Server port (default: 8000)
  --voice       Optional voice identifier
  --no-server   Assume the server is already running

Notes:
  This manual test validates compressed streaming only (mp3/opus).
  It is not suitable for PCM debugging; use play_tts_alsa.py for PCM playback.
USAGE
}

host="127.0.0.1"
port="8000"
voice=""
no_server=0
positional=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      host="$2"
      shift 2
      ;;
    --port)
      port="$2"
      shift 2
      ;;
    --no-server)
      no_server=1
      shift
      ;;
    --voice)
      voice="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -* )
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
    *)
      positional+=("$1")
      shift
      ;;
  esac
done

if [[ $# -gt 0 ]]; then
  positional+=("$@")
fi

if [[ ${#positional[@]} -ne 3 ]]; then
  usage
  exit 1
fi

device="${positional[0]}"
format="${positional[1]}"
text="${positional[2]}"

if [[ "$format" != "mp3" && "$format" != "opus" ]]; then
  echo "Format must be mp3 or opus" >&2
  exit 1
fi

json_escape() {
  local input="$1"
  input=${input//\\/\\\\}
  input=${input//"/\\"}
  input=${input//$'\n'/\\n}
  input=${input//$'\r'/\\r}
  input=${input//$'\t'/\\t}
  printf '%s' "$input"
}

wait_for_server() {
  local url="$1"
  local timeout=10
  local start
  start=$(date +%s)
  while true; do
    local now
    now=$(date +%s)
    if (( now - start > timeout )); then
      echo "Server did not become ready" >&2
      exit 1
    fi

    local status
    status=$(curl --silent --output /dev/null --write-out '%{http_code}' "$url" || true)
    if [[ "$status" != "000" && "$status" -lt 500 ]]; then
      return 0
    fi
    sleep 0.2
  done
}

server_pid=""
cleanup() {
  if [[ -n "$server_pid" ]]; then
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  fi
}

if [[ "$no_server" -eq 0 ]]; then
  python -m assistant_api.main --host "$host" --port "$port" >/dev/null 2>&1 &
  server_pid=$!
  trap cleanup EXIT
  wait_for_server "http://${host}:${port}/v1/audio/speech"
fi

payload=$(printf '{"input":"%s","format":"%s"}' "$(json_escape "$text")" "$format")
if [[ -n "$voice" ]]; then
  payload=$(printf '{"input":"%s","format":"%s","voice":"%s"}' \
    "$(json_escape "$text")" \
    "$format" \
    "$(json_escape "$voice")")
fi

curl --silent --show-error -N \
  -H "Content-Type: application/json" \
  -d "$payload" \
  "http://${host}:${port}/v1/audio/speech" \
  | ffmpeg -hide_banner -loglevel error \
    -i pipe:0 \
    -f s16le \
    -acodec pcm_s16le \
    -ac 1 \
    -ar 22050 \
    pipe:1 \
  | aplay -D "$device" -f S16_LE -r 22050 -c 1
