"""gen_ref_pages automatically generates pages for the Itmpl API
reference."""
from pathlib import Path

import mkdocs_gen_files

IGNORE_PATHS = list((Path(__file__).parent.parent / "itmpl" / "templates").rglob("*"))
nav = mkdocs_gen_files.Nav()


for path in sorted(Path("itmpl").rglob("*.py")):
    if path.resolve() in IGNORE_PATHS:
        continue

    module_path = path.relative_to("itmpl").with_suffix("")
    doc_path = path.relative_to("itmpl").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(["itmpl"] + list(module_path.parts))

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        if not parts:
            continue

        nav[parts] = doc_path.as_posix()

        identifier = ".".join(parts)
        print("::: " + identifier, file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
