import feedparser
import json
import os
import re
from datetime import datetime, UTC

from intelligence.database import IntelligenceDatabase

RSS_FEEDS = [
    {
        "name": "The Hacker News",
        "url": "https://feeds.feedburner.com/TheHackersNews"
    },
    {
        "name": "BleepingComputer",
        "url": "https://www.bleepingcomputer.com/feed/"
    },
    {
        "name": "SecurityWeek",
        "url": "https://www.securityweek.com/feed/"
    },
    {
        "name": "ProjectDiscovery",
        "url": "https://projectdiscovery.io/blog/rss.xml"
    }
]

CVE_REGEX = re.compile(r"CVE-\d{4}-\d+")


class RSSCollector:

    def __init__(self):
        self.output = "data/rss_news.json"

    def fetch(self):

        articles = []

        for feed in RSS_FEEDS:

            print(f"[+] Fetching {feed['name']}")

            try:

                parsed = feedparser.parse(feed["url"])

                for entry in parsed.entries:

                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    content = f"{title} {summary}"

                    articles.append({

                        "source": feed["name"],
                        "title": title,
                        "url": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "summary": summary,
                        "cves": sorted(
                            set(
                                CVE_REGEX.findall(content)
                            )
                        )

                    })

            except Exception as e:

                print(f"[-] {feed['name']} : {e}")

        db = IntelligenceDatabase()

        added = db.merge_articles(articles)

        os.makedirs("data", exist_ok=True)

        with open(self.output, "w", encoding="utf-8") as f:

            json.dump(
                {
                    "updated": datetime.now(UTC).isoformat(),
                    "count": len(articles),
                    "new_articles": added,
                    "articles": articles
                },
                f,
                indent=4,
                ensure_ascii=False
            )

        print()
        print(f"[+] Retrieved: {len(articles)} articles")
        print(f"[+] New Articles: {added}")

        return articles


if __name__ == "__main__":

    RSSCollector().fetch()
