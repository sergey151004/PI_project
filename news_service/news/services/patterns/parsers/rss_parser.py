import feedparser
from typing import List, Dict, Any
from .base_parser import NewsParser


class RSSParser(NewsParser):
    """Парсер RSS-лент (использует библиотеку feedparser)"""

    def __init__(self, source_name: str):
        self.source_name = source_name

    def parse(self, raw_data: Any) -> List[Dict]:
        if not isinstance(raw_data, dict) or 'entries' not in raw_data:
            return []

        items = []
        for entry in raw_data['entries']:
            item = {
                'title': entry.get('title', '').strip(),
                'content': self._extract_content(entry),
                'source_url': entry.get('link', ''),
                'published_at': entry.get('published_parsed') or entry.get('updated_parsed'),
                'image_url': self._extract_image(entry),
                'tags': self._extract_tags(entry),
            }
            # убираем None-поля
            item = {k: v for k, v in item.items() if v is not None}
            items.append(item)

        return items

    def get_source_name(self) -> str:
        return self.source_name

    def _extract_content(self, entry) -> str:
        content = (
            entry.get('content', [{}])[0].get('value') or
            entry.get('summary') or
            entry.get('description') or
            ''
        )
        return content.strip()

    @staticmethod
    def _extract_image(entry) -> str | None:
        # разные RSS-ленты кладут картинку по-разному
        if 'media_content' in entry:
            for media in entry['media_content']:
                if media.get('medium') == 'image':
                    return media.get('url')
        if 'enclosure' in entry and entry.enclosure.get('type', '').startswith('image/'):
            return entry.enclosure.get('href')
        return None

    @staticmethod
    def _extract_tags(entry) -> List[str]:
        tags = []
        if 'tags' in entry:
            for tag in entry['tags']:
                if 'term' in tag:
                    tags.append(tag['term'].strip())
        return tags