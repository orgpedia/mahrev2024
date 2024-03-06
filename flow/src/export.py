import json
import shutil
import sys
from pathlib import Path

docs_dir = Path(sys.argv[1])
task_dir = Path(sys.argv[2])
export_dir = Path(sys.argv[3])

task_output_dir = task_dir / "output"

import_infos = json.loads((docs_dir / "documents.json").read_text())
export_json_file = export_dir / "GRs.json"
export_infos = json.loads(export_json_file.read_text()) if export_json_file.exists() else []

export_codes = set(i["Unique Code"] for i in export_infos)

new_infos = [i for i in import_infos if i["Unique Code"] not in export_codes]
print(f"New codes: {len(new_infos)}")

new_export_infos = []
for info in new_infos:
    code = info["Unique Code"]

    en_file = task_output_dir / f"{code}.pdf.en.txt"
    mr_file = task_output_dir / f"{code}.pdf.mr.txt"

    doc_file = task_output_dir / f"{code}.pdf.doc.json"

    if mr_file.exists() and en_file.exists():
        json_doc = json.loads(doc_file.read_text())
        order_number_dict = json_doc.get('order_number', None)
        
        shutil.copyfile(en_file, export_dir / en_file.name)
        shutil.copyfile(mr_file, export_dir / mr_file.name)
        
        info["mr_file"] = mr_file.name
        info["en_file"] = en_file.name
        if order_number_dict:
            info['order_number'] = order_number_dict['order_number']
            info['order_type'] = order_number_dict['order_type']            
        else:
            info['order_number'] = None
            info['order_type'] = None
        info["status"] = "exported"
    else:
        continue
    new_export_infos.append(info)

if new_export_infos:
    export_json_file.write_text(json.dumps(export_infos + new_export_infos))
