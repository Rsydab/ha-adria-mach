"""Adria MACH – fristående testklient (Fas 2–3: autentisering + LÄSNING).

ENBART LÄSNING. Skickar inga styrkommandon.
Inloggningsuppgifter läses från .env i samma mapp (se .env.example).
Skriver aldrig ut token eller lösenord.

Kör:  python mach_client.py
"""
import json
import os
import sys
import urllib.request
import urllib.error

BASE = "https://mach-backend.solvesall.com"
UA = "ha-adria-mach-test/0.1 (personal Home Assistant integration test)"

# Enheter vi vill se, i prioriterad ordning (enhets-id -> etikett, enhet)
WANTED = [
    ("LIVING_MEASURED_TEMPERATURE", "Inomhustemperatur", "°C"),
    ("OUTSIDE_MEASURED_TEMPERATURE", "Utomhustemperatur", "°C"),
    ("OUTSIDE_MEASURED_HUMIDITY", "Utomhusfuktighet", "%"),
    ("FRESH_WATER_LEVEL", "Färskvatten", "%"),
    ("WASTE_WATER_LEVEL", "Gråvatten", "%"),
    ("GAS_BOTTLE_LEVEL_P", "Gasol flaska 1", "%"),
    ("GAS_BOTTLE_LEVEL_BACKUP_P", "Gasol flaska 2", "%"),
    ("GAS_SENSOR_MEASUREMENT_STATUS", "Gasolsensor status", ""),
    ("LIVING_BATTERY_SOC", "Bodelsbatteri SOC", "%"),
    ("LIVING_BATTERY_VOLTAGE", "Bodelsbatteri spänning", "V"),
    ("LIVING_BATTERY_CURRENT", "Bodelsbatteri ström", "A"),
    ("MAINS_SUPPLY_VALUE", "Landström ansluten", ""),
    ("ENERGY_SOURCE", "Energikälla", ""),
    ("ALDE_PANEL_VALUE", "Alde panel", ""),
    ("AIR_HEATER_VALUE", "Alde värme på/av", ""),
    ("AIR_HEATER_WORKING", "Alde värme arbetar", ""),
    ("AIR_HEATER_TEMPERATURE", "Alde börtemperatur", "°C"),
    ("WATER_HEATER_WORKING", "Varmvatten arbetar", ""),
    ("HEATER_NOTIFICATION", "Värmare notis", ""),
    ("INTERNAL_LIGHT_VALUE", "Innerbelysning", ""),
    ("EXTERNAL_LIGHT_VALUE", "Ytterbelysning", ""),
    ("WATER_PUMP_VALUE", "Vattenpump", ""),
    ("LTE_SIGNAL_STRENGTH", "LTE signal", ""),
    ("SYSTEM_IO_FIRMWARE_VERSION", "Firmware", ""),
]

# Enhets-id som aldrig skrivs ut eller sparas (personliga identifierare / hemligheter)
SENSITIVE_SUBSTR = ("SIM_ID", "PASSWORD", "PIN", "USERNAME", "APN", "SMS_FORWARDING")

NOT_SET = -9007199254740991


def load_env(path):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def post(path, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE + path, data=data, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def auth(username, password):
    r = post("/v0/client/api/auth", {"username": username, "password": password})
    token = r.get("token")
    if not token:
        raise SystemExit("Inloggning misslyckades: inget token i svaret. Svar-nycklar: %s" % list(r.keys()))
    print("Inloggad. Token giltigt i %.0f min." % (r.get("durationMSec", 0) / 60000))
    return token


def rpc(token, mach_id, rtype, method, **content):
    body = {
        "token": token,
        "machId": mach_id,
        "payload": {"type": "ui-req", "payload": {"type": rtype, "content": {"method": method, **content}}},
    }
    r = post("/v0/client/api/all", body)
    if r.get("status") != 200:
        raise SystemExit("RPC %s/%s gav status %s" % (rtype, method, r.get("status")))
    return r.get("payload")


def fmt(v, unit):
    if v == NOT_SET or v is None:
        return "(ej satt)"
    return "%s %s" % (v, unit) if unit else str(v)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    env = load_env(os.path.join(here, ".env"))
    username = env.get("MACH_USERNAME") or os.environ.get("MACH_USERNAME")
    password = env.get("MACH_PASSWORD") or os.environ.get("MACH_PASSWORD")
    mach_id = env.get("MACH_ID") or os.environ.get("MACH_ID")
    if not (username and password):
        raise SystemExit("Saknar MACH_USERNAME eller MACH_PASSWORD. Kopiera .env.example till .env och fyll i.")

    try:
        token = auth(username, password)
        if not mach_id:
            sync = post("/v0/api/mobile/syncData", {"payload": {"current": [], "deleted": []},
                                                    "auth": {"username": username, "password": password}})
            found = [d["machId"] for b in ("add", "update") for d in (sync.get("devices", {}).get(b) or []) if d.get("machId")]
            if not found:
                raise SystemExit("Ingen MACH-enhet hittades på kontot.")
            mach_id = found[0]
            print("Hittade enhet automatiskt: %s%s" % (mach_id, " (fler finns: %s)" % ", ".join(found[1:]) if len(found) > 1 else ""))
        info = rpc(token, mach_id, "systemRequest", "getMachInfo")
        print("MACH-info: typ=%s version=%s release=%s" % (info.get("type"), info.get("version"), info.get("releaseType")))

        values = rpc(token, mach_id, "device", "getValuesAll")
    except urllib.error.HTTPError as e:
        raise SystemExit("HTTP-fel %s på %s" % (e.code, e.url))
    except urllib.error.URLError as e:
        raise SystemExit("Nätverksfel: %s" % e.reason)

    by_id = {v.get("device"): v.get("status") for v in values.get("values", []) if isinstance(v, dict)}
    print("\nHämtade %d enheter.\n" % len(by_id))
    print("%-28s %s" % ("Sensor", "Värde"))
    print("-" * 50)
    for dev, label, unit in WANTED:
        if dev in by_id:
            print("%-28s %s" % (label, fmt(by_id[dev], unit)))
        else:
            print("%-28s (saknas)" % label)

    # Spara hela tillståndet lokalt (utan känsliga id:n) för vidare analys
    safe = {k: v for k, v in by_id.items() if not any(s in k for s in SENSITIVE_SUBSTR)}
    out = os.path.join(here, "last_values.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(safe, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("\nAlla värden (utom känsliga id:n) sparade i: %s" % out)


if __name__ == "__main__":
    sys.exit(main())
