import json
import os


class IntelligenceDatabase:
    def __init__(self, db_file="data/intelligence_db.json"):
        self.db_file = db_file
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.db_file):
            self.save([])

    def load(self):
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save(self, data):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def merge_articles(self, new_articles):
        existing = self.load()

        seen = {
            article.get("url")
            for article in existing
        }

        added = 0

        for article in new_articles:
            if article.get("url") not in seen:
                existing.append(article)
                seen.add(article.get("url"))
                added += 1

        self.save(existing)

        return added

    def stats(self):
        data = self.load()

        return {
            "articles": len(data)
        }
