import logging
import sys
import traceback

from PIL import Image

from FileTranslator.Converters.ImageAndPDF import merge_images_into_pdf
from FileTranslator.Converters.ImageAndPDF import split_pdf_into_images

# OCR
from FileTranslator.OCR.IOCR import IOCR
from FileTranslator.OCR.OCRManager import get_ocr

# Translators
from FileTranslator.Translator.ITranslator import ITranslator
from FileTranslator.Translator.TranslatorManager import get_translator

# Other
import FileTranslator.Util.Logs as Logs
from FileTranslator.Util.ParseArgs import parse_args
from FileTranslator.Util.PathInfo import PathInfo
from FileTranslator.Util.TranslateInfo import TranslateInfo

################################################################################


class CLI:
    def __init__(self):
        pass

    def start(self):
        # Read args and set up variables
        self._prologue()

        # Split pdf into images
        self.translate_info.images = split_pdf_into_images(
            self.path_info.source_file_path
        )

        # Translate images
        try:
            self._translate_images()
        except:
            Logs.error(
                "Unexpected error. "
                "Emergency termination of the program. "
                "Save current progress? (y/n)"
            )
            smb = input()
            while smb not in ["y", "n"]:
                Logs.warning(
                    "Incorrect symbol. Type 'y' or 'n' and press 'enter'"
                )
                smb = input()
            if smb == "n":
                return

        # Convert translated images to pdf
        pdf_path = self.path_info.target_file_path
        merge_images_into_pdf(self.translated_images, pdf_path)

    def _prologue(self):
        self.path_info = PathInfo(__file__)
        self.is_release = bool(open(self.path_info.is_release_path, "r").read())
        Logs.init(self.path_info.logs_path, self.is_release)
        self.translate_info = TranslateInfo()
        parse_args(self.path_info, self.translate_info)

    def _translate_images(self) -> None:
        # Init components
        self.ocr = get_ocr(self.path_info, self.translate_info)
        self.translator = get_translator(self.path_info, self.translate_info)

        # Init cycle variables
        self.raw_images_nums = self.translate_info.get_page_numbers()
        self.translated_images = []
        self.prev_page = -2
        self.finish_translation = False
        Logs.user("Starting translation")
        for i in self.raw_images_nums:
            # Check for finish
            if self.finish_translation:
                break
            self._translate_image_loop(i)

    def _translate_image_loop(self, ind: int) -> None:
        Logs.user(f"*** Translating page {ind + 1}  ***")
        cur_image = self.translate_info.images[ind]
        self.save_context = (
            self.translate_info.save_context and ind == self.prev_page + 1
        )
        self.page_handled = False

        while not self.page_handled and not self.finish_translation:
            try:
                translated_image = self._translate_image(cur_image)
                self.translated_images.append(translated_image)
                self.prev_page = ind
                break
            except:
                self._handle_translation_failure(ind)
        Logs.user(f"page {ind + 1} translated")

    def _translate_image(self, image: Image) -> Image:
        # Extract text from image
        Logs.user("Extracting text")
        text = self.ocr.get_text_to_translate(image, self.save_context)
        Logs.dev(f"text before translation:\n{text}\n-------------------")

        # Translate text
        Logs.user("Translating text")
        text = self.translator.translate(text)
        Logs.dev(f"text after translation:\n{text}\n-------------------")

        # Save translated image
        Logs.user("Saving translated text")
        res = self.ocr.translated_text_to_image(text, self.translator)
        self.page_handled = True
        return res

    def _handle_translation_failure(self, ind: int):
        Logs.warning(f"Exception raised while translating page {ind + 1}")
        logging.error(traceback.format_exc())
        sys.stderr.flush()
        sys.stdout.flush()
        Logs.warning(
            "Put according letter and press 'enter':\n"
            "r: retry to translate this page and "
            "continue translating\n"
            "s: skip page and continue translating\n"
            "f: finish translation and save translated pages"
        )
        smb = input()
        while smb not in ["r", "s", "f"]:
            Logs.warning(
                "Incorrect symbol. Type 'r', 's' or 'f' and press 'enter'"
            )
            smb = input()
        if smb == "r":
            self.translator.reset()
            self.ocr.reset()
            return
        if smb == "s":
            image = self.ocr.translated_text_to_image("", self.translator)
            self.translated_images.append(image)
            self.page_handled = True
            self.translator.reset()
            self.ocr.reset()
        if smb == "f":
            self.finish_translation = True
            return

    is_release = True
    path_info: PathInfo
    translate_info: TranslateInfo
    ocr: IOCR
    translator: ITranslator
    raw_images_nums: list[int]
    translated_images: list[Image]
    prev_page: int
    finish_translation: bool
    save_context: bool
    page_handled: bool


def main():
    cli = CLI()
    cli.start()
