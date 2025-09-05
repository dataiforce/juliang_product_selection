from DrissionPage import Chromium
from db.manage.base import get_session
from db.manage.selection import get_promotion_product_by_id
from crawl.uitls import human_like_mouse_move
import random


class checkCosChange:
    def __init__(self, browser: Chromium):
        self.browser = browser
        self.check_tab = browser.new_tab()
        self.session = get_session()
        self.check_tab.listen.start("buyin.jinritemai.com/pc/selection/decision/pack_detail")
        self.check_tab.listen.pause()

    def check_one(self, promotion_id):
        promotion_url = f"https://buyin.jinritemai.com/dashboard/merch-picking-library/merch-promoting?id={promotion_id}"
        self.check_tab.listen.resume()
        self.check_tab.get(promotion_url)
        resp = self.check_tab.listen.wait(timeout=30)
        self.check_tab.listen.pause()
        core = resp.response.body["data"]["model"]["product"]["product_cos"]['cos_label']['cos']['cos_fee']
        human_like_mouse_move(tab=self.check_tab, duration=random.randint(3, 7))
        if random.randint(0, 10) % 2:
            self.check_tab.actions.scroll(random.uniform(100, 500))
        data = get_promotion_product_by_id(promotion_id=promotion_id)

        if data.product_cos != core:
            print(f"原佣金：{data.product_cos}，当前佣金：{core}，发生变化")
        else:
            print(f"{core} 未发生变化")