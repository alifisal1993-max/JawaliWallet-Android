from pathlib import Path
import sys,re
p=Path(sys.argv[1]);s=p.read_text(encoding='utf-8')
marker='<script src="jawali-live.js"></script>'
assert s.count(marker)==1, 'Missing live JS script marker'
before,after=s.split(marker,1)
assert 'const jwOldLoginView=clientLoginView;' in after
assert 'const jw96OldLoginView=clientLoginView;' in after
# All later scripts override live authentication, letting demo accounts open demo financial pages.
# Remove only the legacy client authentication overrides written after the live bundle.
after_clean=re.sub(r'<script>\s*/\* V30\.95: accessible register/login screens.*?</script>','',after,flags=re.S)
after_clean=re.sub(r'<script>\s*/\* V30\.96: inline Arabic validation.*?</script>','',after_clean,flags=re.S)
assert 'jw96OldLoginView' not in after_clean
assert 'jwOldLoginView' not in after_clean
assert 'jw96OldLoginView' in after
s=before+marker+after_clean
# Disable the old demo authentication function as a defense against accidental entrypoints.
start=s.index('function submitClientAuth(){')
end=s.index('function clientLogout(){',start)
s=s[:start]+"function submitClientAuth(){toast('هذه الواجهة غير مدعومة. سجّل الدخول عبر خادم المحفظة.');go('client')} "+s[end:]
# Replace demo topup HTML, so that an unexpected legacy route cannot simulate request creation.
start=s.index('function clientTopupView(){')
end=s.index('function clientInvoicesView(){',start)
s=s[:start]+"""function clientTopupView(){return panel('تغذية الرصيد','<p class="note">يلزم تسجيل الدخول إلى خادم المحفظة لعرض طلبات الإيداع وإرسالها. لا تتوفر طلبات تجريبية.</p>')} function submitTopup(){toast('استخدم طلب الإيداع المتصل بالخادم بعد تسجيل الدخول الحقيقي.')} """+s[end:]
assert 'إرسال طلب شحن تجريبي' not in s
assert 'TOP-'+chr(39) not in s[s.index('function clientTopupView(){'):s.index('function clientInvoicesView(){')]
assert 'const jw96OldLoginView' not in s
p.write_text(s,encoding='utf-8')
print('Removed late auth overrides and replaced legacy topup with safe notice. Live auth now wins.')
