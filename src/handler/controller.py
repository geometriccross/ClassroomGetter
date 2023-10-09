import threading
from tkinter import Widget

from ..gui import *
from ..my_util import *
from ..data import *
from ..interface import *

from .driver_session import *
from .event_runner import *


def children(widget) -> dict[Widget, type]:
    result = {widget: widget.__class__}
    def _loop(widget):
        for child in widget.winfo_children():
            #インスタンスをkeyにしているので、同一クラスのインスタンスを取得できる
            result.update({child: child.__class__})
            _loop(child)

    _loop(widget)
    return result

def name_of(cls, dic) -> str:
    from_value = [k for k, v in dic.items() if v == cls]
    if len(from_value) == 1:
        #固有のものであればそれを返す
        return from_value[0]
    else:
        return from_value

class Controller:
    def __init__(self, root: ApplicationRoot, session: DriverSession) -> None:
        self.root = root
        self.default_session = session
        self.event_runner: EventRunner = EventRunner()
        
        self.binding(children(root), session)
            
    def binding(self, ins_type: dict[Widget, type], session: DriverSession):
        app_root:           ApplicationRoot = name_of(ApplicationRoot, ins_type)
        setting_frame:      SettingFrame =    name_of(SettingFrame, ins_type)
        node_info_frame:    NodeInfoFrame =   name_of(NodeInfoFrame, ins_type)
        timer:              Timer =           name_of(Timer, ins_type)
        time_setters:       TimeSetters =     name_of(TimeSetters, ins_type)
        node_box:           NodeBox =         name_of(NodeBox, ins_type)
        
#region 設定管理系
        setting_frame.on_save(lambda: 
            setting_frame.save_cfg(
                file_path=ISettingData.SETTINGFOLDER_PATH.joinpath('setting.json')))
#endregion
        
#region Node管理系
        node_info_frame.on_node_init_btn_press(lambda:
            self.event_runner.add(
                threading.Thread(target=lambda:
                    node_info_frame.node_box.initialize(aqcuire=session.next_key_url)).start))
        
        #監視しているNodeBoxを更新する
        timer.on_time_set_btn_press(lambda:
            timer.clock_event_publish(
                dead_line=time_setters.value(),
                interval_ms=10))
        
        timer.on_time_reset_btn_press(f=timer.clock_reset)
        
        #この関数はなくし、できれば無名関数で書きたい
        #しかしながら無名関数内での代入はできなかった
        #これは妥協である
        def __set_box_to_info_frame(other: NodeBox):
            node_info_frame.node_box = other
        
        #最初に表示されるNodeBoxのeventを設定する
        node_box.on_click_this(lambda:__set_box_to_info_frame(node_box))
        node_box.on_expand(
            lambda n: n.on_click_this(lambda: __set_box_to_info_frame(n)))
#endregion


        def __root_stop(root, session):
            close_thread = threading.Thread(target=session.close)
            close_thread.start()
            
            for thread in [t for t in threading.enumerate()
                           if t not in (threading.main_thread(), close_thread)]:
                thread.join()
                
            root.destroy()
            close_thread.join()
            
        app_root.on_loop_end(self.event_runner.run_all)
        app_root.on_stop(__root_stop, root=app_root, session=session)

    def run_applicaiton(self):
        self.root.run()