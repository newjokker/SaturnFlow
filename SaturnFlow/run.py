# -*- coding: utf-8  -*-
# -*- author: jokker -*-


from JoTools.txkjRes.deteRes import DeteRes


class SaturnFlow(object):

    def __init__(self, host, port):
        self.hot = host
        self.port = port
        self.product_dict = {}
        self.nms = -1
        self.conf = -1
        self.need_tags = []
        self.output_dir = r""

    def register(self, product):
        """产品注册"""
        self.product_list.append(product)

    def dete(self, img, product_name_list="*"):
        """产品检测"""
        if product_name_list == "*":
            product_name_list = list(self.product_dict.keys())

        dete_res = DeteRes()
        for each_name in product_name_list:
            each_p = self.product_dict[each_name]
            each_dete_res = each_p.dete(img)
            dete_res += each_dete_res

        if self.nms > 0:
            dete_res.do_nms(self.nms)

        if self.conf > 0:
            dete_res.filter_by_conf(self.conf)

        if len(self.need_tags) > 0:
            dete_res.filter_by_tags(need_tag=self.need_tags)

        return dete_res

    def run(self):
        # 持续运行

        while True:
            img = None
            # todo 获取图片信息和需要检测的模型
            product_name_list = "*"
            self.dete(img, product_name_list)



class SaturnFlow_V2(SaturnFlow):
    pass
