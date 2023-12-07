import os
import re

from jmcomic import create_option, JmHtmlClient, JmApiClient, \
    PatternTool, file_exists, write_text, read_text, \
    save_resp_content

apk_version_txt = './APK_VERSION.txt'
is_dev: bool = file_exists('.idea')
cur_ver: str = read_text(apk_version_txt).strip()
op = create_option('op.yml')
cl: JmHtmlClient = op.new_jm_client()


def add_output(k, v):
    if is_dev:
        return

    cmd = f'echo "{k}={v}" >> $GITHUB_OUTPUT'
    print(f'{cmd}: {os.system(cmd)}')


def download_new_ver(new_ver, download_path):
    resp = cl.get(download_path)
    save_resp_content(resp, f'./{new_ver}.apk')
    write_text(apk_version_txt, new_ver)


def check_apk():
    download_path, new_ver = fetch_apk_ver_and_download_path()
    # download_path, new_ver = fetch_apk_ver_and_download_path2()
    add_output('new_ver', new_ver)

    if new_ver <= cur_ver:
        add_output('found_new', 'false')
        return

    add_output('found_new', 'true')
    add_output('download_path', download_path)
    download_new_ver(new_ver, download_path)


def fetch_apk_ver_and_download_path():
    resp = cl.get_jm_html('/stray/?utm_source=18comic')
    apk_version_pattern = re.compile(r'a href="(/static/apk/(.*?).apk)"')
    match = PatternTool.require_match(resp.text, apk_version_pattern, '未匹配上apk下载路径', None)
    download_path, new_ver = match[1], match[2]
    return download_path, new_ver


def fetch_apk_ver_and_download_path2():
    app: JmApiClient = op.new_jm_client(impl=JmApiClient)
    resp = app.setting()
    data = resp.model_data

    return data.version, data.download_url


if __name__ == '__main__':
    check_apk()
