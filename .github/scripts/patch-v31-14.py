from pathlib import Path
root=Path('extracted/JawaliWallet_Android_V31_07')
p=root/'app/src/main/java/com/jawali/wallet/MainActivity.java'
s=p.read_text(encoding='utf-8')
s=s.replace('final boolean[] authenticated={false};','final boolean[] authenticated={false};\n      final boolean[] initialStatusCheck={true};')
needle='''          if(portal&&"/status".equals(current.getPath())){
            // Check the response itself before showing "connected" in the wallet.
            view.evaluateJavascript("(function(){return !!(document.querySelector('a[href*=logout],form[action*=logout]')||document.body.textContent.includes('session-time-left'));})()",
              result->{
                if("true".equals(result)){
                  authenticated[0]=true;
                  feedback.accept("connected","تم تسجيل دخول الهاتف؛ صفحة استهلاك المحفظة جاهزة");
                }else feedback.accept("failed","لم يؤكد الراوتر جلسة نشطة؛ راجع سبب رفض الدخول في السجلات");
              });
            return;
          }
          if(!portal||attempted[0]||authenticated[0])return;'''
replacement='''          if(portal&&"/status".equals(current.getPath())){
            // A real status response for THIS phone is required. An HTTP 200,
            // portal redirect, or a session belonging to another user isn't enough.
            String check="(function(){var body=document.body?document.body.innerText:'';"+
              "var active=!!document.querySelector('a[href*=logout],form[action*=logout]');"+
              "return active&&body.includes("+jsUsername+");})()";
            view.evaluateJavascript(check,result->{
              if("true".equals(result)){
                authenticated[0]=true;
                feedback.accept("connected","جلسة Hotspot نشطة لرقم الهاتف؛ لا حاجة لتسجيل دخول جديد. تحقق من اتصال الإنترنت بصورة منفصلة");
              }else if(initialStatusCheck[0]&&!attempted[0]){
                initialStatusCheck[0]=false;
                feedback.accept("pending","لا توجد جلسة مؤكدة لهذا الرقم؛ جارٍ فتح صفحة دخول الشبكة مرة واحدة");
                view.loadUrl("http://172.16.0.1/login");
              }else feedback.accept("failed","لم يؤكد الراوتر جلسة نشطة لهذا الرقم؛ تحقق من صفحة حالة Hotspot");
            });
            return;
          }
          if(!portal||attempted[0]||authenticated[0])return;
          initialStatusCheck[0]=false;'''
assert needle in s, 'status block missing'
s=s.replace(needle,replacement)
assert 'hotspot.loadUrl("http://172.16.0.1/login");' in s
s=s.replace('hotspot.loadUrl("http://172.16.0.1/login");','''// Probe existing MikroTik session first; never POST credentials if already active.
      hotspot.loadUrl("http://172.16.0.1/status");''')
p.write_text(s,encoding='utf-8')
g=root/'app/build.gradle'
s=g.read_text().replace('versionCode 3113; versionName "31.13"','versionCode 3114; versionName "31.14"')
assert 'versionName "31.14"' in s
g.write_text(s)
print('V31.14 Hotspot status-first patch applied')
