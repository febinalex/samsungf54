import os,json,base64,sys;from pathlib import Path;from Crypto.Cipher import AES;from Crypto.Protocol.KDF import PBKDF2;from Crypto.Hash import SHA256;from Crypto.Random import get_random_bytes
S,K,CH=Path("data/threads.json"),os.getenv("ENCRYPTION_KEY"),15*1024*1024
def eS(d,p):
 s,n=get_random_bytes(16),get_random_bytes(16);k=PBKDF2(p,s,dkLen=32,count=600000,hmac_hash_module=SHA256);c=AES.new(k,AES.MODE_GCM,nonce=n);ct,t=c.encrypt_and_digest(d.encode('utf-8'));u=s+n+t+ct;return base64.b64encode(u).decode('utf-8')
def dS(c,p):
 try:
  b=base64.b64decode(c);s,n,t,ct=b[:16],b[16:32],b[32:48],b[48:];k=PBKDF2(p,s,dkLen=32,count=600000,hmac_hash_module=SHA256);c=AES.new(k,AES.MODE_GCM,nonce=n);return c.decrypt_and_verify(ct,t).decode('utf-8')
 except:return None
def main():
 if len(sys.argv)<2:return
 a=sys.argv[1].lower();k=K or input("Key: ");f=S
 if a=="encrypt":
  if not f.exists():return
  r=f.read_text(encoding="utf-8")
  if r.strip().startswith("{"):
   e=eS(r,k)
   for i in range(0,len(e),CH):
    p=Path(f"{f}.{i//CH+1:02}")
    p.write_text(e[i:i+CH]);print(f"Saved {p}")
   print("D")
 elif a=="decrypt":
  c=""
  for p in sorted(f.parent.glob(f"{f.name}.*")):
   c+=p.read_text()
  if not c:return
  d=dS(c,k)
  if d:f.write_text(d,encoding="utf-8");print("Open")
  else:sys.exit(1)
if __name__=="__main__":main()
