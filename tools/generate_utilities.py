from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
classes=set()
for p in root.glob('*.html'):
 for c in re.findall(r'class="([^"]+)"',p.read_text()):classes.update(c.split())
colors={'slate-50':'#f8fafc','slate-300':'#cbd5e1','slate-400':'#94a3b8','slate-500':'#64748b','slate-600':'#475569','slate-700':'#334155','slate-800':'#1e293b','slate-900':'#0f172a','blue-100':'#dbeafe','blue-500':'#3b82f6','blue-600':'#2563eb','white':'#fff','yellow-400':'#facc15'}
fixed={'flex':'display:flex','grid':'display:grid','hidden':'display:none','flex-wrap':'flex-wrap:wrap','items-center':'align-items:center','items-start':'align-items:flex-start','justify-center':'justify-content:center','justify-start':'justify-content:flex-start','w-full':'width:100%','mx-auto':'margin-left:auto;margin-right:auto','max-w-7xl':'max-width:1280px','max-w-2xl':'max-width:672px','max-w-xl':'max-width:576px','max-w-sm':'max-width:384px','text-center':'text-align:center','uppercase':'text-transform:uppercase','not-italic':'font-style:normal','line-through':'text-decoration:line-through','tracking-widest':'letter-spacing:.1em','leading-relaxed':'line-height:1.625','border':'border:1px solid #e2e8f0','rounded-3xl':'border-radius:24px','rounded-xl':'border-radius:12px','shadow-2xl':'box-shadow:0 25px 50px -12px rgb(0 0 0 / .25)','overflow-hidden':'overflow:hidden'}
sizes={'xs':'.75rem','sm':'.875rem','lg':'1.125rem','xl':'1.25rem','2xl':'1.5rem','3xl':'1.875rem','4xl':'2.25rem','5xl':'3rem'}
weight={'bold':700,'extrabold':800,'black':900}
lines=['/* Local utilities used by the existing static service pages; no runtime CSS compiler. */']
for item in sorted(classes):
 prefix,_,base=item.rpartition(':');base=base or item
 important=base.startswith('!');base=base.lstrip('!')
 css=fixed.get(base)
 m=re.fullmatch(r'(p[xytrbl]?|m[xytrbl]?|gap|w|h)-(\d+)',base)
 if m:
  prop,n=m.groups();value=f'{int(n)/4:g}rem'
  if prop=='gap':css='gap:'+value
  elif prop in ('w','h'):css=('width' if prop=='w' else 'height')+':'+value
  else:
   axis=prop[1:];key='padding' if prop[0]=='p' else 'margin'
   sides={'x':['left','right'],'y':['top','bottom'],'t':['top'],'b':['bottom'],'l':['left'],'r':['right'],'':[''] }[axis]
   css=';'.join(key+('-'+side if side else '')+':'+value for side in sides)
 if base.startswith('text-'):
  v=base[5:]
  if v in sizes:css='font-size:'+sizes[v]
  elif v in colors:css='color:'+colors[v]
 if base.startswith('bg-') and base[3:] in colors:css='background-color:'+colors[base[3:]]
 if base.startswith('border-') and base[7:] in colors:css='border-color:'+colors[base[7:]]
 if base.startswith('font-') and base[5:] in weight:css='font-weight:'+str(weight[base[5:]])
 m=re.fullmatch(r'grid-cols-(\d)',base)
 if m:css=f'grid-template-columns:repeat({m[1]},minmax(0,1fr))'
 m=re.fullmatch(r'space-y-(\d+)',base)
 suffix=''
 if m:css=f'margin-top:{int(m[1])/4:g}rem';suffix=' > :not([hidden]) ~ :not([hidden])'
 if not css:continue
 selector='.'+re.sub(r'([^a-zA-Z0-9_-])',r'\\\1',item)+suffix
 if prefix=='hover':selector+=':hover'
 if important:css=css.replace(';','!important;')+'!important'
 rule=selector+'{'+css+'}'
 if prefix in ('md','lg'):rule=f'@media(min-width:{768 if prefix=="md" else 1024}px){{{rule}}}'
 lines.append(rule)
(root/'assets/utilities.css').write_text('\n'.join(lines)+'\n')
print('Generated',len(lines)-1,'local utility rules.')
