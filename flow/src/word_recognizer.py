import json
from pathlib import Path

from docint.page import Page
from docint.pdfwrapper import open as pdf_open
from docint.pipeline.tess_recognizer import add_words_to_page
from docint.vision import Vision


def add_text_from_word_image(page_image, word, lang_str):
    import pytesseract

    word_image = Page.get_base64_image_from_pil(page_image, word.shape, height=100)
    text = pytesseract.image_to_string(word_image, lang=lang_str, config="--psm 7")
    word.text_ = text.strip()
    return word.text_


TessCutoff = 10  # Number of unmatched words for it to use recognizer


@Vision.factory(
    "word_recognizer",
    depends=["pytesseract", "apt:tesseract-ocr-all"],
    is_recognizer=True,
    default_config={
        "output_dir_path": "output",
        "output_stub": "word_recognizer",
        "languages": ["eng", "mar"],
    },
)
class WordRecognizer:
    def __init__(self, output_dir_path, output_stub, languages):
        self.output_dir_path = Path(output_dir_path)
        self.languages = languages
        self.output_stub = output_stub

    def __call__(self, doc):
        #print(f"Processing word_recognizer {doc.pdf_name}")

        json_path = self.output_dir_path / f"{doc.pdf_name}.{self.output_stub}.json"
        if json_path.exists():
            word_infos = json.loads(json_path.read_text())
            for page_idx, word_idx, text in word_infos:
                doc.pages[page_idx][word_idx].text_ = text
            return doc

        pdf = pdf_open(Path("input") / doc.pdf_name)

        word_infos, full_page_extract = [], False
        for page, pdf_page, info in zip(doc.pages, pdf.pages, doc.cid_info["page_infos"]):
            num_cids = sum(c for (f, c) in info["font_word_counts"].items() if f != "sakalmarathi")

            if num_cids > TessCutoff or pdf_page.has_one_large_image:
                print(f'\tTesseract on page: {page.page_idx}')
                full_page_extract = True
                page.words.clear()
                add_words_to_page(page, pdf_page, ["eng", "mar"])
            else:
                page_image = None
                for word in [w for w in page.words if "-cid:" in w.text]:
                    if page_image is None:
                        page_image = pdf_page.page_image_to_pil(dpi=600)

                    print(f"\tReplaced {page.page_idx}:{word.word_idx} >{word.text}< ", end=" ")
                    text = add_text_from_word_image(page_image, word, "mar+eng")
                    print(f">{text}<")
                    word_infos.append([page.page_idx, word.word_idx, word.text_])
        # end for

        if not full_page_extract:
            json_path.write_text(json.dumps(word_infos))
        return doc
