# Backlog Document Exporter

Backlog Document Exporter is a small command line tool for exporting documents from Backlog. The program uses the Backlog Document API (beta) and prints information in Markdown format.

## Configuration

Create a `.env` file based on `.env.example` and set the following values:

```
BACKLOG_SPACE_DOMAIN=your-space.backlog.com
BACKLOG_API_KEY=your-api-key
BACKLOG_PROJECT_KEY=PROJECTKEY
BACKLOG_SSL_VERIFY=true
```

Set `BACKLOG_SSL_VERIFY` to `false` if you need to skip TLS certificate verification.

## Setup

Install dependencies into a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```
python3 -m backlog_document_exporter.cli list
python3 -m backlog_document_exporter.cli tree
python3 -m backlog_document_exporter.cli info <document_id>
python3 -m backlog_document_exporter.cli download <document_id> [output_dir]
```

If `output_dir` is omitted, files are saved to the current directory.

The `list` command automatically fetches all pages using the required `offset` parameter. Each row in its output also contains a `url` column in the following format:

```
https://BACKLOG_SPACE_DOMAIN/document/BACKLOG_PROJECT_KEY/<document_id>
```

`<document_id>` is the identifier shown in the list or tree output. All command output other than downloaded files is printed in Markdown.

## Reference

- [Backlog Document API update information](https://backlog.com/ja/blog/backlog-update-document-202506/#API%E3%82%92%E6%8B%A1%E5%85%85%E3%81%97%E3%81%BE%E3%81%97%E3%81%9F)

