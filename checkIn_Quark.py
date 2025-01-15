import os
import re
import sys
import requests
from datetime import datetime

# 替代 notify 功能
def send(title, message):
    print(f"[{datetime.now()}] {title}: {message}")

# 获取环境变量 
def get_env(): 
    try:
        # 判断 COOKIE_QUARK是否存在于环境变量 
        if "COOKIE_QUARK" in os.environ: 
            # 读取系统变量以 \n 或 && 分割变量 
            cookie_list = re.split('\n|&&', os.environ.get('COOKIE_QUARK')) 
            print(f"[{datetime.now()}] ✅ 成功读取环境变量 COOKIE_QUARK，共 {len(cookie_list)} 个账号")
        else: 
            # 标准日志输出 
            print(f"[{datetime.now()}] ❌ 未添加 COOKIE_QUARK 变量") 
            send('夸克自动签到', '❌ 未添加 COOKIE_QUARK 变量') 
            # 脚本退出 
            sys.exit(0) 

        return cookie_list
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 获取环境变量时发生错误: {e}")
        sys.exit(1)

# 其他代码...

class Quark:
    '''
    Quark类封装了签到、领取签到奖励的方法
    '''
    def __init__(self, user_data):
        '''
        初始化方法
        :param user_data: 用户信息，用于后续的请求
        '''
        self.param = user_data
        print(f"[{datetime.now()}] 🚀 初始化 Quark 实例，用户: {self.param.get('user')}")

    def convert_bytes(self, b):
        '''
        将字节转换为 MB GB TB
        :param b: 字节数
        :return: 返回 MB GB TB
        '''
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = 0
        while b >= 1024 and i < len(units) - 1:
            b /= 1024
            i += 1
        return f"{b:.2f} {units[i]}"

    def get_growth_info(self):
        '''
        获取用户当前的签到信息
        :return: 返回一个字典，包含用户当前的签到信息
        '''
        try:
            url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info"
            querystring = {
                "pr": "ucpro",
                "fr": "android",
                "kps": self.param.get('kps'),
                "sign": self.param.get('sign'),
                "vcode": self.param.get('vcode')
            }
            print(f"[{datetime.now()}] 📡 请求获取用户签到信息: {url}")
            response = requests.get(url=url, params=querystring).json()
            print(f"[{datetime.now()}] 📦 收到签到信息响应: {response}")
            if response.get("data"):
                return response["data"]
            else:
                print(f"[{datetime.now()}] ❌ 获取签到信息失败: {response.get('message', '未知错误')}")
                return False
        except Exception as e:
            print(f"[{datetime.now()}] ❌ 获取签到信息时发生错误: {e}")
            return False

    def get_growth_sign(self):
        '''
        获取用户当前的签到信息
        :return: 返回一个字典，包含用户当前的签到信息
        '''
        try:
            url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign"
            querystring = {
                "pr": "ucpro",
                "fr": "android",
                "kps": self.param.get('kps'),
                "sign": self.param.get('sign'),
                "vcode": self.param.get('vcode')
            }
            data = {"sign_cyclic": True}
            print(f"[{datetime.now()}] 📡 请求执行签到: {url}")
            response = requests.post(url=url, json=data, params=querystring).json()
            print(f"[{datetime.now()}] 📦 收到签到响应: {response}")
            if response.get("data"):
                return True, response["data"]["sign_daily_reward"]
            else:
                return False, response["message"]
        except Exception as e:
            print(f"[{datetime.now()}] ❌ 执行签到时发生错误: {e}")
            return False, str(e)

    def do_sign(self):
        '''
        执行签到任务
        :return: 返回一个字符串，包含签到结果
        '''
        log = ""
        try:
            # 每日领空间
            growth_info = self.get_growth_info()
            if growth_info:
                log += (
                    f"[{datetime.now()}] {'88VIP' if growth_info['88VIP'] else '普通用户'} {self.param.get('user')}\n"
                    f"[{datetime.now()}] 💾 网盘总容量：{self.convert_bytes(growth_info['total_capacity'])}，"
                    f"签到累计容量：")
                if "sign_reward" in growth_info['cap_composition']:
                    log += f"{self.convert_bytes(growth_info['cap_composition']['sign_reward'])}\n"
                else:
                    log += "0 MB\n"
                if growth_info["cap_sign"]["sign_daily"]:
                    log += (
                        f"[{datetime.now()}] ✅ 签到日志: 今日已签到+{self.convert_bytes(growth_info['cap_sign']['sign_daily_reward'])}，"
                        f"连签进度({growth_info['cap_sign']['sign_progress']}/{growth_info['cap_sign']['sign_target']})\n"
                    )
                else:
                    sign, sign_return = self.get_growth_sign()
                    if sign:
                        log += (
                            f"[{datetime.now()}] ✅ 执行签到: 今日签到+{self.convert_bytes(sign_return)}，"
                            f"连签进度({growth_info['cap_sign']['sign_progress'] + 1}/{growth_info['cap_sign']['sign_target']})\n"
                        )
                    else:
                        log += f"[{datetime.now()}] ❌ 签到异常: {sign_return}\n"
            else:
                log += f"[{datetime.now()}] ❌ 签到异常: 获取成长信息失败\n"
        except Exception as e:
            log += f"[{datetime.now()}] ❌ 执行签到任务时发生错误: {e}\n"

        return log


def main():
    '''
    主函数
    :return: 返回一个字符串，包含签到结果
    '''
    msg = ""
    try:
        global cookie_quark
        cookie_quark = get_env()

        print(f"[{datetime.now()}] ✅ 检测到共 {len(cookie_quark)} 个夸克账号\n")

        i = 0
        while i < len(cookie_quark):
            # 获取user_data参数
            user_data = {}  # 用户信息
            for a in cookie_quark[i].replace(" ", "").split(';'):
                if not a == '':
                    user_data.update({a[0:a.index('=')]: a[a.index('=') + 1:]})
            print(f"[{datetime.now()}] 🔍 解析用户数据: {user_data}")
            # 开始任务
            log = f"[{datetime.now()}] 🙍🏻‍♂️ 第 {i + 1} 个账号"
            msg += log
            # 登录
            log = Quark(user_data).do_sign()
            msg += log + "\n"

            i += 1

        print(f"[{datetime.now()}] 📝 签到结果汇总:\n{msg}")

        try:
            send('夸克自动签到', msg)
        except Exception as err:
            print(f"[{datetime.now()}] ❌ 发送通知时发生错误: {err}")

        return msg[:-1]
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 主函数运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print(f"[{datetime.now()}] ----------夸克网盘开始签到----------")
    main()
    print(f"[{datetime.now()}] ----------夸克网盘签到完毕----------")
