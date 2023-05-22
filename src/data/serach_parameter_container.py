import asyncio
from typing import Coroutine
from dataclasses import dataclass
from selenium.common.exceptions import TimeoutException

from src import my_util
from src.interface.i_node import INode

@dataclass(frozen=True)
class SearchParameter:
    xpath: str
    regex: str
    attribute_func: callable
        
    def next_values(self, acquiring_func: callable) -> callable:
        """
        この関数はカリー化されている

        Args:
            acquiring_func (callable):
                この関数は高階関数で無ければならず、最終的にIterableな値を返さなければならない
                
            format_func (callable):
                acquiring_funcの戻り値をこの関数でmapする
        """
        async def __filter(format_func: callable) -> Coroutine:
            return map(
                format_func,
                #asyncio.gatherは値をリストに包んで返すため、二次元リストとなってしまう。
                #そのため平坦化する
                    await asyncio.create_task(acquiring_func(self.xpath, self.regex)(self.attribute_func)) 
                )
        return __filter
        
@dataclass(frozen=True)
class SearchParameterPattern:
    pattern_name: str
    text_param: SearchParameter
    link_param: SearchParameter
    
    text_filter: callable = my_util.do_nothing
    link_filter: callable = my_util.do_nothing
    pre_proc:    callable = my_util.do_nothing
    
    #func:textとlinkのペアに対して行う関数
    #text_filter, link_filter: それぞれのlistに対して行う関数
    async def elements(self, node: INode) -> list[tuple[str, str]]:
        self.pre_proc(node)
        if self.text_param == None or self.link_param == None:
            return my_util.convert_to_tuple([node.key + 'の授業タブ'], [my_util.to_all_tab_link(node.url)])
        else:
            try:
                return my_util.convert_to_tuple(
                        await self.text_param.next_values(node.BrowserControl.elements)(self.text_filter),
                        await self.link_param.next_values(node.BrowserControl.elements)(self.link_filter)
                    )
            except TimeoutException:
                return []
        
class SearchParameterContainer:
    @staticmethod
    def __get_text(elem):
        return elem.text
    
    @staticmethod
    def __get_link(elem):
        return elem.get_attribute('href')

    @staticmethod
    def __move(node: INode):
        node.BrowserControl.move(node.url)
        
    def __move_and_click(node: INode):
        SearchParameterContainer.__move(node)
        node.BrowserControl.click_all_sections()

    parameters: list[SearchParameterPattern] = [
        #添字とtree_heightを一致させる
        SearchParameterPattern(
            pattern_name='Home',
            text_param=SearchParameter(
                "//div[@class='YVvGBb z3vRcc-ZoZQ1']",
                '.+',
                __get_text
            ),
            link_param=SearchParameter(
                "//a[@class='onkcGd ZmqAt Vx8Sxd']",
                "^.*/c/.{16}$",
                __get_link
            ),
            text_filter = my_util.text_filter,
            pre_proc=__move
        ),
        
        SearchParameterPattern(
            pattern_name='LessonTab',
            text_param=None,
            link_param=None
        ),
        
        SearchParameterPattern(
            pattern_name='Sections',
            text_param=SearchParameter(
                "//span[@class='YVvGBb UzbjTd']",
                ".+",
                __get_text
            ),
            link_param=SearchParameter(
                "//a[contains(@aria-label, '表示')]",
                ".*/details$",
                __get_link
            ),
            pre_proc=__move_and_click
        ),
        
        SearchParameterPattern(
            pattern_name='Details',
            text_param=SearchParameter(
                "//div[@class='A6dC2c QDKOcc VBEdtc-Wvd9Cc zZN2Lb-Wvd9Cc']",
                ".+",
                __get_text
            ),
            link_param=SearchParameter(
                "//a[@class='vwNuXe JkIgWb QRiHXd MymH0d maXJsd']",
                '.*/file/d.*',
                __get_link
            ),
            pre_proc=__move
        )
    ]

    @staticmethod
    async def elements(node: INode):
        if len(SearchParameterContainer.parameters) > node.tree_height:
            return await SearchParameterContainer.parameters[node.tree_height].elements(node)
        else:
            return []