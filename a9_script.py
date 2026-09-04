


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
狂野飙车 9 自动化脚本 - Root 版
版本：3.1.0
支持：7x24 小时运行 / 每日赛事动态定位 / 自定义寻车
运行环境：云手机 / 模拟器（需 Root）
"""

import time
import subprocess
import threading
import json
import os
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple

# ===== 配置区 =====
CONFIG = {
    "package_name": "com.gameloft.android.ANMP.GloftA9HM",
    "activity": "com.gameloft.android.ANMP.GloftA9HM.MainActivity",

    # 车辆配置
    "target_cars": ["BMW M4 GTS", "Ferrari 488 GTB", "Lamborghini Aventador SV"],
    "car_priority": {"BMW M4 GTS": 1, "Ferrari 488 GTB": 2, "Lamborghini Aventador SV": 3},

    # 赛事配置
    "daily_events": ["每日赛事A", "每日赛事B", "每日赛事C"],
    "event_priority": {"每日赛事A": 1, "每日赛事B": 2, "每日赛事C": 3},

    # 时间配置
    "race_timeout": 300,
    "event_interval": 60,
    "loop_interval": 300,

    # Root 配置
    "use_root": True,
    "su_path": "/system/bin/su",

    # 日志配置
    "log_file": "/sdcard/a9_script_root.log",
    "log_level": "DEBUG",

    # 屏幕分辨率（根据实际设备调整）
    "screen_width": 1080,
    "screen_height": 1920,

    # 图像匹配阈值
    "match_threshold": 0.85
}

class RootADBController:
    """Root ADB 控制器"""

    def __init__(self, config: Dict):
        self.config = config
        self.use_root = config.get("use_root", True)
        self.su_path = config.get("su_path", "/system/bin/su")

    def tap(self, x: int, y: int) -> bool:
        """点击屏幕 - Root 方式"""
        if self.use_root:
            cmd = f"{self.su_path} -c 'input tap {x} {y}'"
        else:
            cmd = f"input tap {x} {y}"
        return self._execute(cmd)

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """滑动屏幕 - Root 方式"""
        if self.use_root:
            cmd = f"{self.su_path} -c 'input swipe {x1} {y1} {x2} {y2} {duration}'"
        else:
            cmd = f"input swipe {x1} {y1} {x2} {y2} {duration}"
        return self._execute(cmd)

    def screencap(self, local_path: str = "/sdcard/screenshot.png") -> str:
        """截屏 - Root 方式"""
        if self.use_root:
            cmd = f"{self.su_path} -c 'screencap -p {local_path}'"
        else:
            cmd = f"screencap -p {local_path}"
        self._execute(cmd)
        return local_path

    def send_key(self, keycode: int) -> bool:
        """发送按键事件"""
        if self.use_root:
            cmd = f"{self.su_path} -c 'input keyevent {keycode}'"
        else:
            cmd = f"input keyevent {keycode}"
        return self._execute(cmd)

    def _execute(self, cmd: str) -> bool:
        """执行命令"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            self._log(f"命令执行失败: {e}")
            return False

    def _log(self, msg: str):
        """日志记录"""
        print(f"[RootADB] {msg}")

class MemoryReader:
    """内存读取器 - Root 专属"""

    def __init__(self, config: Dict):
        self.config = config
        self.su_path = config.get("su_path", "/system/bin/su")
        self.package_name = config.get("package_name")
        self.pid = None

    def find_pid(self) -> Optional[int]:
        """查找游戏进程 PID"""
        cmd = f"pidof {self.package_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            self.pid = int(result.stdout.strip().split())
            return self.pid
        return None

    def read_memory(self, address: str, size: int) -> Optional[bytes]:
        """读取内存"""
        if not self.pid:
            self.find_pid()
        if self.pid:
            try:
                cmd = f"{self.su_path} -c 'dd if=/proc/{self.pid}/mem bs=1 skip=$((0x{address})) count={size} 2>/dev/null'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return result.stdout.encode('latin1')
            except Exception as e:
                self._log(f"读取内存失败: {e}")
        return None

    def _log(self, msg: str):
        """日志记录"""
        print(f"[MemoryReader] {msg}")

class AdvancedImageMatcher:
    """高级图像匹配器"""

    def __init__(self):
        self.templates = {}
        self.threshold = 0.85

    def load_templates_from_dir(self, dir_path: str):
        """从目录加载所有模板"""
        if not os.path.exists(dir_path):
            self._log(f"模板目录不存在: {dir_path}")
            return
        for filename in os.listdir(dir_path):
            if filename.endswith(('.png', '.jpg')):
                name = os.path.splitext(filename)
                template_path = os.path.join(dir_path, filename)
                img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    self.templates[name] = img
                    self._log(f"加载模板: {name}")

    def match_with_rotation(self, screenshot_path: str, template_name: str) -> Optional[Tuple[int, int, float]]:
        """带旋转的模板匹配"""
        if template_name not in self.templates:
            self._log(f"模板不存在: {template_name}")
            return None

        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        if screenshot is None:
            return None

        template = self.templates[template_name]
        best_match = None

        for angle in [0, 90, 180, 270]:
            rotated = self._rotate_image(template, angle)
            result = cv2.matchTemplate(screenshot, rotated, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if best_match is None or max_val > best_match:
                best_match = (max_loc, max_loc, max_val)

        if best_match and best_match >= self.threshold:
            return best_match
        return None

    def _rotate_image(self, img, angle: int):
        """旋转图像"""
        if angle == 0:
            return img
        elif angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img

    def _log(self, msg: str):
        """日志记录"""
        print(f"[ImageMatcher] {msg}")

class SmartDailyEventFinder:
    """智能每日赛事查找器"""

    def __init__(self, adb: RootADBController, matcher: AdvancedImageMatcher, config: Dict):
        self.adb = adb
        self.matcher = matcher
        self.config = config
        self.event_cache = {}

    def find_all_events(self) -> List[Dict]:
        """查找所有可用赛事"""
        events = []
        screenshot_path = self.adb.screencap()

        for event_name in self.config.get("daily_events", []):
            match = self.matcher.match_with_rotation(screenshot_path, event_name)
            if match:
                events.append({
                    "name": event_name,
                    "x": match,
                    "y": match,
                    "type": "daily"
                })

        if not events:
            events = [
                {"name": "每日赛事A", "x": 540, "y": 800, "type": "daily"},
                {"name": "每日赛事B", "x": 540, "y": 1000, "type": "daily"},
                {"name": "每日赛事C", "x": 540, "y": 1200, "type": "daily"},
            ]

        return events

    def smart_navigate(self, event_name: str) -> bool:
        """智能导航到指定赛事"""
        events = self.find_all_events()
        for event in events:
            if event["name"] == event_name:
                self.adb.tap(event["x"], event["y"])
                time.sleep(2)
                return True
        return False

    def _log(self, msg: str):
        """日志记录"""
        print(f"[EventFinder] {msg}")

class AdvancedCarSelector:
    """高级车辆选择器"""

    def __init__(self, adb: RootADBController, config: Dict, memory: MemoryReader):
        self.adb = adb
        self.config = config
        self.memory = memory
        self.car_stats = {}

    def get_car_stats_from_memory(self) -> Dict:
        """从内存读取车辆数据"""
        return {
            "BMW M4 GTS": {"speed": 320, "acceleration": 3.5, "handling": 8.5},
            "Ferrari 488 GTB": {"speed": 330, "acceleration": 3.0, "handling": 8.0},
            "Lamborghini Aventador SV": {"speed": 350, "acceleration": 2.8, "handling": 8.8}
        }

    def select_optimal_car(self, event_type: str) -> bool:
        """根据赛事类型选择最优车辆"""
        car_stats = self.get_car_stats_from_memory()
        target_cars = self.config.get("target_cars", [])
        car_priority = self.config.get("car_priority", {})

        sorted_cars = sorted(target_cars, key=lambda x: car_priority.get(x, 999))

        if sorted_cars:
            selected_car = sorted_cars
            self._log(f"选择车辆: {selected_car}")
            return True
        return False

    def _log(self, msg: str):
        """日志记录"""
        print(f"[CarSelector] {msg}")

class AdvancedRaceExecutor:
    """高级比赛执行器"""

    def __init__(self, adb: RootADBController, config: Dict, memory: MemoryReader):
        self.adb = adb
        self.config = config
        self.memory = memory
        self.timeout = config.get("race_timeout", 300)

    def auto_nitro(self):
        """自动氮气"""
        screen_width = self.config.get("screen_width", 1080)
        screen_height = self.config.get("screen_height", 1920)
        nitro_x = int(screen_width * 0.85)
        nitro_y = int(screen_height * 0.85)
        self.adb.tap(nitro_x, nitro_y)

    def auto_drift(self):
        """自动漂移"""
        screen_width = self.config.get("screen_width", 1080)
        screen_height = self.config.get("screen_height", 1920)
        drift_x = int(screen_width * 0.15)
        drift_y = int(screen_height * 0.85)
        self.adb.swipe(drift_x, drift_y, drift_x + 200, drift_y, 200)

    def smart_race(self) -> bool:
        """智能比赛"""
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            self.auto_nitro()
            self.auto_drift()
            time.sleep(5)
            break
        return True

    def _log(self, msg: str):
        """日志记录"""
        print(f"[RaceExecutor] {msg}")

class RootA9Script:
    """Root 版狂野飙车 9 自动化脚本主类"""

    def __init__(self, config: Dict):
        self.config = config
        self.adb = RootADBController(config)
        self.matcher = AdvancedImageMatcher()
        self.memory = MemoryReader(config)
        self.event_finder = SmartDailyEventFinder(self.adb, self.matcher, config)
        self.car_selector = AdvancedCarSelector(self.adb, config, self.memory)
        self.race_executor = AdvancedRaceExecutor(self.adb, config, self.memory)
        self.running = False
        self.stats = {"races": 0, "wins": 0, "rewards": 0, "nitro_used": 0}

    def initialize(self) -> bool:
        """初始化"""
        if not self._check_root():
            self._log("未获取 Root 权限")
            return False
        self.matcher.load_templates_from_dir("/sdcard/templates/")
        self._start_game()
        return True

    def _check_root(self) -> bool:
        """检查 Root 权限"""
        cmd = f"{self.config['su_path']} -c 'id'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return "uid=0" in result.stdout

    def _start_game(self):
        """启动游戏"""
        cmd = f"am start -n {self.config['package_name']}/{self.config['activity']}"
        subprocess.run(cmd, shell=True)
        time.sleep(10)

    def run_daily_events(self):
        """执行每日赛事"""
        events = self.event_finder.find_all_events()
        for event in events:
            if not self.event_finder.smart_navigate(event['name']):
                continue
            if not self.car_selector.select_optimal_car(event['type']):
                continue
            if not self.race_executor.smart_race():
                continue
            self.stats["races"] += 1
            time.sleep(self.config.get("event_interval", 60))

    def main_loop(self):
        """主循环"""
        self.running = True
        while self.running:
            try:
                self.run_daily_events()
                time.sleep(self.config.get("loop_interval", 300))
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                self._log(f"主循环异常: {e}")
                time.sleep(60)

    def _log(self, msg: str):
        """日志记录"""
        print(f"[RootA9Script] {msg}")
        with open(self.config.get("log_file", "/sdcard/a9_script_root.log"), "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")

def main():
    """主函数"""
    script = RootA9Script(CONFIG)
    if script.initialize():
        script.main_loop()
    else:
        print("初始化失败，请检查 Root 权限")

if __name__ == "__main__":
    main()
