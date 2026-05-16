# Android Player Reference

This file records factual product-research references only. Third-party product and company names do not imply affiliation, endorsement, sponsorship, association, official support, or compatibility. Do not copy logos, screenshots, icons, UI assets, branding, or long text from third-party products.

This is not authorization to implement UI, Android SDK code, playback, cache/offline/download, Android Auto, MediaSession, DSP/EQ, or real audio drivers.

- Symfonium: provider registry, provider capability matrix, sync manager, offline/cache/download models, multiple queues, smart playlists/smart mixes, notification/media session buttons, Android Auto, backup/restore, application profiles, and automation/API intents.
- USB Audio Player PRO (UAPP): USB DAC, hi-res output, bit-perfect capability, sample rate and bit depth support, DSD/MQA awareness as metadata, Bluetooth codec/output state, renderer/output diagnostics, and output troubleshooting hints.
- Poweramp: local library/folder browsing, dynamic queue, per-output settings, ReplayGain, gapless/crossfade/fade, format support, CUE/radio stream support, lyrics/artwork metadata, and Android controls.

Related notes live in `docs/product-research/`.

Use generic Aria domain names such as `SmartPlaylist`, `MultipleQueue`, `OutputProfile`, `BitPerfectCapability`, and `MediaProviderRegistry`. Do not use brand-based class or feature names.

Any future implementation needs a dedicated spec and explicit block scope.
