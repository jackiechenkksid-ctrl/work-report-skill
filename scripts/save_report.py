#!/usr/bin/env python3
"""
公司内部系统 - 日报/周报保存脚本
用法:
  python3 save_report.py <username> <password> --daily   "<日报内容>" [--status 0]
  python3 save_report.py <username> <password> --weekly  "<周报内容>" [--status 0]

status: 0=仅保存草稿, 1=提交（默认0，只保存不提交）
"""

import sys, argparse, base64
import requests
import urllib3
urllib3.disable_warnings()

BASE_URL = "https://<YOUR_SYSTEM_URL>"
CLIENT_ID = "<YOUR_CLIENT_ID>"
CLIENT_SECRET = "<YOUR_CLIENT_SECRET>"


def login(username: str, password: str) -> str:
    """登录，返回 access_token"""
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(f"{BASE_URL}/api/oauth/token", data={
        "grant_type": "password", "username": username, "password": password, "scope": "server",
    }, headers={
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }, timeout=15, verify=False)

    data = resp.json()
    if data.get("code") != "000" and not data.get("access_token"):
        sys.exit(f"❌ 登录失败: {data.get('msg', '未知错误')}")

    print(f"✅ 登录成功")
    return data["access_token"]


def save_weekly_report(token: str, start_date: str, end_date: str, content: str, status: str = "0"):
    """保存周报（POST /api/statement/week）"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "statementDataSnapshot": content,
        "status": status,  # "0"=草稿, "1"=提交
    }

    resp = requests.post(f"{BASE_URL}/api/statement/week", json=body, headers=headers, timeout=15, verify=False)
    data = resp.json()

    if data.get("success") or data.get("code") == "000":
        print(f"✅ 周报{'已保存（草稿）' if status == '0' else '已提交'}！")
        return True
    else:
        msg = data.get("msg", "未知错误")
        if "已经提交" in msg or "already" in msg.lower():
            print(f"⚠️  周报已存在（{msg}），尝试使用 PUT 更新...")
            return update_weekly_report(token, start_date, end_date, content, status)
        print(f"❌ 保存失败: {msg}")
        return False


def update_weekly_report(token: str, start_date: str, end_date: str, content: str, status: str = "0"):
    """更新已有周报"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "statementDataSnapshot": content,
        "status": status,
    }

    resp = requests.put(f"{BASE_URL}/api/statement/week", json=body, headers=headers, timeout=15, verify=False)
    data = resp.json()

    if data.get("success") or data.get("code") == "000":
        print(f"✅ 周报已更新！")
        return True
    else:
        print(f"❌ 更新失败: {data.get('msg', '未知错误')}")
        return False


def save_daily_report(token: str, date: str, content: str, status: str = "0"):
    """保存日报（POST /api/statement/daily）"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    body = {
        "startDate": date,
        "endDate": date,
        "statementDataSnapshot": content,
        "status": status,
    }

    resp = requests.post(f"{BASE_URL}/api/statement/daily", json=body, headers=headers, timeout=15, verify=False)
    data = resp.json()

    if data.get("success") or data.get("code") == "000":
        print(f"✅ 日报{'已保存（草稿）' if status == '0' else '已提交'}！")
        return True
    elif data.get("code") == "006":
        print(f"⚠️  日报已存在（{data.get('msg')}），尝试更新...")
        return update_daily_report(token, date, content, status)
    else:
        print(f"❌ 保存失败: {data.get('msg', '未知错误')}")
        return False


def update_daily_report(token: str, date: str, content: str, status: str = "0"):
    """更新已有日报"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    body = {
        "startDate": date,
        "endDate": date,
        "statementDataSnapshot": content,
        "status": status,
    }

    resp = requests.put(f"{BASE_URL}/api/statement/daily", json=body, headers=headers, timeout=15, verify=False)
    data = resp.json()

    if data.get("success") or data.get("code") == "000":
        print(f"✅ 日报已更新！")
        return True
    else:
        print(f"❌ 更新失败: {data.get('msg', '未知错误')}")
        return False


def main():
    parser = argparse.ArgumentParser(description="日报/周报保存")
    parser.add_argument("username", help="登录用户名")
    parser.add_argument("password", help="登录密码")
    parser.add_argument("--daily", help="日报内容")
    parser.add_argument("--weekly", help="周报内容")
    parser.add_argument("--date", help="日期（日报用），格式 yyyy-MM-dd，默认今天")
    parser.add_argument("--week-start", help="周报开始日期，格式 yyyy-MM-dd")
    parser.add_argument("--week-end", help="周报结束日期，格式 yyyy-MM-dd")
    parser.add_argument("--status", default="0", choices=["0", "1"],
                        help="0=仅保存草稿（默认）, 1=提交")
    args = parser.parse_args()

    if not args.daily and not args.weekly:
        sys.exit("❌ 请指定 --daily 或 --weekly")

    # 日期处理
    from datetime import date, timedelta
    today = date.today()

    if args.daily:
        report_date = args.date or today.strftime("%Y-%m-%d")
    else:
        # 默认本周一至周日
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        report_date = args.week_start or monday.strftime("%Y-%m-%d")
        end_date = args.week_end or sunday.strftime("%Y-%m-%d")

    # 登录
    token = login(args.username, args.password)

    # 保存
    status_text = "草稿" if args.status == "0" else "提交"
    if args.daily:
        print(f"📝 保存日报（{report_date}，{status_text}）...")
        save_daily_report(token, report_date, args.daily, args.status)
    elif args.weekly:
        print(f"📝 保存周报（{report_date} ~ {end_date}，{status_text}）...")
        save_weekly_report(token, report_date, end_date, args.weekly, args.status)


if __name__ == "__main__":
    main()
