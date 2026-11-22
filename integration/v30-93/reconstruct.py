#!/usr/bin/env python3
"""Reconstruct V30.93 sources from the existing V30.89 ZIP and versioned patch."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import base64, zlib, json, hashlib

root = Path(__file__).resolve().parents[2]
base = root / "JawaliWallet_Android_V30_89_Source.zip"
out = root / "JawaliWallet_Android_V30_93_Source.zip"
patch_file = root / "integration/v30-93/patch.b64"
if not base.exists():
    raise SystemExit("V30.89 baseline missing; refusing to create a wrong V30.93 archive")
encoded = ''.join(patch_file.read_text(encoding='ascii').split())
patch = json.loads(zlib.decompress(base64.b64decode(encoded)))
seen = set()
with ZipFile(base) as old, ZipFile(out, "w", ZIP_DEFLATED) as new:
    for info in old.infolist():
        if info.is_dir():
            continue
        suffix = info.filename.split("/", 1)[-1]
        data = old.read(info)
        if suffix in patch:
            base_lines = data.decode("utf-8").splitlines(keepends=True)
            data = ''.join(''.join(base_lines[p[1]:p[2]]) if p[0] == '=' else p[1] for p in patch[suffix]).encode("utf-8")
        new.writestr("JawaliWallet_Android_V30_93/" + suffix, data)
        seen.add(suffix)
    for suffix in patch:
        if suffix not in seen:
            data = ''.join(item[1] for item in patch[suffix] if item[0] == '+').encode("utf-8")
            new.writestr("JawaliWallet_Android_V30_93/" + suffix, data)
with ZipFile(out) as z:
    assert z.testzip() is None
    assert "JawaliWallet_Android_V30_93/app/src/main/assets/jawali-live.js" in z.namelist()
    assert "JawaliWallet_Android_V30_93/app/build.gradle" in z.namelist()
print("Reconstructed:", out.name, out.stat().st_size, "bytes")
