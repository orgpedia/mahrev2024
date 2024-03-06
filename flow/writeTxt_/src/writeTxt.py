import sys
from pathlib import Path

import docint  # noqa
import orgpedia  # noqa
import word_recognizer  # noqa

def order_num(pdf_path):
    return int(pdf_path.stem)

if __name__ == "__main__":
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    viz = docint.load("src/writeTxt.yml")

    if input_path.is_dir():
        assert output_path.is_dir()
        input_files = sorted(input_path.glob("*.pdf"), key=order_num)
        print(len(input_files))

        # docs = viz.pipe_all(input_files[:3])
        docs = viz.pipe_all(input_files)

        for doc in docs:
            output_doc_path = output_path / (doc.pdf_name + ".doc.json")
            doc.to_disk(output_doc_path)
        print(f'#docs: {viz.total_docs} #processed: {viz.total_docs - viz.unprocessed_docs}')
    elif input_path.suffix.lower() == ".pdf":
        doc = viz(input_path)
        doc.to_disk(output_path)

    elif input_path.suffix.lower() in (".list", ".lst"):
        print("processing list")
        input_files = input_path.read_text().split("\n")

        pdf_files = [Path("input") / f for f in input_files if f and f[0] != "#"]
        pdf_files = [p for p in pdf_files if p.exists()]

        docs = viz.pipe_all(pdf_files)
        for doc in docs:
            output_doc_path = output_path / (doc.pdf_name + ".doc.json")
            doc.to_disk(output_doc_path)
