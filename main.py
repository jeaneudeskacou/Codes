import json
import argparse
import data_getter
import conf
import os

LOG_DIR = conf.LOG_DIR
OUTPUT_DIR = conf.OUTPUT_DIR
TRACE_FILE_NAME = conf.TRACE_FILE_NAME
TRACE_PATH = os.path.join(LOG_DIR, TRACE_FILE_NAME)
TABLE_MARKER = conf.TABLE_MARKER
BAD_LINE = conf.BAD_LINE
OUTPUT_FILE_EXTENTION = conf.OUTPUT_FILE_EXTENTION
LOG_LEVEL = conf.LOG_LEVEL
TRACE_PATH = conf.TRACE_PATH
LOG_PATH = conf.LOG_PATH
STAT_FILES = conf.STAT_FILES
STAT_DIR = conf.STAT_DIR
STAT_FILES = conf.STAT_FILES
START_GENERATE_REPORT_MARKER = conf.START_GENERATE_REPORT_MARKER
END_GENERATE_REPORT_MARKER = conf.END_GENERATE_REPORT_MARKER
START_KEY = conf.START_KEY
END_KEY = conf.END_KEY
TABLES = conf.TABLES

parser = argparse.ArgumentParser(description="Get table from log file")
parser.add_argument('-l', "--list", action="store_true")
parser.add_argument('-t', "--table_name", nargs='+',
                    help="Name of the table to retrieve")
parser.add_argument('-o', "--output_file", nargs='?', help="Path where results will be dump")
parser.add_argument('-a', "--all", action="store_true", help="If used alone, this option retrieve all the tables."
                                                             " If combined with --table_name, retrieve all tables"
                                                             " with the given name")
parser.add_argument('-i', "--interactive", action="store_true", help="You can choose the tables you want to retrieve"
                                                                     " in a file or just print in the terminal use the." 
                                                                     " --prompt or --prompt_only option for that")
parser.add_argument('-g', "--group", action="store_true", help="in development")
parser.add_argument('-S', "--stat_only", action="store_true", help="")
parser.add_argument('-p', '--prompt', action="store_true")
parser.add_argument('-P', '--prompt_only', action="store_true")
parser.add_argument('-c', "--count", action="store_true", help="in development")

args = parser.parse_args()
table_list = args.table_name
prompt = False
print_only = False
stat_only = False
output_file = ""

# print(f"Used trace file {TRACE_PATH}")
if args.prompt_only:
    print_only = True

if args.stat_only:
    stat_only = True

if args.prompt:
    prompt = True

if args.output_file:
    output_file = args.output_file

if args.table_name:
    lines_by_table_name = data_getter.get_tables(table_list=args.table_name, table_path=TRACE_PATH,
                                                 table_marker=TABLE_MARKER, bad_line=BAD_LINE, All=args.all)
    if args.all:
        # TODO: Gerer l'utilisation de l'option -a, (--all) combinee a celle de -t (--table_name)
        pass
    else:
        # lines_by_table_name: list({table_name: list_lines})
        if args.prompt or print_only:
            print(json.dumps(lines_by_table_name, indent=4))
        if not print_only:
            # write in file
            if args.output_file:
                data_getter.multi_dump(list_of_tables=lines_by_table_name, table_marker=TABLE_MARKER,
                                       output_dir=OUTPUT_DIR, output_filename=output_file,
                                       write_to_multiple_files=False)
            else:
                # group tables in one file or one file by table
                if args.group:
                    data_getter.multi_dump(list_of_tables=lines_by_table_name,table_marker=TABLE_MARKER,
                                           output_dir=OUTPUT_DIR,
                                           output_filename=data_getter.get_output_file(OUTPUT_DIR, OUTPUT_FILE_EXTENTION,
                                                                                       default=True),
                                           write_to_multiple_files=True)
                else:
                    data_getter.multi_dump(list_of_tables=lines_by_table_name,table_marker=TABLE_MARKER,
                                           output_dir=OUTPUT_DIR, output_filename=None, write_to_multiple_files=False)

if args.list:
    table_list = data_getter.get_table_list_by_pos(TRACE_PATH, TABLE_MARKER)
    table_list = [pair[0] for pair in table_list]
    table_list.sort()
    for table in table_list:
        print(table)

if args.interactive:
    data_getter.main_by_pos(log_path=LOG_PATH, start_marker=START_GENERATE_REPORT_MARKER,
                            end_marker=END_GENERATE_REPORT_MARKER, start_key=START_KEY, end_key=END_KEY, table_key=TABLES,
                            trace_path=TRACE_PATH, table_marker=TABLE_MARKER, bad_line=BAD_LINE,
                            file_extention=OUTPUT_FILE_EXTENTION, outuput_dir=OUTPUT_DIR, print_only=print_only,
                            from_stats_only=stat_only, prompt=prompt, stat_file_list=STAT_FILES)

if __name__ == '__main__':
    data_getter.main_by_pos(log_path=LOG_PATH, start_marker=START_GENERATE_REPORT_MARKER,
                            end_marker=END_GENERATE_REPORT_MARKER, start_key=START_KEY, end_key=END_KEY,
                            table_key=TABLES,
                            trace_path=TRACE_PATH, table_marker=TABLE_MARKER, bad_line=BAD_LINE,
                            file_extention=OUTPUT_FILE_EXTENTION, outuput_dir=OUTPUT_DIR, print_only=print_only,
                            from_stats_only=True, prompt=prompt, stat_file_list=STAT_FILES)