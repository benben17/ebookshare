import uuid
import boto3
from book import *
from book.utils import *

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

def bookInfo(filepath):

    import subprocess
    metadata = {
        "title": None,
        "author": "",
        "language": "",
        "publisher": "",
        "filesize" : 0
    }
    try:
        command = '/Applications/calibre.app/Contents/MacOS/ebook-meta'
        # file_path = '/Users/benben/Documents/电子书/纸牌大厦++卢瑟经济学之21世纪金融危机.pdf'

        # Run command using subprocess
        res = subprocess.run([command, filepath], capture_output=True, text=True)
        # print(res.stdout.split('\n'))
        for line in res.stdout.split('\n'):
            line = line.strip()
            if "Title" in line:
                metadata['title'] = line.split(":")[1].strip()
            elif "Author" in line:
                metadata['author'] = line.split(":")[1].strip()
            elif "Languages" in line:
                file_ext = line.split(":")[1].strip()
                metadata['language'] = file_ext
            elif "Publisher" in line:
                metadata['publisher'] = line.split(":")[1].strip()

        if metadata['title'] is None:
            metadata['title'] = get_file_name(filepath)
        if "/" in metadata['title']:
            metadata['title'] = metadata['title'].replace("/",'-')
        metadata['filesize'] = os.path.getsize(filepath)
        metadata['extension'] = get_file_suffix(filepath)
        if metadata['extension'].lower() == 'pdf':
            metadata['title'] = get_file_name(filepath)

        return metadata
    except Exception as e:
        print(e)
        # logging.error(filepath+e)
        return None

def list_all_files(rootdir, max_depth=10, max_files=None):
    """
    列出文件夹下所有的目录与文件
    :param rootdir: 根路径
    :param max_depth: 最大遍历深度，默认为10层
    :param max_files: 最大遍历文件数量，默认为None，表示不限制
    :return: 文件列表
    """
    files = []
    stack = [(rootdir, 0)]  # 使用栈保存文件夹和遍历深度
    while stack:
        path, depth = stack.pop()
        if os.path.isfile(path):
            files.append(path)
        elif os.path.isdir(path):
            if depth < max_depth:
                for name in os.listdir(path):
                    child_path = os.path.join(path, name)
                    stack.append((child_path, depth + 1))
                    if max_files and len(files) >= max_files:
                        return files
    return files

if __name__ == '__main__':

    # authors = metadata.authors
    # title = metadata.title
    # isbn = metadata.isbn
    # print(authors, title, isbn)
    # with app.app_context():
    #     db.init_app(app)
    for file in list_all_files('/Users/benben/Downloads/P001核对完/'):
        if get_file_name(file) == ".DS_Store":
            continue
        if allowed_ebook_ext(file):
            print(bookInfo(file))
        # print(file)
    #             book_name = str(os.path.basename(file)).replace(".mobi", "").replace(" ","")
    #             print(str(os.path.basename(file)).replace(".mobi", ""))
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
    # with app.app_context():
    #     res = Books.query.filter(Books.title == '平凡的世界').first()
    #     print(res)



    # Print metadata
