const API_URL = 'http://127.0.0.1:8000/tasks';


function createTaskElement(task) {
    const taskElement = document.createElement('div');
    taskElement.className = 'task';
    taskElement.dataset.id = task.id;
    taskElement.innerHTML = `
        <h3>[${task.id}] ${task.header}</h3>
        <p>${task.description}</p>
        <select class="status-select">
            <option value="new" ${task.status === 'new' ? 'selected' : ''}>New</option>
            <option value="in progress" ${task.status === 'in progress' ? 'selected' : ''}>In Progress</option>
            <option value="done" ${task.status === 'done' ? 'selected' : ''}>Done</option>
        </select>
        <span class="date">Створено: ${task.created_at.split(' ')[0]}</span>
        <hr>
        <button class="delete-btn">🗑 Видалити</button>
    `;
    return taskElement;
}

const tasksContainer = document.getElementById('tasks-container');

async function loadTasks() {
    try {
        const response = await fetch(API_URL);
        const tasks = await response.json();
        tasksContainer.innerHTML = '';

        if (tasks.length === 0) {
            tasksContainer.innerHTML = '<p>Задач поки немає. Створіть першу!</p>';
            return;
        }

        tasks.forEach(task => {
            const el = createTaskElement(task);
            tasksContainer.appendChild(el);
        });

    } catch (error) {
        console.error('Помилка мережі:', error);
        document.getElementById('tasks-container').innerHTML = '<p style="color: red;">Помилка з\'єднання з сервером.</p>';
    }
}

loadTasks();

// Create task

const form = document.getElementById('create-form');

form.addEventListener('submit', async function(event) {
    
    event.preventDefault();

    const headerInput = document.getElementById('new-header').value;
    const descInput = document.getElementById('new-description').value;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                header: headerInput,
                description: descInput
            })
        });

        if (!response.ok) {
            throw new Error(`Помилка сервера: ${response.status}`);
        }

        const newTask = await response.json();
        const el = createTaskElement(newTask);
        tasksContainer.appendChild(el);

        form.reset();

    } catch (error) {
        console.error('Критичний збій при відправці POST-запиту:', error);
        alert("Помилка: не вдалося зберегти задачу. Перевір чи запущений сервер.");
    }
});

// 2. ДЕЛЕГУВАННЯ ПОДІЙ ДЛЯ ВИДАЛЕННЯ

tasksContainer.addEventListener('click', async function(event) {

    const deleteBtn = event.target.closest('.delete-btn');
    if (!deleteBtn) return;

    const taskElement = deleteBtn.closest('.task');
    if (!taskElement) return;

    const taskId = taskElement.dataset.id;

    if (!confirm(`Точно видалити задачу №${taskId}?`)) {
        return; 
    }

    deleteBtn.disabled = true;
    deleteBtn.textContent = 'Видалення...';

    try {
        const response = await fetch(`${API_URL}/${taskId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`Помилка сервера: ${response.status}`);
        }

        taskElement.remove();

    } catch (error) {
        console.error('Помилка при видаленні:', error);
        alert("Не вдалося видалити задачу!");
        deleteBtn.disabled = false;
        deleteBtn.textContent = '🗑 Видалити';
    }
});

// 3. ДЕЛЕГУВАННЯ ПОДІЙ ДЛЯ ОНОВЛЕННЯ СТАТУСУ

tasksContainer.addEventListener('change', async function(event) {

    const statusSelect = event.target.closest('.status-select');
    if (!statusSelect) return;

    const taskElement = statusSelect.closest('.task');
    if (!taskElement) return;
    const taskId = taskElement.dataset.id;

    const newStatus = statusSelect.value;

    try {
        const response = await fetch(`${API_URL}/${taskId}`, {
            method: 'PATCH',
            headers: {
                'Content-type': 'application/json'
            },
            body: JSON.stringify({
                status: newStatus
            })
        });

        if (!response.ok) {
            throw new Error(`Помилка сервера: ${response.status}`);
        }

        console.log(`Статус задачі ${taskId} успішно змінено на ${newStatus}`);

    } catch (error) {
        console.error('Помилка при оновленні статусу:', error);
        alert("Не вдалося оновити статус!");
    }
});