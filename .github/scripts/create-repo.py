#!/usr/bin/env python3
"""Build the Mihon/Tachiyomi repo index (index.min.json / index.json) + icons.

Unlike the anime repo this needs no aapt: every assembleRelease emits a
`keiyoushi-source-info.json` next to its APK with the full metadata, and the
launcher icon is already in the extension's own `res/mipmap-xxxhdpi`.

Expects:
  - APK artifacts already moved into ./apk/
  - The matching source-info files collected into ./source-info/
"""

import json
import shutil
from pathlib import Path

REPO_DIR = Path(".")
APK_DIR = REPO_DIR / "apk"
ICON_DIR = REPO_DIR / "icon"
INFO_DIR = REPO_DIR / "source-info"
SRC_DIR = REPO_DIR / "src"
MULTISRC_DIR = REPO_DIR / "lib-multisrc"

ICON_PATH = "res/mipmap-xxxhdpi/ic_launcher.png"

ICON_DIR.mkdir(parents=True, exist_ok=True)

index_data = []

for info_file in sorted(INFO_DIR.glob("*.json")):
    with info_file.open(encoding="utf-8") as f:
        info = json.load(f)

    package_name = info["packageName"]
    module = info["module"]  # e.g. "ru.readmanga"
    lang = module.split(".")[0]

    apk = APK_DIR / f"tachiyomi-{module}-v{info['versionName']}.apk"
    if not apk.exists():
        matches = sorted(APK_DIR.glob(f"*{module.replace('.', '-')}*.apk")) or sorted(
            APK_DIR.glob(f"*{module.split('.')[-1]}*.apk")
        )
        if not matches:
            raise FileNotFoundError(f"{package_name}: no apk found for module {module}")
        apk = matches[0]

    # The extension's own icon, else its theme's, else the shared default.
    candidates = [SRC_DIR / module.replace(".", "/") / ICON_PATH]
    if info.get("theme"):
        candidates.append(MULTISRC_DIR / info["theme"] / ICON_PATH)
    candidates.append(REPO_DIR / "core/src/main" / ICON_PATH)

    icon = next((p for p in candidates if p.exists()), None)
    if icon is None:
        raise FileNotFoundError(f"{package_name}: no launcher icon found")
    shutil.copyfile(icon, ICON_DIR / f"{package_name}.png")

    # Proto ContentWarning: UNSPECIFIED=0, SAFE=1, MIXED=2, NSFW=3.
    nsfw = 1 if info.get("contentWarning", 0) == 3 else 0

    index_data.append(
        {
            "name": info["name"],
            "pkg": package_name,
            "apk": apk.name,
            "lang": lang,
            "code": info["versionCode"],
            "version": info["versionName"],
            "nsfw": nsfw,
            "sources": [
                {
                    "name": source["name"],
                    "lang": source["lang"],
                    "id": str(source["id"]),
                    "baseUrl": source["baseUrl"],
                }
                for source in info.get("sources", [])
            ],
        }
    )

index_data.sort(key=lambda x: x["name"])

with REPO_DIR.joinpath("index.min.json").open("w", encoding="utf-8") as f:
    json.dump(index_data, f, ensure_ascii=False, separators=(",", ":"))

with REPO_DIR.joinpath("index.json").open("w", encoding="utf-8") as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Indexed {len(index_data)} extension(s):")
for entry in index_data:
    print(f"  {entry['name']} {entry['version']} ({entry['pkg']}) sources={len(entry['sources'])}")
