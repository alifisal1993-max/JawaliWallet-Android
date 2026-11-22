from pathlib import Path
root=Path("extracted/JawaliWallet_Android_V31_07")
p=root/"app/src/main/assets/jawali-live.js"
s=p.read_text(encoding="utf-8")
start=s.index(" let preflight;\n",s.index("window.jawaliActivateProfile="))
end=s.index(" if(!confirm('شراء وتفعيل ",start)
new=""" // Follow the working JawaliWallet-Full-System activation route.
 // Quota is advisory only: failed quota lookup must not prevent phone provisioning.
 let preflight=null;
 try{
  preflight=await call('/api/client/wifi-phone-quota');
 }catch(err){
  status('تعذر قراءة الاستهلاك الحالي؛ سيتم التحقق من التفعيل عبر خادم المحفظة.');
 }
 const q=preflight?.quota||{};
 const matches=String(q.packageName||q.profile||'').trim()===String(p.name).trim();
 const remaining=q.remainingSeconds===null||q.remainingSeconds===undefined?null:Number(q.remainingSeconds);
 const hasActiveEntitlement=!!q.entitlementId && matches && (remaining===null||remaining>0);
 if(hasActiveEntitlement){
  clientTab='internet';render();jawaliPhoneQuota();
  if(window.JawaliNative?.openHotspotLogin)JawaliNative.openHotspotLogin('http://172.16.0.1/login',liveUser.phone,'');
  return;
 }
"""
s=s[:start]+new+s[end:]
s=s.replace("const r=await call('/api/client/wifi-phone-login','POST',{phoneProfileId:id,deviceToken});","const r=await call('/api/client/wifi-phone-login','POST',{phoneProfileId:p.id,deviceToken});")
s=s.replace("if(r.ok!==true||!r.username||!r.hotspotLoginUrl)throw new Error('لم يؤكد الخادم تفعيل بروفايل الهاتف');","if(r.ok!==true||String(r.username)!==String(liveUser.phone)||!r.hotspotLoginUrl)throw new Error('لم يؤكد الخادم ربط بروفايل الهاتف بالرقم المسجل');")
s=s.replace("toast('جارٍ تفعيل البروفايل على User Manager؛ قد يستغرق الاتصال بعض الوقت');","toast('جارٍ ربط البروفايل برقم '+liveUser.phone+' عبر User Manager؛ يرجى عدم تكرار الطلب');")
s=s.replace("else toast('تم التفعيل؛ افتح صفحة الدخول الخاصة بالشبكة من الهاتف');","else toast('أكد الخادم تفعيل الباقة لرقم '+r.username+'؛ افتح صفحة الدخول الخاصة بالشبكة');")
s=s.replace("if(!p)return;\n if(busy)return toast('عملية تفعيل سابقة قيد التنفيذ');","if(!p)return;\n if(!token||!liveUser?.phone)return toast('سجّل الدخول بحساب العميل أولًا');\n if(busy)return toast('عملية تفعيل سابقة قيد التنفيذ');")
assert "Quota is advisory only" in s and "{phoneProfileId:p.id,deviceToken}" in s
p.write_text(s,encoding="utf-8")
g=root/"app/build.gradle"
s=g.read_text().replace('versionCode 3109; versionName "31.09"','versionCode 3110; versionName "31.10"')
assert 'versionName "31.10"' in s
g.write_text(s)
print("V31.10 activation patch installed")
