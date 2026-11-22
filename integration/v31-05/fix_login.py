from pathlib import Path
import sys
root=Path(sys.argv[1])
java=root/'app/src/main/java/com/jawali/wallet/MainActivity.java'
js=root/'app/src/main/assets/jawali-live.js'
j=java.read_text(encoding='utf-8')
s=js.read_text(encoding='utf-8')
start=j.index('      final boolean[] attempted={false};')
end=j.index('      hotspot.loadUrl("http://172.16.0.1/login");',start)
replacement=r'''      final boolean[] attempted={false};
      final boolean[] authenticated={false};
      final android.widget.FrameLayout parent=(android.widget.FrameLayout)web.getParent();
      final String jsUsername=JSONObject.quote(username);
      final String jsPassword=JSONObject.quote(password);
      java.util.function.BiConsumer<String,String> feedback=(state,message)->{
        final String script="window.jawaliHotspotState&&window.jawaliHotspotState("+JSONObject.quote(state)+","+JSONObject.quote(message)+")";
        web.evaluateJavascript(script,null);
      };
      hotspot.setWebViewClient(new WebViewClient(){
        @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){
          Uri target=request.getUrl();
          return !("http".equalsIgnoreCase(target.getScheme())
            && "172.16.0.1".equals(target.getHost())
            && (target.getPort()==-1||target.getPort()==80));
        }
        @Override public void onPageFinished(WebView view,String url){
          if(url.startsWith("http://172.16.0.1/status")){
            // Check the response itself before showing "connected" in the wallet.
            view.evaluateJavascript("(function(){return !!(document.querySelector('a[href*=logout],form[action*=logout]')||document.body.textContent.includes('session-time-left'));})()",
              result->{
                if("true".equals(result)){
                  authenticated[0]=true;
                  feedback.accept("connected","تم تسجيل دخول الهاتف؛ صفحة استهلاك المحفظة جاهزة");
                }else feedback.accept("pending","لم يتم تأكيد جلسة Hotspot؛ تحقق من صفحة الدخول");
              });
            return;
          }
          if(!url.startsWith("http://172.16.0.1/login")||attempted[0]||authenticated[0])return;
          attempted[0]=true;
          feedback.accept("pending","تم الوصول إلى الراوتر؛ جارٍ إرسال بيانات الهاتف");
          // Submit the actual form. requestSubmit/click triggers the router's own
          // onsubmit handler (including CHAP if configured), unlike form.submit().
          String script="(function(){try{"+
            "var u=document.querySelector('input[name=username]');"+
            "var p=document.querySelector('input[name=password]');"+
            "if(!u)return 'FORM_NOT_FOUND';"+
            "u.value="+jsUsername+";"+
            "u.dispatchEvent(new Event('input',{bubbles:true}));"+
            "if(p){p.value="+jsPassword+";p.dispatchEvent(new Event('input',{bubbles:true}));}"+
            "var f=u.form||document.querySelector('form[name=login],form[action*=login]');"+
            "if(!f)return 'FORM_NOT_FOUND';"+
            "var btn=f.querySelector('button[type=submit],input[type=submit]');"+
            "if(btn){btn.click();return 'LOGIN_SUBMITTED'}"+
            "if(typeof f.requestSubmit==='function'){f.requestSubmit();return 'LOGIN_SUBMITTED'}"+
            "if(typeof window.doLogin==='function'){window.doLogin();return 'CHAP_SUBMITTED'}"+
            "return 'SUBMIT_HANDLER_NOT_FOUND'"+
            "}catch(e){return 'FORM_ERROR:'+String(e.message||e)}})()";
          view.evaluateJavascript(script,result->{
            String code=result==null?"NULL":result.replace("\"","");
            if(code.startsWith("LOGIN_SUBMITTED")||code.startsWith("CHAP_SUBMITTED")){
              feedback.accept("pending","أُرسلت بيانات الدخول؛ جارٍ التحقق من الجلسة");
              // Read status only if login response did not already navigate there.
              view.postDelayed(()->{
                if(!authenticated[0]&&view.getUrl()!=null&&view.getUrl().contains("/login")){
                  view.loadUrl("http://172.16.0.1/status");
                }
              },7500);
            } else {
              feedback.accept("failed","لم يُرسِل نموذج الراوتر طلب الدخول: "+code);
            }
          });
        }
        @Override public void onReceivedError(WebView view,WebResourceRequest request,WebResourceError error){
          if(request.isForMainFrame())feedback.accept("failed","تعذر الوصول إلى الراوتر؛ تأكد من اتصال Wi-Fi المحلي");
        }
      });
      hotspot.setAlpha(0f);
      parent.addView(hotspot,new android.widget.FrameLayout.LayoutParams(2,2));
      hotspot.postDelayed(()->{
        if(!authenticated[0]){
          feedback.accept("pending","لم يتأكد اتصال Hotspot بعد؛ افحص جلسة الهاتف في WinBox");
        }
      },15000);
'''
j=j[:start]+replacement+j[end:]
assert 'document.body.textContent.includes' in j
assert 'dialog.setContentView' not in j
# The quota screen must never claim live access just because UM assigned a profile.
old="""window.jawaliHotspotState=(state,message)=>{
 const el=document.getElementById('jw-hotspot-state');
 if(el)el.textContent=message||'';
 if(state==='connected')jawaliPhoneQuota();
};"""
new="""window.jawaliHotspotState=(state,message)=>{
 const el=document.getElementById('jw-hotspot-state');
 if(el){el.textContent=message||'';el.dataset.connection=state||'unknown'}
 if(state==='connected')jawaliPhoneQuota();
 if(state==='failed')toast(message||'تعذر دخول Hotspot، تحقق من الاتصال');
};"""
assert s.count(old)==1
s=s.replace(old,new)
java.write_text(j,encoding='utf-8')
js.write_text(s,encoding='utf-8')
build=root/'app/build.gradle'
b=build.read_text(encoding='utf-8')
assert 'versionCode 3104; versionName "31.04"' in b
build.write_text(b.replace('versionCode 3104; versionName "31.04"','versionCode 3105; versionName "31.05"'),encoding='utf-8')
print('V31.05: submit real Hotspot form, respect CHAP, report errors, verify status response')
