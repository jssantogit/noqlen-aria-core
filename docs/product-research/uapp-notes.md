# USB Audio Player PRO Notes

Product research notes for Aria Core planning only. These notes do not authorize implementation.

- USB DAC: model route availability and capability metadata.
- Hi-Res output: represent high-resolution support as output capability state.
- Bit-perfect capability: expose capability and conflict state; do not implement a bit-perfect driver.
- Sample rate and bit depth support: model supported values and active route metadata.
- DSD/MQA awareness: keep as capability metadata, not decoding or driver behavior.
- Bluetooth codec/output state: represent route state, codec metadata, and limitations.
- Renderer/output route diagnostics: surface route readiness, unsupported format, and capability mismatch diagnostics.
- Output troubleshooting hints: provide safe warnings for route/capability issues.
- No real driver implementation in Aria Core.
