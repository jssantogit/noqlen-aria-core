# USB Audio Player PRO Notes

Product research notes for Aria Core planning only. These notes do not authorize implementation.

Trademark/reference notice: third-party product and company names are used only as factual research references. Noqlen is not affiliated with, endorsed by, sponsored by, or associated with those products or companies. Do not copy logos, screenshots, icons, UI assets, branding, or long text from third-party products.

Use generic Aria domain names such as `MediaProviderRegistry`, `SmartPlaylist`, `MultipleQueue`, `OutputProfile`, and `BitPerfectCapability`. Do not create brand-based class or feature names.

- USB DAC: model route availability and capability metadata.
- Hi-Res output: represent high-resolution support as output capability state.
- Bit-perfect capability: expose capability and conflict state; do not implement a bit-perfect driver.
- Sample rate and bit depth support: model supported values and active route metadata.
- DSD/MQA awareness: keep as capability metadata, not decoding or driver behavior.
- Bluetooth codec/output state: represent route state, codec metadata, and limitations.
- Renderer/output route diagnostics: surface route readiness, unsupported format, and capability mismatch diagnostics.
- Output troubleshooting hints: provide safe warnings for route/capability issues.
- No real driver implementation in Aria Core.
