#!/bin/bash

# Exit if something fails
set -e

prefix="${XDG_DATA_HOME:-$HOME/.local/share}"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"

krunner_dbusdir="$prefix/krunner/dbusplugins"
services_dir="$prefix/dbus-1/services/"
config_dir="$config_home/krunner-kdbx"

rm $krunner_dbusdir/org.kde.krunner_kdbx.service
rm $krunner_dbusdir/krunner-kdbx.desktop
# rm $config_dir/config.json

kquitapp6 krunner

