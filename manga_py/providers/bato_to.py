import re

from manga_py.provider import Provider
from .helpers.std import Std
from ..crypt.bato_to_crypt import BatoToCrypt


class BatoTo(Provider, Std):

    def get_chapter_index(self) -> str:
        return '{}-{}'.format(
            self.chapter_id,
            self.chapter[1],
        )

    def get_main_content(self):
        url = self.get_url()
        if ~url.find('/chapter/'):
            url = self.html_fromstring(url, '.nav-path .nav-title > a', 0).get('href')
        return self.http_get(url)

    def get_manga_name(self) -> str:
        selector = '.nav-path .nav-title > a,.title-set .item-title > a'
        content = self.http_get(self.get_url())
        return self.text_content(content, selector, 0)

    def get_chapters(self):
        items = self._elements('.main > .item > a')
        n = self.http().normalize_uri
        result = []
        for i in items:
            title = i.cssselect('b')[0].text_content().strip(' \n\t\r')
            if ~title.find('DELETED'):  # SKIP DELETED
                continue
            result.append((
                n(i.get('href')),
                title,
            ))
        return result

    @staticmethod
    def _sort_files(data):
        keys = sorted(data, key=lambda _: int(_))
        return [data[i] for i in keys]

    def get_files(self):
        content = self.http_get(self.chapter[0])
        data = self.re.search(r'\simages\s*=\s*(\{.+});', content)
        try:
            return self._sort_files(self.json.loads(data.group(1)))
        except AttributeError:  # new format
            server = BatoToCrypt.decrypt_server(content)
            server = self.json.loads(server)

            images = self.re.search(r'\simages\s*=\s*(\[.+\]);', content).group(1)
            images = self.json.loads(images)

            n = self.http().normalize_uri
            print([n(f'{server}{img}') for img in images])
            return [n(f'{server}{img}') for img in images]
        except ValueError as e:
            self.log(f'Bato.to get_files error: {e}')
            return []

    def get_cover(self) -> str:
        return self._cover_from_content('.attr-cover img')

    def book_meta(self) -> dict:
        # todo meta
        pass

    def chapter_for_json(self):
        return self.chapter[0]

    # region specified data for eduhoribe/comic-builder

    def chapter_details(self, chapter) -> dict:

        volume = re.search('Volume \\d+', chapter[1])
        volume = re.findall('\\d+', volume.group())[0] if volume is not None else None

        chapter = re.search('Chapter \\d+', chapter[1])
        chapter = re.findall('\\d+', chapter.group())[0] if chapter is not None else None

        return {
            "chapter": chapter,
            "volume": volume,
            "title": None,
            "language": None,
            "publisher": None,
        }

    def manga_details(self):
        authors = [author.text for author in self._elements('.attr-item > span > a')]
        description = '\n'.join([desc.text for desc in self._elements('.attr-main > pre')])

        return {
            "title": self.get_manga_name(),
            "description": description,
            "authors": authors,
            "sauce": self.original_url,
            "volume_covers": {"": self.get_cover()},
        }

    # endregion


main = BatoTo
