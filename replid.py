import logging
import os
import pathlib
import sys

import pandas as pd
from lxml import etree

from common_functions import Exclusion, LogBuilder, Write_DMC
from validateEntities import valent


class SheetParsing():
    def start(self, all_files: list, choice: list):
        DF = {'warn': pd.read_excel(entxl, 'WARNINGS'),
              'caut': pd.read_excel(entxl, 'CAUTIONS'),
              'seq': pd.read_excel(entxl, 'TOOLS'),
              'sup': pd.read_excel(entxl, 'SUPPLIES'),
              'othr': pd.read_excel(entxl, 'OTHERS')}
        logger = LogBuilder().build_log(dirpath, 'id_replacement.log', 'w')

        for frame in list(DF.keys()):
            if frame in choice:
                for file in all_files:
                    if (file.startswith('DMC-HON') or file.startswith('PMC-HON')) and (file.endswith('.xml') or file.endswith('.XML')):
                        file = valent(file, dirpath)
                        logger.info("Parsing file - {0}".format(file))
                        par = etree.XMLParser(no_network=True, recover=True)
                        dmroot = etree.parse(file, par).getroot()
                        cxt = dmroot.xpath(
                            '//*[self::content or self::identAndStatusSection]')

                        for element in cxt:
                            if frame == 'warn':
                                warn_dict = {}
                                [warn_dict.update({oldx: DF[frame]['NEW'][x]})
                                 for x, oldx in enumerate(DF[frame]['OLD'])]
                                FunctionEquips().modify_warncaut(
                                    element, 'warningRefs', 'cautionRefs', warn_dict, logger)

                            elif frame == 'caut':
                                caut_dict = {}
                                [caut_dict.update({oldy: DF[frame]['NEW'][y]})
                                 for y, oldy in enumerate(DF[frame]['OLD'])]
                                FunctionEquips().modify_warncaut(
                                    element, 'cautionRefs', 'warningRefs', caut_dict, logger)

                            elif (frame == 'sup') or (frame == 'seq'):
                                sup_dict = {}
                                [sup_dict.update({oldz: DF[frame]['NEW'][z]})
                                 for z, oldz in enumerate(DF[frame]['OLD'])]
                                FunctionEquips().modify_toolcons(
                                    element, 'internalRef', 'internalRefId', sup_dict, logger)

                            else:
                                othr_dict = {}
                                [othr_dict.update({old: DF[frame]['NEW'][o]})
                                 for o, old in enumerate(DF[frame]['OLD'])]
                                othr = str(
                                    choice[choice.index('othr')+1]).split(' ')
                                FunctionEquips().modify_toolcons(
                                    element, othr[0], othr[1], othr_dict, logger)

                        Write_DMC(dmroot, file, dirpath)
        logger.info('Task Completed :: Ident Replacement')


class FunctionEquips():

    def modify_warncaut(self, rootelem: etree._Element, attribute: str,
                        accent: str, collector: dict, logger: logging.Logger):
        element = rootelem.xpath('.//*[@{0}]'.format(attribute))

        if element != []:
            for each in element:
                attr_list = str(each.attrib[attribute]).split(' ')
                for i, attr in enumerate(attr_list):
                    for src in list(collector.keys()):
                        if attr == src:
                            logger.info("Modifying {0} as {1}".format(
                                attr_list[i], collector[src]))
                            attr_list[i] = collector[src]
                W = [w for w in attr_list if w.startswith('warn-')]
                C = [c for c in attr_list if c.startswith('caut-')]
                if attribute == "warningRefs":
                    self.warn_edit(W, C, each, attribute, accent, collector)
                else:
                    self.caut_edit(W, C, each, attribute, accent, collector)

    def warn_edit(self, warn_segr: list, caut_segr: list,
                  src_elem: etree._Element, warn_attr: str, warn_acnt: str, collector: dict):
        if warn_segr != []:
            warn_attbs = list(dict.fromkeys(
                str(src_elem.attrib[warn_attr] + " " + " ".join(warn_segr)).split(' ')))
            [warn_attbs.remove(x)
                for x in warn_attbs if x in list(collector.keys())]
            src_elem.attrib[warn_attr] = " ".join(warn_attbs)
        else:
            src_elem.attrib.pop(warn_attr)

        if caut_segr != []:
            try:
                warn_acnts = list(dict.fromkeys(
                    str(src_elem.attrib[warn_acnt] + " " + " ".join(caut_segr)).split(' ')))
            except KeyError:
                warn_acnts = caut_segr
            src_elem.attrib[warn_acnt] = " ".join(warn_acnts)

    def caut_edit(self, warn_segr: list, caut_segr: list,
                  src_elem: etree._Element, caut_attr: str, caut_acnt: str, collector: dict):
        if warn_segr != []:
            try:
                caut_acnts = list(dict.fromkeys(
                    str(src_elem.attrib[caut_acnt] + " " + " ".join(warn_segr)).split(' ')))
            except KeyError:
                caut_acnts = warn_segr
            src_elem.attrib[caut_acnt] = " ".join(caut_acnts)

        if caut_segr != []:
            caut_attbs = list(dict.fromkeys(
                str(src_elem.attrib[caut_attr] + " " + " ".join(caut_segr)).split(' ')))
            [caut_attbs.remove(y)
             for y in caut_attbs if y in list(collector.keys())]
            src_elem.attrib[caut_attr] = " ".join(caut_segr)
        else:
            src_elem.attrib.pop(caut_attr)

    def modify_toolcons(self, rootelem: etree._Element, refelem: str, attribute: str,
                        collector: dict, logger: logging.Logger):
        if attribute != '*':
            element = rootelem.xpath('.//{0}[@{1}]'.format(refelem, attribute))
            if element != []:
                for each in element:
                    for src in list(collector.keys()):
                        if each.attrib[attribute] == src:
                            logger.info("Modifying {0} as {1}".format(
                                each.attrib[attribute], collector[src]))
                            each.attrib[attribute] = "##$$"+collector[src]
                for x in element:
                    x.attrib[attribute] = str(x.attrib[attribute]).replace("##$$", '')
        else:
            element_ = rootelem.xpath('.//{0}'.format(refelem))
            if element_ != []:
                for elem in element_:
                    if elem.attrib != {}:
                        for attb in elem.attrib:
                            for orig in list(collector.keys()):
                                if elem.attrib[attb] == orig:
                                    logger.info("Modifying {0} as {1}".format(
                                        elem.attrib[attb], collector[orig]))
                                    elem.attrib[attb] = "##$$"+collector[orig]
                for y in element_:
                    y.attrib[attribute] = str(y.attrib[attribute]).replace("##$$", '')

dirpath = pathlib.Path(sys.argv[1])
filelist = Exclusion().parsable_list(dirpath)
os.chdir(dirpath)

entxl = pathlib.Path(os.path.join(dirpath, 'id_replacement_template.xlsx'))
selections = str(sys.argv[2]).split('_')

SheetParsing().start(filelist, selections)
