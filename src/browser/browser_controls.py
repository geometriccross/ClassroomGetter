from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from re import search

from factory import create_driver
from ..setting.setting_data import SettingData

class BrowserControls:
    def __init__(self, setting: SettingData, driver: webdriver = None, wait: WebDriverWait = None) -> None:        
        self.driver = driver if (driver != None) else create_driver(setting.profile())
        self.wait   = wait   if (wait   != None) else WebDriverWait(self.driver, setting.loading_wait_time)
        
        self.__setting = setting
    
    def __del__(self):
        del self.wait
        self.driver.quit()
        del self.driver
    
    def move(self, url: str):
        self.driver.get(url)
        
    def serch(self, xpath: str) -> WebElement:
        return self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        
    def hrefs(self):
        def __get_hrefs(locator, pattern: str = ''):
            unique_links = set() #重複処理のため
            try:
                elems = self.wait.until(EC.presence_of_all_elements_located(locator))
            except TimeoutException:
                return unique_links
            
            for elem in elems:
                link = str(elem.get_attribute('href'))
                #文字列が見つかれば
                if (search(pattern, string=link) != None):
                    unique_links.add(link)
            return unique_links
        
        return __get_hrefs
    
    def click_all_sections(self, func, locator_and_pattern: tuple):
        def __move_and_click(elem: WebElement):
            self.driver.execute_script("arguments[0].scrollIntoView(true);", elem)
            self.driver.execute_script('arguments[0].click()', elem)

        #一つめは3点ボタン、2つめは「リンクをコピー」へのxpath
        links = []
        xpathes = ["//div[@class='SFCE1b']"]
        
        try:
            buttons = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, xpathes[0])))
        except TimeoutException:
            return []
        
        self.wait._timeout /= 10 #ファイルの読み込みは早いため
        for button in buttons:
            __move_and_click(button)
            links.extend(func()(*locator_and_pattern))
            
        self.wait._timeout *= 10 #元に戻す
        return links
 
    def login_college_form(self, setting: SettingData):
        befor_at_index = setting.user_email.find('@')
        user_name = setting.user_email[:befor_at_index]
        
        #1:emailの@以前をユーザー名に送る
        #2:passwordを送る
        #3:ログインボタンを押す
        self.serch("//input[@id='j_username']").send_keys(user_name)
        self.serch("//input[@id='j_password']").send_keys(setting.user_password)
        self.serch("//button[@type='submit']").click()
    
    def login_google(self, setting: SettingData):
        #1:emailを入力する
        #2:続行を押す
        #3:大学のフォームにログイン
        #4:続行を押す
        self.serch("//input[@type='email']")        .send_keys(setting.user_email)
        self.serch("//div[@id='identifierNext']")   .click()
        self.login_college_form(setting)
        self.serch("//div[@jsname='Njthtb']")       .click()
        
    def login_classroom(self, setting: SettingData):
        #1:ログイン画面に移動する
        #2:Googleにログインする
        #3:プロファイルを設定する
        self.move(self.serch("//a[@class='gfe-button gfe-button--medium-emphasis gfe-button--middle-align']").get_attribute('href'))
        self.login_google(setting)