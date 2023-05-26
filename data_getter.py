import csv
import glob
import json
import os
import re
import time
from datetime import datetime

from tabulate import tabulate

import OpenStatLogManager
import conf

LOG_LEVEL = conf.LOG_LEVEL
ALL_INDEX = 0
RANGE_SEPARATOR = "-"
STAT_FILES = conf.STAT_FILES


def get_tables_by_pos(table_list_by_pos, trace_path, table_marker, bad_line):
    """
    Retrieve tables provided by table_list_by_pos.
    This method is intended to improve the get_tables() method.
    The search is done by "jumping" to the next position register in table_list_by_pos
    :param table_list_by_pos: [(table_name, pos)] where pos is the start line of the table in the file
    :param path: path of the trace file
    :return: a list of dict of this form {table_name: list_of_lines}
    """
    if LOG_LEVEL.value >= conf.LOG_LEVEL_ENUM.INFO.value: print("Tables reading")
    big_start_time = time.time()
    lines_by_table_name = []
    current_pos = 1
    last_pos = table_list_by_pos[-1][1]
    with open(trace_path) as table_file:
        line = table_file.readline()
        while not current_pos > last_pos:
            target_name, target_pos = table_list_by_pos.pop(0)
            while current_pos != target_pos and line != '':
                line = table_file.readline()
                current_pos += 1
            timestamp = line.split('|')[0]
            line = table_file.readline()
            current_pos += 1
            lines = []
            if LOG_LEVEL == conf.LOG_LEVEL_ENUM.DEBUG: print(
                f"\tReading of table: {target_name} at line {target_pos}...")
            start_time = time.time()
            while line != '' and line.find(table_marker) == -1 and line.find("Message  :") == -1:
                line = table_file.readline()
                current_pos += 1
                if line.find(bad_line) > -1 or line.find("Message  :") > -1:
                    continue
                lines.append(line)
            lines_by_table_name.append({target_name: lines, "timestamp": timestamp})
            if LOG_LEVEL == conf.LOG_LEVEL_ENUM.DEBUG: print(
                f"\tTable {target_name} at line {target_pos} read in: {(time.time() - start_time)}ms")
        if LOG_LEVEL == conf.LOG_LEVEL_ENUM.DEBUG: print(f"Tables read in : {(time.time() - big_start_time)}ms")
    return lines_by_table_name


def get_table_list_by_pos(trace_path, table_marker):
    pattern = r"(?<=Start log content for table ).*"
    regex = re.compile(pattern)
    tables_by_pos = []
    pos = 0
    with open(trace_path, 'r') as log_file:
        line = log_file.readline()
        pos += 1
        while line != '':
            if line.find(table_marker) > -1:
                name = regex.search(line)
                tables_by_pos.append((name.group(0), pos))
                line = log_file.readline()
                pos += 1
            else:
                line = log_file.readline()
                pos += 1
    return tables_by_pos


def get_tables(table_list, trace_path, table_marker, bad_line, ALL=False):
    """
    Retrieve tables provided by table_list.
    The search is done from the beginning to the end of the file looking for a table marker using regex. Once found,
    the table is read until another table marker is found or the end of file is reached.
    :param table_list:
    :param trace_path:
    :return: a list of dict of this form {table_name: list_of_lines}
    """
    if LOG_LEVEL.value >= conf.LOG_LEVEL_ENUM.INFO.value: print("Tables reading")
    lines_by_table_name = []
    pattern = r"(?<=Start log content for table ).*"
    regex = re.compile(pattern)
    with open(trace_path) as table_file:
        line = table_file.readline()
        # Recherche de table
        while line != '':
            while line.find(table_marker) == -1 and line != '':
                line = table_file.readline()
            if line == '':
                break
            # Verifie si le nom de la table est dans la list
            name = regex.search(line).group(0)
            timestamp = line.split('|')[0]
            if name in table_list:
                if LOG_LEVEL == conf.LOG_LEVEL_ENUM.DEBUG: print(f"\tReading of table: {name}...")
                start_time = time.time()
                # Lecture de la table
                lines = []
                line = table_file.readline()
                while line != '' and line.find(table_marker) == -1 and line.find('Message ') == -1:
                    line = table_file.readline()
                    if line.find(bad_line) > -1 or line.find("Message  :") > -1:
                        continue
                    lines.append(line)
                lines_by_table_name.append({name: lines, "timestamp": timestamp})
                if LOG_LEVEL == conf.LOG_LEVEL_ENUM.DEBUG: print(
                    f"\tTable {name} read in: {(time.time() - start_time)}ms")
            else:
                line = table_file.readline()
    if LOG_LEVEL.value >= conf.LOG_LEVEL_ENUM.INFO.value: print("Tables reading finish")
    return lines_by_table_name


def multi_dump(list_of_tables, table_marker, output_dir, file_extention, output_filename=None,
               write_to_multiple_files=False):
    """
    Use to dump selected tables either in one file or in a file by table
    """
    if LOG_LEVEL.value >= conf.LOG_LEVEL_ENUM.INFO.value: print("Tables writing")
    if write_to_multiple_files:
        if LOG_LEVEL.value >= conf.LOG_LEVEL_ENUM.INFO.value: print("\t Writing in multiple files")
        for table_dict in list_of_tables:
            table_name = list(table_dict.keys())[0]
            timestamp = table_dict["timestamp"]
            lines = table_dict[table_name]
            table_id = f"{timestamp} | {table_marker} {table_name} \n"
            output_path = get_output_file(output_dir, file_extention, table_name, timestamp)
            with open(output_path, 'w') as output_file:
                output_file.write(table_id)
                output_file.writelines(lines)
                if LOG_LEVEL.value >= conf.LOG_LEVEL_ENUM.INFO.value: print(f"\t File {output_path} created")
    else:
        if LOG_LEVEL.value >= conf.LOG_LEVEL_ENUM.INFO.value: print("\t Writing in single file")
        with open(output_filename, 'w') as output_file:
            for table_dict in list_of_tables:
                table_name = list(table_dict.keys())[0]
                timestamp = table_dict["timestamp"]
                lines = table_dict[table_name]
                table_id = f"{timestamp} | {table_marker} {table_name} \n"
                output_file.write(table_id)
                output_file.writelines(lines)
            if LOG_LEVEL.value >= conf.LOG_LEVEL_ENUM.INFO.value: print(f"\t Output file at {output_filename}")


def multi_dump_by_stat(table_by_stat, table_key, table_marker, output_dir, file_extention, start_key):
    """
    Used to dump tables by stat files
    """
    if LOG_LEVEL.value >= conf.LOG_LEVEL_ENUM.INFO.value: print("\t Writing in multiple files")
    for stat in table_by_stat:
        if start_key in table_by_stat[stat].keys():
            timestamp = table_by_stat[stat][start_key]
            output_path = get_output_file(output_dir, file_extention, stat, timestamp)
            with open(output_path, 'w') as output_file:
                for table in table_by_stat[stat][table_key]:
                    table_name = list(table.keys())[0]
                    timestamp = table["timestamp"]
                    lines = table[table_name]
                    table_id = f"{timestamp} | {table_marker} {table_name} \n"
                    output_file.write(table_id)
                    output_file.writelines(lines)
                if LOG_LEVEL.value >= conf.LOG_LEVEL_ENUM.INFO.value: print(f"\t File {output_path} created")


def show_table_list(table_list):
    for index, pair in enumerate(table_list):
        print(f"{index + 1}/ {pair[0]} at line: {pair[1]}")
    print(f"{ALL_INDEX}/ CHOOSE ALL")
    list_of_choices = input("Choose your tables: ")
    if list_of_choices == "":
        return None
    else:
        if RANGE_SEPARATOR in list_of_choices:
            list_of_choices = list_of_choices.split(RANGE_SEPARATOR)
            list_of_choices = range(int(list_of_choices[0]), int(list_of_choices[-1]) + 1)
        else:
            list_of_choices = list_of_choices.split(",")
        return list(map(lambda x: int(x), list_of_choices))


def main_by_pos(trace_path, table_marker, bad_line, outuput_dir, file_extention, log_path=None, start_marker=None,
                end_marker=None, start_key=None, end_key=None, table_key=None, output_path=None, prompt=False,
                print_only=False, from_stats_only=False, stat_file_list=None):
    table_list = get_table_list_by_pos(trace_path, table_marker)
    if from_stats_only:
        tables_from_stat = OpenStatLogManager.get_tables_names_from_stat_files()
        table_list = list(filter(lambda table: table[0] in tables_from_stat, table_list))
        log_path_list = get_log_file_list(log_path)
        print(log_path_list)
        stat_by_timestamp = {}
        for current_log_path in log_path_list:
            current_stat_by_timestamp = get_stat_file_timestamp(current_log_path, stat_file_list, start_marker, end_marker, start_key,
                                    end_key, table_key)
            print(current_stat_by_timestamp)
            stat_by_timestamp.update(current_stat_by_timestamp)
    _continue = True
    while _continue:
        chose_index_list = show_table_list(table_list)
        if chose_index_list is None:
            exit()
        if ALL_INDEX in chose_index_list:
            selected_table_list = table_list
        else:
            selected_table_list = list(filter(lambda pair: table_list.index(pair) + 1 in chose_index_list, table_list))
        lines_by_table_name = get_tables_by_pos(selected_table_list, trace_path, table_marker, bad_line)
        if from_stats_only:
            # Filtrer les lignes et mettre celles retenues dans stat_by_timestamp
            match_stat_timestamp_and_lines(stat_by_timestamp, lines_by_table_name, start_key, end_key, table_key)
        if output_path is None:
            output_path = get_output_file(outuput_dir, file_extention, default=True)
        if prompt or LOG_LEVEL.value == LOG_LEVEL.DEBUG.value:
            # print(json.dumps(lines_by_table_name, indent=4))
            print_tables(lines_by_table_name)
        if not print_only:
            if from_stats_only:
                multi_dump_by_stat(stat_by_timestamp, table_key, table_marker, outuput_dir, file_extention, start_key)
            else:
                multi_dump(lines_by_table_name, table_marker, outuput_dir, file_extention, output_path)
        enter = input("Continue? y/n: ")
        _continue = True if enter == "y" else False


def get_log_file_list(log_path):
    return glob.glob(log_path + "*")

def match_stat_timestamp_and_lines(stat_by_timestamp, tables_by_timestamp, start_key, end_key, table_key):
    for table in tables_by_timestamp:
        for stat in stat_by_timestamp.values():
            if start_key in stat and end_key in stat:
                if compare_timestamp(table["timestamp"], stat[start_key], stat[end_key]):
                    stat[table_key].append(table)


def get_stat_file_timestamp(log_path, stat_file_list, start_marker, end_marker, start_key, end_key, table_key):
    stat_file_by_timestamp = {}
    # init stat_dic
    for stat_file in stat_file_list:
        stat_file_by_timestamp[stat_file] = {table_key: []}
    with open(log_path, 'r') as log_file:
        start_pattern = r"(?<= Start : ).*"
        end_pattern = r"(?<= End : ).*"
        start_regex = re.compile(start_pattern)
        end_regex = re.compile(end_pattern)
        line = log_file.readline()
        _continue = True
        not_visited = len(stat_file_list)
        while _continue:
            while line != '' and line.find(start_marker) == -1 and line.find(end_marker) == -1:
                line = log_file.readline()
            if line == '' or not_visited == 0:
                _continue = False
                break
            if line.find(start_marker) > -1:
                stat_path = start_regex.search(line).group(0).split('/')[-1]
                if stat_path in stat_file_list:
                    line = log_file.readline()
                    start_timestamp = line.split('|')[0]
                    stat_file_by_timestamp[stat_path].update({start_key: start_timestamp})
                else:
                    line = log_file.readline()
            elif line.find(end_marker) > -1:
                stat_path = end_regex.search(line).group(0).split('/')[-1].split(" ")[0]
                if stat_path in stat_file_list:
                    line = log_file.readline()
                    end_timestamp = line.split('|')[0]
                    stat_file_by_timestamp[stat_path].update({end_key: end_timestamp})

                    if start_key in stat_file_by_timestamp[stat_path] and end_key in stat_file_by_timestamp[stat_path]:
                        not_visited -= 1
                else:
                    line = log_file.readline()
        return stat_file_by_timestamp


def get_output_file(output_dir, file_extention, base_name=None, timestamp=None, default=False):
    _time = datetime.now().isoformat().replace(':', '-')
    if default:
        output_path = os.path.join(output_dir, f"output_{_time}.{file_extention}")
        return output_path
    else:
        if base_name:
            if timestamp:
                _time = timestamp.strip().replace(' ', 'T').replace(':', '-').replace(',', '.')
            output_path = os.path.join(output_dir, f"{base_name}_{_time}.{file_extention}")
            return output_path


def compare_timestamp(target, start_timestamp, end_timestamp):
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


def print_tables(lines_by_table_name):
    for table_lines_dict in lines_by_table_name:
        for table_name, lines in table_lines_dict.items():
            if table_name == "timestamp":
                continue
            print(table_name)
            splited_lines = map(lambda line: line.split('|'), lines)
            print(tabulate(splited_lines, headers="firstrow"))

