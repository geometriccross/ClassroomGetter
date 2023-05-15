from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from re import search

from src.browser.factory import create_driver
from src.data.setting_data import SettingData

class BrowserControl:
    def __init__(self, setting: SettingData, driver: webdriver = None, wait: WebDriverWait = None) -> None:        
        self.driver = driver if (driver != None) else create_driver(SettingData.profile_path())
        self.wait   = wait   if (wait   != None) else WebDriverWait(self.driver, setting.loading_wait_time, 1)
    
    def __del__(self):
        del self.wait
        self.driver.quit()
        del self.driver
        
    def move(self, url: str):
        self.driver.get(url)
        
    def serch(self, xpath: str) -> WebElement:
        return self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        
    def elements(self, xpath: str, pattern: str = ''):
        def __get_hrefs(filter_func: callable):
            elems = []
            try:
                elems = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
            except TimeoutException as e:
                raise e
                
            values = map(filter_func, elems)
            current_values = filter(
                lambda string: search(pattern, string=str(string)) != None,
                values
            )
            
            return list(current_values)
        return __get_hrefs
    
    def click_all_sections(self):
        def __check_loaded(xpath) -> bool:
            def __predictate(driver):
                sample_buttons = driver.find_elements(By.XPATH, "//li[@jsmodel='dSSknb;PTCFbe;xeYtDf;']")
                if all([x.get_attribute('data-controller-loaded') == 'true' for x in sample_buttons]):
                    return driver.find_elements(By.XPATH, xpath)
                else:
                    return False
            return __predictate
            
        try:
            xpath = "//div[@jsname='rQC7Ie' and @role='button']"
            buttons = self.wait.until(__check_loaded(xpath))
            
            action = ActionChains(self.driver)
            for button in buttons:
                action.move_to_element(button).click(button).pause(self.wait._poll).perform()
                
        except TimeoutException:
            return
        
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