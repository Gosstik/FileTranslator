import argparse

import FileTranslator.Util.Logs as Logs
from FileTranslator.Util.PathInfo import PathInfo
from FileTranslator.Util.TranslateInfo import TranslateInfo

################################################################################


def parse_args(path_info: PathInfo, translate_info: TranslateInfo) -> None:
    Logs.user("Parsing arguments")
    parser = argparse.ArgumentParser(
        prog="translate_file",
        description="Utility to translate files to different languages",
    )

    parser.add_argument(
        "-s",
        "--source-path",
        required=True,
        type=str,
        help="absolute or relative path to file to translate",
    )
    parser.add_argument(
        "-e",
        "--extension",
        required=False,
        type=str,
        help="extension of source file",
    )
    parser.add_argument(
        "-c",
        "--current-language",
        required=True,
        type=str,
        help="language of source file",
    )
    parser.add_argument(
        "-d",
        "--desired-language",
        required=True,
        type=str,
        help="language of translated file",
    )
    parser.add_argument(
        "-f",
        "--first",
        required=False,
        type=int,
        help="page number, from which translation begins",
    )
    parser.add_argument(
        "-l",
        "--last",
        required=False,
        type=int,
        help="page number, where translation ends",
    )
    parser.add_argument(
        "-g",
        "--font",
        required=False,
        type=str,
        default="arial.ttf",
        help="name of file with font located in 'fonts' folder",
    )
    parser.add_argument(
        "-m",
        "--save-context",
        required=False,
        type=bool,
        default=True,
        help="try to save context of previous pages",
    )
    parser.add_argument(
        "-t",
        "--target-path",
        required=False,
        type=str,
        default="",
        help="absolute or relative path to translated file",
    )
    # TODO: choose ocr and translator
    args = parser.parse_args()

    # source_path, extension
    path_info.set_source_file_info(args.source_path, args.extension)
    # current_language, desired_language
    translate_info.set_languages(args.current_language, args.desired_language)
    # first, last
    translate_info.set_pages_count(
        path_info.source_file_path, path_info.source_extension
    )
    translate_info.set_pages_range(args.first, args.last)
    # font
    translate_info.set_font(path_info.fonts_dir, args.font)
    # save_context
    translate_info.save_context = args.save_context
    # target_path
    path_info.set_target_file_info(
        args.target_path, args.desired_language, args.extension, translate_info
    )
    Logs.user("Parsing arguments finished")
