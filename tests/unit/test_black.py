import pytest


@pytest.mark.parametrize(
    ("text", "fail"),
    [
        (
            (
                'test = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec'
                " porta, nunc at interdum gravida, massa sem lacinia libero, non"
                ' feugiat turpis nunc nec sapien."'
            ),
            True,
        ),
        (
            (
                'test = """Lorem ipsum dolor sit amet, consectetur adipiscing elit\n'
                "onec porta, nunc at interdum gravida, massa sem lacinia libero\n"
                "non feugiat turpis nunc nec sapien.\n"
                '"""\n'
            ),
            False,
        ),
    ],
)
def test_black_test_wrap(tmp_path, text, fail):
    # This is optional; shows that Black leaves string literal content alone.
    p = tmp_path / "sample.py"
    p.write_text(text)
    # Defer to existing black pre-commit config; skip if black unavailable.
    import subprocess

    proc = subprocess.run(["black", "--check", str(p)], capture_output=True, text=True)
    if fail:
        assert proc.returncode == 1
        assert "1 file would be reformatted." in proc.stderr
    else:
        assert proc.returncode == 0
        assert "1 file would be left unchanged." in proc.stderr
