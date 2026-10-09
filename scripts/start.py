import os,sys,subprocess,threading,time,urllib.request,webbrowser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'frontend/dist/index.html').exists():raise SystemExit('Prebuilt frontend missing. Run setup with --rebuild.')
# Read the simple KEY=VALUE configuration without a shell or extra dependencies.
if (ROOT/'.env').exists():
 for line in (ROOT/'.env').read_text().splitlines():
  if line.strip() and not line.lstrip().startswith('#') and '=' in line:
   key,value=line.split('=',1);os.environ.setdefault(key.strip(),value.strip().strip('"').strip("'"))
port=os.getenv('PORT','8000')
if not port.isdigit() or not 1024<=int(port)<=65535:raise SystemExit('PORT must be a number from 1024 to 65535.')
url='http://127.0.0.1:'+port
try:
 with urllib.request.urlopen(url+'/api/health',timeout=1) as response:
  if response.status==200:raise SystemExit(f'An application already uses {url}. Stop it before starting MotionMind.')
except (OSError,ValueError):pass
process=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',port,'--ws-max-size','32768'],cwd=ROOT/'backend')
def open_when_ready():
 for _ in range(50):
  if process.poll() is not None:return
  try:
   with urllib.request.urlopen(url+'/api/health',timeout=.5):webbrowser.open(url);return
  except OSError:time.sleep(.2)
threading.Thread(target=open_when_ready,daemon=True).start()
print(f'MotionMind: {url}\nKeep this window open. Press Ctrl+C to stop.')
try:raise SystemExit(process.wait())
except KeyboardInterrupt:
 process.terminate()
 try:process.wait(timeout=8)
 except subprocess.TimeoutExpired:process.kill()
