#!/bin/bash

# Standalone install script for copying files

set -e

prefix="${XDG_DATA_HOME:-$HOME/.local/share}"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"

krunner_dbusdir="$prefix/krunner/dbusplugins"
services_dir="$prefix/dbus-1/services/"
config_dir="$config_home/krunner-kdbx"

mkdir -p $krunner_dbusdir
mkdir -p $services_dir
mkdir -p $config_dir

cp krunner-kdbx.desktop $krunner_dbusdir
cp org.kde.krunner_kdbx.service $services_dir
cp config.json $config_dir

kquitapp6 krunner

