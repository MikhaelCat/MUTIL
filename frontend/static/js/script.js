const API_BASE_URL = '/api'; 

document.addEventListener('DOMContentLoaded', () => {
    const newTaskBtn = document.getElementById('new-task-btn');
    const taskTextElement = document.getElementById('task-text');
    const responseSection = document.getElementById('response-section');
    const responseForm = document.getElementById('response-form');

    newTaskBtn.addEventListener('click', fetchNewTask);
    responseForm.addEventListener('submit', submitResponse);

    async function fetchNewTask() {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({}) 
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const task = await response.json();
            taskTextElement.textContent = task.text;
            responseSection.style.display = 'block'; // Показываем форму ответа
        } catch (error) {
            console.error('Ошибка при получении задания:', error);
            taskTextElement.textContent = 'Не удалось получить задание. Попробуйте еще раз.';
        }
    }

    async function submitResponse(event) {
        event.preventDefault();
        // Пока просто показываем сообщение, так как API для отправки ответов еще не реализовано
        alert('Ответ отправлен! (Функционал в разработке)');
        // Здесь будет логика отправки ответа на сервер
    }
});
