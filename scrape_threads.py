import json,random,re,sys,xml.etree.ElementTree as ET;from concurrent.futures import ThreadPoolExecutor,as_completed;from dataclasses import asdict,dataclass,field;from datetime import datetime,timezone;from html import unescape;from itertools import cycle;from pathlib import Path;from typing import Any,Dict,List,Optional;from urllib.parse import urlparse;from urllib.request import Request,urlopen
L_F,O_F,U_A=Path("links.txt"),Path("data/threads.json"),["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0","Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1"]
U_C=cycle(U_A)
@dataclass
class _m:id:Optional[str]=None;subject:Optional[str]=None;text:str="";source:str="";author:Optional[str]=None;author_id:Optional[str]=None;published:Optional[str]=None;kudos:int=0;is_solution:bool=False;author_avatar:Optional[str]=None;url:Optional[str]=None;images:List[str]=field(default_factory=list)
@dataclass
class _td:url:str;domain:str;group:str;thread_id:Optional[str];title:str;topic_group:str;fetched_at_utc:str;messages:List[_m];model:str="Unknown";source_file:str="unknown";views:int=0
def _rl(p:Path)->List[str]:s,l=set(),[];for ln in p.read_text(encoding="utf-8").splitlines():u=ln.strip().rstrip(".");if not u or u.startswith("#") or u in s:continue;s.add(u);l.append(u)
 return l
def _rt(u:str)->str:r=Request(u,headers={"User-Agent":next(U_C),"Accept":"application/xml, text/xml, */*"});with urlopen(r,timeout=30) as rs:return rs.read().decode("utf-8",errors="replace")
def _st(v:str)->str:v=unescape(v or "");v=re.sub(r"<(script|style)[^>]*>.*?</\1>"," ",v,flags=re.I|re.S);v=re.sub(r"<br\s*/?>","\n",v,re.I);v=re.sub(r"</p\s*>","\n",v,re.I);v=re.sub(r"<[^>]+>"," ",v);v=unescape(v);v=re.sub(r"[ \t\r\f\v]+"," ",v);v=re.sub(r"\n\s*\n+","\n",v);return v.strip()
def _ti(u:str)->Optional[str]:m=re.search(r"/(?:td-p|m-p)/(\d+)",u);return m.group(1) if m else None
def _gu(u:str)->str:p=urlparse(u);t=[x for x in p.path.split("/") if x];b="general"
 if "t5" in t:
  try:b=t[t.index("t5")+1]
  except:b="general"
 return f"{p.netloc} / {b}"
def _sl(t:str)->str:v=re.sub(r"[^a-z0-9]+","-",t.lower());return v.strip("-")
def _dm(t:str)->str:t=t.lower();if re.search(r"f\s*54",t):return "F54"
 if re.search(r"s\s*22",t):return "S22"
 if re.search(r"s\s*23",t):return "S23"
 if re.search(r"s\s*24",t):return "S24"
 return "Others"
def _ct(t:str,c:str)->str:x=f"{t} {c}".lower();if "green line" in x:return "Green Line Issue"
 if "display" in x or "screen" in x:return "Display Issue"
 return "Other"
def _pn(n:ET.Element,s:str,d:str,b:str="t5",ts:str="msg")->Optional[_m]:bh=n.findtext("body") or "";bn=n.find("body");if not bh and bn is not None:bh=bn.text or ""
 t=_st(bh);im=[];it=re.findall(r'<img[^>]+?src=["\'](https?://[^"\']+)["\']',bh,re.I);for i in it:if "/emojis/" not in i.lower():im.append(i)
 a=n.findtext("./author/login");an=n.find("author");ai=None;if an is not None and "href" in an.attrib:ai=an.attrib["href"].split("/")[-1]
 p=n.findtext("post_time");sj=n.findtext("subject");mi=n.findtext("id");k=0;kt=n.findtext("./kudos/count") or n.findtext("kudos");if kt and kt.isdigit():k=int(kt)
 sl=n.findtext("is_solution")=="true";av=n.findtext("./author/avatar/profile") or n.findtext(".//avatar/profile");vu=f"https://{d}/t5/{b}/{ts}/{('td-p' if s=='root' else 'm-p')}/{mi}" if mi else None
 return _m(id=mi,author=a,author_id=ai,published=p,subject=sj,text=t,source=s,kudos=k,is_solution=sl,author_avatar=av,url=vu,images=im)
def _fr(d:str,i:str,b:str="t5",ts:str="msg")->_m:x=_rt(f"https://{d}/restapi/vc/messages/id/{i}");r=ET.fromstring(x);n=r.find("./message");p=_pn(n,"root",d,b,ts);if not p:raise Exception();return p
def _rr(d:str,i:str)->str:x=_rt(f"https://{d}/restapi/vc/messages/id/{i}");r=ET.fromstring(x);h=r.find("./message/root");if h is None:return i
 m=re.search(r"/messages/id/(\d+)",h.attrib.get("href",""));return m.group(1) if m else i
def _fc(d:str,ri:str,b:str="t5",ts:str="msg")->List[_m]:m,s,q=[],{ri},[ri]
 while q:
  if len(s)>1000:break
  ci=q.pop(0);p=1
  while True:
   try:x=_rt(f"https://{d}/restapi/vc/messages/id/{ci}/comments?page_size=50&page={p}");r=ET.fromstring(x)
   except:break
   ns=r.findall(".//message");if not ns:break
   fp=0;for n in ns:
    i=n.findtext("id");if i and i not in s:s.add(i);fp+=1;try:p_=_fr(d,i,b,ts);p_.source="comment";m.append(p_);q.append(i)
    except:continue
   if fp==0 or len(ns)<50:break
   p+=1
 return m
def _slnk(u:str,sf:str="unknown")->_td:p=urlparse(u);li=_ti(u);ri=_rr(p.netloc,li);pt=[x for x in p.path.split("/") if x];b="GalaxyF"
 if "t5" in pt:
  try:b=pt[pt.index("t5")+1]
  except:pass
 rp=_fr(p.netloc,ri,b,"thread");t=rp.subject or f"T{ri}";ts=_sl(t);rm=_fr(p.netloc,ri,b,ts);cm=_fc(p.netloc,ri,b,ts);vw=0
 try:v_=_rt(f"https://{p.netloc}/restapi/vc/messages/id/{ri}");vr=ET.fromstring(v_);vt=vr.findtext("./message/views/count");if vt and vt.isdigit():vw=int(vt)
 except:pass
 ms,s=[],{rm.id};for m in [rm]+cm:if m.id not in s:s.add(m.id);ms.append(m)
 return _td(url=u,domain=p.netloc,group=_gu(u),thread_id=ri,title=t,topic_group=_ct(t,rm.text),fetched_at_utc=datetime.now(timezone.utc).isoformat(),messages=ms,model=_dm(t+rm.text),source_file=sf,views=vw)
def main()->None:
 l,a=[],[]
 for p in Path(".").glob("*.txt"):
  if p.name in ["robots.txt","sitemap.txt"]:continue
  for u in _rl(p):a.append((u,p.name));l.append(u)
 l=list(dict.fromkeys(l));if not l:return
 O_F.parent.mkdir(parents=True,exist_ok=True);td=[]
 def wk(i,it):
  u,sf=it
  try:th=_slnk(u,sf);print(f"[{i}] OK {u}");return asdict(th)
  except Exception as e:print(f"[{i}] ERR {u} {e}");return{"url":u,"thread_id":_ti(u),"title":"ERR","messages":[]}
 s_u,d_l={},[]
 for u,f in a:
  if u not in s_u:s_u[u]=f;d_l.append((u,f))
 with ThreadPoolExecutor(max_workers=10) as ex:
  ft={ex.submit(wk,i,it):it for i,it in enumerate(d_l,1)}
  for f in as_completed(ft):td.append(f.result())
 py={"generated_at_utc":datetime.now(timezone.utc).isoformat(),"total":len(l),"threads":td}
 O_F.write_text(json.dumps(py,separators=(',',':')),encoding="utf-8")
if __name__=="__main__":main()
