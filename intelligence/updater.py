import json
import os
from datetime import datetime, UTC

from intelligence.rss import RSSCollector
from intelligence.nvd import NVDCollector
from intelligence.cisa import CISACollector


OUTPUT = "data/threat_intelligence.json"


def update():

    print("=" * 60)
    print("NeuralReaper Intelligence Update")
    print("=" * 60)

    rss = RSSCollector().fetch()
    nvd = NVDCollector().fetch()
    kev = CISACollector().fetch()

    intelligence = {}

    # -------------------------
    # RSS
    # -------------------------

    intelligence["rss"] = rss

    # -------------------------
    # NVD
    # -------------------------

    for vuln in nvd:

        cid = vuln["id"]

        if cid not in intelligence:

            intelligence[cid] = vuln

            intelligence[cid]["kev"] = False

    # -------------------------
    # CISA
    # -------------------------

    for exploited in kev:

        cid = exploited["id"]

        if cid in intelligence:

            intelligence[cid]["kev"] = True

        else:

            intelligence[cid] = exploited

            intelligence[cid]["kev"] = True

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:

        json.dump(
            {
                "updated": datetime.now(UTC).isoformat(),
                "total_cves": len(intelligence) - 1,
                "rss_articles": len(rss),
                "database": intelligence,
            },
            f,
            indent=4,
            ensure_ascii=False,
        )

    print()
    print("=" * 60)
    print("Finished")
    print("=" * 60)

    print(f"RSS : {len(rss)}")
    print(f"NVD : {len(nvd)}")
    print(f"CISA: {len(kev)}")
    print()
    print(f"Saved -> {OUTPUT}")


if __name__ == "__main__":
    update()
