// DOM elementy
const waitTimeEl = document.getElementById('waitTime');
const peopleCountEl = document.getElementById('peopleCount');
const themeToggleBtn = document.getElementById('themeToggle');
const videoStream = document.getElementById('videoStream');

// Stav
let connectionLost = false;
let smoothWaitTime = 0;
let isMobile = window.innerWidth < 768;

// Detekce změn velikosti okna
window.addEventListener('resize', () => {
    isMobile = window.innerWidth < 768;
});

// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        updateThemeIcon();
    }
}

function toggleTheme() {
    const isLight = document.body.classList.toggle('light-theme');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    updateThemeIcon();
}

function updateThemeIcon() {
    const icon = themeToggleBtn.querySelector('.theme-icon');
    const isLight = document.body.classList.contains('light-theme');
    icon.textContent = isLight ? '☀️' : '🌙';
}

themeToggleBtn.addEventListener('click', toggleTheme);

// Formátování času
function formatWaitTime(seconds) {
    if (seconds === 0) {
        return 'Čekání: 0s';
    }
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    
    if (minutes === 0) {
        return `${secs}s`;
    }
    
    if (minutes < 60) {
        return `${minutes}m ${secs}s`;
    }
    
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
}

// Plynulá animace čekacího času
function smoothUpdateWaitTime(targetTime) {
    const diff = targetTime - smoothWaitTime;
    
    // Pokud se liší o více než 15 sekund, skočíme na nový čas
    if (Math.abs(diff) > 15) {
        smoothWaitTime = targetTime;
    } else {
        // Jinak přidáme 1/6 rozdílu (pomalejší přechod = plynulejší pokles)
        smoothWaitTime += diff * 0.16667;
    }
    
    const displayTime = Math.round(smoothWaitTime);
    return formatWaitTime(displayTime);
}

// Aktualizace statistiky
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        
        if (!response.ok) {
            throw new Error('Chyba serveru');
        }
        
        const data = await response.json();

        // Plynulá aktualizace času
        const waitTimeText = smoothUpdateWaitTime(data.wait_time);
        
        // Aktualizace elementů
        if (waitTimeEl) {
            waitTimeEl.textContent = waitTimeText;
        }
        
        if (peopleCountEl) {
            peopleCountEl.textContent = data.people_count;
        }
        
        // Aktualizace stavu
        updateConnectionStatus(true);
        return true;
    } catch (error) {
        console.error('Chyba:', error);
        updateConnectionStatus(false);
        return false;
    }
}

// Aktualizace stavu spojení
function updateConnectionStatus(connected) {
    if (connectionLost === !connected) {
        connectionLost = !connected;
        if (connected) {
            console.log('Připojeno');
        } else {
            console.log('Bez spojení');
        }
    }
}

// Inicializace
window.addEventListener('load', () => {
    initTheme();
    updateStats();
    
    // Optimizace pro mobilní zařízení
    if (isMobile) {
        videoStream.style.willChange = 'transform';
        document.body.style.overscrollBehavior = 'none';
    }
});

// Periodická aktualizace statistiky
let updateInterval = setInterval(updateStats, 1000);

// Viditelnost stránky - úspora energie
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Stránka je skrytá');
        clearInterval(updateInterval);
    } else {
        updateStats();
        updateInterval = setInterval(updateStats, 1000);
    }
});
