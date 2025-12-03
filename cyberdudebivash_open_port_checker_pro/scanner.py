import nmap
import requests
from pathlib import Path
import json
import os

def get_shodan_key():
    config_path = Path.home() / ".cyberdudebivash" / "config.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                return json.load(f).get("shodan_key", "")
        except:
            return ""
    return ""

def run_scan(target, ports, is_pro, update_progress, update_results, use_shodan):
    scanner = nmap.PortScanner()
    try:
        update_results("[+] Starting scan...\n")
        scanner.scan(target, ports)
        progress = 0
        for host in scanner.all_hosts():
            update_results(f"\nHost: {host} ({scanner[host].hostname()})\n")
            update_results(f"State: {scanner[host].state()}\n")
            for proto in scanner[host].all_protocols():
                ports_list = scanner[host][proto].keys()
                for port in ports_list:
                    state = scanner[host][proto][port]['state']
                    service = scanner[host][proto][port].get('name', 'unknown')
                    update_results(f"  {port}/{proto}: {state} [{service}]\n")
                    progress += 1
                    update_progress(int(progress * 10))
            if is_pro and use_shodan:
                key = get_shodan_key()
                if key:
                    try:
                        r = requests.get(f"https://api.shodan.io/shodan/host/{host}?key={key}", timeout=5)
                        if r.status_code == 200:
                            data = r.json()
                            update_results(f"  Shodan: {data.get('org','?')} | {data.get('os','?')}\n")
                    except:
                        pass
        update_results("\nSCAN COMPLETE — STAY DANGEROUS.")
        update_progress(100)
    except Exception as e:
        update_results(f"ERROR: {str(e)}")