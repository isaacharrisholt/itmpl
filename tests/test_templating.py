import shutil
from pathlib import Path

import pytest

from itmpl import global_vars, templating, tree_utils
from itmpl.metadata import ItmplMetadata, ItmplToml


def test_get_templates_in_dir(template_dirs):
    """Test that the get_templates_in_dir function works as expected."""
    source, _ = template_dirs
    templates = templating.get_templates_in_dir(source)

    assert templates == {
        "test-template-complete": (
            source / "test-template-complete",
            ItmplToml(
                metadata=ItmplMetadata(
                    template_description="Test template complete",
                    template_requirements=[],
                    templating_excludes=[],
                ),
                variables={"a": 1, "b": 2},
            ),
        ),
        "test-template-empty-files": (
            source / "test-template-empty-files",
            ItmplToml(
                metadata=ItmplMetadata(
                    template_description=None,
                    template_requirements=[],
                    templating_excludes=[],
                ),
                variables={},
            ),
        ),
        "test-template-no-files": (
            source / "test-template-no-files",
            ItmplToml(
                metadata=ItmplMetadata(
                    template_description=None,
                    template_requirements=[],
                    templating_excludes=[],
                ),
                variables={},
            ),
        ),
        "test-template-exceptions": (
            source / "test-template-exceptions",
            ItmplToml(
                metadata=ItmplMetadata(
                    template_description=None,
                    template_requirements=[],
                    templating_excludes=[],
                ),
                variables={},
            ),
        ),
    }


def test_get_templates_in_dir_empty_dir(template_dirs):
    """Test that the get_templates_in_dir function works in an empty directory."""
    _, destination = template_dirs
    templates = templating.get_templates_in_dir(destination)

    assert templates == {}


def test_get_template_options_no_duplicates(
    monkeypatch,
    mock_config_file,
    template_dirs,
):
    """Test that the get_template_options function reads both directories."""
    source, _ = template_dirs
    temp_template_dir = Path("/tmp/templates")
    (temp_template_dir / "test-template-temp").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(global_vars, "TEMPLATES_DIR", source)

    templates = templating.get_template_options()

    assert templates == {
        "test-template-complete": (
            source / "test-template-complete",
            ItmplToml(
                metadata=ItmplMetadata(
                    template_description="Test template complete",
                    template_requirements=[],
                    templating_excludes=[],
                ),
                variables={"a": 1, "b": 2},
            ),
        ),
        "test-template-empty-files": (
            source / "test-template-empty-files",
            ItmplToml(
                metadata=ItmplMetadata(
                    template_description=None,
                    template_requirements=[],
                    templating_excludes=[],
                ),
                variables={},
            ),
        ),
        "test-template-no-files": (
            source / "test-template-no-files",
            ItmplToml(
                metadata=ItmplMetadata(
                    template_description=None,
                    template_requirements=[],
                    templating_excludes=[],
                ),
                variables={},
            ),
        ),
        "test-template-exceptions": (
            source / "test-template-exceptions",
            ItmplToml(
                metadata=ItmplMetadata(
                    template_description=None,
                    template_requirements=[],
                    templating_excludes=[],
                ),
                variables={},
            ),
        ),
        "test-template-temp": (
            temp_template_dir / "test-template-temp",
            ItmplToml(
                metadata=ItmplMetadata(
                    template_description=None,
                    template_requirements=[],
                    templating_excludes=[],
                ),
                variables={},
            ),
        ),
    }

    shutil.rmtree(temp_template_dir)


def test_get_template_options_with_duplicates(
    monkeypatch,
    mock_config_file,
    template_dirs,
):
    """Test that the get_template_options function raises an error when there are
    duplicate templates."""
    source, _ = template_dirs
    temp_template_dir = Path("/tmp/templates")
    (temp_template_dir / "test-template-complete").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(global_vars, "TEMPLATES_DIR", source)

    with pytest.raises(templating.DuplicateTemplateError):
        templating.get_template_options()

    shutil.rmtree(temp_template_dir)


def test_get_default_variables():
    """Test that the get_default_variables function works as expected."""
    variables = templating.get_default_variables(project_name="test-project")

    assert variables == {
        "project_name": "test-project",
        "project_title": "Test Project",
    }


def test_get_toml_variables(template_dirs):
    """Test that the get_toml_variables function works as expected."""
    source, _ = template_dirs
    variables = templating.get_toml_variables(source / "test-template-complete")

    assert variables == {
        "a": 1,
        "b": 2,
    }


def test_get_toml_variables_no_variables(template_dirs):
    """Test that the get_toml_variables function works when there is no TOML file."""
    source, _ = template_dirs
    variables = templating.get_toml_variables(source / "test-template-empty-files")

    assert variables == {}


def test_get_toml_variables_no_toml_file(template_dirs):
    """Test that the get_toml_variables function works when there is no TOML file."""
    source, _ = template_dirs
    variables = templating.get_toml_variables(source / "test-template-no-files")

    assert variables == {}


def test_get_python_variables(template_dirs):
    """Test that the get_python_variables function works as expected."""
    source, destination = template_dirs
    variables = templating.get_python_variables(
        source / "test-template-complete",
        "project-name",
        destination,
        {"c": 3},
    )

    assert variables == {
        "a": 1,
        "b": 2,
        "c": 3,
        "project_name": "project-name",
        "destination": destination,
    }


def test_get_python_variables_no_get_variables_function(template_dirs):
    """Test that the get_python_variables function works when there is no
    get_variables function."""
    source, destination = template_dirs
    variables = templating.get_python_variables(
        source / "test-template-empty-files",
        "project-name",
        destination,
        {"c": 3},
    )

    assert variables == {}


def test_get_python_variables_no_python_file(template_dirs):
    """Test that the get_python_variables function works when there is no Python
    file."""
    source, destination = template_dirs
    variables = templating.get_python_variables(
        source / "test-template-no-files",
        "project-name",
        destination,
        {"c": 3},
    )

    assert variables == {}


def test_get_python_variables_exception(template_dirs):
    """Test that the get_python_variables function raises an error when the
    get_variables function raises an error."""
    source, destination = template_dirs
    with pytest.raises(templating.TemplatingException):
        templating.get_python_variables(
            source / "test-template-exceptions",
            "project-name",
            destination,
            {"c": 3},
        )


def test_template_directory_files_in_root(template_dirs):
    """Test the template_directory function successfully templates files in the roof of
    the directory."""
    source, destination = template_dirs

    tree_utils.copy_tree(source / "test-template-complete", destination)
    templating.template_directory(
        destination,
        {
            **templating.get_default_variables("test-project"),
            "project_description": "Test project description",
        },
    )

    template_file_path = destination / "{{ project_name }}.txt"
    test_file_path = destination / "test-project.txt"
    assert not template_file_path.exists()
    assert test_file_path.exists()
    assert test_file_path.is_file()
    assert test_file_path.read_text() == "Test Project\n\nTest project description\n"


def test_template_directory_directory_names(template_dirs):
    """Test the template_directory function successfully templates directory names."""
    source, destination = template_dirs

    tree_utils.copy_tree(source / "test-template-complete", destination)
    templating.template_directory(
        destination,
        {
            **templating.get_default_variables("test-project"),
            "project_description": "Test project description",
        },
    )

    template_directory_path = destination / "{{ project_title }}"
    test_directory_path = destination / "Test Project"
    assert not template_directory_path.exists()
    assert test_directory_path.exists()
    assert test_directory_path.is_dir()
    assert (test_directory_path / "test.txt").exists()


def test_template_directory_files_in_subdirectories(template_dirs):
    """Test the template_directory function successfully templates files in
    subdirectories."""
    source, destination = template_dirs

    tree_utils.copy_tree(source / "test-template-complete", destination)
    templating.template_directory(
        destination,
        {
            **templating.get_default_variables("test-project"),
            "project_description": "Test project description",
        },
    )
    template_json_file_path = (
        destination / "{{ project_title }}" / "{{ project_description }}.json"
    )
    test_json_file_path = destination / "Test Project" / "Test project description.json"
    assert not template_json_file_path.exists()
    assert test_json_file_path.exists()
    assert test_json_file_path.is_file()


def test_template_directory_ignores_itmpl_files(template_dirs):
    """Test the template_directory function ignores files starting with .itmpl."""
    source, destination = template_dirs

    tree_utils.copy_tree(source / "test-template-complete", destination)
    templating.template_directory(
        destination,
        {
            **templating.get_default_variables("test-project"),
            "project_description": "Test project description",
        },
    )

    itmpl_metadata_path = destination / ".itmpl.py"
    assert itmpl_metadata_path.exists()
    assert "{{ project_name }}" in itmpl_metadata_path.read_text()


def test_template_directory_with_exclude_glob(template_dirs):
    """Test the template_directory function successfully excludes files matching the
    exclude glob."""
    source, destination = template_dirs

    tree_utils.copy_tree(source / "test-template-complete", destination)
    templating.template_directory(
        destination,
        {
            **templating.get_default_variables("test-project"),
            "project_description": "Test project description",
        },
        exclude=["*.txt"],
    )

    template_file_path = destination / "{{ project_name }}.txt"
    test_file_path = destination / "test-project.txt"
    assert template_file_path.exists()
    assert not test_file_path.exists()
