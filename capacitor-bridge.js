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
 * TXT files:
 *   - Write to Directory.CACHE → open with FileOpener (app chooser appears) ✓
 *
 * PDF files (extra reliable path):
 *   - Write to Directory.CACHE (for immediate viewing attempt)
 *   - ALSO write to Directory.External (app-scoped:
 *     Android/data/com.threecats.lsp.dplanner/files/) — permanent, accessible
 *     via USB/file manager even if no viewer opens
 *   - Try FileOpener first; if that throws ActivityNotFoundException or similar,
 *     fall back to @capacitor/share Share sheet so user can save to Drive/Files/etc.
 *
 * No WRITE_EXTERNAL_STORAGE permission needed for Cache or app-scoped External
 * on Android 11+ (targetSdk 34, minSdk 22).
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
 * Directory.Cache, then open it with FileOpener (with Share sheet fallback for PDF).
 */

(function () {
  // Only activate inside Capacitor (Android app)
  if (!window.Capacitor || !window.Capacitor.isNativePlatform()) return;

  const FS = 'Filesystem';
  const FO = 'FileOpener'; // plugin registration name — @CapacitorPlugin(name = "FileOpener")
  const SH = 'Share';      // @capacitor/share — registration name = "Share"

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

  // Write base64 data to a given Capacitor directory.
  // Returns the absolute URI string, or null on failure.
  async function writeToDir(base64Data, filename, directory) {
    try {
      const result = await Capacitor.Plugins[FS].writeFile({
        path: filename,
        data: base64Data,
        directory: directory,
        recursive: true
      });
      return result.uri;
    } catch (err) {
      console.warn('[CapBridge] writeFile to', directory, 'failed:', err);
      return null;
    }
  }

  // Try to open a file with the system viewer via FileOpener.
  // Returns true if it succeeded, false otherwise.
  async function tryOpenFile(uri, mime) {
    try {
      await Capacitor.Plugins[FO].openFile({ path: uri, mimeType: mime });
      return true;
    } catch (err) {
      console.warn('[CapBridge] FileOpener failed for', mime, ':', err);
      return false;
    }
  }

  // Try the native Share sheet so the user can save to Files / Drive / etc.
  // Returns true if Share plugin is available and share() was called.
  async function tryShare(uri, filename, mime) {
    const plugin = Capacitor.Plugins[SH];
    if (!plugin || typeof plugin.share !== 'function') {
      console.warn('[CapBridge] Share plugin not available');
      return false;
    }
    try {
      await plugin.share({
        title: filename,
        url: uri,
        dialogTitle: 'Save or share ' + filename
      });
      return true;
    } catch (err) {
      console.warn('[CapBridge] Share failed:', err);
      return false;
    }
  }

  // Main export handler — called for every intercepted blob download.
  async function saveAndOpen(blob, filename) {
    const mime = mimeFromFilename(filename);
    const isPDF = mime === 'application/pdf';

    // Encode blob once
    let base64Data;
    try {
      base64Data = await blobToBase64(blob);
    } catch (err) {
      console.error('[CapBridge] blobToBase64 failed:', err);
      notify('Export failed: could not read file data');
      return;
    }

    // --- TXT path: write to CACHE, open with FileOpener ---
    if (!isPDF) {
      const cacheUri = await writeToDir(base64Data, filename, 'CACHE');
      if (!cacheUri) {
        notify('Export failed: could not write file');
        return;
      }
      const opened = await tryOpenFile(cacheUri, mime);
      if (!opened) notify('Saved — install a text viewer app to open .txt files');
      return;
    }

    // --- PDF path: dual-write, FileOpener → Share fallback ---

    // 1. Write to CACHE (for FileOpener / immediate viewing)
    const cacheUri = await writeToDir(base64Data, filename, 'CACHE');
    if (!cacheUri) {
      notify('Export failed: could not write PDF to cache');
      return;
    }

    // 2. Also write to External app directory (permanent copy, survives regardless)
    //    Accessible via: Android/data/com.threecats.lsp.dplanner/files/
    const extUri = await writeToDir(base64Data, filename, 'EXTERNAL');
    if (extUri) {
      console.log('[CapBridge] PDF also saved to External:', extUri);
    }

    // 3. Try FileOpener first (opens PDF viewer if installed)
    const opened = await tryOpenFile(cacheUri, mime);
    if (opened) return; // success — viewer opened

    // 4. FileOpener failed — try Share sheet as fallback
    //    Share sheet lets user save to Files, Drive, email, etc.
    notify('Opening share options…');
    const shared = await tryShare(cacheUri, filename, mime);
    if (shared) return;

    // 5. Both failed — but the file IS saved permanently to External
    if (extUri) {
      notify('PDF saved to Android/data/com.threecats.lsp.dplanner/files/' + filename);
    } else {
      notify('PDF saved to app cache — use a file manager to retrieve it');
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

  console.log('[CapBridge] Filesystem bridge active (Cache + External dual-write for PDF)');
})();
