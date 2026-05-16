# Poweramp Notes

Product research notes for Aria Core planning only. These notes do not authorize implementation.

Trademark/reference notice: third-party product and company names are used only as factual research references. Noqlen is not affiliated with, endorsed by, sponsored by, or associated with those products or companies. Do not copy logos, screenshots, icons, UI assets, branding, or long text from third-party products.

Use generic Aria domain names such as `MediaProviderRegistry`, `SmartPlaylist`, `MultipleQueue`, `OutputProfile`, and `BitPerfectCapability`. Do not create brand-based class or feature names.

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
