"""Atualiza data/sofascore.json com os números de cada atleta no Sofascore.
Roda todo dia pelo GitHub Actions (.github/workflows/sofascore.yml)."""
import json, re, time, urllib.request, datetime

API = "https://api.sofascore.com/api/v1"
HDR = {"User-Agent": "Mozilla/5.0 (GFRAME site updater)", "Accept": "application/json"}

def get(path):
    req = urllib.request.Request(API + path, headers=HDR)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def pid(v):
    m = re.search(r"(\d{4,})", str(v or ""))
    return m.group(1) if m else None

def fmt(x, nd=0):
    if x is None: return None
    return f"{x:.{nd}f}" if nd else str(int(round(x)))

def build(player_id):
    info = get(f"/player/{player_id}")["player"]
    seasons = get(f"/player/{player_id}/statistics/seasons").get("uniqueTournamentSeasons", [])
    if not seasons: return None
    ut = seasons[0]["uniqueTournament"]; season = ut and seasons[0]["seasons"][0]
    st = get(f"/player/{player_id}/unique-tournament/{ut['id']}/season/{season['id']}/statistics/overall")["statistics"]
    gk = info.get("position") == "G"
    rows = [[fmt(st.get("appearances")), "Jogos"], [fmt(st.get("minutesPlayed")), "Minutos"]]
    if gk:
        rows += [[fmt(st.get("saves")), "Defesas"], [fmt(st.get("cleanSheet")), "Jogos sem sofrer gol"], [fmt(st.get("goalsConceded")), "Gols sofridos"]]
    else:
        rows += [[fmt(st.get("goals")), "Gols"], [fmt(st.get("assists")), "Assistências"]]
    if st.get("rating"): rows.append([fmt(st["rating"], 2), "Nota média"])
    rows = [r for r in rows if r[0] is not None]
    return {"stats": rows, "note": f"{ut['name']} · {season['year']}",
            "sofa": f"https://www.sofascore.com/player/{info.get('slug','')}/{player_id}"}

def main():
    ids = json.load(open("data/sofascore_ids.json"))
    out = {"updated": datetime.datetime.utcnow().strftime("%Y-%m-%d")}
    for k, v in ids.items():
        if k.startswith("_"): continue
        p = pid(v)
        if not p: continue
        try:
            d = build(p)
            if d: out[k] = d
            print(k, "ok")
        except Exception as e:
            print(k, "erro:", e)
        time.sleep(2)
    json.dump(out, open("data/sofascore.json", "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
