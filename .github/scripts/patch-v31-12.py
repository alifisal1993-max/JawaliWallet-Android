from pathlib import Path
root=Path('extracted/JawaliWallet_Android_V31_07')
p=root/'app/src/main/assets/jawali-live.js'
s=p.read_text(encoding='utf-8')
a=s.index('window.jawaliActivateProfile=async id=>{')
b=s.index('window.jawaliTransfer=',a)
new="""// Full-System: server-side profile assignment and refund are authoritative.
window.jawaliActivateProfile=async id=>{
 const p=(liveData.profiles?.profiles||[]).find(x=>x.id===id);
 if(!p)return toast('لم يتم العثور على الباقة. حدّث قائمة بروفايلات الهاتف');
 if(!token||!liveUser?.phone)return toast('سجّل الدخول بحساب العميل أولًا');
 if(busy)return toast('عملية أخرى قيد التنفيذ');
 const balance=Number(liveData.wallet?.balance);
 if(Number.isFinite(balance)&&balance<Number(p.price))return toast('رصيد المحفظة غير كافٍ لشراء هذه الباقة');
 const deviceToken=window.JawaliNative?.deviceToken?.()||'';
 const deviceMac=window.JawaliNative?.deviceMac?.()||'';
 if(deviceToken.length<16)return toast('تعذّر التعرف على الجهاز المرتبط برقم الهاتف');
 if(!confirm('شراء وتفعيل بروفايل '+p.name+' لرقم '+liveUser.phone+' بسعر '+rial(p.price)+'؟'))return;
 busy=true;
 try{
  status('جارٍ تفعيل باقة '+p.name+' لرقم '+liveUser.phone+' عبر خادم المحفظة…');
  const d=await call('/api/client/wifi-phone-login','POST',{phoneProfileId:p.id,deviceToken,deviceMac});
  if(d.ok!==true||!d.username||String(d.username)!==String(liveUser.phone)||!d.hotspotLoginUrl)
   throw new Error('لم يؤكد الخادم ربط الباقة بالرقم المسجل؛ افحص كشف العمليات قبل إعادة الطلب');
  if(Number.isFinite(Number(d.balance))){liveData.wallet=liveData.wallet||{};liveData.wallet.balance=Number(d.balance);}
  status('تم تفعيل '+(d.packageName||p.name)+' لرقم '+d.username+' في User Manager؛ جاري التحقق من الاستهلاك');
  clientTab='internet';render();
  try{await jawaliPhoneQuota()}catch(e){status('تم تأكيد التفعيل؛ تعذر تحميل الاستهلاك: '+errorText(e))}
  if(window.JawaliNative?.openHotspotLogin)
   JawaliNative.openHotspotLogin(d.hotspotLoginUrl,d.username,d.password||'');
  else toast('تم التفعيل في User Manager؛ تعذر بدء دخول Hotspot داخل التطبيق');
 }catch(e){
  const msg=errorText(e);
  status('تعذر تأكيد تفعيل الباقة: '+msg);
  toast('لم يُؤكد التفعيل: '+msg+' — افحص الرصيد والاستهلاك قبل أي محاولة ثانية');
 }finally{busy=false;}
};
"""
s=s[:a]+new+s[b:]
s=s.replace("{phone,password,deviceToken});if(!r.token", "{phone,password,deviceToken,deviceMac:window.JawaliNative?.deviceMac?.()||''});if(!r.token")
s=s.replace("{name,phone,email,password,deviceToken});","{name,phone,email,password,deviceToken,deviceMac:window.JawaliNative?.deviceMac?.()||''});")
assert "{phoneProfileId:p.id,deviceToken,deviceMac}" in s
assert "call('/api/client/wifi-phone-quota')" in s
p.write_text(s,encoding='utf-8')
g=root/'app/build.gradle'
s=g.read_text().replace('versionCode 3111; versionName "31.11"','versionCode 3112; versionName "31.12"')
assert 'versionName "31.12"' in s
g.write_text(s)
print('V31.12 full-system contract patch applied')
