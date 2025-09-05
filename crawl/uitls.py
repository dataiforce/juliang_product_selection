import random
import time
from DrissionPage._pages.mix_tab import MixTab
from urllib.parse import urlparse, parse_qs

def cubic_bezier(p0, p1, p2, p3, t):
    """三次贝塞尔曲线插值"""
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def human_like_mouse_move(tab: MixTab, duration=2):
    mouse = tab.actions
    width, height = tab.rect.viewport_size

    # 如果初始位置不在窗口内，随机一个起点
    if not (0 <= mouse.curr_x <= width and 0 <= mouse.curr_y <= height):
        x0 = random.randint(0, width)
        y0 = random.randint(0, height)
        mouse.move(x0, y0, random.uniform(0.05, 0.25))
    else:
        x0 = mouse.curr_x
        y0 = mouse.curr_y

    start_time = time.time()
    while time.time() - start_time < duration:
        # 随机终点
        x3 = random.randint(0, width)
        y3 = random.randint(0, height)

        # 控制点，限制在窗口内
        x1 = clamp(
            x0 + random.randint(-int(min(300, x0)), int(min(300, width - x0))),
            0, width
        )
        y1 = clamp(
            y0 + random.randint(-int(min(200, y0)), int(min(200, height - y0))),
            0, height
        )
        x2 = clamp(
            x3 + random.randint(-int(min(300, x3)), int(min(300, width - x3))),
            0, width
        )
        y2 = clamp(
            y3 + random.randint(-int(min(200, y3)), int(min(200, height - y3))),
            0, height
        )
        segment_duration = random.uniform(0.8, 1.5)
        steps = random.randint(40, 70)
        delay = segment_duration / steps

        for i in range(steps + 1):
            t = i / steps
            x_abs = cubic_bezier(x0, x1, x2, x3, t)
            y_abs = cubic_bezier(y0, y1, y2, y3, t)

            # 相对偏移基于 curr_x / curr_y
            offset_x = int(x_abs - mouse.curr_x)
            offset_y = int(y_abs - mouse.curr_y)

            mouse.move(offset_x, offset_y, delay)

            # 偶尔轻微停顿
            if random.random() < 0.05:
                time.sleep(random.uniform(0.02, 0.08))

        # 更新起点为本段终点
        x0, y0 = x3, y3



def random_human_action(tab: MixTab, duration=3):
    base_random = random.randint(1, 10)
    if base_random % 3 == 0:
        scroll_distance = random.randint(200, 400)
        tab.actions.scroll(-scroll_distance)
        human_like_mouse_move(tab, duration/2)
        tab.actions.scroll(scroll_distance + random.uniform(-10, 10))
    elif base_random % 2 == 0:
        human_like_mouse_move(tab, duration + random.uniform(-1, 1))
    else:
        time.sleep(duration + random.uniform(-1, 1))


def extract_id_from_url(url: str) -> str:
    """
    从 URL 中提取 'id' 参数的值
    :param url: 包含查询参数的完整 URL
    :return: 'id' 参数的值，若不存在则返回 None
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('id', [None])[0]


def is_dynamic(resp) -> bool:
    """
    判断响应包是否为 dynamic 类型
    :param resp: 监听得到的响应对象
    :return: True if dynamic, else False
    """
    return resp.request.postData.get("data_module") == "dynamic"