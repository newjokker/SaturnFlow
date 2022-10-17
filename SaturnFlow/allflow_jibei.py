# -*- coding: utf-8  -*-
# -*- author: jokker -*-
import copy
import json
import subprocess
import os
from JoTools.utils.ZipUtil import ZipUtil
import requests
import time
import shutil
import argparse
import configparser
import base64
import prettytable
import sys
import uuid
import signal
import numpy as np
import cv2
from gevent import monkey
from gevent.pywsgi import WSGIServer
from flask import Flask, request, jsonify
from JoTools.txkjRes.deteRes import DeteRes
from JoTools.utils.FileOperationUtil import FileOperationUtil
from JoTools.utils.JsonUtil import JsonUtil
#
monkey.patch_all()

app = Flask(__name__)


@app.route('/dete', methods=['post'])
def start_dete():
    """获取检测状态"""

    # 接收到 post 的次数加一
    global post_index
    post_index += 1

    try:
        model_list = request.form['model_list'].split(',')

        if len(model_list) == 0:
            raise ValueError("* error code : 002, model list is empty")
        #
        img_path_list = request.form['img_path_list'].split(',')
        post_url = request.form['post_url']
        batch_id = request.form['batch_id']
        heart_beat_url = request.form['heart_beat_url']
        success_url = "http://{0}:{1}/server_success".format(host, port)
        # 打印接受到的信息
        print_post_info(model_list, img_path_list, batch_id, post_url)

        print("--------------------------------------------------")
        print("model_list count : ", len(model_list))
        print("img_path_list count : ", len(img_path_list))
        print("post_ucr : ", post_url)
        print("batch_id : ", batch_id)
        print("heart_beat_url : ", heart_beat_url)
        print("--------------------------------------------------")

        # （1）将接受到的信息，放到指定的文件夹下面
        assign_txt_path = os.path.join(assign_txt_dir, batch_id + '.txt')
        # 第一行写上模型列表信息
        with open(assign_txt_path, 'w') as txt_file:
            txt_file.write(",".join(model_list) + "\n")
            for each_img_path in img_path_list:
                txt_file.write(each_img_path + "\n")

        # （2）启动对应的 server，针对文件夹进行处理
        each_save_dir = os.path.join(save_dir, "assign_logs_dir", batch_id)
        # log dir
        log_dir = os.path.join(each_save_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        # xml temp dir
        xml_tmp_dir = os.path.join(each_save_dir, 'xml_tmp')
        os.makedirs(xml_tmp_dir, exist_ok=True)
        # sign dir
        sign_dir = os.path.join(each_save_dir, 'xml_tmp')
        os.makedirs(sign_dir, exist_ok=True)
        # log file
        server_bug_file = open(os.path.join(log_dir, "server_bug" + ".txt"), "w+")
        server_std_file = open(os.path.join(log_dir, "server_std" + ".txt"), "w+")
        #
        print('-'*20)
        print("* start new dete mission")
        # server_cmd_str = r"python3 scripts/server/jibei_server.py --xml_dir {0} --res_dir {1} --post_url {2} " \
        #                  r"--img_count {3} --sign_dir {4} --print_process {5} --batch_id {6} --heart_beat_url {7} --success_url {8}".format(
        #     xml_tmp_dir, each_save_dir, post_url, len(img_path_list), sign_dir, "True", batch_id, heart_beat_url, success_url)

        server_cmd_str = f"python3 scripts/server/jibei_server.py --xml_dir {xml_tmp_dir} --res_dir {each_save_dir} " \
                         f"--post_url {post_url} --img_count {len(img_path_list)} --sign_dir {sign_dir} --print_process True " \
                         f"--batch_id {batch_id} --heart_beat_url {heart_beat_url} --success_url {success_url}"

        pid = subprocess.Popen(server_cmd_str.split(), stdout=server_std_file, stderr=server_bug_file, shell=False)
        server_dict[batch_id] = pid.pid
        print("* server pid : {0}".format(pid.pid))
        print("* {0}".format(server_cmd_str))

        return jsonify({"status":"post success"}), 200
    except Exception as e:
        print(e)
        print(e.__traceback__.tb_frame.f_globals["__file__"])
        print(e.__traceback__.tb_lineno)
        return jsonify({"status": "ERROR:{0}".format(e)}), 400

@app.route('/stop', methods=['post'])
def stop_assign_batch():
    """停止指定 batch"""
    global server_dict
    batch_id = request.form['batch_id']
    assign_txt_path = os.path.join(assign_txt_dir, batch_id + '.txt')
    # assign_logs_dir = os.path.join(save_dir, "assign_logs_dir", batch_id)

    print('-'*20)
    print("* stop server : {0}".format(batch_id))

    if os.path.exists(assign_txt_path):
        # （1）删除待检 txt 文件
        os.remove(assign_txt_path)
        # （2）删除 jibei_server
        if batch_id in server_dict:
            print("* batch_id not in server_dict : {0}".format(batch_id))
            server_pid = server_dict[batch_id]
            try:
                os.kill(server_pid, signal.SIGKILL)
            except Exception as e:
                print(e)
                print(e.__traceback__.tb_frame.f_globals["__file__"])
                print(e.__traceback__.tb_lineno)
                print("* stop server error : no process : server_pid ")
            del server_dict[batch_id]
            print("* stop server success")

        # （3）删除日志文件 todo 这个是不是有必要删除掉？
        # shutil.rmtree(assign_logs_dir)

        return jsonify({"status": "stop success"})
    else:
        print("* assign txt file not exists : {0}".format(assign_txt_path))
        return jsonify({"status": "stop failed"})

@app.route('/server_success', methods=['post'])
def server_end():
    """服务正常结束，返回信息用于删除记录的对应 pid """
    global server_dict
    try:
        batch_id = request.form['batch_id']
        print('-' * 20)
        print("* dete sucess, del pid from server_dict : {0}".format(batch_id))
        if batch_id in server_dict:
            del server_dict[batch_id]
            print("* dete pid success")
        return jsonify({"server success": "success"}), 200
    except Exception as e:
        print("* server end failed")
        print(e)
        print(e.__traceback__.tb_frame.f_globals["__file__"])
        print(e.__traceback__.tb_lineno)
        return jsonify({"server success error": "{0}".format(e)}), 400

@app.route('/re_start', methods=['post'])
def restart_server():
    """关闭所有在检测和待检测的server"""

    # fixme 自动结束的 server 如何从列表中去掉

    global server_dict
    try:
        print("-"*20)
        print("* restart all server and dete")
        # （1）关闭 all_models_flow
        stop_all_models_flow()
        # （2）删除所有 server
        for each_batch_id in server_dict:
            try:
                os.kill(server_dict[each_batch_id], signal.SIGKILL)
            except Exception as e:
                print(f"* 删除进程报错, {each_batch_id} {server_dict[each_batch_id]} {e}")
        server_dict = {}
        # （3）删除所有待检 txt
        for each_txt_path in FileOperationUtil.re_all_file(assign_txt_dir, endswitch='.txt'):
            os.remove(each_txt_path)
        # （4）开启 all_models_flow
        start_all_models_flow()
        print("* restart sucess")
        return jsonify({"status": "restart success"}), 200
    except Exception as e:
        print("* restart failed")
        print(e)
        print(e.__traceback__.tb_frame.f_globals["__file__"])
        print(e.__traceback__.tb_lineno)
        return jsonify({"status error": "{0}".format(e)}), 400

@app.route('/get_log', methods=['post'])
def get_log_file():
    """获取日志信息，打包发到指定路径下面"""
    try:
        global assign_logs_dir
        batch_id = request.form['batch_id']
        post_url = request.form['post_url']
        #
        print('-'*20)
        print("* get log file")
        print("batch_id : ", batch_id)
        print("post_url : ", post_url)
        #
        folder_dir = os.path.join(assign_logs_dir, batch_id)
        if batch_id == "dete_log":
            save_path = os.path.join(assign_logs_dir, batch_id + uuid.uuid1()+ '.zip')
        else:
            save_path = os.path.join(assign_logs_dir, batch_id + '.zip')
        #
        ZipUtil.zip_folder(folder_dir, save_path)
        requests.post(post_url, files={"file": open(save_path, "rb")}, data={"batch_id": batch_id})
        os.remove(save_path)
        print("* get log file success")
        return jsonify({"status": "get log success"}), 200
    except Exception as e:
        print("* get log file failed")
        print(e)
        print(e.__traceback__.tb_frame.f_globals["__file__"])
        print(e.__traceback__.tb_lineno)
        return jsonify({"status error": "{0}".format(e)}), 400

@app.route('/get_docker_info', methods=['post'])
def get_docker_info():
    """将 docker 的信息返回"""
    return jsonify({"model_list": ["nc", "fzcRust", "fzc", "ljcRust", "kkxClearance", "kkxQuiting", "kkxRust", "kkxTC",
                                   "xjDP", "jyzWH", "jyzZB", "jyzPS", "fhjyzPS", "xjQX", "jyhQX", "waipo", "yh", "bzpClear", "dxsg"]})

@app.route('/get_model_info', methods=['get'])
def get_model_info():
    # 获取模型信息
    json_file_path = r"/v0.0.1/model_info.json"
    model_info = JsonUtil.load_data_from_json_file(json_file_path)
    return jsonify(model_info), 200

def start_all_models_flow():
    """开始检测"""
    global all_models_flow_pid
    # log file
    log_dir = os.path.join(assign_logs_dir, "dete_log")
    os.makedirs(log_dir, exist_ok=True)
    dete_bug_file = open(os.path.join(log_dir, "dete_bug_" + str(uuid.uuid1()) + ".txt"), "w+")
    dete_std_file = open(os.path.join(log_dir, "dete_std_" + str(uuid.uuid1()) + ".txt"), "w+")
    dete_cmd_str = f"python3 scripts/all_models_flow_permanent.py --output_dir {assign_logs_dir} --assign_txt_dir {assign_txt_dir}"
    pid = subprocess.Popen(dete_cmd_str.split(), stdout=dete_std_file, stderr=dete_bug_file, shell=False)
    print("* server pid : {0}".format(pid.pid))
    print("* {0}".format(dete_cmd_str))
    all_models_flow_pid = pid.pid
    print('-' * 50)

def stop_all_models_flow():
    """关闭检测服务"""
    global all_models_flow_pid
    if all_models_flow_pid is not None:
        os.kill(all_models_flow_pid, signal.SIGKILL)
        all_models_flow_pid = None

def server_start():
    global host, port
    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()

def print_post_info(model_list, img_path_list, batch_id, post_url):
    print('-' * 100)
    print("* model list : {0}, type : {1}".format(model_list, type(model_list)))
    print("* img path list length: {0}, type : {1}".format(len(img_path_list), type(img_path_list)))
    print("* batch id : {0}, type : {1}".format(batch_id, type(batch_id)))
    print("* post url : {0}, type : {1}".format(post_url, type(post_url)))
    # print("* heartbeat message url: {0}, type : {1}".format(heartbeat_message_url, type(heartbeat_message_url)))
    print('-' * 100)

def parse_args():
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    parser.add_argument('--port', dest='port', type=int, default=111)
    parser.add_argument('--host', dest='host', type=str, default='0.0.0.0')
    #
    parser.add_argument('--save_dir', dest='save_dir', type=str, default="/usr/output_dir")
    parser.add_argument('--gpu_id', dest='gpu_id', type=int, default=0)
    #
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = parse_args()
    port = args.port
    host = args.host
    save_dir = args.save_dir
    gpu_id = args.gpu_id
    #
    # 接受到 post 的次数
    post_index = 0
    all_models_flow_pid = None
    # server dict, {"batch_id": "server_id"}
    server_dict = {}
    #
    assign_txt_dir = os.path.join(save_dir, "assign_txt_dir")
    os.makedirs(assign_txt_dir, exist_ok=True)
    #
    assign_logs_dir = os.path.join(save_dir, "assign_logs_dir")
    os.makedirs(assign_logs_dir, exist_ok=True)
    #
    start_all_models_flow()
    #
    print("-"*50)
    print("* host : {0}".format(host))
    print("* port : {0}".format(port))
    print("* save_dir : {0}".format(save_dir))
    print("* gpu_id : {0}".format(gpu_id))
    print("-"*50)

    #
    server_start()


