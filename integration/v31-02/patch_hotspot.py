from pathlib import Path
import sys
root=Path(sys.argv[1])
js=root/'app/src/main/assets/jawali-live.js'
java=root/'app/src/main/java/com/jawali/wallet/MainActivity.java'
manifest=root/'app/src/main/AndroidManifest.xml'
s=js.read_text(encoding='utf-8')
src="const timeout=setTimeout(()=>{inflight.delete(id);reject(new Error('انتهت مهلة الاتصال بالخادم؛ تحقق من سجل العمليات قبل إعادة أي دفع'))},25000);"
dst="const timeout=setTimeout(()=>{inflight.delete(id);reject(new Error('انتهت مهلة الاتصال بالخادم؛ تحقق من حالة الباقة وكشف العمليات قبل إعادة الشراء'))},path==='/api/client/wifi-phone-login'?95000:25000);"
assert s.count(src)==1
s=s.replace(src,dst)
start=s.index('window.jawaliActivateProfile=')
end=s.index('\n',start)
old=s[start:end]
assert "write('/api/client/wifi-phone-login'" in old
new="""window.jawaliActivateProfile=async id=>{
 const p=(liveData.profiles?.profiles||[]).find(x=>x.id===id);
 if(!p)return;
 if(busy)return toast('عملية تفعيل سابقة قيد التنفيذ');
 const deviceToken=window.JawaliNative?.deviceToken?.();
 if(!deviceToken)return toast('تعذّر التعرف على الجهاز');
 if(!confirm('شراء وتفعيل '+p.name+' برقم هاتفك مقابل '+rial(p.price)+'؟\\nسيتم الخصم من المحفظة عند نجاح التفعيل.'))return;
 busy=true;
 try{
  toast('جارٍ تفعيل البروفايل على User Manager؛ قد يستغرق الاتصال بعض الوقت');
  const r=await call('/api/client/wifi-phone-login','POST',{phoneProfileId:id,deviceToken});
  if(r.ok!==true||!r.username||!r.hotspotLoginUrl)throw new Error('لم يؤكد الخادم تفعيل بروفايل الهاتف');
  await refresh().catch(()=>{});
  render();
  toast('تم تفعيل الباقة على رقم هاتفك؛ سيتم فتح صفحة دخول الشبكة');
  if(window.JawaliNative?.openHotspotLogin)JawaliNative.openHotspotLogin(r.hotspotLoginUrl,r.username,r.password||'');
  else toast('تم التفعيل؛ افتح صفحة الدخول الخاصة بالشبكة من الهاتف');
 }catch(e){
  const timed=/مهلة|timeout|timed out/i.test(errorText(e));
  toast(timed?'لم يتضح مصير طلب التفعيل؛ تحقق من استهلاك بروفايل الهاتف وكشف العمليات قبل شراء الباقة مجددًا':errorText(e));
 }finally{busy=false;}
};"""
s=s[:start]+new+s[end:]
# Enable reopening Hotspot with user phone only on explicit tap; no unverified auto-login.
old="<button class=\"lv-action\" onclick=\"jawaliPhoneQuota()\">عرض رصيد باقة الهاتف واستهلاكها</button>"
newbtn=old+"<button class=\"lv-action\" onclick=\"jawaliReopenHotspot()\">فتح صفحة دخول الشبكة</button>"
assert old in s;s=s.replace(old,newbtn)
anchor="window.jawaliPhoneQuota="
assert anchor in s
s=s.replace(anchor,"""window.jawaliReopenHotspot=()=>{if(!liveUser?.phone)return toast('سجّل الدخول أولًا');if(window.JawaliNative?.openHotspotLogin)JawaliNative.openHotspotLogin('http://172.16.0.1/login',liveUser.phone,'');else toast('افتح صفحة Hotspot من شبكة الراوتر')};
"""+anchor,1)
js.write_text(s,encoding='utf-8')
j=java.read_text(encoding='utf-8')
j=j.replace('import android.app.Activity;','import android.app.Activity;\nimport android.app.Dialog;\nimport android.view.Window;\nimport android.view.WindowManager;\nimport android.webkit.WebResourceError;\nimport android.webkit.WebResourceRequest;')
# Phone profile activation can take longer than standard read (UM synchronisation).
j=j.replace('connection.setConnectTimeout(12000);connection.setReadTimeout(15000);',
"""connection.setConnectTimeout(15000);
          connection.setReadTimeout("/api/client/wifi-phone-login".equals(url.getPath())?80000:15000);""")
anchor='    @JavascriptInterface public void requestBiometric() {'
assert anchor in j
j=j.replace(anchor,"""    @JavascriptInterface public void openHotspotLogin(String loginUrl,String username,String password){
      runOnUiThread(()->showHotspotLogin(loginUrl,username,password));
    }

"""+anchor)
anchor='  private void biometricResult(boolean ok) {'
assert anchor in j
bridge="""  private void showHotspotLogin(String urlText,String username,String password){
    try{
      Uri uri=Uri.parse(urlText);
      if(!"http".equalsIgnoreCase(uri.getScheme()) || !"172.16.0.1".equals(uri.getHost())
          || (uri.getPort()!=-1 && uri.getPort()!=80)
          || !"/login".equals(uri.getPath()) || uri.getUserInfo()!=null){
        Toast.makeText(this,"عنوان Hotspot غير معتمد",Toast.LENGTH_LONG).show();return;
      }
      Dialog dialog=new Dialog(this);
      WebView hotspot=new WebView(this);
      hotspot.getSettings().setJavaScriptEnabled(true);
      hotspot.getSettings().setDomStorageEnabled(true);
      hotspot.getSettings().setAllowFileAccess(false);
      hotspot.getSettings().setAllowContentAccess(false);
      hotspot.getSettings().setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
      final boolean[] attempted={false};
      hotspot.setWebViewClient(new WebViewClient(){
        @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){
          Uri d=request.getUrl();
          if("172.16.0.1".equals(d.getHost())&&"http".equals(d.getScheme()))return false;
          return true;
        }
        @Override public void onPageFinished(WebView view,String url){
          if(!url.startsWith("http://172.16.0.1/login")||attempted[0])return;
          attempted[0]=true;
          String script="(function(){try{"+
            "var u=document.querySelector('input[name=username]');"+
            "var p=document.querySelector('input[name=password]');"+
            "if(!u)return 'FORM_NOT_FOUND';"+
            "u.value="+JSONObject.quote(username)+";"+
            "if(p)p.value="+JSONObject.quote(password)+";"+
            "var f=u.form||document.querySelector('form[name=login]');"+
            "if(!f)return 'FORM_NOT_FOUND';"+
            "if(typeof window.doLogin==='function'){window.doLogin();return 'CHAP_ATTEMPTED'}"+
            "var btn=f.querySelector('button[type=submit],input[type=submit]');"+
            "if(btn)btn.click();else if(typeof f.requestSubmit==='function')f.requestSubmit();else f.submit();"+
            "return 'LOGIN_SUBMITTED';"+
            "}catch(e){return 'FORM_ERROR'}})()";
          view.evaluateJavascript(script,null);
        }
        @Override public void onReceivedError(WebView view,WebResourceRequest request,WebResourceError error){
          if(request.isForMainFrame())Toast.makeText(MainActivity.this,"اتصل أولاً بشبكة MikroTik ثم أعد المحاولة",Toast.LENGTH_LONG).show();
        }
      });
      dialog.setContentView(hotspot);
      Window w=dialog.getWindow();if(w!=null)w.setLayout(WindowManager.LayoutParams.MATCH_PARENT,WindowManager.LayoutParams.MATCH_PARENT);
      dialog.setOnDismissListener(d->hotspot.destroy());
      dialog.show();
      if(dialog.getWindow()!=null)dialog.getWindow().setLayout(WindowManager.LayoutParams.MATCH_PARENT,WindowManager.LayoutParams.MATCH_PARENT);
      hotspot.loadUrl("http://172.16.0.1/login");
    }catch(Exception e){Toast.makeText(this,"تعذر فتح صفحة الدخول: "+e.getMessage(),Toast.LENGTH_LONG).show();}
  }
"""
j=j.replace(anchor,bridge+anchor)
java.write_text(j,encoding='utf-8')
m=manifest.read_text(encoding='utf-8')
assert 'android:usesCleartextTraffic="false"' in m
m=m.replace('android:usesCleartextTraffic="false"','android:usesCleartextTraffic="false" android:networkSecurityConfig="@xml/network_security_config"')
manifest.write_text(m,encoding='utf-8')
folder=root/'app/src/main/res/xml';folder.mkdir(parents=True,exist_ok=True)
(folder/'network_security_config.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
 <base-config cleartextTrafficPermitted="false"/>
 <domain-config cleartextTrafficPermitted="true"><domain>172.16.0.1</domain></domain-config>
</network-security-config>''',encoding='utf-8')
print('V31.02: extend UM timeout, no retry on ambiguous payment, open trusted hotspot inside app with auto-prefill & submit.')
