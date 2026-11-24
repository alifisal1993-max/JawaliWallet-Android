from pathlib import Path
r=Path('extracted/JawaliWallet_Android_V31_07')
p=r/'app/src/main/assets/jawali-live.js'
s=p.read_text(encoding='utf-8')
a=s.index('let restoringDeviceSession=false, lastSessionAttempt=0;')
b=s.index(chr(10)+'})();',a)
new=r"""// The Android device token is stable across Wi-Fi MAC randomization.
// Only the wallet server may identify the linked phone. MAC is advisory, never
// an identity key or a reason to create a fresh wallet or purchase.
let restoringDeviceSession=false, lastSessionAttempt=0, lastHotspotAttempt=0;
async function walletWifiEntry(shouldAuthenticate){
 if(restoringDeviceSession)return;
 if(Date.now()-lastSessionAttempt<5000 && !liveUser)return;
 lastSessionAttempt=Date.now();
 restoringDeviceSession=true;
 try{
  const deviceToken=window.JawaliNative?.deviceToken?.()||'';
  if(deviceToken.length<16)throw Object.assign(new Error('تعذّر التعرف على الهاتف؛ سجّل الدخول مرة واحدة لربط الجهاز'),{code:'DEVICE_TOKEN_REQUIRED'});
  go('client');
  status('جارٍ التحقق من حساب هذا الهاتف وباقته…');
  if(!token||!liveUser?.phone){
   await selectServer();
   const session=await call('/api/auth/device-session','POST',{
    deviceToken,deviceMac:window.JawaliNative?.deviceMac?.()||''
   });
   if(!session.token||!session.user?.phone)throw new Error('الخادم لم يؤكد ربط هذا الجهاز برقم الهاتف');
   token=session.token;liveUser=session.user;
   activeClient=String(liveUser.phone);clientSession=String(liveUser.phone);
  }
  // Show the quota before doing any Hotspot work; no financial operation here.
  clientTab='internet';render();
  try{await refresh();clientTab='internet';render()}catch(e){
   status('تم تحديد حساب الهاتف. تعذّر تحديث إحدى خدمات المحفظة: '+errorText(e));
  }
  let quota=null;
  try{
   const response=await call('/api/client/wifi-phone-quota');
   if(String(response.phone||'')!==String(liveUser.phone))
    throw new Error('بيانات الباقة لا تخص رقم الهاتف المرتبط بالجهاز');
   quota=response.quota||{};
   await jawaliPhoneQuota();
  }catch(e){
   status('تم التعرف على الهاتف، لكن لم تتوفر قراءة مؤكدة للباقة: '+errorText(e));
  }
  const entitlement=quota&&!!quota.entitlementId;
  const seconds=quota?.remainingSeconds;
  const bytes=quota?.remainingBytes;
  const usable=entitlement &&
   (seconds==null || (Number.isFinite(Number(seconds)) && Number(seconds)>0)) &&
   (bytes==null || (Number.isFinite(Number(bytes)) && Number(bytes)>0));
  if(!usable){
   status(entitlement?'الباقة الحالية منتهية؛ لن يُرسل طلب دخول تلقائي':'لا توجد باقة نشطة مؤكدة. يمكن عرض الباقات دون شراء تلقائي');
   return;
  }
  // A changed randomized MAC creates a NEW MikroTik Hotspot host. A session
  // read from User Manager doesn't authorize that new MAC: router PAP login
  // is needed once more. This is not a wallet login and never buys a package.
  if(shouldAuthenticate && window.JawaliNative?.openHotspotLogin &&
     Date.now()-lastHotspotAttempt>30000){
   lastHotspotAttempt=Date.now();
   status('الباقة نشطة لهذا الرقم. جارٍ التحقق من جلسة MikroTik وإعادة الدخول عند الحاجة دون كلمة مرور المحفظة');
   JawaliNative.openHotspotLogin('http://172.16.0.1/login',String(liveUser.phone),'');
  }else{
   status('تم فتح باقة الهاتف واستهلاكها؛ لا حاجة لتسجيل دخول جديد إلى المحفظة');
  }
 }catch(e){
  const code=e?.code||'';
  // Never silently rebind a different device. Admin intervention is required
  // if a reinstall erased the device token while the server retains old hash.
  if(code==='DEVICE_NOT_LINKED'||code==='DEVICE_MISMATCH'||e?.status===404||e?.status===409){
   status('تعذّر استعادة الحساب المربوط بهذا الجهاز. إن حُذف التطبيق وأُعيد تثبيته، يلزم مراجعة الإدارة لإعادة ربطه بأمان، ثم تسجيل الدخول مرة واحدة.');
  }else{
   status('تعذّر استعادة اتصال الهاتف: '+errorText(e));
  }
  if(!liveUser){go('client');render();}
 }finally{restoringDeviceSession=false;}
}
window.jawaliOpenWifiFromSystem=()=>walletWifiEntry(true);
// Expose an explicit manual retry that NEVER purchases or renews a package.
window.jawaliResumeWifi=()=>walletWifiEntry(true);
"""
s=s[:a]+new+s[b:]
assert 'window.jawaliOpenWifiFromSystem=()=>walletWifiEntry(true)' in s
p.write_text(s,encoding='utf-8')

j=r/'app/src/main/java/com/jawali/wallet/MainActivity.java'
s=j.read_text(encoding='utf-8')
old='connectivity.registerDefaultNetworkCallback(wifiCallback);'
assert old in s
s=s.replace(old,'''// Captive Wi-Fi may not be Android's default network when mobile data is on.
    android.net.NetworkRequest request=new android.net.NetworkRequest.Builder()
      .addTransportType(NetworkCapabilities.TRANSPORT_WIFI).build();
    connectivity.registerNetworkCallback(request,wifiCallback);''')
# Ensure pending login survives cold launch and page rendering without starting
# the same process multiple times on simple activity resumption.
needle='  @Override protected void onResume(){super.onResume();foreground=true;}'
assert needle in s
s=s.replace(needle,'''  @Override protected void onResume(){
    super.onResume();foreground=true;
    if(pendingWifiEntry)showWifiSection();
  }''')
j.write_text(s,encoding='utf-8')

m=r/'app/src/main/AndroidManifest.xml'
s=m.read_text(encoding='utf-8')
# Other login URLs encountered on the router: never claim arbitrary HTTPS URLs.
needle='<data android:scheme="http" android:host="172.16.0.1" android:path="/login/"/>'
assert needle in s
s=s.replace(needle,needle+'''
        <data android:scheme="http" android:host="172.16.0.1" android:path="/login.html"/>''')
needle='<data android:scheme="http" android:host="a.com" android:path="/login/"/>'
assert needle in s
s=s.replace(needle,needle+'''
        <data android:scheme="http" android:host="a.com" android:path="/index.html/"/>''')
m.write_text(s,encoding='utf-8')
g=r/'app/build.gradle'
s=g.read_text(encoding='utf-8')
assert 'versionCode 3118; versionName "31.18"' in s
g.write_text(s.replace('versionCode 3118; versionName "31.18"','versionCode 3119; versionName "31.19"'),encoding='utf-8')
print('V31.19 MAC-independent device session and Hotspot reauth ready')
