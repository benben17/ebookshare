# encoding:utf-8
import hashlib
import time
import xml.etree.ElementTree as ET
from werkzeug.utils import secure_filename
import os
import config
from book import *
from book.models import *


@app.route('/')
def hello_world():  # put application's code here
    return config.APPID


@app.route('/api/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # 处理验证请求
        token = config.wechat_token
        echostr = request.args.get('echostr', '')
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        s = [timestamp, nonce, token]
        s.sort()
        s = ''.join(s)
        if signature == hashlib.sha1(s.encode('utf-8')).hexdigest():
            return echostr
        else:
            return ''
    else:
        # 处理消息请求

        xml_data = request.data
        root = ET.fromstring(xml_data)
        if root.find('MsgType').text == 'text':
            content = root.find('Content').text
        else:
            content = "欢迎关注我的公众号"

        from_user = root.find('FromUserName').text
        to_user = root.find('ToUserName').text
        create_time = str(int(time.time()))
        reply_xml = f"""
        <xml>
            <ToUserName><![CDATA[{from_user}]]></ToUserName>
            <FromUserName><![CDATA[{to_user}]]></FromUserName>
            <CreateTime>{create_time}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{content}]]></Content>
        </xml>
        """
        return reply_xml

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''