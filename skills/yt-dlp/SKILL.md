---
name: yt-dlp
description: Download videos or playlists, extract MP3 audio, save subtitles, or select video quality with yt-dlp when the user asks to save media from a URL. Also use for troubleshooting yt-dlp downloads.
---

# yt-dlp

Adapted from MapleShaw's [yt-dlp-downloader-skill](https://github.com/MapleShaw/yt-dlp-downloader-skill)
(MIT, as declared in its README).

Turn a media URL and the user's preferences into a download. Use the host
agent's shell tool; this skill works in Claude Code, Codex, pi, and Cursor.

## Download

Use `scripts/download` from this skill's directory, resolved to an absolute
path. Run it with `python3`; no Python packages are needed for the helper.

Do not ask about quality, subtitles, or destination when the user simply asks
to download a video. Default to best available quality, one video, and
`~/Downloads/yt-dlp`. Honor any preferences already given. Use `--playlist`
only when the user requests a playlist, and `--items` for a requested subset.
`--no-playlist` prevents a watch URL's playlist parameter from expanding scope.
The helper also limits unrequested collections to their first item, since
`--no-playlist` alone does not limit a URL that identifies only a playlist.

```bash
python3 /absolute/path/to/yt-dlp/scripts/download 'VIDEO_URL'
python3 /absolute/path/to/yt-dlp/scripts/download --audio 'VIDEO_URL'
python3 /absolute/path/to/yt-dlp/scripts/download --subs --quality 720 'VIDEO_URL'
python3 /absolute/path/to/yt-dlp/scripts/download --path '/path/to/save' 'VIDEO_URL'
python3 /absolute/path/to/yt-dlp/scripts/download --playlist --items '1:5' 'PLAYLIST_URL'
python3 /absolute/path/to/yt-dlp/scripts/download --list 'VIDEO_URL'
python3 /absolute/path/to/yt-dlp/scripts/download --format 'FORMAT_ID' 'VIDEO_URL'
```

The helper accepts flags before or after the URL. `--format` takes precedence
over `--quality`. `--audio` extracts MP3; `--subs` saves available uploaded
subtitles in all languages. Automatic captions and thumbnail downloads can be
requested directly with yt-dlp's `--write-auto-subs` and `--write-thumbnail`.
Use the [official options reference](https://github.com/yt-dlp/yt-dlp#usage-and-options)
for needs outside the helper. Preserve the requested destination and scope.

The helper ignores saved yt-dlp configuration so its options determine the
operation. `--print` previews the shell-quoted command without dependencies,
network access, or directory creation. It is a preview, not a completed download.

## Dependencies and authentication

The helper checks for `yt-dlp`, plus `ffmpeg` for audio extraction and format
merging. If missing, use the user's package manager and environment conventions.
Typical commands are `pip install yt-dlp` (or `pipx install yt-dlp`) and
`brew install ffmpeg` on macOS or `sudo apt install ffmpeg` on Debian/Ubuntu.
Follow the host's installation and permission rules.

Start without browser cookies. When authentication is needed or the user has
chosen a browser, pass `--browser chrome` (or firefox, safari, edge, brave,
opera, chromium, vivaldi, whale). This adds `--cookies-from-browser chrome`
for Chrome. Use the browser the user chose; do not silently access another
profile or export cookies into the repository. Cookies do not guarantee that
a YouTube 403 will be resolved.

## Recover and report

- Interrupted transfer: retry the same command and destination to let yt-dlp
  resume partial files. Keep retries bounded; report persistent errors.
- Unavailable format: use `--list`, then pick an available format consistent
  with the request. Explain if the requested quality is unavailable.
- Authentication or 403 error: inspect the error, installed version, and
  yt-dlp's current guidance before retrying with the selected browser.
- Connection problems: `--ipv4` forces IPv4 when appropriate.
- Extractor failures: update yt-dlp through its existing installation method
  when permitted. Do not repeatedly retry private or unavailable media.

Check the exit status and output. Successful downloads print final file paths;
verify those files exist before reporting completion. Give the saved paths and
any failed playlist items. A directory or a successful command preview alone
does not prove a download succeeded.
