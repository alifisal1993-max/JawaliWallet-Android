from pathlib import Path
import sys
root=Path(sys.argv[1])
js=root/'app/src/main/assets/jawali-live.js'
s=js.read_text(encoding='utf-8')
original="if(!confirm('شراء وتفعيل '+p.name+' برقم هاتفك مقابل '+rial(p.price)+'؟\\nسيتم الخصم من المحفظة عند نجاح التفعيل.'))return;"
replacement="""let preflight;
 try {
  preflight=await call('/api/client/wifi-phone-quota');
 } catch (err) {
  const msg=errorText(err);
  if(!confirm('تعذّر التحقق من حالة بروفايل الهاتف على User Manager: '+msg+
    '\\\\nقد يكون هناك تفعيل سابق لم يكتمل إشعاره. لن تتم إعادة الشراء تلقائيًا. هل تريد متابعة مراجعة الطلب فقط؟'))return;
  toast('تحقق من حالة الباقة عبر الإدارة قبل أي شراء جديد');return;
 }
 const q=preflight?.quota||{};
 const matches=String(q.packageName||q.profile||'').trim()===String(p.name).trim();
 const remaining=q.remainingSeconds===null||q.remainingSeconds===undefined?null:Number(q.remainingSeconds);
 const entitlement=q.entitlementId&&matches&&(remaining===null||remaining>0);
 if(entitlement){
   toast('الباقة مرتبطة بالفعل برقم هاتفك. سيتم فتح دخول الشبكة دون خصم جديد');
   if(window.JawaliNative?.openHotspotLogin)JawaliNative.openHotspotLogin('http://172.16.0.1/login',liveUser.phone,'');
   return;
 }
 if(!confirm('شراء وتفعيل '+p.name+' برقم هاتفك مقابل '+rial(p.price)+'؟\\nسيتم الخصم من المحفظة عند نجاح التفعيل.'))return;"""
if s.count(original)!=1:raise SystemExit('Expected one profile confirm, found '+str(s.count(original)))
s=s.replace(original,replacement,1)
# Status check is read-only; exposes precise entitlement details, never charges on status view.
anchor="window.jawaliPhoneQuota=async()=>"
check="""window.jawaliCheckPhoneActivation=async()=>{
 if(!token||!liveUser)return toast('سجل الدخول أولًا');
 try{
  toast('جارٍ التحقق من ربط الباقة برقم الهاتف');
  const r=await call('/api/client/wifi-phone-quota');
  const q=r.quota||{};
  if(!q.entitlementId)return toast('لا يوجد تأكيد بباقة هاتف نشطة. تحقق من الإدارة قبل إعادة الشراء');
  const remaining=q.remainingSeconds==null?'غير محدد':Math.ceil(Number(q.remainingSeconds)/60)+' دقيقة';
  const el=document.getElementById('jw-phone-quota');
  const msg='الباقة المرتبطة برقم '+liveUser.phone+': '+(q.packageName||q.profile||'غير محددة')+' — الوقت المتبقي: '+remaining;
  if(el)el.textContent=msg;
  toast('تم العثور على باقة مرتبطة بهاتفك. استخدم زر دخول الشبكة دون شراء');
 }catch(err){toast('تعذر تأكيد تفعيل الباقة: '+errorText(err))}
};
"""
assert s.count(anchor)==1
s=s.replace(anchor,check+anchor,1)
old='<button class="lv-action" onclick="jawaliPhoneQuota()">عرض رصيد باقة الهاتف واستهلاكها</button>'
new='<button class="lv-action" onclick="jawaliCheckPhoneActivation()">التحقق من ربط الباقة برقم الهاتف</button>'+old
assert s.count(old)==1
s=s.replace(old,new,1)
assert 'jawaliCheckPhoneActivation' in s
js.write_text(s,encoding='utf-8')
build=root/'app/build.gradle'
b=build.read_text(encoding='utf-8')
assert 'versionCode 3102; versionName "31.02"' in b
build.write_text(b.replace('versionCode 3102; versionName "31.02"','versionCode 3103; versionName "31.03"'),encoding='utf-8')
print('V31.03: preflight checks active phone entitlement; prevents repeated purchase of existing profile.')
