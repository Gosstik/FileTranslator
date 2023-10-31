from FileTranslator.OCR.IOCR import IOCR
from FileTranslator.OCR.TesseractOCR import TesseractOCR
import FileTranslator.Util.Logs as Logs
from FileTranslator.Util.PathInfo import PathInfo
from FileTranslator.Util.TranslateInfo import TranslateInfo

################################################################################


_ocr_map = {"tesseract": TesseractOCR()}

################################################################################


def get_ocr(path_info: PathInfo, translate_info: TranslateInfo) -> IOCR:
    alias = translate_info.ocr_alias
    if alias not in _ocr_map.keys():
        Logs.error(
            f"Incorrect ocr alias. Supported ocr and their aliases: {_ocr_map}"
        )
    ocr = _ocr_map[alias]
    ocr.init(path_info, translate_info)
    Logs.user(f"'{alias}' ocr constructed")
    return ocr
