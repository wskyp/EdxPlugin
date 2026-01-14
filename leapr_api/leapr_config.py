import sys
import os
import matplotlib
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
matplotlib.use('Agg')  # Non-interactive backend for saving to files
try:
    from h_anchor_fast import Cell
    from h_anchor_fast import HAnchorPlacer, PlacementConfig, ScoringMethod
except ImportError:
    print("h_anchor_fast.py not found. Please make sure it is in the same directory as this script.")


class Design:
    def __init__(self):
        self._cells: Dict[str, Cell] = {}
        self._name: str = ""
        self._core_width: float = 0.0
        self._core_height: float = 0.0
        self._pin_to_cell: Dict[str, str] = {}
        self._nets: Dict[str, list[list[str]]] = {}

    @property
    def cells(self) -> Dict[str, Cell]:
        return self._cells

    @cells.setter
    def cells(self, cells: Dict[str, Cell]):
        self._cells = cells

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def core_width(self) -> float:
        return self._core_width

    @core_width.setter
    def core_width(self, core_width: float):
        self._core_width = core_width

    @property
    def core_height(self) -> float:
        return self._core_height

    @core_height.setter
    def core_height(self, core_height: float):
        self._core_height = core_height

    @property
    def pin_to_cell(self) -> Dict[str, str]:
        return self._pin_to_cell

    @pin_to_cell.setter
    def pin_to_cell(self, pin_to_cell: Dict[str, str]):
        self._pin_to_cell = pin_to_cell

    @property
    def nets(self) -> Dict[str, list[list[str]]]:
        return self._nets

    @nets.setter
    def nets(self, nets: Dict[str, list[list[str]]]):
        self._nets = nets


class TimingPath:
    """
    Timing path class for Leapr.
    """
    def __init__(self):
        self._start_point: str = ""
        self._end_point: str = ""
        self._scenario: str = ""
        self._path_group: str = ""
        self._path_type: str = ""
        self._path: list[Tuple[str, float, float]] = []
        self._data_required_time: float = 0.0
        self._data_arrival_time: float = 0.0
        self._slack: float = 0.0

    @property
    def start_point(self) -> str:
        return self._start_point

    @start_point.setter
    def start_point(self, start_point: str):
        self._start_point = start_point

    @property
    def end_point(self) -> str:
        return self._end_point

    @end_point.setter
    def end_point(self, end_point: str):
        self._end_point = end_point

    @property
    def scenario(self) -> str:
        return self._scenario

    @scenario.setter
    def scenario(self, scenario: str):
        self._scenario = scenario

    @property
    def path_group(self) -> str:
        return self._path_group

    @path_group.setter
    def path_group(self, path_group: str):
        self._path_group = path_group

    @property
    def path_type(self) -> str:
        return self._path_type

    @path_type.setter
    def path_type(self, path_type: str):
        self._path_type = path_type

    @property
    def path(self) -> list[Tuple[str, float, float]]:
        return self._path

    @path.setter
    def path(self, path: list[Tuple[str, float, float]]):
        self._path = path

    @property
    def data_required_time(self) -> float:
        return self._data_required_time

    @data_required_time.setter
    def data_required_time(self, data_required_time: float):
        self._data_required_time = data_required_time

    @property
    def data_arrival_time(self) -> float:
        return self._data_arrival_time

    @data_arrival_time.setter
    def data_arrival_time(self, data_arrival_time: float):
        self._data_arrival_time = data_arrival_time

    @property
    def slack(self) -> float:
        return self._slack

    @slack.setter
    def slack(self, slack: float):
        self._slack = slack


class STA:
    """
    Timing class for Leapr.
    """
    def __init__(self):
        self._timing_paths: List[TimingPath] = []

    @property
    def timing_paths(self) -> List[TimingPath]:
        return self._timing_paths

    @timing_paths.setter
    def timing_paths(self, timing_paths: List[TimingPath]):
        self._timing_paths = timing_paths


class LeaprConfig:
    """
    Configuration class for Leapr.
    定义API_DIR变量， 作为类变量
    """

    def __init__(self):
        self.api_dir = '/data/wskyp/cases/top_ASAP7/api/'
        self.debug_mode = False
        self.pyc_placer_dir = '/data/wskyp/PycPlacer'
        self.msg_list = []
        self.case_name = 'asap7_scr'
        self.global_placer: HAnchorPlacer = None  # 需要指定类型，但当前没有合适的类型定义
        self.global_design: Design = None
        self.sta: STA = STA()

    def set_api_dir(self, api_dir: str):
        self.api_dir = api_dir

    def set_debug_mode(self, debug_mode: bool):
        self.debug_mode = debug_mode

    def set_pyc_placer_dir(self, pyc_placer_dir: str):
        self.pyc_placer_dir = pyc_placer_dir

    def clear_msg_list(self):
        self.msg_list = []

    def output_info(self, msg: str):
        now = datetime.now()
        # 格式化为字符串
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[PYC_PLACER][INFO][{formatted_time}] {msg}")
        self.msg_list.append(msg)

    def output_debug(self, msg: str):
        if self.debug_mode:
            now = datetime.now()
            # 格式化为字符串
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[PYC_PLACER][DEBUG][{formatted_time}] {msg}")

    def get_api_dir(self) -> str:
        return self.api_dir

    def get_debug_mode(self) -> bool:
        return self.debug_mode

    def get_pyc_placer_dir(self) -> str:
        return self.pyc_placer_dir

    def get_case_name(self):
        return self.case_name

    def get_global_placer(self) -> HAnchorPlacer:
        return self.global_placer

    def get_global_design(self) -> Design:
        return self.global_design

    def refresh_sta(self, report_file):
        # 读文
        '''
            Startpoint: u_macc_top/macc[3].u_macc/sload_reg_reg/QN (rising edge-triggered flip-flop clocked by clk_m)
            Endpoint: u_macc_top/macc[3].u_macc/adder_out_reg[13]/D (falling edge-triggered flip-flop clocked by clk_m)
            Common Pin: clk_m
            Scenario: func_WorstLT_cworst_CCworst_T
            Path Group: REG2REG
            Path Type: max

            Point                                                                            Incr         Path
            -------------------------------------------------------------------------------------------------------------------------
            clock clk_m (rise edge)                                                          0.000        0.000
            clock network delay (ideal)                                                      0.000        0.000
            u_macc_top/macc[3].u_macc/sload_reg_reg/CLK                                      0.000        0.000 r
            u_macc_top/macc[3].u_macc/adder_out_reg[13]/D (DFFHQNx1_ASAP7_75t_L)             0.000        665.700 f
            data arrival time                                                                             665.700

            clock clk_m                                                                      0.000        0.000
            clock network delay (ideal)                                                      0.000        0.000
            u_macc_top/macc[3].u_macc/adder_out_reg[13]/CLK (DFFHQNx1_ASAP7_75t_L)                        0.000
            library setup time                                                              -15.076      -15.076
            path check period                                                                1000.000     984.924
            clock reconvergence pessimism                                                    0.000        984.924
            clock uncertainty                                                               -300.000      684.924
            data required time                                                                            684.924
            -------------------------------------------------------------------------------------------------------------------------
            data required time                                                                            684.924
            data arrival time                                                                            -665.700
            -------------------------------------------------------------------------------------------------------------------------
            slack (MET)                                                                                   19.224
        '''

        with open(report_file, 'r', encoding='utf-8') as f:
            #文本格式是注释的样子，文件有很多这种路径，读取文件，解析成STA对象
            self.sta = STA()
            in_point = False
            counter = 0
            timing_path = None  # 初始化timing_path为None
            for line in f:
                if 'Startpoint:' in line:
                    # 如果之前有未完成的timing_path，将其添加到列表中
                    if timing_path is not None:
                        self.output_debug(f'Saving incomplete timing path for {timing_path.start_point}')
                        self.sta.timing_paths.append(timing_path)
                    timing_path = TimingPath()
                    timing_path.start_point = line.split(':')[1].strip().split()[0]
                    continue
                if 'Endpoint:' in line:
                    timing_path.end_point = line.split(':')[1].strip().split()[0]
                    continue
                if 'Path Group:' in line:
                    timing_path.path_group = line.split(':')[1].strip()
                    continue
                if 'Scenario:' in line:
                    timing_path.scenario = line.split(':')[1].strip()
                    continue
                if 'Path Type:' in line:
                    timing_path.path_type = line.split(':')[1].strip()
                    continue
                if 'clock network delay' in line:
                    if counter %2 == 0:
                        in_point =  True
                    else:
                        in_point = False
                    counter = counter + 1
                    continue
                if in_point:
                    if 'data arrival time' in line:
                        in_point = False
                        continue
                    # 将line按空白字符分割，空白字符包括空格、制表符、换行符等
                    point_incr_path = line.split()
                    pin_name = point_incr_path[0]
                    self.output_debug(f'line is {line}')
                    if '(' in point_incr_path[1]:
                        incr = point_incr_path[2]
                        path_delay = point_incr_path[3]
                    else:
                        incr = point_incr_path[1]
                        path_delay = point_incr_path[2]
                    timing_path.path.append((pin_name, float(incr), float(path_delay)))
                    continue
                if 'data required time' in line:
                    timing_path.data_required_time = float(line.split()[3])
                    continue
                if 'data arrival time' in line:
                    timing_path.data_arrival_time = float(line.split()[3])
                    continue
                if 'slack (' in line:
                    self.output_info(f'slack: {line}')
                    timing_path.slack = float(line.split()[2])
                    self.sta.timing_paths.append(timing_path)
                    self.output_info(f'path cell num is {len(timing_path.path)}')
                    timing_path = None  # 重置timing_path为None，准备下一个路径

    def print_sta(self, path_num = 1):
        self.output_info(f'print sta...')
        counter = 1
        for timing_path in self.sta.timing_paths:
            if counter > path_num:
                break
            self.output_info(f'-------------------------------path {counter} begin------------------------------------')
            self.output_info(f"{timing_path.start_point} ---> {timing_path.end_point}")
            self.output_info(f"path group: {timing_path.path_group}")
            self.output_info(f"scenario: {timing_path.scenario}")
            self.output_info(f"path type: {timing_path.path_type}")
            for point in timing_path.path:
                self.output_info(f"{point[0]} Incr: {point[1]} Path: {point[2]}")
            self.output_info(f"data arrival time: {timing_path.data_arrival_time}")
            self.output_info(f"data required time: {timing_path.data_required_time}")
            self.output_info(f"slack (MET): {timing_path.slack}")
            self.output_info(f'-------------------------------path {counter} end------------------------------------')
            counter = counter + 1
