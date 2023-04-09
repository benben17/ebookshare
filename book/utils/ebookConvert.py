import os
import subprocess

import config


def mobi_to_epub(mobi_file_path):
    """
    将mobi格式电子书转换为epub格式
    :param mobi_file_path: mobi文件的路径
    :return: epub文件的路径
    """
    # 获取mobi文件名和目录
    mobi_file_name = os.path.basename(mobi_file_path)
    # 生成epub文件路径
    epub_file_name = os.path.splitext(mobi_file_name)[0] + '.epub'
    epub_file_path = os.path.join(config.DOWNLOAD_DIR, epub_file_name)

    # 调用calibre进行转换
    command = f"ebook-convert {mobi_file_path} {epub_file_path}"
    try:
        status = subprocess.check_call(command, shell=True, stdout=subprocess.PIPE)
        if status == 0:
            return config.DOWNLOAD_URL + epub_file_name
        return "error"
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed with return code {e.returncode}.")
        return False

