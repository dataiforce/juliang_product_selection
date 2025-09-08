from crawl.chrome_browser import ChromeBrower
from crawl.save_data import AutoProductSelection
from crawl.uitls import load_json, is_done, mark_done, set_category_path
from config import Config
import os

def run_spider(category:dict, action_type:str = "list"):
    auto = ChromeBrower(tab_count=2, port=29681)
    tab = auto.get_tab(0)
    details_tab = auto.get_tab(1)
    browser = auto.get_browser()
    selecion = AutoProductSelection(main_tab=tab, details_tab=details_tab, browser=browser, category=category)
    if action_type == "list":
        selecion.list_page_logic()
    else:
        selecion.detail_page_logic()


def create_category():
    source = load_json(r"E:\巨量百应自动选品\category\食品饮料.json")
    category_list = []
    for i in range(2):
        base_source = source[i]
        for third in base_source["childs"]:
            category = {
                "first": "食品饮料",
                "second": base_source["name"],
                "third": third["name"]
            }
            category_list.append(category)
    category = {
        "first": "食品饮料",
        "second": "茶"
    }
    category_list.append(category)
    return category_list


if __name__ == "__main__":
    log_json = os.path.join(Config.BASE_PATH, "食品饮料", "log.json")
    category_list = create_category()
    for category in category_list:
        if is_done(log_json, category, done_type="detail_done"):
            print(f"{set_category_path(category)} 已经完成，跳过")
            continue
        run_spider(category, "details")
        mark_done(log_json, category, done_type="detail_done")
        print(f"{set_category_path(category)} 已完成")
