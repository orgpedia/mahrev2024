import base64
import datetime
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import requests

DeptName = "Revenue and Forest Department"


def request_pdf(url, pdf_file):
    downloaded, dt_str = False, None
    try:
        print(f"Downloading {url}")
        r = requests.get(url)
        if r.status_code == 200:
            with pdf_file.open("wb") as f:
                f.write(r.content)
            downloaded = True
            dt_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z%z")
        else:
            print(f"An error occurred while downloading {url} Status: {r.status_code}")
    except Exception as e:
        print(f"An exception occurred while downloading {url}: {e}")

    time.sleep(2)
    return downloaded, dt_str


def main():
    all_info_path = Path(sys.argv[1])
    doc_info_path = Path(sys.argv[2])
    link_dir = Path(sys.argv[3])

    assert link_dir.exists()

    all_infos = json.loads(all_info_path.read_text())
    dept_infos = [i for i in all_infos if i["Department Name"] == DeptName]

    doc_infos = json.loads(doc_info_path.read_text()) if doc_info_path.exists() else []
    doc_set = set(i["Unique Code"] for i in doc_infos)
    doc_dir = doc_info_path.parent

    new_infos = [i for i in dept_infos if i["Unique Code"] not in doc_set]

    for info in new_infos:
        doc_path = doc_dir / f"{info['Unique Code']}.pdf"

        status, dt_str = request_pdf(info["Download"], doc_path)
        if not status and info["archive"]["status"]:
            archive_status, dt_str = request_pdf(info["archive"]["url"], doc_path)
            if not archive_status:
                info["status"] = "not_downloaded"
                continue
        else:
            info["status"] = "downloaded"

        if info["wayback"]["status"]:
            h = hashlib.sha1(open(doc_path, "rb").read())
            pdf_digest = base64.b32encode(bytearray(h.digest())).decode("utf-8")
            info["status"] = "verified" if pdf_digest == info["wayback"]["sha1"] else "unverified"
        else:
            print(f'Wayback not found {info["Unique Code"]}')

        tgt_path = link_dir / doc_path.name
        src_path = os.path.relpath(str(doc_path), start=str(link_dir))

        tgt_path.symlink_to(src_path)
        doc_infos.append(info)

    doc_info_path.write_text(json.dumps(doc_infos))


main()
