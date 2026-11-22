from pathlib import Path
import sys
root=Path(sys.argv[1])
js=root/'app/src/main/assets/jawali-live.js'
html=root/'app/src/main/assets/index.html'
java=root/'app/src/main/java/com/jawali/wallet/MainActivity.java'
s=js.read_text(encoding='utf8')
old='<p id="jw-phone-quota" class="lv-note">'
assert old in s
s=s.replace(old,'<div id="jw-phone-quota" class="wallet-consumption"><h3>استهلاك باقة الهاتف</h3><p class="lv-note">',1)
s=s.replace('الدخول إلى صفحة Hotspot يُستكمل على شبكة الراوتر.</p>','تظهر هنا تفاصيل الباقة المرتبطة برقم الهاتف من خادم المحفظة.</p></div>',1)
start=s.index('window.jawaliPhoneQuota=')
end=s.index('window.jawaliCardQuota=',start)
new="""window.jawaliPhoneQuota=async()=>{
 const el=document.getElementById('jw-phone-quota');if(el)el.textContent='جارٍ قراءة استهلاك الهاتف من خادم المحفظة…';
 try{
  const r=await call('/api/client/wifi-phone-quota'),q=r.quota||{};
  const size=v=>v==null?'غير محدد':(Number(v)/1048576).toLocaleString('ar-YE',{maximumFractionDigits:1})+' ميجابايت';
  const minutes=v=>v==null?'غير محدد':Math.ceil(Number(v)/60).toLocaleString('ar-YE')+' دقيقة';
  const use=Number(q.totalUsedBytes||0),limit=q.transferLimitBytes==null?null:Number(q.transferLimitBytes);
  const pct=limit&&limit>0?Math.min(100,Math.round(use*100/limit)):null;
  const content='<div class="wallet-consumption-head"><small>جوالي محفظتي — استهلاك الشبكة</small><h3>'+safe(q.packageName||q.profile||'لا توجد باقة مفعلة')+'</h3><span>الهاتف: '+safe(r.phone||liveUser?.phone||'')+'</span></div>'+
  '<div class="wallet-consumption-grid"><div><small>المستهلك</small><b>'+size(use)+'</b></div><div><small>المتبقي</small><b>'+size(q.remainingBytes)+'</b></div><div><small>الوقت المتبقي</small><b>'+minutes(q.remainingSeconds)+'</b></div></div>'+
  (pct===null?'':'<div class="wallet-consumption-track"><span style="width:'+pct+'%"></span></div><small>استهلاك '+pct+'% من الباقة</small>')+
  '<p class="wallet-consumption-msg">'+(q.entitlementId?'البيانات من خادم المحفظة وUser Manager':'لم يؤكد الخادم وجود باقة نشطة لهذا الهاتف')+'</p>';
  if(el)el.innerHTML=content;else toast('الباقة: '+(q.packageName||q.profile||'غير محددة')+' — المتبقي '+size(q.remainingBytes));
 }catch(e){if(el)el.textContent='تعذر قراءة الاستهلاك: '+errorText(e);else toast(errorText(e))}
};
window.jawaliHotspotState=(state,message)=>{
 const el=document.getElementById('jw-hotspot-state');
 if(el)el.textContent=message||'';
 if(state==='connected')jawaliPhoneQuota();
};
"""
s=s[:start]+new+s[end:]
s=s.replace('<button class="lv-action" onclick="jawaliReopenHotspot()">فتح صفحة دخول الشبكة</button>','<button class="lv-action" onclick="jawaliReopenHotspot()">الدخول إلى الشبكة من المحفظة</button><p id="jw-hotspot-state" class="lv-note" role="status" aria-live="polite">يتم الدخول خلف واجهة المحفظة دون عرض صفحة الراوتر التقليدية.</p>')
s=s.replace("toast('تم تفعيل الباقة على رقم هاتفك؛ سيتم فتح صفحة دخول الشبكة');","clientTab='internet';render();jawaliPhoneQuota();")
s=s.replace("toast('الباقة مرتبطة بالفعل برقم هاتفك. سيتم فتح دخول الشبكة دون خصم جديد');","clientTab='internet';render();jawaliPhoneQuota();")
s=s.replace("clientNavigate=function(t){priorNav(t);if(liveUser)window.jawaliLiveRefresh()};","clientNavigate=function(t){priorNav(t);if(liveUser){window.jawaliLiveRefresh();if(t==='internet')setTimeout(()=>jawaliPhoneQuota(),180)}};")
js.write_text(s,encoding='utf8')
h=html.read_text(encoding='utf8')
css="""<style id="wallet-consumption-project">.wallet-consumption{margin:12px 0;padding:17px;border-radius:18px;background:linear-gradient(135deg,#0a356c,#106fcb);color:white;text-align:right}.wallet-consumption h3{font-size:21px;color:white;margin:10px 0}.wallet-consumption-head small,.wallet-consumption-head span{color:#d1e7ff;font-size:12px}.wallet-consumption-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;margin:18px 0}.wallet-consumption-grid div{background:#ffffff20;border-radius:11px;padding:10px 5px;min-width:0}.wallet-consumption-grid small{display:block;font-size:10px}.wallet-consumption-grid b{display:block;font-size:12px;margin:7px 0;overflow-wrap:anywhere}.wallet-consumption-track{height:8px;overflow:hidden;background:#ffffff55;border-radius:12px}.wallet-consumption-track span{height:100%;display:block;background:#57edc1}.wallet-consumption-msg{font-size:11px;color:#e1f3ff}</style>"""
h=h.replace('</head>',css+'</head>',1)
html.write_text(h,encoding='utf8')
j=java.read_text(encoding='utf8')
assert 'Dialog dialog=new Dialog(this);' in j
j=j.replace('Dialog dialog=new Dialog(this);','')
start=j.index('      dialog.setContentView(hotspot);')
end=j.index('      hotspot.loadUrl("http://172.16.0.1/login");',start)
j=j[:start]+"""      android.widget.FrameLayout parent=(android.widget.FrameLayout)web.getParent();
      hotspot.setAlpha(0f);
      parent.addView(hotspot,new android.widget.FrameLayout.LayoutParams(2,2));
"""+j[end:]
needle='        @Override public void onPageFinished(WebView view,String url){'
assert needle in j
j=j.replace(needle,needle+"""
          if(url.startsWith("http://172.16.0.1/status")){
            web.evaluateJavascript("window.jawaliHotspotState&&window.jawaliHotspotState('connected','تم تأكيد جلسة الشبكة؛ بيانات الاستهلاك تظهر من المحفظة')",null);
            return;
          }
""",1)
j=j.replace('          view.evaluateJavascript(script,null);','''          view.evaluateJavascript(script,null);
          view.postDelayed(()->{if(view.getUrl()!=null&&!view.getUrl().contains("/status"))view.loadUrl("http://172.16.0.1/status");},4500);''',1)
java.write_text(j,encoding='utf8')
b=root/'app/build.gradle'
old='versionCode 3103; versionName "31.03"'
assert old in b.read_text(encoding='utf8')
b.write_text(b.read_text(encoding='utf8').replace(old,'versionCode 3104; versionName "31.04"'),encoding='utf8')
print('Wallet usage status and hidden network authentication applied')
