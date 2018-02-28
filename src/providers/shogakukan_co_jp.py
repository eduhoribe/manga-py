from src.providers.shogakukan_tameshiyo_me import ShogakukanTameshiyoMe
from .helpers.std import Std


class ShogakukanCoJp(ShogakukanTameshiyoMe, Std):

    def get_archive_name(self) -> str:
        return 'vol_{:0>3}-{}'.format(
            self.get_chapter_index(),
            self.re.search(r'/(\d+)', self.chapter).group(1)
        )

    def get_chapter_index(self) -> str:
        return str(self._chapter_index())

    def get_main_content(self):
        types = [
            'magazines/series',
            'books'
        ]
        re = r'(/(?:{})/\d+)'.format('|'.join(types))
        url = self.re.search(re, self.get_url()).group(1)
        return self.http_get(self.domain + url)

    def get_manga_name(self) -> str:
        return self._get_name(r'/(?:series|books)/(\d+)')

    def get_chapters(self):
        return self._elements('a[href*="shogakukan.tameshiyo.me"]')

    def get_cover(self) -> str:
        img = self._cover_from_content('.mainimg01')
        if not img:
            img = self._cover_from_content('.image01 > img', 'data-original')
        return img


main = ShogakukanCoJp
