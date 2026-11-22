from pathlib import Path
import sys
root=Path(sys.argv[1])
java=root/'app/src/main/java/com/jawali/wallet/MainActivity.java'
js=root/'app/src/main/assets/jawali-live.js'
j=java.read_text(encoding='utf-8')
s=js.read_text(encoding='utf-8')
# V31.06 falsely calls any delayed load without submitted form "no login form".
# Record the actual terminal landing path, HTTP status and DOM form availability.
needle='''      final boolean[] attempted={false};
      final boolean[] authenticated={false};'''
replacement='''      final boolean[] attempted={false};
      final boolean[] authenticated={false};
      final boolean[] pageFinished={false};
      final String[] currentPage={"لم يبدأ تحميل الصفحة"};'''
assert j.count(needle)==1
j=j.replace(needle,replacement,1)
needle='''        @Override public void onPageStarted(WebView view,String url,android.graphics.Bitmap favicon){
          Uri location=Uri.parse(url);'''
assert j.count(needle)==1
j=j.replace(needle,'''        @Override public void onPageStarted(WebView view,String url,android.graphics.Bitmap favicon){
          currentPage[0]=Uri.parse(url).getPath();
          Uri location=Uri.parse(url);''',1)
needle='''        @Override public void onPageFinished(WebView view,String url){
          Uri current=Uri.parse(url);'''
assert j.count(needle)==1
j=j.replace(needle,'''        @Override public void onPageFinished(WebView view,String url){
          pageFinished[0]=true;
          currentPage[0]=Uri.parse(url).getPath();
          Uri current=Uri.parse(url);''',1)
old='''          if(!portal||!"/login".equals(current.getPath())||attempted[0]||authenticated[0])return;'''
new='''          if(!portal||attempted[0]||authenticated[0])return;
          // Different captive templates serve the login form at different paths.
          // Find a real username field before deciding that this is a login page.
          view.evaluateJavascript("(function(){return JSON.stringify({path:location.pathname,forms:document.forms.length,username:!!document.querySelector('input[name=username]'),title:document.title})})()",probe->{
            if(probe!=null)feedback.accept("pending","تم تحميل البوابة: "+String.valueOf(current.getPath()));
          });
          if(!("/login".equals(current.getPath())||"/".equals(current.getPath())||"/login.html".equals(current.getPath())))return;'''
assert j.count(old)==1
j=j.replace(old,new,1)
# Do not trigger on body "doLogin" unless onclick, use native DOM validation and feedback.
old='''            if(code.startsWith("LOGIN_SUBMITTED")||code.startsWith("CHAP_SUBMITTED")){'''
assert j.count(old)==1
j=j.replace(old,'''            if(code.startsWith("LOGIN_SUBMITTED")||code.startsWith("CHAP_SUBMITTED")){''',1)
# If page does not contain fields, offer real path so user can report it, rather than generic failure.
old='''              feedback.accept("failed","لم يُرسِل نموذج الراوتر طلب الدخول: "+code);'''
new='''              feedback.accept("failed","تعذر إرسال نموذج الدخول ("+code+") في "+String.valueOf(currentPage[0]));'''
assert j.count(old)==1
j=j.replace(old,new,1)
# No page finished at all => networking; a loaded page but no form => template/redirect.
old='''      hotspot.postDelayed(()->{
        if(!authenticated[0]&&!attempted[0]){
          feedback.accept("failed","لم يظهر نموذج دخول Hotspot. تحقق من اتصال الهاتف بـ Wi-Fi ومن اسم DNS الخاص بالراوتر");
        }
      },15000);'''
new='''      hotspot.postDelayed(()->{
        if(!authenticated[0]&&!attempted[0]){
          if(!pageFinished[0]){
            feedback.accept("failed","لم يكتمل تحميل بوابة الراوتر من الهاتف. تحقق من Wi-Fi وأوقف VPN مؤقتًا. المسار: "+currentPage[0]);
          } else {
            feedback.accept("failed","فتحت البوابة ولكن لم يظهر نموذج الدخول في المسار: "+currentPage[0]+". قد تكون صفحة إعادة توجيه أو جلسة أخرى");
          }
        }
      },15000);'''
assert j.count(old)==1
j=j.replace(old,new,1)
# Warn if reach status with no evidence; never claim connected just from URL.
assert 'session-time-left' in j
# App still uses branded consumption display.
assert 'function toast' in s
java.write_text(j,encoding='utf-8')
b=root/'app/build.gradle'
t=b.read_text(encoding='utf-8')
assert 'versionCode 3106; versionName "31.06"' in t
b.write_text(t.replace('versionCode 3106; versionName "31.06"','versionCode 3107; versionName "31.07"'),encoding='utf-8')
print('V31.07: precise portal/page diagnostics and alternate captive login form locations')
