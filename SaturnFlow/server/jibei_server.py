# -*- coding: utf-8  -*-
# -*- author: jokker -*-

"""
* 泰州服务
"""
import copy
import os
import time
import shutil
import csv
import argparse
from JoTools.utils.FileOperationUtil import FileOperationUtil
from JoTools.txkjRes.deteRes import DeteRes
from JoTools.utils.CsvUtil import CsvUtil
from JoTools.utils.JsonUtil import JsonUtil
from base_server import BaseServer
import requests
import json


# dete_error 001
# download_img error 002
# post_error 003

class JiBeiServer(BaseServer):

    def __init__(self, img_count, xml_dir, res_dir, sign_dir, mul_progress_num, post_url, heart_beat_url,  batch_id, success_url=None, pid_list=None, print_proecss="True"):
        super(JiBeiServer, self).__init__(img_count, xml_dir, res_dir, sign_dir, mul_progress_num, pid_list, print_proecss)
        self.post_url = post_url
        self.heart_beat_url = heart_beat_url
        self.success_url = success_url                  # 运动成功之后需要发送的标志
        self.batch_id = batch_id
        #
        self.post_success_xml_path = set()
        self.post_error_tmp_dict = {}
        self.post_error_list = []
        self.keep_post_time = 60 * 15
        #
        self.error_info = {"001":set(), "002":set(), "003":set()}


    def if_end(self):
        """根据 sign 文件夹中的信息，判断是否已经结束"""
        # fixme 只有超时和全部图片检测完了才算检测成功

        # if time.time() - self.start_time > self.max_dete_time:
        #     print("* 检测超时，退出，max_dete_time ： {0}".format(self.max_dete_time))
        #     return True

        # image num enough
        if self.save_log.img_index > self.save_log.img_count:
            print("* self.save_log.img_count 已达预期值，检测完毕，退出")
            return True

        return False

    def post_res(self, each_xml_path, headers=None):

        try:
            dete_res = DeteRes(each_xml_path)

            data = {
                "file_name": "",
                "start_time": "",
                "end_time":"",
                "width": -1,
                "height": -1,
                "count": -1,
                "alarms": [],
                "batch_id":self.batch_id
            }
            # alarms
            alarms, xml_id = [], 0
            for each_dete_obj in dete_res:
                xml_id += 1
                alarms.append([xml_id, each_dete_obj.x1, each_dete_obj.y1, each_dete_obj.x2, each_dete_obj.y2, each_dete_obj.tag, each_dete_obj.conf])
            # time
            if dete_res.des in ["", None]:
                start_time, end_time = -1, -1
            else:
                des = dete_res.des.split("-")
                start_time, end_time = float(des[0]), float(des[1])
            #
            data["file_name"] = dete_res.file_name
            data["start_time"] = start_time
            data["end_time"] = end_time
            data["width"] = int(dete_res.width)
            data["height"] = int(dete_res.height)
            data["count"] = xml_id
            data["alarms"] = alarms
            #
            if headers is None:
                headers = {'Connection': 'close'}

            # 设定超时时间，这边默认是不超时的，会阻塞
            response_data = requests.post(url=self.post_url,  data=json.dumps(data), headers=headers, timeout=5)
            print('-'*50)
            print("* img index {0} post : {1} data : {2}".format(self.save_log.img_index, self.post_url, data))
            #
            if response_data.status_code == 200:
                print("* post success : ", dete_res.file_name)
                return True
            else:
                print("* post failed : ", dete_res.file_name)
                return False
            # return response_data
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_frame.f_globals["__file__"])
            print(e.__traceback__.tb_lineno)
            return False

    def post_heart_beat_info(self, if_end=False, beat_interval=5):
        """心跳信息"""
        global last_beat_time

        if time.time() - last_beat_time < beat_interval:
            return True
        else:
            last_beat_time = time.time()

        print("* img count", self.save_log.img_count)
        print("* img index", self.save_log.img_index -1)
        # print("* post error", len(self.post_error_list))
        print("* batch id", self.batch_id)
        print('-'*50)
        try:
            data = {
                "img_count": self.save_log.img_count,
                "img_index": self.save_log.img_index -1,
                # "post_error": len(self.post_error_list),
                "batch_id": self.batch_id,
                "if_end": str(if_end),
                "error_info":{}
            }

            error_info = copy.deepcopy(self.error_info)
            for each_key in error_info:
                error_info[each_key] = list(error_info[each_key])

            data["error_info"] = error_info
            requests.post(url=self.heart_beat_url, data=json.dumps(data), timeout=2)
            # 结束后，当配置了检测成功返回地址，就返回消息回去
            if if_end and self.success_url:
                print("* post server success")
                print("* success url : {0}".format(self.success_url))
                requests.post(url=self.success_url, data=data, timeout=2)
            return True
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_frame.f_globals["__file__"])
            print(e.__traceback__.tb_lineno)
            return False

    def add_each_xml_info(self, xml_path, is_history=False):
        """检测成功增加信息，分为历史信息和新的信息"""
        self.post_heart_beat_info()

        # fixme 如果是在 error 文件夹中那么就认定图片是错误的，拿到 img_id 通过心跳消息传出去
        img_dir, img_id, _ = FileOperationUtil.bang_path(xml_path)
        if img_dir.endswith("download_error"):
            self.error_info["002"].add(img_id)
        elif img_dir.endswith("dete_error"):
            self.error_info["001"].add(img_id)

        # post 不成功就下一轮继续 post

        if xml_path not in self.post_success_xml_path:
            post_status = self.post_res(xml_path)
            if not post_status:
                # 推送错误一个就等待一秒，防止出现全部是错误的情况，会不断地去推送，会重复太多次，图片数量比较多的情况，日志吃不消
                time.sleep(1)
                if xml_path in self.post_error_tmp_dict:
                    if time.time() - self.post_error_tmp_dict[xml_path] < self.keep_post_time:
                        return
                    else:
                        # 记录推送失败的图片
                        # self.post_error_list.append(xml_path)
                        self.error_info["003"].add(img_id)
                else:
                    self.post_error_tmp_dict[xml_path] = time.time()
                    return
            else:
                self.post_success_xml_path.add(xml_path)
                super(JiBeiServer, self).add_each_xml_info(xml_path, is_history=is_history)
        else:
            if os.path.exists(xml_path):
                print("* xml move or delete error, ", xml_path)
                os.remove(xml_path)

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
                # print("* {0} , dete {1} img , speed : {2} pic/second , average speed : {3} pic/second".format(self.dete_img_index, dete_img_num, dete_speed, average_speed))
                print(f"* {self.dete_img_index} , dete {dete_img_num} img , speed : {dete_speed} pic/second , average speed : {average_speed} pic/second")

            # wait
            self.post_heart_beat_info()
            time.sleep(self.flash_interval)

    def main(self):
        """主流程"""
        self.empty_history_info()
        self.set_max_dete_time(50)
        self.start_monitor()
        self.post_heart_beat_info(if_end=True)
        self.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    #
    parser.add_argument('--img_count', dest='img_count',type=int)
    parser.add_argument('--xml_dir', dest='xml_dir',type=str)
    parser.add_argument('--res_dir', dest='res_dir',type=str)
    parser.add_argument('--sign_dir', dest='sign_dir',type=str)
    parser.add_argument('--print_process', dest='print_process', type=str, default='False', choices=['True', 'False'])
    #
    parser.add_argument('--post_url', dest='post_url',type=str)
    parser.add_argument('--heart_beat_url', dest='heart_beat_url',type=str)
    parser.add_argument('--success_url', dest='success_url',type=str, default=None)
    parser.add_argument('--batch_id', dest='batch_id', type=str)
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = parse_args()

    print('-'*50)
    print("* batch_id", args.batch_id)
    print("* post_url", args.post_url)
    print("* heart_beat_url", args.heart_beat_url)
    print('-'*50)

    last_beat_time = time.time()

    ft_server = JiBeiServer(img_count=args.img_count, xml_dir=args.xml_dir, res_dir=args.res_dir, sign_dir=args.sign_dir,
                            mul_progress_num=1, post_url=args.post_url, heart_beat_url=args.heart_beat_url, batch_id=args.batch_id, success_url=args.success_url)

    ft_server.keep_post_time = 60 * 1
    ft_server.main()























