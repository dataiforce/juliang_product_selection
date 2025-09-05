import time, random

class DomainSleepController:
    def __init__(self):
        # 短周期状态
        self.short_start = time.monotonic()
        self.short_work = random.uniform(150, 300)   # 5–10分钟
        self.short_rest = random.uniform(75, 150)   # 2–4分钟
        # 长周期状态
        self.long_start = time.monotonic()
        self.long_work = random.uniform(900, 1800)  # 30–60分钟
        self.long_rest = random.uniform(450, 900)   # 15–25分钟


    def maybe_sleep(self):
        now = time.monotonic()

        # 长周期优先
        if now - self.long_start > self.long_work:
            print(f"触发长周期休眠 {self.long_rest:.1f}s")
            time.sleep(self.long_rest)

            # ✅ 重置长周期
            self.long_start = time.monotonic()
            self.long_work = random.uniform(900, 1800)
            self.long_rest = random.uniform(450, 900)

            # ✅ 同时重置短周期，避免长休眠后立即短休眠
            self.short_start = self.long_start
            self.short_work = random.uniform(150, 300)
            self.short_rest = random.uniform(75, 150)
            print(f"长休眠结束 {self.short_rest:.1f}s")
            return

        # 短周期判断
        if now - self.short_start > self.short_work:
            print(f"触发短周期休眠 {self.short_rest:.1f}s")
            time.sleep(self.short_rest)

            # 重置短周期
            self.short_start = time.monotonic()
            self.short_work = random.uniform(150, 300)
            self.short_rest = random.uniform(75, 150)
            
            print(f"短休眠结束 {self.short_rest:.1f}s")
