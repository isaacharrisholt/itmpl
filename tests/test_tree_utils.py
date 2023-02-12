from itmpl import tree_utils


def test_find_duplicates_in_root(tempdir):
    """Test that the find_duplicates function finds all the duplicates."""
    tempdir, source, destination = tempdir
    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.txt").touch()
    (destination / "a.txt").touch()
    (destination / "b.txt").touch()
    (destination / "d.txt").touch()

    duplicates = sorted(tree_utils.find_duplicates(source, destination))

    assert duplicates == [destination / "a.txt", destination / "b.txt"]


def test_find_duplicates_in_subdirectories(tempdir):
    """Test that the find_duplicates function finds all the duplicates."""
    tempdir, source, destination = tempdir
    (source / "subdir").mkdir()
    (destination / "subdir").mkdir()

    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.txt").touch()
    (destination / "a.txt").touch()
    (destination / "b.txt").touch()
    (destination / "d.txt").touch()

    (source / "subdir" / "a.txt").touch()
    (source / "subdir" / "b.txt").touch()
    (source / "subdir" / "c.txt").touch()
    (destination / "subdir" / "a.txt").touch()
    (destination / "subdir" / "b.txt").touch()
    (destination / "subdir" / "d.txt").touch()

    duplicates = sorted(tree_utils.find_duplicates(source, destination))

    assert duplicates == [
        destination / "a.txt",
        destination / "b.txt",
        destination / "subdir" / "a.txt",
        destination / "subdir" / "b.txt",
    ]


def test_find_duplicates_with_ignore(tempdir):
    """Test that the find_duplicates function finds all the duplicates."""
    tempdir, source, destination = tempdir
    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.txt").touch()
    (destination / "a.txt").touch()
    (destination / "b.txt").touch()
    (destination / "d.txt").touch()

    duplicates = sorted(
        tree_utils.find_duplicates(
            source,
            destination,
            ignore=lambda p: p.name == "b.txt",
        ),
    )

    assert duplicates == [destination / "a.txt"]


def test_find_duplicates_no_duplicates(tempdir):
    """Test that the find_duplicates function finds all the duplicates."""
    tempdir, source, destination = tempdir
    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.txt").touch()
    (destination / "d.txt").touch()
    (destination / "e.txt").touch()
    (destination / "f.txt").touch()

    duplicates = sorted(tree_utils.find_duplicates(source, destination))

    assert duplicates == []


def test_copy_tree_in_root(tempdir):
    """Test that the copy_tree function copies the tree correctly."""
    tempdir, source, destination = tempdir
    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.txt").touch()

    tree_utils.copy_tree(source, destination)

    assert sorted(destination.iterdir()) == [
        destination / "a.txt",
        destination / "b.txt",
        destination / "c.txt",
    ]


def test_copy_tree_in_subdirectories(tempdir):
    """Test that the copy_tree function copies the tree correctly."""
    tempdir, source, destination = tempdir
    (source / "subdir").mkdir()

    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.txt").touch()

    (source / "subdir" / "a.txt").touch()
    (source / "subdir" / "b.txt").touch()
    (source / "subdir" / "c.txt").touch()

    tree_utils.copy_tree(source, destination)

    assert sorted(destination.iterdir()) == [
        destination / "a.txt",
        destination / "b.txt",
        destination / "c.txt",
        destination / "subdir",
    ]
    assert sorted((destination / "subdir").iterdir()) == [
        destination / "subdir" / "a.txt",
        destination / "subdir" / "b.txt",
        destination / "subdir" / "c.txt",
    ]


def test_copy_tree_with_ignore(tempdir):
    """Test that the copy_tree function copies the tree correctly."""
    tempdir, source, destination = tempdir
    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.txt").touch()

    tree_utils.copy_tree(source, destination, ignore=lambda p: p.name == "b.txt")

    assert sorted(destination.iterdir()) == [
        destination / "a.txt",
        destination / "c.txt",
    ]


def test_copy_tree_with_duplicates(tempdir):
    """Test that the copy_tree function copies the tree correctly."""
    tempdir, source, destination = tempdir
    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.txt").touch()

    (destination / "a.txt").touch()
    (destination / "b.txt").touch()

    tree_utils.copy_tree(source, destination)

    assert sorted(destination.iterdir()) == [
        destination / "a.txt",
        destination / "b.txt",
        destination / "c.txt",
    ]


def test_copy_tree_no_overwrite(tempdir):
    """Test that the copy_tree function doesn't overwrite existing files."""
    tempdir, source, destination = tempdir
    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.txt").touch()

    (destination / "d.txt").touch()
    (destination / "e.txt").touch()

    tree_utils.copy_tree(source, destination)

    assert sorted(destination.iterdir()) == [
        destination / "a.txt",
        destination / "b.txt",
        destination / "c.txt",
        destination / "d.txt",
        destination / "e.txt",
    ]


def test_recursive_delete_in_root(tempdir):
    """Test that the recursive_delete function deletes the tree correctly."""
    tempdir, source, destination = tempdir
    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.json").touch()

    tree_utils.recursive_delete(source, "*.txt")

    assert sorted(source.iterdir()) == [source / "c.json"]


def test_recursive_delete_in_subdirectories(tempdir):
    """Test that the recursive_delete function deletes the tree correctly."""
    tempdir, source, destination = tempdir
    (source / "subdir").mkdir()

    (source / "a.txt").touch()
    (source / "b.txt").touch()
    (source / "c.json").touch()

    (source / "subdir" / "a.txt").touch()
    (source / "subdir" / "b.txt").touch()
    (source / "subdir" / "c.json").touch()

    tree_utils.recursive_delete(source, "*.txt")

    assert sorted(source.iterdir()) == [source / "c.json", source / "subdir"]
    assert sorted((source / "subdir").iterdir()) == [source / "subdir" / "c.json"]
