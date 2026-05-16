# Symfonium Notes

Product research notes for Aria Core planning only. These notes do not authorize implementation.

Trademark/reference notice: third-party product and company names are used only as factual research references. Noqlen is not affiliated with, endorsed by, sponsored by, or associated with those products or companies. Do not copy logos, screenshots, icons, UI assets, branding, or long text from third-party products.

Use generic Aria domain names such as `MediaProviderRegistry`, `SmartPlaylist`, `MultipleQueue`, `OutputProfile`, and `BitPerfectCapability`. Do not create brand-based class or feature names.

- Provider registry: model provider identity, accounts, connection state, and auth state.
- Provider capability matrix: normalize provider differences through explicit capabilities.
- Sync manager: track sync all, sync provider, full/incremental sync, summaries, counts, and safe errors.
- Offline/cache/download types: distinguish offline rules, download queue, playback cache, permanent cache, rolling cache, and provider offline cache.
- Multiple queues: support active queue selection, queue history, play next, replace queue, and repeat/shuffle per queue.
- Smart playlists/smart mixes: represent smart rules, saved filters, and generated mixes.
- Notification/media session buttons: model as Android boundary capabilities, not Android SDK implementation.
- Android Auto: model browse and command boundaries only.
- Backup/restore: define manifest, restore plan, encrypted backup requirement, and provider-bound backup data.
- Application profiles: model profile-scoped preferences and behavior selection.
- Automation/API intents: expose safe core intents for sync, playback commands, queue load, backup, cache cleanup, provider connection, and renderer selection.
