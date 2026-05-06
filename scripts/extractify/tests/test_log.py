from __future__ import annotations

import sys

from lib.log import log_info


def test_verbose_off_emits_nothing(capsys):
    log_info("ignored", verbose=False)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_verbose_on_emits_to_stderr(capsys):
    log_info("hello", verbose=True)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "INFO: hello\n"
