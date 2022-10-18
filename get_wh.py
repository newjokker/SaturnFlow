# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import os
from JoTools.utils.FileOperationUtil import FileOperationUtil
from JoTools.txkjRes.deteRes import DeteRes


img_dir = r""
xml_dir = r""
save_dir = r""


for each_xml_path in FileOperationUtil.re_all_file(xml_dir, endswitch=[".xml"]):
    a = DeteRes(each_xml_path)
    img_path = os.path.join(img_dir, FileOperationUtil.bang_path(each_xml_path)[1] + ".jpg")
    a.img_path = img_path
    a.save_to_xml(os.path.join(save_dir, os.path.split(each_xml_path)[1]))

