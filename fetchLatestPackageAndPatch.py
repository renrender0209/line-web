import re
import requests
import shutil
import struct
import os

def patch():
    # targets
    target_main = "www/static/js/main.js"
    target_ltsm = "www/static/js/ltsmSandbox.js"

    # patch patterns
    originPatchPatterns = [
            [r'window.origin', r'"chrome-extension://ophjlpahpchlmihnnnihgmmeilfjmjjc"'],
            [r'window.location.origin', r'"chrome-extension://ophjlpahpchlmihnnnihgmmeilfjmjjc"'],
            [r'location.origin', r'"chrome-extension://ophjlpahpchlmihnnnihgmmeilfjmjjc"']
    ]
    corsPatchPatterns = [
            [r'"https://ci.line-apps.com/R4"', r'`${location.origin}/_proxy/R4`'],
            [r'"line-chrome-gw.line-apps.com"', r'`${location.host}/_proxy/CHROME_GW`']
    ]

    # load main
    with open(target_main, "r", encoding="utf-8") as f:
        content_main = f.read()

    # load ltsm
    with open(target_ltsm, "r", encoding="utf-8") as f:
        content_ltsm = f.read()

    # patch origin
    for pattern in originPatchPatterns:
        print(pattern)
        content_ltsm = re.sub(pattern[0], pattern[1], content_ltsm)

    # patch cors proxy
    for pattern in corsPatchPatterns:
        print(pattern)
        content_main = re.sub(pattern[0], pattern[1], content_main)
        content_ltsm = re.sub(pattern[0], pattern[1], content_ltsm)

    # save main
    with open(target_main, "w", encoding="utf-8") as f:
        f.write(content_main)

    # save ltsm
    with open(target_ltsm, "w", encoding="utf-8") as f:
        f.write(content_ltsm)


def fetchPackage():
    extension_id = 'ophjlpahpchlmihnnnihgmmeilfjmjjc'
    dir_path = 'www'
    crx_url = f'https://clients2.google.com/service/update2/crx?response=redirect&prodversion=103.0.1264.77&acceptformat=crx3&x=id%3D{extension_id}%26installsource%3Dondemand%26uc'

    headers = {
        'User-Agent': 'Mozilla/5.0',
    }

    response = requests.get(crx_url, headers=headers, allow_redirects=True)

    with open(f'{extension_id}.zip', 'wb') as f:
        response = requests.get(crx_url, headers=headers, allow_redirects=True)
        crx_data = response.content
        zip_data = crx_data[(struct.unpack('<I', crx_data[8:12])[0] + 12):]
        f.write(crx_data)

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    shutil.unpack_archive(f'{extension_id}.zip', dir_path)


fetchPackage()
patch()
