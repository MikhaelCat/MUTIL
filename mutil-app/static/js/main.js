document.addEventListener('DOMContentLoaded', () => {
    const getTaskBtn = document.getElementById('get-task-btn');
    const taskTextElem = document.getElementById('task-text');
    const submissionForm = document.getElementById('submission-form-container');
    const taskIdInput = document.getElementById('task_id_input');

    if (getTaskBtn) {
        getTaskBtn.addEventListener('click', async () => {
            getTaskBtn.textContent = 'Думаем...';
            getTaskBtn.disabled = true;

            try {
                const response = await fetch('/api/get-task');
                const data = await response.json();
                
                taskTextElem.textContent = data.text;
                taskIdInput.value = data.id;
                submissionForm.style.display = 'block';

            } catch (error) {
                taskTextElem.textContent = 'Ошибка! Не удалось получить задание. Попробуйте еще раз.';
                console.error('Fetch error:', error);
            } finally {
                getTaskBtn.textContent = 'Получить новое задание!';
                getTaskBtn.disabled = false;
            }
        });
    }

    document.querySelectorAll('.vote-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const submissionId = button.dataset.id;
            const votesSpan = document.getElementById(`votes-${submissionId}`);
            
            try {
                const response = await fetch(`/api/submission/${submissionId}/vote`, { method: 'POST' });
                const data = await response.json();
                votesSpan.textContent = data.votes;
            } catch (error) {
                console.error('Vote error:', error);
            }
        });
    });
});


const API = {
    async get(url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    },
    
    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }
};

// Уведомления
const Notifications = {
    show(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
        
        setTimeout(() => {
            notification.classList.add('notification-show');
        }, 10);
    },
    
    getIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }
};

const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Основной класс приложения
class MutilApp {
    constructor() {
        this.currentTaskId = null; // Текущий ID задания
        this.apiUrl = '/api'; // Базовый URL для  Flask/FastAPI бэкенда
        this.init();
    }

    init() {
        console.log("MutilApp: Фронтенд-приложение инициализировано.");
        this.setupEventListeners(); 
        this.loadInitialData(); 
    }

    setupEventListeners() {
        const getTaskButton = document.getElementById('get-task-button');
        if (getTaskButton) {
            getTaskButton.addEventListener('click', () => this.getNewTask());
        }

        const submitAnswerButton = document.getElementById('submit-answer-button');
        if (submitAnswerButton) {
            submitAnswerButton.addEventListener('click', () => this.submitUserAnswer());
        }
    }

    loadInitialData() {
        this.fetchGalleryAnswers();
    }

    async getNewTask() {
        console.log("MutilApp: Запрашиваем новое задание...");
        try {
            const response = await fetch(`${this.apiUrl}/get_task`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            this.displayTask(data.task); 
            this.currentTaskId = data.task_id;
        } catch (error) {
            console.error("MutilApp: Ошибка при получении задания:", error);
            this.displayTask("Не удалось получить задание. Попробуйте еще раз.");
        }
    }

    displayTask(taskText) {
        const taskDisplayElement = document.getElementById('task-display');
        if (taskDisplayElement) {
            taskDisplayElement.textContent = taskText;
        }
    }

    async submitUserAnswer() {
        console.log("MutilApp: Отправляем ответ пользователя...");
        const answerInput = document.getElementById('answer-input'); 
        const answerText = answerInput ? answerInput.value : '';

        if (!answerText.trim() || !this.currentTaskId) {
            alert('Пожалуйста, введите ответ и убедитесь, что у вас есть текущее задание.');
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/submit_answer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    task_id: this.currentTaskId,
                    answer_data: answerText,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            alert(data.message); 
            answerInput.value = ''; 
            this.fetchGalleryAnswers(); 
        } catch (error) {
            console.error("MutilApp: Ошибка при отправке ответа:", error);
            alert("Не удалось отправить ответ. Попробуйте еще раз.");
        }
    }

    async fetchGalleryAnswers() {
        console.log("MutilApp: Загружаем ответы для галереи...");
        try {
            const response = await fetch(`${this.apiUrl}/gallery`); 
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const answers = await response.json();
            this.renderGallery(answers); 
        } catch (error) {
            console.error("MutilApp: Ошибка при загрузке галереи:", error);
        }
    }

    renderGallery(answers) {
        const galleryContainer = document.getElementById('gallery-container');
        if (!galleryContainer) return;

        galleryContainer.innerHTML = ''; 

        if (answers.length === 0) {
            galleryContainer.innerHTML = '<p>Пока нет ответов в галерее.</p>';
            return;
        }

        answers.forEach(answer => {
            const answerDiv = document.createElement('div');
            answerDiv.className = 'gallery-item';
            answerDiv.innerHTML = `
                <h3>Задание: ${answer.task}</h3>
                <p><strong>Ответ:</strong> ${answer.user_answer}</p>
                ${answer.image_url ? `<img src="${answer.image_url}" alt="Ответ пользователя" style="max-width: 100%;">` : ''}
                <p>Голосов: <span id="votes-${answer.id}">${answer.votes}</span></p>
                <button class="vote-button" data-answer-id="${answer.id}">Голосовать</button>
            `;
            galleryContainer.appendChild(answerDiv);

        
            const voteButton = answerDiv.querySelector(`.vote-button[data-answer-id="${answer.id}"]`);
            if (voteButton) {
                voteButton.addEventListener('click', () => this.voteForAnswer(answer.id));
            }
        });
    }

    async voteForAnswer(answerId) {
        console.log(`MutilApp: Голосуем за ответ ID: ${answerId}`);
        try {
            const response = await fetch(`${this.apiUrl}/vote/${answerId}`, {
                method: 'POST', 
                headers: {
                    'Content-Type': 'application/json',
                },
                
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            alert(data.message);
    
            const votesSpan = document.getElementById(`votes-${answerId}`);
            if (votesSpan) {
                votesSpan.textContent = parseInt(votesSpan.textContent) + 1; 
            }
        } catch (error) {
            console.error("MutilApp: Ошибка при голосовании:", error);
            alert("Не удалось проголосовать.");
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const mutilApp = new MutilApp();
});