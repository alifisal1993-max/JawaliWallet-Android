from pathlib import Path
import sys,re
p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
assert "function clientDemoView()" in s and "function jawaliOpenRegistration()" in s
s=s.replace("width:100,height:170,title:15,detail:10,price:18,radius:14,pad:9","width:100,height:178,title:13,detail:10,price:16,radius:14,pad:7",1)
s=s.replace("'height','ارتفاع البطاقة','range',115,300,5","'height','ارتفاع البطاقة','range',100,260,5",1)
style = """
/* V30.96: mobile responsive layout, navigational fix and compact cards */
html{scroll-padding-bottom:110px}body{width:100%;overflow-x:hidden}
body.clientApp{background:#f2f6ff!important}
body.clientApp main{min-width:0!important;max-width:100%!important}
body.clientApp #content{min-width:0!important;max-width:100vw!important;padding:0!important}
body.clientApp .jw-top{padding-top:max(62px,calc(env(safe-area-inset-top) + 24px))!important;padding-bottom:23px!important;overflow:hidden}
body.clientApp .jw-page-head{padding-top:max(61px,calc(env(safe-area-inset-top) + 24px))!important;min-height:0!important;gap:10px!important;flex-wrap:wrap!important}
body.clientApp .jw-page-head strong{font-size:19px!important;line-height:1.4!important}
body.clientApp .jw-body,body.clientApp .jw-page{width:100%!important;max-width:100%!important;min-width:0!important;margin-inline:auto!important;padding-left:12px!important;padding-right:12px!important}
body.clientApp .jw-body{padding-bottom:110px!important}
body.clientApp .jw-bottom{transform:none!important;position:fixed!important;left:0!important;right:0!important;bottom:0!important;max-width:100vw!important;width:100%!important;height:74px!important;min-height:74px!important;display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:0!important;padding:6px 4px max(9px,env(safe-area-inset-bottom))!important;box-sizing:border-box!important;z-index:65!important;overflow:visible!important}
body.clientApp .jw-bottom button{min-width:0!important;width:100%!important;max-width:100%!important;min-height:49px!important;line-height:1.3!important;margin:0!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:3px!important;padding:4px 1px!important;font-size:clamp(9px,2.6vw,12px)!important;white-space:normal!important;box-sizing:border-box!important}
body.clientApp .jw-bottom button span{font-size:20px!important;line-height:1!important}
body.clientApp .jw-bottom button.scan{min-width:0!important;width:100%!important;height:51px!important;border-radius:15px!important;top:0!important;transform:none!important;box-shadow:0 3px 8px #0a5fd444!important;margin:0!important}
body.clientApp .jw-bottom button.scan small{display:block!important;position:static!important;top:auto!important;margin:0!important;color:inherit!important;font-size:10px!important}
body.clientApp .jw-shop-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px!important;align-items:start!important}
body.clientApp .jw-shop-card{min-width:0!important;padding:8px!important;gap:3px!important;min-height:0!important}
body.clientApp .jw-shop-card .jw-shop-tag{display:none!important}
body.clientApp .jw-shop-card .jw-shop-meta span:last-child{display:none!important}
body.clientApp .jw-shop-card h3{line-height:1.35!important;overflow-wrap:anywhere!important}
body.clientApp .jw-shop-card .jw-shop-head{gap:3px!important}
body.clientApp .jw-shop-card .jw-shop-buy{min-height:33px!important;padding:6px 4px!important}
body.clientApp .jw-shop-orders{margin-bottom:25px!important}
body.clientApp .profileTile{min-width:0!important;min-height:0!important;box-sizing:border-box!important;max-width:100%!important}
body.clientApp .panel,body.clientApp .jw-finance-card{max-width:100%!important;min-width:0!important;box-sizing:border-box!important}
body.clientApp .panel label{line-height:1.5}
body.clientApp .panel input,body.clientApp .panel select,body.clientApp .panel textarea{width:100%;box-sizing:border-box;max-width:100%;font-size:16px!important;min-height:43px}
body.clientApp button.primary{border-radius:12px!important;min-height:42px!important}
body.clientApp .jw-auth-wrapper{padding:0 12px 90px!important;max-width:490px!important;box-sizing:border-box!important}
body .jw-auth-panel{gap:10px!important;padding:16px 14px!important}
body .jw-auth-header{padding:23px 14px 17px!important}
body .jw-auth-header h1{font-size:20px!important}
body .jw-auth-panel input{font-size:16px!important;min-height:43px!important}
body .jw-auth-panel .jw-auth-submit{margin-top:2px!important}
body .jw-auth-error{color:#b42342!important;background:#fff1f3!important;border:1px solid #ffcbd4!important;border-radius:10px!important;padding:10px!important;font-size:12px!important;display:none}
body .jw-auth-error:not(:empty){display:block}
body .jw-auth-panel input[aria-invalid="true"]{border-color:#d12b46!important;background:#fff8f9!important}
#jw-studio .studio-sheet{max-width:min(96vw,560px)!important;width:100%!important;max-height:calc(100dvh - 35px)!important;overflow-y:auto!important;box-sizing:border-box!important}
#jw-studio .studio-grid{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important}
#jw-studio .studio-grid label{min-width:0!important;overflow:hidden!important}
#jw-studio .studio-grid input{max-width:100%!important;min-width:0!important}
body.clientApp:has(input:focus) .jw-bottom,body.clientApp:has(textarea:focus) .jw-bottom{display:none!important}
@media(max-width:349px){body.clientApp .jw-shop-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}}
"""
s=s.replace("</head>",'<style id="jw-v3096">'+style+"</style></head>",1)
js = r"""
/* V30.96: inline Arabic validation for demo accounts. */
const jw96OldLoginView=clientLoginView;
clientLoginView=function(){
 const html=jw96OldLoginView();
 return html.replace('</div></section>','<div id="jw96-auth-error" class="jw-auth-error" role="alert" aria-live="polite"></div></div></section>');
};
const jw96OldSubmit=submitClientAuth;
submitClientAuth=function(){
 const phone=document.getElementById('authPhone');
 const password=document.getElementById('authPassword');
 const name=document.getElementById('authName');
 const email=document.getElementById('authEmail');
 const err=document.getElementById('jw96-auth-error');
 for(const el of [phone,password,name,email])if(el)el.removeAttribute('aria-invalid');
 const fail=(el,msg)=>{if(el)el.setAttribute('aria-invalid','true');if(err)err.textContent=msg;if(el){el.focus();el.scrollIntoView({block:'center',behavior:'smooth'})}return false};
 if(err)err.textContent='';
 if(!phone||!/^(71|73|77|78)[0-9]{7}$/.test(phone.value.trim()))return fail(phone,'رقم الهاتف يجب أن يحتوي على 9 أرقام إنجليزية ويبدأ بـ 71 أو 73 أو 77 أو 78.');
 if(name&&!/^[\u0621-\u064A]+(?:\s+[\u0621-\u064A]+){3}$/.test(name.value.trim()))return fail(name,'يرجى إدخال اسم رباعي باللغة العربية فقط.');
 if(!password||!/^[A-Za-z][0-9]{5}$/.test(password.value))return fail(password,'كلمة المرور: حرف إنجليزي واحد يتبعه خمسة أرقام إنجليزية.');
 if(email&&email.value.trim()&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim()))return fail(email,'صيغة البريد الإلكتروني غير صحيحة.');
 return jw96OldSubmit();
};
"""
needle="</script></body></html>"
assert s.rstrip().endswith(needle)
s=s.rstrip()[:-len(needle)]+"</script><script>"+js+"</script></body></html>"
s=s.replace("تطبيق جوالي محفظتي V30.92","تطبيق جوالي محفظتي V30.96",1)
p.write_text(s,encoding="utf-8")
print("V30.96 mobile UI and auth validation applied", p.stat().st_size)
