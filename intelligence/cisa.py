import requests
import json
import os
from datetime import datetime, UTC

CISA_KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)


class CISACollector:

    def __init__(self):
        self.output = "data/cisa_kev.json"

    def fetch(self):

        print("[+] Downloading CISA KEV Catalog...")

        response = requests.get(CISA_KEV_URL, timeout=30)
        response.raise_for_status()

        data = response.json()

        vulnerabilities = []

        for vuln in data.get("vulnerabilities", []):

            vulnerabilities.append({

                "id": vuln.get("cveID"),

                "vendor": vuln.get("vendorProject"),

                "product": vuln.get("product"),

                "name": vuln.get("vulnerabilityName"),

                "dateAdded": vuln.get("dateAdded"),

                "requiredAction": vuln.get("requiredAction"),

                "knownRansomware": vuln.get("knownRansomwareCampaignUse"),

                "notes": vuln.get("notes", "")
            })

        os.makedirs("data", exist_ok=True)

        with open(self.output, "w", encoding="utf-8") as f:

            json.dump(
                {
                    "updated": datetime.now(UTC).isoformat(),
                    "count": len(vulnerabilities),
                    "vulnerabilities": vulnerabilities
                },
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"[+] Saved {len(vulnerabilities)} exploited CVEs")

        return vulnerabilities


if __name__ == "__main__":

    collector = CISACollector()

    kev = collector.fetch()

    print()

    for item in kev[:10]:
        print(item["id"], "-", item["vendor"])
