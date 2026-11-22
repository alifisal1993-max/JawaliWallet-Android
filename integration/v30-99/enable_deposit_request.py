from pathlib import Path
import sys,re
app=Path(sys.argv[1])
s=app.read_text(encoding='utf-8')
pattern=r"window\.jawaliDepositRequest=\(\)=>\{const amount=Number\(document\.getElementById\('lv-request-amount'\)\.value\),description=document\.getElementById\('lv-request-desc'\)\.value\.trim\(\);if\(!Number\.isFinite\(amount\)\|\|amount<=0\|\|description\.length<2\)return toast\('أدخل مبلغًا ووصفًا صحيحين'\);write\('/api/client/requests',\{type:'DEPOSIT',amount,description\},.إرسال طلب شحن بقيمة \$\{rial\(amount\)\}\؟.\)\};"
new="""window.jawaliDepositRequest=async()=>{
 if(busy)return toast('طلب الإيداع قيد الإرسال');
 if(!token||!liveUser)return toast('سجّل الدخول إلى المحفظة أولًا');
 const amount=Number(document.getElementById('lv-request-amount')?.value);
 const description=(document.getElementById('lv-request-desc')?.value||'').trim();
 if(!Number.isFinite(amount)||amount<=0||Math.round(amount*100)!==amount*100||description.length<2||description.length>200)
   return toast('أدخل مبلغًا موجبًا صالحًا ووصفًا من 2 إلى 200 حرف');
 if(!confirm('هل تريد إرسال طلب إيداع بقيمة '+rial(amount)+' إلى الإدارة؟\\nلن يتم إضافة أي مبلغ إلى رصيدك قبل موافقة الإدارة.'))return;
 busy=true;
 try{
   status('جارٍ إرسال الطلب إلى خادم المحفظة…');
   const result=await call('/api/client/requests','POST',{type:'DEPOSIT',amount,description});
   if(!result||typeof result.id!=='string')throw new Error('لم يؤكد الخادم تسجيل الطلب. افحص قائمة الطلبات قبل المحاولة مجددًا.');
   try{await refresh()}catch(e){/* submission succeeded; list refresh can fail independently */}
   clientTab='requests';render();
   toast('تم تسجيل طلب الإيداع في الخادم برقم '+result.id+' وهو بانتظار مراجعة الإدارة');
 }catch(e){
   toast(errorText(e)+' — إذا انتهت مهلة الاتصال، افحص الطلبات قبل إعادة الإرسال');
 }finally{busy=false}
};"""
s,count=re.subn(pattern,lambda _:new,s)
if count!=1:
 raise SystemExit('Deposit function not found exactly once: '+str(count)+'; refusing unverified patch')
assert "if(path!=='/api/client/account/password')return" in s, "Unexpected financial permission change"
assert "const result=await call('/api/client/requests','POST',{type:'DEPOSIT',amount,description})" in s
assert s.count("window.jawaliDepositRequest=")==1
app.write_text(s,encoding='utf-8')
print('Activated only customer deposit request creation; all other financial writes remain blocked.')
