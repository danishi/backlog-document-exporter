import argparse
import json
import os
from typing import Any, Dict, List

from .client import BacklogClient


def to_markdown_table(items: List[Dict[str, Any]], headers: List[str]) -> str:
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for item in items:
        row = [str(item.get(h, "")) for h in headers]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def print_document_list(client: BacklogClient) -> None:
    project_id = client.get_project_id()
    docs = client.get_document_list(project_id)
    for doc in docs:
        doc["url"] = (
            f"https://{client.space_domain}/document/"
            f"{client.project_key}/{doc['id']}"
        )
    md = to_markdown_table(docs, ["id", "title", "url"])
    print(md)


def print_document_tree(client: BacklogClient) -> None:
    project_id = client.get_project_id()
    tree = client.get_document_tree(project_id)

    def walk(nodes: List[Dict[str, Any]], indent: int = 0) -> List[str]:
        lines = []
        for node in nodes:
            prefix = "  " * indent + "- " + node.get("name", "")
            lines.append(prefix)
            children = node.get("children", [])
            lines.extend(walk(children, indent + 1))
        return lines

    nodes = tree.get("activeTree", {}).get("children", [])
    for line in walk(nodes):
        print(line)


def _dict_to_markdown(info: Dict[str, Any]) -> str:
    lines = []
    for key, value in info.items():
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, ensure_ascii=False)
        else:
            value_str = str(value)
        lines.append(f"- **{key}**: {value_str}")
    return "\n".join(lines)


def print_document_info(client: BacklogClient, document_id: str) -> None:
    info = client.get_document_info(document_id)
    print(_dict_to_markdown(info))


def download_attachments(
    client: BacklogClient, document_id: str, output_dir: str
) -> None:
    os.makedirs(output_dir, exist_ok=True)
    attachments = client.get_document_attachments(document_id)
    for att in attachments:
        path = client.download_attachment(document_id, att["id"], output_dir)
        print(f"Downloaded {att['name']} -> {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backlog Document Exporter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List documents")
    subparsers.add_parser("tree", help="Show document tree")

    info = subparsers.add_parser("info", help="Show document info")
    info.add_argument("document_id")

    dl = subparsers.add_parser(
        "download", help="Download document attachments"
    )
    dl.add_argument("document_id")
    dl.add_argument("output", help="Output directory")

    args = parser.parse_args()

    client = BacklogClient.from_env()

    if args.command == "list":
        print_document_list(client)
    elif args.command == "tree":
        print_document_tree(client)
    elif args.command == "info":
        print_document_info(client, args.document_id)
    elif args.command == "download":
        download_attachments(client, args.document_id, args.output)


if __name__ == "__main__":
    main()
