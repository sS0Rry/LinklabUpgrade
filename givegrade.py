from flask import Flask, request, redirect, url_for, render_template
import os
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'handin'

# 确保handin目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

SRC_dir='src'
BOMBROOTdir='bombs'
@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return '没有文件上传'

    file = request.files['file']
    if file.filename == '':
        return '未选择文件'

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # 运行评分程序
    try:
        # 在这里指定你的评分脚本和参数
        command = ['python3', 'grade_linklab.py', filepath, BOMBROOTdir ,SRC_dir , 'file_grade']
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout

        return f'评分结果：<br>{output}'
    except Exception as e:
        return f'运行评分程序时出错：{e}'


if __name__ == "__main__":
    app.run(debug=True)
