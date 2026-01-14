# -*- coding: utf-8 -*-
'''
这个脚本是PycPlaycer和EDA工具交互的接口，主要是生成TCL脚本，将脚本写到指定的目录下，同时等待EDA结果返回，然后读取EDA工具写的内容，供PycPlacer分析
'''
import time
import os
import logging

from leapr_config import *

from config import DEFAULT_CONFIG

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# 如果没有处理器，添加一个控制台处理器
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class TCLSender:

    # 输入是tcl命令列表，将命令列表写到command.tcl文件里
    def send_tcl(self, tcl_command_list):
        # 如果是windows环境，直接返回API_DIR目录下的server_result.txt文件--用于本地调试
        if os.name == 'nt':
            logger.info("Running on Windows, returning server_result.txt content for local debugging")
            return [line.rstrip('\n') for line in open(DEFAULT_CONFIG.get("api_dir") + "server_result.txt", "r")]
        # 1. 写命令
        command_tcl_path = os.path.join(DEFAULT_CONFIG.get("api_dir"), "command.tcl")
        logger.info(f"Writing TCL commands to {command_tcl_path}")
        with open(command_tcl_path, "w") as f:
            f.writelines([line + '\n' for line in tcl_command_list])
        # 如果server_result_done存在，则删除server_result_done文件
        server_result_done_path = os.path.join(DEFAULT_CONFIG.get("api_dir"), "server_result_done")
        if os.path.exists(server_result_done_path):
            logger.debug("Deleting existing server_result_done file")
            os.remove(server_result_done_path)
        # 2. 创建client_result_done文件 --告诉EDA工具命令发送完成
        logger.info("Creating client_result_done file to signal command transmission complete")
        client_file = open(os.path.join(DEFAULT_CONFIG.get("api_dir"), "client_result_done"), "w")
        client_file.write('done')
        # 3. 等待EDA工具返回结果
        logger.info("Waiting for EDA tool to return results")
        while True:
            if os.path.exists(server_result_done_path):
                logger.debug("Server result done file detected, removing it")
                os.remove(server_result_done_path)
                break
            logger.debug("Waiting for server result done file...")
            time.sleep(1)
        # 4. 读取EDA工具返回结果, 规定结果文件为server_result.txt，按行读取存到list中返回
        logger.info("Reading results from EDA tool")
        server_result_txt_path = os.path.join(DEFAULT_CONFIG.get("api_dir"), "server_result.txt")
        if not os.path.exists(server_result_txt_path):
            logger.warning("Server result file does not exist, returning empty list")
            return []
        server_file = open(server_result_txt_path, "r")
        result = [s.rstrip('\n') for s in server_file.readlines()]
        logger.info(f"Successfully read {len(result)} lines from server result")
        return result


    # 发送tcl脚本
    def send_tcl_file(self, tcl_file_path):
        logger.info(f"Sending TCL file: {tcl_file_path}")
        # 1. 读取tcl文件
        with open(tcl_file_path, "r", encoding="utf-8") as f:
            tcl_command_list = f.readlines()
        logger.info(f"Loaded {len(tcl_command_list)} commands from TCL file")
        # 2. 发送tcl命令
        result = self.send_tcl(tcl_command_list)
        logger.info(f"TCL file execution completed, received {len(result)} lines of result")
        return result

if __name__ == '__main__':
    tcl_sender = TCLSender()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    result = tcl_sender.send_tcl_file(os.path.join(current_dir,"get_all_cell_info.tcl"))
    print(result)