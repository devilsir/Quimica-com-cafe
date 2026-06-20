# Runtime hook para PyInstaller/Kivy.
# Roda antes do app principal e força o Kivy a usar ffpyplayer, não GStreamer.

import os
import sys
import site

# Alguns builds congelados podem deixar site.USER_BASE/USER_SITE como None.
# Isso evita crashes em dependências que consultam esses valores.
_user_base = os.environ.get("PYTHONUSERBASE")
if not _user_base:
    _user_base = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python")

if getattr(site, "USER_BASE", None) is None:
    site.USER_BASE = _user_base

if getattr(site, "USER_SITE", None) is None:
    site.USER_SITE = os.path.join(
        _user_base,
        f"Python{sys.version_info.major}{sys.version_info.minor}",
        "site-packages",
    )

# Força os providers do Kivy. No Kivy o provider se chama ffpyplayer.
os.environ["KIVY_VIDEO"] = "ffpyplayer"
os.environ["KIVY_AUDIO"] = "ffpyplayer"
