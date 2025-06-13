# Backlog Document Exporter

Command line utility to export Backlog documents. Configuration is loaded
from a `.env` file. Copy `.env.example` and set the following values:

```
BACKLOG_SPACE_DOMAIN=your-space.backlog.com
BACKLOG_API_KEY=your-api-key
BACKLOG_PROJECT_KEY=PROJECTKEY
```

## Usage

```
python -m backlog_document_exporter.cli list
python -m backlog_document_exporter.cli tree
python -m backlog_document_exporter.cli info <document_id>
python -m backlog_document_exporter.cli download <document_id> <output_dir>
```

`<document_id>` is the identifier shown in the list or tree output.

All output except for downloaded files is printed in Markdown format.
