from pathlib import Path
root=Path("extracted/JawaliWallet_Android_V31_07")
p=root/"app/src/main/java/com/jawali/wallet/MainActivity.java"
s=p.read_text(encoding="utf-8")
old='if("/index.html/".equals(landingPath)||"/index.html".equals(landingPath)){'
assert old in s
s=s.replace(old,'if("/index.html/".equals(landingPath)||"/index.html".equals(landingPath)||"/login/".equals(landingPath)){')
old='''            } else {
              feedback.accept("failed","تعذر إرسال نموذج الدخول ("+code+") في "+String.valueOf(currentPage[0]));
            }
'''
new='''            } else if("FORM_NOT_FOUND".equals(code)){
              // RouterOS HTTP-PAP is enabled. The portal can serve a form-less
              // page at /login. Submit only once then check actual session.
              feedback.accept("pending","صفحة الدخول بلا نموذج؛ جارٍ محاولة دخول PAP واحدة والتحقق من الجلسة");
              try{
                String body="username="+java.net.URLEncoder.encode(username,"UTF-8")+
                  "&password="+java.net.URLEncoder.encode(password,"UTF-8")+
                  "&dst="+java.net.URLEncoder.encode("http://172.16.0.1/status","UTF-8")+
                  "&popup=false";
                view.postUrl("http://172.16.0.1/login",body.getBytes(java.nio.charset.StandardCharsets.UTF_8));
                view.postDelayed(()->{if(!authenticated[0])view.loadUrl("http://172.16.0.1/status");},6500);
              }catch(Exception e){feedback.accept("failed","تعذر إرسال دخول PAP: "+e.getMessage());}
            } else {
              feedback.accept("failed","تعذر إرسال نموذج الدخول ("+code+") في "+String.valueOf(currentPage[0]));
            }
'''
assert old in s
s=s.replace(old,new)
p.write_text(s,encoding="utf-8")
g=root/"app/build.gradle"
s=g.read_text(encoding="utf-8")
assert 'versionCode 3114; versionName "31.14"' in s
g.write_text(s.replace('versionCode 3114; versionName "31.14"','versionCode 3115; versionName "31.15"'),encoding="utf-8")
print("V31.15 PAP form-less redirect patch applied")
