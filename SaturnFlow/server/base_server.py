# -*- coding: utf-8  -*-
# -*- author: jokker -*-

"""
* 定时扫 xml 文件夹，并据此生成 log 和 csv
"""

import os
import time
import shutil
import csv
import argparse
from JoTools.utils.FileOperationUtil import FileOperationUtil
from JoTools.txkjRes.deteRes import DeteRes
from JoTools.utils.CsvUtil import CsvUtil
from JoTools.utils.JsonUtil import JsonUtil


class SaveLog():

    def __init__(self, log_path, img_count, csv_path=None):
        self.log_path = log_path
        self.img_count = img_count
        self.img_index = 1
        self.csv_path = csv_path
        # self.csv_list = [['filename', 'name', 'score', 'xmin', 'ymin', 'xmax', 'ymax']]
        # empty log
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

        # add csv title
        with open(self.csv_path, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows([['filename', 'name', 'score', 'xmin', 'ymin', 'xmax', 'ymax']])

    def init_log(self):
        log = open(self.log_path, 'w')
        log.write("Loading Finished\n")
        log.close()

    def add_log(self, img_name):
        log = open(self.log_path, 'a')
        log.write("process:{0}/{1} {2}\n".format(self.img_index, self.img_count, img_name))
        self.img_index += 1
        log.close()

    def add_csv_info(self, dete_res, img_name):
        """add one csv info"""
        csv_list= []
        for dete_obj in dete_res:
            csv_list.append([img_name, dete_obj.tag, dete_obj.conf, dete_obj.x1, dete_obj.y1, dete_obj.x2, dete_obj.y2])

        with open(self.csv_path, "a", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_list)

    def close(self):
        log = open(self.log_path, 'a')
        log.write("---process complete---\n")
        log.close()


class BaseServer(object):

    def __init__(self, img_count, xml_dir, res_dir, sign_dir, mul_progress_num, pid_list=None, print_proecss="True"):
        # self.img_dir = img_dir
        self.xml_tmp_dir = xml_dir
        self.res_dir = res_dir
        self.xml_res_dir = os.path.join(self.res_dir, "xml_res")
        self.sign_dir = sign_dir
        self.sign_end_txt_dir = os.path.join(self.sign_dir, 'res_txt')
        self.mul_progress_num = mul_progress_num            # 进程个数
        #
        self.start_time = time.time()
        self.last_flash_time = self.start_time
        self.stop_time = None
        self.max_dete_time = -1
        self.dete_img_index = 0                             # 已检测的图片的数量
        #
        log_path = os.path.join(self.res_dir, 'log')
        csv_path = os.path.join(self.res_dir, 'result.csv')
        # img_count = len(list(FileOperationUtil.re_all_file(self.img_dir, endswitch=['.jpg', '.JPG', '.png', '.PNG'])))
        self.all_img_count = img_count                                                           # 所有要检测图片的数目
        self.save_log = SaveLog(log_path, img_count, csv_path)
        self.save_log.init_log()
        self.max_dete_time = 1000000 * self.all_img_count
        #
        self.print_process = eval(print_proecss)
        # 解析 json 文件
        #self.parse_json_dict()
        self.flash_interval = 5
        # 检测结束之后还需要再次扫描一下 tmp 文件夹，防止最后剩余的文件没被处理
        self.dete_end = False

    def if_end(self):
        """根据 sign 文件夹中的信息，判断是否已经结束"""
        # over time
        if self.dete_end:
            return True

        if time.time() - self.start_time > self.max_dete_time:
            self.dete_end = True
            return False

        # image num enough
        if self.save_log.img_index > self.save_log.img_count:
            self.dete_end = True
            return False

        # each process ended
        for i in range(1, self.mul_progress_num+1):
            each_txt_path = os.path.join(self.sign_end_txt_dir, "{0}.txt".format(i))
            if not os.path.exists(each_txt_path):
                return False

        # 已经结束了，还会增加一次扫描
        self.dete_end = True

    def set_max_dete_time(self, assign_each_dete_use_time=9.5):
        """获取最长的检测时间，超过检测时间自动退出并保存日志和 csv"""
        self.max_dete_time = assign_each_dete_use_time * self.all_img_count

    def empty_history_info(self):
        """清空历史数据"""
        def empty_dir(assign_dir):
            """清空文件夹中的文件"""
            for each_file_path in FileOperationUtil.re_all_file(assign_dir):
                os.remove(each_file_path)
        #
        if os.path.exists(self.sign_end_txt_dir):
            empty_dir(self.sign_end_txt_dir)
        #
        os.makedirs(self.res_dir, exist_ok=True)
        os.makedirs(self.xml_res_dir, exist_ok=True)
        os.makedirs(self.sign_dir, exist_ok=True)
        os.makedirs(self.xml_tmp_dir, exist_ok=True)

    def add_each_xml_info(self, xml_path, is_history=False):
        """检测成功增加信息，分为历史信息和新的信息"""
        img_name = FileOperationUtil.bang_path(xml_path)[1] + '.jpg'
        try:
            each_dete_res = DeteRes(xml_path)
            if each_dete_res.file_name:
                img_name = each_dete_res.file_name
            self.save_log.add_log(img_name)
            self.save_log.add_csv_info(each_dete_res, img_name)
            # history xml needn't change folder
            if os.path.exists(xml_path):
                if (not is_history):
                    new_xml_path = os.path.join(self.xml_res_dir, os.path.split(xml_path)[1])
                    shutil.move(xml_path, new_xml_path)
            else:
                print("* xml_path not exists : ", xml_path)

        except Exception as e:
            print(e)
            self.save_log.add_log(img_name)
            print('-' * 50, 'error', '-' * 50)
            if os.path.exists(xml_path):
                os.remove(xml_path)
        print("* post finished : ", time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())))
        self.dete_img_index += 1

    def start_monitor(self):
        """开始监听"""
        # --------------------------------------------------------------------------------------------------------------
        # 先将已经完成的结果数据放到 log 中去，用于断点检测
        history_xml_path_list = FileOperationUtil.re_all_file(self.xml_res_dir, endswitch=['.xml'])
        for each_xml_path in history_xml_path_list:
            self.add_each_xml_info(each_xml_path, is_history=True)
        # update start time
        self.start_time = time.time()
        # --------------------------------------------------------------------------------------------------------------
        while True:
            # all end
            if self.if_end():
                self.stop_time = time.time()
                return

            xml_path_list = list(FileOperationUtil.re_all_file(self.xml_tmp_dir, endswitch=['.xml']))
            for each_xml_path in xml_path_list:
                self.add_each_xml_info(each_xml_path, is_history=False)

            # print process
            if self.print_process:
                use_time = time.time() - self.last_flash_time
                self.last_flash_time = time.time()
                dete_img_num = len(xml_path_list)
                dete_speed =  dete_img_num / use_time if dete_img_num > 0 else None
                average_speed = self.dete_img_index / (time.time()-self.start_time)
                print("* {0} , dete {1} img , speed : {2} pic/second , average speed : {3} pic/second".format(self.dete_img_index, dete_img_num, dete_speed, average_speed))

            # wait
            time.sleep(self.flash_interval)

    def close(self):
        # fixme 这边专门用于 后处理的
        use_time = self.stop_time - self.start_time
        print("* check img {0} use time {1} {2} s/pic".format(self.all_img_count, use_time, use_time / self.all_img_count))
        self.save_log.close()

    def main(self):
        """主流程"""
        self.empty_history_info()
        self.set_max_dete_time(9.5)
        self.start_monitor()
        self.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    #
    parser.add_argument('--img_count', dest='img_count',type=int)
    parser.add_argument('--xml_dir', dest='xml_dir',type=str)
    parser.add_argument('--res_dir', dest='res_dir',type=str)
    parser.add_argument('--sign_dir', dest='sign_dir',type=str)
    parser.add_argument('--mul_progress_num', dest='mul_progress_num',type=int)
    parser.add_argument('--print_process', dest='print_process', type=str, default='False', choices=['True', 'False'])
    #
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = parse_args()
    ft_server = BaseServer(args.img_count, args.xml_dir, args.res_dir, args.sign_dir, args.mul_progress_num)
    ft_server.main()























