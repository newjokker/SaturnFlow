# -*- coding: utf-8  -*-
# -*- author: jokker -*-
import time

import requests
import json
import uuid
from JoTools.utils.FileOperationUtil import FileOperationUtil
from JoTools.utils.JsonUtil import JsonUtil

# fixme 输入的图片的 img_id 必须是唯一的，重复的话会影响到后面的检测

def do_dete(model_list=None, ucd_path=None, receieve_port=4567):

    if model_list is None:
        model_list = "jc"
    else:
        model_list = ",".join(model_list)

    data = {
        # "model_list":"waipo,yanhuo",
        "model_list":model_list,
        # "model_list":"prebase",
        # 需要能下载的图片
        "img_path_list":
            'http://192.168.3.99:7001/images/ht_test/0.JPG-+-001',
        "post_url":"http://192.168.3.221:{0}/res".format(receieve_port),
        "heart_beat_url":"http://192.168.3.221:{0}/heart_beat".format(receieve_port),
        "batch_id":"Repeated_output_001" + str(uuid.uuid1())
    }

    a = JsonUtil.load_data_from_json_file(ucd_path)
    for each_uc in a["uc_list"]:
        img_path = f"http://192.168.3.111:11101/file/{each_uc}.jpg"
        data["img_path_list"] += r",{0}-+-{1}".format(img_path, each_uc)

    post_url = "http://192.168.3.221:{0}/dete".format(port)
    response_data = requests.post(url=post_url,  data=data)
    print(post_url)
    print(response_data.text)

def stop_dete(assign_batch_id):
    post_url = "http://192.168.3.221:{0}/stop".format(port)
    data_stop = {"batch_id": assign_batch_id}
    response_data = requests.post(url=post_url,  data=data_stop)
    print(response_data.text)

def get_log(assign_batch_id):
    post_url = "http://192.168.3.221:{0}/get_log".format(port)
    data_stop = {"batch_id":assign_batch_id, "post_url":r"http://192.168.3.221:11122/save_log"}
    response_data = requests.post(url=post_url,  data=data_stop)
    print(response_data.text)

def restart():
    post_url = "http://192.168.3.221:{0}/re_start".format(port)
    response_data = requests.post(url=post_url)
    print(post_url)
    print(response_data.text)

def get_model_info():
    post_url = "http://192.168.3.221:{0}/get_model_info".format(port)
    response_data = requests.post(url=post_url)
    print(response_data.text)


if __name__ == "__main__":


    port = "12345"

    assign_batch_id = "Repeated_output_001"
    assign_dete_txt_path = r"C:\Users\14271\Desktop\test.json"
    # assign_batch_id = "dete_log"

    modelList = ["fnc", "nc", "fzcRust", "fzc", "ljcRust", "kkxClearance", "kkxQuiting", "kkxRust", "kkxTC", "xjDP", "jyzWH",
                 "jyzZB", "jyzPS", "fhjyzPS", "xjQX", "jyhQX", "waipo", "yh", "bzpClear", "dxsg", "gtYW", "jdtWL", "tdSY", "lmQS", "tcjyzLJ", "fzcHY", "jyhFZ"]


    do_dete(modelList, ucd_path=assign_dete_txt_path, receieve_port=4568)
    # stop_dete(assign_batch_id)
    # get_log(assign_batch_id)
    # restart()
    # get_model_info()





