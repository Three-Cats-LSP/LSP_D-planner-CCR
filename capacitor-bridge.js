/**
 * capacitor-bridge.js
 *
 * Intercepts blob <a download> clicks produced by exportTXT() and exportPDF()
 * and saves the file via @capacitor/filesystem, then opens it with the system
 * viewer via @capawesome-team/capacitor-file-opener.
 *
 * On the web / PWA this file does nothing — the normal <a download> path runs as-is.
 *
 * ANDROID STORAGE STRATEGY
 * -------------------------
 * Directory.Documents  — broken on Android 11+ (requires MANAGE_EXTERNAL_STORAGE)
 * Directory.ExternalStorage — broken on Android 11+ (same issue)
 * Directory.External   — app-scoped external dir, works but hard for users to find
 * Directory.Cache      — always works, no permissions needed, any Android version ✓
 *
 * We write to Cache, then immediately open with FileOpener so the user can view
 * the file and use "Save to Downloads / Share" from the system viewer.
 * This is the standard pattern for modern Android export flows.
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
 * Directory.Cache, then open it with FileOpener.
 */

(function () {
  // Only activate inside Capacitor (Android app)
  if (!window.Capacitor || !window.Capacitor.isNativePlatform()) return;

  const FS = 'Filesystem';
  const FO = 'FileOpener'; // plugin registration name — @CapacitorPlugin(name = "FileOpener")

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

  // Write blob to Cache directory, then open with system viewer.
  // Cache works on all Android versions without any storage permissions.
  // The user can Save / Share from the system viewer (PDF viewer, text editor, etc.)
  async function saveAndOpen(blob, filename) {
    const mime = mimeFromFilename(filename);

    // 1 — Write to Cache (no permissions required on any Android version)
    let savedPath;
    try {
      const base64Data = await blobToBase64(blob);
      const result = await Capacitor.Plugins[FS].writeFile({
        path: filename,
        data: base64Data,
        directory: 'CACHE',   // was 'DOCUMENTS' — broken on Android 11+
        recursive: true
      });
      savedPath = result.uri; // absolute file:// URI returned by Filesystem
    } catch (err) {
      console.error('[CapBridge] writeFile failed:', err);
      notify('Export failed: ' + (err && err.message ? err.message : err));
      return;
    }

    // 2 — Open immediately with system viewer so user can save/share from there
    try {
      await Capacitor.Plugins[FO].openFile({
        path: savedPath,
        mimeType: mime
      });
    } catch (openErr) {
      // FileOpener failed but file is in cache — show path as fallback info
      console.warn('[CapBridge] FileOpener failed:', openErr);
      notify('File saved — could not open viewer');
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

  console.log('[CapBridge] Filesystem bridge active (Cache directory)');
})();
