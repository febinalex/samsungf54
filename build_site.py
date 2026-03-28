import os,json,base64,sys,re,shutil;from datetime import datetime;from pathlib import Path;from collections import Counter
I,O,T,A,B=Path("data/threads.json"),Path("docs"),Path("templates"),Path("docs/api"),"https://febinalex.github.io/samsungf54"
def mH(h):h=re.sub(r'<!--(.*?)-->','',h,flags=re.DOTALL);h=re.sub(r'>\s+<','><',h);h=re.sub(r'\s+',' ',h);return h.strip()
def mC(c):c=re.sub(r'/\*.*?\*/','',c,flags=re.DOTALL);c=re.sub(r'\s*([\{\};:,])\s*',r'\1',c);c=re.sub(r'\s+',' ',c);return c.strip()
def mJ(j):j=re.sub(r'/\*.*?\*/','',j,flags=re.DOTALL);j=re.sub(r'(?<!:)\/\/.*','',j);j=re.sub(r'\s+',' ',j);return j.strip()
def main():
 if not I.exists():return
 d=json.loads(I.read_text(encoding="utf-8"));t=d.get("threads",[]);O.mkdir(parents=True,exist_ok=True)
 if A.exists():shutil.rmtree(A)
 A.mkdir(parents=True,exist_ok=True);iT=[];tL=set();vC,rC=0,0
 for x in t:
  root_msg=next((m for m in x.get("messages",[]) if m.get("source")=="root"),None)
  if not root_msg and x.get("messages"):root_msg=x["messages"][0]
  tg=x.get("topic_group")
  if tg:tL.add(tg)
  k=root_msg.get("kudos",0) if root_msg else 0
  v=x.get("views",0);rc=max(0,len(x.get("messages",[]))-1);vC+=v;rC+=rc
  iT.append({"thread_id":x["thread_id"],"url":x.get("url"),"title":x.get("title"),"model":x.get("model"),"topic_group":tg,"views":v,"likes":k,"source_file":x.get("source_file"),"reply_count":rc,"author":root_msg.get("author") if root_msg else "Unknown","author_id":root_msg.get("author_id") if root_msg else "","published":root_msg.get("published") if root_msg else None,"preview":root_msg.get("text","")[:200] if root_msg else ""})
 mCts=Counter(x["model"] for x in iT).most_common(5);iD={"generated_at_utc":d.get("generated_at_utc") or datetime.now().isoformat(),"total":len(iT),"threads":iT,"topics":sorted(list(tL)),"stats":{"v":vC,"r":rC,"u":len(set(x['author'] for x in iT))},"analytics":{"models":mCts}}
 (O/"data.json").write_text(json.dumps(iD,separators=(',',':')),encoding="utf-8")
 for x in t:(A/f"{x['thread_id']}.json").write_text(json.dumps(x,separators=(',',':')),encoding="utf-8")
 h=(T/"index.html").read_text(encoding="utf-8");c=(T/"style.css").read_text(encoding="utf-8");j=(T/"script.js").read_text(encoding="utf-8")
 tS="Samsung Green Line Issue Tracking Board | Dashboard for F54, S22, S23, S24"
 dS="Global tracking board for Samsung Green Line issues, Pink Line, and Display defects. Search community reports for F54, S21, S22, S23, S24. Check for Samsung Free Replacement eligibility."
 kY="samsung green line issue, green line issue, samsung pink line, samsung free replacement, display line defect, F54 screen issue, S22 display line, S23 green line, S24 display issues"
 f=h.replace("__TITLE__",tS).replace("__DESCRIPTION__",dS).replace("__BASE_URL__",B)
 sB=f'<meta name="keywords" content="{kY}">\n<meta property="og:site_name" content="Samsung Display Issue Tracker">\n';f=f.replace('<!-- SEO & Social Graph -->',sB+'<!-- SEO & Social Graph -->')
 (O/"index.html").write_text(mH(f),encoding="utf-8");(O/"style.css").write_text(mC(c),encoding="utf-8");(O/"script.js").write_text(mJ(j),encoding="utf-8")
 fav=Path("favicon.png")
 if fav.exists():shutil.copy(fav,O/"favicon.png")
 wR();wS();wM()
 print(f"Built Full Site for {B}")
def wR():(O/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {B}/sitemap.xml\n",encoding="utf-8")
def wS():
 n=datetime.now().strftime("%Y-%m-%d");x=f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n <url>\n <loc>{B}/</loc>\n <lastmod>{n}</lastmod>\n <changefreq>daily</changefreq>\n <priority>1.0</priority>\n </url>\n</urlset>'
 (O/"sitemap.xml").write_text(x,encoding="utf-8")
def wM():
 m={"name":"Samsung Display Complaints Board","short_name":"Samsung Tracker","description":"Archive of Samsung Community display line complaints.","start_url":"./index.html","display":"standalone","background_color":"#010816","theme_color":"#0062ff","icons":[{"src":"favicon.png","sizes":"192x192","type":"image/png"},{"src":"favicon.png","sizes":"512x512","type":"image/png"}]}
 (O/"manifest.webmanifest").write_text(json.dumps(m,separators=(',',':')),encoding="utf-8")
if __name__=="__main__":main()
