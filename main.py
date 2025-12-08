import json
import os
import re

from jmcomic import create_option, JmHtmlClient, JmApiClient, \
    PatternTool, file_exists, write_text, read_text, \
    save_resp_content, JmModuleConfig, JmcomicText, jm_log

apk_version_txt = './APK_VERSION.txt'
is_dev: bool = file_exists('.idea')
cur_ver: str = read_text(apk_version_txt).strip()
JmModuleConfig.FLAG_API_CLIENT_REQUIRE_COOKIES = False
op = create_option('op.yml')
html_cl: JmHtmlClient = op.new_jm_client(impl='html')
api_cl: JmApiClient = op.new_jm_client(impl='api')


def compare_versions(v1: str, v2: str) -> int:
    parts1 = list(map(int, v1.split(".")))
    parts2 = list(map(int, v2.split(".")))

    # 补齐长度
    length = max(len(parts1), len(parts2))
    parts1 += [0] * (length - len(parts1))
    parts2 += [0] * (length - len(parts2))

    if parts1 > parts2:
        return 1  # v1 大
    elif parts1 < parts2:
        return -1  # v2 大
    else:
        return 0  # 相等

def add_output(k, v):
    cmd = f'echo "{k}={v}" >> $GITHUB_OUTPUT'
    if is_dev:
        print(cmd)
        return

    print(f'{cmd}: {os.system(cmd)}')


def download_new_ver(new_ver, download_path):
    resp = html_cl.get(download_path)
    save_resp_content(resp, f'./{new_ver}.apk')
    write_text(apk_version_txt, new_ver)


def check_apk():
    # new_ver, download_path = fetch_apk_ver_and_download_path()
    new_ver, download_path, desc = fetch_apk_info_via_api()
    add_output('new_ver', new_ver)

    if compare_versions(new_ver, cur_ver) < 1:
        add_output('found_new', 'false')
        return

    add_output('found_new', 'true')
    add_output('download_path1', f'{JmModuleConfig.PROT}18comic.vip{download_path}')
    add_output('download_path2', f'{JmModuleConfig.PROT}jmcomic.me{download_path}')
    add_output('desc', desc.replace('\r\n', '\n').replace('\n', '<p>'))
    download_new_ver(new_ver, download_path)


def fetch_apk_info_via_html():
    resp = html_cl.get_jm_html('/stray/?utm_source=18comic')
    apk_version_pattern = re.compile(r'a href="(/static/apk/(.*?).apk)"')
    match = PatternTool.require_match(resp.text, apk_version_pattern, '未匹配上apk下载路径', None)
    download_path, new_ver = match[1], match[2]
    return new_ver, download_path


def get_download_path(url):
    try:
        domain = JmcomicText.parse_to_jm_domain(url)
        return url.replace(JmModuleConfig.PROT, '').replace(domain, '')
    except Exception as e:
        jm_log('get_download_path', f'{e}: [{url}]')
        return url.replace(JmModuleConfig.PROT, '')


def fetch_apk_info_via_api():
    resp = api_cl.setting()
    jm_log('apk.setting', json.dumps(resp.res_data, indent=2, ensure_ascii=False))
    data = resp.model_data

    version = data.jm3_version
    return version, get_download_path(data.jm3_download_url), data.jm3_version_info


if __name__ == '__main__':
    check_apk()
