from operator import itemgetter
from typing import Dict, List

from tabulate import tabulate
import random


def get_tables(filepath):
    f = open(filepath)

    table_name = ""
    result = {}

    for line in f.readlines():
        line = line.strip()
        if "Start log content for table " in line:
            table_name = (line.split("Start log content for table ", 1)[1].strip() + " " + str(random.randint(1000, 9999))).lower()
            result[table_name] = []
        elif any(_ in line for _ in ["Message  :", "|TRACE", "|INFO", "|DEBUG"]) or any(_ not in line for _ in ["|"]):
            # Do nothing
            pass
        else:
            if line.endswith(" |"):
                line = line[:-2]
            result[table_name].append(line.split(" | "))

    f.close()
    return result


def display_tables(tables: Dict[str, list], rows_filter: Dict[str, str] = None, columns_filter: List[str] = None, tables_filter: List[str] = None):
    """
            Parameters
            ----------
            tables (required) : Dict[str, list]
                Matrix of tables to display

            rows_filter (optional) : Dict[str, str]
                Filter for rows.
                The first element is the name of the table to filter
                The second element is the filter to apply

                WARNING : Use simple quote inside the filter sentence

                Example :
                    rows_filter={
                        "result": "IP_NETWORK_SERVICE_TYPE == 'INTERNET DIRECT' and BYTES_RECEPTION == '2994'",
                        "result_COS": "DATE in ['2022-05-01 00:00:00', '2022-06-01 00:00:00'] and BYTES_EMISSION4 == '236979'"
                    }
                The first filter will keep lines if IP_NETWORK_SERVICE_TYPE is INTERNET DIRECT  and BYTES_RECEPTION is 2994 in table result
                The second filter will keep lines if DATE is '2022-05-01 00:00:00' or '2022-06-01 00:00:00'  and BYTES_EMISSION4 is 236979 in table result_COS


            columns_filter (optional) : List[str]
                List of columns to display
                If columns are not found in a table, all table will be displayed

            tables_filter (optional) : List[str]
                List of tables to display

            """

    display_only_tables = [_.lower().strip() for _ in tables_filter]
    columns_filter = [_.strip().lower() for _ in columns_filter]
    rows_filter = dict((k.lower(), v) for k, v in rows_filter.items())

    for table_name, table_content in tables.items():

        # Handle table filter
        if display_only_tables and table_name[:-5] not in display_only_tables:
            continue
        print("\nTABLE", table_name[:-5])

        # Handle rows filter
        if rows_filter and table_name[:-5] in rows_filter.keys():
            row_filter = rows_filter.get(table_name[:-5])
            table_content_temp = []

            for line in table_content[1:]:
                local_row_filter = row_filter
                for header in table_content[0]:
                    if header in local_row_filter:
                        local_row_filter = local_row_filter.replace(header, "'"+line[table_content[0].index(header)]+"'")

                if eval(local_row_filter):
                    table_content_temp.append(line)

            table_content = [table_content.pop(0)]+table_content_temp

        # Handle columns filter
        if columns_filter:
            indexes = []
            for header in table_content[0]:
                if header.strip().lower() in columns_filter:
                    indexes.append(table_content[0].index(header))

            if len(indexes) == 1:
                table_content = [[_[indexes[0]]] for _ in table_content]
            elif len(indexes) > 1:
                table_content = [list((itemgetter(*indexes)(row))) for row in table_content]

        print(tabulate(table_content, headers='firstrow'))


trace_tables = get_tables(r"C:\OpenStat\workspace-openstat\OpenStat\openstat-parent\domain\logs\arbopr_openreport_trace.log")

display_tables(
    trace_tables,
    rows_filter={
        "total_tRaffic": "CUSTOMER_CODE == ''",
        "total_traffic_cos": "CUSTOMER_CODE == ''",
        "thirteen_last_months_by_vpn": "CUSTOMER_CODE == ''",
        "result_tmp": "CUSTOMER_CODE == ''",
        "result": "CUSTOMER_CODE == ''",
        "result_cos": "CUSTOMER_CODE == ''",
        "result_COS_tmp": "CUSTOMER_CODE == ''",
    },
    columns_filter=[],
    tables_filter=[]
)
