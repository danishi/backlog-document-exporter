# Backlog Document Exporter

Command line utility to export Backlog documents. Configuration is loaded
from a `.env` file. Copy `.env.example` and set the following values:

```
BACKLOG_SPACE_DOMAIN=your-space.backlog.com
BACKLOG_API_KEY=your-api-key
BACKLOG_PROJECT_KEY=PROJECTKEY
BACKLOG_SSL_VERIFY=true
```

Set `BACKLOG_SSL_VERIFY` to `false` to disable TLS certificate verification.

## Setup

Create a virtual environment in `.venv` and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Activate the environment before using the commands below.

## Usage

```
python3 -m backlog_document_exporter.cli list
python3 -m backlog_document_exporter.cli tree
python3 -m backlog_document_exporter.cli info <document_id>
python3 -m backlog_document_exporter.cli download <document_id> <output_dir>
```

The ``list`` command automatically fetches all pages of results using the
required ``offset`` parameter of the Backlog API.

Each row in the ``list`` output also contains a ``url`` column pointing to the
document in Backlog using the following format:

```
https://BACKLOG_SPACE_DOMAIN/document/BACKLOG_PROJECT_KEY/<document_id>
```

`<document_id>` is the identifier shown in the list or tree output.

All output except for downloaded files is printed in Markdown format.
