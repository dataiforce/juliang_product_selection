from DrissionPage import Chromium
from DrissionPage._pages.mix_tab import MixTab
from crawl.download_sleep import DomainSleepController
from crawl.uitls import human_like_mouse_move, save_json, random_human_action, load_json, append_dicts_to_json, set_category_path, is_done, mark_done
from config import Config
import random
import os

class AutoProductSelection:
    def __init__(self, main_tab: MixTab, details_tab: MixTab, browser: Chromium, category: dict):
        self.category = category

        if category:
            self.category_path = set_category_path(category)
        self.json_path = os.path.join(Config.BASE_PATH, f"{self.category_path}.json")
        self.sleep = DomainSleepController()
        self.tab = main_tab
        self.details_tab = details_tab
        self.browser = browser
        self.queue = []
        self.tab.listen.start("buyin.jinritemai.com/pc/selection/common/material_list")
        self.tab.listen.pause()
        self.details_tab.listen.start("buyin.jinritemai.com/pc/selection/decision/pack_detail")
        self.tab.listen.pause()
        self.browser.activate_tab(self.tab)
        self.log_file = os.path.join(Config.BASE_PATH, "食品饮料", "log.json")
        self.init = True
        if "merch-promoting" in self.details_tab.url:
            self.init = False


    def init_categroy(self,  category_choice:dict = {}):
        if category_choice.get("third") and category_choice.get("second"):
            depth = 3
        elif category_choice.get("second"):
            depth = 2
        else:
            depth = 1

        first_category = category_choice.get("first")
        second_category = category_choice.get("second", None)
        third_category = category_choice.get("third", None)
        show_category = self.tab.ele("text=展开", timeout=1)

        if show_category:
            show_category.click()
        first_ele = self.tab.ele(f"text={first_category}")
        self.tab.actions.move_to(
            ele_or_loc=first_ele,
            offset_x=random.uniform(-10.0, 10.0),
            offset_y=random.uniform(-1, 1)
        ).click()

        if depth != 3:
            self.tab.wait(0.5, 1.0)
            if depth == 1:
                choice_eles = self.tab.eles("text=不限")
                for ele in choice_eles:
                    if ele.states.is_clickable:
                        choice_ele = ele
                        break
            elif depth == 2:
                choice_ele = self.tab.ele(f"@title={second_category}")
            self.tab.actions.move_to(
                ele_or_loc=choice_ele,
                offset_x=random.uniform(15.0, 25.0)
            ).click()
            return

        self.tab.wait(0.5, 1.0)
        second_ele = self.tab.ele(f"@title={second_category}")
        self.tab.actions.move_to(
            ele_or_loc=second_ele,
            offset_x=random.uniform(15.0, 25.0)
        )
        self.tab.wait(0.5, 1)

        self.tab.ele(f"@title={third_category}").click()


    def init_second_condition(self, condition):
        self.tab.ele("text=带货达人数").click()
        while True:
            if self.tab.wait.ele_displayed(f"text={condition}", timeout=0.5):
                break
            self.tab.ele("text=带货达人数").click()
        self.tab.ele(f"text={condition}").click()
        print(f"增加条件带货达人数为：{condition}")


    def list_page_logic(self):
        带货达人数_选项 = Config.带货达人数
        self.browser.activate_tab(self.tab)
        self.tab.get("https://buyin.jinritemai.com/dashboard/merch-picking-library")
        self.tab.wait.eles_loaded("tag=tr")
        self.tab.listen.resume()
        self.init_categroy(self.category)
        try_count = 2
        for index in range(try_count):
            resp = self.tab.listen.wait(timeout=100)
            json_data = resp.response.body
            all_total = json_data["data"]["total"]
            product_list = json_data["data"]["summary_promotions"]
            if len(product_list) != 0:
                break
            if index + 1 == try_count:
                print("该类目无商品，跳过")
                return
            self.tab.listen.pause()
            self.tab.actions.move_to("text=全部").click()
            self.browser.wait(1,3)
            self.init_categroy(self.category)
            self.tab.listen.resume()
        self.tab.listen.pause()

        for i in 带货达人数_选项:
            if is_done(self.log_file, self.category, done_type=f"list_{i}_done"):
                print(f"本次已完成，跳过，条件: {self.category_path} {i}")
                continue
            self.init_second_condition(i)
            self.tab.listen.resume()
            is_new_start = True
            for max_loop_limit in range(100):
                try:
                    resp = self.tab.listen.wait(timeout=100)
                except Exception as e:
                    print(e)
                    break
                if resp:
                    print("捕获到数据包，开始处理")
                    json_data = resp.response.body
                    all_total = json_data["data"]["total"]
                    product_list = json_data["data"]["summary_promotions"]
                    if len(product_list) == 0:
                        if is_new_start:
                            for index in range(2):
                                self.tab.listen.pause()
                                self.tab.actions.move_to("text=全部").click()
                                self.browser.wait(1,3)
                                self.init_categroy(self.category)
                                self.tab.listen.resume()
                                resp = self.tab.listen.wait(timeout=100)
                                json_data = resp.response.body
                                all_total = json_data["data"]["total"]
                                product_list = json_data["data"]["summary_promotions"]
                                if len(product_list) != 0:
                                    break
                        else:
                            print("数据包中数据条数为0")
                            break
                    now_total = append_dicts_to_json(self.json_path, product_list)
                    print(f"已将本批数据保存至 {self.json_path} 当前进度为: {now_total}/{all_total} ")
                    is_new_start = False
                human_like_mouse_move(tab=self.tab, duration=random.randint(1, 3))
                if len(product_list) != 0:
                    self.tab.ele("#portal").scroll.to_bottom()
                else:
                    break
            mark_done(self.log_file, self.category, done_type=f"list_{i}_done")
            self.tab.listen.pause()
            self.tab.refresh()
            self.tab.wait.eles_loaded("tag=tr")
            self.init_categroy(self.category)

    def detail_page_logic(self):
        self.browser.activate_tab(self.details_tab)
        all_data = load_json(self.json_path)
        for product in all_data:
            self.queue.append(product["promotion_id"])
        print(f"已入队所有数据: {len(all_data)} 条")
        self.main_handle()


    def main_logic(self):
        if self.init:
            self.tab.get("https://buyin.jinritemai.com/dashboard/merch-picking-library")
            self.tab.wait.eles_loaded("tag=tr")
            self.init_categroy(self.category)
        else:
            temp_data = load_json(self.temp_json_path)
            for product in temp_data:
                self.queue.append(product["promotion_id"])
            print(f"已入队上批中断数据: {len(temp_data)} 条")
            self.tab.ele("#portal").scroll.to_bottom()
        while True:
            is_end = self.main_handle()
            if is_end == "end":
                return "end"
            self.browser.activate_tab(self.tab)
            human_like_mouse_move(tab=self.tab, duration=random.randint(3, 7))
            self.sleep.maybe_sleep()
            self.tab.ele("#portal").scroll.to_bottom()


    def main_handle(self):
        is_end = self.list_handle()
        if is_end == "end":
            return "end"
        while self.queue:
            promotion_id = self.queue.pop()
            self.details_tab.listen.resume()
            try:
                self.details_handle(promotion_id)
            except Exception as e:
                print(f"商品（{promotion_id}）出现异常：{e}")
            self.details_tab.listen.pause()
            self.sleep.maybe_sleep()


    def list_handle(self):
        self.tab.listen.resume()
        try:
            print("开始等待数据包")
            resp = self.tab.listen.wait(timeout=30)
        except Exception as e:
            return "end"
        if resp:
            print("捕获到数据包，开始处理")
            json_data = resp.response.body
            product_list = json_data["data"]["summary_promotions"]
            if len(product_list) == 0:
                return "end"
            save_json(product_list, self.temp_json_path)
            print(f"已将本批数据保存至 {self.temp_json_path}")
            for product in product_list:
                self.queue.append(product["promotion_id"])
        self.tab.listen.pause()
        


    def details_handle(self, promotion_id):
        core_path = os.path.join(Config.BASE_PATH, self.category_path, promotion_id, "core.json")
        non_core_path = os.path.join(Config.BASE_PATH, self.category_path, promotion_id, "non_core.json")
        if os.path.exists(core_path) and os.path.exists(non_core_path):
            print(f"跳过已存在文件: {promotion_id}")
            return

        promotion_url = f"https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?id={promotion_id}"
        self.browser.activate_tab(self.details_tab)
        self.details_tab.get(promotion_url)

        human_like_mouse_move(tab=self.details_tab, duration=random.randint(2, 6))

        # 真正有用的逻辑
        non_core, core = self.core_part()
        save_json(core, core_path)
        save_json(non_core, non_core_path)
        print(f"保存成功: {promotion_id}")

        # 为了像人的逻辑
        if random.randint(0, 10) % 3 == 0:
            self.details_tab.wait.ele_displayed("text=带货内容")
            dynamic_ele = self.details_tab.ele("text=带货内容")
            self.details_tab.actions.move_to(
                ele_or_loc=dynamic_ele,
                offset_x=random.uniform(-5.0, 5.0),
                offset_y=random.uniform(-2.5, 2.5)
            ).click(dynamic_ele)
        elif random.randint(0, 10) % 3 == 0:
            self.details_tab.wait.ele_displayed("text=带货内容")
            if random.randint(0, 10) % 3:
                dynamic_ele = self.details_tab.ele("text=商品评价")
            else:
                dynamic_ele = self.details_tab.ele("text=商品详情")
            self.details_tab.actions.move_to(
                ele_or_loc=dynamic_ele,
                offset_x=random.uniform(-5.0, 5.0),
                offset_y=random.uniform(-2.5, 2.5)
            ).click(dynamic_ele)
            
        random_human_action(tab=self.details_tab, duration=random.randint(2, 4))
        random_human_action(tab=self.details_tab, duration=random.randint(3, 6))



    def core_part(self, action_page:MixTab = None):
        if action_page is None:
            action_page = self.details_tab
        try:
            resp_list = action_page.listen.wait(count=2, timeout=30)
            for resp in resp_list:
                if resp.request.postData["data_module"] == 'pc-non-core':
                    non_core = resp.response.body['data']
                else:
                    core = resp.response.body['data']
            return non_core, core
        except Exception as e:
            action_page.wait(0, 5)
            action_page.refresh()
            action_page.wait(0, 5)
            return self.core_part()
