package com.threecats.lsp.dplanner;

import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Edge-to-edge: app draws behind status and navigation bars
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        applyStatusBarStyle();
    }

    @Override
    protected void onResume() {
        super.onResume();
        applyStatusBarStyle();
    }

    private void applyStatusBarStyle() {
        try {
            Window window = getWindow();
            // Make status bar fully transparent so app bg shows through
            window.setStatusBarColor(Color.TRANSPARENT);

            View decorView = window.getDecorView();
            WindowInsetsControllerCompat ctrl =
                new WindowInsetsControllerCompat(window, decorView);

            // Read saved theme: Capacitor stores localStorage in CapacitorStorage prefs
            SharedPreferences prefs = getSharedPreferences("CapacitorStorage", MODE_PRIVATE);
            String theme = prefs.getString("diveTheme", "dark");
            boolean isLight = "light".equals(theme);

            // true = dark icons (visible on light bg), false = white icons (visible on dark bg)
            ctrl.setAppearanceLightStatusBars(isLight);
        } catch (Exception e) {
            // Non-critical — silently ignore
        }
    }
}
