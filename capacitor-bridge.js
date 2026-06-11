/**
 * capacitor-bridge.js
 *
 * Intercepts blob <a download> clicks produced by exportTXT() and exportPDF()
 * and saves the file to the device's Documents directory via @capacitor/filesystem
 * when running inside the Android app. After saving, immediately opens the file
 * with the system viewer via @capawesome-team/capacitor-file-opener.
 *
 * On the web / PWA this file does nothing — the normal <a download> path runs as-is.
 *
 * HOW IT WORKS
 * ------------
 * exportTXT / exportPDF both do:
 *   const a = document.createElement('a');
 *   a.href = URL.createObjectURL(blob);
 *   a.download = 'filename.ext';
 *   document.body.appendChild(a);
 *   a.click();            <-- we intercept this
 *   document.body.removeChild(a);
 *   URL.revokeObjectURL(a.href);
 *
 * We patch HTMLAnchorElement.prototype.click so that when:
 *   - Capacitor is present (i.e. we are in the Android app), AND
 *   - the anchor has a `download` attribute, AND
 *   - the href is a blob: URL
 * we read the blob, base64-encode it, write it via Filesystem.writeFile to
 * Directory.DOCUMENTS, then open it with FileOpener.
 */

(function () {
  // Only activate inside Capacitor (Android app)
  if (!window.Capacitor || !window.Capacitor.isNativePlatform()) return;

  const FS = 'Filesystem';
  const FO = 'CapacitorFileOpener'; // plugin registration name for file-opener v6

  // Helper: read a blob as base64 string
  function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        // result is "data:<mime>;base64,<data>" — strip the prefix
        resolve(reader.result.split(',')[1]);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  // Helper: derive MIME type from filename extension
  function mimeFromFilename(name) {
    if (name.endsWith('.pdf'))  return 'application/pdf';
    if (name.endsWith('.txt'))  return 'text/plain';
    return 'application/octet-stream';
  }

  // Helper: show a brief toast (reuses app's showExportToast if available)
  function notify(msg) {
    if (typeof window.showExportToast === 'function') {
      window.showExportToast(msg);
      return;
    }
    const div = document.createElement('div');
    div.textContent = msg;
    div.style.cssText = [
      'position:fixed', 'bottom:24px', 'left:50%', 'transform:translateX(-50%)',
      'background:rgba(0,200,255,0.92)', 'color:#000', 'padding:8px 20px',
      'border-radius:20px', 'font-size:13px', 'z-index:99999',
      'pointer-events:none', 'max-width:80vw', 'text-align:center'
    ].join(';');
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 3000);
  }

  // Save blob to Documents/<filename>, then open it with the system viewer
  async function saveAndOpen(blob, filename) {
    const mime = mimeFromFilename(filename);

    // 1 — Write to Documents
    let savedPath;
    try {
      const base64Data = await blobToBase64(blob);
      const result = await Capacitor.Plugins[FS].writeFile({
        path: filename,
        data: base64Data,
        directory: 'DOCUMENTS',
        recursive: true
      });
      savedPath = result.uri; // absolute file:// URI returned by Filesystem
    } catch (err) {
      console.error('[CapBridge] writeFile failed:', err);
      // Last-resort fallback: native share sheet
      try {
        const url = URL.createObjectURL(blob);
        await Capacitor.Plugins['Share'].share({
          title: filename,
          url,
          dialogTitle: 'Save or share file'
        });
        URL.revokeObjectURL(url);
      } catch (shareErr) {
        console.error('[CapBridge] share fallback failed:', shareErr);
        notify('Save failed — try copying to clipboard instead');
      }
      return;
    }

    notify(`Saved: ${filename}`);

    // 2 — Open the file immediately with the system viewer
    try {
      await Capacitor.Plugins[FO].openFile({
        path: savedPath,
        mimeType: mime
      });
    } catch (openErr) {
      // Not fatal — file is already saved, viewer just didn't open
      console.warn('[CapBridge] FileOpener failed (file still saved):', openErr);
    }
  }

  // Patch HTMLAnchorElement.prototype.click to intercept blob downloads
  const _origClick = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    if (this.download && this.href && this.href.startsWith('blob:')) {
      fetch(this.href)
        .then(r => r.blob())
        .then(blob => saveAndOpen(blob, this.download))
        .catch(err => {
          console.error('[CapBridge] blob fetch failed:', err);
          _origClick.call(this);
        });
      return; // don't call original — we're handling it
    }
    _origClick.call(this);
  };

  console.log('[CapBridge] Filesystem + FileOpener bridge active');
})();
