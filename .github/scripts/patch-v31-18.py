from pathlib import Path
r=Path('extracted/JawaliWallet_Android_V31_07')
p=r/'app/src/main/assets/jawali-live.js'
s=p.read_text(encoding='utf-8')
old="""// A captive Wi-Fi event only navigates to login. It never purchases a package.
window.jawaliOpenWifiFromSystem=function(){
 try{
  go('client');
  if(liveUser && typeof clientNavigate==='function') clientNavigate('internet');
  else status('اتصلت بشبكة Wi-Fi. سجّل الدخول إلى المحفظة لإكمال دخول الشبكة');
 }catch(e){console.warn('Wi-Fi navigation unavailable',e)}
};"""
assert old in s, 'WiFi hook missing'
new="""// Restore device-bound server session without storing customer passwords.
// This is the same /api/auth/device-session contract as Full-System.
let restoringDeviceSession=false, lastSessionAttempt=0;
window.jawaliOpenWifiFromSystem=async function(){
 if(restoringDeviceSession)return;
 try{
  if(token && liveUser && liveUser.phone){
   go('client');clientTab='internet';render();
   try{await jawaliPhoneQuota();}catch(e){status('تعذر تحديث الاستهلاك: '+errorText(e));}
   return;
  }
  const deviceToken=window.JawaliNative?.deviceToken?.()||'';
  if(deviceToken.length<16){go('client');status('تعذر التعرف على الجهاز؛ سجل الدخول إلى المحفظة مرة واحدة');return;}
  // Ignore duplicate callbacks for the same captive-portal event.
  if(Date.now()-lastSessionAttempt<7000)return;
  lastSessionAttempt=Date.now();
  restoringDeviceSession=true;
  go('client');render();
  status('جارٍ استعادة الحساب المرتبط بهذا الهاتف من الخادم…');
  await selectServer();
  const r=await call('/api/auth/device-session','POST',{
   deviceToken,deviceMac:window.JawaliNative?.deviceMac?.()||''
  });
  if(!r.token||!r.user?.phone)throw new Error('لم يؤكد الخادم ارتباط هذا الجهاز بحساب عميل');
  token=r.token;liveUser=r.user;activeClient=r.user.phone;clientSession=r.user.phone;
  // This read-only refresh never purchases, renews or activates a package.
  try{await refresh();}catch(e){console.warn('Read-only wallet refresh:',errorText(e));}
  restoringDeviceSession=false;
  clientTab='internet';go('client');render();
  try{await jawaliPhoneQuota();}catch(e){status('تم التعرف على الحساب، لكن تعذر جلب الاستهلاك: '+errorText(e));}
 }catch(e){
  token=null;liveUser=null;activeClient='';clientSession=null;
  restoringDeviceSession=false;go('client');render();
  const msg=e?.code==='DEVICE_NOT_LINKED'||e?.status===404?
   'هذا الجهاز غير مرتبط بحساب العميل بعد؛ سجل الدخول برقم الهاتف وكلمة المرور مرة واحدة فقط.':
   (e?.code==='DEVICE_MISMATCH'||e?.status===409?
     'الحساب مرتبط بجهاز آخر؛ اطلب من الإدارة مراجعة الارتباط.':
     'تعذر استعادة جلسة الهاتف: '+errorText(e));
  status(msg);
 }
};"""
s=s.replace(old,new)
needle="clientLoginView=function(){\n const reg=liveAuthMode==='register';"
assert needle in s
s=s.replace(needle,"clientLoginView=function(){\n if(restoringDeviceSession)return '<section class=\"lv-auth-shell\" dir=\"rtl\"><div class=\"lv-auth-hero\"><h1>جوالي محفظتي</h1><p>جارٍ التعرف على الهاتف وفتح استهلاك الباقة…</p></div><p class=\"lv-note\" id=\"live-status\" role=\"status\"></p></section>';\n const reg=liveAuthMode==='register';")
# variable lexical declaration must exist before scheduled invocation; declared above.
assert "call('/api/auth/device-session','POST'" in s
p.write_text(s,encoding='utf-8')

j=r/'app/src/main/java/com/jawali/wallet/MainActivity.java'
s=j.read_text(encoding='utf-8')
needle='  private boolean captiveObserved=false;'
assert needle in s
s=s.replace(needle,needle+'\n  private boolean webContentReady=false;\n  private boolean pendingWifiEntry=false;')
needle='''  private void showWifiSection(){
    if(web!=null)web.evaluateJavascript("if(window.jawaliOpenWifiFromSystem)jawaliOpenWifiFromSystem()",null);
  }'''
assert needle in s
s=s.replace(needle,'''  private void showWifiSection(){
    if(web==null || !webContentReady){pendingWifiEntry=true;return;}
    pendingWifiEntry=false;
    web.evaluateJavascript("if(window.jawaliOpenWifiFromSystem)jawaliOpenWifiFromSystem()",null);
  }''')
needle='''    web.setWebViewClient(new WebViewClient() {
      @Override public boolean shouldOverrideUrlLoading'''
assert needle in s
s=s.replace(needle,'''    web.setWebViewClient(new WebViewClient() {
      @Override public void onPageFinished(WebView view, String url){
        if(url!=null && url.startsWith("file:///android_asset/index.html")){
          webContentReady=true;
          if(pendingWifiEntry)showWifiSection();
        }
      }
      @Override public boolean shouldOverrideUrlLoading''')
needle='''    web.loadUrl("file:///android_asset/index.html");'''
assert needle in s
s=s.replace(needle,'''    pendingWifiEntry="com.jawali.wallet.OPEN_WIFI".equals(getIntent().getAction())
      || isSupportedEntryIntent(getIntent());
    web.loadUrl("file:///android_asset/index.html");''')
j.write_text(s,encoding='utf-8')
g=r/'app/build.gradle'
s=g.read_text(encoding='utf-8')
assert 'versionCode 3117; versionName "31.17"' in s
g.write_text(s.replace('versionCode 3117; versionName "31.17"','versionCode 3118; versionName "31.18"'),encoding='utf-8')
print('V31.18 device session recovery & quota entry ready')
