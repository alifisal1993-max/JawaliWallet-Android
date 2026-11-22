from pathlib import Path
root=Path("extracted/JawaliWallet_Android_V31_07")
j=root/"app/src/main/java/com/jawali/wallet/MainActivity.java"
s=j.read_text()
s=s.replace('if(!"https".equalsIgnoreCase(url.getProtocol())) throw new Exception("يلزم اتصال HTTPS موثوق بالخادم");\n          if(!"alfaisal.taild58c1c.ts.net".equalsIgnoreCase(url.getHost()) || url.getPort()!=-1 || url.getUserInfo()!=null) throw new Exception("عنوان خادم غير معتمد");', '''boolean local="http".equalsIgnoreCase(url.getProtocol()) && "172.16.20.20".equals(url.getHost()) && url.getPort()==4000;
          boolean remote="https".equalsIgnoreCase(url.getProtocol()) && "alfaisal.taild58c1c.ts.net".equalsIgnoreCase(url.getHost()) && url.getPort()==-1;
          if ((!local && !remote) || url.getUserInfo()!=null || url.getQuery()!=null || url.getRef()!=null) throw new Exception("عنوان خادم غير معتمد");''')
s=s.replace("تعذر الاتصال بخادم المحفظة. تأكد من اتصال Tailscale ثم جرّب فحص الخادم.","تعذر الاتصال بخادم المحفظة. افحص Wi-Fi المحلي والاتصال الخارجي.")
assert 'boolean local="http"' in s
j.write_text(s)
x=root/"app/src/main/res/xml/network_security_config.xml"
s=x.read_text().replace("<domain>172.16.0.1</domain></domain-config>","<domain>172.16.0.1</domain><domain>172.16.20.20</domain></domain-config>")
assert "<domain>172.16.20.20</domain>" in s
x.write_text(s)
p=root/"app/src/main/assets/jawali-live.js"
s=p.read_text()
s=s.replace("let liveUser=null, token=null, apiBase='https://alfaisal.taild58c1c.ts.net'","let liveUser=null, token=null, apiBase='http://172.16.20.20:4000'")
s=s.replace("const SERVER_URL='https://alfaisal.taild58c1c.ts.net';\nconst saved=SERVER_URL;","const LOCAL_URL='http://172.16.20.20:4000';\nconst SERVER_URL='https://alfaisal.taild58c1c.ts.net';\nconst saved=LOCAL_URL;")
needle="window.JawaliLive={receive(id,status,payload)"
assert needle in s
s=s.replace(needle,"""// Choose a server using GET health checks only. Never automatically repeat a POST.
let lastConnectionCheck=0;
async function selectServer(){
 if(Date.now()-lastConnectionCheck<20000 && apiBase)return apiBase;
 const previous=apiBase;
 for(const candidate of [LOCAL_URL,SERVER_URL]){
  apiBase=candidate;
  try{const r=await call('/api/health');if(r.ok===true&&r.database==='connected'){
   lastConnectionCheck=Date.now();return candidate;
  }}catch(e){}
 }
 apiBase=previous;
 throw new Error('تعذر الاتصال بالخادم محليًا أو خارجيًا');
}
"""+needle)
s=s.replace("window.jawaliCheck=async()=>{try{apiBase=SERVER_URL;const x=await call('/api/health');","window.jawaliCheck=async()=>{try{await selectServer();const x=await call('/api/health');")
s=s.replace("apiBase=SERVER_URL;const deviceToken=window.JawaliNative?.deviceToken?.();","await selectServer();const deviceToken=window.JawaliNative?.deviceToken?.();")
s=s.replace("try{status('جارٍ إرسال طلب إنشاء الحساب…');const r=await call('/api/auth/register'","try{await selectServer();status('جارٍ إرسال طلب إنشاء الحساب…');const r=await call('/api/auth/register'")
s=s.replace("اتصال HTTPS موثوق؛ إدارة الخادم للمسؤول فقط.","تحذير: HTTP المحلي غير مشفر؛ يلزم HTTPS محلي قبل استخدام الحسابات المالية الحقيقية.")
assert "await selectServer();const deviceToken" in s and "await selectServer();status('جارٍ إرسال" in s
p.write_text(s)
g=root/"app/build.gradle"
s=g.read_text().replace('versionCode 3108; versionName "31.08"','versionCode 3109; versionName "31.09"')
assert 'versionName "31.09"' in s
g.write_text(s)
print("Patched Jawali Wallet V31.09")
