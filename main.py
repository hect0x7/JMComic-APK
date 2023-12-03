import os
import re

from jmcomic import JmOption, JmHtmlClient, PatternTool, \
    file_exists, write_text, read_text, \
    ProxyBuilder, save_resp_content

apk_version_txt = './APK_VERSION.txt'
is_dev: bool = file_exists('.idea')
cur_ver: str = read_text(apk_version_txt).strip()
# noinspection PyTypeChecker
cl: JmHtmlClient = (JmOption
                    .default()
                    .new_jm_client(impl=JmHtmlClient, proxies=ProxyBuilder.clash_proxy() if is_dev else None)
                    )


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
    resp = cl.get_jm_html('/stray/?utm_source=18comic')

    apk_version_pattern = re.compile(r'a href="/static/apk/(.*?).apk"')

    new_ver = PatternTool.require_match(resp.text, apk_version_pattern, '未匹配上apk下载路径')
    add_output('new_ver', new_ver)

    if new_ver <= cur_ver:
        add_output('found_new', 'false')
        return

    add_output('found_new', 'true')
    download_new_ver(new_ver, f'/static/apk/{new_ver}.apk')


if __name__ == '__main__':
    check_apk()
