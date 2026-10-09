"""Cross-platform dependency installer. Run with Python 3.11 or 3.12."""
import argparse,subprocess,sys,venv,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(args,cwd=ROOT):subprocess.run(args,cwd=cwd,check=True)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--rebuild',action='store_true',help='Rebuild React UI (requires Node 20+)');args=parser.parse_args()
 if sys.version_info[:2] not in ((3,11),(3,12)):raise SystemExit('Use Python 3.12 or 3.11. On Windows: py -3.12 scripts/setup.py')
 env=ROOT/'.venv';print('Creating local Python environment…');venv.EnvBuilder(with_pip=True).create(env)
 python=env/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
 run([str(python),'-m','pip','install','--upgrade','pip'])
 run([str(python),'-m','pip','install','-r',str(ROOT/'backend/requirements.txt')])
 if args.rebuild or not (ROOT/'frontend/dist/index.html').exists():
  node=shutil.which('node');npm=shutil.which('npm.cmd' if sys.platform=='win32' else 'npm')
  if not node or not npm:raise SystemExit('Install Node.js 20+ and re-run setup, or use the ZIP with the prebuilt frontend.')
  major=int(subprocess.check_output([node,'--version'],text=True).strip().lstrip('v').split('.')[0])
  if major<20:raise SystemExit('Node.js 20 or later is required for rebuilding.')
  run([npm,'ci'],ROOT/'frontend');run([npm,'run','assets'],ROOT/'frontend');run([npm,'run','build'],ROOT/'frontend')
 else: print('Prebuilt frontend and pose model found; Node.js is not required for quick start.')
 run([str(python),'-c','from app.database.database import initialize; initialize()'],ROOT/'backend')
 print('\nSetup complete. Run start.bat on Windows or ./start.sh on Linux/macOS.')
if __name__=='__main__':
 try:main()
 except subprocess.CalledProcessError as e:raise SystemExit(f'Setup command failed ({e.returncode}). See docs/TROUBLESHOOTING.md.')
