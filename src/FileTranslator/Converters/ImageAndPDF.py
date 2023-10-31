from typing import Callable

from pdf2image import convert_from_path
from PIL import Image

import FileTranslator.Util.Logs as Logs

################################################################################


def split_pdf_into_images(pdf_path: str) -> list[Image]:
    Logs.user(f'Splitting "{pdf_path}" to images')
    images = convert_from_path(pdf_path)
    Logs.user(f"Splitting finished")
    return images


def merge_images_into_pdf(
    images: list[str] | list[Image], pdf_path: str
) -> None:
    Logs.user(f"Converting images to pdf")
    image_count = len(images)
    if image_count == 0:
        Logs.warning("No images to merge into pdf")
        return
    if images is list[str]:
        image_list = [Image.open(fp=images[i]) for i in range(image_count)]
    else:
        image_list = images
    image_list[0].save(fp=pdf_path, save_all=True, append_images=image_list[1:])
    Logs.user(f"Converting images to pdf finished. Path to pdf: {pdf_path}")


# def convert_image_to_pdf(img_path: str, pdf_path: str) -> None:
#     pdf_bytes = img2pdf.convert(img_path)
#     open(pdf_path, "wb").write(pdf_bytes)


# def merge_pdfs(src_pdf_paths: list[str], trg_pdf_path: str):
#     program_log(f'Merging pdf\'s. Path to pdf: "{trg_pdf_path}"')
#     pdf_writer = PdfFileWriter()
#     for path in src_pdf_paths:
#         pdf_reader = PdfFileReader(path)  # strict = False
#         pdf_writer.addPage(pdf_reader.getPage(0))
#
#     # Write out the merged PDF
#     with open(trg_pdf_path, 'wb') as out:
#         pdf_writer.write(out)
#
#     program_log(f'Merging pdf\'s finished. Path to pdf: "{trg_pdf_path}"')
