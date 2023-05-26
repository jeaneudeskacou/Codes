import os
import xml.etree.ElementTree as ET

import conf
import data_getter

STAT_DIR = conf.STAT_DIR
STAT_FILES = conf.STAT_FILES
LOG_DIR = conf.LOG_DIR
TRACE_PATH = conf.TRACE_PATH


def get_tables_names_from_stat_files(stat_file_list=STAT_FILES):
    # TODO: Sortir toutes les tables attendues pour un fichier stat donnée. Aller plus loin que les requests et les
    #  cassandraAdapter: Les tables au niveau de l'inventaire
    """
    Retrieve a list containing request name from the stat files given.
    Stat files should respect StatReport.xsd
    :param stat_file_list: list of stat file
    :return: request name of in this form {stat_file: list_of_tableAliasResult}
    """
    _tables_by_filename = {}
    for stat_filename in stat_file_list:
        stat_path = os.path.join(STAT_DIR, stat_filename)
        with open(stat_path, 'r') as stat_file:
            tree = ET.parse(stat_file)
            root = tree.getroot()
            entities = root.findall("./inventory/entityType")
            entities_name = [name for name in list(map(lambda entity: entity.get("type"), entities))]
            filters = root.findall("./inventory/filter")
            filters_name = [name for name in list(map(lambda _filter: f"{_filter.get('type')}_FILTER", filters))]
            links = root.findall("./inventory/link")
            link_name = [name for name in list(map(lambda _link: f"{_link.get('type')}_LINK", links))]
            requests = root.findall("./computeBlocks/queries/request")
            cassandraAdapters = root.findall("./dataSourceList/dataSource/CassandraAdapter")
            requests_name = [name for name in list(map(lambda req: req.get("tableAliasResult"), requests)) if
                             name is not None]
            cassandraAdapters_name = [name for name in list(map(lambda c_adpt: c_adpt.get("tableAlias"), cassandraAdapters))]
            _tables_by_filename[stat_filename] = entities_name + filters_name + link_name + requests_name + cassandraAdapters_name
    return merge_table_name(_tables_by_filename)


def merge_table_name(_tables_by_filename: dict):
    name_list = list(_tables_by_filename.values())
    for i in name_list[1::]:
        name_list[0].extend(i)
    return set(name_list[0])


if __name__ == '__main__':
    tables_by_filename = get_tables_names_from_stat_files()
    table_list = merge_table_name(tables_by_filename)
    table_list_by_pos = data_getter.get_table_list_by_pos(TRACE_PATH, )
    rest_table_list = list(filter(lambda pair: pair[0] in table_list, table_list_by_pos))
    lines = data_getter.get_tables_by_pos(rest_table_list, TRACE_PATH)
    output_path = os.path.join(LOG_DIR, "sortie.txt")
    data_getter.multi_dump(lines, output_path)
