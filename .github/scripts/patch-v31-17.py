from pathlib import Path
root=Path('extracted/JawaliWallet_Android_V31_07')
manifest=root/'app/src/main/AndroidManifest.xml'
s=manifest.read_text(encoding='utf-8')
needle='<data android:scheme="jawaliwallet" android:host="wifi-login"/></intent-filter>'
assert needle in s
filters='''<data android:scheme="jawaliwallet" android:host="wifi-login"/></intent-filter>
      <!-- Only the router login URLs, not arbitrary web traffic. User opt-in remains required. -->
      <intent-filter android:label="جوالي محفظتي — دخول الشبكة">
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="http" android:host="172.16.0.1" android:path="/login"/>
        <data android:scheme="http" android:host="172.16.0.1" android:path="/login/"/>
        <data android:scheme="http" android:host="172.16.0.1" android:path="/index.html/"/>
      </intent-filter>
      <intent-filter android:label="جوالي محفظتي — دخول الشبكة">
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="http" android:host="a.com" android:path="/login"/>
        <data android:scheme="http" android:host="a.com" android:path="/login/"/>
      </intent-filter>'''
s=s.replace(needle,filters)
manifest.write_text(s,encoding='utf-8')
p=root/'app/src/main/java/com/jawali/wallet/MainActivity.java'
s=p.read_text(encoding='utf-8')
needle='(getIntent().getData()!=null && "jawaliwallet".equals(getIntent().getData().getScheme()))'
assert needle in s
s=s.replace(needle,'isSupportedEntryIntent(getIntent())')
needle='(intent.getData()!=null && "jawaliwallet".equals(intent.getData().getScheme()))'
assert needle in s
s=s.replace(needle,'isSupportedEntryIntent(intent)')
anchor='  @Override protected void onNewIntent(Intent intent){'
assert anchor in s
helper='''  private boolean isSupportedEntryIntent(Intent intent){
    if(intent==null || intent.getData()==null)return false;
    android.net.Uri uri=intent.getData();
    if("jawaliwallet".equals(uri.getScheme()) && "wifi-login".equals(uri.getHost()))return true;
    if(!"http".equals(uri.getScheme()))return false;
    String host=uri.getHost(),path=uri.getPath();
    return ("172.16.0.1".equals(host)||"a.com".equalsIgnoreCase(host))
      && ("/login".equals(path)||"/login/".equals(path)||"/index.html/".equals(path));
  }
'''
s=s.replace(anchor,helper+anchor)
p.write_text(s,encoding='utf-8')
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8').replace('versionCode 3116; versionName "31.16"','versionCode 3117; versionName "31.17"')
assert 'versionName "31.17"' in s
g.write_text(s,encoding='utf-8')
print('V31.17 explicit captive portal intent routing ready')
