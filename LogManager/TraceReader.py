import json
from typing import List, Tuple, Dict
import time
from tabulate import tabulate
import re
import OpenStatLogManager
from datetime import datetime
import conf


def get_report_parameter(line):
    path = line.split(':')[2].split('|')
    reporting_group = path[0]
    stat_file_name = path[1].split('/')[-1]
    return reporting_group, stat_file_name


def timestamp_is_between(target, start_timestamp, end_timestamp):
    t_target, n_target = datetime.fromisoformat(target.split(',')[0]), int(target.split(',')[-1])
    t_start_timestamp, n_start_timestamp = datetime.fromisoformat(start_timestamp.split(',')[0]), int(
        start_timestamp.split(',')[-1])
    is_after_start = False
    if_before_end = False
    if t_target >= t_start_timestamp:
        if t_target == t_start_timestamp:
            if n_target >= n_start_timestamp:
                is_after_start = True
        else:
            is_after_start = True
    if is_after_start:
        t_end_timestamp, n_end_timestamp = datetime.fromisoformat(end_timestamp.split(',')[0]), int(
            end_timestamp.split(',')[-1])
        if t_target <= t_end_timestamp:
            if t_target == t_end_timestamp:
                if n_target <= n_end_timestamp:
                    if_before_end = True
            else:
                if_before_end = True
    return is_after_start and if_before_end


class TraceReader:
    table_marker = re.compile(r"(?<=Start log content for table ).*")
    bad_line = re.compile(r"\|CorrelationId")
    start_report_marker = re.compile(r"\[generateReport.*\] Start")
    end_report_marker = re.compile(r"\[generateReport.*\] End")
    report_paramter_marker = re.compile(r"\[buildReport.*\] Start")
    inventory_marker = re.compile(r"(?<=Loading inventory ).*")
    RANGE_SEPARATOR = "-"

    def __init__(self, trace_path=None, log_path=None, stat_file_list=None):
        self.log_path = log_path
        self.trace_path = trace_path
        self.stat_file_list = stat_file_list
        self.table_name_and_line_number = self.get_tables_name_with_line_number_and_timestamp()
        self.executed_report_info = self.get_exectuted_reports_info_from_log()
        self.stat_file_list = self.set_stat_file_list(stat_file_list)
        self.executed_report_info = self.get_tables_by_stat_file()
        self.selected_tables = []
        self.content_by_table_name = {}

    def set_stat_file_list(self, stat_file_list):
        if stat_file_list is None:
            return self.executed_report_info
        else:
            corrected_stat_file_list = self.set_corrected_stat_file_list(stat_file_list)
            return [stat_file for stat_file in corrected_stat_file_list if stat_file in self.executed_report_info]

    def set_corrected_stat_file_list(self, stat_file_list):
        corrected_stat_file_list = []
        for index, stat_file in enumerate(stat_file_list):
            corrected_stat_file = stat_file.upper()
            if not stat_file.endswith("xml"):
                corrected_stat_file += ".xml"
            corrected_stat_file_list.append(corrected_stat_file)
        return corrected_stat_file_list

    def run(self):
        _continue = True
        while _continue:
            choice = self.print_stat_list()
            tables_by_stat_file = self.get_selected_tables(choice)
            print(tables_by_stat_file)
            # for stat_file in selected_table_list:
            # TODO: A la selection d'un fichier stat, lister les tables detectés
            # TODO: Gerer le cas simple où l'utilisateur entre le nom d'une table
            # print(json.dumps(table_by_stat_file, indent=4))
            _continue = input("Continue? y/Any: ") == "y"

    def get_selected_tables(self, choice: List[int]) -> Dict[str, List[Tuple[str, int, str]]]:
        selected_stat_file_list = [self.stat_file_list[i - 1] for i in choice]
        return {stat_file: self.executed_report_info[stat_file]["TABLES"] for stat_file in
                selected_stat_file_list}

    def get_exectuted_reports_info_from_log(self) -> Dict[str, Dict]:
        stat_file_by_timestamp = {}
        with open(self.log_path) as log_file:
            for index, line in enumerate(log_file, 1):
                if self.start_report_marker.search(line):
                    report_execution_info = self.get_report_execution_info(log_file)
                    stat_file_name = report_execution_info[0][1]
                    stat_file_by_timestamp[stat_file_name] = {
                        "REPORTING_GROUP": report_execution_info[0][0],
                        "START_TIME": report_execution_info[1],
                        "END_TIME": report_execution_info[2],
                        "INVENTORY": report_execution_info[3]
                    }
        return stat_file_by_timestamp

    def get_report_execution_info(self, log_file):
        line = log_file.readline()
        starttime = line.split('|')[0]
        inventory_path = ""
        while not self.is_end_of_report(line):
            if self.report_paramter_marker.search(line):
                parameter = get_report_parameter(line)
            if not inventory_path and self.inventory_marker.search(line):
                inventory_path = self.inventory_marker.search(line).group(0).split(' ')[0]
            line = log_file.readline()
        line = log_file.readline()
        endtime = line.split('|')[0]
        return [parameter, starttime, endtime, inventory_path]

    def is_end_of_report(self, line):
        return self.end_report_marker.search(line)

    def get_tables_name_with_line_number_and_timestamp(self) -> List[Tuple[str, int, str]]:
        tables_name_and_line_number = []
        with open(self.trace_path) as trace_file:
            for index, line in enumerate(trace_file, 1):
                if table_name := self.table_marker.search(line):
                    tables_name_and_line_number.append((table_name.group(0), index, line.split('|')[0]))
        return tables_name_and_line_number

    def get_tables_by_stat_file(self):
        for stat_file_name in self.executed_report_info.keys():
            current_stat_file = self.executed_report_info[stat_file_name]
            for table in self.table_name_and_line_number:
                if timestamp_is_between(table[2], current_stat_file["START_TIME"], current_stat_file["END_TIME"]):
                    current_stat_file.setdefault("TABLES", []).append(table)
            # current_stat_file['TABLES'] = self.get_tables(current_stat_file["TABLES"])
        return self.executed_report_info

    def get_tables(self, selected_tables: List[Tuple[str, int]] = None) -> Dict[str, List[str]]:
        content_by_table_name = {}
        # filtered_table_list = self.filter_table_list(selected_tables)
        table_indexes = list(map(lambda table_index: table_index[1], selected_tables))
        with open(self.trace_path) as trace_file:
            for index, line in enumerate(trace_file, 1):
                if index in table_indexes:
                    table_name = selected_tables[table_indexes.index(index)][0]
                    lines = self.read_current_table(trace_file)
                    content_by_table_name[table_name] = lines
        return content_by_table_name

    def read_current_table(self, trace_file):
        lines = []
        trace_file.readline()
        line = trace_file.readline()
        while not self.is_stop_line(line):
            lines.append(line.split('|'))
            line = trace_file.readline()
        return lines

    def is_stop_line(self, line):
        return line == '' or self.table_marker.search(line) or self.bad_line.search(line)

    def print_tables(self, tables) -> None:
        for table_name, lines in tables.items():
            header = lines.pop(0)
            print(f"Table name: {table_name}")
            print(tabulate(lines, headers=header))
            print(len(lines))

    def print_tables_by_stat_file(self, tables_by_stat_file):
        for stat_file_name, tables in tables_by_stat_file:
            current_stat_file = self.executed_report_info[stat_file_name]
            print(stat_file_name)
            for table in tables:
                print(f"\t{table}")
                lines = current_stat_file["TABLES"][table]
                header = lines.pop(0)
                print(tabulate(lines, headers=header), '\n')

    def print_stat_list(self):
        for index, stat_file_name in enumerate(self.stat_file_list, 1):
            print(f"{index}/ {stat_file_name}")
        print("0/ CHOOSE ALL")
        list_of_choices = input("Choose your tables: ")
        if list_of_choices == "":
            return None
        else:
            if self.RANGE_SEPARATOR in list_of_choices:
                list_of_choices = list_of_choices.split(self.RANGE_SEPARATOR)
                list_of_choices = range(int(list_of_choices[0]), int(list_of_choices[-1]) + 1)
            else:
                list_of_choices = list_of_choices.split(",")
            return list(map(lambda x: int(x), list_of_choices))


class ReportInfo:
    def __init__(self):
        self.stat_file_list


if __name__ == '__main__':
    _trace_path = conf.TRACE_PATH
    _log_path = conf.LOG_PATH
    stat_file_list = ["STAT_report_1337", "STAT", "stat_report_1370"]
    trace_reader = TraceReader(trace_path=_trace_path, log_path=_log_path, stat_file_list=stat_file_list)
    trace_reader.run()
    # table = [("VPN_CUSTOMER_LIST", 24746, "2023-05-24 15:19:21,177")]
    # content = trace_reader.get_tables(table)
    # trace_reader.print_tables(content)
