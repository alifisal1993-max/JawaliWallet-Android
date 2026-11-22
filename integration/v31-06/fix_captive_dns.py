from pathlib import Path
import sys
root=Path(sys.argv[1])
java=root/'app/src/main/java/com/jawali/wallet/MainActivity.java'
js=root/'app/src/main/assets/jawali-live.js'
j=java.read_text(encoding='utf-8')
s=js.read_text(encoding='utf-8')
assert 'final boolean[] authenticated={false};' in j
assert 'parent.addView(hotspot,new android.widget.FrameLayout.LayoutParams(2,2));' in j
# Real Hotspot profile has dns-name=a.com, so normal captive redirects are not 172.16.0.1-only.
# Restrict to the one configured captive DNS name and gateway, never arbitrary links.
old='''          return !("http".equalsIgnoreCase(target.getScheme())
            && "172.16.0.1".equals(target.getHost())
            && (target.getPort()==-1||target.getPort()==80));'''
new='''          String host=target.getHost();
          boolean trusted="172.16.0.1".equalsIgnoreCase(host)||"a.com".equalsIgnoreCase(host);
          if(!trusted)feedback.accept("failed","تحويل الدخول إلى نطاق غير معتمد: "+String.valueOf(host));
          return !("http".equalsIgnoreCase(target.getScheme())&&trusted
            && (target.getPort()==-1||target.getPort()==80));'''
assert j.count(old)==1
j=j.replace(old,new)
# Explicit request state must be visible immediately and indicate real load stages.
anchor='''        @Override public void onPageFinished(WebView view,String url){'''
before='''        @Override public void onPageStarted(WebView view,String url,android.graphics.Bitmap favicon){
          Uri location=Uri.parse(url);
          String host=location.getHost();
          if("172.16.0.1".equalsIgnoreCase(host)||"a.com".equalsIgnoreCase(host))
            feedback.accept("pending","جارٍ التواصل مع بوابة الشبكة: "+String.valueOf(location.getPath()));
        }
        @Override public void onReceivedHttpError(WebView view,WebResourceRequest request,android.webkit.WebResourceResponse response){
          if(request.isForMainFrame())feedback.accept("failed","أرجع الراوتر HTTP "+response.getStatusCode()+" أثناء تسجيل الدخول");
        }
'''
assert j.count(anchor)==1
j=j.replace(anchor,before+anchor)
j=j.replace('if(url.startsWith("http://172.16.0.1/status")){','''Uri current=Uri.parse(url);
          boolean portal="172.16.0.1".equalsIgnoreCase(current.getHost())||"a.com".equalsIgnoreCase(current.getHost());
          if(portal&&"/status".equals(current.getPath())){''',1)
j=j.replace('if(!url.startsWith("http://172.16.0.1/login")||attempted[0]||authenticated[0])return;','''if(!portal||!"/login".equals(current.getPath())||attempted[0]||authenticated[0])return;''',1)
# Response callback must not quietly leave the user with a timeout-only message.
j=j.replace('''if("true".equals(result)){
                  authenticated[0]=true;''','''if("true".equals(result)){
                  authenticated[0]=true;''',1)
j=j.replace('''feedback.accept("pending","لم يتم تأكيد جلسة Hotspot؛ تحقق من صفحة الدخول");''','''feedback.accept("failed","لم يؤكد الراوتر جلسة نشطة؛ راجع سبب رفض الدخول في السجلات");''',1)
j=j.replace('''feedback.accept("failed","تعذر الوصول إلى الراوتر؛ تأكد من اتصال Wi-Fi المحلي");''','''feedback.accept("failed","تعذر فتح بوابة الشبكة: "+String.valueOf(error.getDescription())+" (رمز "+error.getErrorCode()+")");''',1)
# Ensure form has real layout and is behind the main wallet screen (not 2x2 viewport).
j=j.replace('''      parent.addView(hotspot,new android.widget.FrameLayout.LayoutParams(2,2));''','''      hotspot.setFocusable(false);
      parent.addView(hotspot,0,new android.widget.FrameLayout.LayoutParams(
        android.widget.FrameLayout.LayoutParams.MATCH_PARENT,
        android.widget.FrameLayout.LayoutParams.MATCH_PARENT));''',1)
# Simplify late timeout message, do not hide an earlier actionable failure.
j=j.replace('''      hotspot.postDelayed(()->{
        if(!authenticated[0]){
          feedback.accept("pending","لم يتأكد اتصال Hotspot بعد؛ افحص جلسة الهاتف في WinBox");
        }
      },15000);''','''      hotspot.postDelayed(()->{
        if(!authenticated[0]&&!attempted[0]){
          feedback.accept("failed","لم يظهر نموذج دخول Hotspot. تحقق من اتصال الهاتف بـ Wi-Fi ومن اسم DNS الخاص بالراوتر");
        }
      },15000);''',1)
# Expose immediate feedback when the user taps the action.
old='''window.jawaliReopenHotspot=()=>{if(!liveUser?.phone)return toast('سجّل الدخول أولًا');if(window.JawaliNative?.openHotspotLogin)JawaliNative.openHotspotLogin('http://172.16.0.1/login',liveUser.phone,'');else toast('افتح صفحة Hotspot من شبكة الراوتر')};'''
new='''window.jawaliReopenHotspot=()=>{
 if(!liveUser?.phone)return toast('سجّل الدخول أولًا');
 const el=document.getElementById('jw-hotspot-state');
 if(el){el.textContent='جارٍ فتح اتصال الشبكة عبر جوالي محفظتي…';el.dataset.connection='pending'}
 if(window.JawaliNative?.openHotspotLogin){
  JawaliNative.openHotspotLogin('http://172.16.0.1/login',liveUser.phone,'');
 }else{
  if(el)el.textContent='تعذر بدء الاتصال: مكوّن Android غير متاح';
  toast('مكوّن الاتصال بالشبكة غير متاح');
 }
};'''
assert s.count(old)==1
s=s.replace(old,new)
# Don't override native actionable error with generic stale status.
# The previous callback already updates the ui for individual router stages.
java.write_text(j,encoding='utf-8')
js.write_text(s,encoding='utf-8')
build=root/'app/build.gradle'
b=build.read_text(encoding='utf-8')
assert 'versionCode 3105; versionName "31.05"' in b
build.write_text(b.replace('versionCode 3105; versionName "31.05"','versionCode 3106; versionName "31.06"'),encoding='utf-8')
print('V31.06: safe captive DNS redirects, full viewport hidden webview, immediate actionable diagnostics')
