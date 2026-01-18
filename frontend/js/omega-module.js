// Orion Omega - Triage Module Logic

document.addEventListener('DOMContentLoaded', () => {
    initTriageModule();
});

function initTriageModule() {
    console.log('🔷 Orion Omega Module Initialized');

    // UI Elements
    const elements = {
        symptomInput: document.getElementById('symptom-search'),
        searchBtn: document.getElementById('btn-search'),
        micBtn: document.getElementById('btn-mic'),
        resultContainer: document.getElementById('result-container'),
        questionsContainer: document.getElementById('questions-container'),
        arToggleBtn: document.getElementById('btn-ar-toggle'),
        arVideo: document.getElementById('ar-feed'),
        reticle: document.getElementById('hud-reticle')
    };

    // State
    let state = {
        symptom: null,
        answers: {},
        questions: [],
        arMode: false,
        authenticated: false
    };

    // --- Interaction Handlers ---

    if (elements.arToggleBtn) {
        elements.arToggleBtn.addEventListener('click', toggleARMode);
    }

    // Expose auth function globally
    window.authenticateBio = async function () {
        const staffId = document.getElementById('staff-id-input').value;
        const statusText = document.getElementById('bio-status-text');

        if (!staffId) return;

        statusText.innerText = "VERIFYING BIOMETRICS...";
        statusText.className = "text-yellow-400 font-mono text-sm mb-8 animate-pulse";

        try {
            const response = await fetch('/api/auth/biocore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ staff_id: staffId, bio_hash: "mock-hash" })
            });
            const data = await response.json();

            if (data.authenticated) {
                statusText.innerText = "IDENTITY CONFIRMED. ACCESS GRANTED.";
                statusText.className = "text-green-500 font-mono text-sm mb-8";

                await new Promise(r => setTimeout(r, 1000));

                state.authenticated = true;
                toggleBioModal(false);
                toggleARMode(); // Resume AR activation
            } else {
                statusText.innerText = "ACCESS DENIED. INVALID CREDENTIALS.";
                statusText.className = "text-red-500 font-mono text-sm mb-8";
            }
        } catch (e) {
            console.error(e);
            statusText.innerText = "SYSTEM ERROR. RETRY.";
            statusText.className = "text-red-500 font-mono text-sm mb-8";
        }
    };

    function toggleBioModal(show) {
        const modal = document.getElementById('bio-auth-modal');
        const inputDiv = document.getElementById('bio-auth-input');

        if (show) {
            modal.classList.remove('opacity-0', 'pointer-events-none');
            // Animate workflow
            setTimeout(() => {
                inputDiv.classList.remove('opacity-0', 'translate-y-4');
                document.getElementById('staff-id-input').focus();
            }, 1000);
        } else {
            modal.classList.add('opacity-0', 'pointer-events-none');
            inputDiv.classList.add('opacity-0', 'translate-y-4');
        }
    }

    async function toggleARMode() {
        // Security Gate
        if (!state.arMode && !state.authenticated) {
            console.log("🔒 Access Request - BioCore Auth Required");
            toggleBioModal(true);
            return;
        }

        state.arMode = !state.arMode;
        const body = document.body;

        if (state.arMode) {
            console.log('🕶️ Activando HUD / AR Mode...');
            // ... (rest of activation logic)
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'environment' }
                });

                if (elements.arVideo) {
                    elements.arVideo.srcObject = stream;
                    elements.arVideo.classList.remove('opacity-0');
                }

                // Add HUD classes
                body.classList.add('hud-active');
                if (elements.reticle) elements.reticle.style.opacity = '1';
                document.getElementById('ambient-bg').style.opacity = '0'; // Hide ambient bg

                // Visual feedback on button
                elements.arToggleBtn.classList.add('bg-primary', 'text-black');
                elements.arToggleBtn.classList.remove('bg-white/5');

            } catch (err) {
                console.error("Error accessing camera:", err);
                alert("Camera access required for AR Mode.");
                state.arMode = false;
            }
        } else {
            console.log('🕶️ Desactivando HUD Mode...');

            // Stop video
            if (elements.arVideo && elements.arVideo.srcObject) {
                const tracks = elements.arVideo.srcObject.getTracks();
                tracks.forEach(track => track.stop());
                elements.arVideo.srcObject = null;
                elements.arVideo.classList.add('opacity-0');
            }

            // Remove HUD classes
            body.classList.remove('hud-active');
            if (elements.reticle) elements.reticle.style.opacity = '0';
            document.getElementById('ambient-bg').style.opacity = '1';

            // Reset button
            elements.arToggleBtn.classList.remove('bg-primary', 'text-black');
            elements.arToggleBtn.classList.add('bg-white/5');
        }
    }

    if (elements.searchBtn) {
        elements.searchBtn.addEventListener('click', handleSearch);
    }

    if (elements.symptomInput) {
        elements.symptomInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSearch();
        });
    }

    async function handleSearch() {
        const query = elements.symptomInput.value.trim();
        if (!query) return;

        console.log(`Searching for: ${query}`);

        // Show loading state
        if (elements.questionsContainer) {
            elements.questionsContainer.innerHTML = `<div class="text-center p-8 text-primary animate-pulse">Analyzing symptom...</div>`;
        }

        try {
            state.symptom = query;
            state.answers = {}; // Reset answers

            // Clear previous results
            if (elements.resultContainer) elements.resultContainer.innerHTML = '';

            // Fetch questions
            const response = await window.orionApi.getQuestions(state.symptom);
            state.questions = response.preguntas;

            if (!state.questions || state.questions.length === 0) {
                if (elements.questionsContainer) {
                    elements.questionsContainer.innerHTML = `<div class="text-center p-8 text-gray-400">No specific protocol found for this symptom. Try 'dolor toracico', 'cefalea', etc.</div>`;
                }
                return;
            }

            renderQuestions(state.questions);

        } catch (error) {
            console.error(error);
            if (elements.questionsContainer) {
                elements.questionsContainer.innerHTML = `<div class="text-center p-8 text-emergency-red">Error: ${error.message}</div>`;
            }
        }
    }

    window.submitTriage = async function () {
        if (!state.symptom) return;

        const btn = document.getElementById('btn-submit-triage');
        if (btn) btn.innerHTML = '<span class="animate-spin material-symbols-outlined">sync</span> Processing...';

        try {
            const payload = {
                sintoma: state.symptom,
                respuestas: state.answers
            };

            const result = await window.orionApi.classifyTriage(payload);
            renderResult(result);

            // Clear questions logic to focus on result
            if (elements.questionsContainer) elements.questionsContainer.innerHTML = '';

        } catch (error) {
            alert(`Classification Error: ${error.message}`);
            if (btn) btn.innerHTML = 'Analyze & Classify';
        }
    };

    // --- Rendering Logic ---

    function renderQuestions(questions) {
        if (!elements.questionsContainer) return;

        const html = `
            <div class="space-y-4 animate-fade-in-up">
                <div class="flex items-center justify-between px-1">
                    <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest font-display">Clinical Assessment</h3>
                    <span class="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded border border-primary/20 font-mono">protocol: ${state.symptom.toUpperCase()}</span>
                </div>
                
                ${questions.map((q, idx) => `
                <div class="bg-surface-glass rounded-xl p-4 border border-white/10 shadow-lg backdrop-blur-sm">
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex-1">
                            <span class="text-xs text-primary font-mono mb-1 block">Q-${idx + 1}</span>
                            <p class="text-lg font-medium text-white">${q.pregunta}</p>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <button onclick="handleAnswer('${q.id}', 'si')" 
                            class="answer-btn h-12 rounded-lg bg-white/5 border border-white/10 hover:border-primary hover:bg-primary/10 transition-all font-bold text-gray-300 active:scale-[0.98]" 
                            data-question="${q.id}" data-value="si">
                            YES
                        </button>
                        <button onclick="handleAnswer('${q.id}', 'no')" 
                            class="answer-btn h-12 rounded-lg bg-white/5 border border-white/10 hover:border-gray-500 hover:bg-white/10 transition-all font-bold text-gray-400 active:scale-[0.98]" 
                            data-question="${q.id}" data-value="no">
                            NO
                        </button>
                    </div>
                </div>
                `).join('')}

                <button id="btn-submit-triage" onclick="submitTriage()" class="w-full bg-primary hover:bg-cyan-300 text-black font-bold py-4 rounded-xl shadow-glow transition-all active:scale-95 uppercase tracking-wider mt-6 flex items-center justify-center gap-2">
                    <span class="material-symbols-outlined">medical_services</span>
                    Analyze & Classify
                </button>
            </div>
        `;

        elements.questionsContainer.innerHTML = html;
    }

    function renderResult(result) {
        if (!elements.resultContainer) return;

        const colorMap = {
            'D1': 'emergency-red',
            'D2': 'emergency-orange',
            'D3': 'emergency-yellow',
            'D4': 'emergency-green',
            'D5': 'emergency-blue'
        };

        const themeColor = colorMap[result.codigo_triage] || 'emergency-blue';

        const html = `
            <div class="animate-fade-in-up mb-6">
                <div class="relative glass-alert rounded-xl overflow-hidden shadow-glow-${themeColor.split('-')[1] || 'blue'} group">
                    <div class="absolute left-0 top-0 bottom-0 w-1.5 bg-${themeColor}"></div>
                    <div class="p-5 pl-7 relative z-10">
                        <div class="flex items-start justify-between mb-3">
                            <div class="flex items-center space-x-2">
                                <span class="material-symbols-outlined text-${themeColor} text-2xl animate-pulse">warning</span>
                                <span class="text-xs font-bold text-${themeColor} uppercase tracking-wider border border-${themeColor}/30 px-2 py-0.5 rounded bg-${themeColor}/10">Triage Result</span>
                            </div>
                            <div class="text-right">
                                <div class="text-[10px] text-gray-400 font-mono uppercase">Conduct Code</div>
                                <div class="text-lg font-display font-bold text-white leading-none">${result.codigo_triage}</div>
                            </div>
                        </div>
                        <h2 class="text-lg font-bold text-white mb-2 font-display uppercase tracking-wide">
                            ${result.categoria}
                        </h2>
                        <div class="bg-black/30 rounded-lg p-3 border border-white/5 mb-4">
                            <p class="text-sm text-gray-200 leading-relaxed font-medium">
                                ${result.instruccion_atencion}
                            </p>
                        </div>
                        
                         <div class="mt-2 mb-4">
                             <p class="text-[10px] uppercase text-gray-500 font-bold mb-1">POSSIBLE CAUSES (AI ASSISTED)</p>
                             <div class="flex flex-wrap gap-2">
                                ${result.posibles_causas.map(c => `<span class="text-xs bg-white/5 border border-white/10 px-2 py-1 rounded text-gray-300">${c}</span>`).join('')}
                             </div>
                        </div>

                        <div class="flex space-x-3">
                            <button onclick="location.reload()" class="flex-1 bg-${themeColor} hover:brightness-110 text-white text-sm font-bold py-3 px-4 rounded-lg shadow-lg transition-all active:scale-95 flex items-center justify-center">
                                <span class="material-symbols-outlined text-lg mr-2">restart_alt</span>
                                NEW TRIAGE
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        elements.resultContainer.innerHTML = html;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Global answer handler
    window.handleAnswer = function (questionId, value) {
        state.answers[questionId] = value;

        // Update UI
        const btns = document.querySelectorAll(`button[data-question="${questionId}"]`);
        btns.forEach(btn => {
            if (btn.dataset.value === value) {
                // Selected style
                btn.className = "answer-btn h-12 rounded-lg border transition-all font-bold active:scale-[0.98] " +
                    "bg-primary/20 border-primary text-primary shadow-glow";
            } else {
                // Unselected style
                btn.className = "answer-btn h-12 rounded-lg bg-white/5 border border-white/10 hover:border-gray-500 hover:bg-white/10 transition-all font-bold text-gray-400 active:scale-[0.98]";
            }
        });
    };
}
