"""gen_ref_pages automatically generates pages for the {{ project_title }} API
reference."""
from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()  # type: ignore

for path in sorted(Path("{{ project_name }}").rglob("*.py")):
    module_path = path.relative_to("{{ project_name }}").with_suffix("")
    doc_path = path.relative_to("{{ project_name }}").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(["{{ project_name }}"] + list(module_path.parts))

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
