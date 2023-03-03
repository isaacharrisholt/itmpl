# Using Custom Templates

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

## The Templating Flow

The templating flow is as follows:

1. The template directory is cloned to a temporary directory.
2. iTmpl gathers templating variables. There are three places it will gather
   from, in order of precedence:

    - The `get_variables` function in the `.itmpl.py` file.
    - The `variables` table in the `.itmpl.toml` file.
    - The default variables provided by iTmpl.

3. iTmpl renders the template files with Jinja2 using the templating variables.
   Any undefined variables will be left as is on this pass.
4. The templated directory is copied to the destination directory.
5. iTmpl runs the `post_script` function in the `.itmpl.py` file, if present.
   If this returns any variables, iTmpl will render the template files again
   with the new variables.

    - You can use this to install dependencies, or run any other post-templating
      script.
    - Note: on the second pass, Jinja2 will throw an error if the template
      contains any undefined variables.

6. Any files or directories matching `.itmpl*` are removed from the destination
   directory. `__pycache__` directories are also removed.

    - It is recommended to prefix any files or directories that you do not want
      to remain the destination directory with `.itmpl`, e.g. requirements
      files.

## The `.itmpl.py` File

The `.itmpl.py` file is used to store Python code that is used to configure the
templating process. Code in the `.itmpl.py` file is imported by iTmpl during
templating, and therefore has access to all of iTmpl's functionality and
any libraries installed in the iTmpl environment.

This includes [Typer](https://typer.tiangolo.com/), which can be used to prompt
the user for input.

You don't have to provide an `.itmpl.py` file, but if you do, it can contain
any combination of the following functions:

| Function Name   | Description                                                                                                                                                                                  |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `get_variables` | A function that returns a `Dict[str, Any]` object containing variables used in templating. You can use this to prompt the user for input, or define a computed variable.                     |
| `post_script`   | A function that runs in the final project directory, and returns a `Dict[str, Any]` of variables to use in the second rendering pass. You can use this to install requirements, for example. |

Note: you can include any combination of the above functions in the `.itmpl.py`
file.

### Function Signatures

#### `get_variables`

```python
def get_variables(
    project_name: str,  # (1)!
    destination: Path,  # (2)!
    variables: Dict[str, Any],  # (3)!
) -> Dict[str, Any]:  # (4)!
    ...
```

1. The project name, as entered by the user.
2. The destination directory.
3. iTmpl's default variables, plus any variables defined in the `.itmpl.toml`
   file.
4. The variables to use in templating. These will be combined with the
   variables passed into the function, with the Python-defined variables taking
   precedence.


#### `post_script`

```python
def post_script(
    project_name: str,  # (1)!
    final_directory: Path,  # (2)!
    variables: Dict[str, Any],  # (3)!
) -> Optional[Dict[str, Any]]:  # (4)!
    ...
```

1. The project name, as entered by the user.
2. The final project directory.
3. Any variables used in the first templating pass.
4. The variables to use in the second templating pass. If this function returns
   a falsy value (e.g. `None`, `{}`), iTmpl will not run the second pass.

## The `.itmpl.toml` File

The `.itmpl.toml` file is an optional file used to store metadata and default
variables for the template. The following is an example `.itmpl.toml` file:

```toml
[metadata]
template_description = "A template for creating a Python package with Poetry."
template_requirements = ["poetry", "pyyaml"]

[variables]
author = "Isaac Harris-Holt"
website = "https://itmpl.ihh.dev/"
```

### Metadata

The `metadata` table is used to store metadata about the template. The
following metadata fields are available:

| Field Name              | Description                                                                                                                                                                         |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `template_description`  | A description of the template. This is used in `itmpl list` to display the purpose of the template.                                                                                 |
| `template_requirements` | A list of requirements for the template. This is used in `itmpl list` to display the requirements, and `itmpl deps` to install project dependencies.                                |
 | `templating_excludes`   | A list of glob patterns to exclude from templating. This is useful if you have files that you don't want to be templated, but still want to be copied to the destination directory. |

### Variables

The `variables` table is used to store default variables for the template. The
variables are passed to Jinja2 as a `Dict[str, Any]` object. You may define
whatever variables you like, and can use this to set defaults used in your
template.

This is useful when you have a variable that doesn't often change, like the
current version of Python, so you don't need to prompt the user for it during
templating, but may want to change it in the future.