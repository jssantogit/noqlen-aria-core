import pytest

from noqlen_aria.cli import main


def test_help(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "Noqlen Aria Core development adapter" in output
    assert "doctor" in output


def test_doctor(capsys):
    assert main(["doctor"]) == 0
    output = capsys.readouterr().out
    assert "Noqlen Aria Core doctor" in output
    assert "anchor: not configured in Bloco 0" in output
    assert "navidrome: not accessed" in output
    assert "music-library: not accessed" in output
