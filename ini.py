[app]
title = A9自动化脚本
package.name = a9script
package.domain = org.example
source.dir = .
source.main = main.py
version = 0.1
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.archs = arm64-v8a
requirements = python3,opencv,numpy
buildozer -v android debug