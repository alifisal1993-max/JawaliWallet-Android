from pathlib import Path
root=Path('extracted/JawaliWallet_Android_V31_07')
p=root/'app/src/main/assets/jawali-live.js'
s=p.read_text(encoding='utf-8')
start=s.index('window.jawaliActivateProfile=async id=>{')
end=s.index('window.jawaliTransfer=',start)
replacement=r"""window.jawaliActivateProfile=async id=>{
 const p=(liveData.profiles?.profiles||[]).find(x=>x.id===id);
 if(!p)return toast('لم يتم العثور على البروفايل؛ حدّث القائمة');
 if(!token||!liveUser?.phone)return toast('سجّل الدخول بحساب العميل أولًا');
 if(busy)return toast('يوجد طلب تفعيل قيد التنفيذ؛ لا تكرر عملية الشراء');
 const deviceToken=window.JawaliNative?.deviceToken?.();
 if(!deviceToken||deviceToken.length<16)return toast('تعذّر التعرف على الجهاز المرتبط بالحساب');
 const deviceMac=(window.JawaliNative?.deviceMac?.()||'').trim();
 if(!confirm('شراء وتفعيل '+p.name+' لرقم '+liveUser.phone+' مقابل '+rial(p.price)+'؟\nلن يُرسل الطلب مرة ثانية تلقائيًا. عند انقطاع الاتصال افحص الرصيد والاستهلاك قبل المحاولة مجددًا.'))return;
 busy=true;
 let submitted=false;
 try{
  status('جارٍ إرسال طلب ربط الباقة لرقم '+liveUser.phone+' إلى الخادم…');
  submitted=true;
  const r=await call('/api/client/wifi-phone-login','POST',{phoneProfileId:p.id,deviceToken,deviceMac});
  if(r.ok!==true||String(r.username)!==String(liveUser.phone)||!r.hotspotLoginUrl){
    throw new Error('لم يؤكد الخادم ربط البروفايل برقم الهاتف. افحص سجل العمليات قبل إعادة الطلب');
  }
  status('أكد الخادم تفعيل '+(r.packageName||p.name)+' على رقم '+r.username+'؛ جاري تحميل بيانات الاستهلاك');
  await refresh().catch(()=>{});
  clientTab='internet';render();
  try{await jawaliPhoneQuota();}catch(e){}
  if(window.JawaliNative?.openHotspotLogin){
    JawaliNative.openHotspotLogin(r.hotspotLoginUrl,r.username,r.password||'');
  }else toast('تم تأكيد ربط الباقة من الخادم؛ افتح صفحة الدخول للشبكة');
 }catch(e){
  const msg=errorText(e);
  status('لم يكتمل تأكيد التفعيل: '+msg);
  toast((/مهلة|timeout|timed out/i.test(msg)&&submitted)
    ?'انتهت مهلة التفعيل. لا تكرر الشراء قبل فحص كشف المحفظة واستهلاك رقم الهاتف'
    :msg);
 }finally{busy=false;}
};
"""
s=s[:start]+replacement+s[end:]
old="""'<div class="wallet-consumption-grid"><div><small>المستهلك</small><b>'+size(use)+'</b></div><div><small>المتبقي</small><b>'+size(q.remainingBytes)+'</b></div><div><small>الوقت المتبقي</small><b>'+minutes(q.remainingSeconds)+'</b></div></div>'+"""
new="""'<div class="wallet-consumption-grid"><div><small>المستهلك</small><b>'+size(use)+'</b></div><div><small>المتبقي</small><b>'+size(q.remainingBytes)+'</b></div><div><small>الوقت المتبقي</small><b>'+minutes(q.remainingSeconds)+'</b></div><div><small>الوقت المستخدم</small><b>'+minutes(q.totalUptimeSeconds)+'</b></div><div><small>التحميل</small><b>'+size(q.totalDownloadBytes)+'</b></div><div><small>الرفع</small><b>'+size(q.totalUploadBytes)+'</b></div></div>'+"""
assert old in s
s=s.replace(old,new)
old="clientNavigate=function(t){priorNav(t);if(liveUser){window.jawaliLiveRefresh();if(t==='internet')setTimeout(()=>jawaliPhoneQuota(),180)}};"
assert old in s
s=s.replace(old,old+"\nsetInterval(()=>{if(liveUser&&clientTab==='internet'&&!busy)jawaliPhoneQuota().catch(()=>{});},30000);")
p.write_text(s,encoding='utf-8')
j=root/'app/src/main/java/com/jawali/wallet/MainActivity.java'
s=j.read_text()
old='    @JavascriptInterface public String deviceToken() {return stableDeviceToken();}'
assert old in s
s=s.replace(old,old+'\n    // Android MAC randomization: backend accepts empty MAC; token binds the device.\n    @JavascriptInterface public String deviceMac() {return "";}' )
j.write_text(s)
g=root/'app/build.gradle'
s=g.read_text().replace('versionCode 3110; versionName "31.10"','versionCode 3111; versionName "31.11"')
assert 'versionName "31.11"' in s
g.write_text(s)
print('V31.11 patch ready')
