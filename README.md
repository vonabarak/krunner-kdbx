### krunner-kdbx

A plugin for KRunner to query KDBX database for passwords

A bunch of code here borrowed from https://github.com/naglfar/krunner-keepassxc

```bash
mkdir -p ~/.local/share/krunner/dbusplugins/
cp krunner-kdbx.desktop ~/.local/share/krunner/dbusplugins/
kquitapp6 krunner
python -m krunner_kdbx
```
