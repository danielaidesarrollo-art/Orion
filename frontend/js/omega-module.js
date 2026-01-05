/**
 * Orion Omega - Triage Module Logic
 */

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
        mainContainer: document.querySelector('main'),

        // Sections to likely replace/update
        triageResultSection: document.getElementById('triage-result'), // We'll add this ID to HTML
        questionsSection: document.getElementById('questions-section'), // We'll add this ID to HTML
        vitalsSection: document.getElementById('vitals-section'), // We'll add this ID to HTML
    };

    // State
    let state = {
        symptom: null,
        answers: {},
        questions: []
    };

    // --- Event Listeners ---

    if (elements.searchBtn) {
        elements.searchBtn.addEventListener('click', handleSearch);
    }

    if (elements.symptomInput) {
        elements.symptomInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSearch();
        });
    }

    // --- Handlers ---

    async function handleSearch() {
        const query = elements.symptomInput.value.trim();
        if (!query) return;

        console.log(`Searching for: ${query}`);

        try {
            // In a real flow we might first search/validate symptom
            // For now, let's treat the input as the selected symptom
            state.symptom = query;

            // Fetch questions
            const response = await window.orionApi.getQuestions(state.symptom);
            state.questions = response.preguntas;

            renderQuestions(state.questions);

        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    async function submitTriage() {
        if (!state.symptom) return;

        try {
            const payload = {
                sintoma: state.symptom,
                respuestas: state.answers
            };

            const result = await window.orionApi.classifyTriage(payload);
            renderResult(result);

        } catch (error) {
            alert(`Classification Error: ${error.message}`);
        }
    }

    // --- Rendering ---

    function renderQuestions(questions) {
        // Replace the "Rapid Assessment" section content
        // This effectively clears the placeholder data

        const containerHtml = `
            <div class="space-y-4 animate-fade-in-up" id="dynamic-questions">
                <div class="flex items-center justify-between px-1">
                    <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest font-display">Clinical Assessment</h3>
                    <span class="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded border border-primary/20 font-mono">LIVE QUESTIONNAIRE</span>
                </div>
                
                ${questions.map((q, idx) => `
                <div class="bg-surface-glass rounded-xl p-4 border border-white/10 shadow-lg backdrop-blur-sm">
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex-1">
                            <span class="text-xs text-primary font-mono mb-1 block">Q-${idx + 1}</span>
                            <p class="text-lg font-medium text-white">${q.texto}</p>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <button onclick="handleAnswer('${q.id}', 'si')" 
                            class="answer-btn h-12 rounded-lg bg-white/5 border border-white/10 hover:border-primary hover:bg-primary/10 transition-all font-bold text-gray-300 active:scale-[0.98]" data-question="${q.id}" data-value="si">
                            YES
                        </button>
                        <button onclick="handleAnswer('${q.id}', 'no')" 
                            class="answer-btn h-12 rounded-lg bg-white/5 border border-white/10 hover:border-gray-500 hover:bg-white/10 transition-all font-bold text-gray-400 active:scale-[0.98]" data-question="${q.id}" data-value="no">
                            NO
                        </button>
                    </div>
                </div>
                `).join('')}

                <button id="btn-submit-triage" class="w-full bg-primary hover:bg-cyan-300 text-black font-bold py-4 rounded-xl shadow-glow transition-all active:scale-95 uppercase tracking-wider mt-6">
                    Analyze & Classify
                </button>
            </div>
        `;

        // Find the rapid assessment container to replace
        // In the template it's the div with "Rapid Assessment" header
        // For simplicity, we'll inject into main container clearing specific children
        // But a cleaner way is to target a specific container ID added to HTML

        const targetContainer = document.getElementById('questions-container');
        if (targetContainer) {
            targetContainer.innerHTML = containerHtml;

            // Re-attach listener to new button
            document.getElementById('btn-submit-triage').addEventListener('click', submitTriage);
        }
    }

    function renderResult(result) {
        const colorMap = {
            'D1': 'emergency-red',
            'D2': 'emergency-orange',
            'D3': 'emergency-yellow',
            'D4': 'emergency-green',
            'D5': 'emergency-blue',
            // Fallback for codes
            'EMERGENCIA': 'emergency-red',
            'URGENCIA': 'emergency-orange'
        };

        const themeColor = colorMap[result.codigo_triage] || 'emergency-blue';
        const displayCode = `${result.codigo_triage} - ${result.categoria}`;

        const resultHtml = `
            <div class="animate-fade-in-up">
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
                             <p class="text-[10px] uppercase text-gray-500 font-bold mb-1">Possible Causes (AI Analysis)</p>
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

        const resultContainer = document.getElementById('result-container');
        if (resultContainer) {
            resultContainer.innerHTML = resultHtml;
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    // Expose for inline onclicks
    window.handleAnswer = function (questionId, value) {
        state.answers[questionId] = value;

        // Visual feedback
        const btns = document.querySelectorAll(`button[data-question="${questionId}"]`);
        btns.forEach(btn => {
            if (btn.dataset.value === value) {
                btn.classList.add('bg-primary/20', 'border-primary', 'text-primary');
                btn.classList.remove('bg-white/5', 'text-gray-300', 'text-gray-400');
            } else {
                btn.classList.remove('bg-primary/20', 'border-primary', 'text-primary');
                btn.classList.add('bg-white/5');
            }
        });
    };
}
