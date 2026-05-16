# Poweramp Notes

Product research notes for Aria Core planning only. These notes do not authorize implementation.

- Local library/folder browsing: model folders, artists, albums, tracks, playlists, genres, sorting, filtering, and pagination.
- Dynamic queue: represent add/remove/move/clear, play next, replace queue, and queue history.
- Per-output settings: model profile/preference and output-route policy state.
- ReplayGain: represent loudness policy and conflicts with bit-perfect output.
- Gapless/crossfade/fade: model playback transition policies, including smart fade.
- Format support: represent provider/source/renderer capability metadata.
- CUE/radio stream support: represent metadata and stream-handle capabilities when scoped later.
- Lyrics/artwork metadata: model as source metadata fields and availability state.
- Android controls: keep notification, lock-screen, headset, widget, and MediaSession behavior as Android boundaries.
- No EQ/DSP implementation in Aria Core.
