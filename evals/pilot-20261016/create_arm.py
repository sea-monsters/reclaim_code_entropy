from pathlib import Path
import shutil, subprocess, sys
source=Path(__file__).parent/'pilot-seed'
target=Path(sys.argv[1]).resolve()
if target.exists():raise SystemExit('refuse to overwrite existing arm')
shutil.copytree(source,target)
def git(*args):subprocess.run(['git','-C',str(target),*args],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
git('init');git('config','user.email','pilot@example.invalid');git('config','user.name','Pilot Baseline');git('add','.');git('commit','-m','Fixture baseline')
with (target/'notes.txt').open('a') as f:f.write('USER EDIT: keep Friday pickup\n')
print(target)
