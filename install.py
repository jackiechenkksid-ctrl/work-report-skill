#!/usr/bin/env python3
"""
一键安装脚本 — 将 work-report skill 安装到 Claude Code 或 Trae IDE
用法:
  python3 install.py              # 自动检测并安装到所有可用平台
  python3 install.py --claude     # 仅安装到 Claude Code
  python3 install.py --trae       # 仅安装到 Trae
  python3 install.py --all        # 安装到所有平台
"""

import os, sys, shutil, json
from pathlib import Path

SKILL_NAME = "work-report"
SKILL_DIR = Path(__file__).resolve().parent

# 各平台的 skill 目录
PLATFORMS = {
    "claude": {
        "dir": Path.home() / ".claude" / "skills" / SKILL_NAME,
        "name": "Claude Code",
        "check": Path.home() / ".claude",
    },
    "trae": {
        "dir": Path.home() / ".trae" / "skills" / SKILL_NAME,
        "name": "Trae IDE",
        "check": Path.home() / ".trae",
    },
}


def detect_platforms() -> list[str]:
    """检测安装了哪些平台"""
    available = []
    for key, cfg in PLATFORMS.items():
        if cfg["check"].exists():
            available.append(key)
    return available


def install_to(platform_key: str) -> bool:
    """安装到指定平台"""
    cfg = PLATFORMS[platform_key]
    target = cfg["dir"]

    # 如果目标已存在且是目录（非软链接），先备份
    if target.exists() and not target.is_symlink():
        backup = Path(str(target) + ".backup")
        if backup.exists():
            shutil.rmtree(backup)
        shutil.move(str(target), str(backup))
        print(f"  📦 已备份旧版本到 {backup.name}")

    # 删除旧的软链接或目录
    if target.is_symlink() or target.exists():
        target.unlink() if target.is_symlink() else shutil.rmtree(target)

    # 创建软链接（推荐，修改源文件自动生效）
    os.symlink(str(SKILL_DIR), str(target))
    print(f"  ✅ {cfg['name']}: {target} -> {SKILL_DIR}")
    return True


def main():
    # 解析参数
    args = sys.argv[1:]
    if not args:
        args = detect_platforms()
        if not args:
            print("⚠️  未检测到 Claude Code 或 Trae IDE，将同时创建配置…")
            args = list(PLATFORMS.keys())
    elif "--all" in args:
        args = list(PLATFORMS.keys())
    else:
        args = [a.replace("--", "") for a in args if a.startswith("--")]
        args = [a for a in args if a in PLATFORMS]

    print(f"\n🚀 安装 work-report skill …\n")

    success_count = 0
    for key in args:
        cfg = PLATFORMS[key]
        if cfg["check"].exists() or "--force" in sys.argv or key in args:
            try:
                if install_to(key):
                    success_count += 1
            except Exception as e:
                print(f"  ❌ {cfg['name']}: {e}")
        else:
            print(f"  ⏭️  跳过 {cfg['name']}（未检测到安装目录，用 --force 强制安装）")

    print(f"\n🎉 安装完成！{success_count}/{len(args)} 个平台已就绪。")
    print(f"\n测试方法：在对话中说「帮我写日报」即可触发。\n")


if __name__ == "__main__":
    main()
