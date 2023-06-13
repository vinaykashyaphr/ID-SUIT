import pathlib
import sys
from lxml import etree

from common_functions import Exclusion, LogBuilder, NameAndCode, Write_DMC
from validateEntities import valent


class Commencement():

    def start(self):
        for each in all_files:
            valent(each, folderpath)
            dmodule = etree.parse(each, par).getroot()
            logger.info(f'Parsing XML: {each}')
            tagnames = {'proceduralStep': 'stp', 'levelledPara': 'par'}
            for tagname in tagnames:
                self.element_modification(dmodule, tagname, tagnames, each)
            Write_DMC(dmodule, each, folderpath)

        for dmc in all_files:
            valent(dmc, folderpath)
            logger.info(f'Parsing XML: {dmc}')
            dmc_root = etree.parse(dmc, par).getroot()
            reffrags = dmc_root.findall('.//dmRef/[@referredFragment]')
            self.externalref_update(reffrags)
            Write_DMC(dmc_root, dmc, folderpath)
        logger.info(f'Task Completed: IETM ID Introduction')

    def element_modification(self, root: etree._Element, element: str,
                             container: dict, filename: str):

        if element == list(container.keys())[0]:
            starter = root.find('.//content//mainProcedure/*')
        else:
            starter = root.find('.//content//description/*')
        if ((starter != None) and ((starter.tag == list(container.keys())[0])
                                   or (starter.tag == list(container.keys())[1]))):
            first_elem = root.find(f'.//{element}')
            if first_elem != None:
                try:
                    PRE.update({filename: first_elem.attrib['id']})
                    logger.info('Changing Existing ID {0} to {1}'.format(
                        first_elem.attrib['id'], f'{container[element]}-1111'))
                    self.internalref_update(
                        first_elem.attrib['id'], root, f'{container[element]}-1111')
                except KeyError:
                    logger.info('Generating ID {0}'.format(
                        f'{container[element]}-1111'))
                first_elem.attrib['id'] = f'{container[element]}-1111'

    def internalref_update(self, attribute: str,
                           root: etree._Element, new_attribute: str):
        intrefs = root.findall(
            './/internalRef/[@internalRefId="{0}"]'.format(attribute))
        if intrefs != []:
            for intref in intrefs:
                logger.info('Changing Internal Reference ID {0} to {1}'.format(
                    intref.attrib['internalRefId'], new_attribute))
                intref.attrib['internalRefId'] = new_attribute

    def externalref_update(self, references: list):
        for each in references:
            refname = NameAndCode().name_from_dmcode(each.find('.//dmCode').attrib)
            for pre in PRE:
                if ((PRE[pre] == each.attrib['referredFragment'])
                        and (pre.startswith(refname))):
                    file = list(folderpath.glob(f'{refname}*.xml'))[0]
                    valent(file, folderpath)
                    ref_file = etree.parse(file, par).getroot()
                    schemes = ref_file.xpath(
                        './/content/*[self::procedure or self::description]')
                    if schemes[0].tag == 'procedure':
                        logger.info('Changing External Reference ID {0} to {1}'.format(
                            each.attrib['referredFragment'], 'stp-1111'))
                        each.attrib['referredFragment'] = 'stp-1111'
                    elif schemes[0].tag == 'description':
                        logger.info('Changing External Reference ID {0} to {1}'.format(
                            each.attrib['referredFragment'], 'par-1111'))
                        each.attrib['referredFragment'] = 'par-1111'
                    else:
                        logger.warning('UNRECOGNIZED SCHEMA')


folderpath = pathlib.Path(input('Path:  '))
all_files = Exclusion().parsable_list(folderpath)
par = etree.XMLParser(no_network=True, recover=True)
logger = LogBuilder().build_log(folderpath, 'id_formatting.log', 'a')
PRE = {}
Commencement().start()
