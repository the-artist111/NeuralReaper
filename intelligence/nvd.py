import requests
from datetime import datetime, timedelta, UTC

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class NVDCollector:

    def fetch(self, days_back=7, results=50):

        end = datetime.now(UTC)
        start = end - timedelta(days=days_back)

        params = {
            "pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "pubEndDate": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "resultsPerPage": results
        }

        print("[+] Fetching recent CVEs from NVD...")

        response = requests.get(
            NVD_API,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        vulns = []

        for item in data.get("vulnerabilities", []):

            cve = item["cve"]

            vuln = {
                "id": cve["id"],
                "published": cve["published"],
                "lastModified": cve["lastModified"],
                "description": cve.get("descriptions", [{}])[0].get("value", ""),
                "cvss": None,
                "severity": "UNKNOWN"
            }

            metrics = cve.get("metrics", {})

            if "cvssMetricV31" in metrics:
                cvss = metrics["cvssMetricV31"][0]["cvssData"]
                vuln["cvss"] = cvss["baseScore"]
                vuln["severity"] = cvss["baseSeverity"]

            elif "cvssMetricV40" in metrics:
                cvss = metrics["cvssMetricV40"][0]["cvssData"]
                vuln["cvss"] = cvss["baseScore"]
                vuln["severity"] = cvss["baseSeverity"]

            vulns.append(vuln)

        return vulns


if __name__ == "__main__":

    collector = NVDCollector()

    vulns = collector.fetch()

    print(f"\nDownloaded {len(vulns)} recent CVEs\n")

    for vuln in vulns[:10]:
        print(
            f"{vuln['id']} | "
            f"{vuln['severity']} | "
            f"{vuln['cvss']}"
        )
