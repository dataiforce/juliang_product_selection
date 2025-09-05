from DrissionPage import Chromium
from DrissionPage._pages.mix_tab import MixTab
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
from collections import Counter
from db.manage.base import get_session
from db.manage.selection import insert_promotion_product, insert_sale_content, promotion_exists, insert_material, get_promotion_product_by_id
from crawl.download_sleep import DomainSleepController
from crawl.uitls import human_like_mouse_move, random_human_action
import random
from crawl.uitls import extract_id_from_url, is_dynamic
from db.models.selection import Material
import json

class AutoProductSelection:
    def __init__(self, main_tab: MixTab, details_tab: MixTab, browser: Chromium, category: dict, qianchuan_id = "1841049718523399"):
        self.category = category
        if category:
            self.category_type = "-".join(
                str(v) for v in [
                    category.get("first"),
                    category.get("second"),
                    category.get("third"),
                ] if v is not None
            )
        self.qianchuan_id = qianchuan_id
        self.session = get_session()
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
        self.init = True
        if "merch-promoting" in self.details_tab.url:
            self.init = False

    def init_filter(self):
        # 月销筛选条件
        self.tab.ele("text=月销").click()
        while True:
            if self.tab.wait.ele_displayed("text=≥5000", timeout=0.5):
                break
            self.tab.ele("text=月销").click()
        self.tab.ele("text=≥5000").click()
        print("月销筛选选择成功")
        

        # 佣金筛选条件
        self.tab.ele("text=佣金区间").click()
        while True:
            if self.tab.wait.ele_displayed("@placeholder=最低值", timeout=0.5):
                break
            self.tab.ele("text=佣金区间").click()
        self.tab.ele("@placeholder=最低值").input("25")
        self.tab.ele("text=确定").click()
        print("佣金区间筛选选择成功")


        # 商家体验分筛选条件
        self.tab.ele("text=商家体验分").click()
        while True:
            if self.tab.wait.ele_displayed("text=85分以上", timeout=0.5):
                break
            self.tab.ele("text=商家体验分").click()
        self.tab.ele("text=85分以上").click()
        print("商家体验分筛选选择成功")


        # 好评率筛选条件
        self.tab.ele("text=好评率").click()
        while True:
            if self.tab.wait.ele_displayed("text=≥90%", timeout=0.5):
                break
            self.tab.ele("text=好评率").click()
        self.tab.ele("text=≥90%").click()
        print("好评率筛选选择成功")


        # 服务与权益筛选条件
        self.tab.ele("text=服务与权益").click()
        while True:
            if self.tab.wait.ele_displayed("text=短视频随心推", timeout=0.5):
                break
            self.tab.ele("text=服务与权益").click()
        self.tab.ele("text=短视频随心推").click()
        print("服务与权益筛选选择成功")


        # 低价好货
        self.tab.eles("text=低价好货")[-1].click()
        print("添加低价好货筛选标签")


    def search_filter(self, keyword):
        search_ele = self.tab.ele("#SearchBarWrapper")
        search_input = search_ele.ele("tag=input")
        search_button = search_ele.ele("tag=button")
        self.tab.actions.move_to(search_input).click().input(keyword).wait(0.5, 2.5).move_to(search_button).click()


    def init_categroy(self,  category_choice:dict = {}, depth=1):
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
                choice_ele = self.tab.ele(f"text={second_category}")
            self.tab.actions.move_to(
                ele_or_loc=choice_ele,
                offset_x=random.uniform(15.0, 25.0)
            ).click()
            return

        self.tab.wait(0.5, 1.0)
        second_ele = self.tab.ele(f"text={second_category}")
        self.tab.actions.move_to(
            ele_or_loc=second_ele,
            offset_x=random.uniform(15.0, 25.0)
        )
        self.tab.wait(0.5, 1)

        self.tab.ele(f"text={third_category}").click()


    def main_logic(self):
        if self.init:
            self.tab.get("https://buyin.jinritemai.com/dashboard/merch-picking-library")
            self.tab.wait.eles_loaded("tag=tr")
            self.init_filter()
            self.init_categroy(self.category)
        else:
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
            resp = self.tab.listen.wait(timeout=30)
        except Exception as e:
            return "end"
        if resp:
            print("捕获到数据包，开始处理")
            json_data = resp.response.body
            product_list = json_data["data"]["summary_promotions"]
            if len(product_list) == 0:
                return "end"
            for product in product_list:
                self.product_list_filter(product)
        self.tab.listen.pause()


    def details_handle(self, promotion_id):
        promotion_url = f"https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?id={promotion_id}"
        self.browser.activate_tab(self.details_tab)
        self.details_tab.get(promotion_url)

        human_like_mouse_move(tab=self.details_tab, duration=random.randint(3, 7))
        non_core, core = self.core_part()
        sale_per_list = non_core["promotion_data"]["stat_data"]["promotion_stat_data_list"][-1]["stat_data"]['sales']['stat_list']
        if not self.check_video_sale_ratio(sale_per_list):
            print(f"未通过筛选：{core['data']['promotion_id']}")
            random_human_action(self.details_tab)
            return

        dynamic = self.promotion_part()
        if not dynamic["sale_content_data"].get("content_list", None) and dynamic["sale_content_data"]['count'] != 0:
            dynamic = self.next_page_packet()
        elif dynamic["sale_content_data"]['count'] == 0:
            return
        human_like_mouse_move(tab=self.details_tab, duration=random.randint(3, 7))

        if self.product_details_filter(non_core, dynamic):
            print(f"通过筛选：{core['data']['promotion_id']}，准备将数据入库")
            self.save_data(core, non_core, dynamic, is_pass=True)
            self.get_pass_video_data()
        else:
            print(f"未通过筛选：{core['data']['promotion_id']}")
            self.save_data(core, non_core, dynamic, is_pass=False)


    def auto_into_database(self, promotion_id):
        auto_into_tab = self.browser.new_tab()
        auto_into_tab.listen.start("buyin.jinritemai.com/pc/selection/decision/pack_detail")
        promotion_url = f"https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?id={promotion_id}"
        auto_into_tab.get(promotion_url)
        human_like_mouse_move(tab=auto_into_tab, duration=random.randint(3, 7))
        non_core, core = self.core_part(action_page=auto_into_tab)
        dynamic = self.promotion_part(action_page=auto_into_tab)
        print(f"{core['data']['promotion_id']}，准备将数据入库")
        self.save_data(core, non_core, dynamic, is_pass=True)
        self.get_pass_video_data(action_page=auto_into_tab)
        auto_into_tab.close()        


    def get_pass_video_data(self, action_page: MixTab = None):
        if action_page is None:
            action_page = self.details_tab
        while True:
            next_page_ele = action_page.ele('@title=下一页')
            btn_disable = next_page_ele.attr("aria-disabled")
            if btn_disable == 'false':
                print("准备翻页并获取数据")
                random_human_action(action_page)
                action_page.actions.move_to(next_page_ele).click()
                resp = action_page.listen.wait()
                if is_dynamic(resp):
                    print("获取到数据，开始插入")
                    dynamic_model = resp.response.body["data"]["model"]
                    promotion_id = extract_id_from_url(action_page.url)
                    self.save_dynamic_content(dynamic_model, promotion_id)
            else:
                print("已达到最后一页")
                break


    def core_part(self, action_page:MixTab = None):
        if action_page is None:
            action_page = self.details_tab
        try:
            resp_list = action_page.listen.wait(count=2, timeout=30)
            for resp in resp_list:
                if resp.request.postData["data_module"] == 'pc-non-core':
                    non_core = resp.response.body["data"]["model"]
                else:
                    core = resp.response.body
            return non_core, core
        except Exception as e:
            action_page.wait(0, 5)
            action_page.refresh()
            action_page.wait(0, 5)
            return self.core_part()


    def promotion_part(self, retry=0, max_retry=2, action_page:MixTab = None):
        if action_page is None:
            action_page = self.details_tab
        try:
            action_page.wait.ele_displayed("text=带货内容")
            dynamic_ele = action_page.ele("text=带货内容")
            action_page.actions.move_to(
                ele_or_loc=dynamic_ele,
                offset_x=random.uniform(-5.0, 5.0),
                offset_y=random.uniform(-2.5, 2.5)
            ).click(dynamic_ele)

            for resp in action_page.listen.steps():
                if resp.request.postData["data_module"] == 'dynamic':
                    break

            dynamic = resp.response.body["data"]["model"]
            return dynamic

        except Exception as e:
            if retry >= max_retry:
                raise e  # 达到最大重试次数，抛出异常
            action_page.wait(0, 5)
            action_page.refresh()
            action_page.wait(0, 5)
            return self.promotion_part(retry=retry + 1, max_retry=max_retry)


    def next_page_packet(self):
        while True:
            next_ele = self.details_tab.ele('@title=下一页')
            self.details_tab.actions.move_to(next_ele).click()
            resp = self.details_tab.listen.wait(timeout=30)
            if resp.response.body["data"]["model"]["sale_content_data"].get("content_list", None):
                break
        return resp.response.body["data"]["model"]


    def product_list_filter(self, data):
        sale_axis = data["base_model"]["product_info"]["sale_axis"]
        month_sale = data["base_model"]["product_info"]["month_sale"]["origin"]
        cooper_author_num = data["base_model"]["promotion_info"]["cooper_author_num"]["origin"]
        # trend = self.is_trending_up(sale_axis)
        proportion = (month_sale / cooper_author_num > 3)
        if proportion and not promotion_exists(self.session, data["promotion_id"]):
            self.queue.append(data["promotion_id"])


    def check_video_sale_ratio(self, sale_per_list: list, threshold: float = 60) -> bool:
        """
        检查视频销量占比是否达到阈值
        :param sale_per_list: promotion_stat_data_list 中的 sales stat_list
        :param threshold: 最低占比阈值，默认 60
        :return: True 表示达标，False 表示未达标
        """
        video_sale_per = None
        for stat in sale_per_list:
            if stat["key"] == "视频":
                video_sale_per = stat["value"]
                break
        if video_sale_per is None:
            return False
        return video_sale_per >= threshold


    def product_details_filter(self, non_core_data, dynamic_data):
        sales = non_core_data["promotion_data"]['calculate_data']['sales']
        pv = non_core_data["promotion_data"]['calculate_data']['pv']
        sale_per_list = non_core_data["promotion_data"]["stat_data"]["promotion_stat_data_list"][-1]["stat_data"]['sales']['stat_list']


        content_list = dynamic_data["sale_content_data"]["content_list"]
        range_3_sale_count = 0
        for content in content_list[:3]:
            range_3_sale_count += content["sales"]

        # 判断转换率
        if pv / sales < 0.15:
            return False
        
        # 销量前3占总销量
        if range_3_sale_count / sales > 0.8:
            return False

        # GPM
        if sales / pv * 1000 < 50:
            return False
        
        # 视频销量占比
        if not self.check_video_sale_ratio(sale_per_list, threshold=60):
            return False
        
        # 带货人数占比
        if len(content_list) > 3:
            key = "author_name"
            values = [d.get(key) for d in content_list]
            c = Counter(values)
            most_common_value, count = c.most_common(1)[0]
            ratio = count / len(content_list)
            if ratio > 0.66:
                return False        

        return True


    def is_trending_up(self, data, future_days=3):
        """
        判断时间序列数据未来是否有上涨趋势。
        data: [{"x": "20250708", "y": 0}, ...]
        future_days: 预测未来几天趋势
        返回: bool, True表示上涨，False表示不上涨
        """
        if not data or len(data) < 2:
            return False

        base_date = datetime.strptime(data[0]["x"], "%Y%m%d")
        X = np.array([(datetime.strptime(d["x"], "%Y%m%d") - base_date).days for d in data]).reshape(-1, 1)
        y = np.array([d["y"] for d in data])

        model = LinearRegression()
        model.fit(X, y)

        last_day = X[-1][0]
        future_X = np.array([last_day + i for i in range(1, future_days + 1)]).reshape(-1, 1)
        predicted = model.predict(future_X)

        return predicted[-1] > y[-1]
        


    def save_data(self, core_data, non_core_data, dynamic, is_pass):
        cos_type = core_data["data"]["model"]["product"]["product_cos"]['cos_label']['cos_type']
        if cos_type == 1:
            is_pass = False

        promotion_data = {
            "promotion_id": core_data['data']['promotion_id'],
            "product_id": core_data['data']['product_id'],
            "product_title": core_data["data"]["model"]["product"]["product_base"]['title'],
            "cover_url": core_data["data"]["model"]["product"]["product_base"]['cover'],
            "image_list":  json.dumps(core_data["data"]["model"]["product"]["product_base"]['images'], ensure_ascii=False),
            "product_price": core_data["data"]["model"]["product"]["product_price"]['price_label']['price'],
            "product_cos": core_data["data"]["model"]["product"]["product_cos"]['cos_label']['cos']['cos_fee'],
            "good_ratio": core_data["data"]["model"]["product"]["product_comment"]['good_ratio'],
            "product_sales": core_data["data"]["model"]["product"]["product_sales"]['product_label']["sales_num"],
            "product_match": core_data["data"]["model"]["product"]["product_match"]['author_num'],
            "shop_id": core_data["data"]["model"]["shop"]["shop_id"],
            "shop_name": core_data["data"]["model"]["shop"]["shop_base"]['shop_name'],
            "exper_score": core_data["data"]["model"]["shop"]["shop_exper_scores"]['shop_exper_score_label']['exper_score']['score'],
            "goods_score": core_data["data"]["model"]["shop"]["shop_exper_scores"]['shop_exper_score_label']['goods_score']['score'],
            "logistics_score": core_data["data"]["model"]["shop"]["shop_exper_scores"]['shop_exper_score_label']['logistics_score']['score'],
            "service_score": core_data["data"]["model"]["shop"]["shop_exper_scores"]['shop_exper_score_label']['service_score']['score'],
            "sales_amount": non_core_data['promotion_data']['calculate_data']['sales_amount'],
            "sales": non_core_data['promotion_data']['calculate_data']['sales'],
            "match_order_num": non_core_data['promotion_data']['calculate_data']['match_order_num'],
            "sales_content_num": non_core_data['promotion_data']['calculate_data']['sales_content_num'],
            "format_order_conversion_rate": non_core_data['promotion_data']['calculate_data']['format_order_conversion_rate'],
            "pv": non_core_data['promotion_data']['calculate_data']['pv'],
            "author_sale_per": non_core_data['promotion_data']['stat_data']['promotion_stat_data_list'][0]['stat_data']['sales']['stat_list'][0]['value'],
            "shop_sale_per": non_core_data['promotion_data']['stat_data']['promotion_stat_data_list'][0]['stat_data']['sales']['stat_list'][1]['value'],
            "live_sale_per": non_core_data['promotion_data']['stat_data']['promotion_stat_data_list'][1]['stat_data']['sales']['stat_list'][0]['value'],
            "video_sale_per": non_core_data['promotion_data']['stat_data']['promotion_stat_data_list'][1]['stat_data']['sales']['stat_list'][1]['value'],
            "visuals_sale_per": non_core_data['promotion_data']['stat_data']['promotion_stat_data_list'][1]['stat_data']['sales']['stat_list'][2]['value'],
            "shopwindow_sale_per": non_core_data['promotion_data']['stat_data']['promotion_stat_data_list'][1]['stat_data']['sales']['stat_list'][3]['value'],
            "is_pass": is_pass,
            "category": self.category_type,
            "roi_check": 0
        }

        promotion = insert_promotion_product(self.session, promotion_data)
        if promotion:
            print(f'插入成功：{core_data['data']['promotion_id']}')
        else:
            print(f'插入失败：{core_data['data']['promotion_id']}')

        self.save_dynamic_content(dynamic, core_data['data']['promotion_id'], is_pass=is_pass)


    def save_dynamic_content(self, dynamic, promotion_id: str, is_pass: bool = True) -> None:
        for sale_data in dynamic.get("sale_content_data", {}).get("content_list", []):
            sale_content_data = {
                "content_id": sale_data["content_id"],
                "promotion_id": promotion_id,
                "content_type": sale_data["content_type"],
                "content_title": sale_data["content_title"],
                "content_cover": sale_data["content_cover"],
                "video_url": sale_data.get("media_info", {}).get("video_url"),
                "duration": sale_data.get("media_info", {}).get("duration"),
                "cover_url": sale_data.get("media_info", {}).get("cover_url"),
                "publish_time": datetime.fromtimestamp(sale_data["publish_time"]),
                "author_name": sale_data["author_name"],
                "author_avatar": sale_data["author_avatar"],
                "author_sec_id": sale_data["author_sec_id"],
                "author_level": sale_data["author_level"],
                "author_fans_count": sale_data["author_fans_count"],
                "author_resident": sale_data["author_resident"],
                "share_url": sale_data["share_url"],
                "sales": sale_data["sales"],
                "format_sales": sale_data["format_sales"],
                "sales_amount": sale_data["sales_amount"],
                "format_sales_amount": sale_data["format_sales_amount"],
                "like_count": sale_data["like_count"],
                "play_count": sale_data["play_count"],
                "order_conversion_rate": sale_data["order_conversion_rate"],
                "format_order_conversion_rate": sale_data["format_order_conversion_rate"],
                "click_rate": sale_data["click_rate"],
                "comment_count": sale_data["comment_count"],
                "share_count": sale_data["share_count"],
                "pcu": sale_data["pcu"],
                "is_self_sale": sale_data["is_self_sale"]
            }

            content = insert_sale_content(self.session, sale_content_data)
            if content:
                print(f'插入成功：{sale_data["content_id"]}')
            else:
                print(f'插入失败：{sale_data["content_id"]}')
            
            if is_pass:
                obj: Material = get_promotion_product_by_id(session=self.session ,promotion_id=promotion_id)
                material_data = {
                    "advertiser_id": self.qianchuan_id,
                    "promotion_id": promotion_id,
                    "product_id": obj.product_id,
                    "qianchuan_id": self.qianchuan_id,
                    "shop_id": obj.shop_id,
                    "shop_name": obj.shop_name,
                    "content_id": sale_data["content_id"],
                    "video_path": f"/data/public/remove_face_video/{promotion_id}",
                    "video_name": f'{sale_data["content_id"]}.mp4',
                    "is_qianchuan": 1,
                }
                material = insert_material(self.session, material_data)
                if material:
                    print(f'插入成功：{sale_data["content_id"]}')
                else:
                    print(f'插入失败：{sale_data["content_id"]}')