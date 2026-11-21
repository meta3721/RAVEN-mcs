#!/usr/bin/env python3
from __future__ import annotations
import shutil, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/"artifacts/e3_local_hajek_weight_and_p2_certificate_final_closure_r1"; ZIP=ROOT/"deliverables/TO_SUBMIT_E3_LOCAL_HAJEK_WEIGHT_AND_P2_CERTIFICATE_FINAL_CLOSURE_R1.zip"
def main():
    ZIP.parent.mkdir(exist_ok=True)
    if ZIP.exists(): ZIP.unlink()
    with zipfile.ZipFile(ZIP,"w",zipfile.ZIP_DEFLATED) as z:
        for p in ART.rglob("*"):
            if p.is_file(): z.write(p,f"{ART.name}/{p.relative_to(ART).as_posix()}")
    print(ZIP)
if __name__=="__main__": main()
