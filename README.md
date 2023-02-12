![iTmpl Logo](https://isaacharrisholt.github.io/itmpl/static/images/itmpl-logo.png)

<p align="center">
    <em>iTmpl. A flexible, powerful project templating tool, written in Python.</em>
</p>

---

**Documentation:** <https://itmpl.ihh.dev>

**Source:** <https://github.com/isaacharrisholt/itmpl>

---

iTmpl is a project templating tool that allows you to create and manage project
templates. iTmpl is written in Python and is cross-platform.

It comes with some default templates, but you can also create your own. iTmpl
also allows you to run arbitrary Python code before and after the templating
process, allowing you to do things like create a git repository, or install
dependencies.

## Installation

Although iTmpl has a well-documented API, its primary aim it to be a command
line tool. As such, the recommended installation method is via
[`pipx`](https://pypa.github.io/pipx/):

```bash
pipx install itmpl
```

However, you can also install iTmpl via `pip`, if you prefer:

```bash
pip install itmpl
```

## Quick Start

To see available project templates, run:

```bash
itmpl list
```

To create a new project from a template, run:

```bash
itmpl new <template> <project-name> [options]
```

For example, to create a new Poetry project, run:

```bash
itmpl new poetry-project my-new-project
```

## Adding Custom Templates

Custom templates are stored in an `extra_templates_dir` specified in the iTmpl
configuration file. To find the default location for your machine, run:

```bash
itmpl config show extra_templates_dir
```

To change the location of the `extra_templates_dir`, run:

```bash
itmpl config set extra_templates_dir <path>
```

To create a new template, simple create a new directory in the
`extra_templates_dir`. iTmpl will automatically detect the new template, and
show it in the list of available templates.

Templates can be configured through `.itmpl.toml` and `.itmpl.py` files. See
the
[documentation](https://itmpl.ihh.dev/using_custom_templates)
for more details.

## Contributing

Contributions are welcome! If you find a bug, or have a feature request, please
open a new issue. If you would like to contribute code, please open a new pull
request.

I'm always open to new templates too! I don't know every possible use case for
this tool, so I've only included a few templates that I thought would be useful
to me. If you have a template that you think would be useful to others, please
open a new issue, or submit a pull request!