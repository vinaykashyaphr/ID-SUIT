import concurrent.futures
import os
import pathlib
import signal
import subprocess
import time

import pandas as pd
import win32com.client
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.button import MDFloatingActionButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

# Window.maximize()
app_path = os.getcwd()
Builder.load_file("design.kv")
FOLDERPATH = []


class InputWizard(MDCard):
    drop_id = ObjectProperty(None)
    filePath = StringProperty('')

    def __init__(self, option=True, **kwargs):
        super(InputWizard, self).__init__(**kwargs)
        del FOLDERPATH[:]
        if option == True:
            Window.bind(on_dropfile=self._on_file_drop)

    def _on_file_drop(self, window, file_path):
        path = file_path.decode("utf-8")
        dirpath = pathlib.PureWindowsPath(str(path)).as_posix()
        self.ids.input_textbox.text = dirpath
        del FOLDERPATH[:]
        FOLDERPATH.append(self.ids.input_textbox.text)
        return self.ids.input_textbox.text


class RootLayout(BoxLayout):
    INPUT = []

    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs)
        self.figref = self.ids.checkbox_figure
        self.graref = self.ids.checkbox_graphic
        self.hotref = self.ids.checkbox_hotspot

    def all_references(self):
        if self.ids.global_checkbox.state == 'down':
            self.modify_checks('down', True)
        else:
            self.modify_checks('normal', False)

    def modify_checks(self, mark, key):
        for each in list(self.ids.keys()):
            if each.startswith('checkbox_'):
                self.ids[each].state = mark
                self.ids[each].disabled = key
                self.ids[each].disabled_color = [50/255, 180/255, 150/255, 1]

    def figure_reference(self):
        self.graref.state = 'normal'
        self.hotref.state = 'normal'

    def graphic_reference(self):
        if self.graref.state == 'down':
            self.figref.state = 'down'
        else:
            self.figref.state = 'normal'
        self.hotref.state = 'normal'

    def hotspot_reference(self):
        if self.hotref.state == 'down':
            self.graref.state = 'down'
            self.figref.state = 'down'
        else:
            self.graref.state = 'normal'
            self.figref.state = 'normal'

    def proceed_further(self):
        del self.INPUT[:]
        for each in list(self.ids.keys()):
            if each.startswith('checkbox_'):
                if self.ids[each].state == 'down':
                    self.INPUT.append(self.ids[each].name)
        self.pop_up1()
        executor = concurrent.futures.ThreadPoolExecutor()

        if FOLDERPATH != []:
            if self.INPUT != []:
                executor.submit(self.process_excecution,
                                str("_".join(self.INPUT)))
            else:
                alert1 = MDDialog(title='No Task Selected',
                                  text='Kindly select type of ident to be edited')
                self.dialog.dismiss()
                alert1.open()
        else:
            alert2 = MDDialog(title='No Input Found',
                              text='Please provide the path for data modules')
            self.dialog.dismiss()
            alert2.open()

    def pop_up1(self):
        self.dialog = MDDialog(
            size_hint=(None, None),
            width=dp(200),
            auto_dismiss=True,
            type="custom",
            content_cls=Matter(),
        )
        self.dialog.open()

    @mainthread
    def process_excecution(self, choice):
        try:
            os.chdir(pathlib.PureWindowsPath(os.path.join(
                app_path, r'source/create_idents')).as_posix())
            autoid_exe = pathlib.PureWindowsPath(os.path.join(
                app_path, r'source/create_idents/launch_autoid.bat')).as_posix()
            if self.ids.ietm_checkbox.state == 'down':
                subprocess.call([autoid_exe, FOLDERPATH[0], choice, "1"])
            else:
                subprocess.call([autoid_exe, FOLDERPATH[0], choice, "0"])
            time.sleep(2)
            self.dialog.dismiss()
        except NotADirectoryError:
            self.dialog.dismiss()
            MDDialog(title='Not A Directory',
                     text='Please provide the path for folder, not a file').open()


class Tooltip(Label):
    pass


class IdReplacement(BoxLayout):
    drop_id = ObjectProperty(None)
    file_Path = StringProperty('')
    INPUT = []

    def __init__(self, **kwargs):
        super(IdReplacement, self).__init__(**kwargs)

    def global_check(self):
        if self.ids.global_replacement.state == 'down':
            RootLayout.modify_checks(self, 'down', True)
        else:
            RootLayout.modify_checks(self, 'normal', False)

    def other_check(self):
        if self.ids.other_item.state == 'down':
            self.ids.attr_input.disabled = False
        else:
            self.ids.attr_input.disabled = True

    def template_download(self, name):
        if FOLDERPATH != []:
            os.chdir(FOLDERPATH[0])
            filepath = pathlib.Path(FOLDERPATH[0]).joinpath(name)
            if not filepath.exists():
                self.create_template()
            else:
                self.alert = MDDialog(title='File Already Exists',
                                      text='Do you want to replace existing file?', buttons=[
                                          MDRaisedButton(text="YES",
                                                         on_release=self.create_template),
                                          MDRaisedButton(text="NO",
                                                         on_release=self.self_dismiss
                                                         )])
                self.alert.open()
        else:
            alert2 = MDDialog(title='No Input Found',
                              text='Please provide the path for data modules')
            alert2.open()

    def create_template(self, button=None):
        Snackbar(text='    Downloading Template...',
                 snackbar_x=dp(20), snackbar_y=dp(20),
                 size_hint_x=(Window.width - (dp(20) * 2)) / Window.width).open()
        temp = pd.ExcelWriter("id_replacement_template.xlsx")
        tempdf = pd.DataFrame({'OLD': [], 'NEW': []})
        tempdf.to_excel(temp, 'WARNINGS', index=False)
        tempdf.to_excel(temp, 'CAUTIONS', index=False)
        tempdf.to_excel(temp, 'TOOLS', index=False)
        tempdf.to_excel(temp, 'SUPPLIES', index=False)
        tempdf.to_excel(temp, 'OTHERS', index=False)
        temp.close()
        try:
            self.alert.dismiss()
        except AttributeError:
            pass

    def self_dismiss(self, button=None):
        self.alert.dismiss()

    def proceed_further(self):
        del self.INPUT[:]
        if FOLDERPATH != []:
            excelpath = pathlib.Path(FOLDERPATH[0]).joinpath(
                'id_replacement_template.xlsx')

            if not excelpath.exists():
                MDDialog(title='Template Not Found',
                         text='Please keep filled template in the working folder').open()
            else:
                for each in list(self.ids.keys()):
                    if each.startswith('checkbox_'):
                        if self.ids[each].state == 'down':
                            self.INPUT.append(self.ids[each].name)
                    elif each == 'other_item':
                        if self.ids[each].state == 'down':
                            if self.ids.attr_input.text != '':
                                self.INPUT.append(
                                    self.ids[each].name+'_'+self.ids.attr_input.text)
                            else:
                                MDDialog(title='No Reference Found',
                                         text='Please provide reference tag name').open()

                if self.INPUT != []:
                    self.pop_up1()
                    executor = concurrent.futures.ThreadPoolExecutor()
                    print(str("_".join(self.INPUT)))
                    executor.submit(self.process_excecution,
                                    str("_".join(self.INPUT)))
                elif self.ids.other_item.state != 'down':
                    self.pop_up1()
                    Snackbar(text='Since no task selected, replaceing as general attributes',
                             snackbar_x=dp(20), snackbar_y=dp(20),
                             size_hint_x=(Window.width - (dp(20) * 2)) / Window.width).open()
                    executor = concurrent.futures.ThreadPoolExecutor()
                    executor.submit(self.process_excecution, "othr_* *")
        else:
            MDDialog(title='No Input Found',
                     text='Please provide the path for data modules').open()

    def pop_up1(self):
        self.dialog = MDDialog(
            size_hint=(None, None),
            width=dp(200),
            auto_dismiss=True,
            type="custom",
            content_cls=Matter(),
        )
        self.dialog.open()

    @mainthread
    def process_excecution(self, choice):
        try:
            os.chdir(pathlib.PureWindowsPath(os.path.join(
                app_path, r'source/replid')).as_posix())
            replid_exe = pathlib.PureWindowsPath(os.path.join(
                app_path, r'source/replid/launch_replid.bat')).as_posix()
            subprocess.call([replid_exe, FOLDERPATH[0], choice])
            time.sleep(2)
            self.dialog.dismiss()
        except NotADirectoryError:
            self.dialog.dismiss()
            MDDialog(title='Not A Directory',
                     text='Please provide the path for folder, not a file').open()


class IdCompile(BoxLayout):
    drop_id = ObjectProperty(None)
    file_Path = StringProperty('')
    INPUT = []

    def __init__(self, **kwargs):
        super(IdCompile, self).__init__(**kwargs)

    def global_check(self):
        if self.ids.global_compile.state == 'down':
            RootLayout.modify_checks(self, 'down', True)
        else:
            RootLayout.modify_checks(self, 'normal', False)

    def template_download(self, name):
        IdReplacement.template_download(self, name)

    def create_template(self, button=None):
        Snackbar(text='    Downloading Template...',
                 snackbar_x=dp(20), snackbar_y=dp(20),
                 size_hint_x=(Window.width - (dp(20) * 2)) / Window.width).open()
        temp = pd.ExcelWriter("id_compilation_template.xlsx")
        temp_warn = pd.DataFrame({'Warning ID': [], 'Warning Para': []})
        temp_caut = pd.DataFrame({'Caution ID': [], 'Caution Para': []})
        temp_tool = pd.DataFrame({'Tool ID': [], 'Tool Number': [], 'Tool Name': [],
                                  'Tool Shortname': [], 'Manufacturer Code': []})
        temp_cons = pd.DataFrame({'Supply ID': [], 'Supply Number': [], 'Supply Name': [],
                                  'Supply Shortname': [], 'Manufacturer Code': []})
        temp_ents = pd.DataFrame({'Enterprise ID': [], 'Vendor Code': [], 'Enterprise Name': [],
                                  'Business Unit Name': [], 'Country': [], 'Street': [],
                                  'Pin Code': [], 'City': [], 'State': [],
                                  'Phone Num': [], 'Website': []})
        temp_warn.to_excel(temp, 'WARNINGS', index=False)
        temp_caut.to_excel(temp, 'CAUTIONS', index=False)
        temp_tool.to_excel(temp, 'TOOLS', index=False)
        temp_cons.to_excel(temp, 'SUPPLIES', index=False)
        temp_ents.to_excel(temp, 'VENDORS', index=False)
        temp.close()
        try:
            self.alert.dismiss()
        except AttributeError:
            pass

    def self_dismiss(self, button=None):
        self.alert.dismiss()

    def proceed_further(self, action: bool):
        del self.INPUT[:]
        if FOLDERPATH != []:
            excelpath = pathlib.Path(FOLDERPATH[0]).joinpath(
                'id_compilation_template.xlsx')

            if not excelpath.exists():
                MDDialog(title='Template Not Found',
                         text='Please keep filled template in the working folder').open()
            else:
                for each in list(self.ids.keys()):
                    if each.startswith('checkbox_'):
                        if self.ids[each].state == 'down':
                            self.INPUT.append(self.ids[each].name)

                if self.INPUT != []:
                    self.pop_up1()
                    executor = concurrent.futures.ThreadPoolExecutor()
                    executor.submit(self.process_excecution,
                                    str("_".join(self.INPUT)), action)
                else:
                    MDDialog(title='No Task Selected',
                             text='Kindly select ident type').open()
        else:
            alert2 = MDDialog(title='No Input Found',
                              text='Please provide the path for data modules')
            alert2.open()

    def pop_up1(self):
        self.dialog = MDDialog(
            size_hint=(None, None),
            width=dp(200),
            auto_dismiss=True,
            type="custom",
            content_cls=Matter(),
        )
        self.dialog.open()

    @mainthread
    def process_excecution(self, choice, action: bool):
        try:
            os.chdir(pathlib.PureWindowsPath(os.path.join(
                app_path, r'source/compileids')).as_posix())
            compileid_exe = pathlib.PureWindowsPath(os.path.join(
                app_path, r'source/compileids/launch_compileid.bat')).as_posix()
            if action == True:
                subprocess.call([compileid_exe, FOLDERPATH[0], choice, "1"])
            else:
                subprocess.call([compileid_exe, FOLDERPATH[0], choice, "0"])
            time.sleep(2)
            self.dialog.dismiss()
        except NotADirectoryError:
            self.dialog.dismiss()
            MDDialog(title='Not A Directory',
                     text='Please provide the path for folder, not a file').open()


class Matter(MDCard):
    pass


class HoverCard(MDRaisedButton, HoverBehavior):
    #tooltip = Tooltip(text='Hello world')

    hover_dialog = {'Continue': '[ Replaces or adds idents for selected type of element(s) ]',
                    'Clear': '[ Clears the provided input ]',
                    'Quit': '[ Terminates the ongoing action ]',
                    'OK': '[ Replaces given old IDs with new ]',
                    'Add Idents': '[ Adds given Ids with details to corresponding repository ]',
                    'Remove Idents': '[ Removes the element corresponding to given id from repository ]', }

    def __init__(self, **kwargs):
        # Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverCard, self).__init__(**kwargs)

    def on_enter(obj):
        obj.text_color = [66/255, 175/255, 1, 1]
        obj.md_bg_color = [50/255, 100/255, 150/255, 1]
        obj.font_size = 16
        obj.reference.text = obj.hover_dialog[obj.text]

    def on_leave(obj):
        obj.reference.text = '[ Select below the type of ident to be replaced ]'
        obj.text_color = [0, 0, 0, 1]
        obj.md_bg_color = [25/255, 154/255, 229/255, 1]
        obj.font_size = 14

    def on_click(obj, parent):
        for each in parent.children:
            if each != obj:
                each.md_bg_color = [0.07, 0.07, 0.07, 1]
                each.elevation = 0
            else:
                obj.elevation = 10
                obj.md_bg_color = [0.4, 0.4, 0.4, 1]

    def on_mouse_pos(self, *args):
        self.tooltip = Tooltip(text='')
        if not self.get_root_window():
            return
        pos = args[1]
        self.tooltip.pos = pos
        # cancel scheduled event since I moved the cursor
        Clock.unschedule(self.display_tooltip)
        self.close_tooltip()  # close if it's opened
        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.display_tooltip, 1)

    def close_tooltip(self, *args):
        Window.remove_widget(self.tooltip)

    def display_tooltip(self, *args):
        self.tooltip = Tooltip(text=self.text)
        Window.add_widget(self.tooltip)


class HoverFloat(MDFloatingActionButton, HoverBehavior):

    hover_dialog = {'id_replace': '[ Downloads the excel template ]'}

    def __init__(self, **kwargs):
        # Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverFloat, self).__init__(**kwargs)

    def on_enter(obj):
        obj.text_color = [66/255, 175/255, 1, 1]
        obj.md_bg_color = [50/255, 100/255, 150/255, 1]
        obj.font_size = 16
        obj.reference.text = obj.hover_dialog[obj.text]

    def on_leave(obj):
        obj.reference.text = '[ Select below the type of ident to be replaced ]'
        obj.text_color = [0, 0, 0, 1]
        obj.md_bg_color = [25/255, 154/255, 229/255, 1]
        obj.font_size = 14


class Id_Suit(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = "M2"
        self.theme_cls.primary_palette = 'LightBlue'
        return RootLayout()

    def clear_input(self):
        del FOLDERPATH[:]
        self.root.ids.inputwizard.ids.input_textbox.text = \
            'Please drop your folder here'

    def action_quit(self, function: str):
        wmi = win32com.client.GetObject('winmgmts:')

        def getpid(process_name):
            return [item.split()[1] for item in os.popen('tasklist').read().splitlines()[4:] if process_name in item.split()]

        for p in wmi.InstancesOf('win32_process'):
            if p.Name == function:
                process_id = getpid(function)
                if len(process_id) > 1:
                    for x in process_id:
                        pid = int(x)
                        os.kill(pid, signal.SIGTERM)
                else:
                    pid = int("".join(getpid(function)))
                    os.kill(pid, signal.SIGTERM)


def reset():
    import kivy.core.window as window
    from kivy.base import EventLoop
    if not EventLoop.event_listeners:
        from kivy.cache import Cache
        window.Window = window.core_select_lib(
            'window', window.window_impl, True)
        Cache.print_usage()
        for cat in Cache._categories:
            Cache._objects[cat] = {}


if __name__ == "__main__":
    reset()
    Id_Suit().run()
