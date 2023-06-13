import glob
import logging
import os
import pathlib
import sys

import pandas as pd
from lxml import etree

from common_functions import LogBuilder, Write_DMC
from validateEntities import valent


def spec(lastelem: etree._Element, root: etree._Element, choice, logger: logging.Logger):
    sheets = {'warn': pd.read_excel(entxl, 'WARNINGS'),
              'caut': pd.read_excel(entxl, 'CAUTIONS'),
              'seq': pd.read_excel(entxl, 'TOOLS'),
              'sup': pd.read_excel(entxl, 'SUPPLIES'),
              'ent': pd.read_excel(entxl, 'VENDORS')}
    if lastelem.tag == 'warningSpec':
        warning_compilation(sheets, root, lastelem, choice, logger)
    elif lastelem.tag == "cautionSpec":
        caution_compilation(sheets, root, lastelem, choice, logger)
    elif lastelem.tag == "toolSpec":
        tool_compilation(sheets, root, lastelem, choice, logger)
    elif lastelem.tag == 'supplySpec':
        supply_compilation(sheets, root, lastelem, choice, logger)
    elif lastelem.tag == 'enterpriseSpec':
        enterprise_compilation(sheets, root, lastelem, choice, logger)


def warning_compilation(sheets: dict, root: etree._Element, lastelem: etree._Element,
                        choice: bool, logger: logging.Logger):
    warn_id = list(sheets['warn']['Warning ID'])
    warn_para = list(sheets['warn']['Warning Para'])
    previous_warn = root.findall('.//warningSpec[@id]')
    existing_warn = [pre_warn.attrib['id'] for pre_warn in previous_warn]

    if warn_id != []:
        for k, warnid in enumerate(warn_id):
            if choice == True:
                if warnid not in existing_warn:
                    warn_spec = '''\n<warningSpec id="{0}">\
<warningIdent warningIdentNumber="{0}"/><warningAndCautionPara>{1}\
</warningAndCautionPara></warningSpec>\n'''.format(warnid, warn_para[k])
                    warn_element = etree.fromstring(warn_spec)
                    logger.info('Adding warning:: {0}'.format(warnid))
                    lastelem.addnext(warn_element)
                else:
                    logger.info(
                        'THIS WARNING ALREADY EXISTS: {0}'.format(warnid))
            else:
                removable_warns = root.findall(
                    './/warningSpec[@id="{0}"]'.format(warnid))
                logger.info('Removing warning:: {0}'.format(warnid))
                [remw.getparent().remove(remw)
                    for remw in removable_warns if removable_warns != []]


def caution_compilation(sheets: dict, root: etree._Element, lastelem: etree._Element,
                        choice: bool, logger: logging.Logger):
    caut_id = list(sheets['caut']['Caution ID'])
    caut_para = list(sheets['caut']['Caution Para'])
    previous_caut = root.findall('.//cautionSpec[@id]')
    existing_caut = [pre_caut.attrib['id'] for pre_caut in previous_caut]

    if caut_id != []:
        for j, cautid in enumerate(caut_id):
            if choice == True:
                if cautid not in existing_caut:
                    caut_spec = '''\n<cautionSpec id="{0}">\
<cautionIdent cautionIdentNumber="{0}"/><warningAndCautionPara>{1}\
</warningAndCautionPara></cautionSpec>\n'''.format(cautid, caut_para[j])
                    caut_element = etree.fromstring(caut_spec)
                    logger.info('Adding caution:: {0}'.format(cautid))
                    lastelem.addnext(caut_element)
                else:
                    logger.info(
                        'THIS CAUTION ALREADY EXISTS: {0}'.format(cautid))
            else:
                removable_cauts = root.findall(
                    './/cautionSpec[@id="{0}"]'.format(cautid))
                logger.info('Removing caution:: {0}'.format(cautid))
                [remc.getparent().remove(remc)
                    for remc in removable_cauts if removable_cauts != []]


def tool_compilation(sheets: dict, root: etree._Element, lastelem: etree._Element,
                     choice: bool, logger: logging.Logger):
    tool_id = list(sheets['seq']['Tool ID'])
    tool_name = list(sheets['seq']['Tool Name'])
    tool_shortname = list(sheets['seq']['Tool Shortname'])
    tool_number = list(sheets['seq']['Tool Number'])
    tool_cage = list(sheets['seq']['Manufacturer Code'])
    previous_seq = root.findall('.//toolSpec/toolIdent[@id]')
    existing_seq = [pre_seq.attrib['id'] for pre_seq in previous_seq]
    if tool_id != []:
        for i, toolid in enumerate(tool_id):
            if choice == True:
                if toolid not in existing_seq:
                    tool_spec = '''\n<toolSpec>\
<toolIdent id="{0}" manufacturerCodeValue="{4}" \
toolNumber="{1}"/>\
<itemIdentData><descrForPart>{2}</descrForPart>\
<shortName>{3}</shortName>\
</itemIdentData>\
<procurementData>\
<enterpriseRef manufacturerCodeValue="{4}"><dmRef \
xlink:href="DMC-HONAERO-A-00-00-00-00A-00KA-D.xml" xmlns:xlink="http://www.w3.org/1999/xlink">\
<dmRefIdent><dmCode assyCode="00" disassyCode="00" disassyCodeVariant="A" infoCode="00K" \
infoCodeVariant="A" itemLocationCode="D" modelIdentCode="HONAERO" \
subSubSystemCode="0" subSystemCode="0" systemCode="00" \
systemDiffCode="A"/></dmRefIdent></dmRef></enterpriseRef>\
</procurementData>\
<techData></techData>\
<toolAlts><tool>\
<itemDescr>Not applicable</itemDescr>\
<taskCategory taskCategoryCode="maintenance"/></tool></toolAlts>\
</toolSpec>\n'''.format(toolid, tool_number[i], tool_name[i], tool_shortname[i], tool_cage[i])
                    tool_element = etree.fromstring(tool_spec)
                    logger.info('Adding tool:: {0}'.format(toolid))
                    lastelem.addnext(tool_element)
                else:
                    logging.info(
                        'THIS TOOL ALREADY EXISTS: {0}'.format(toolid))
            else:
                removable_tools = root.xpath(
                    './/toolSpec[child::toolIdent/@id="{0}"]'.format(toolid))
                logger.info('Removing tool:: {0}'.format(toolid))
                [remt.getparent().remove(remt)
                    for remt in removable_tools if removable_tools != []]


def supply_compilation(sheets: dict, root: etree._Element, lastelem: etree._Element,
                       choice: bool, logger: logging.Logger):
    sup_id = list(sheets['sup']['Supply ID'])
    sup_name = list(sheets['sup']['Supply Name'])
    sup_shortname = list(sheets['sup']['Supply Shortname'])
    sup_number = list(sheets['sup']['Supply Number'])
    sup_cage = list(sheets['sup']['Manufacturer Code'])
    previous_sup = root.findall('.//supplySpec/supplyIdent[@id]')
    existing_sup = [pre_sup.attrib['id'] for pre_sup in previous_sup]
    if sup_id != []:
        for l, supid in enumerate(sup_id):
            if choice == True:
                if supid not in existing_sup:
                    sup_spec = '''\n<supplySpec>\
<supplyIdent id="{0}" supplyNumber="{1}" \
supplyNumberType="sp01"/>\
<name>{2}</name>\
<shortName>{3}</shortName>\
<enterpriseGroup><enterpriseInfo locallySuppliedFlag="0">\
<enterpriseRef manufacturerCodeValue="{4}"><dmRef \
xlink:href="DMC-HONAERO-A-00-00-00-00A-00KA-D.xml" xmlns:xlink="http://www.w3.org/1999/xlink"><dmRefIdent><dmCode \
assyCode="00" disassyCode="00" disassyCodeVariant="A" infoCode="00K" \
infoCodeVariant="A" itemLocationCode="D" modelIdentCode="HONAERO" \
subSubSystemCode="0" subSystemCode="0" systemCode="00" \
systemDiffCode="A"/></dmRefIdent></dmRef></enterpriseRef>\
</enterpriseInfo></enterpriseGroup></supplySpec>\n'''.format(supid, sup_number[l],
                                                             sup_name[l], sup_shortname[l], sup_cage[l])
                    sup_element = etree.fromstring(sup_spec)
                    logger.info('Adding cosumable:: {0}'.format(supid))
                    lastelem.addnext(sup_element)
                else:
                    logger.info(
                        'THIS SUPPLY ALREADY EXISTS: {0}'.format(supid))
            else:
                removable_cons = root.xpath(
                    './/supplySpec[child::supplyIdent/@id="{0}"]'.format(supid))
                logger.info('Removing cosumable:: {0}'.format(supid))
                [rems.getparent().remove(rems)
                    for rems in removable_cons if removable_cons != []]


def enterprise_compilation(sheets: dict, root: etree._Element, lastelem: etree._Element,
                           choice: bool, logger: logging.Logger):
    ent_id = list(sheets['ent']['Enterprise ID'])
    ent_val = list(sheets['ent']['Vendor Code'])
    ent_name = list(sheets['ent']['Enterprise Name'])
    unit_name = list(sheets['ent']['Business Unit Name'])
    street = list(sheets['ent']['Street'])
    zip_code = list(sheets['ent']['Pin Code'])
    city = list(sheets['ent']['City'])
    country = list(sheets['ent']['Country'])
    state = list(sheets['ent']['State'])
    phone = list(sheets['ent']['Phone Num'])
    internet = list(sheets['ent']['Website'])
    previous_ent = root.findall('.//enterpriseSpec/enterpriseIdent[@id]')
    existing_ent = [pre_ent.attrib['id'] for pre_ent in previous_ent]
    if ent_id != []:
        for m, vendor in enumerate(ent_id):
            if choice == True:
                if vendor not in existing_ent:
                    ent_spec = '''\n<enterpriseSpec>\
<enterpriseIdent id="{0}" manufacturerCodeValue="{1}"/>\
<enterpriseName>{2}</enterpriseName>\
<businessUnit>\
<businessUnitName>{3}</businessUnitName>\
<businessUnitAddress>\
<street>{4}</street>\
<postalZipCode>{5}</postalZipCode>\
<city>{6}</city>\
<country>{7}</country>\
<state>{8}</state>\
<phoneNumber>{9}</phoneNumber>\
<internet>{10}</internet>\
</businessUnitAddress>\
</businessUnit>\
</enterpriseSpec>\n'''.format(vendor, ent_val[m], ent_name[m], unit_name[m],
                            street[m], zip_code[m], city[m], country[m], state[m],
                            phone[m], internet[m])
                    ent_element = etree.fromstring(ent_spec)
                    logger.info('Adding enterprise:: {0}'.format(vendor))
                    lastelem.addnext(ent_element)
                else:
                    logger.info(
                        'THIS VENDOR ALREADY EXISTS: {0}'.format(vendor))
            else:
                removable_ents = root.xpath(
                    './/enterpriseSpec[child::enterpriseIdent/@id="{0}"]'.format(vendor))
                logger.info('Removing enterprise:: {0}'.format(vendor))
                [reme.getparent().remove(reme)
                    for reme in removable_ents if removable_ents != []]


def get_reference(content: etree._Element, filename: str):
    if content.find('warningRepository') != None:
        reference = content.find('.//warningSpec[last()]')
    elif content.find('cautionRepository') != None:
        reference = content.find('.//cautionSpec[last()]')
    elif content.find('toolRepository') != None:
        reference = content.find('.//toolSpec[last()]')
    elif content.find('.//supplyRepository') != None:
        reference = content.find('.//supplySpec[last()]')
    elif content.find('.//enterpriseRepository') != None:
        reference = content.find('.//enterpriseSpec[last()]')
    else:
        raise FileNotFoundError(
            'The file is not a repository: {0}'.format(filename))
    return reference


def repo_parse(action):
    reponames = glob.glob("DMC-HONAERO-*-00LA-*.xml") + \
        glob.glob("DMC-HONAERO-*-00NA-*.xml") + \
        glob.glob("DMC-HONAERO-*-0A4A-*.xml") + \
        glob.glob("DMC-HONAERO-*-0A5A-*.xml") + \
        glob.glob("DMC-HONAERO-*-00KA-*.xml")

    logger = LogBuilder().build_log(folderpath, 'id_compilation.log', 'w')
    logger.info('Loading...')
    for each in reponames:
        repo = valent(each, folderpath)
        par = etree.XMLParser(no_network=True)
        reporoot = etree.parse(repo, par).getroot()
        rootelement = reporoot.find('.//content/commonRepository')
        reference = get_reference(rootelement, repo)
        logger.info('Obtained repository reference:: {0}'.format(reference))
        spec(reference, reporoot, action, logger)
        Write_DMC(reporoot, repo, folderpath)
    logger.info('Task copleted: Ident Compilation')


def choose_bool(user_ip):
    if user_ip == 1:
        bool_ip = True
    else:
        bool_ip = False
    return bool_ip


folderpath = pathlib.Path(sys.argv[1])  # input('Path:  '))
os.chdir(folderpath)
entxl = pathlib.Path(os.path.join(folderpath, 'id_compilation_template.xlsx'))
selections = str(sys.argv[2]).split('_')  # "warn_caut_sup_seq_ent".split('_')
task = choose_bool(int(sys.argv[3]))

repo_parse(task)
