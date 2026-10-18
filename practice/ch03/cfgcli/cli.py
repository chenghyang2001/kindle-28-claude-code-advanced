"""cfgcli 指令列入口：set / get / list / export。"""
import argparse
import json
import sys
from pathlib import Path

from cfgcli.store import load_config, save_config


def cmd_set(args) -> int:
    config = load_config()
    config[args.key] = args.value
    save_config(config)
    print(f"已設定 {args.key} = {args.value}")
    return 0


def cmd_get(args) -> int:
    config = load_config()
    if args.key not in config:
        print(f"錯誤：找不到設定 {args.key}", file=sys.stderr)
        return 1
    print(config[args.key])
    return 0


def cmd_list(args) -> int:
    for key, value in sorted(load_config().items()):
        print(f"{key}={value}")
    return 0


def to_json(config: dict) -> str:
    """設定轉 JSON 字串；sort_keys 讓輸出穩定可 diff，ensure_ascii=False 保留中文原文。"""
    return json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True)


def cmd_export(args) -> int:
    text = to_json(load_config())
    if args.output is None:
        print(text)
        return 0
    try:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    except OSError as e:
        print(f"錯誤：無法寫入 {args.output}（{e}）", file=sys.stderr)
        return 1
    print(f"已匯出到 {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cfgcli", description="簡易設定管理工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p_set = sub.add_parser("set", help="設定一個值")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.set_defaults(func=cmd_set)

    p_get = sub.add_parser("get", help="讀取一個值")
    p_get.add_argument("key")
    p_get.set_defaults(func=cmd_get)

    p_list = sub.add_parser("list", help="列出全部設定")
    p_list.set_defaults(func=cmd_list)

    p_export = sub.add_parser("export", help="把目前設定輸出成 JSON")
    p_export.add_argument("-o", "--output", help="輸出檔案路徑；省略時印到 stdout")
    p_export.set_defaults(func=cmd_export)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ValueError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
