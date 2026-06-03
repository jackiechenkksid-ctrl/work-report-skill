#!/usr/bin/env python3
"""
青鸾系统 - 自动登录 & 考勤数据拉取脚本
用法: python3 login_and_fetch.py <username> <password> [--date 20260603] [--range 20260601-20260605]
"""

import sys, json, os, argparse, base64
import requests
import urllib3
urllib3.disable_warnings()

BASE_URL = "https://c.jbufa.com"
CLIENT_ID = "web"
CLIENT_SECRET = "111111"


def login(username: str, password: str) -> str:
    """登录青鸾系统，返回 access_token"""
    session = requests.Session()
    session.verify = False

    # OAuth2 Password Grant
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    resp = session.post(f"{BASE_URL}/api/oauth/token", data={
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "server",
    }, headers={
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }, timeout=15)

    data = resp.json()

    # API 返回 code="000" 表示成功，code="001" 表示失败
    if data.get("code") != "000" and not data.get("access_token"):
        sys.exit(f"❌ 登录失败: {data.get('msg', '未知错误')}")

    token = data.get("access_token")
    if not token:
        sys.exit("❌ 登录成功但未获取到 token")

    print(f"✅ 登录成功")
    return token, session


def fetch_checkin_records(token: str, start_date: str, end_date: str):
    """拉取考勤打卡记录"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # 已验证的 API 端点
    endpoints = [
        ("GET", f"/api/checkin/records?startDate={start_date}&endDate={end_date}", None),
        ("GET", f"/api/checkin/tracks?startDate={start_date}&endDate={end_date}", None),
    ]

    results = {}
    for method, path, body in endpoints:
        try:
            if method == "POST":
                resp = requests.post(f"{BASE_URL}{path}", json=body, headers=headers, timeout=30)
            else:
                resp = requests.get(f"{BASE_URL}{path}", headers=headers, timeout=30)

            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "000":
                    key = path.split("?")[0].split("/")[-1]  # records or tracks
                    results[key] = data.get("data", [])
                    print(f"✅ 获取 {key} 成功: {len(results[key])} 条")
            else:
                print(f"⚠️  {method} {path} → {resp.status_code}")
        except Exception as e:
            print(f"⚠️  {method} {path} → {e}")

    if not results:
        sys.exit("❌ 所有 API 尝试均失败")

    return results


def format_output(data: dict, start_date: str, end_date: str):
    """格式化输出为 JSON，方便 AI 解析"""
    print("\n===== 考勤数据（JSON） =====")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"\n日期范围: {start_date} ~ {end_date}")


def main():
    parser = argparse.ArgumentParser(description="青鸾系统考勤数据拉取")
    parser.add_argument("username", help="登录用户名")
    parser.add_argument("password", help="登录密码")
    parser.add_argument("--date", help="单日查询，格式 yyyyMMdd，如 20260603")
    parser.add_argument("--range", help="日期范围查询，格式 yyyyMMdd-yyyyMMdd，如 20260601-20260605")
    args = parser.parse_args()

    # 确定日期范围
    if args.range:
        start_date, end_date = args.range.split("-")
    elif args.date:
        start_date = end_date = args.date
    else:
        # 默认今天
        from datetime import date
        today = date.today().strftime("%Y%m%d")
        start_date = end_date = today

    # 登录
    token, session = login(args.username, args.password)

    # 拉取考勤数据
    data = fetch_checkin_records(token, start_date, end_date)

    # 输出
    format_output(data, start_date, end_date)


if __name__ == "__main__":
    main()
