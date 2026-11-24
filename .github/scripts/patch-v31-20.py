from pathlib import Path
r=Path('extracted/JawaliWallet_Android_V31_07')
m=r/'app/src/main/AndroidManifest.xml'
s=m.read_text(encoding='utf-8')
needle='<action android:name="android.intent.action.MAIN"/>'
assert needle in s
anchor='''<intent-filter android:label="جوالي محفظتي — دخول الشبكة">'''
assert anchor in s
# Android invokes the standard captive portal sign-in action, not merely VIEW /login.
s=s.replace(anchor,'''<intent-filter android:label="جوالي محفظتي — إكمال تسجيل دخول Wi-Fi">
        <action android:name="android.net.conn.CAPTIVE_PORTAL"/>
        <category android:name="android.intent.category.DEFAULT"/>
      </intent-filter>
      '''+anchor,1)
m.write_text(s,encoding='utf-8')
j=r/'app/src/main/java/com/jawali/wallet/MainActivity.java'
s=j.read_text(encoding='utf-8')
needle='  private boolean isSupportedEntryIntent(Intent intent){'
assert needle in s
s=s.replace(needle,'''  private boolean isCaptivePortalIntent(Intent intent){
    return intent!=null &&
      "android.net.conn.CAPTIVE_PORTAL".equals(intent.getAction());
  }
'''+needle)
old='''    pendingWifiEntry="com.jawali.wallet.OPEN_WIFI".equals(getIntent().getAction())
      || isSupportedEntryIntent(getIntent());'''
assert old in s
s=s.replace(old,'''    pendingWifiEntry=(getIntent()!=null && "com.jawali.wallet.OPEN_WIFI".equals(getIntent().getAction()))
      || isSupportedEntryIntent(getIntent()) || isCaptivePortalIntent(getIntent());''')
old='''    if("com.jawali.wallet.OPEN_WIFI".equals(getIntent().getAction()) ||
       isSupportedEntryIntent(getIntent())){'''
assert old in s
s=s.replace(old,'''    if((getIntent()!=null && "com.jawali.wallet.OPEN_WIFI".equals(getIntent().getAction())) ||
       isSupportedEntryIntent(getIntent()) || isCaptivePortalIntent(getIntent())){''')
old='''    if("com.jawali.wallet.OPEN_WIFI".equals(intent.getAction()) ||
      isSupportedEntryIntent(intent))showWifiSection();'''
assert old in s
s=s.replace(old,'''    if("com.jawali.wallet.OPEN_WIFI".equals(intent.getAction()) ||
      isSupportedEntryIntent(intent) || isCaptivePortalIntent(intent))showWifiSection();''')
# Don't report captive portal dismissed prematurely: Android must validate live Internet.
# Do not bind the entire wallet process to a caller-supplied Network.
j.write_text(s,encoding='utf-8')
g=r/'app/build.gradle'
s=g.read_text(encoding='utf-8')
assert 'versionCode 3119; versionName "31.19"' in s
g.write_text(s.replace('versionCode 3119; versionName "31.19"','versionCode 3120; versionName "31.20"'),encoding='utf-8')
print('V31.20 Android native captive portal intent registered.')
