from crawl.chrome_browser import ChromeBrower
from crawl.product_selection import AutoProductSelection

if __name__ == "__main__":
    auto = ChromeBrower(tab_count=2, port=29681)
    tab = auto.get_tab(0)
    details_tab = auto.get_tab(1)
    browser = auto.get_browser()
    category = {
        "first": "食品饮料"
    }
    selecion = AutoProductSelection(main_tab=tab, details_tab=details_tab, browser=browser, category=category)
    selecion.search_filter("茶")
