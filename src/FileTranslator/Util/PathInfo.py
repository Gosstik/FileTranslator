import os
from tempfile import TemporaryDirectory

import FileTranslator.Util.Logs as Logs
from FileTranslator.Util.TranslateInfo import TranslateInfo

################################################################################


supported_src_extensions = ["pdf"]
supported_trg_extensions = ["pdf"]

################################################################################


def _autodetect_extension(path: str) -> str:
    # Get src file name and remove extension if it exists
    src_name = os.path.basename(path).split(".")
    if len(src_name) == 1 or src_name[-1] not in supported_src_extensions:
        Logs.error(
            f"Unable to auto detect language for file '{path}'. "
            "Specify it explicitly with -e option. "
            "Currently supported formats: "
            f"{supported_src_extensions}"
        )
        raise RuntimeError
    else:
        return src_name[-1]


################################################################################


class PathInfo:
    def __init__(self, main_file: str):
        self.package_dir = os.path.dirname(main_file)
        self.data_dir = os.path.join(self.package_dir, "data")
        self.fonts_dir = os.path.join(self.data_dir, "fonts")
        self.fake_text_path = os.path.join(self.data_dir, "FakeText.txt")
        self.tmp_dir_obj = TemporaryDirectory()
        self.tmp_dir = self.tmp_dir_obj.name
        self.source_extension = self.target_extension = ""
        self.logs_path = os.path.join(self.package_dir, ".logs")
        self.is_release_path = os.path.join(self.package_dir, ".is_release")

    def set_source_file_info(self, path: str, extension: str | None):
        self.source_file_path = os.path.abspath(path)
        if extension is None:
            self.source_extension = _autodetect_extension(self.source_file_path)
        elif extension not in supported_src_extensions:
            Logs.error(
                "Source file format is not supported. "
                "Currently supported formats: "
                f"{supported_src_extensions}"
            )
        else:
            self.source_extension = extension

    def set_target_file_info(
        self,
        path: str,
        trg_lang: str,
        extension: str | None,
        translate_info: TranslateInfo,
    ):
        if extension is not None and extension not in supported_trg_extensions:
            Logs.error(
                f"'{extension}' extension is not supported for "
                "target files. Supported target file extensions: "
                f"{supported_trg_extensions}"
            )
        if extension is None:
            extension = self.source_extension

        if len(path) == 0:
            # Path was not specified in arguments

            dir_name = os.path.dirname(self.source_file_path)

            # Get src file name and remove extension if it exists
            src_name = os.path.basename(self.source_file_path).split(".")
            if len(src_name) == 1 or self.source_extension != src_name[-1]:
                src_name = src_name[0]
            else:
                src_name = ".".join(src_name[:-1])

            if translate_info.entire_file_to_translate():
                name = f"{src_name}.{trg_lang}.{extension}"
            else:
                first = translate_info.first_page
                last = translate_info.last_page
                name = f"{src_name}.{first}-{last}.{trg_lang}.{extension}"
            self.target_file_path = os.path.join(dir_name, name)
        else:
            self.target_file_path = os.path.abspath(path)
        self.target_extension = extension

    def get_image_path(self, i: int, translated: bool):
        if translated:
            return f"{self.tmp_dir}/{i}.translated.png"
        return f"{self.tmp_dir}/{i}.png"

    def get_single_file_path(self, index: int) -> str:
        return f"{self.tmp_dir}/{index}.{self.target_extension}"

    # set by __init__
    package_dir: str
    data_dir: str
    fonts_dir: str
    fake_text_path: str
    tmp_dir_obj: type(TemporaryDirectory)
    tmp_dir: str
    logs_path: str
    is_release_path: str

    # set by program args
    source_file_path: str
    source_extension: str
    target_file_path: str
    target_extension: str


################################################################################


def get_image_path(i: int, translated: bool, path_info: PathInfo):
    if translated:
        return f"{path_info.tmp_dir}/{i}.translated.png"
    return f"{path_info.tmp_dir}/{i}.png"
