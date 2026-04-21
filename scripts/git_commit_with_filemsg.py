#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

msg = Path('commit_msg.txt').read_text(encoding='utf-8')
paths = [
    'bingo_game/ui/renderers/renderer_wx.py',
    'bingo_game/ui/overlay_numero.py',
    'CHANGELOG.md',
]
cmd = ['python', 'scripts/git_runner.py', 'commit', '--message', msg, '--paths'] + paths
proc = subprocess.run(cmd, text=True)
if proc.returncode != 0:
    sys.exit(proc.returncode)
sys.exit(0)
