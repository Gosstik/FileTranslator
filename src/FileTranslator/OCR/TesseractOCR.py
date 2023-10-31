# string.whitespace
from itertools import accumulate
from operator import add

# regex for transforming recognized text
import re
import string

# Read Image
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# convert language code from ISO 639-1 to ISO 639-2
import pycountry

# OCR
from pytesseract import pytesseract as pt

from FileTranslator.OCR.IOCR import IOCR
from FileTranslator.Translator.ITranslator import ITranslator
import FileTranslator.Util.Logs as Logs
from FileTranslator.Util.PathInfo import PathInfo
from FileTranslator.Util.TranslateInfo import TranslateInfo

################################################################################


def _get_lang_code(iso_639_1_code: str) -> str:
    return pycountry.languages.get(alpha_2=iso_639_1_code).alpha_3


def _get_font_size(text: str, width: int, font_path: str) -> int:
    start, finish = 1, 1
    cur = 1
    font = ImageFont.truetype(font_path, cur)
    inc = False
    while font.getbbox(text)[2] < width:
        if inc:
            finish += 1
        else:
            finish *= 2
        try:
            font = ImageFont.truetype(font_path, finish)
        except OSError:
            # invalid pixel size
            if inc:
                break
            else:
                inc = True
    if inc:
        finish -= 1
        return finish - 1
    while finish - start > 1:
        mid = (finish - start) // 2
        cur = start + mid
        font = ImageFont.truetype(font_path, cur)
        if font.getbbox(text)[2] > width:
            finish = cur
        else:
            start = cur
    return start


def _is_strip(word: str) -> bool:
    return bool(re.match(f"^[{string.whitespace}]*$", word))


def _empty(word: str) -> bool:
    return len(word) == 0


################################################################################


def _print_lines(text) -> None:
    pars = text.split("\n\n")
    lines = list()
    for par in pars:
        # dev_log(f"par:\n{par}")
        lines += par.split("\n")
    msg = ""
    for i, line in enumerate(lines):
        msg += f"{i}: {line}\n"
    Logs.dev(msg)


class TesseractOCR(IOCR):
    # Exceptions
    class IncorrectTranslatedTextFormat(Exception):
        pass

    # API
    def __init__(self):
        pass

    def init(self, path_info: PathInfo, translate_info: TranslateInfo) -> None:
        self.search_lang = _get_lang_code(translate_info.src_lang)
        self.font_path = translate_info.font_path
        self.context = ""
        self.save_context = self.context_added = False

    def change_search_language(self, iso_639_1_lang: str):
        self.search_lang = _get_lang_code(iso_639_1_lang)

    def get_text_to_translate(self, image: Image, save_context: bool) -> str:
        Logs.dev("get_text_to_translate() started")
        self.save_context = save_context
        self.image = image

        # extract text and its location from image
        self.src_dict = pt.image_to_data(
            self.image, lang=self.search_lang, output_type=pt.Output.DICT
        )

        # transform to string
        self._dict_to_text()
        self._compute_src_pars()

        Logs.dev("Transformed text")
        _print_lines(self.src_text)

        self._try_add_context()

        Logs.dev("get_text_to_translate() finished")
        return self.src_text

    def translated_text_to_image(
        self, text: str, translator: ITranslator
    ) -> Image:
        Logs.dev(f"Converting translated text to image")
        if _empty(text):
            res = self.image
            self.reset()
            Logs.dev(f"No text to convert, image saved unchanged")
            return res

        # handle context
        text = self._try_remove_context(text)
        self._save_context()

        lines = self._split_translated_text_to_lines(text, translator)

        self._put_text_on_image(lines)

        # save image
        res = self.image
        self.reset()
        Logs.dev(f"Converting translated text to image finished")
        return res

    def reset(self) -> None:
        self.image = Image.Image()
        self.src_text = self.trg_text = ""
        self.src_dict = {}
        self.boxes = list[TesseractOCR.LineBox]()

    # Internals
    class LineBox:
        x: int  # left top x
        y: int  # left top y
        w: int  # width
        h: int  # height

    def _split_translated_text_to_lines(
        self, text: str, translator: ITranslator
    ) -> list[str]:
        Logs.dev(f"Splitting translated text to lines")
        pars = text.split("\n\n")
        lines = list()
        for par in pars:
            lines += par.split("\n")
        for i, line in enumerate(lines):
            Logs.dev(f"{i}: {line}")
        if len(lines) != len(self.boxes):
            Logs.dev(
                "Incorrect number of lines after translation"
                f"len(lines) = {len(lines)},"
                f"len(self.boxes) = {len(self.boxes)}"
            )
            new_lines = []
            src_pars_count = len(self.pars_info)
            for i in range(src_pars_count):
                cur_lines = pars[i].split("\n")
                if len(self.pars_info[i]) == len(cur_lines):
                    Logs.dev(
                        f"Paragraph {i} coincide, "
                        f"len(cur_lines) = {len(cur_lines)}"
                    )
                    new_lines += cur_lines
                    continue
                # translating line by line
                Logs.dev("Translating line by line")
                for j in range(len(self.pars_info[i])):
                    new_lines.append(translator.translate(self.pars_info[i][j]))
                # make remaining text
                Logs.dev("Make remaining text")
                new_text = ""
                for j in range(i + 1, src_pars_count):
                    if len(new_text) != 0:
                        new_text += "\n\n" + "\n".join(self.pars_info[j])
                    else:
                        new_text = "\n".join(self.pars_info[j])
                # translate text
                Logs.dev(f"remaining text: {new_text}")
                new_lines += self._recursive_translation(
                    i + 1, new_text, translator
                )
                break
            lines = new_lines
        Logs.dev(f"Translated text splitted")
        return lines

    def _recursive_translation(
        self, cur_par_num: int, src_text: str, translator: ITranslator
    ) -> list[str]:
        Logs.dev("-------Recursive translation-----------")
        trg_text = translator.translate(src_text)
        pars = trg_text.split("\n\n")
        lines = list()
        for par in pars:
            lines += par.split("\n")
        for i, line in enumerate(lines):
            Logs.dev(f"{i}: {line}")
        if len(lines) != self._lines_left(cur_par_num):
            Logs.warning(
                "Incorrect number of lines after translationlen(lines) ="
                f" {len(lines)},self._lines_left(cur_par_num) ="
                f" {self._lines_left(cur_par_num)}"
            )
            new_lines = []
            src_pars_count = len(self.pars_info) - cur_par_num
            for i in range(src_pars_count):
                ni = i + cur_par_num
                cur_lines = pars[i].split("\n")
                if len(self.pars_info[ni]) == len(cur_lines):
                    new_lines += cur_lines
                    continue
                # translating line by line
                for j in range(len(self.pars_info[ni])):
                    new_lines.append(
                        translator.translate(self.pars_info[ni][j])
                    )
                # make remaining text
                if i + 1 == src_pars_count:
                    # if problem was in last paragraph, we translated all text
                    return new_lines
                new_text = ""
                for j in range(ni + 1, src_pars_count + cur_par_num):
                    if len(new_text) != 0:
                        new_text += "\n\n" + "\n".join(self.pars_info[j])
                    else:
                        new_text = "\n".join(self.pars_info[j])
                # translate text
                new_lines += self._recursive_translation(
                    i + 1, new_text, translator
                )
                return new_lines
        else:
            return lines

    def _dict_to_text(self) -> None:
        # init member fields
        self.src_text = ""
        self.boxes = list()

        # remove extra symbols
        self._remove_extra_symbols()

        # make self.src_text
        new_line_smb = 1
        accum_top_y = accum_bot_y = 0
        first_word_ind = words_in_line = 0  # first_word_ind in line
        for i, word in enumerate(self.src_dict["text"]):
            if len(word) == 0:
                if new_line_smb == 0:
                    # prev line ended
                    self._append_to_boxes(
                        first_word_ind, words_in_line, accum_top_y, accum_bot_y
                    )
                    new_line_smb = 1
                    self.src_text += "\n"
                elif new_line_smb < self.max_new_line:
                    new_line_smb += 1
                    self.src_text += "\n"
                else:
                    continue
            elif new_line_smb != 0:
                # new line started
                new_line_smb = 0
                first_word_ind = i
                words_in_line = 1
                accum_top_y = self.src_dict["top"][i]
                accum_bot_y = (
                    self.src_dict["top"][i] + self.src_dict["height"][i]
                )
                self.src_text += word
            else:
                # next word in line
                words_in_line += 1
                accum_top_y += self.src_dict["top"][i]
                accum_bot_y += (
                    self.src_dict["top"][i] + self.src_dict["height"][i]
                )
                self.src_text += " " + word
        # append last line
        words_count = len(self.src_dict["text"])
        if words_count != 0:
            self._append_to_boxes(
                first_word_ind, words_in_line, accum_top_y, accum_bot_y
            )
        return

    def _put_text_on_image(self, lines: list[str]):
        Logs.dev(f"Pytesseract, putting text on image")
        for i, line in enumerate(lines):
            # set variables
            box = self.boxes[i]
            y_scale = min(int(0.15 * box.h), 5)
            box.y, box.h = box.y - y_scale, box.h + 2 * y_scale

            # TODO: probably check conf
            # get optimal font size
            fontsize = _get_font_size(line, box.w, self.font_path)
            font = ImageFont.truetype(self.font_path, fontsize)

            # set text
            y_off = 1
            x_off = 2
            _, _, text_width, text_height = font.getbbox(line)
            text_width += 2 * x_off
            text_height = text_height + 2 * y_off
            # img = Image.new('RGBA', (text_width, text_height), color=(100, 100, 100))
            img = Image.new(
                "RGBA", (text_width, text_height), color=(255, 255, 255)
            )
            draw = ImageDraw.Draw(img)
            draw.text((x_off, y_off), line, font=font, fill=(0, 0, 0))
            img = img.resize((box.w, box.h))

            self.image.paste(img, (box.x, box.y))
        Logs.dev(f"Pytesseract, putting text on image finished")

    def _compute_src_pars(self) -> None:
        self.pars_info = []
        if _empty(self.src_text):
            return
        pars = self.src_text.split("\n\n")
        for par in pars:
            self.pars_info.append(par.split("\n"))
        total = self._lines_left(0)
        if total != len(self.boxes):
            Logs.error(
                "Unexpected error in compute_src_pars: "
                "invalid number of lines. "
                f"total = {total}, len(self.boxes) = {len(self.boxes)}"
            )
            exit(111)

    def _lines_left(self, start_par_num: int) -> int:
        res = 0
        for i in range(start_par_num, len(self.pars_info)):
            res += len(self.pars_info[i])
        return res

    def _print_src_dict(self) -> None:
        msg = ""
        for attr in self.src_dict.keys():
            msg += f"{attr}: {self.src_dict[attr]}\n"
        Logs.dev(msg)

    def _remove_extra_symbols(self) -> None:
        # remove leading extra words
        self._iterative_strip(0)

        # remove end extra words
        self._iterative_strip(-1)

        # print dict
        Logs.dev("Pytesseract, stripped text:")
        self._print_src_dict()

        # remove extra whitespaces
        last_new_line = -1
        i = 0
        while i < len(self.src_dict["text"]) - 1:
            i += 1
            word = self.src_dict["text"][i]
            if last_new_line != -1:
                if _is_strip(word):
                    continue
                if i > last_new_line + 1:
                    self.src_dict["text"][last_new_line + 1] = ""
                    while i > last_new_line + 2:
                        i -= 1
                        self._delete_dict_item(i)
                last_new_line = -1
            elif _empty(word):
                last_new_line = i

    def _try_add_context(self) -> None:
        Logs.dev("Pytesseract, try add context")
        self.context_added = (
            self.save_context
            and not _empty(self.context)
            and not _empty(self.src_text)
        )
        if self.context_added:
            Logs.dev(f"Pytesseract, adding context: {self.context}")
            self.src_text = self.context + "\n" + self.src_text

    def _try_remove_context(self, text: str) -> str:
        if not self.context_added:
            return text
        ind = text.find("\n")
        if ind == -1:
            Logs.error("Pytesseract, unexpected error: remove context failed")
            raise RuntimeError
        text = text[ind + 1 :]
        return text

    def _save_context(self):
        splitted = self.src_text.split("\n\n")
        par = splitted[-1]
        self.context = re.sub("\n", " ", par)
        if self.context.isnumeric():
            # Most likely this is the page number.
            if len(splitted) > 1:
                par = splitted[-2]
                self.context = re.sub("\n", " ", par)
            else:
                self.context = ""
        if self.context.find("\n") != -1:
            Logs.error("Pytesseract: unexpected error, context contains \\n")
            raise RuntimeError

    def _dict_is_empty(self):
        return len(self.src_dict["text"]) == 0

    def _iterative_strip(self, ind: int):
        if self._dict_is_empty():
            return
        word = self.src_dict["text"][ind]
        while not self._dict_is_empty() and _is_strip(word):
            self._delete_dict_item(ind)
            if self._dict_is_empty():
                return
            word = self.src_dict["text"][ind]

    def _delete_dict_item(self, ind: int):
        for attr in self.src_dict.keys():
            del self.src_dict[attr][ind]

    def _append_to_boxes(
        self,
        first_word_ind: int,
        words_in_line: int,
        accum_top_y: float,
        accum_bot_y: float,
    ) -> None:
        box = TesseractOCR.LineBox()
        # x
        box.x = self.src_dict["left"][first_word_ind]
        # w
        last_word_ind = first_word_ind + words_in_line - 1
        lxl = self.src_dict["left"][last_word_ind]
        lxw = self.src_dict["width"][last_word_ind]
        box.w = lxl + lxw - box.x
        # y
        box.y = int(accum_top_y / words_in_line)
        # h
        box.h = int(accum_bot_y / words_in_line - box.y)
        self.boxes.append(box)

    # Member fields
    max_new_line = 2

    search_lang: str
    image: Image.Image
    src_text: str
    trg_text: str
    src_dict: dict
    boxes: list[LineBox]
    font_path: str

    pars_info: list[list[str]]

    save_context: bool
    context_added: bool
    context: str
