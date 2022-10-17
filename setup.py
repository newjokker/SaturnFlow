# -*- coding: utf-8  -*-
# -*- author: jokker -*-

"""
* pip install opencv-python : 安装 cv2
* conda install shapely : 安装 shapely, pip 安装比较容易报错
"""

from setuptools import setup, find_packages

setup(

    name='SaturnFlow',                                                                          # 打包起来的包的文件名
    version='0.0.1',                                                                        # 版本
    description='a tools for NewFrame',                                                    # 描述
    author='jokker',                                                                        # 作者
    author_email='18761609908@163.com',                                                     # 邮箱
    url='https://github.com/newjokker/SaturnFlow.git',
    requires=['numpy', 'pillow', 'pandas', 'easydict', 'matplotlib', 'imagehash', 'prettytable', 'progress',
              'progressbar', 'requests', 'imageio', 'pyexiv2', 'cv2', 'exifread', 'whatimage', 'pyheif',
              'pymysql', 'pytesseract', 'beautifulsoup4', 'Crypto', 'flask'
              ],          # 定义依赖哪些模块
    # 打包的python文件夹AZ
    packages=[],
    # packages=find_packages('JoTools'),          # 包含所有 JoTools 中的包
    package_data={},
    long_description="""
    * 将 NewFrame 中的内容用一个包的形式进行实现
    """,
    )

# ----------------------------------------------------------------------------------------------------------------------
# refer : https://zhuanlan.zhihu.com/p/276461821
# 打包的命令
# 切换到 setup.py 文件所在文件夹
# python setup.py bdist_wheel, 构建分法 build-distribution wheel 文件？
# python setup.py sdist ，打包为 zip 文件

# 注意
# 需要将用到的包全部写到 packages 参数后
# 需要在 setup.py 同级目录创建一个 test.py 文件用于测试
# requires 不能出现 *-* 格式的写法 如 scikit-image，否则会报错

# setuptools 的进一步学习参考：https://www.jianshu.com/p/ea9973091fdf

# ----------------------------------------------------------------------------------------------------------------------
# 发布到 pypi 上去，refer : https://www.justdopython.com/2020/05/13/Python-pip/
# python -m twine upload --repository pypi dist/*
# 或者
# python -m twine upload --repository pypi dist/JoUtil-0.2.21-py3-none-any.whl
# 账号：jokker
# 密码：*u@%Uu.#PU8ty,w

# 有时候明明上传了，但是提示历史版本为最新的版本，看一下版本号是不是设置错了，或者改一下版本号，twine 会根据版本号决定哪个是最新的版本
# 报错试一下关闭 VPN 再试一下，一定确保 vpn 关掉了
# 试着在网页上登录上
# 还是报错的话尝试更新一下 twine

# ----------------------------------------------------------------------------------------------------------------------
# pip freeze > requirements.txt，环境导出
# pip install -r requirements.txt，环境安装
# ----------------------------------------------------------------------------------------------------------------------

