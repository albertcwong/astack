"""Exercise the helper with fake tools, without downloading or accessing cookies."""

import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/yt-dlp/scripts/download"
URL = "https://example.com/watch?v=1&list=PL"


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.dest = self.root / "saved media"
        self.log = self.root / "arguments"
        self.env = dict(os.environ, PATH=str(self.bin), YTDLP_TEST_ARGS=str(self.log))

    def run_download(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--path", str(self.dest), *args],
            env=self.env, cwd=self.root, capture_output=True, text=True, check=False,
        )

    def preview(self, *args):
        result = self.run_download("--print", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.dest.exists())
        return shlex.split(result.stdout)

    def tools(self):
        for name, body in (
            ("yt-dlp", 'printf \'%s\\n\' "$@" > "$YTDLP_TEST_ARGS"\nexit "${YTDLP_TEST_EXIT:-0}"\n'),
            ("ffmpeg", "exit 0\n"),
        ):
            tool = self.bin / name
            tool.write_text("#!/bin/sh\n" + body)
            tool.chmod(0o700)

    def test_preview_needs_no_tools_and_defaults_to_one_video(self):
        command = self.preview(URL)
        self.assertIn("--ignore-config", command)
        self.assertIn("--no-playlist", command)
        self.assertEqual(command[command.index("-I") + 1], "1")
        self.assertNotIn("--cookies-from-browser", command)
        self.assertEqual(command[-2:], ["--", URL])
        self.assertIn("after_move:filepath", command)

    def test_cookie_access_is_explicit_even_for_youtube(self):
        url = "https://www.youtube.com/watch?v=abc"
        self.assertNotIn("--cookies-from-browser", self.preview(url))
        command = self.preview(url, "--browser", "firefox")
        self.assertEqual(command[command.index("--cookies-from-browser") + 1], "firefox")

    def test_quality_audio_subtitles_and_format_precedence(self):
        command = self.preview(URL, "--quality", "720", "--audio", "--subs", "--ipv4")
        self.assertIn("bestvideo[height<=720]+bestaudio/best[height<=720]", command)
        for value in ("-x", "mp3", "--write-subs", "all", "-4"):
            self.assertIn(value, command)
        command = self.preview("--quality", "720", "--format", "18", URL)
        self.assertEqual(command[command.index("-f") + 1], "18")

    def test_playlist_requires_explicit_scope(self):
        for flags in (("--playlist",), ("--items", "1:5")):
            with self.subTest(flags=flags):
                command = self.preview(URL, *flags)
                self.assertIn("--yes-playlist", command)
                self.assertNotIn("--no-playlist", command)
                self.assertIn("%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s", command)

    def test_list_runs_without_ffmpeg_or_creating_output(self):
        self.tools()
        (self.bin / "ffmpeg").unlink()
        result = self.run_download(URL, "--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-F", self.log.read_text().splitlines())
        self.assertFalse(self.dest.exists())

    def test_invalid_arguments_fail_before_tools_or_writes(self):
        for args in ((), ("--exec=touch bad",), ("file:///etc/passwd",),
                     (URL, URL), (URL, "--quality", "0"), (URL, "--quality", "best"),
                     (URL, "--browser", "unknown"), (URL, "--quality")):
            with self.subTest(args=args):
                result = self.run_download(*args)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(self.dest.exists())

    def test_missing_dependencies_fail_before_download(self):
        result = self.run_download(URL)
        self.assertEqual(result.returncode, 1)
        self.assertIn("yt-dlp", result.stderr)
        self.tools()
        (self.bin / "ffmpeg").unlink()
        for flags in ((), ("--audio", "--format", "18"), ("--format", "137+140")):
            result = self.run_download(URL, *flags)
            self.assertEqual(result.returncode, 1)
            self.assertIn("ffmpeg", result.stderr)
            self.assertFalse(self.log.exists())

    def test_execution_preserves_literal_arguments_and_failure_status(self):
        self.tools()
        self.dest = self.root / 'media $(touch injected) `touch injected`'
        url = 'https://example.com/v?x=$(touch injected)&y="quoted"'
        result = self.run_download(url, "--format", "18")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.dest.is_dir())
        arguments = self.log.read_text().splitlines()
        self.assertEqual(arguments[-2:], ["--", url])
        self.assertEqual(arguments[arguments.index("-P") + 1], str(self.dest.resolve()))
        self.assertFalse((self.root / "injected").exists())
        self.env["YTDLP_TEST_EXIT"] = "7"
        self.assertEqual(self.run_download(URL).returncode, 7)


if __name__ == "__main__":
    unittest.main()
