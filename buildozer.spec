[app]
title = 狂野飙车9助手
package.name = asphalt9helper
package.domain = org.z1059166378
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

requirements = python3,kivy==2.3.0,opencv-python-headless==4.9.0.80,numpy==1.24.4,Pillow==10.3.0

orientation = landscape
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
