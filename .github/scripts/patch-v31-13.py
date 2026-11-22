from pathlib import Path
root=Path('extracted/JawaliWallet_Android_V31_07')
p=root/'app/src/main/assets/jawali-live.js'
s=p.read_text(encoding='utf-8')
a=s.index('window.jawaliPhoneQuota=async()=>{')
b=s.index('window.jawaliHotspotState=',a)
replacement="""window.jawaliPhoneQuota=async()=>{
 const el=document.getElementById('jw-phone-quota');if(el)el.textContent='جارٍ قراءة استهلاك الباقة الحالية…';
 try{
  const r=await call('/api/client/wifi-phone-quota');
  if(String(r.phone||'')!==String(liveUser?.phone||''))throw new Error('رقم الاستهلاك لا يطابق الحساب');
  const q=r.quota||{}, confirmed=!!q.entitlementId;
  const num=v=>v==null||!Number.isFinite(Number(v))?null:Number(v);
  const fmtBytes=v=>v==null||!Number.isFinite(Number(v))?'غير متاح':(Number(v)/1048576).toLocaleString('ar-YE',{maximumFractionDigits:1})+' ميجابايت';
  const fmtTime=v=>v==null||!Number.isFinite(Number(v))?'غير متاح':Math.ceil(Number(v)/60).toLocaleString('ar-YE')+' دقيقة';
  const used=num(q.totalUsedBytes),down=num(q.totalDownloadBytes),up=num(q.totalUploadBytes),limit=num(q.transferLimitBytes);
  const match=confirmed&&used!=null&&down!=null&&up!=null&&Math.abs(down+up-used)<=Math.max(1048576,used*0.02);
  const pct=confirmed&&used!=null&&limit!=null&&limit>0?Math.max(0,Math.min(100,100*used/limit)):null;
  const title=confirmed?(q.packageName||q.profile||'الباقة الحالية'):'لم يؤكد الخادم وجود باقة نشطة';
  const content='<div class="wallet-consumption-head"><small>استهلاك الباقة الحالية — '+safe(new Date().toLocaleTimeString('ar-YE'))+'</small><h3>'+safe(title)+'</h3><span>الهاتف: '+safe(r.phone)+'</span></div>'+
   '<div class="wallet-consumption-grid"><div><small>المستهلك من الباقة</small><b>'+fmtBytes(confirmed?used:null)+'</b></div><div><small>المتبقي من الباقة</small><b>'+fmtBytes(confirmed?q.remainingBytes:null)+'</b></div><div><small>الوقت المتبقي</small><b>'+fmtTime(confirmed?q.remainingSeconds:null)+'</b></div><div><small>الوقت المستخدم</small><b>'+fmtTime(confirmed?q.totalUptimeSeconds:null)+'</b></div><div><small>تحميل الباقة</small><b>'+fmtBytes(match?down:null)+'</b></div><div><small>رفع الباقة</small><b>'+fmtBytes(match?up:null)+'</b></div></div>'+
   (pct==null?'':'<div class="wallet-consumption-track"><span style="width:'+pct+'%"></span></div><small>استهلاك '+pct.toFixed(1)+'% من الباقة</small>')+
   '<p class="wallet-consumption-msg">'+(!confirmed?'لا توجد باقة نشطة مؤكدة في سجل المحفظة':match?'البيانات تخص الباقة الحالية من خادم المحفظة وUser Manager':'عدادات التحميل والرفع التراكمية غير مطابقة لاستهلاك هذه الباقة ولذلك لم تُعرض')+'</p>';
  if(el)el.innerHTML=content;else toast(title+' — المتبقي '+fmtBytes(confirmed?q.remainingBytes:null));
 }catch(e){if(el)el.textContent='تعذر قراءة الاستهلاك: '+errorText(e);else toast(errorText(e))}
};
"""
s=s[:a]+replacement+s[b:]
p.write_text(s,encoding='utf-8')
j=root/'app/src/main/java/com/jawali/wallet/MainActivity.java'
s=j.read_text(encoding='utf-8')
needle='''          if(!portal||attempted[0]||authenticated[0])return;
          // Different captive templates serve the login form at different paths.'''
assert needle in s
s=s.replace(needle,'''          if(!portal||attempted[0]||authenticated[0])return;
          // Some Hotspot configurations redirect /login to /index.html/.
          // Send one direct RouterOS login POST, then verify status; this is
          // compatible with PAP. CHAP-only needs a real router login form.
          String landingPath=current.getPath();
          if("/index.html/".equals(landingPath)||"/index.html".equals(landingPath)){
            attempted[0]=true;
            feedback.accept("pending","بوابة الراوتر حولت صفحة الدخول؛ جارٍ إرسال بيانات الهاتف وفحص الجلسة");
            try{
              String body="username="+java.net.URLEncoder.encode(username,"UTF-8")+
                "&password="+java.net.URLEncoder.encode(password,"UTF-8")+
                "&dst="+java.net.URLEncoder.encode("http://172.16.0.1/status","UTF-8")+
                "&popup=false";
              view.postUrl("http://172.16.0.1/login",body.getBytes(java.nio.charset.StandardCharsets.UTF_8));
              view.postDelayed(()->{if(!authenticated[0])view.loadUrl("http://172.16.0.1/status");},6500);
            }catch(Exception e){feedback.accept("failed","تعذر إرسال بيانات الدخول: "+e.getMessage());}
            return;
          }
          // Different captive templates serve the login form at different paths.''')
j.write_text(s,encoding='utf-8')
g=root/'app/build.gradle'
s=g.read_text().replace('versionCode 3112; versionName "31.12"','versionCode 3113; versionName "31.13"')
assert 'versionName "31.13"' in s
g.write_text(s)
print('V31.13 prepared')
