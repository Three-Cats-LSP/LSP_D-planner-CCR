/**
 * capacitor-bridge.js
 *
 * Intercepts blob <a download> clicks produced by exportTXT() and exportPDF()
 * and saves the file via @capacitor/filesystem, then shares via @capacitor/share.
 *
 * On the web / PWA this file does nothing — the normal <a download> path runs as-is.
 *
 * STORAGE STRATEGY
 * ----------------
 * Android ≤ 12 (API ≤ 32):
 *   - Requests READ_EXTERNAL_STORAGE + WRITE_EXTERNAL_STORAGE at runtime
 *   - Writes to Directory.DOCUMENTS (visible in Files app / Downloads)
 *
 * Android 13+ (API 33+):
 *   - Granular media permissions replace the old storage ones
 *   - WRITE_EXTERNAL_STORAGE is ignored (maxSdkVersion=32 in manifest)
 *   - Falls back to Directory.EXTERNAL (app-scoped, no permission needed)
 *     which is visible via USB at Android/data/com.threecats.lsp.dplanner/files/
 *
 * Both paths then open the native Share sheet so the user can also send
 * the file to Downloads, Drive, email, etc.
 */

(function () {
  if (!window.Capacitor || !window.Capacitor.isNativePlatform()) return;

  const FS = 'Filesystem';
  const SH = 'Share';

  // Helper: blob → base64 string (strip data: prefix)
  function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result.split(',')[1]);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  // Toast — red for errors, cyan for info
  function notify(msg, isError) {
    console.log('[CapBridge]', msg);
    if (typeof window.showExportToast === 'function') {
      window.showExportToast(msg);
      return;
    }
    const div = document.createElement('div');
    div.textContent = msg;
    const bg = isError ? 'rgba(220,50,50,0.95)' : 'rgba(0,200,255,0.92)';
    const fg = isError ? '#fff' : '#000';
    div.style.cssText = [
      'position:fixed', 'bottom:24px', 'left:50%', 'transform:translateX(-50%)',
      'background:' + bg, 'color:' + fg, 'padding:10px 22px',
      'border-radius:20px', 'font-size:13px', 'z-index:99999',
      'pointer-events:none', 'max-width:85vw', 'text-align:center',
      'font-family:sans-serif', 'line-height:1.4'
    ].join(';');
    document.body.appendChild(div);
    setTimeout(() => div.remove(), isError ? 5000 : 3500);
  }

  // Request storage permission via Filesystem plugin.
  // Returns true if granted (or not needed), false if denied.
  async function requestStoragePermission() {
    const plugin = Capacitor.Plugins[FS];
    if (!plugin || typeof plugin.requestPermissions !== 'function') {
      console.log('[CapBridge] requestPermissions not available — assuming granted');
      return true;
    }
    try {
      const result = await plugin.requestPermissions();
      console.log('[CapBridge] permission result:', JSON.stringify(result));
      // result.publicStorage = 'granted' | 'denied' | 'prompt'
      const status = result && result.publicStorage;
      if (status === 'denied') {
        notify('Storage permission denied — cannot save file', true);
        return false;
      }
      return true;
    } catch (err) {
      // On Android 13+ requestPermissions may throw — that's fine, EXTERNAL works without it
      console.warn('[CapBridge] requestPermissions threw (likely API 33+):', err);
      return true;
    }
  }

  // Try writing to a directory. Returns file:// URI or null.
  async function tryWrite(base64Data, filename, directory) {
    try {
      const result = await Capacitor.Plugins[FS].writeFile({
        path: filename,
        data: base64Data,
        directory: directory,
        recursive: true
      });
      console.log('[CapBridge] write OK dir=' + directory + ' uri=' + result.uri);
      return result.uri;
    } catch (err) {
      const msg = err && err.message ? err.message : String(err);
      console.warn('[CapBridge] write FAILED dir=' + directory + ':', msg);
      return null;
    }
  }

  // Share sheet for a file:// URI
  async function shareFile(fileUri, filename) {
    const plugin = Capacitor.Plugins[SH];
    if (!plugin || typeof plugin.share !== 'function') {
      notify('Share plugin not available', true);
      return;
    }
    try {
      await plugin.share({ title: filename, url: fileUri, dialogTitle: 'Save ' + filename });
    } catch (err) {
      const msg = err && err.message ? err.message : String(err);
      if (!msg.toLowerCase().includes('cancel') && !msg.toLowerCase().includes('dismiss')) {
        notify('Share error: ' + msg, true);
      }
    }
  }

  // Main export handler
  async function saveAndOpen(blob, filename) {
    let base64Data;
    try {
      base64Data = await blobToBase64(blob);
    } catch (err) {
      notify('Export failed: cannot read file — ' + err, true);
      return;
    }

    // Request permission first (shows dialog on Android ≤ 12 if not yet granted)
    const hasPermission = await requestStoragePermission();
    if (!hasPermission) return;

    // Try DOCUMENTS first (visible in Files/Downloads on Android ≤ 12)
    let fileUri = await tryWrite(base64Data, filename, 'DOCUMENTS');
    let savedTo = 'Documents';

    if (!fileUri) {
      // Fallback: app-scoped External (no permission, always works, USB-visible)
      fileUri = await tryWrite(base64Data, filename, 'EXTERNAL');
      savedTo = 'device storage (Android/data/com.threecats.lsp.dplanner/files/)';
    }

    if (!fileUri) {
      // Last resort: Cache
      fileUri = await tryWrite(base64Data, filename, 'CACHE');
      savedTo = 'app cache (use share to save permanently)';
    }

    if (!fileUri) {
      notify('Export failed — could not write file to any location', true);
      return;
    }

    notify('Saved to ' + savedTo + ': ' + filename);

    // Open share sheet — lets user also send to Downloads, Drive, etc.
    await shareFile(fileUri, filename);
  }

  // Patch HTMLAnchorElement.prototype.click
  const _origClick = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    if (this.download && this.href && this.href.startsWith('blob:')) {
      fetch(this.href)
        .then(r => r.blob())
        .then(blob => saveAndOpen(blob, this.download))
        .catch(err => {
          notify('Export failed: ' + err, true);
          _origClick.call(this);
        });
      return;
    }
    _origClick.call(this);
  };

  console.log('[CapBridge] Bridge active — DOCUMENTS→EXTERNAL→CACHE, runtime permission');
})();
