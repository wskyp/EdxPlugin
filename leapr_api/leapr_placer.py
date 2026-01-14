# -*- coding: utf-8 -*-
from tcl_sender import *
from leapr_config import *
from typing import Dict, List, Tuple

from leapr_config import LeaprConfig
import sys,random
import os
import time
import re
import matplotlib
import networkx as nx
import numpy as np
import argparse
import copy
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
matplotlib.use('Agg')  # Non-interactive backend for saving to files
try:
    from h_anchor_fast import Cell
    from h_anchor_fast import HAnchorPlacer, PlacementConfig, ScoringMethod
except ImportError:
    print("h_anchor_fast.py not found. Please make sure it is in the same directory as this script.")

leaprConfig = LeaprConfig()

def generate_place_cmd(cell_name: str, x: float, y: float, orient: str):
    cmd = f"place_cell {cell_name} {x:.2f} {y:.2f} -placed"
    # 百分之5%的概率打印命令
    if random.random() < 0.05:
        print(cmd)
    return cmd

def read_design() -> Design:
    tcl_sender = TCLSender(leaprConfig)
    result = tcl_sender.send_tcl_file(leaprConfig.pyc_placer_dir + "/scripts/apicommon/get_all_cell_info.tcl")
    my_design = Design()
    '''
        result列表中第2行design的core长宽，格式为：core_size: {78.12 69.192}，之后每4行一组，格式为
        u_macc_top/macc[0].u_macc/adder_out_reg[15] --cell name
        4.32 -- cell width
        1.08 --cell height
        u_macc_top/macc[0].u_macc/adder_out_reg[15]/QN|u_macc_top/macc[0].u_macc/adder_out_reg[15]/D --- all pins join with,
    '''
    core_line = result[1]  # "core_size: {78.12 69.192}"
    match = re.search(r'\{([\d.]+)\s+([\d.]+)\}', core_line)
    if match:
        my_design.core_width = float(match.group(1))
        my_design.core_height = float(match.group(2))
    row_counter = 3
    for row_index in range(3, len(result), 3):
        row_counter = row_index
        cell_name = result[row_index].strip()
        if '======' in cell_name:
            break
        prop = result[row_index+1].strip().split(",")
        cell_width = float(prop[0])
        cell_height = float(prop[1])
        cell_orient = prop[2]
        cell_place_status = prop[3]
        loc_x = prop[4]
        loc_y = prop[5]
        pin_str = result[row_index + 2].strip()
        pins = pin_str.split('|')
        for pin in pins:
            pin = pin.strip()
            if pin:  # 确保不是空字符串
                my_design.pin_to_cell[pin] = cell_name
        my_design.cells[cell_name] = [cell_name, cell_width, cell_height, cell_orient,cell_place_status,loc_x,loc_y]
    for i in range(row_counter+1,len(result)):
        # 读取net
        net_info = result[i].strip()
        if len(net_info) < 1:
            continue
        split = net_info.split(',')
        if len(split) < 3:
            print(f'net {split[0]} dont has load pins or driver pins')
            continue
        net_name = split[0]
        load_pins = split[1].split('|')
        driver_pins = split[2].split('|')
        my_design.nets[net_name] = [load_pins, driver_pins]
    return my_design

def run_placement(design: Design, send_tcl: bool = True):
    # Run placement
    leaprConfig.output_info("Running H-Anchor placement...")
    placer = leaprConfig.global_placer
    graph, cells = generate_case_design(design)
    placer.load_netlist(graph, cells)
    #
    start = time.time()
    pos = placer.run()
    # 遍历pos,执行place命令
    tcl_sender = TCLSender(leaprConfig)
    tcl_cmd = []
    for cell_name, position in pos.items():
        # print(f"cell name: {cell_name}, x={pos[0]:.2f},y={pos[1]:.2f}")
        tcl_cmd.append(generate_place_cmd(cell_name, position[0], position[1], "R0"))
    if send_tcl:
        tcl_sender.send_tcl(tcl_cmd)
    place_time = time.time() - start
    #
    leaprConfig.output_info(placer.get_placement_stats())
    leaprConfig.output_info(f"\n  Placement time: {place_time:.2f} seconds")
    leaprConfig.output_info(f"  Throughput: {len(cells) / place_time:.0f} cells/sec")


def generate_case_design(design_info:Design) -> Tuple[nx.Graph, Dict[str, Cell]]:
    """
        将一个design解析成算法需要的格式: nx.Graph
        design_info中存储了全量cell，每个cell包含的所有pin，以及每个pin所属的net。构建图时，忽略掉pin，把pin的net看成是cell的net,
        如果两个cell之间有多个Net,构件图时这两个cell的边权重就是之间连接net的数量
    """
    G = nx.Graph()
    cells = {cell[0]: Cell(id=cell[0], width=cell[1], height=cell[2], module=cell[0].split('/')[0] if '/' in cell[0] else cell[0], x=float(cell[5]), y = float(cell[6]), legal_x=float(cell[5]), legal_y=float(cell[6])) for cell in design_info.cells.values()}

    #计算cell之间的连接以及权重,先获取每个cell的net,然后两个cell的net有条，则weight+1
    leaprConfig.output_info(f"generate case design for {len(design_info.nets)}...")
    not_find_cell_pin_counter = 0
    for net_name in design_info.nets.keys():
        load_pins = design_info.nets[net_name][0]
        driver_pins = design_info.nets[net_name][1]
        for driver_pin in driver_pins:
            for load_pin in load_pins:
                if load_pin in design_info.pin_to_cell and driver_pin in design_info.pin_to_cell:
                    load_cell = design_info.pin_to_cell[load_pin]
                    driver_cell = design_info.pin_to_cell[driver_pin]
                    from_to_cell = tuple(sorted([driver_cell, load_cell]))
                    if G.has_edge(from_to_cell[0], from_to_cell[1]):
                        G[driver_cell][load_cell]['weight'] += 1 # 如果两个cell之间有多个Net,构件图时这两个cell的边权重就是之间连接net的数量
                    else:
                        G.add_edge(from_to_cell[0], from_to_cell[1], weight=1) # 默认权重为1
                else:
                    not_find_cell_pin_counter+=1
    # 存在没有连接的cell，需要加到图里
    for cell_name in cells.keys():
        if not G.has_node(cell_name):
            G.add_node(cell_name)
    # Add some random long-distance connections (global signals like clock, reset)
    leaprConfig.output_info(f"the graph edges is {G.number_of_edges()}, the node num is {G.number_of_nodes()}, new cell is {len(cells)}")
    return G, cells

def run_incremental_placement():
    '''
       运行增量add node的场景
       读取当前的design，与global_design做对比。
            如果有cell删除，则对删除的cell及其影响的cell重新做增量place
            如果有cell新增，则对新增的cell及其影响的cell重新做place
            如果有net删除，则对删除的net影响的cell重新做place
            如果有net增家，则对增加的net影响 的cell做增量place
    '''
    leaprConfig.output_debug("Running incremental placement...")
    current_design = read_design()
    add_cell_list = list(set(current_design.cells.keys()) - set(leaprConfig.global_design.cells.keys()))
    del_cell_list = list(set(leaprConfig.global_design.cells.keys()) - set(current_design.cells.keys()))

    old_edges = {}
    load_drivers = leaprConfig.global_design.nets.values()
    for load_driver in load_drivers:
        for driver_pin in load_driver[1]:
            for load_pin in load_driver[0]:
                if load_pin in leaprConfig.global_design.pin_to_cell and driver_pin in leaprConfig.global_design.pin_to_cell:
                    load_cell = leaprConfig.global_design.pin_to_cell[load_pin]
                    driver_cell = leaprConfig.global_design.pin_to_cell[driver_pin]
                    key = tuple(sorted([driver_cell, load_cell]))
                    old_edges[key] = old_edges.get(key, 0) + 1
    new_edges = {}
    load_drivers = current_design.nets.values()
    for load_driver in load_drivers:
        for driver_pin in load_driver[1]:
            for load_pin in load_driver[0]:
                if load_pin in current_design.pin_to_cell and driver_pin in current_design.pin_to_cell:
                    load_cell = current_design.pin_to_cell[load_pin]
                    driver_cell = current_design.pin_to_cell[driver_pin]
                    key = tuple(sorted([driver_cell, load_cell]))
                    new_edges[key] = new_edges.get(key, 0) + 1
    # new_edges-old_edges代表新增的edge
    add_edges = {}
    for key in new_edges.keys():
        if old_edges.get(key, 0) == 0:
            add_edges[key] = new_edges[key]
    # 删除edge的场景
    del_edges = {}
    for key in old_edges.keys():
        if new_edges.get(key, 0) == 0:
            del_edges[key] = old_edges[key]
    # 处理新增cell的场景
    new_cells = {}
    if len(add_cell_list) > 0:
        for cell_name in add_cell_list:
            cell = current_design.cells[cell_name]
            new_cells[cell[0]] = Cell(id=cell[0], width=cell[1], height=cell[2], module=cell[0].split('/')[0] if '/' in cell[0] else cell[0])
    leaprConfig.output_debug(f'=====new cell size is {len(new_cells)}')
    total_affected_cells = set()
    # 运行新增场景
    n_cells, affected_cells = leaprConfig.global_placer.add_nodes(new_cells, [(k[0],k[1], v) for k,v in add_edges.items()])
    total_affected_cells.update(affected_cells)
    # 运行删除node场景
    if len(del_cell_list) > 0:
        node_to_idx, affected_cells = leaprConfig.global_placer.remove_nodes(del_cell_list)
        total_affected_cells.update(affected_cells)
    # 运行删除边场景
    if len(del_edges) > 0:
        affected_cells = leaprConfig.global_placer.remove_edges([(k[0],k[1]) for k,v in del_edges.items()])
        total_affected_cells.update(affected_cells)

    tcl_sender = TCLSender(leaprConfig)
    tcl_cmd = []
    leaprConfig.output_debug(f'=========affecte cell is {len(total_affected_cells)}==========')
    for cell_name in affected_cells:
        if cell_name in leaprConfig.global_placer.legal_positions:
            pos = leaprConfig.global_placer.legal_positions[cell_name]
            tcl_cmd.append(generate_place_cmd(cell_name, pos[0], pos[1], "R0"))
    leaprConfig.output_info(f'incremental place {len(tcl_cmd)} cells')
    leaprConfig.global_design = current_design
    tcl_sender.send_tcl(tcl_cmd)
    leaprConfig.output_debug(f' incremental place done')

def split_design_by_cell(cell_list: List[str], design: Design):
    '''
        将design中在cell_list中的cell移除，跟cell关联的pin和net也要一并移除
    '''
    for cell_name in cell_list:
        # design.cells删除cell_name这个key
        design.cells.pop(cell_name)
        design.pin_to_cell = {pin: cell for pin, cell in design.pin_to_cell.items() if cell != cell_name}
        design.nets = {net_name: [[pin for pin in net_pins[0] if pin in design.pin_to_cell],
                                 [pin for pin in net_pins[1] if pin in design.pin_to_cell]]
                      for net_name, net_pins in design.nets.items()}
        design.nets = {net_name: net_pins for net_name, net_pins in design.nets.items() if net_pins[0] and net_pins[1]}

def setup_argparse():
    parser = argparse.ArgumentParser(description='PycPlacer 增量布局工具')
    parser.add_argument('--design', default='asap7_scr', help='设计名称')
    parser.add_argument('--cell-ratio', type=float, default=0.1, help='增量cell比例')
    parser.add_argument('--mode', choices=['local', 'plugin'],
                        default='local', help='执行模式')
    parser.add_argument('--api-dir', default='', help='API目录')
    parser.add_argument('--pyc-dir', default='', help='PycPlacer目录')

    return parser

def cmd_pyc_reset():
    # 启动读取全局网表信息
    design = read_design()
    leaprConfig.global_design = design

    config = PlacementConfig(
        num_layers=8,
        top_layer_size=30,  # Smaller top layer for more layers
        decimation_factor=0.4,  # Smoother layer progression
        die_width=design.core_width,
        die_height=design.core_height,
        top_layer_iterations=300,
        refinement_iterations=100,
        repulsion_strength=3.0,  # Increased repulsion to spread cells
        attraction_strength=0.03,  # Reduced attraction to avoid clustering
        overlap_repulsion=5.0,  # Strong overlap prevention
        min_spacing=10.0,  # Minimum spacing between cells
        center_gravity=0.02,  # Gentle center pull
    )
    placer = HAnchorPlacer(config)
    leaprConfig.global_placer = placer
    leaprConfig.output_info("reset pyc success...")
    leaprConfig.output_info(f'   cell count: {len(design.cells)}')
    leaprConfig.output_info(f'   pin count: {len(design.pin_to_cell)}')
    leaprConfig.output_info(f'   net count: {len(design.nets)}')

def cmd_pyc_reset_only_incremental():
    leaprConfig.output_debug(f'enter cmd_pyc_reset_only_incremental...')
    cmd_pyc_reset()
    # 将global_design.cells中，placed的cell过滤出来
    removed_cell = [cell_name for cell_name, cell_info in leaprConfig.global_design.cells.items() if 'placed' != cell_info[4]]
    split_design_by_cell(removed_cell, leaprConfig.global_design)
    graph, cells = generate_case_design(leaprConfig.global_design)
    leaprConfig.global_placer.load_netlist_with_exist_positions(graph, cells)
    leaprConfig.output_info("cmd_pyc_reset_only_incremental success...")
    leaprConfig.output_info(f'   cell count: {len(leaprConfig.global_design.cells)}')
    leaprConfig.output_info(f'   pin count: {len(leaprConfig.global_design.pin_to_cell)}')
    leaprConfig.output_info(f'   net count: {len(leaprConfig.global_design.nets)}')

def cmd_pyc_global_placement(select_ratio: float = 1):
    # 选出一部分不参与global placement的cell, 按比例选取，默认选取design.cells中的10%，这里直接通过numpy随机选取
    cell_names = list(leaprConfig.global_design.cells.keys())
    removed_cell = np.random.choice(cell_names, int(len(cell_names) * (1-select_ratio)), replace=False).tolist()
    global_place_design = copy.deepcopy(leaprConfig.global_design)
    split_design_by_cell(removed_cell, global_place_design)
    run_placement(global_place_design)

def get_cell_positions(cell_list: List[str]):
    for cell in cell_list:
        x,y = leaprConfig.global_placer.get_position(cell)
        leaprConfig.output_info(f'{cell} position: ({x:.2f},{y:.2f}), id is {leaprConfig.global_placer.get_cell_id(cell)}')
    tcl_sender = TCLSender(leaprConfig)
    tcl_sender.send_tcl(['echo "^v^"'])

def get_cell_name_by_id(cell_id_list: List[str]):
    for id in cell_id_list:
        cell_name = leaprConfig.global_placer.get_cell_name(int(id))
        leaprConfig.output_info(f'cell id: {id}, name: {cell_name}')

def get_cell_num():
    leaprConfig.output_info(f'cell count: {len(leaprConfig.global_placer.cells)}')

def load_timing_path():
    leaprConfig.output_info('load timing path...')
    leaprConfig.refresh_sta(os.path.join(leaprConfig.api_dir, 'report'))

def cmd_report_timing(path_num: int):
    leaprConfig.print_sta(path_num)

# 执行命令，要考虑有些命令以及对应的函数有些参数，所以这里要考虑
def run_command(cmd: str):
    # 解析命令和参数，命令与参数之间用空格分割
    parts = cmd.strip().split()
    if not parts:
        leaprConfig.output_info('命令不能为空')
        return
    
    cmd_name = parts[0]
    cmd_args = parts[1:]  # 获取命令后的所有参数
    
    cmds = {
        'pyc_reset': (cmd_pyc_reset, 0, False),  # 无需参数
        'pyc_reset_only_increment': (cmd_pyc_reset_only_incremental, 0, False), # 无需参数，重置pycplacer并加载已有布局
        'pyc_global_placement': (cmd_pyc_global_placement, 1, False),  # 需要一个参数，布局网表的%多少，值从0-1
        'pyc_increment_placement': (run_incremental_placement, 0, False),  # 需要一个参数（cell列表）,运行PycPlacer的GP+inremental
        'pyc_get_cell': (get_cell_positions, 1, True),
        'pyc_get_name': (get_cell_name_by_id, 1, True),
        'pyc_refresh_timing': (load_timing_path, 0, False),
        'pyc_report_timing': (cmd_report_timing, 1, True)
    }
    
    if cmd_name not in cmds:
        leaprConfig.output_info(f'command {cmd_name} not found')
        return
    func, expected_arg_count, required_args = cmds[cmd_name]
    
    if required_args and (len(cmd_args) != expected_arg_count):
        leaprConfig.output_info(f'命令 {cmd_name} 需要 {expected_arg_count} 个参数，但提供了 {len(cmd_args)} 个参数')
        return
    if cmd_name == 'pyc_get_cell' or cmd_name == 'pyc_get_name':
        # 增量放置，参数应该一个cell名称列表，以逗号分隔
        cell_list = cmd_args[0].replace('{', '').replace('}', '').strip(',').split(',')
        func(cell_list)
        return
    if cmd_name == 'pyc_global_placement':
        # 全局布局，参数应该一个float值，表示布局网表的%多少，值从0-1
        if not cmd_args:
            func()
            return
        func(float(cmd_args[0]))
        return
    if 'pyc_report_timing' == cmd_name:
        func(int(cmd_args[0]))
        return
    func()

if __name__ == '__main__':
    parser = setup_argparse()
    args = parser.parse_args()
    leaprConfig.api_dir = args.api_dir
    leaprConfig.pyc_placer_dir = args.pyc_dir
    # 当leaprConfig.api_dir不以/结尾时，添加/
    if leaprConfig.api_dir[-1] != '/':
        leaprConfig.api_dir += '/'
    # 当leaprConfig.pyc_placer_dir以/结尾时，则去掉/
    if leaprConfig.pyc_placer_dir[-1] == '/':
        leaprConfig.pyc_placer_dir = leaprConfig.pyc_placer_dir[:-1]

    if args.mode == 'local':
        while True:
            print("请输入PycPlacer命令：")
            cmd = input()
            run_command(cmd)
    else:
        # 这里循环监听api_dir目录下是否有plugin_cmd_done文件，要是有，则读取plugin_cmd.txt文件
        print('PycPlacer started with plugin mode...')
        while True:
            plugin_flag_path = os.path.join(leaprConfig.api_dir , 'plugin_cmd_done')
            plugin_cmd = os.path.join(leaprConfig.api_dir , 'plugin_cmd.txt')
            if os.path.exists(plugin_flag_path):
                with open(plugin_cmd) as f:
                    leaprConfig.clear_msg_list()
                    cmd = f.read().strip()
                    run_command(cmd)
                    os.remove(plugin_flag_path)
                    os.remove(plugin_cmd)
                    # 将MSG_LIST写到api_dir目录下的plugin_msg.txt文件中
                    with open(os.path.join(leaprConfig.api_dir , 'plugin_msg.txt'), 'w') as f:
                        for msg in leaprConfig.msg_list:
                            f.write(f'{msg}\n')
                    # 写入plugin_msg_done标记文件
                    open(os.path.join(leaprConfig.api_dir , 'plugin_msg_done'), 'w').close()
                    leaprConfig.output_info('')
            time.sleep(1)
