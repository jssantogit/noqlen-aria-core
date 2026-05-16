# Android Boundary

Aria Core is not an Android app and does not contain Android UI.

Bloco 0 does not add Android SDK, Kotlin, Gradle, screens, navigation, player UI, media controls, Android Auto, storage UX, or playback engine code.

Bloco 4 defines Android/player boundary contracts as abstract vocabulary only. The bridge protocols and fake implementations model boundaries for playback, media session, storage, Android Auto, foreground service, app lifecycle, notification, lock-screen, and headset events. They are not Android SDK integration.

Bloco 5 documents how a future UI/app shell consumes those boundaries: the UI does not call bridge protocols directly. It consumes app-facing Aria state and emits intents. A future platform adapter may wire bridge implementations behind Aria Core, but screens remain thin and display-only.

Future Android integration must remain a thin adapter over Aria Core and requires specs before implementation.

Forbidden without a future dedicated spec:

- Android SDK integration.
- Kotlin, Java, or Gradle files.
- Screens, navigation, player UI, or app shell code.
- Media3, ExoPlayer, MediaSession, or Android Auto implementation.
- Queue, now playing, playback engine, offline/cache, or storage mutation.

Allowed at the planning level:

- Documenting how `PermissionState`, `StorageAccessState`, and `AndroidBoundarySnapshot` may be presented as app-facing state.
- Documenting how platform permission prompts are delegated to a future Android adapter.
- Documenting that playback/media controls emit Aria intents rather than owning playback logic.
