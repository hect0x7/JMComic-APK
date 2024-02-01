import os
import re

from jmcomic import create_option, JmHtmlClient, JmApiClient, \
    PatternTool, file_exists, write_text, read_text, \
    save_resp_content

apk_version_txt = './APK_VERSION.txt'
is_dev: bool = file_exists('.idea')
cur_ver: str = read_text(apk_version_txt).strip()
op = create_option('op.yml')
html_cl: JmHtmlClient = op.new_jm_client(impl='html')
api_cl: JmApiClient = op.new_jm_client(impl='api')


def add_output(k, v):
    if is_dev:
        return

    cmd = f'echo "{k}={v}" >> $GITHUB_OUTPUT'
    print(f'{cmd}: {os.system(cmd)}')


def download_new_ver(new_ver, download_path):
    resp = html_cl.get(download_path)
    save_resp_content(resp, f'./{new_ver}.apk')
    write_text(apk_version_txt, new_ver)


def check_apk():
    # new_ver, download_path = fetch_apk_ver_and_download_path()
    new_ver, download_path, desc = fetch_apk_info_via_api()
    add_output('new_ver', new_ver)

    if new_ver <= cur_ver:
        add_output('found_new', 'false')
        return

    add_output('found_new', 'true')
    add_output('download_path', download_path)
    add_output('desc', desc.replace('\n', '<p>'))
    download_new_ver(new_ver, download_path)


def fetch_apk_info_via_html():
    resp = html_cl.get_jm_html('/stray/?utm_source=18comic')
    apk_version_pattern = re.compile(r'a href="(/static/apk/(.*?).apk)"')
    match = PatternTool.require_match(resp.text, apk_version_pattern, '未匹配上apk下载路径', None)
    download_path, new_ver = match[1], match[2]
    return new_ver, download_path


def fetch_apk_info_via_api():
    resp = api_cl.setting()
    data = resp.model_data

    version = data.version
    return version, f'/static/apk/{version}.apk', data.version_info


if __name__ == '__main__':
    check_apk()
