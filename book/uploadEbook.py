import logging
import os
import uuid
from pathlib import Path
import boto3
from ebooklib import epub
from book.models import *
from book import *


class S3Uploader:
    def __init__(self):
        """
        初始化S3客户端对象

        Args:
            aws_region: AWS服务所在的区域
            aws_access_key_id: AWS访问密钥ID
            aws_secret_access_key: AWS访问密钥
            bucket_name: S3存储桶名称
        """
        self.aws_region = "ap-northeast-1"
        self.aws_access_key_id = "AKIARHTH3MTSG55OAIHS"
        self.aws_secret_access_key = "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"
        self.bucket_name = "ebookshare"

        self.s3 = boto3.client('s3',
                               region_name=self.aws_region,
                               aws_access_key_id=self.aws_access_key_id,
                               aws_secret_access_key=self.aws_secret_access_key)

    def upload_file(self, local_file, key_name=None):
        """
        将本地文件上传到S3存储桶中

        Args:
            local_path: 本地文件路径
            key_name: S3对象键名

        Returns:
            None
        """
        try:
            # 使用uuid生成唯一文件名
            filename = str(uuid.uuid4()).replace("-", "") + Path(local_file).suffix
            # 上传文件到S3
            if key_name is None:
                descFile = filename
            else:
                descFile = key_name + "/" + filename
            self.s3.upload_file(local_file, self.bucket_name, descFile)
            logging.info(f"File uploaded to S3: {local_file} ,desc: {descFile}")
            return {"filename": filename, "url": descFile}
        except Exception as e:
            logging.exception("Error uploading file to S3:{}".format(e))
            return None

class getBookInfo:
    def __init__(self, bookFile):
        self.file = bookFile
        self.bookType = ['epub', 'mobi', 'txt', 'pdf', 'azw3']

    def return_res(self, title=None,authors=None,publisher=None):
        if title is None and authors is None and publisher is None :
            return { "title": "", "authors": "", "publisher": ""}
        else:
            return {"title": title,"authors": authors,"publisher": publisher}

    def epubInfo(self):
        # 打开epub文件
        if not os.path.exists(self.file):
            return None
        # 获取作者信息
        try:
            # book = epub.read_epub(self.file)
            book = epub.read_epub(self.file)

            try:
                creator = book.get_metadata("DC",'creator')[0][0]
            except Exception as e:
                logging.error(e)
            authors = creator if creator else None

            if len(book.get_metadata("DC", "publisher")) > 0:
                publisher = book.get_metadata("DC", "publisher")[0][0]
            return self.return_res(book.title, authors, publisher)
        except Exception as e:
            logging.error(e)
            return self.return_res("", "", "")

    def txt_info(self):
        fileType = str(Path(self.file).suffix)
        title = os.path.basename(self.file).replace(fileType, "")
        return self.return_res(title)

    def mobi_info(self):
        from calibre.ebooks import Metadata

        # 打开Mobi电子书文件
        with open('/Users/benben/Downloads/卢瑟经济学_MRandson.mobi', 'rb') as mobi_file:
            # 解析Mobi文件的元数据
            mobi_metadata = Metadata.from_book(mobi_file.read(), 'MOBI')

            # 获取书名信息
            book_title = mobi_metadata.title

            # 获取作者信息
            author = mobi_metadata.author

            # 获取发布时间信息
            date = mobi_metadata.timestamp

            # 获取作者信息
            author = mobi.author
        return self.return_res(title , author,"")

    def azw3_info(self):
        import pykindle
        # 打开azw3电子书文件
        with open('path/to/your/azw3/file.azw3', 'rb') as azw3_file:
            # 解析azw3文件的元数据
            azw3 = pykindle.KindleBook(azw3_file.read())

            # 获取书名信息
            book_title = azw3.title

            # 获取作者信息
            author = azw3.author

            # 获取出版社信息
            publisher = azw3.publisher

            # 打印信息
            print(f"书名信息：{book_title}")
            print(f"作者信息：{author}")
            print(f"出版社信息：{publisher}")

    def bookInfo(self):
        if os.path.exists(self.file):
            file_type = str(Path(self.file).suffix).lower()
            if file_type in self.bookType:
                if file_type == 'epub':
                    return self.epubInfo()
                elif file_type == 'txt':
                    return self.txt_info()
                elif file_type == 'mobi':
                    return self.return_res()
                elif file_type == 'azw3':
                    return self.return_res()
                else:
                    return self.return_res()
        else:
            return self.return_res()


def list_all_files(rootdir):
    """
    列出文件夹下所有的目录与文件
    :param rootdir: 根路径
    :return:
    """
    _files = []
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isdir(path):
            _files.extend(list_all_files(path))
        if os.path.isfile(path):
            _files.append(path)
    return _files

if __name__ == '__main__':
    # local_file = '/Users/benben/Documents/电子书/平凡的世界.mobi'

    with app.app_context():
        db.init_app(app)
        for file in list_all_files('/Users/benben/Documents/电子书/'):
            if str(Path(file).suffix) == '.mobi':
                book_name = str(os.path.basename(file)).replace(".mobi", "").replace(" ","")
                print(str(os.path.basename(file)).replace(".mobi", ""))
                # if Books.query.filter(Books.title == book_name).first() is not None:
                #     continue
                # book = Books()
                # book.title = book_name
                # book.author = ''
                # book.status = 1
                # book.filesize = os.path.getsize(file)
                # s3Upload = S3Uploader()
                # remote_key = time.strftime("%Y%m%d", time.localtime())
                # s3res = s3Upload.upload_file(local_file=file,key_name=remote_key)
                # bookurl = Bookurl()
                # bookurl.book_id = book.id
                # bookurl.book_download_url = s3res['url']
                #
                # book.bookext = bookurl
                # db.session.add(bookurl)
                # db.session.add(book)
                # db.session.commit()
        # print(book.bookext)
        # print(bookurl.book_download_url)
        # res = Books.query.filter(Books.title == '平凡的世界').first()
        # print(res)


