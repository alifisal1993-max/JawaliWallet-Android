from pathlib import Path
r=Path('extracted/JawaliWallet_Android_V31_07')
manifest=r/'app/src/main/AndroidManifest.xml'
m=manifest.read_text(encoding='utf-8')
needle='<action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>'
assert needle in m
m=m.replace(needle,needle+'<intent-filter><action android:name="android.net.conn.CAPTIVE_PORTAL"/><category android:name="android.intent.category.DEFAULT"/></intent-filter>')
manifest.write_text(m,encoding='utf-8')
j=r/'app/src/main/java/com/jawali/wallet/MainActivity.java'
s=j.read_text(encoding='utf-8')
s=s.replace('import android.net.NetworkCapabilities;', 'import android.net.NetworkCapabilities;\nimport android.net.CaptivePortal;')
needle='  private boolean captiveObserved=false;'
assert needle in s
s=s.replace(needle,needle+'''
  private CaptivePortal systemCaptivePortal=null;
  private Network systemCaptiveNetwork=null;
  private static final String SYSTEM_CAPTIVE_ACTION=ConnectivityManager.ACTION_CAPTIVE_PORTAL_SIGN_IN;
  private boolean isWifiLaunch(Intent intent){
    return intent!=null&&(SYSTEM_CAPTIVE_ACTION.equals(intent.getAction())
      ||"com.jawali.wallet.OPEN_WIFI".equals(intent.getAction())
      ||(intent.getData()!=null&&"jawaliwallet".equals(intent.getData().getScheme())));
  }
  private void handleCaptiveIntent(Intent intent){
    if(intent==null||!SYSTEM_CAPTIVE_ACTION.equals(intent.getAction()))return;
    try{
      systemCaptivePortal=intent.getParcelableExtra(ConnectivityManager.EXTRA_CAPTIVE_PORTAL);
      systemCaptiveNetwork=intent.getParcelableExtra(ConnectivityManager.EXTRA_NETWORK);
      // The portal must be contacted through the Wi-Fi network passed by Android.
      if(connectivity!=null&&systemCaptiveNetwork!=null)connectivity.bindProcessToNetwork(systemCaptiveNetwork);
    }catch(Exception e){android.util.Log.w("JawaliWallet","Captive portal intent: "+e.getClass().getSimpleName());}
  }
  private void confirmCaptivePortalDismissed(){
    if(systemCaptivePortal!=null){
      try{
        // Called only after /status confirms a session for this phone.
        systemCaptivePortal.reportCaptivePortalDismissed();
      }catch(Exception e){android.util.Log.w("JawaliWallet","Portal reevaluation failed",e);}
      systemCaptivePortal=null;
    }
  }
''')
needle='''        final String script="window.jawaliHotspotState&&window.jawaliHotspotState("+JSONObject.quote(state)+","+JSONObject.quote(message)+")";'''
assert needle in s
s=s.replace(needle,'''        if("connected".equals(state))confirmCaptivePortalDismissed();
'''+needle)
needle='''    watchCaptiveWifi();
    getWindow().setStatusBarColor'''
assert needle in s
s=s.replace(needle,'''    watchCaptiveWifi();
    handleCaptiveIntent(getIntent());
    getWindow().setStatusBarColor''')
needle='''    if("com.jawali.wallet.OPEN_WIFI".equals(getIntent().getAction()) ||
       (getIntent().getData()!=null && "jawaliwallet".equals(getIntent().getData().getScheme()))){
      web.postDelayed(()->showWifiSection(),1000);
    }'''
assert needle in s
s=s.replace(needle,'''    if(isWifiLaunch(getIntent()))web.postDelayed(()->showWifiSection(),1000);''')
needle='''    if("com.jawali.wallet.OPEN_WIFI".equals(intent.getAction()) ||
      (intent.getData()!=null && "jawaliwallet".equals(intent.getData().getScheme())))showWifiSection();'''
assert needle in s
s=s.replace(needle,'''    handleCaptiveIntent(intent);
    if(isWifiLaunch(intent))showWifiSection();''')
needle='''    if(connectivity!=null && wifiCallback!=null)connectivity.unregisterNetworkCallback(wifiCallback);'''
assert needle in s
s=s.replace(needle,'''    if(connectivity!=null && wifiCallback!=null)connectivity.unregisterNetworkCallback(wifiCallback);
    if(connectivity!=null && systemCaptiveNetwork!=null)connectivity.bindProcessToNetwork(null);''')
j.write_text(s,encoding='utf-8')
g=r/'app/build.gradle'
t=g.read_text(encoding='utf-8')
assert 'versionCode 3116; versionName "31.16"' in t
g.write_text(t.replace('versionCode 3116; versionName "31.16"','versionCode 3117; versionName "31.17"'),encoding='utf-8')
print('Added Android captive portal chooser handler in V31.17')
