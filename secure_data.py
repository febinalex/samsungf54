import os,json,base64,sys;from pathlib import Path;from Crypto.Cipher import AES;from Crypto.Protocol.KDF import PBKDF2;from Crypto.Hash import SHA256;from Crypto.Random import get_random_bytes
S_F,E_K,C_S=Path("data/threads.json"),os.getenv("ENCRYPTION_KEY"),15*1024*1024
def _es(d,p):s=get_random_bytes(16);n=get_random_bytes(16);k=PBKDF2(p,s,dkLen=32,count=600000,hmac_hash_module=SHA256);c=AES.new(k,AES.MODE_GCM,nonce=n);ct,t=c.encrypt_and_digest(d.encode('utf-8'));return base64.b64encode(s+n+t+ct).decode('utf-8')
def _ds(cB,p):
 try:
  d=base64.b64decode(cB);s,n,t,ct=d[:16],d[16:32],d[32:48],d[48:];k=PBKDF2(p,s,dkLen=32,count=600000,hmac_hash_module=SHA256);c=AES.new(k,AES.MODE_GCM,nonce=n);return c.decrypt_and_verify(ct,t).decode('utf-8')
 except Exception as e:return None
def main():
 if len(sys.argv)<2:return
 a=sys.argv[1].lower();k=E_K or os.environ.get("ENCRYPTION_KEY")
 if not k:k=input("Key: ")
 if a=="encrypt":
  if not S_F.exists():return
  r=S_F.read_text(encoding="utf-8");e=_es(r,k);n=len(e)
  for i in range(0,n,C_S):
   p=Path(f"{S_F}.{i//C_S+1:02d}");p.write_text(e[i:i+C_S],encoding="utf-8");print(f"Saved {p.name}")
 elif a=="decrypt":
  c=sorted(S_F.parent.glob(f"{S_F.name}.*"));e="".join(x.read_text(encoding="utf-8") for x in c) if c else (S_F.read_text(encoding="utf-8") if S_F.exists() else "");d=_ds(e,k)
  if d:S_F.write_text(d,encoding="utf-8");print(f"Decrypted to {S_F}")
  else:sys.exit(1)
if __name__=="__main__":main()
