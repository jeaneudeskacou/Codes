import json
import os.path
import xml.etree.ElementTree as ET

REPORT_CONFIG_PATH = r"C:\OpenStat\workspace-openstat\OpenStat\openstat-parent\arbrrt\src\main\resources\global\provisioning\reportConfig\DATA-RE_INTERACTIVE.xml"
REPORT_PATH = r"C:\OpenStat\workspace-openstat\OpenStat\openstat-parent\arbrrt\src\main\resources\global\provisioning\report\report.xml"


def get_report_config(report_config_path=REPORT_CONFIG_PATH, filters=None):
    """
    :param report_config_path:
    :param filters: dict {filter_name: value}
    :return:
    """
    report_config_file = ET.parse(report_config_path)
    report_config_list = report_config_file.findall('reportConfig')
    report_config_set = []
    for report_config in report_config_list:
        report_ref_id = report_config.get("reportRefId")
        report_output = os.path.basename(report_config.find('reportOutput/uri').text)
        if filters is not None:
            keep_report_config = filter_xml_elm(report_config, filters)
            if keep_report_config:
                report_config_set.append({"REFID": report_ref_id, "OUTPUT_FILE": report_output})
        else:
            report_config_set.append({"REFID": report_ref_id, "OUTPUT_FILE": report_output})
    return report_config_set


def find_report(report_config_set, report_path=REPORT_PATH):
    result = {}
    reports_from_report_config = []
    for report_config in report_config_set:
        reports_from_report_config.append(report_config["REFID"])
    report_file = ET.parse(report_path)
    report_file_list = filter(lambda report: report.find('refId').text in reports_from_report_config, report_file.findall('report'))
    for report in report_file_list:
        result[report.find('refId').text] = {"STAT": os.path.basename(report.find('computeUri').text), "OUTPUT": report_config_set[reports_from_report_config.index(report.find('refId').text)]['OUTPUT_FILE']}
        # print(f"{report.find('refId').text} :: {os.path.basename(report.find('computeUri').text)} :: {report_config_set[reports_from_report_config.index(report.find('refId').text)]['OUTPUT_FILE']}")
    return result


def filter_xml_elm(elm, filters):
    """
    Determine si l'element xml elm correspond ou non au filtre filters.
    :param elm:
    :param filters:
    :return:
    """
    keep_elm = True
    for key, val_obj in filters.items():
        candidate_val = elm.find(f".//{key}")
        # On considère qu'on filtre sur des attributs si on passe un dict comme valeur
        if type(val_obj) == dict:
            for attrib_name, attrib_val in val_obj.items():
                current_val = candidate_val.attrib[attrib_name]
                if type(attrib_val) == list:
                    if current_val.upper() not in [val.upper() for val in attrib_val]:
                        keep_elm = False
                        break
                elif type(attrib_val) == str:
                    if current_val.upper() != attrib_val.upper():
                        keep_elm = False
                        break
        elif type(val_obj) == list:
            if candidate_val.text is None or candidate_val.text.upper() not in [val.upper() for val in val_obj]:
                keep_elm = False
                break
    return keep_elm


if __name__ == '__main__':
    # report_ref_id_set = get_report_config(REPORT_CONFIG_PATH, filters={"paramType": ["ACCESS"]})
    report_ref_id_set = get_report_config(filters={"paramType": {"alias": "ACCESS"}})
    result = find_report(report_ref_id_set)
    print(json.dumps(result, indent=4))
    print(len(result))
