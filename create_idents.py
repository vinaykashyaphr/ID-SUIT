import os
import pathlib
import re
import sys
import subprocess
from lxml import etree

from generalfunctions.helper_classes import Exclusion, LogBuilder, NameAndCode, Write_DOC
from validateEntities import valent


class IdGeneration():

    def figures(self, dmroot: etree._Element, file: str, GC: dict, ID: dict, choice: str):
        dmcont = dmroot.find('.//content')
        all_figures = dmcont.findall('.//figure')
        for i, figure in enumerate(all_figures):
            i = i+1
            fid = 'fig-'+f"{int(i):04}"
            try:
                old_figid = figure.attrib['id']
                figure.attrib['id'] = fid
                GC.update({file+'||'+fid: old_figid})
                ID.update({fid: old_figid})
                logger.info(
                    'Replacing old id:: {0} by {1}'.format(old_figid, fid))
            except KeyError:
                figure.attrib['id'] = fid
                GC.update({file+'||'+fid: None})
                ID.update({fid: None})
                logger.info('Generating figure ID:: {0}'.format(fid))

            if 'gra' in choice:
                self.graphics(figure, fid, file, GC, ID, dmroot, choice)

    def graphics(self, figure, fid, file, GC, ID, dmroot, choice):
        all_graphics = figure.findall('graphic')
        for b, graphic in enumerate(all_graphics):
            b = b + 1
            gid = fid+'-gra-'+f"{int(b):04}"
            try:
                old_graid = graphic.attrib['id']
                graphic.attrib['id'] = gid
                GC.update({file+'||'+gid: old_graid})
                ID.update({gid: old_graid})
                logger.info(
                    'Replacing old id:: {0} by {1}'.format(old_graid, gid))
            except KeyError:
                graphic.attrib['id'] = gid
                GC.update({file+'||'+gid: None})
                ID.update({gid: None})
                logger.info('Generating graphic ID:: {0}'.format(gid))

            if 'hsp' in choice:
                self.hotspots(graphic, gid, file, GC, ID, dmroot)

    def hotspots(self, graphic, gid, file, GC, ID, dmroot):
        all_hotspots = graphic.findall('hotspot')
        for l, hotspot in enumerate(all_hotspots):
            try:
                old_hotid = hotspot.attrib['id']
                autoid = hotspot.attrib['applicationStructureIdent']
                CH.update({file+'||'+old_hotid: gid+'-'+autoid})
                hotspot.attrib['id'] = gid+'-'+autoid
                GC.update({file+'||'+gid+'-'+autoid: old_hotid})
                ID.update({gid+'-'+autoid: old_hotid})
                logger.info('Replacing old id:: {0} by {1}'.format(
                    old_hotid, gid+'-'+autoid))
                intrefs = dmroot.findall(
                    './/internalRef/[@internalRefId]')

                for irf in intrefs:
                    if (irf.attrib['internalRefId'] == old_hotid) and (irf != None):
                        irf.attrib['internalRefId'] = gid+'-'+autoid

            except KeyError:
                hotspot.attrib['id'] = gid+'-'+autoid
                GC.update({file+'||'+gid+'-'+autoid: None})
                ID.update({gid+'-'+autoid: None})
                logger.info(
                    'Generating hotspot ID:: {0}'.format(gid+'-'+autoid))

        HSP = {}
        [(h.getparent().remove(h), HSP.update(
            {h.attrib['id']: h})) for h in all_hotspots]
        [graphic.insert(0, HSP[hsp]) for hsp in HSP]

    def reason_for_update(self, dmroot, file, ID, GC):
        dmiss = dmroot.find('.//identAndStatusSection')
        all_rfus = dmiss.findall('.//reasonForUpdate')
        for a, rfu in enumerate(all_rfus):
            a = a+1
            try:
                old_rfuid = rfu.attrib['id']
                rfu.attrib['id'] = 'rfu-'+f"{int(a):03}"
                ID.update({'rfu-'+f"{int(a):03}": old_rfuid})
                GC.update({file+'||'+'rfu$$'+f"{int(a):03}": old_rfuid})
                logger.info('Replacing old id:: {0} by {1}'.format(
                    old_rfuid, 'rfu-'+f"{int(a):03}"))
            except KeyError:
                rfu.attrib['id'] = 'rfu-'+f"{int(a):03}"
                ID.update({'rfu-'+f"{int(a):03}": None})
                GC.update({file+'||'+'rfu-'+f"{int(a):03}": None})
                logger.info('Generating RFU ID:: {0}'.format(
                    'rfu-'+f"{int(a):03}"))

    def tables(self, dmroot, file, ID, GC):
        dmcont = dmroot.find('.//content')
        all_tables = dmcont.findall('.//table')
        if all_tables != []:
            for b, table in enumerate(all_tables):
                b = b+1
                try:
                    old_tabid = table.attrib['id']
                    table.attrib['id'] = 'tab-'+f"{int(b):04}"
                    ID.update({'tab-'+f"{int(b):04}": old_tabid})
                    GC.update({file+'||'+'tab$$'+f"{int(b):04}": old_tabid})
                    logger.info('Replacing old id:: {0} by {1}'.format(
                        old_tabid, 'tab-'+f"{int(b):04}"))
                except KeyError:
                    table.attrib['id'] = 'tab-'+f"{int(b):04}"
                    ID.update({'tab-'+f"{int(b):04}": None})
                    GC.update({file+'||'+'tab-'+f"{int(b):04}": None})
                    logger.info('Generating table ID:: {0}'.format(
                        'tab-'+f"{int(b):04}"))

    def levelled_paras(self, dmroot, file, ID, GC):
        dmcont = dmroot.find('.//content')
        all_lvps = dmcont.findall('.//levelledPara/[@id]')
        if all_lvps != []:
            for c, lvp in enumerate(all_lvps):
                c = c+1
                old_lvpid = lvp.attrib['id']
                if old_lvpid != 'par-1111':
                    lvp.attrib['id'] = 'par-'+f"{int(c):04}"
                    ID.update({'par-'+f"{int(c):04}": old_lvpid})
                    GC.update({file+'||'+'par-'+f"{int(c):04}": old_lvpid})
                    logger.info('Replacing old id:: {0} by {1}'.format(
                        old_lvpid, 'par-'+f"{int(c):04}"))

    def paras(self, dmroot, file, ID, GC):
        dmcont = dmroot.find('.//content')
        all_paras = dmcont.findall('.//para/[@id]')
        if all_paras != []:
            for d, para in enumerate(all_paras):
                d = d+1
                old_paraid = para.attrib['id']
                para.attrib['id'] = 'para-'+f"{int(d):04}"
                ID.update({'para-'+f"{int(d):04}": old_paraid})
                GC.update({file+'||'+'para-'+f"{int(d):04}": old_paraid})
                logger.info('Replacing old id:: {0} by {1}'.format(
                    old_paraid, 'para-'+f"{int(d):04}"))

    def procedural_steps(self, dmroot, file, ID, GC):
        dmcont = dmroot.find('.//content')
        all_steps = dmcont.findall('.//proceduralStep/[@id]')
        if all_steps != []:
            for e, step in enumerate(all_steps):
                e = e+1
                old_stepid = step.attrib['id']
                if old_stepid != 'stp-1111':
                    step.attrib['id'] = 'stp-'+f"{int(e):04}"
                    ID.update({'stp-'+f"{int(e):04}": old_stepid})
                    GC.update({file+'||'+'stp-'+f"{int(e):04}": old_stepid})
                    logger.info('Replacing old id:: {0} by {1}'.format(
                        old_stepid, 'stp-'+f"{int(e):04}"))

    def multimedias(self, dmroot, file, ID, GC):
        dmcont = dmroot.find('.//content')
        all_mm = dmcont.findall('.//multimediaObject/[@id]')
        if all_mm != []:
            for f, mm in enumerate(all_mm):
                f = f+1
                old_mmid = mm.attrib['id']
                mm.attrib['id'] = 'mmo-'+f"{int(f):04}"
                ID.update({'mmo-'+f"{int(f):04}": old_mmid})
                GC.update({file+'||'+'mmo-'+f"{int(f):04}": old_mmid})
                logger.info('Replacing old id:: {0} by {1}'.format(
                    old_mmid, 'mmo-'+f"{int(f):04}"))


class InternalReference():

    def review(self, dmroot, ID):
        logger.info('Updating Internal references')
        intrefs = dmroot.findall('.//internalRef/[@internalRefId]')
        IDCOMPILE = {'fig-[0-9]{4}': 'irtt01',
                     'tab-[0-9]{4}': 'irtt02',
                     'par-[0-9]{4}': 'irtt07',
                     'stp-[0-9]{4}': 'irtt08',
                     'fig-[0-9]{4}-gra-[0-9]{4}': 'irtt09',
                     'mmo-[0-9]{4}': 'irtt10',
                     'para-[0-9]{4}': 'irtt51',
                     'fig-[0-9]{4}-gra-[0-9]{4}-\w+': 'irtt11',
                     'sup-[0-9]{4,5}': 'irtt04',
                     'seq-[0-9]{4,5}': 'irtt05',
                     'spa-[0-9]{4}': 'irtt06'
                     }
        for iref in intrefs:
            for ident in ID:
                if iref.attrib['internalRefId'] == ID[ident]:
                    iref.attrib['internalRefId'] = str(
                        ident).replace('-', '##')

        for x in intrefs:
            x.attrib['internalRefId'] = x.attrib['internalRefId'].replace(
                '##', '-')

        for y in intrefs:
            for idc in IDCOMPILE:
                if re.match(r'{0}'.format(idc), str(y.attrib['internalRefId'])) is not None:
                    y.attrib['internalRefTargetType'] = IDCOMPILE[idc]

        rfurefs = dmroot.findall('.//*/[@reasonForUpdateRefIds]')
        for rref in rfurefs:
            for refs in ID:
                if rref.attrib['reasonForUpdateRefIds'] == ID[refs]:
                    rref.attrib['reasonForUpdateRefIds'] = refs.replace(
                        '-', '@@')
        for y in rfurefs:
            y.attrib['reasonForUpdateRefIds'] = str(
                y.attrib['reasonForUpdateRefIds']).replace('@@', '-')
        return dmroot


class Commencement():
    GC = {}

    def initiate(self, all_files, dirpath, choice):
        print(all_files)
        for each in all_files:
            if each.startswith('DMC-') and (each.endswith('.xml') or each.endswith('.XML')):
                ID = {}
                file = valent(each, dirpath)
                logger.info('Parsing XML:: {0}'.format(file))
                fileparser = etree.XMLParser(no_network=True, recover=True)
                parsedxml = etree.parse(file, fileparser)
                dmroot = parsedxml.getroot()

                if 'fig' in choice:
                    IdGeneration().figures(dmroot, file, self.GC, ID, choice)

                if 'rfu' in choice:
                    IdGeneration().reason_for_update(dmroot, file, ID, self.GC)

                if 'tab' in choice:
                    IdGeneration().tables(dmroot, file, ID, self.GC)

                if 'lvlp' in choice:
                    IdGeneration().levelled_paras(dmroot, file, ID, self.GC)

                if 'par' in choice:
                    IdGeneration().paras(dmroot, file, ID, self.GC)

                if 'pstp' in choice:
                    IdGeneration().procedural_steps(dmroot, file, ID, self.GC)

                if 'mmo' in choice:
                    IdGeneration().multimedias(dmroot, file, ID, self.GC)

                dmroot1 = InternalReference().review(dmroot, ID)
                Write_DOC().data_module(dmroot1, file, dirpath)

        all_files2 = Exclusion().parsable_list(dirpath)
        for xml in all_files2:
            if xml.startswith('DMC-'):
                xml = valent(xml, dirpath)
                logger.info('Parsing DMC:: {0}'.format(xml))
                xmlpar = etree.XMLParser(no_network=True, recover=True)
                xmlroot = etree.parse(xml, xmlpar).getroot()
                xmlroot = self.extref_replacement(xmlroot, self.GC)
                xmlroot = self.ext_hsp_replace(xmlroot)
                Write_DOC().data_module(xmlroot, xml, dirpath)

    def extref_replacement(self, dmroot, GC):
        logger.info('Updating external references')
        extrefs = dmroot.findall('.//dmRef/[@referredFragment]')
        for eref in extrefs:
            for gc in GC:
                if GC[gc] == eref.attrib['referredFragment']:
                    if str(gc).startswith(NameAndCode().name_from_dmcode(eref.find('.//dmCode').attrib)):
                        eref.attrib['referredFragment'] = str(gc).split('||')[
                            1]
        for each in extrefs:
            each.attrib['referredFragment'] = str(
                each.attrib['referredFragment']).replace('$$', '-')
        return dmroot

    def ext_hsp_replace(self, dmroot):
        exthsp = dmroot.findall('.//dmRef/[@referredFragment]')
        for href in exthsp:
            for ch in CH:
                if str(ch).split('||')[1] == href.attrib['referredFragment']:
                    if str(ch).startswith(NameAndCode().name_from_dmcode(href.find('.//dmCode').attrib)):
                        href.attrib['referredFragment'] = CH[ch]
        return dmroot


def choose_bool(user_ip):
    if user_ip == 1:
        bool_ip = True
    else:
        bool_ip = False
    return bool_ip


app_path = pathlib.Path(os.getcwd())
dirpath = pathlib.PureWindowsPath(input('Path:  ')).as_posix()
os.chdir(dirpath)

all_files = Exclusion().parsable_list(dirpath)
logger = LogBuilder().build_log(dirpath, 'id_formatting.log', 'w')
CH = {}

selection = 'fig_gra_rfu_tab_lvlp_par_pstp'.split('_')
ietm = choose_bool(0)
Commencement().initiate(all_files, dirpath, selection)
logger.info('Task Completed:: Modify idents')


if ietm == True:
   ietm_formatting = pathlib.Path(os.path.join(
       app_path, 'ietm_format/ietm_form_launch.bat'))
   os.chdir(os.path.join(app_path, 'ietm_format'))
   subprocess.call([ietm_formatting, dirpath])
