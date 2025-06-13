import argparse
import json
import os
from typing import Any, Dict, List

from tqdm import tqdm

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
            children = node.get("children", [])
            prefix = "  " * indent + "- " + node.get("name", "")
            if not children and "id" in node:
                url = (
                    f"https://{client.space_domain}/document/"
                    f"{client.project_key}/{node['id']}"
                )
                prefix += f" - {url}"
            lines.append(prefix)
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
    client: BacklogClient, document_id: str, output_dir: str = "."
) -> None:
    os.makedirs(output_dir, exist_ok=True)
    attachments = client.get_document_attachments(document_id)
    for att in attachments:
        path = client.download_attachment(
            document_id,
            att["id"],
            output_dir,
            filename=att.get("name"),
        )
        print(f"Downloaded {att['name']} -> {path}")


def safe_name(name: str) -> str:
    """Return a filesystem-safe name."""
    return "".join("_" if c in "\\/" else c for c in name)


def export_all_documents(client: BacklogClient, output_dir: str = ".") -> None:
    print("Fetching document tree...")
    project_id = client.get_project_id()
    tree = client.get_document_tree(project_id)

    nodes = tree.get("activeTree", {}).get("children", [])
    docs: List[tuple[str, List[str]]] = []

    def gather(nodes: List[Dict[str, Any]], path: List[str]) -> None:
        for node in nodes:
            name = safe_name(node.get("name", ""))
            children = node.get("children", [])
            new_path = path + [name]
            if "id" in node:
                docs.append((str(node["id"]), new_path))
            if children:
                gather(children, new_path)

    gather(nodes, [])

    print(f"Creating directory tree at {output_dir}...")
    for _, parts in docs:
        os.makedirs(os.path.join(output_dir, *parts), exist_ok=True)

    print("Downloading documents...")
    for doc_id, parts in tqdm(docs, desc="Documents", unit="doc"):
        dir_path = os.path.join(output_dir, *parts)
        info = client.get_document_info(doc_id)
        content = info.get("content") or info.get("text") or ""
        with open(os.path.join(dir_path, "document.md"), "w", encoding="utf-8") as f:
            f.write(_dict_to_markdown(info))
            f.write("\n\n")
            f.write(content)
        download_attachments(client, doc_id, dir_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Backlog Document Exporter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List documents")
    subparsers.add_parser("tree", help="Show document tree")

    info = subparsers.add_parser("info", help="Show document info")
    info.add_argument("document_id")

    dl = subparsers.add_parser("download", help="Download document attachments")
    dl.add_argument("document_id")
    dl.add_argument(
        "output",
        nargs="?",
        default=".",
        help="Output directory (default: current directory)",
    )

    export_all = subparsers.add_parser(
        "export", help="Export all documents and attachments"
    )
    export_all.add_argument(
        "output",
        nargs="?",
        default=".",
        help="Output directory (default: current directory)",
    )

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
    elif args.command == "export":
        export_all_documents(client, args.output)


if __name__ == "__main__":
    main()
