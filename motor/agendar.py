"""Coloca na agenda do Instagram os videos novos de motor/fila.json que ja existem em videos/."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fila = json.load(open(f"{R}/motor/fila.json", encoding="utf-8"))
ag_path = f"{R}/instagram/agenda.json"
agenda = json.load(open(ag_path, encoding="utf-8"))
ja = {a["video"] for a in agenda}
novos = 0
for f in fila:
    v = f"{f['id']}.mp4"
    if v not in ja and os.path.exists(f"{R}/videos/{v}"):
        agenda.append({"video": v, "quando": f["quando"], "legenda": f["legenda"]}); novos += 1
agenda.sort(key=lambda a: a["quando"])
json.dump(agenda, open(ag_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(ag_path, "a").write("\n")
print(f"{novos} videos novos na agenda")
