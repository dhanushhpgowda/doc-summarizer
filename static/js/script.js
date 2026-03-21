/**
 * script.js - DocuSumm AI Frontend Logic
 * ========================================
 * Handles drag-and-drop upload, file preview, loading states,
 * password toggles, and admin table filtering.
 */

/* ── Flash auto-dismiss ──────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(1rem)';
      flash.style.transition = 'all .3s ease';
      setTimeout(() => flash.remove(), 300);
    }, 5000);
  });
});


/* ── Drag-and-drop upload ────────────────────────────────────────────────────── */
const dropzone    = document.getElementById('dropzone');
const fileInput   = document.getElementById('fileInput');
const dropContent = document.getElementById('dropzoneContent');
const filePreview = document.getElementById('filePreview');
const uploadActs  = document.getElementById('uploadActions');
const uploadForm  = document.getElementById('uploadForm');
const loadingOverlay = document.getElementById('loadingOverlay');

if (dropzone && fileInput) {

  // Prevent default drag behaviours on window
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
    window.addEventListener(evt, e => e.preventDefault(), false);
  });

  // Highlight on drag-over
  ['dragenter', 'dragover'].forEach(evt => {
    dropzone.addEventListener(evt, () => dropzone.classList.add('drag-over'));
  });
  ['dragleave', 'drop'].forEach(evt => {
    dropzone.addEventListener(evt, () => dropzone.classList.remove('drag-over'));
  });

  // Handle drop
  dropzone.addEventListener('drop', e => {
    const files = e.dataTransfer.files;
    if (files.length) handleFile(files[0]);
  });

  // Handle manual select
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
  });

  // Submit with loading overlay
  if (uploadForm) {
    uploadForm.addEventListener('submit', e => {
      if (!fileInput.files.length) {
        e.preventDefault();
        return;
      }
      showLoading();
    });
  }
}


/**
 * Display a file preview inside the dropzone and show the action buttons.
 * @param {File} file
 */
function handleFile(file) {
  const allowed = ['pdf', 'docx', 'pptx', 'png', 'jpg', 'jpeg'];
  const ext = file.name.split('.').pop().toLowerCase();

  if (!allowed.includes(ext)) {
    alert(`Unsupported file type: .${ext}\nAllowed types: ${allowed.join(', ')}`);
    return;
  }

  // Transfer to the real input so the form can submit it
  const dt = new DataTransfer();
  dt.items.add(file);
  fileInput.files = dt.files;

  // Pick an icon
  const iconMap = {
    pdf:  'fa-file-pdf',
    docx: 'fa-file-word',
    pptx: 'fa-file-powerpoint',
    png:  'fa-file-image',
    jpg:  'fa-file-image',
    jpeg: 'fa-file-image',
  };

  document.getElementById('filePreviewName').textContent = file.name;
  document.getElementById('filePreviewSize').textContent = formatSize(file.size);
  document.getElementById('filePreviewIcon').innerHTML =
    `<i class="fa-solid ${iconMap[ext] || 'fa-file'}"></i>`;

  // Show preview, hide original content
  dropContent.style.display = 'none';
  filePreview.style.display  = 'flex';
  uploadActs.style.display   = 'flex';

  // Disable the invisible file input so only the preview remove btn works
  fileInput.style.pointerEvents = 'none';
}


/** Reset the dropzone to its initial state. */
function clearFile() {
  fileInput.value = '';
  fileInput.style.pointerEvents = '';
  dropContent.style.display = '';
  filePreview.style.display = 'none';
  uploadActs.style.display  = 'none';
  dropzone.classList.remove('drag-over');
}


/** Show the full-screen loading overlay and animate the steps. */
function showLoading() {
  if (!loadingOverlay) return;
  loadingOverlay.style.display = 'grid';

  const steps = [
    'Extracting text…',
    'Cleaning content…',
    'Sending to AI…',
    'Generating summary…',
    'Almost done…',
  ];
  const stepEl = document.getElementById('loadingStep');
  let i = 0;

  setInterval(() => {
    if (i < steps.length) {
      stepEl.textContent = steps[i++];
    }
  }, 2000);
}


/** Format bytes to human-readable string. */
function formatSize(bytes) {
  if (bytes < 1024)       return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}


/* ── Password visibility toggle ──────────────────────────────────────────────── */
/**
 * Toggle the visibility of a password input field.
 * @param {string} inputId - The id of the <input type="password"> element.
 */
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const eyeIcon = document.getElementById(`${inputId}-eye`);
  if (!input) return;

  if (input.type === 'password') {
    input.type = 'text';
    if (eyeIcon) {
      eyeIcon.classList.replace('fa-eye', 'fa-eye-slash');
    }
  } else {
    input.type = 'password';
    if (eyeIcon) {
      eyeIcon.classList.replace('fa-eye-slash', 'fa-eye');
    }
  }
}


/* ── Admin table filter ───────────────────────────────────────────────────────── */
/**
 * Live-filter table rows by matching the query against all cell text.
 * @param {string} tableId - The id of the <table> element.
 * @param {string} query   - The search string.
 */
function filterTable(tableId, query) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const rows = table.querySelectorAll('tbody tr');
  const q = query.toLowerCase();

  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(q) ? '' : 'none';
  });
}


/* ── Smooth scroll helper ────────────────────────────────────────────────────── */
function scrollTo(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth' });
}
