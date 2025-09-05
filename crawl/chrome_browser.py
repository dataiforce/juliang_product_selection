from DrissionPage import Chromium, ChromiumOptions



class ChromeBrower:
    def __init__(self, tab_count = 1, port = None, wait_login = False):
        if port is not None:
            option = ChromiumOptions().set_local_port(port).set_user_data_path(f'D:/browser_data/browser_{port}')
            self.browser = Chromium(addr_or_opts=option)
        else:
            self.browser = Chromium()
        now_tabs = self.browser.get_tabs()

        self.tab_list = []
        if len(now_tabs) == 2:
            for tab in now_tabs:
                if "merch-promoting" in tab.url:
                    self.tab_list.append(tab)
                else:
                    self.tab_list.insert(0, tab)
        else:
            if len(now_tabs) > 1:
                for i in range(1, len(now_tabs)):
                    now_tabs[i].close()
            self.tab_count = tab_count
            self.tab_list = []
            self.tab_list.append(self.browser.latest_tab)
            self.tab_list[0].get("https://buyin.jinritemai.com/dashboard")
            if wait_login:
                input("请登录巨量百应，按回车键继续")
            for i in range(1, tab_count):
                self.tab_list.append(self.browser.new_tab("https://buyin.jinritemai.com/dashboard"))
        
    def get_tab(self, i):
        return self.tab_list[i]
    
    def get_browser(self):
        return self.browser
