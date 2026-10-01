from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json, os, ast, io, contextlib

ROOT=os.path.dirname(__file__)
PLAYER={'name':'Alex','xp':2450,'coins':620,'level':8,'streak':7,'completed':[],'achievements':[]}
CHALLENGES={
 'variables': {'title':'Crystal Variables','topic':'Variables','difficulty':'EASY','xp':100,'coins':50,'prompt':'Create a variable named score with the value 100, then print score.','starter':'# Create score and print it\n'},
 'conditions': {'title':'Gatekeeper Logic','topic':'Conditions','difficulty':'EASY','xp':120,'coins':60,'prompt':'Print "open" if key == "emerald", otherwise print "locked".','starter':'key = "emerald"\n# Write your condition\n'},
 'loops': {'title':'Magic Crystals','topic':'Loops','difficulty':'MEDIUM','xp':180,'coins':80,'prompt':'Use a for loop to print every crystal in the list.','starter':'crystals = ["Ruby", "Emerald", "Sapphire", "Diamond"]\n# Write your loop\n'},
 'functions': {'title':'Spell Function','topic':'Functions','difficulty':'MEDIUM','xp':200,'coins':90,'prompt':'Create a function greet(name) that returns "Hello, <name>!" and print greet("Alex").','starter':'# Define greet(name)\n'},
 'boss': {'title':'Loop Dragon','topic':'Loops','difficulty':'BOSS','xp':500,'coins':250,'prompt':'Defeat the Loop Dragon: calculate the total of scores = [10, 20, 30, 40] using a loop and print 100.','starter':'scores = [10, 20, 30, 40]\n# Defeat the dragon\n'}
}

def safe_execute(code):
    blocked=['import ','__','open(','exec(','eval(','compile(','os.','sys.','subprocess','socket','shutil','pathlib','input(','globals(','locals(','getattr(','setattr(']
    low=code.lower()
    if any(x in low for x in blocked): return {'ok':False,'output':'Blocked: unsafe operation detected.','error':'Use only basic Python syntax for this challenge.'}
    try:
        tree=ast.parse(code,mode='exec')
        allowed=(ast.Module,ast.Assign,ast.AnnAssign,ast.Expr,ast.Name,ast.Constant,ast.List,ast.Tuple,ast.Dict,ast.For,ast.While,ast.If,ast.Compare,ast.BinOp,ast.UnaryOp,ast.BoolOp,ast.Call,ast.Load,ast.Store,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Mod,ast.Pow,ast.Eq,ast.NotEq,ast.Lt,ast.LtE,ast.Gt,ast.GtE,ast.In,ast.NotIn,ast.And,ast.Or,ast.Not,ast.USub,ast.UAdd,ast.FunctionDef,ast.arguments,ast.arg,ast.Return,ast.JoinedStr,ast.FormattedValue,ast.AugAssign,ast.Subscript,ast.Slice,ast.Index)
        if any(not isinstance(n,allowed) for n in ast.walk(tree)): return {'ok':False,'output':'Unsupported Python construct for the safe demo runner.','error':'Try variables, conditions, loops, functions, lists and print.'}
        buf=io.StringIO()
        builtins={'print':print,'range':range,'len':len,'sum':sum,'str':str,'int':int}
        with contextlib.redirect_stdout(buf): exec(compile(tree,'<quest>','exec'), {'__builtins__':builtins}, {})
        return {'ok':True,'output':buf.getvalue().strip() or '(no output)','error':''}
    except Exception as e: return {'ok':False,'output':'','error':f'{type(e).__name__}: {e}'}

def check(cid,code):
    r=safe_execute(code); passed=False
    if r['ok']:
        out=r['output']
        if cid=='variables': passed='100' in out
        elif cid=='conditions': passed=out.strip()=='open'
        elif cid=='loops': passed=all(x in out for x in ['Ruby','Emerald','Sapphire','Diamond'])
        elif cid=='functions': passed='Hello, Alex!' in out
        elif cid=='boss': passed=out.strip().splitlines()[-1:] == ['100']
    return {**r,'passed':passed}

class Handler(BaseHTTPRequestHandler):
    def send_json(self,data,status=200):
        raw=json.dumps(data).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/':
            html=open(os.path.join(ROOT,'templates','index.html'),encoding='utf-8').read().replace('{{ challenges|tojson }}',json.dumps(CHALLENGES)).replace('{{ player|tojson }}',json.dumps(PLAYER))
            raw=html.encode(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        if path.startswith('/static/'):
            fp=os.path.join(ROOT,path.lstrip('/'))
            if os.path.isfile(fp):
                raw=open(fp,'rb').read(); typ='image/png' if fp.endswith('.png') else 'application/octet-stream'; self.send_response(200); self.send_header('Content-Type',typ); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        if path=='/api/state': self.send_json(PLAYER); return
        self.send_json({'error':'Not found'},404)
    def body(self):
        n=int(self.headers.get('Content-Length','0')); return json.loads(self.rfile.read(n) or b'{}')
    def do_POST(self):
        path=urlparse(self.path).path; data=self.body()
        if path=='/api/run': self.send_json(check(data.get('challenge','loops'),data.get('code',''))); return
        if path=='/api/submit':
            cid=data.get('challenge','loops'); r=check(cid,data.get('code',''))
            if r['passed'] and cid not in PLAYER['completed']:
                c=CHALLENGES[cid]; PLAYER['completed'].append(cid); PLAYER['xp']+=c['xp']; PLAYER['coins']+=c['coins']; PLAYER['level']=PLAYER['xp']//300+1
                if 'First Quest' not in PLAYER['achievements']: PLAYER['achievements'].append('First Quest')
                if len(PLAYER['completed'])>=3 and 'Quest Hunter' not in PLAYER['achievements']: PLAYER['achievements'].append('Quest Hunter')
                if cid=='boss' and 'Boss Slayer' not in PLAYER['achievements']: PLAYER['achievements'].append('Boss Slayer')
            r['player']=PLAYER; self.send_json(r); return
        if path=='/api/tutor':
            msg=(data.get('message') or '').lower(); code=(data.get('code') or '').lower(); low=msg+' '+code
            if 'loop' in low or 'for ' in low: reply='Think about three parts: the loop variable, the collection, and the indented body. Hint: for item in items: print(item). Try it yourself before I reveal more.'
            elif 'nameerror' in low: reply='A NameError means Python cannot find the variable name. Check spelling and make sure the variable is created before you use it.'
            elif 'function' in low or 'def ' in low: reply='A function groups reusable logic. Start with def function_name(parameters):, indent the body, and use return when you want to send a value back.'
            elif 'condition' in low or 'if ' in low: reply='For conditions, think: if the condition is true, run this block; otherwise run the else block. Use == when checking equality.'
            else: reply='Let’s solve it step by step. Identify the input, expected output, and smallest Python construct that connects them. Paste your error or code and I’ll give you a progressive hint.'
            self.send_json({'reply':reply}); return
        if path=='/api/reset':
            PLAYER.update({'xp':2450,'coins':620,'level':8,'completed':[],'achievements':[]}); self.send_json(PLAYER); return
        self.send_json({'error':'Not found'},404)
    def log_message(self,format,*args): pass

if __name__=='__main__':
    port=int(os.environ.get('PORT','5000')); ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
