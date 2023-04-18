from __future__ import annotations
from selenium.webdriver.common.by import By
from inspect import signature

from src import my_util
from src.interface.i_node import INode
from src.browser.browser_controls import BrowserControls as bc

class Node(INode):
    #クラス変数の宣言と同時に定義を行わないのは、変数が勝手に起動してしまうため
    #つまり、BrowserControlはWebDrivreを有しているため、Chromeが勝手に起動してしまう
    BrowserControl: bc = None
    Nodes: set[INode] = set() #全てのノードの集合

    def __init__(self, key: str, url: str, tree_height: int) -> None:
        if Node.BrowserControl is None:
            raise TypeError('BrowserControl is None')
        
        self.__edges: list[INode] = []
        self.key = key
        self.url = url
        self.tree_height = abs(tree_height) #負の値が入れられないように
        Node.Nodes.add(self)
        pass
    
    def __str__(self) -> str:
        return str.format('{0}:{1}', self.tree_height, self.key)
    
    def __lt__(self, other) -> bool:
        return self.tree_height < other.tree_height
    
    def __eq__(self, other) -> bool:
        if (other == None):
            return False
        else:
            return \
                self.tree_height == other.tree_height and\
                self.key         == other.key         and\
                self.url         == other.url         and\
                self.edges()     == other.edges()
    
    def __hash__(self) -> int:
        key_hash    = hash(self.key)
        url_hash    = hash(self.url)
        height_hash = hash(self.tree_height)
        
        return hash((key_hash, url_hash, height_hash))
    
    def __del__(self) -> None:
        if (self in Node.Nodes):
            Node.Nodes.remove(self)
            
        #それぞれのedgeから削除
        for node in Node.Nodes:
            if (self is node):
                continue
            
            if (self in node.edges()):
                node.edges().remove(self)
    
    #getter/setterを兼ねたもの
    def edges(self, add_value: INode = None) -> list[INode]:
        if add_value == None:
            return self.__edges
        else:
            self.__edges.append(add_value)
            Node.Nodes.add(add_value)
    
    def next_links(self) -> list[tuple[str, str]]: #(title, url)
        c = self.BrowserControl

        #ホームなら
        if (self.tree_height == 0):
            c.move(self.key)
            link_locator = (By.XPATH, "//a[@class='onkcGd ZmqAt Vx8Sxd']")
            link_pattern = '^.*/c/.{16}$'
            links = c.elements(link_locator, link_pattern)(lambda elem: elem.get_attribute('href'))
            
            title_locator = (By.XPATH, "//div[@class='YVvGBb z3vRcc-ZoZQ1']")
            title_pattern = ''
            titles = list(
                map(
                    my_util.text_filter,
                    c.elements(title_locator, title_pattern)(lambda elem: elem.text)
                ))
            
            return my_util.convert_to_tuple(titles, links)
                
        #授業のタブなら
        #https://classroom.google.com/c/NjAyMTUwMTQyNzk1
        elif (self.tree_height == 1):
            return [(self.key + '_授業タブ', my_util.to_all_tab_link(self.url))]
        
        #「全てのトピック」なら
        elif ('/t/all' in self.url):
            c.move(self.url)
            file_locator = (By.XPATH, "//a[@class='VkhHKd e7EEH ']")
            file_pattern = '^.*/file/d/.*$'
            files = c.click_all_sections(c.elements(file_locator, file_pattern), lambda elem: elem.get_attribute('href'))
            
            name_locator = (By.XPATH, "//div[@class='lIHx8b YVvGBb asQXV ']")
            name_pattern = ''
            names = c.elements(name_locator, name_pattern)(lambda elem: elem.text)
            
            return my_util.convert_to_tuple(names, files)
        
        #ファイルのurlなら
        else:
            return []
            
    def create_childs(self, *args: tuple[str, str]):
        for tuple in args:
            self.edges(
                add_value=Node(*tuple, self.tree_height + 1)
            )
            
        return self

    @staticmethod
    def ShowTree(parent: INode):
        def __indent(indent_size: int):
            result: str = ''
            for i in range(indent_size):
                result += '    ' #半角スペース4つはpythonと同じインデントである
            return result
        
        if (parent == None):
            return
        
        print(__indent(parent.tree_height) + str(parent))
        
        for node in parent.edges():
            Node.ShowTree(node)
                
    #深さ優先探索
    @staticmethod
    def Serch(entry: INode) -> INode:
        def __do_serch(func):
            #if not my_util.has_curretn_args(func, Node):
            #    raise ValueError('func arguments invailed')
            
            stack: list[INode] = [entry]
            
            while(len(stack) > 0):
                value = stack.pop()
                func(value)

                for child in value.edges():
                    stack.append(child)
                    
        return __do_serch
                
    #幅優先探索
    @staticmethod
    def InitializeTree(parent: INode):
        queue: list[Node] = [parent]
                
        while (len(queue) > 0):
            value = queue.pop(0)
            links = value.next_links()
            
            if (len(links) > 0):
                value.create_childs(*links)
                
            for child in value.edges():
                queue.append(child)