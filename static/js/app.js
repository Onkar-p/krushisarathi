/**
 * app.js — KrushiSarathi Frontend (Animated + Camera)
 */

// ═══════════════════════════════════════════════════════════════
//  INITIALIZATION
// ═══════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initTypingEffect();
    initStatCounters();
    initTabIndicator();
    loadSchemes();
    loadYieldMeta();
});

// ═══════════════════════════════════════════════════════════════
//  BACKGROUND PARTICLES
// ═══════════════════════════════════════════════════════════════
function initParticles() {
    const container = document.getElementById('bgParticles');
    const colors = ['#52b788', '#74c69d', '#95d5b2', '#b7e4c7', '#40916c'];
    for (let i = 0; i < 25; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 12 + 4;
        p.style.cssText = `
            width: ${size}px; height: ${size}px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            left: ${Math.random() * 100}%;
            animation-duration: ${Math.random() * 15 + 10}s;
            animation-delay: ${Math.random() * 10}s;
        `;
        container.appendChild(p);
    }
}

// ═══════════════════════════════════════════════════════════════
//  TYPING EFFECT
// ═══════════════════════════════════════════════════════════════
function initTypingEffect() {
    const phrases = [
        'Detect Crop Diseases with AI',
        'Explore Government Schemes for Farmers',
        'Predict Crop Yield with Smart Analytics',
        'Capture Leaf Photos Directly from Camera',
    ];
    const el = document.getElementById('typingText');
    let phraseIdx = 0, charIdx = 0, deleting = false;

    function type() {
        const phrase = phrases[phraseIdx];
        if (!deleting) {
            el.textContent = phrase.substring(0, charIdx + 1);
            charIdx++;
            if (charIdx === phrase.length) {
                setTimeout(() => { deleting = true; type(); }, 2000);
                return;
            }
        } else {
            el.textContent = phrase.substring(0, charIdx - 1);
            charIdx--;
            if (charIdx === 0) {
                deleting = false;
                phraseIdx = (phraseIdx + 1) % phrases.length;
            }
        }
        setTimeout(type, deleting ? 30 : 60);
    }
    type();
}

// ═══════════════════════════════════════════════════════════════
//  STAT COUNTERS
// ═══════════════════════════════════════════════════════════════
function initStatCounters() {
    document.querySelectorAll('.stat-number').forEach(el => {
        const target = parseInt(el.getAttribute('data-count'));
        animateCounter(el, 0, target, 1500);
    });
}

function animateCounter(el, start, end, duration) {
    const startTime = performance.now();
    function update(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + (end - start) * eased);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// ═══════════════════════════════════════════════════════════════
//  TAB NAVIGATION
// ═══════════════════════════════════════════════════════════════
function initTabIndicator() {
    const tabs = document.querySelectorAll('.tab-btn');
    const indicator = document.getElementById('tabIndicator');
    const activeTab = document.querySelector('.tab-btn.active');
    if (activeTab && indicator) {
        indicator.style.width = activeTab.offsetWidth + 'px';
        indicator.style.left = activeTab.offsetLeft + 'px';
    }
}

document.querySelectorAll('.tab-btn').forEach((btn, idx) => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(btn.getAttribute('data-tab')).classList.add('active');

        // Move indicator
        const indicator = document.getElementById('tabIndicator');
        if (indicator) {
            indicator.style.width = btn.offsetWidth + 'px';
            indicator.style.left = btn.offsetLeft + 'px';
        }
    });
});

// Handle resize for tab indicator
window.addEventListener('resize', initTabIndicator);

// ═══════════════════════════════════════════════════════════════
//  TOAST NOTIFICATION
// ═══════════════════════════════════════════════════════════════
function showToast(message, icon = 'info') {
    const toast = document.getElementById('toast');
    const iconMap = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    document.getElementById('toastIcon').textContent = iconMap[icon] || iconMap.info;
    document.getElementById('toastMsg').textContent = message;
    toast.classList.add('visible');
    setTimeout(() => toast.classList.remove('visible'), 3500);
}

// ═══════════════════════════════════════════════════════════════
//  TAB 1 — DISEASE DETECTION
// ═══════════════════════════════════════════════════════════════
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');
const fileNameEl = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultPanel = document.getElementById('resultPanel');
const resultPlaceholder = document.getElementById('resultPlaceholder');

let selectedFile = null;
let cameraStream = null;

// ─── Input Mode Toggle ──────────────────────────────────────────
function switchInputMode(mode) {
    document.getElementById('toggleUpload').classList.toggle('active', mode === 'upload');
    document.getElementById('toggleCamera').classList.toggle('active', mode === 'camera');

    document.getElementById('uploadMode').classList.toggle('active', mode === 'upload');
    document.getElementById('cameraMode').classList.toggle('active', mode === 'camera');

    // Stop camera if switching away
    if (mode === 'upload' && cameraStream) stopCamera();
}

// ─── File Upload ─────────────────────────────────────────────────
uploadArea.addEventListener('click', () => imageInput.click());

uploadArea.addEventListener('dragover', e => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});
uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
uploadArea.addEventListener('drop', e => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
});

imageInput.addEventListener('change', () => {
    if (imageInput.files.length > 0) handleFile(imageInput.files[0]);
});

function handleFile(file) {
    if (!file.type.match('image.*')) {
        showToast('Please upload a valid image (JPG, PNG)', 'error');
        return;
    }
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = e => {
        previewImage.src = e.target.result;
        previewContainer.style.display = 'block';
        fileNameEl.textContent = file.name;
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
    showToast('Image loaded! Click Analyze to detect disease.', 'success');
}

// ─── Camera ──────────────────────────────────────────────────────
async function startCamera() {
    try {
        // Enumerate cameras
        const devices = await navigator.mediaDevices.enumerateDevices();
        const cameras = devices.filter(d => d.kind === 'videoinput');
        const cameraSelect = document.getElementById('cameraSelect');

        if (cameras.length > 1) {
            cameraSelect.innerHTML = cameras.map((c, i) =>
                `<option value="${c.deviceId}">${c.label || 'Camera ' + (i + 1)}</option>`
            ).join('');
            cameraSelect.style.display = 'block';
            cameraSelect.onchange = () => startCameraWithDevice(cameraSelect.value);
        }

        // Prefer back camera on mobile
        const constraints = {
            video: {
                facingMode: { ideal: 'environment' },
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        };

        cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
        const video = document.getElementById('cameraFeed');
        video.srcObject = cameraStream;
        video.classList.add('active');

        document.getElementById('cameraPlaceholder').classList.add('hidden');
        document.getElementById('cameraOverlay').classList.add('active');
        document.getElementById('startCameraBtn').style.display = 'none';
        document.getElementById('captureBtn').style.display = 'flex';
        document.getElementById('stopCameraBtn').style.display = 'flex';

        showToast('Camera started! Point at a leaf and capture.', 'success');
    } catch (err) {
        showToast('Camera access denied or not available.', 'error');
        console.error('Camera error:', err);
    }
}

async function startCameraWithDevice(deviceId) {
    if (cameraStream) cameraStream.getTracks().forEach(t => t.stop());
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: { exact: deviceId }, width: { ideal: 1280 }, height: { ideal: 720 } }
        });
        document.getElementById('cameraFeed').srcObject = cameraStream;
    } catch (err) {
        showToast('Failed to switch camera.', 'error');
    }
}

function capturePhoto() {
    const video = document.getElementById('cameraFeed');
    const canvas = document.getElementById('cameraCanvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    // Flash effect
    const container = document.getElementById('cameraContainer');
    container.style.transition = 'none';
    container.style.filter = 'brightness(2)';
    setTimeout(() => {
        container.style.transition = 'filter 0.3s';
        container.style.filter = 'brightness(1)';
    }, 100);

    canvas.toBlob(blob => {
        selectedFile = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
        previewImage.src = canvas.toDataURL('image/jpeg');
        previewContainer.style.display = 'block';
        fileNameEl.textContent = 'Camera Capture';
        analyzeBtn.disabled = false;

        // Show retake, hide capture
        document.getElementById('captureBtn').style.display = 'none';
        document.getElementById('retakeBtn').style.display = 'flex';

        showToast('Photo captured! Click Analyze to detect disease.', 'success');
    }, 'image/jpeg', 0.9);
}

function retakePhoto() {
    previewContainer.style.display = 'none';
    analyzeBtn.disabled = true;
    selectedFile = null;
    document.getElementById('captureBtn').style.display = 'flex';
    document.getElementById('retakeBtn').style.display = 'none';
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(t => t.stop());
        cameraStream = null;
    }
    const video = document.getElementById('cameraFeed');
    video.srcObject = null;
    video.classList.remove('active');

    document.getElementById('cameraPlaceholder').classList.remove('hidden');
    document.getElementById('cameraOverlay').classList.remove('active');
    document.getElementById('startCameraBtn').style.display = 'flex';
    document.getElementById('captureBtn').style.display = 'none';
    document.getElementById('retakeBtn').style.display = 'none';
    document.getElementById('stopCameraBtn').style.display = 'none';
    document.getElementById('cameraSelect').style.display = 'none';
}

// ─── Analyze Button ──────────────────────────────────────────────
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    analyzeBtn.disabled = true;
    analyzeBtn.classList.add('loading');
    resultPanel.classList.remove('visible');
    resultPlaceholder.style.display = 'none';
    hideError('diseaseError');

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
        const response = await fetch('/api/detect-disease', { method: 'POST', body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Analysis failed.');
        displayDiseaseResult(data);
        showToast('Disease analysis complete!', 'success');
    } catch (err) {
        showError('diseaseError', err.message);
        resultPlaceholder.style.display = 'block';
        showToast('Analysis failed: ' + err.message, 'error');
    } finally {
        analyzeBtn.classList.remove('loading');
        analyzeBtn.disabled = false;
    }
});

function displayDiseaseResult(data) {
    const info = data.disease_info || {};
    const isHealthy = data.prediction.toLowerCase().includes('healthy');
    const severity = (info.severity || 'Unknown').toLowerCase();

    // Header styling
    const header = document.getElementById('resultHeader');
    header.className = 'result-header';
    if (isHealthy) header.classList.add('card-success');
    else if (severity.includes('very high')) header.classList.add('card-danger');
    else header.classList.add('card-warning');

    // Emoji
    const emoji = isHealthy ? '✅' : (severity.includes('very high') ? '🚨' : '⚠️');
    document.getElementById('resultEmoji').textContent = emoji;

    // Title
    document.getElementById('resultTitle').textContent =
        `${info.crop || ''} — ${info.disease || data.display_name}`;

    // Severity badge
    let badgeClass = 'severity-moderate';
    if (severity.includes('none')) badgeClass = 'severity-none';
    else if (severity.includes('very high')) badgeClass = 'severity-veryhigh';
    else if (severity.includes('high')) badgeClass = 'severity-high';

    document.getElementById('resultConfidence').innerHTML =
        `Confidence: <strong>${data.confidence}%</strong>
         <span class="severity-badge ${badgeClass}">${info.severity || 'N/A'}</span>`;

    // Content
    document.getElementById('resultCause').innerHTML = info.cause || 'N/A';
    fillList('resultSymptoms', info.symptoms || []);
    fillList('resultManagement', info.management || []);

    // Top-5 chart
    const chartDiv = document.getElementById('top5Chart');
    chartDiv.innerHTML = '';
    (data.top5 || []).forEach((item, i) => {
        const div = document.createElement('div');
        div.className = 'bar-item';
        div.style.animationDelay = `${i * 0.1}s`;
        div.innerHTML = `
            <span class="bar-label" title="${item.display_name}">${item.display_name}</span>
            <div class="bar-track">
                <div class="bar-fill" style="width: 0%;"></div>
            </div>
            <span class="bar-value">${item.confidence}%</span>
        `;
        chartDiv.appendChild(div);
        // Animate bar fill after DOM insert
        setTimeout(() => {
            div.querySelector('.bar-fill').style.width = item.confidence + '%';
        }, 100 + i * 100);
    });

    resultPanel.classList.add('visible');
    resultPlaceholder.style.display = 'none';
}

function fillList(elementId, items) {
    const ul = document.getElementById(elementId);
    ul.innerHTML = '';
    items.forEach(text => {
        const li = document.createElement('li');
        li.textContent = text;
        ul.appendChild(li);
    });
}


// ═══════════════════════════════════════════════════════════════
//  TAB 2 — GOVERNMENT SCHEMES
// ═══════════════════════════════════════════════════════════════
let allSchemes = [];

async function loadSchemes() {
    try {
        const res = await fetch('/api/schemes');
        const data = await res.json();
        allSchemes = data.schemes;

        const select = document.getElementById('categoryFilter');
        select.innerHTML = '<option value="">All Categories</option>';
        data.categories.forEach(cat => {
            select.innerHTML += `<option value="${cat}">${cat}</option>`;
        });
        renderSchemes(allSchemes);
    } catch (err) {
        console.error('Failed to load schemes:', err);
    }
}

document.getElementById('categoryFilter').addEventListener('change', filterSchemes);
document.getElementById('searchInput').addEventListener('input', debounce(filterSchemes, 300));

function filterSchemes() {
    const cat = document.getElementById('categoryFilter').value.toLowerCase();
    const query = document.getElementById('searchInput').value.toLowerCase().trim();
    let filtered = allSchemes;
    if (cat) filtered = filtered.filter(s => s.category.toLowerCase() === cat);
    if (query) filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(query) ||
        s.description.toLowerCase().includes(query) ||
        s.category.toLowerCase().includes(query)
    );
    renderSchemes(filtered);
}

function renderSchemes(schemes) {
    document.getElementById('schemeCount').textContent = `Showing ${schemes.length} scheme(s)`;
    const container = document.getElementById('schemesList');
    container.innerHTML = schemes.map((s, i) => `
        <div class="scheme-card" id="scheme-${i}" style="animation-delay:${i * 0.05}s">
            <div class="scheme-header" onclick="toggleScheme(${i})">
                <h3>${s.icon} ${s.name} <span class="category-tag">${s.category}</span></h3>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="scheme-body">
                <p class="ministry">${s.ministry}</p>
                <p class="description">${s.description}</p>
                <div class="scheme-grid">
                    <div>
                        <h4>✅ Key Benefits</h4>
                        <ul>${s.benefits.map(b => `<li>${b}</li>`).join('')}</ul>
                    </div>
                    <div>
                        <h4>👤 Eligibility</h4>
                        <ul>${s.eligibility.map(e => `<li>${e}</li>`).join('')}</ul>
                    </div>
                </div>
                <div class="apply-section">
                    <h4>📝 How to Apply</h4>
                    <ol>${s.how_to_apply.map(h => `<li>${h}</li>`).join('')}</ol>
                </div>
                <a href="${s.website}" target="_blank" rel="noopener" class="scheme-link">
                    🔗 Visit Official Website →
                </a>
            </div>
        </div>
    `).join('');
}

function toggleScheme(index) {
    document.getElementById(`scheme-${index}`).classList.toggle('expanded');
}


// ═══════════════════════════════════════════════════════════════
//  TAB 3 — YIELD PREDICTION
// ═══════════════════════════════════════════════════════════════

// Range slider live values
const rangeConfig = {
    temp: { suffix: '°C' },
    rain: { suffix: ' mm' },
    humidity: { suffix: '%' },
    ph: { suffix: '' },
};

Object.keys(rangeConfig).forEach(name => {
    const range = document.getElementById(`${name}Range`);
    const display = document.getElementById(`${name}Value`);
    if (range && display) {
        range.addEventListener('input', () => {
            display.textContent = range.value + rangeConfig[name].suffix;
        });
    }
});

async function loadYieldMeta() {
    try {
        const res = await fetch('/api/yield-meta');
        const data = await res.json();

        ['cropSelect', 'compareCrop'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.innerHTML = data.crops.map(c => `<option value="${c}">${c}</option>`).join('');
            }
        });

        const soilEl = document.getElementById('soilSelect');
        if (soilEl) soilEl.innerHTML = data.soils.map(s => `<option value="${s}">${s}</option>`).join('');
    } catch (err) {
        console.error('Failed to load yield meta:', err);
    }
}

// Predict
document.getElementById('predictBtn').addEventListener('click', async () => {
    const btn = document.getElementById('predictBtn');
    btn.disabled = true;
    btn.classList.add('loading');
    document.getElementById('yieldResult').classList.remove('visible');
    document.getElementById('yieldPlaceholder').style.display = 'none';
    hideError('yieldError');

    const payload = {
        crop: document.getElementById('cropSelect').value,
        soil: document.getElementById('soilSelect').value,
        temperature: parseFloat(document.getElementById('tempRange').value),
        rainfall: parseFloat(document.getElementById('rainRange').value),
        humidity: parseFloat(document.getElementById('humidityRange').value),
        ph: parseFloat(document.getElementById('phRange').value),
        nitrogen: parseFloat(document.getElementById('nitrogenInput').value),
        phosphorus: parseFloat(document.getElementById('phosphorusInput').value),
        potassium: parseFloat(document.getElementById('potassiumInput').value),
    };

    try {
        const res = await fetch('/api/predict-yield', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Prediction failed.');
        displayYieldResult(data, payload);
        showToast(`Predicted yield: ${data.predicted_yield} t/ha`, 'success');
    } catch (err) {
        showError('yieldError', err.message);
        document.getElementById('yieldPlaceholder').style.display = 'block';
        showToast('Prediction failed', 'error');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

function displayYieldResult(data, payload) {
    // Animated value
    const valEl = document.getElementById('yieldValue');
    animateValue(valEl, 0, data.predicted_yield, 1200);

    // Ring animation
    const ring = document.getElementById('yieldRing');
    const maxYield = Math.max(80, data.predicted_yield * 1.5);
    const pct = Math.min(data.predicted_yield / maxYield, 1);
    const circumference = 2 * Math.PI * 52; // r=52
    ring.style.strokeDashoffset = circumference * (1 - pct);

    document.getElementById('yieldCrop').textContent = `${data.crop} on ${data.soil} soil`;

    // Summary table
    const tbody = document.querySelector('#summaryTable tbody');
    tbody.innerHTML = [
        ['Crop', payload.crop], ['Soil Type', payload.soil],
        ['Temperature', `${payload.temperature}°C`], ['Rainfall', `${payload.rainfall} mm`],
        ['Humidity', `${payload.humidity}%`], ['Soil pH', payload.ph],
        ['Nitrogen', `${payload.nitrogen} kg/ha`], ['Phosphorus', `${payload.phosphorus} kg/ha`],
        ['Potassium', `${payload.potassium} kg/ha`],
    ].map(([k, v]) => `<tr><td>${k}</td><td><strong>${v}</strong></td></tr>`).join('');

    // Feature importance
    const impChart = document.getElementById('importanceChart');
    impChart.innerHTML = '';
    const maxImp = Math.max(...data.importances.map(i => i.importance));
    data.importances.forEach((item, i) => {
        const pctBar = (item.importance / maxImp * 100).toFixed(1);
        const div = document.createElement('div');
        div.className = 'bar-item';
        div.style.animationDelay = `${i * 0.08}s`;
        div.innerHTML = `
            <span class="bar-label">${item.feature}</span>
            <div class="bar-track"><div class="bar-fill" style="width:0%;"></div></div>
            <span class="bar-value">${(item.importance * 100).toFixed(1)}%</span>
        `;
        impChart.appendChild(div);
        setTimeout(() => div.querySelector('.bar-fill').style.width = pctBar + '%', 100 + i * 80);
    });

    // Recommendations
    const recDiv = document.getElementById('recommendations');
    if (data.recommendations.length > 0) {
        recDiv.innerHTML = '<h4 class="result-sub-title"><span>💡</span> Recommendations</h4>';
        data.recommendations.forEach((r, i) => {
            const icon = r.type === 'warning' ? '🔸' : '🔹';
            recDiv.innerHTML += `<div class="recommendation ${r.type}" style="animation-delay:${i * 0.1}s">${icon} ${r.text}</div>`;
        });
    } else {
        recDiv.innerHTML = `<div class="recommendation success" style="margin-top:1rem;">
            ✅ All parameters look good! Conditions are favorable for this crop.
        </div>`;
    }

    document.getElementById('yieldResult').classList.add('visible');
    document.getElementById('yieldPlaceholder').style.display = 'none';
}

// Compare soils
document.getElementById('compareBtn').addEventListener('click', async () => {
    const crop = document.getElementById('compareCrop').value;
    const btn = document.getElementById('compareBtn');
    btn.disabled = true; btn.textContent = 'Loading...';

    try {
        const res = await fetch('/api/compare-soils', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ crop }),
        });
        const data = await res.json();

        const chart = document.getElementById('compareChart');
        chart.innerHTML = '';
        const maxY = Math.max(...data.results.map(r => r.yield));
        data.results.forEach((r, i) => {
            const pct = (r.yield / maxY * 100).toFixed(1);
            const div = document.createElement('div');
            div.className = 'bar-item';
            div.style.animationDelay = `${i * 0.06}s`;
            div.innerHTML = `
                <span class="bar-label">${r.soil}</span>
                <div class="bar-track"><div class="bar-fill" style="width:0%;"></div></div>
                <span class="bar-value">${r.yield} t/ha</span>
            `;
            chart.appendChild(div);
            setTimeout(() => div.querySelector('.bar-fill').style.width = pct + '%', 100 + i * 60);
        });
    } catch (err) {
        console.error('Compare failed:', err);
    } finally {
        btn.disabled = false; btn.textContent = 'Compare';
    }
});


// ═══════════════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════════════
function showError(id, msg) {
    const el = document.getElementById(id);
    el.textContent = '⚠️ ' + msg;
    el.classList.add('visible');
}

function hideError(id) {
    document.getElementById(id).classList.remove('visible');
}

function debounce(fn, delay) {
    let timer;
    return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}

function animateValue(el, start, end, duration) {
    const startTime = performance.now();
    function update(now) {
        const progress = Math.min((now - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = (start + (end - start) * eased).toFixed(2);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}
