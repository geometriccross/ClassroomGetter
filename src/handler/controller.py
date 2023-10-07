from tkinter import Widget

from ..gui import *
from ..my_util import *
from ..data import *
from ..interface import *


def children(widget) -> dict[Widget, type]:
    result = {}
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
    def __init__(self, root: ApplicationRoot) -> None:
        self.root = root
        self.binding(children(root))
            
    def binding(self, ins_type: dict[Widget, type]):
        setting_frame:      SettingFrame =  name_of(SettingFrame, ins_type)
        node_info_frame:    NodeInfoFrame = name_of(NodeInfoFrame, ins_type)
        timer:              Timer =         name_of(Timer, ins_type)
        time_setters:       TimeSetters =   name_of(TimeSetters, ins_type)
        node_box:           NodeBox =       name_of(NodeBox, ins_type)

#region 設定管理系
        setting_frame.on_save(lambda: 
            setting_frame.save_cfg(
                file_path=ISettingData.SETTINGFOLDER_PATH.joinpath('setting.json')))
#endregion
        
#region Node管理系
        node_info_frame.on_node_init_btn_press(node_info_frame.node_box.initialize)
        
        #監視しているNodeBoxを更新する
        timer.on_time_set_btn_press(lambda:
            timer.clock_event_publish(
                dead_line=time_setters.value(),
                when_reach=node_info_frame.node_box.initialize,
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

    def run_applicaiton(self):
        self.root.mainloop()