# -*- coding: utf-8  -*-
# -*- author: jokker -*-

import os, sys
import random

this_dir = os.path.dirname(__file__)
lib_path = os.path.join(this_dir, '..')
sys.path.insert(0, lib_path)
#
import argparse
import cv2
import shutil
import json
import torch
import uuid
import time
import copy
import requests
import numpy as np
from PIL import Image
from io import BytesIO
#
from lib.JoTools.utils.FileOperationUtil import FileOperationUtil
from lib.JoTools.utils.DecoratorUtil import DecoratorUtil
from lib.JoTools.txkjRes.deteRes import DeteRes
#
from dete.dete_prebase import dete_prebase
from dete.all_model_restore import all_model_restore

#-------------------------------------------------------------
def map_model_list(model_list):
    """映射模型列表"""

    model_list_dict = {
        # ljj_all
        "nc": ["prebase", "ljj_all"],
        "fzcRust": ["prebase", "ljj_all"],
        "fzc": ["prebase", "ljj_all"],
        "ljcRust": ["prebase", "ljj_all"],
        # kkx_all
        "kkxClearence":["prebase", "kkx_all"],
        "kkxQuiting":["prebase", "kkx_all"],
        "kkxRust":["prebase", "kkx_all"],
        "kkxTC":["prebase", "kkx_all"],
        "xjDP":["prebase", "kkx_all"],
        # jyz_all
        "jyzWH":["prebase","jyz_all"],
        "jyzZB":["prebase","jyz_all"],
        "jyzPS":["lightSD"],
        "fhjyzPS":["lightSD"],
        "jyhTL":["lightSD"],
        "jyzRust": ["prebase", "jyz_all"],
        # xjQX
        "xjQX":["prebase","xjQX"],
        # jyhQX
        "jyhQX": ["prebase","jyhQX"],
        # waipo
        "waipo": ["prebase","waipo"],
        # yanhuo
        "yh":["prebase","yanhuo"],
        # bzpClear
        "bzpClear":["prebase","bzp_clear"],
        # dxsg
        "dxsg":["lightSD"],
        #
        "jc":["jc"],
        #
        "fnc":["fnc"],
        # 杆塔异物
        "gtYW": ["lightSD"],
        # 接地体外漏
        "jdtWL": ["lightSD"],
        # 基础水淹
        "tdSY": ["lightSD"],
        # 螺母缺失
        "lmQS": ["lightSD"],
        # 陶瓷绝缘子累雷击
        "tcjyzLJ": ["lightSD"],
        # 防振锤滑移
        "fzcHY": ["lightSD"],
        # 均压环反装
        "jyhFZ": ["lightSD"],
        # 均压环锈蚀
        "ringXS": ["lightSD"],
    }

    all_model_list_tmp = set()
    for each_model in model_list:
        if each_model in model_list_dict:
            for each_model_new_name in model_list_dict[each_model]:
                all_model_list_tmp.add(each_model_new_name)
    # 转为列表
    model_list = list(all_model_list_tmp)

    return model_list

def filter_dete_res_by_model_list(dete_res, model_list):
    """将检测结果使用 model_list 对应的模型进行过滤"""

    need_tags = set()

    if "nc" in model_list:
        need_tags.add("nc")
        need_tags.add("fw")

    # todo 等待确认
    if "fzc" in model_list:
        need_tags.add("fzcObj_broken")
        need_tags.add("fzc_ps")

    if "fzcRust" in model_list:
        need_tags.add("fzcObj_rust")

    if "yh" in model_list:
        need_tags.add("fire")
        need_tags.add("smoke")

    if "waipo" in model_list:
        need_tags.add("TaDiao")
        need_tags.add("ShuiNiBengCheYb")
        need_tags.add("DiaoCheYb")
        need_tags.add("DaoXianYiWu")
        need_tags.add("FanDouChe")
        need_tags.add("DiaoChe")
        need_tags.add("ChanChe")
        need_tags.add("DaZhuangJi")
        need_tags.add("TuiTuJi")
        need_tags.add("ShuiNiBengChe")
        need_tags.add("WaJueji")

    if "dxsg" in model_list:
        need_tags.add("dxObj_sg")

    if "dxdg" in model_list:
        need_tags.add("dxObj_dg")

    if "bzpClear" in model_list:
        need_tags.add("bzpObj_fuzzy")

    if "xjQX" in model_list:
        need_tags.add("xjObj_oblique")

    if "jyhQX" in model_list:
        need_tags.add("jyhObj_oblique")

    if "jyzZB" in model_list:
        need_tags.add("jyzObj_bigbang")

    if "jyzWH" in model_list:
        need_tags.add("jyzObj_dirty")

    if "jyzPS" in model_list:
        need_tags.add("jyzSub_broken")

    if "jyzRust" in model_list:
        need_tags.add("jyzObj_rust")

    if "ljcRust" in model_list:
        need_tags.add("ljj_rust")
        #
        need_tags.add("UGuaHuan_rust")
        need_tags.add("ZGuaBan_rust")
        need_tags.add("ZBDGuaBan_rust")
        need_tags.add("WTGB_rust")
        need_tags.add("UBGuaBan_rust")
        need_tags.add("PGuaBan_rust")
        need_tags.add("QYB_rust")
        need_tags.add("Sanjiaoban_rust")
        need_tags.add("LKLB_rust")
        need_tags.add("LCLB_rust")
        need_tags.add("LLLB_rust")
        need_tags.add("LLB_rust")
        need_tags.add("DBTZB_rust")
        need_tags.add("PTTZB_rust")
        need_tags.add("Zhongchui_rust")

    if "xjDP" in model_list:
        need_tags.add("dpObj_miss")

    if "fhjyzPS" in model_list:
        need_tags.add("fhjyz_broken")

    if "jyhTL" in model_list:
        need_tags.add("jyhObj_drop")

    if "kkxClearence" in model_list:
        need_tags.add("kkxObj_clearence")
        need_tags.add("LmObj_flat")

    if "kkxQuiting" in model_list:
        need_tags.add("kkxObj_tc")
        need_tags.add("kkxObj_bgf")

    if "kkxRust" in model_list:
        need_tags.add("kkxObj_rust")
        need_tags.add("dpObj_rust")
        need_tags.add("noObj_rust")
        need_tags.add("LmObj_rust")

    if "kkxTC" in model_list:
        need_tags.add("kkxObj_miss")

    if "jc" in model_list:
        need_tags.add("qutu")
        need_tags.add("yanmo")

    if "fnc" in model_list:
        need_tags.add("fnc_sdps")
        need_tags.add("fnc_wdk")

    if "gtYW" in model_list:
        need_tags.add("gt_yw")

    if "jdtWL" in model_list:
        need_tags.add("jdt_wl")

    if "tdSY" in model_list:
        need_tags.add("td_sy")

    if "lmQS" in model_list:
        need_tags.add("lmqs")

    if "tcjyzLJ" in model_list:
        need_tags.add("tcjyz_lj")

    if "fzcHY" in model_list:
        need_tags.add("fzc_hy")

    if "jyhFZ" in model_list:
        need_tags.add("jyh_fz")

    if "ringXS" in model_list:
        need_tags.add("ring_xs")

    #
    dete_res.filter_by_tags(need_tag=list(need_tags))
#-------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    #
    parser.add_argument('--output_dir', dest='output_dir', default=r"/usr/output_dir")                                              # 输出文件夹地址
    parser.add_argument('--assign_txt_dir', dest='assign_txt_dir',type=str, default=None)                                           #
    parser.add_argument('--model_list', dest='model_list',type=str, default=None)                                                   # 启动的模型列表
    #
    parser.add_argument('--ignore_history', dest='ignore_history',type=str, default='True', choices=['True', 'False'])              # 如果存在历史 xml 文件，是不是重复进行检测
    parser.add_argument('--draw_res', dest='draw_res',type=str, default='False', choices=['True', 'False'])                         # 是否画出结果
    parser.add_argument('--crop_res', dest='crop_res',type=str, default='False', choices=['True', 'False'])                         # 是裁剪出结果
    #
    parser.add_argument('--gpuID', dest='gpuID', type=int, default=0)
    parser.add_argument('--port', dest='port', type=int, default=45452)
    parser.add_argument('--gpuRatio', dest='gpuRatio', type=float, default=0.3)
    parser.add_argument('--host', dest='host', type=str, default='127.0.0.1')
    parser.add_argument('--logID', dest='logID', type=str, default=str(uuid.uuid1())[:12])
    parser.add_argument('--objName', dest='objName', type=str, default='')
    #
    args = parser.parse_args()
    return args

def use_one_cpu():
    cpu_num = 1  # 这里设置成你想运行的CPU个数
    os.environ['OMP_NUM_THREADS'] = str(cpu_num)
    os.environ['OPENBLAS_NUM_THREADS'] = str(cpu_num)
    os.environ['MKL_NUM_THREADS'] = str(cpu_num)
    os.environ['VECLIB_MAXIMUM_THREADS'] = str(cpu_num)
    os.environ['NUMEXPR_NUM_THREADS'] = str(cpu_num)
    torch.set_num_threads(cpu_num)

def get_img_path_from_assign_txt_dir(txt_dir):
    """从用 txt 记录文件路径的文件夹中获取文件路径"""
    # 按照文件名对文件列表进行排序，文件名：时间 + batch_id
    each_img_path_list = []
    each_txt_path = None
    each_model_list = []
    txt_path_list = list(FileOperationUtil.re_all_file(txt_dir, endswitch=['.txt']))
    if len(txt_path_list) > 0:
        each_txt_path = txt_path_list[0]
        try:
            with open(each_txt_path, 'r') as img_path_file:
                # 模型的第一行是模型列表信息
                model_info_line = next(img_path_file)
                for model_name in model_info_line.strip().split(','):
                    each_model_list.append(model_name)
                # 解析图片信息
                for each_line in img_path_file:
                    each_img_path_list.append(each_line.strip())
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_frame.f_globals["__file__"])
            print(e.__traceback__.tb_lineno)
            print("* 删除错误的检测任务 txt : ", each_txt_path)
            if(os.path.exists(each_txt_path)):
                os.remove(each_txt_path)
            return [], None, []

    return each_img_path_list, each_txt_path, each_model_list

def parse_txt_path(each_txt_path):
    """解析txt文件名中的信息"""
    _, assign_txt_name, _ = FileOperationUtil.bang_path(each_txt_path)
    return assign_txt_name

def print_args_info():
    """打印配置信息"""
    print('-' * 50)
    print("* {0} : {1}".format("assign_txt_dir", assignTxtDir))
    print("* {0} : {1}".format("output dir", outputDir))
    print('-' * 50)

def model_warmup(args, all_model_list):
    # warm up
    print("* start warm model ")
    scriptName = os.path.basename(__file__).split('.')[0]
    all_model_dict = all_model_restore(args, scriptName, all_model_list)
    print("* warm model success ")
    return all_model_dict

@DecoratorUtil.time_this
def model_dete(img_path, model_dict, model_list, output_dir, draw_res=False, crop_res=False):
    """进行模型检测, 支持网络图片"""

    # ------------------------------------------------------------------------------------------------------------------
    # 对接受到的模型名就行映射
    region_model_list = copy.deepcopy(model_list)
    model_list = map_model_list(model_list)
    # ------------------------------------------------------------------------------------------------------------------

    res_save_dir = os.path.join(output_dir, "xml_tmp")
    os.makedirs(res_save_dir, exist_ok=True)
    #
    save_download_error_dir = os.path.join(output_dir, "xml_tmp", "download_error")
    os.makedirs(save_download_error_dir, exist_ok=True)
    #
    save_dete_error_dir = os.path.join(output_dir, "xml_tmp", "dete_error")
    os.makedirs(save_dete_error_dir, exist_ok=True)
    #
    res_save_draw_res_dir = os.path.join(output_dir, "draw_res")
    os.makedirs(res_save_draw_res_dir, exist_ok=True)
    #
    res_save_crop_res = os.path.join(output_dir, "dete_crop")
    os.makedirs(res_save_crop_res, exist_ok=True)

    #
    if not "-+-" in img_path:
        raise ValueError("error code : 001, web img format : web_path-+-img_id")

    img_path, each_img_name = img_path.split('-+-')
    dete_res_all = DeteRes()
    dete_res_all.file_name = each_img_name
    # todo 是不是要把文件保存到本地，等检测完毕再去删除，这样比较不容易报错
    each_save_path_jpg = os.path.join(res_save_draw_res_dir, each_img_name + '.jpg')
    each_save_path_xml_normal = os.path.join(res_save_dir, each_img_name + '.xml')
    each_save_path_xml_dete_error = os.path.join(save_dete_error_dir, each_img_name + '.xml')
    each_save_path_xml_download_error = os.path.join(save_download_error_dir, each_img_name + '.xml')

    #
    start_time = time.time()

    try:
        response = requests.get(img_path)
        image = Image.open(BytesIO(response.content))
        im = np.array(image)
        height, width = im.shape[:2]
        dete_res_all.height, dete_res_all.width = height, width
    except Exception as e:
        print(e)
        print(e.__traceback__.tb_frame.f_globals["__file__"])
        print(e.__traceback__.tb_lineno)
        end_time = time.time()
        dete_res_all.des = "{0}-{1}".format(start_time, end_time)
        dete_res_all.save_to_xml(each_save_path_xml_download_error)
        return

    try:
        # im 是 RGB 形式的，不是 GBR 形式的
        data = {"path": img_path, 'name': each_img_name, 'im': im, 'height': height, 'width': width}

        # ------------------------------------------------------------------------------
        if "prebase" in model_list:
            prebase_dete_res = dete_prebase(model_dict, copy.deepcopy(data))
            data["prebase"] = prebase_dete_res.deep_copy()
        # ------------------------------------------------------------------------------
        for each_model in model_list:
            # prebase 不记录结果
            if each_model == 'prebase':
                continue
            dete_str = f'dete_{each_model}(model_dict, copy.deepcopy(data))'
            each_dete_res = eval(dete_str)
            if each_dete_res:
                dete_res_all += each_dete_res
        # ------------------------------------------------------------------------------
        dete_res_all.print_as_fzc_format()
        print('*'*30)
        # --------------------------------------------------------------------------------------------------------------

        # set confidence as 1 when confidence less then 0.3
        for each_dete_obj in dete_res_all:
            if isinstance(each_dete_obj.conf, str):
                each_dete_obj.conf = float(each_dete_obj.conf)
            if each_dete_obj.conf <= 0.3:
                each_dete_obj.conf = 1

        # --------------------------------------------------------------------------
        # 根据传入的 model_list 对结果进行筛选
        filter_dete_res_by_model_list(dete_res_all, region_model_list)
        # --------------------------------------------------------------------------

        # nms
        dete_res_all.do_nms(0.25)

        # end time
        end_time = time.time()
        dete_res_all.des = "{0}-{1}".format(start_time, end_time)

        # save xml
        if len(dete_res_all) > 0:
            dete_res_all.print_as_fzc_format()
        else:
            print([])

        # draw
        if draw_res or crop_res:
            im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
            dete_res_all.img_ndarry = im
            # crop
            if crop_res:
                if len(dete_res_all):
                    dete_res_all.crop_dete_obj(res_save_crop_res, augment_parameter=[0.1, 0.1, 0.1, 0.1], split_by_tag=True)

            if draw_res:
                if len(dete_res_all):
                    dete_res_all.draw_dete_res(each_save_path_jpg, assign_img=im)

        dete_res_all.save_to_xml(each_save_path_xml_normal)

    except Exception as e:
        print(e)
        print(e.__traceback__.tb_frame.f_globals["__file__"])
        print(e.__traceback__.tb_lineno)
        # end time
        print('-'*50)
        dete_res_all.print_as_fzc_format()
        end_time = time.time()
        dete_res_all.des = "{0}-{1}".format(start_time, end_time)
        dete_res_all.save_to_xml(each_save_path_xml_dete_error)


    print("dete finished : ", time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())))
    # empty cache
    torch.cuda.empty_cache()
    return dete_res_all


if __name__ == '__main__':

    # 使用一个 gpu
    use_one_cpu()
    #
    args = parse_args()
    assignTxtDir = args.assign_txt_dir
    outputDir = args.output_dir.strip()
    allModelListStr = args.model_list
    ignoreHistory = eval(args.ignore_history)
    drawRes = eval(args.draw_res)
    cropRes = eval(args.crop_res)

    # 打印配置信息
    print_args_info()

    # 清空待检图片 txt
    if os.path.exists(assignTxtDir):
        shutil.rmtree(assignTxtDir)
    os.makedirs(assignTxtDir)
    # -------------------------------------------------------------------------------
    # get model list
    if allModelListStr is None:
        allModelList = ["prebase", "waipo", "yanhuo", "dxsg", "bzp_clear", "jyz_all", "kkx_all", "ljj_all", "xjQX", "jyhQX", "jc", "fnc", "lightSD"]
    else:
        allModelList = []
        for eachModelName in allModelListStr.split(','):
            allModelList.append(eachModelName.strip())
    # -------------------------------------------------------------------------------
    # import model
    print('-'*50)
    for eachModel in allModelList:
        importStr = f"from dete.dete_{eachModel} import dete_{eachModel}"
        print(f"exec import str : {importStr}")
        exec(importStr)
    # start model
    allModelDict = model_warmup(args, allModelList)
    # ------------------------------------------------------------------------------------------------------------------
    is_wait = False
    while True:
        time.sleep(1)

        # 获取当前批次检测信息
        imgPathList, assignTxtPath, assignModelList = get_img_path_from_assign_txt_dir(assignTxtDir)

        if assignTxtPath is None:
            localTime = time.localtime()
            if is_wait is False:
                print(f"* waiting from : {localTime.tm_year}-{localTime.tm_mon}-{localTime.tm_mday} {localTime.tm_hour}:{localTime.tm_min}:{localTime.tm_sec}")
                is_wait = True
            continue
        else:
            if is_wait is True:
                localTime = time.localtime()
                print(f"* working from : {localTime.tm_year}-{localTime.tm_mon}-{localTime.tm_mday} {localTime.tm_hour}:{localTime.tm_min}:{localTime.tm_sec}")
            is_wait = False

            #
            eachBatchId = parse_txt_path(assignTxtPath)
            eachOutputDir = os.path.join(outputDir, eachBatchId)
            os.makedirs(eachOutputDir, exist_ok=True)
            print('-' * 30)
            print("* img_path_length    : ", len(imgPathList))
            print("* output_dir         : ", eachOutputDir)
            print("* assign_txt_path    : ", assignTxtPath)
            print("* assign_model_list  : ", assignModelList)
            print('-' * 30)
            # do dete
            for imgIndex, eachImgPath in enumerate(imgPathList):
                model_dete(eachImgPath, allModelDict, assignModelList, eachOutputDir, draw_res=drawRes, crop_res=cropRes)
                # model_dete(eachImgPath, allModelDict, assignModelList, eachOutputDir, draw_res=True, crop_res=True)
                print("* do detect : {0}".format(eachImgPath))
                if imgIndex % 5 == 0:
                    if not os.path.exists(assignTxtPath):
                        print("* 检测 txt 文件丢失，停止检测")
                        break

        # 每检测几次就看一下正在检测的 txt 是不是还在，要是不在的话就直接把服务给关了，将待检测的路径列表清空？
        # delete txt file after dete
        if assignTxtDir:
            if os.path.exists(assignTxtPath):
                os.remove(assignTxtPath)
    # ------------------------------------------------------------------------------------------------------------------
