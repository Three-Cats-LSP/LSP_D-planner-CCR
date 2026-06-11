/**
 * capacitor-bridge.js
 *
 * Intercepts blob <a download> clicks produced by exportTXT() and exportPDF()
 * and saves the file via @capacitor/filesystem, then shares via @capacitor/share.
 *
 * On the web / PWA this file does nothing — the normal <a download> path runs as-is.
 *
 * STRATEGY
 * --------
 * 1. Try writing to Directory.EXTERNAL (app-scoped, no permission needed):
 *    /storage/emulated/0/Android/data/com.threecats.lsp.dplanner/files/
 *    File is permanent, visible via USB/file manager.
 *
 * 2. If EXTERNAL fails (storage not mounted, etc.) fall back to Directory.CACHE.
 *    File is temporary but still accessible via Share sheet.
 *
 * 3. Open native Share sheet via @capacitor/share.
 *    Pass file:// URI — Share plugin converts to content:// via FileProvider.
 *    User can save to Downloads, Files, Drive, etc.
 *
 * 4. Show clear error toasts at every failure point so we can debug.
 */

(function () {
  // Only activate inside Capacitor (Android app)
  if (!window.Capacitor || !window.Capacitor.isNativePlatform()) return;

  const FS = 'Filesystem';
  const SH = 'Share';

  // Helper: read a blob as base64 string
  function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result.split(',')[1]);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  // Show a toast — always visible, red for errors
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

  // Try to write base64 data to a Capacitor directory.
  // Returns the file:// URI on success, null on failure.
  async function tryWrite(base64Data, filename, directory) {
    try {
      const result = await Capacitor.Plugins[FS].writeFile({
        path: filename,
        data: base64Data,
        directory: directory,
        recursive: true
      });
      console.log('[CapBridge] writeFile OK dir=' + directory + ' uri=' + result.uri);
      return result.uri; // file:///...absolute path...
    } catch (err) {
      console.warn('[CapBridge] writeFile FAILED dir=' + directory + ':', err);
      return null;
    }
  }

  // Open native share sheet for a file:// URI
  async function shareFile(fileUri, filename) {
    const plugin = Capacitor.Plugins[SH];
    if (!plugin || typeof plugin.share !== 'function') {
      notify('Share plugin not available', true);
      return;
    }
    try {
      console.log('[CapBridge] Share.share url=' + fileUri);
      await plugin.share({
        title: filename,
        url: fileUri,
        dialogTitle: 'Save ' + filename
      });
    } catch (err) {
      // Dismissed or failed — file already saved, that's OK
      const msg = err && err.message ? err.message : String(err);
      console.warn('[CapBridge] Share result:', msg);
      // Only show error if it's not just a cancel
      if (!msg.toLowerCase().includes('cancel') && !msg.toLowerCase().includes('dismiss')) {
        notify('Share error: ' + msg, true);
      }
    }
  }

  // Main handler
  async function saveAndOpen(blob, filename) {
    let base64Data;
    try {
      base64Data = await blobToBase64(blob);
    } catch (err) {
      notify('Export failed: cannot read blob — ' + err, true);
      return;
    }

    // Try EXTERNAL first (permanent, no permission needed, USB-visible)
    let fileUri = await tryWrite(base64Data, filename, 'EXTERNAL');
    let savedTo = 'device storage';

    if (!fileUri) {
      // Fallback to CACHE
      notify('External storage unavailable, using cache…', false);
      fileUri = await tryWrite(base64Data, filename, 'CACHE');
      savedTo = 'app cache';
    }

    if (!fileUri) {
      notify('Export failed: could not write file to device', true);
      return;
    }

    notify('Saved to ' + savedTo + ': ' + filename);

    // Share sheet so user can also send to Downloads/Drive/etc
    await shareFile(fileUri, filename);
  }

  // Patch HTMLAnchorElement.prototype.click to intercept blob downloads
  const _origClick = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    if (this.download && this.href && this.href.startsWith('blob:')) {
      fetch(this.href)
        .then(r => r.blob())
        .then(blob => saveAndOpen(blob, this.download))
        .catch(err => {
          notify('Export failed: blob fetch error — ' + err, true);
          _origClick.call(this);
        });
      return;
    }
    _origClick.call(this);
  };

  console.log('[CapBridge] Bridge active — EXTERNAL→CACHE fallback + Share sheet');
})();
