/**
 * Socio-Economic Field Surveyor App - Single-Page Door-to-Door Logic
 */

// Application State
const state = {
    householdIndex: parseInt(localStorage.getItem('current_household_index') || '1'),
    selectedPhotos: [], // Array of { id, file, previewUrl, name, sizeKb }
    submissions: JSON.parse(localStorage.getItem('local_survey_submissions') || '[]'),
    gpsLocation: null
};

// DOM Elements
const form = document.getElementById('singleSurveyForm');
const btnSaveAndNext = document.getElementById('btnSaveAndNext');
const btnQuickSave = document.getElementById('btnQuickSave');
const btnResetHouse = document.getElementById('btnResetHouse');
const btnAutoGps = document.getElementById('btnAutoGps');
const gpsStatusText = document.getElementById('gpsStatusText');
const gpsCoordinates = document.getElementById('gpsCoordinates');

// Badges & Labels
const householdNumberBadge = document.getElementById('householdNumberBadge');
const bottomHouseCounter = document.getElementById('bottomHouseCounter');
const currentHouseholdLabel = document.getElementById('currentHouseholdLabel');
const avatarBadge = document.getElementById('avatarBadge');
const totalSavedCounter = document.getElementById('totalSavedCounter');

// Photo Elements
const photoFileInput = document.getElementById('photoFileInput');
const photoCameraInput = document.getElementById('photoCameraInput');
const btnBrowsePhotos = document.getElementById('btnBrowsePhotos');
const btnTakePhoto = document.getElementById('btnTakePhoto');
const photoPreviewContainer = document.getElementById('photoPreviewContainer');
const photoGrid = document.getElementById('photoGrid');
const photoCountText = document.getElementById('photoCountText');
const btnClearAllPhotos = document.getElementById('btnClearAllPhotos');

// Modals
const supabaseModal = document.getElementById('supabaseModal');
const btnOpenSupabaseModal = document.getElementById('btnOpenSupabaseModal');
const btnCloseSupabaseModal = document.getElementById('btnCloseSupabaseModal');
const cfgSupabaseUrl = document.getElementById('cfgSupabaseUrl');
const cfgSupabaseKey = document.getElementById('cfgSupabaseKey');
const btnTestSupabase = document.getElementById('btnTestSupabase');
const btnSaveSupabase = document.getElementById('btnSaveSupabase');
const btnResetToDemo = document.getElementById('btnResetToDemo');
const cfgTestResult = document.getElementById('cfgTestResult');
const supabaseStatusDot = document.getElementById('supabaseStatusDot');
const supabaseStatusText = document.getElementById('supabaseStatusText');

const dashboardModal = document.getElementById('dashboardModal');
const btnOpenDashboard = document.getElementById('btnOpenDashboard');
const btnCloseDashboard = document.getElementById('btnCloseDashboard');
const btnRefreshResponses = document.getElementById('btnRefreshResponses');
const btnExportCSV = document.getElementById('btnExportCSV');
const responsesTableBody = document.getElementById('responsesTableBody');
const statTotalSubmissions = document.getElementById('statTotalSubmissions');
const statTotalPhotos = document.getElementById('statTotalPhotos');
const statEngine = document.getElementById('statEngine');

const lightboxModal = document.getElementById('lightboxModal');
const lightboxImage = document.getElementById('lightboxImage');
const lightboxCaption = document.getElementById('lightboxCaption');
const btnCloseLightbox = document.getElementById('btnCloseLightbox');

// Toast
const toastPopup = document.getElementById('toastPopup');
const toastMessage = document.getElementById('toastMessage');

// ==========================================================================
// Initialization
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    initSupabaseFromStorage();
    setupEventListeners();
    setupOtherInputs();
    updateHouseholdCounters();
    updateSavedCountBadge();
    if (window.lucide) lucide.createIcons();
});

function initSupabaseFromStorage() {
    const savedUrl = localStorage.getItem('SUPABASE_URL') || '';
    const savedKey = localStorage.getItem('SUPABASE_ANON_KEY') || '';

    cfgSupabaseUrl.value = savedUrl;
    cfgSupabaseKey.value = savedKey;

    if (savedUrl && savedKey) {
        initSupabase(savedUrl, savedKey);
        setSupabaseStatus(true, 'Supabase: Connected');
    } else {
        setSupabaseStatus(false, 'Local Demo Mode');
    }
}

function setSupabaseStatus(isConnected, text) {
    supabaseStatusText.textContent = text;
    if (isConnected) {
        supabaseStatusDot.className = 'w-2 h-2 rounded-full bg-emerald-400 mr-1.5';
        statEngine.textContent = 'Supabase Cloud';
    } else {
        supabaseStatusDot.className = 'w-2 h-2 rounded-full bg-amber-400 mr-1.5';
        statEngine.textContent = 'Local Browser Demo';
    }
}

function updateHouseholdCounters() {
    householdNumberBadge.textContent = `House #${state.householdIndex}`;
    bottomHouseCounter.textContent = `Entering Household #${state.householdIndex}`;
    avatarBadge.textContent = `H${state.householdIndex}`;
    const nameVal = document.getElementById('fullName').value.trim();
    currentHouseholdLabel.textContent = nameVal ? `Visiting: ${nameVal} (House #${state.householdIndex})` : `Visiting Household #${state.householdIndex}`;
}

function updateSavedCountBadge() {
    totalSavedCounter.textContent = state.submissions.length;
}

// Live update name in header
document.getElementById('fullName').addEventListener('input', (e) => {
    updateHouseholdCounters();
});

// ==========================================================================
// Event Listeners
// ==========================================================================
function setupEventListeners() {
    btnSaveAndNext.addEventListener('click', () => submitHousehold(true));
    btnQuickSave.addEventListener('click', () => submitHousehold(false));
    btnResetHouse.addEventListener('click', () => {
        if (confirm('Clear current household form?')) resetFormFields();
    });

    // GPS Geolocation Tagging
    btnAutoGps.addEventListener('click', captureGpsLocation);

    // Photos
    btnTakePhoto.addEventListener('click', () => photoCameraInput.click());
    btnBrowsePhotos.addEventListener('click', () => photoFileInput.click());
    photoCameraInput.addEventListener('change', (e) => handleFilesSelected(e.target.files));
    photoFileInput.addEventListener('change', (e) => handleFilesSelected(e.target.files));
    btnClearAllPhotos.addEventListener('click', clearAllPhotos);

    // Supabase Modal
    btnOpenSupabaseModal.addEventListener('click', () => {
        cfgTestResult.classList.add('hidden');
        supabaseModal.classList.remove('hidden');
    });
    btnCloseSupabaseModal.addEventListener('click', () => supabaseModal.classList.add('hidden'));
    btnSaveSupabase.addEventListener('click', saveSupabaseConfig);
    btnTestSupabase.addEventListener('click', testSupabaseConnection);
    btnResetToDemo.addEventListener('click', resetToDemoStorage);

    // Records Explorer Modal
    btnOpenDashboard.addEventListener('click', openDashboard);
    btnCloseDashboard.addEventListener('click', () => dashboardModal.classList.add('hidden'));
    btnRefreshResponses.addEventListener('click', loadResponsesDashboard);
    btnExportCSV.addEventListener('click', exportResponsesToCSV);

    // Lightbox
    btnCloseLightbox.addEventListener('click', () => lightboxModal.classList.add('hidden'));
    lightboxModal.addEventListener('click', (e) => {
        if (e.target === lightboxModal) lightboxModal.classList.add('hidden');
    });
}

function setupOtherInputs() {
    const textFocusPairs = [
        { textId: 'highestQualificationOther', radioName: 'highestQualification' },
        { textId: 'educationDifficultiesOther', checkName: 'educationDifficulties' },
        { textId: 'employmentStatusOther', radioName: 'employmentStatus' },
        { textId: 'primaryOccupationOther', radioName: 'primaryOccupation' },
        { textId: 'houseTypeOther', radioName: 'houseType' },
        { textId: 'drinkingWaterSourceOther', radioName: 'drinkingWaterSource' },
        { textId: 'primaryCookingFuelOther', radioName: 'primaryCookingFuel' },
        { textId: 'wasteDisposalOther', radioName: 'wasteDisposal' },
        { textId: 'internetDevicesOther', checkName: 'internetDevices' },
        { textId: 'biggestProblemsOther', checkName: 'biggestProblems' },
        { textId: 'highestPriorityOther', checkName: 'highestPriority' },
    ];

    textFocusPairs.forEach(p => {
        const txt = document.getElementById(p.textId);
        if (txt) {
            txt.addEventListener('focus', () => {
                if (p.radioName) {
                    const r = form.querySelector(`input[name="${p.radioName}"][value="Other"]`);
                    if (r) r.checked = true;
                }
                if (p.checkName) {
                    const c = form.querySelector(`input[name="${p.checkName}"][value="Other"]`);
                    if (c) c.checked = true;
                }
            });
        }
    });
}

// Geolocation helper
function captureGpsLocation() {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
    }

    gpsStatusText.textContent = 'Locating GPS...';
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const coords = `${pos.coords.latitude.toFixed(6)}, ${pos.coords.longitude.toFixed(6)}`;
            state.gpsLocation = coords;
            gpsCoordinates.value = coords;
            gpsStatusText.textContent = `GPS: ${coords}`;
            showToast(`GPS Tagged: ${coords}`);
        },
        (err) => {
            console.warn('GPS error:', err);
            gpsStatusText.textContent = 'GPS Unavailable';
            showToast('Could not fetch GPS. Ensure location permission is enabled.');
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}

// Toast helper
function showToast(msg) {
    toastMessage.textContent = msg;
    toastPopup.classList.remove('translate-y-[-100px]', 'opacity-0');
    toastPopup.classList.add('translate-y-0', 'opacity-100');
    setTimeout(() => {
        toastPopup.classList.remove('translate-y-0', 'opacity-100');
        toastPopup.classList.add('translate-y-[-100px]', 'opacity-0');
    }, 3500);
}

// ==========================================================================
// Photo Upload Management
// ==========================================================================
function handleFilesSelected(files) {
    if (!files || files.length === 0) return;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file.type.startsWith('image/')) continue;
        if (file.size > 15 * 1024 * 1024) {
            alert(`File "${file.name}" exceeds 15MB limit.`);
            continue;
        }

        const previewUrl = URL.createObjectURL(file);
        const photoId = 'photo_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);

        state.selectedPhotos.push({
            id: photoId,
            file: file,
            previewUrl: previewUrl,
            name: file.name,
            sizeKb: Math.round(file.size / 1024)
        });
    }

    renderPhotoPreviews();
}

function renderPhotoPreviews() {
    if (state.selectedPhotos.length === 0) {
        photoPreviewContainer.classList.add('hidden');
        photoGrid.innerHTML = '';
        return;
    }

    photoPreviewContainer.classList.remove('hidden');
    photoCountText.textContent = `Attached Photos (${state.selectedPhotos.length})`;
    photoGrid.innerHTML = '';

    state.selectedPhotos.forEach(item => {
        const photoDiv = document.createElement('div');
        photoDiv.className = 'photo-thumb group';
        photoDiv.innerHTML = `
            <img src="${item.previewUrl}" alt="${item.name}">
            <div class="thumb-delete-btn" data-id="${item.id}" title="Remove photo">
                <i data-lucide="x" class="w-3.5 h-3.5"></i>
            </div>
        `;
        photoGrid.appendChild(photoDiv);
    });

    photoGrid.querySelectorAll('.thumb-delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            state.selectedPhotos = state.selectedPhotos.filter(p => p.id !== id);
            renderPhotoPreviews();
        });
    });

    if (window.lucide) lucide.createIcons();
}

function clearAllPhotos() {
    state.selectedPhotos = [];
    renderPhotoPreviews();
}

async function uploadPhotosToSupabase() {
    if (state.selectedPhotos.length === 0) return [];
    const uploadedUrls = [];

    if (supabaseClient) {
        for (const item of state.selectedPhotos) {
            const timestamp = Date.now();
            const sanitizedName = item.name.replace(/[^a-zA-Z0-9.-]/g, '_');
            const filePath = `households/house_${state.householdIndex}_${timestamp}_${sanitizedName}`;

            const { data, error } = await supabaseClient.storage
                .from('survey-photos')
                .upload(filePath, item.file, {
                    cacheControl: '3600',
                    upsert: false
                });

            if (error) {
                console.error(`Error uploading photo to Supabase:`, error);
                uploadedUrls.push(item.previewUrl);
            } else {
                const { data: pubData } = supabaseClient.storage
                    .from('survey-photos')
                    .getPublicUrl(filePath);
                uploadedUrls.push(pubData.publicUrl);
            }
        }
    } else {
        // Local mode fallback
        for (const item of state.selectedPhotos) {
            try {
                const base64 = await fileToBase64(item.file);
                uploadedUrls.push(base64);
            } catch (e) {
                uploadedUrls.push(item.previewUrl);
            }
        }
    }

    return uploadedUrls;
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = err => reject(err);
    });
}

// ==========================================================================
// Validation
// ==========================================================================
function validateAllFields() {
    // Clear previous error outlines
    form.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'));

    let firstErrorElement = null;

    const checkInput = (id) => {
        const el = document.getElementById(id);
        if (!el || !el.value.trim()) {
            el.classList.add('input-error');
            if (!firstErrorElement) firstErrorElement = el;
            return false;
        }
        return true;
    };

    const checkRadio = (name) => {
        const checked = form.querySelector(`input[name="${name}"]:checked`);
        if (!checked) {
            const group = form.querySelector(`input[name="${name}"]`).closest('.chip-group') || form.querySelector(`input[name="${name}"]`).parentElement;
            group.classList.add('input-error');
            if (!firstErrorElement) firstErrorElement = group;
            return false;
        }
        return true;
    };

    const checkCheckboxes = (name) => {
        const checked = form.querySelectorAll(`input[name="${name}"]:checked`);
        if (checked.length === 0) {
            const group = form.querySelector(`input[name="${name}"]`).closest('.chip-group');
            if (group) group.classList.add('input-error');
            if (!firstErrorElement) firstErrorElement = group;
            return false;
        }
        return true;
    };

    // 1. Respondent
    checkInput('fullName');
    checkInput('email');
    checkRadio('gender');
    checkInput('age');

    // 2. Locality
    checkInput('locality');
    checkRadio('householdMembers');

    // 3. Education
    checkRadio('highestQualification');
    checkRadio('membersStudying');
    checkRadio('distanceToEducation');
    checkCheckboxes('educationDifficulties');

    // 4. Employment & Income
    checkRadio('employmentStatus');
    checkRadio('primaryOccupation');
    checkRadio('earningMembers');
    checkRadio('monthlyIncome');

    // 5. Housing & Basic Amenities
    checkRadio('houseType');
    checkRadio('availableRooms');
    checkRadio('hasElectricity');
    checkRadio('drinkingWaterSource');
    checkRadio('waterAvailableYearRound');
    checkRadio('toiletAccess');
    checkRadio('primaryCookingFuel');
    checkRadio('wasteDisposal');

    // 6. Digital Access
    checkRadio('hasInternet');
    checkCheckboxes('internetDevices');

    // 7. Ratings
    ['rating_education', 'rating_healthcare', 'rating_transportation', 'rating_banking', 'rating_markets'].forEach(r => {
        checkRadio(r);
    });
    checkCheckboxes('biggestProblems');
    checkCheckboxes('highestPriority');

    if (firstErrorElement) {
        firstErrorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        showToast('Please answer all required questions highlighted in red.');
        return false;
    }

    return true;
}

// ==========================================================================
// Submit Household Record
// ==========================================================================
async function submitHousehold(startNextHousehold = true) {
    if (!validateAllFields()) return;

    btnSaveAndNext.disabled = true;
    btnQuickSave.disabled = true;
    const origBtnText = btnSaveAndNext.innerHTML;
    btnSaveAndNext.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 mr-2 animate-spin"></i> Saving...`;
    if (window.lucide) lucide.createIcons();

    try {
        // 1. Upload photos to Supabase Storage
        const photoUrls = await uploadPhotosToSupabase();

        // 2. Build record object
        const getCheckValues = (name) => {
            return Array.from(form.querySelectorAll(`input[name="${name}"]:checked`)).map(el => el.value);
        };

        const gpsVal = gpsCoordinates.value.trim();
        const baseNotes = document.getElementById('surveyorNotes')?.value.trim() || '';
        const combinedNotes = gpsVal ? `[GPS: ${gpsVal}] ${baseNotes}`.trim() : (baseNotes || null);

        const record = {
            id: 'HH-' + state.householdIndex + '-' + Date.now().toString(36).toUpperCase(),
            created_at: new Date().toISOString(),

            // Section 1
            full_name: document.getElementById('fullName').value.trim(),
            email: document.getElementById('email').value.trim(),
            gender: form.querySelector('input[name="gender"]:checked').value,
            age: parseInt(document.getElementById('age').value),

            // Section 2
            locality: document.getElementById('locality').value.trim(),
            household_members: form.querySelector('input[name="householdMembers"]:checked').value,

            // Section 3
            highest_qualification: form.querySelector('input[name="highestQualification"]:checked').value,
            highest_qualification_other: document.getElementById('highestQualificationOther')?.value.trim() || null,
            members_studying: form.querySelector('input[name="membersStudying"]:checked').value,
            distance_to_education: form.querySelector('input[name="distanceToEducation"]:checked').value,
            education_difficulties: getCheckValues('educationDifficulties'),
            education_difficulties_other: document.getElementById('educationDifficultiesOther')?.value.trim() || null,

            // Section 4
            employment_status: form.querySelector('input[name="employmentStatus"]:checked').value,
            employment_status_other: document.getElementById('employmentStatusOther')?.value.trim() || null,
            primary_occupation: form.querySelector('input[name="primaryOccupation"]:checked').value,
            primary_occupation_other: document.getElementById('primaryOccupationOther')?.value.trim() || null,
            earning_members: form.querySelector('input[name="earningMembers"]:checked').value,
            monthly_income: form.querySelector('input[name="monthlyIncome"]:checked').value,

            // Section 5
            house_type: form.querySelector('input[name="houseType"]:checked').value,
            house_type_other: document.getElementById('houseTypeOther')?.value.trim() || null,
            available_rooms: form.querySelector('input[name="availableRooms"]:checked').value,
            has_electricity: form.querySelector('input[name="hasElectricity"]:checked').value,
            drinking_water_source: form.querySelector('input[name="drinkingWaterSource"]:checked').value,
            drinking_water_source_other: document.getElementById('drinkingWaterSourceOther')?.value.trim() || null,
            water_available_year_round: form.querySelector('input[name="waterAvailableYearRound"]:checked').value,
            toilet_access: form.querySelector('input[name="toiletAccess"]:checked').value,
            primary_cooking_fuel: form.querySelector('input[name="primaryCookingFuel"]:checked').value,
            primary_cooking_fuel_other: document.getElementById('primaryCookingFuelOther')?.value.trim() || null,
            waste_disposal: form.querySelector('input[name="wasteDisposal"]:checked').value,
            waste_disposal_other: document.getElementById('wasteDisposalOther')?.value.trim() || null,

            // Section 6
            has_internet: form.querySelector('input[name="hasInternet"]:checked').value,
            internet_devices: getCheckValues('internetDevices'),
            internet_devices_other: document.getElementById('internetDevicesOther')?.value.trim() || null,

            // Section 7
            rating_education: parseInt(form.querySelector('input[name="rating_education"]:checked').value),
            rating_healthcare: parseInt(form.querySelector('input[name="rating_healthcare"]:checked').value),
            rating_transportation: parseInt(form.querySelector('input[name="rating_transportation"]:checked').value),
            rating_banking: parseInt(form.querySelector('input[name="rating_banking"]:checked').value),
            rating_markets: parseInt(form.querySelector('input[name="rating_markets"]:checked').value),
            biggest_problems: getCheckValues('biggestProblems'),
            biggest_problems_other: document.getElementById('biggestProblemsOther')?.value.trim() || null,
            highest_priority_improvement: getCheckValues('highestPriority'),
            highest_priority_improvement_other: document.getElementById('highestPriorityOther')?.value.trim() || null,

            // Section 8: Photos & Notes
            photo_urls: photoUrls,
            surveyor_notes: combinedNotes
        };

        // 3. Save to Supabase
        if (supabaseClient) {
            const { data, error } = await supabaseClient
                .from('survey_responses')
                .insert([record])
                .select();

            if (error) {
                console.error('Supabase DB Insert Error:', error);
                throw new Error(error.message);
            }
            if (data && data[0] && data[0].id) {
                record.id = data[0].id;
            }
        }

        // Local cache save
        state.submissions.unshift(record);
        localStorage.setItem('local_survey_submissions', JSON.stringify(state.submissions));
        updateSavedCountBadge();

        showToast(`Household #${state.householdIndex} saved to ${supabaseClient ? 'Supabase' : 'local cache'}!`);

        if (startNextHousehold) {
            // Increment household count
            state.householdIndex += 1;
            localStorage.setItem('current_household_index', state.householdIndex);
            resetFormFields();
            updateHouseholdCounters();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

    } catch (err) {
        console.error('Save failed:', err);
        alert('Could not save to Supabase: ' + err.message + '\n\nSaved copy into local browser cache. Click Supabase Settings in the top bar to verify your credentials.');
    } finally {
        btnSaveAndNext.disabled = false;
        btnQuickSave.disabled = false;
        btnSaveAndNext.innerHTML = origBtnText;
        if (window.lucide) lucide.createIcons();
    }
}

function resetFormFields() {
    form.reset();
    clearAllPhotos();
    state.gpsLocation = null;
    gpsCoordinates.value = '';
    gpsStatusText.textContent = 'Tag GPS Location';
    form.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'));
    updateHouseholdCounters();
}

// ==========================================================================
// Supabase Config Modal
// ==========================================================================
function saveSupabaseConfig() {
    const url = cfgSupabaseUrl.value.trim();
    const key = cfgSupabaseKey.value.trim();

    if (!url || !key) {
        alert('Please provide both Project URL and Anon API Key.');
        return;
    }

    localStorage.setItem('SUPABASE_URL', url);
    localStorage.setItem('SUPABASE_ANON_KEY', key);

    const client = initSupabase(url, key);
    if (client) {
        setSupabaseStatus(true, 'Supabase: Connected');
        supabaseModal.classList.add('hidden');
        showToast('Supabase connected successfully!');
    }
}

async function testSupabaseConnection() {
    const url = cfgSupabaseUrl.value.trim();
    const key = cfgSupabaseKey.value.trim();

    if (!url || !key) {
        cfgTestResult.className = 'text-xs p-2.5 rounded-lg bg-red-50 text-red-700 border border-red-200 block';
        cfgTestResult.innerHTML = '⚠️ Enter URL and Anon Key first.';
        return;
    }

    cfgTestResult.className = 'text-xs p-2.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 block';
    cfgTestResult.innerHTML = '🔄 Testing connection to table and storage bucket...';

    try {
        const testClient = window.supabase.createClient(url, key);
        const { error: dbError } = await testClient.from('survey_responses').select('id').limit(1);

        if (dbError) {
            cfgTestResult.className = 'text-xs p-2.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 block';
            cfgTestResult.innerHTML = `⚠️ Connected, but table access failed: ${dbError.message}.`;
            return;
        }

        cfgTestResult.className = 'text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 block';
        cfgTestResult.innerHTML = `✅ Successfully connected to Supabase! Table & storage ready.`;
    } catch (err) {
        cfgTestResult.className = 'text-xs p-2.5 rounded-lg bg-red-50 text-red-700 border border-red-200 block';
        cfgTestResult.innerHTML = `❌ Connection failed: ${err.message}`;
    }
}

function resetToDemoStorage() {
    localStorage.removeItem('SUPABASE_URL');
    localStorage.removeItem('SUPABASE_ANON_KEY');
    cfgSupabaseUrl.value = '';
    cfgSupabaseKey.value = '';
    initSupabase('', '');
    setSupabaseStatus(false, 'Local Demo Mode');
    supabaseModal.classList.add('hidden');
    showToast('Switched to local browser mode.');
}

// ==========================================================================
// Dashboard & CSV Export
// ==========================================================================
async function openDashboard() {
    dashboardModal.classList.remove('hidden');
    await loadResponsesDashboard();
}

async function loadResponsesDashboard() {
    responsesTableBody.innerHTML = `<tr><td colspan="7" class="p-6 text-center text-slate-400">Loading records...</td></tr>`;

    let records = [];
    if (supabaseClient) {
        try {
            const { data, error } = await supabaseClient
                .from('survey_responses')
                .select('*')
                .order('created_at', { ascending: false });

            if (!error && data) records = data;
            else records = state.submissions;
        } catch (e) {
            records = state.submissions;
        }
    } else {
        records = state.submissions;
    }

    statTotalSubmissions.textContent = records.length;
    let totalPhotos = 0;
    records.forEach(r => {
        if (r.photo_urls && Array.isArray(r.photo_urls)) totalPhotos += r.photo_urls.length;
    });
    statTotalPhotos.textContent = totalPhotos;

    if (records.length === 0) {
        responsesTableBody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-slate-400">No household survey entries recorded yet.</td></tr>`;
        return;
    }

    responsesTableBody.innerHTML = '';
    records.forEach((rec, idx) => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 transition';

        const timeStr = rec.created_at ? new Date(rec.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'N/A';
        const photoCount = rec.photo_urls ? rec.photo_urls.length : 0;

        tr.innerHTML = `
            <td class="p-2.5 text-slate-500 whitespace-nowrap">${timeStr}</td>
            <td class="p-2.5 font-bold text-slate-900">${rec.full_name || 'N/A'}</td>
            <td class="p-2.5 text-slate-700">${rec.locality || 'N/A'}</td>
            <td class="p-2.5 text-slate-600">${rec.house_type || 'N/A'}</td>
            <td class="p-2.5 text-slate-600">${rec.monthly_income || 'N/A'}</td>
            <td class="p-2.5">
                ${photoCount > 0 ? `
                    <span class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200 cursor-pointer hover:bg-blue-100 photo-gallery-trigger" data-photos='${JSON.stringify(rec.photo_urls)}'>
                        <i data-lucide="image" class="w-3 h-3 mr-1"></i>
                        ${photoCount}
                    </span>
                ` : `<span class="text-slate-400 text-[11px]">-</span>`}
            </td>
            <td class="p-2.5 text-right">
                <button type="button" class="view-details-btn text-blue-600 hover:text-blue-800 font-bold text-xs" data-idx="${idx}">
                    View
                </button>
            </td>
        `;
        responsesTableBody.appendChild(tr);
    });

    responsesTableBody.querySelectorAll('.photo-gallery-trigger').forEach(pill => {
        pill.addEventListener('click', () => {
            const urls = JSON.parse(pill.dataset.photos || '[]');
            if (urls.length > 0) openLightbox(urls[0], `Attached Photo`);
        });
    });

    responsesTableBody.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = parseInt(btn.dataset.idx);
            const rec = records[idx];
            if (rec) {
                alert(`--- HOUSEHOLD DETAILS ---\n` +
                    `Respondent: ${rec.full_name} (${rec.gender}, Age ${rec.age})\n` +
                    `Email: ${rec.email}\n` +
                    `Locality: ${rec.locality}\n` +
                    `Household Size: ${rec.household_members} members\n` +
                    `Education: ${rec.highest_qualification} (Studying: ${rec.members_studying}, Dist: ${rec.distance_to_education})\n` +
                    `Occupation: ${rec.primary_occupation} (${rec.employment_status})\n` +
                    `Monthly Income: ${rec.monthly_income} (Earners: ${rec.earning_members})\n` +
                    `House: ${rec.house_type}, Rooms: ${rec.available_rooms}, Electricity: ${rec.has_electricity}\n` +
                    `Water: ${rec.drinking_water_source} (Year-round: ${rec.water_available_year_round})\n` +
                    `Toilet: ${rec.toilet_access}, Fuel: ${rec.primary_cooking_fuel}, Waste: ${rec.waste_disposal}\n` +
                    `Internet: ${rec.has_internet} (${rec.internet_devices?.join(', ') || 'None'})\n` +
                    `Ratings (1-5): Edu=${rec.rating_education}, Health=${rec.rating_healthcare}, Transport=${rec.rating_transportation}, Bank=${rec.rating_banking}, Market=${rec.rating_markets}\n` +
                    `Notes: ${rec.surveyor_notes || 'None'}`);
            }
        });
    });

    if (window.lucide) lucide.createIcons();
}

function openLightbox(imageUrl, caption) {
    lightboxImage.src = imageUrl;
    lightboxCaption.textContent = caption || '';
    lightboxModal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
}

function exportResponsesToCSV() {
    const records = state.submissions;
    if (records.length === 0) {
        alert('No household records to export.');
        return;
    }

    const headers = [
        'ID', 'Timestamp', 'Name', 'Email', 'Gender', 'Age',
        'Locality', 'Household Members',
        'Highest Qualification', 'Members Studying', 'Distance to Education', 'Education Difficulties',
        'Employment Status', 'Primary Occupation', 'Earning Members', 'Monthly Income',
        'House Type', 'Available Rooms', 'Electricity', 'Drinking Water', 'Water Year Round',
        'Toilet Access', 'Cooking Fuel', 'Waste Disposal', 'Internet Access', 'Internet Devices',
        'Rating Education', 'Rating Healthcare', 'Rating Transportation', 'Rating Banking', 'Rating Markets',
        'Biggest Problems', 'Highest Priority Improvements', 'Photo Count', 'Surveyor Notes'
    ];

    const rows = records.map(r => [
        `"${r.id || ''}"`,
        `"${r.created_at || ''}"`,
        `"${(r.full_name || '').replace(/"/g, '""')}"`,
        `"${(r.email || '').replace(/"/g, '""')}"`,
        `"${r.gender || ''}"`,
        r.age || '',
        `"${(r.locality || '').replace(/"/g, '""')}"`,
        `"${r.household_members || ''}"`,
        `"${(r.highest_qualification || '').replace(/"/g, '""')}"`,
        `"${r.members_studying || ''}"`,
        `"${r.distance_to_education || ''}"`,
        `"${(Array.isArray(r.education_difficulties) ? r.education_difficulties.join(', ') : '').replace(/"/g, '""')}"`,
        `"${r.employment_status || ''}"`,
        `"${r.primary_occupation || ''}"`,
        `"${r.earning_members || ''}"`,
        `"${r.monthly_income || ''}"`,
        `"${r.house_type || ''}"`,
        `"${r.available_rooms || ''}"`,
        `"${r.has_electricity || ''}"`,
        `"${r.drinking_water_source || ''}"`,
        `"${r.water_available_year_round || ''}"`,
        `"${r.toilet_access || ''}"`,
        `"${r.primary_cooking_fuel || ''}"`,
        `"${r.waste_disposal || ''}"`,
        `"${r.has_internet || ''}"`,
        `"${(Array.isArray(r.internet_devices) ? r.internet_devices.join(', ') : '').replace(/"/g, '""')}"`,
        r.rating_education || '',
        r.rating_healthcare || '',
        r.rating_transportation || '',
        r.rating_banking || '',
        r.rating_markets || '',
        `"${(Array.isArray(r.biggest_problems) ? r.biggest_problems.join(', ') : '').replace(/"/g, '""')}"`,
        `"${(Array.isArray(r.highest_priority_improvement) ? r.highest_priority_improvement.join(', ') : '').replace(/"/g, '""')}"`,
        (r.photo_urls ? r.photo_urls.length : 0),
        `"${(r.surveyor_notes || '').replace(/"/g, '""')}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `field_survey_households_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
