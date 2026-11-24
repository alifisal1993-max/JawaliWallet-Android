from pathlib import Path
r=Path("extracted/JawaliWallet_Android_V31_07")
j=r/"app/src/main/java/com/jawali/wallet/MainActivity.java"
s=j.read_text(encoding="utf-8")
s=s.replace("import android.app.Activity;", """import android.app.Activity;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.NotificationChannel;
import android.app.PendingIntent;
import android.Manifest;
import android.content.pm.PackageManager;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;""")
needle="  private WebView web;"
assert needle in s
s=s.replace(needle,'''  private WebView web;
  private ConnectivityManager connectivity;
  private ConnectivityManager.NetworkCallback wifiCallback;
  private boolean foreground=true;
  private boolean captiveObserved=false;
  private static final String CONNECT_CHANNEL="jawali_wifi_entry";
  private static final int CONNECT_NOTIFICATION=3116;
  private void showWifiSection(){
    if(web!=null)web.evaluateJavascript("if(window.jawaliOpenWifiFromSystem)jawaliOpenWifiFromSystem()",null);
  }
  private void makeConnectionChannel(){
    if(Build.VERSION.SDK_INT>=26){
      NotificationManager manager=(NotificationManager)getSystemService(Context.NOTIFICATION_SERVICE);
      manager.createNotificationChannel(new NotificationChannel(CONNECT_CHANNEL,"تسجيل الدخول إلى شبكة الواي فاي",NotificationManager.IMPORTANCE_DEFAULT));
    }
  }
  private void promptForWifiEntry(){
    if(foreground){showWifiSection();return;}
    if(Build.VERSION.SDK_INT>=33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)return;
    Intent open=new Intent(this,MainActivity.class).setAction("com.jawali.wallet.OPEN_WIFI");
    open.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);
    PendingIntent action=PendingIntent.getActivity(this,CONNECT_NOTIFICATION,open,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
    Notification.Builder b=Build.VERSION.SDK_INT>=26?new Notification.Builder(this,CONNECT_CHANNEL):new Notification.Builder(this);
    b.setSmallIcon(android.R.drawable.ic_dialog_info)
      .setContentTitle("جوالي محفظتي — دخول الشبكة")
      .setContentText("شبكة Wi-Fi تحتاج تسجيل دخول. اضغط لاستكمال الدخول بالمحفظة")
      .setAutoCancel(true).setContentIntent(action);
    NotificationManager manager=(NotificationManager)getSystemService(Context.NOTIFICATION_SERVICE);
    manager.notify(CONNECT_NOTIFICATION,b.build());
  }
  private void watchCaptiveWifi(){
    connectivity=(ConnectivityManager)getSystemService(Context.CONNECTIVITY_SERVICE);
    if(connectivity==null)return;
    wifiCallback=new ConnectivityManager.NetworkCallback(){
      @Override public void onCapabilitiesChanged(Network network,NetworkCapabilities caps){
        boolean captive=caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
          && caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_CAPTIVE_PORTAL);
        if(captive && !captiveObserved){
          captiveObserved=true;
          runOnUiThread(()->promptForWifiEntry());
        }else if(!captive && captiveObserved){captiveObserved=false;}
      }
      @Override public void onLost(Network network){captiveObserved=false;}
    };
    connectivity.registerDefaultNetworkCallback(wifiCallback);
  }
''')
s=s.replace("    super.onCreate(savedInstanceState);",'''    super.onCreate(savedInstanceState);
    makeConnectionChannel();
    if(Build.VERSION.SDK_INT>=33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED){
      requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},3116);
    }
    watchCaptiveWifi();''')
s=s.replace('    web.loadUrl("file:///android_asset/index.html");','''    web.loadUrl("file:///android_asset/index.html");
    web.postDelayed(()->{if(captiveObserved && foreground)showWifiSection();},1500);
    if("com.jawali.wallet.OPEN_WIFI".equals(getIntent().getAction()) ||
       (getIntent().getData()!=null && "jawaliwallet".equals(getIntent().getData().getScheme()))){
      web.postDelayed(()->showWifiSection(),1000);
    }''')
s=s.replace("  @Override public void onBackPressed()",'''  @Override protected void onNewIntent(Intent intent){
    super.onNewIntent(intent);setIntent(intent);
    if("com.jawali.wallet.OPEN_WIFI".equals(intent.getAction()) ||
      (intent.getData()!=null && "jawaliwallet".equals(intent.getData().getScheme())))showWifiSection();
  }
  @Override protected void onResume(){super.onResume();foreground=true;}
  @Override protected void onPause(){foreground=false;super.onPause();}
  @Override public void onBackPressed()''')
s=s.replace("    apiExecutor.shutdownNow(); web.destroy(); super.onDestroy();",'''    if(connectivity!=null && wifiCallback!=null)connectivity.unregisterNetworkCallback(wifiCallback);
    apiExecutor.shutdownNow(); web.destroy(); super.onDestroy();''')
j.write_text(s,encoding="utf-8")
m=r/"app/src/main/AndroidManifest.xml"
s=m.read_text(encoding="utf-8")
s=s.replace('<uses-permission android:name="android.permission.INTERNET"/>','''<uses-permission android:name="android.permission.INTERNET"/>
 <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
 <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>''')
s=s.replace('<category android:name="android.intent.category.LAUNCHER"/></intent-filter>','''<category android:name="android.intent.category.LAUNCHER"/></intent-filter><intent-filter><action android:name="android.intent.action.VIEW"/><category android:name="android.intent.category.DEFAULT"/><category android:name="android.intent.category.BROWSABLE"/><data android:scheme="jawaliwallet" android:host="wifi-login"/></intent-filter>''')
m.write_text(s,encoding="utf-8")
p=r/"app/src/main/assets/jawali-live.js"
s=p.read_text(encoding="utf-8")
assert s.endswith('})();\n')
s=s[:-6]+'''// Wi-Fi captive prompt only navigates; never purchases a package.
window.jawaliOpenWifiFromSystem=function(){
 try{
  go('client');
  if(liveUser && typeof clientNavigate==='function')clientNavigate('internet');
  else status('اتصلت بشبكة Wi-Fi؛ سجّل الدخول إلى المحفظة لإكمال دخول الشبكة');
 }catch(e){console.warn('Wi-Fi navigation unavailable',e)}
};
})();
'''
p.write_text(s,encoding="utf-8")
g=r/"app/build.gradle"
s=g.read_text(encoding="utf-8").replace('versionCode 3115; versionName "31.15"','versionCode 3116; versionName "31.16"')
assert 'versionName "31.16"' in s
g.write_text(s,encoding="utf-8")
print("V31.16 Wi-Fi captive entry ready")
