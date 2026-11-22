#!/usr/bin/env python3
"""V30.95: Add clearly accessible client registration without touching live finance APIs."""
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
assert 'function clientLoginView(){' in s, 'Client login function missing'
assert 'function clientAccountView(){' in s, 'Client account function missing'
assert '</script>' in s and '</head>' in s
additional = r"""
/* V30.95: accessible register/login screens based on the project's existing demo-auth validation. */
function jawaliOpenRegistration(){
  clientSession=null;
  clientAuthMode='register';
  clientTab='home';
  document.body.classList.remove('clientApp');
  render();
  setTimeout(()=>window.scrollTo(0,0),50);
}
function jawaliOpenLogin(){
  clientSession=null;
  clientAuthMode='login';
  clientTab='home';
  document.body.classList.remove('clientApp');
  render();
  setTimeout(()=>window.scrollTo(0,0),50);
}
const jwOldLoginView=clientLoginView;
clientLoginView=function(){
 const reg=clientAuthMode==='register';
 return '<section class="jw-auth-wrapper"><div class="jw-auth-header"><div class="jw-auth-mark">◈</div><div class="jw-auth-brand">جوالي محفظتي</div><h1>'+ (reg?'إنشاء حساب جديد':'مرحبًا بعودتك')+'</h1><p>'+(reg?'سجّل بياناتك لتجربة خدمات المحفظة':'ادخل إلى حسابك لمتابعة خدماتك')+'</p></div>'+
 '<div class="jw-auth-panel">'+
 (reg?'<label>الاسم الرباعي باللغة العربية<input id="authName" class="field" autocomplete="name" placeholder="الاسم الأول واسم الأب والجد واللقب"></label>':'')+
 '<label>رقم الهاتف<input id="authPhone" class="field" type="tel" inputmode="numeric" autocomplete="tel" maxlength="9" placeholder="77xxxxxxx"></label>'+
 '<label>كلمة المرور<input id="authPassword" class="field" type="password" autocomplete="'+(reg?'new-password':'current-password')+'" placeholder="حرف إنجليزي وخمسة أرقام"></label>'+
 (reg?'<label>البريد الإلكتروني (اختياري)<input id="authEmail" class="field" type="email" autocomplete="email" placeholder="name@example.com"></label>':'')+
 '<button class="jw-auth-submit" onclick="submitClientAuth()">'+(reg?'إنشاء حساب تجريبي':'تسجيل الدخول')+'</button>'+
 '<div class="jw-auth-switch">'+(reg?'لديك حساب بالفعل؟ <button onclick="jawaliOpenLogin()">تسجيل الدخول</button>':'ليس لديك حساب؟ <button onclick="jawaliOpenRegistration()">إنشاء حساب جديد</button>')+'</div>'+
 '<div class="jw-auth-note">وضع المعاينة: إنشاء الحساب محلي ولا يتم حفظه في خادم المحفظة. لا تستخدم كلمة مرور حقيقية.</div>'+
 (!reg?'<p class="jw-auth-example">حساب التجربة: <b dir="ltr">733456789</b> / <b dir="ltr">A12345</b></p>':'')+
 '</div></section>';
};
const jwOriginalAccountView=clientAccountView;
clientAccountView=function(){
 return jwOriginalAccountView()+ '<div class="jw-register-account"><h3>الحسابات</h3><p>يمكنك تسجيل الخروج أو إنشاء حساب تجريبي آخر على هذا الجهاز.</p><button onclick="jawaliOpenRegistration()">＋ إنشاء حساب جديد</button><button onclick="jawaliOpenLogin()">تسجيل الدخول بحساب آخر</button></div>';
};
"""
# Install inside the last existing script block, after app helpers and before closure.
# Script globals are attached via a fresh script, AFTER main script execution: lexical vars remain accessible.
s=s.replace('</body></html>', '<script>'+additional+'</script></body></html>',1)
style=r"""
/* V30.95 client auth and mobile keyboard responsiveness */
body .jw-auth-wrapper{direction:rtl;max-width:500px;margin:10px auto 100px;padding:0 12px;color:#132d50}
body .jw-auth-header{text-align:center;background:linear-gradient(135deg,#0c2c65,#096ecc);color:#fff;border-radius:22px 22px 8px 8px;padding:26px 18px 23px}
body .jw-auth-mark{width:48px;height:48px;border-radius:15px;display:grid;place-items:center;background:#ffffff25;border:1px solid #ffffff45;margin:0 auto 8px;font-size:26px}
body .jw-auth-brand{font-size:12px;opacity:.8}
body .jw-auth-header h1{color:#fff;font-size:22px;margin:12px 0 5px}
body .jw-auth-header p{font-size:13px;color:#e6f4ff;margin:0}
body .jw-auth-panel{background:#fff;padding:21px 17px;border-radius:0 0 20px 20px;box-shadow:0 9px 22px #0b3f731c;display:grid;gap:13px}
body .jw-auth-panel label{display:grid;gap:6px;font-size:13px;font-weight:700;text-align:right;color:#193457}
body .jw-auth-panel input{width:100%;box-sizing:border-box;min-height:46px;background:#f6f9ff;border:1px solid #cbd9e9;border-radius:12px;padding:10px 12px;font-size:14px;direction:rtl;color:#162e4b}
body .jw-auth-panel input:focus{outline:2px solid #1686df;border-color:transparent}
body .jw-auth-submit{width:100%;min-height:46px;border:0;border-radius:12px;background:#0875e7;color:white;font-weight:800;font-size:15px}
body .jw-auth-switch{text-align:center;font-size:13px;color:#60728b}
body .jw-auth-switch button{border:0;background:transparent;padding:8px;color:#006ed7;text-decoration:underline;font-weight:700}
body .jw-auth-note{font-size:11px;line-height:1.65;background:#e9f8fc;color:#276075;padding:11px;border-radius:11px}
body .jw-auth-example{font-size:12px;color:#647b92;margin:0;text-align:center}
body .jw-register-account{background:#fff;border:1px solid #e3eaf4;border-radius:18px;padding:15px;margin:12px 0 80px;display:grid;gap:8px}
body .jw-register-account h3{margin:0;color:#142c54}
body .jw-register-account p{margin:0 0 4px;font-size:12px;color:#69809a}
body .jw-register-account button{border:0;min-height:42px;border-radius:12px;background:#e9f3ff;color:#075cb7;font-size:13px;font-weight:700}
body .jw-register-account button:first-of-type{background:#0b76e7;color:#fff}
@supports selector(:has(*)){body.clientApp:has(input:focus) .jw-bottom,body.clientApp:has(textarea:focus) .jw-bottom{display:none!important}}
body.clientApp input:focus,body.clientApp textarea:focus{scroll-margin-bottom:210px}
body.clientApp .jw-finance-screen input,body.clientApp .jw-finance-screen textarea,body.clientApp .jw-finance-screen select{min-height:44px;border-radius:12px}
"""
s=s.replace('</head>','<style id="jawali-v30-95-auth-style">'+style+'</style></head>',1)
p.write_text(s,encoding='utf-8')
print('V30.95 registration interface patched:',p,'bytes',p.stat().st_size)
