"""Publica no Instagram os Reels agendados em agenda.json que ja passaram do horario.

Roda no GitHub Actions. Usa a API oficial da Meta (Instagram API com login do Instagram).
O token fica no segredo IG_TOKEN do repositorio; ele nunca aparece no codigo nem nos logs.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://graph.instagram.com/v21.0"
API_FB = "https://graph.facebook.com/v21.0"
IG_USER_ID = os.environ.get("IG_USER_ID", "17841476308695336")  # @padrejoseanthonio
REPO_RAW = "https://raw.githubusercontent.com/{repo}/main/videos/{video}"
AGENDA = os.path.join(os.path.dirname(__file__), "agenda.json")


def chamar(metodo, caminho, **params):
    params["access_token"] = os.environ["IG_TOKEN"]
    dados = urllib.parse.urlencode(params).encode()
    if metodo == "GET":
        req = urllib.request.Request(f"{API}/{caminho}?{dados.decode()}")
    else:
        req = urllib.request.Request(f"{API}/{caminho}", data=dados, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace").replace(os.environ["IG_TOKEN"], "***")
        raise RuntimeError(f"{metodo} {caminho} -> {e.code}: {corpo}") from None


def publicar(ig_id, post, repo):
    url = REPO_RAW.format(repo=repo, video=urllib.parse.quote(post["video"]))
    cont = chamar("POST", f"{ig_id}/media", media_type="REELS", video_url=url,
                  caption=post["legenda"], share_to_feed="true")
    cid = cont["id"]
    for _ in range(60):  # ate ~10 min processando o video
        st = chamar("GET", cid, fields="status_code,status")
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram recusou o video {post['video']}: {st}")
        time.sleep(10)
    else:
        raise RuntimeError(f"Video {post['video']} demorou demais para processar")
    pub = chamar("POST", f"{ig_id}/media_publish", creation_id=cid)
    return pub["id"]


def conectar():
    global API
    try:  # token do login do Instagram
        me = chamar("GET", "me", fields="user_id,username")
        return me["user_id"], me["username"]
    except RuntimeError as e1:  # token do Facebook / usuario do sistema
        API = API_FB
        try:
            me = chamar("GET", IG_USER_ID, fields="id,username")
        except RuntimeError as e2:
            raise RuntimeError(f"Token nao funcionou.\n{e1}\n{e2}") from None
        return me["id"], me["username"]


def main():
    if not os.environ.get("IG_TOKEN"):
        print("Segredo IG_TOKEN ainda nao configurado; nada a fazer.")
        return 0
    repo = os.environ["GITHUB_REPOSITORY"]
    if os.environ.get("TESTAR") == "true":
        global API
        API = API_FB
        for cam, campos in [("me", "id,name"),
                            ("me/accounts", "name,instagram_business_account{id,username}"),
                            ("2377319089775132/instagram_accounts", "id,username"),
                            ("2377319089775132/owned_instagram_accounts", "id,username"),
                            ("debug_token", None)]:
            try:
                kw = {"fields": campos} if campos else {"input_token": os.environ["IG_TOKEN"]}
                r = chamar("GET", cam, **kw)
                if cam == "debug_token":
                    d = r.get("data", {})
                    r = {k: d.get(k) for k in ("type", "app_id", "is_valid", "expires_at", "scopes", "granular_scopes")}
                print("DIAG", cam, json.dumps(r, ensure_ascii=False)[:1500])
            except Exception as e:
                print("DIAG", cam, "ERRO", str(e)[:400])
        return 0
    agenda = json.load(open(AGENDA, encoding="utf-8"))
    agora = datetime.now(timezone.utc)
    pendentes = [p for p in agenda if not p.get("publicado")
                 and datetime.fromisoformat(p["quando"]) <= agora]
    if not pendentes:
        print("Nenhum post na hora.")
        return 0
    ig_id, nome = conectar()
    print(f"Conta: @{nome}")
    erros = 0
    for p in pendentes[:3]:  # no maximo 3 por rodada
        try:
            mid = publicar(ig_id, p, repo)
            p["publicado"] = agora.isoformat(timespec="minutes")
            p["media_id"] = mid
            print(f"OK {p['video']} -> {mid}")
        except Exception as e:  # segue para o proximo e falha no final
            erros += 1
            p["ultimo_erro"] = str(e)[:500]
            print(f"ERRO {p['video']}: {e}")
    with open(AGENDA, "w", encoding="utf-8") as f:
        json.dump(agenda, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
