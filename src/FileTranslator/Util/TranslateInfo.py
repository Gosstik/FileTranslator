import os.path

from PIL import Image
from PyPDF4 import PdfFileReader

import FileTranslator.Util.Logs as Logs

################################################################################


class TranslateInfo:
    def __init__(self):
        pass

    def set_languages(self, src_lang: str, trg_lang: str):
        self.src_lang, self.trg_lang = src_lang, trg_lang

    def set_pages_count(self, file_path: str, extension: str):
        if extension == "pdf":
            self.images_count = PdfFileReader(open(file_path, "rb")).numPages
        else:
            raise NotImplementedError

    def set_pages_range(self, first: int | None, last: int | None):
        self.first_spec = first is not None
        self.first_page = first if self.first_spec else 1
        self.last_spec = last is not None
        self.last_page = last if self.last_spec else self.images_count
        self._check_file_bounds()

    def set_font(self, fonts_dir: str, font_file: str):
        self.font_path = os.path.join(fonts_dir, font_file)

    def get_page_numbers(self) -> list[int]:
        return [i for i in range(self.first_page - 1, self.last_page)]

    def entire_file_to_translate(self) -> bool:
        return self.first_page == 1 and self.last_page == self.images_count

    ############################################################################

    # Internals

    def _check_file_bounds(self) -> None:
        if self.first_spec:
            if self.first_page < 1 or self.first_page > self.images_count:
                Logs.error(
                    f"Incorrect value for first page. "
                    + self._error_info(self.images_count)
                )
                raise RuntimeError
        if self.last_spec:
            if self.last_page < 1 or self.last_page > self.images_count:
                Logs.error(
                    f"Incorrect value for last page. "
                    + self._error_info(self.images_count)
                )
                raise RuntimeError
        if self.first_page > self.last_page:
            Logs.error(
                f"First page must not be more than last page. "
                + self._error_info(self.images_count)
            )
            raise RuntimeError

    def _error_info(self, pages) -> str:
        first_page = "<not specified>" if self.first_spec else self.first_page
        last_page = "<not specified>" if self.last_spec else self.last_page
        return (
            f"Total number of pages = {pages}, "
            "Parsed arguments: "
            f"first page = {first_page}, "
            f"last page = {last_page}"
        )

    ocr_alias = "tesseract"
    translator_alias = "yandex"

    font_path: str
    src_lang: str
    trg_lang: str
    images_count: int
    images: list[Image]
    first_page: int
    last_page: int
    first_spec: bool
    last_spec: bool
    save_context: bool
