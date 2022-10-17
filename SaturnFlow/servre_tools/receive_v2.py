# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import os
import base64
import prettytable
import sys
import time
import uuid
import numpy as np
import cv2
import requests
import json

this_dir = os.path.dirname(__file__)
lib_path = os.path.join(this_dir, '..')
sys.path.insert(0, lib_path)

import argparse
from gevent import monkey
from gevent.pywsgi import WSGIServer
import datetime
#
from JoTools.txkjRes.deteRes import DeteRes
from JoTools.utils.FileOperationUtil import FileOperationUtil
#

monkey.patch_all()
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/res', methods=['post'])
def receive_img():
    """获取检测状态"""
    try:
        print(request.data)
        json_dict = json.loads(request.data)
        alarms = json_dict['alarms']
        # todo 转化为 dete_res,更好地去看结果
        # [1, 1617, 1590, 1755, 1737, 'jyz_gm_clean', 1.0
        dete_res = DeteRes()
        for each_alarm in alarms:
            dete_res.add_obj(each_alarm[1], each_alarm[2], each_alarm[3], each_alarm[4], tag=each_alarm[5], conf=each_alarm[6], assign_id=each_alarm[0])
        dete_res.print_as_fzc_format()

        save_path = os.path.join(save_dir, json_dict["file_name"] + ".xml")
        dete_res.save_to_xml(save_path)

        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        print('-'*50)
        return jsonify({"status":"OK"})
    except Exception as e:
        print(e)
        return jsonify({"status": "ERROR:{0}".format(e)})

@app.route('/heart_beat', methods=['post'])
def heart_beat():
    """获取检测状态"""
    try:
        print(request.data)
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        print('-'*50)
        return jsonify({"status":"OK"})
    except Exception as e:
        return jsonify({"status": "ERROR:{0}".format(e)})

@app.route('/save_log', methods=['post'])
def save_log():
    """获取检测状态"""
    try:
        print("* save log file to zip")
        batch_id = request.form['batch_id']
        save_path = os.path.join(log_zip_dir, str(batch_id) + '.zip')
        request.files['file'].save(save_path)
        return jsonify({"status":"OK"})
    except Exception as e:
        print(e)
        return jsonify({"status": "ERROR:{0}".format(e)})


def serv_start():
    global host, port
    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()

def parse_args():
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    parser.add_argument('--port', dest='port', type=int, default=3232)
    parser.add_argument('--host', dest='host', type=str, default='0.0.0.0')
    parser.add_argument('--save_dir', dest='save_dir', type=str, default=r"./xml")
    parser.add_argument('--log_zip_dir', dest='log_zip_dir', type=str, default='/home/ldq/NewFrame/log_zip')

    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = parse_args()
    port = args.port
    host = args.host
    save_dir = args.save_dir
    log_zip_dir = args.log_zip_dir

    os.makedirs(save_dir, exist_ok=True)

    serv_start()














