# -*- coding: utf-8  -*-
# -*- author: jokker -*-


class ProductBase(object):

    def __init__(self):
        self.model_dict = {}
        # 配置文件地址
        self.config_path = ""
        # 模型文件夹
        self.model_dir = ""
        # 模型名，和检测对应
        self.model_name = "model_name"
        # 模型版本
        self.version = "model_version"
        # 输出的标签
        self.output_labels = ["tag1", "tag2", "tag3"]               # 这些信息方便和服务和外界进行交互

    def warm_up(self):
        # 加载模型
        pass

    def dete(self, img_path, img, dete_res_before):
        # 模型检测返回标准结果
        pass


