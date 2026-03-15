const API_BASE_URL = '/api';

// DOM элементы
const waitTimeEl = document.getElementById('waitTime');
const peopleCountEl = document.getElementById('peopleCount');
const themeToggleBtn = document.getElementById('themeToggle');
const htmlEl = document.documentElement;
const body = document.body;

// Инициализация темы
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        body.classList.add('light-theme');
        updateThemeIcon('☀️');
    } else {
        body.classList.remove('light-theme');
        updateThemeIcon('🌙');
    }
}

// Обновление иконки темы
function updateThemeIcon(icon) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = icon;
    }
}

// Переключение темы
themeToggleBtn.addEventListener('click', () => {
    const isLight = body.classList.toggle('light-theme');
    const theme = isLight ? 'light' : 'dark';
    localStorage.setItem('theme', theme);
    updateThemeIcon(isLight ? '☀️' : '🌙');
});

// Плавное обновление времени ожидания
let currentWaitTime = 0;
const INTERPOLATION_FACTOR = 0.16667; // 1/6 для плавного анимирования

function formatWaitTime(seconds) {
    if (seconds === 0) {
        return 'Volno ✓';
    }
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}m ${secs}s`;
}

// Получение статистики
async function updateStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (!response.ok) {
            console.error('Stats API error:', response.status);
            return;
        }
        const data = await response.json();

        // Обновление счета людей
        if (peopleCountEl) {
            peopleCountEl.textContent = data.people_count;
        }

        // Плавное интерполирование времени ожидания
        const targetWaitTime = data.wait_time || 0;
        currentWaitTime += (targetWaitTime - currentWaitTime) * INTERPOLATION_FACTOR;

        if (waitTimeEl) {
            waitTimeEl.textContent = formatWaitTime(currentWaitTime);
        }

    } catch (error) {
        console.error('Error updating stats:', error);
        if (waitTimeEl) {
            waitTimeEl.textContent = '-';
        }
        if (peopleCountEl) {
            peopleCountEl.textContent = '-';
        }
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    updateStats(); // Первое обновление
    setInterval(updateStats, 1000); // Обновление каждую секунду

    // Останавливаем обновление если вкладка не видна (оптимизация батареи)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            console.log('Tab hidden - pausing updates');
        } else {
            console.log('Tab visible - resuming updates');
        }
    });
});
