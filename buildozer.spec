[app]
title = Naughty or Nice Scanner
package.name = naughtyornicescanner
package.domain = com.stevechavez
source.dir = .
source.include_exts = py,png,jpg,jpeg,wav,mp3,ogg
version = 1.0
requirements = python3, pygame==2.1.0
orientation = portrait
fullscreen = 1

# Icons (optional — replace with your own PNGs if you like)
icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1

[android]
# Minimum supported API level
android.minapi = 21
android.api = 33
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET
