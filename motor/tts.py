"""Gera as vozes que faltam (ElevenLabs API) para os itens de motor/fila.json."""
import json, os, re, sys, urllib.request, urllib.parse

KEY = os.environ["ELEVENLABS_API_KEY"]
BASE = os.path.dirname(os.path.abspath(__file__))
VOZ_NOME = "Fabio Oliveira"
API = "https://api.elevenlabs.io"


def req(method, path, body=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(API + path, data=data, method=method,
                               headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "*/*"})
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            b = resp.read()
            return b if raw else json.loads(b)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} -> {e.code}: {e.read().decode(errors='replace')[:400]}")


def voice_id():
    vs = req("GET", "/v1/voices")["voices"]
    for v in vs:
        if VOZ_NOME.lower() in v["name"].lower():
            return v["voice_id"]
    sh = req("GET", "/v1/shared-voices?" + urllib.parse.urlencode({"search": VOZ_NOME, "page_size": 5}))["voices"]
    v = next(x for x in sh if VOZ_NOME.lower() in x["name"].lower())
    req("POST", f"/v1/voices/add/{v['public_owner_id']}/{v['voice_id']}", {"new_name": v["name"]})
    return v["voice_id"]


def modelo():
    try:
        ms = [m["model_id"] for m in req("GET", "/v1/models")]
    except SystemExit:
        return "eleven_multilingual_v2"
    for pref in ("eleven_v4", "eleven_v3", "eleven_multilingual_v2"):
        if pref in ms:
            return pref
    return next((m for m in ms if "v4" in m), "eleven_multilingual_v2")


def main():
    fila = json.load(open(f"{BASE}/fila.json", encoding="utf-8"))
    textos = json.load(open(f"{BASE}/stories/lote3.json", encoding="utf-8"))
    faltam = [f["id"] for f in fila if not os.path.exists(f"{BASE}/voices/{f['id']}.mp3")]
    if not faltam:
        print("Nenhuma voz faltando."); return
    vid, mid = voice_id(), modelo()
    print(f"voz {vid} modelo {mid}; gerando: {faltam}")
    for k in faltam:
        audio = req("POST", f"/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                    {"text": textos[k], "model_id": mid, "language_code": "pt",
                     "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}, raw=True)
        open(f"{BASE}/voices/{k}.mp3", "wb").write(audio)
        print(f"OK {k}: {len(audio)} bytes, {len(textos[k])} caracteres")


if __name__ == "__main__":
    main()
