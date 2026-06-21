package com.threecats.lsp.dplannerccr;

import android.os.Bundle;
import android.webkit.CookieManager;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Edge-to-edge: app draws behind status and navigation bars
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        // styles.xml sets windowLightStatusBar=true (dark icons, safe default for light theme).
        // Override to white icons here if the saved theme is dark.
        applyStatusBarIconColor();
    }

    @Override
    public void onResume() {
        super.onResume();
        applyStatusBarIconColor();
    }

    /**
     * Reads diveTheme from the WebView cookie (written by JS toggleTheme via document.cookie).
     * styles.xml default = windowLightStatusBar true = dark icons (correct for light bg).
     * If cookie says "dark" theme, flip to white icons (visible on dark bg).
     * If no cookie yet (first install), default stays dark icons — correct since app defaults to dark theme.
     *
     * NOTE: First install with dark theme default will show dark icons on dark bg until user
     * toggles theme once (which writes the cookie). This is acceptable — the cookie persists forever after.
     */
    private void applyStatusBarIconColor() {
        try {
            String cookies = CookieManager.getInstance().getCookie("https://localhost");
            // Default: assume dark theme (no cookie on first install) = white icons
            boolean isLight = false;
            if (cookies != null) {
                for (String part : cookies.split(";")) {
                    String trimmed = part.trim();
                    if (trimmed.startsWith("diveTheme=")) {
                        isLight = "light".equals(trimmed.substring("diveTheme=".length()).trim());
                        break;
                    }
                }
            }
            WindowInsetsControllerCompat ctrl =
                new WindowInsetsControllerCompat(getWindow(), getWindow().getDecorView());
            // true = dark icons (readable on light bg), false = white icons (readable on dark bg)
            ctrl.setAppearanceLightStatusBars(isLight);
        } catch (Exception e) {
            // Non-critical — silently ignore
        }
    }
}
