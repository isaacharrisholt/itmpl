from pathlib import Path

import pytest

from itmpl import utils


def test_import_external_module():
    """Test that the import_external_module function works as expected."""
    module = utils.import_external_module(
        Path(__file__).parent / "files" / "test_module.py",
    )

    assert module is not None
    assert module.hello("world") == "Hello world!"


def test_import_external_module_nonexistent_module():
    """Test that the import_external_module function raises an error when the module
    does not exist."""
    with pytest.raises(ValueError):
        utils.import_external_module(
            Path(__file__).parent / "files" / "nonexistent_module.py",
        )


def test_construct_table_from_templates():
    """Test that the construct_table_from_templates function works as expected."""
    templates = [
        (Path("template1"), "Template 1 description"),
        (Path("template2"), "Template 2 description"),
    ]

    table = utils.construct_table_from_templates(templates)

    assert table is not None
    assert table.row_count == 2
