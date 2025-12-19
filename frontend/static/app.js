// Глобальные переменные
let currentUser = null;
let currentSessionId = null;
let currentProduct = null;
const API_BASE = 'http://localhost:8000/api';

// Утилиты
function showMessage(text, type = 'info') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 3000);
}

function hideAllSections() {
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
}

// Аутентификация
async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('username-display').textContent = currentUser.username;
            document.getElementById('user-info').style.display = 'block';
            hideAllSections();
            showMainMenu();
            showMessage('Успешный вход в систему', 'success');
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка входа', 'error');
        }
    } catch (error) {
        showMessage('Ошибка соединения с сервером', 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const userType = document.getElementById('register-user-type').value;

    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('email', email);
        formData.append('password', password);
        formData.append('user_type', userType);
        
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            showMessage('Регистрация успешна! Войдите в систему', 'success');
            showLogin();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка регистрации', 'error');
        }
    } catch (error) {
        showMessage('Ошибка соединения с сервером', 'error');
    }
}

function showLogin() {
    hideAllSections();
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('register-section').style.display = 'none';
}

function showRegister() {
    hideAllSections();
    document.getElementById('register-section').style.display = 'block';
    document.getElementById('login-section').style.display = 'none';
}

function logout() {
    currentUser = null;
    currentSessionId = null;
    currentProduct = null;
    document.getElementById('user-info').style.display = 'none';
    hideAllSections();
    showLogin();
    showMessage('Вы вышли из системы', 'info');
}

// Навигация
function showMainMenu() {
    hideAllSections();
    document.getElementById('main-menu').style.display = 'block';
    
    // Показываем кнопку загрузки только для владельцев
    const uploadBtn = document.getElementById('upload-btn');
    const productsBtn = document.getElementById('products-menu-btn');
    if (currentUser && currentUser.user_type === 'owner') {
        uploadBtn.style.display = 'block';
        productsBtn.textContent = 'Продукты';
    } else {
        uploadBtn.style.display = 'none';
        productsBtn.textContent = 'Каталог продуктов';
    }
}

async function showProductsMenu() {
    hideAllSections();
    document.getElementById('products-menu').style.display = 'block';
    
    // Изменяем заголовок для владельца
    const titleEl = document.getElementById('products-menu-title');
    if (currentUser && currentUser.user_type === 'owner') {
        titleEl.textContent = 'Продукты';
    } else {
        titleEl.textContent = 'Каталог продуктов';
    }
    
    try {
        // Для владельца получаем все его продукты, для остальных - только проверенные
        const url = currentUser && currentUser.user_type === 'owner' 
            ? `${API_BASE}/products?owner_id=${currentUser.id}`
            : `${API_BASE}/products`;
        const response = await fetch(url);
        if (response.ok) {
            const products = await response.json();
            displayProducts(products);
        } else {
            showMessage('Ошибка загрузки продуктов', 'error');
        }
    } catch (error) {
        showMessage('Ошибка соединения с сервером', 'error');
    }
}

function displayProducts(products) {
    const productsList = document.getElementById('products-list');
    if (products.length === 0) {
        productsList.innerHTML = '<p>Продукты не найдены</p>';
        return;
    }

    const isOwner = currentUser && currentUser.user_type === 'owner';
    
    productsList.innerHTML = products.map(product => {
        const ownerControls = isOwner ? `
            <div class="product-actions">
                <button class="btn-edit" onclick="editProduct(${product.id})">Редактировать</button>
                <button class="btn-delete" onclick="deleteProduct(${product.id})">Удалить</button>
            </div>
        ` : '';
        
        const demoButton = !isOwner ? `<button class="btn-demo" onclick="startSimulation(${product.id})">Начать демо</button>` : '';
        
        return `
        <div class="product-card">
            <h3>${product.name}</h3>
            <p>${product.description || 'Нет описания'}</p>
            <p><strong>Статус:</strong> ${product.status}</p>
            ${demoButton}
            ${ownerControls}
        </div>
    `;
    }).join('');
}

function showUploadMenu() {
    hideAllSections();
    document.getElementById('upload-menu').style.display = 'block';
    // Сбрасываем форму редактирования если была
    document.getElementById('upload-form').reset();
    delete document.getElementById('upload-form').dataset.editId;
    document.querySelector('#upload-menu h2').textContent = 'Загрузка моделей';
    const submitBtn = document.querySelector('#upload-form button[type="submit"]');
    submitBtn.textContent = 'Загрузить продукт';
    submitBtn.onclick = null;
}

// Загрузка продукта
async function handleUpload(event) {
    event.preventDefault();
    
    if (!currentUser || currentUser.user_type !== 'owner') {
        showMessage('Только владельцы могут загружать продукты', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('name', document.getElementById('product-name').value);
    formData.append('description', document.getElementById('product-description').value);
    formData.append('owner_id', currentUser.id);
    
    const characteristicsText = document.getElementById('product-characteristics').value;
    if (characteristicsText) {
        formData.append('characteristics', characteristicsText);
    }
    
    const scenariosText = document.getElementById('product-scenarios').value;
    if (scenariosText) {
        formData.append('scenarios', scenariosText);
    }
    
    const modelFile = document.getElementById('model-file').files[0];
    if (modelFile) {
        formData.append('model_file', modelFile);
    }

    try {
        const response = await fetch(`${API_BASE}/products/upload`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            showMessage(result.message || 'Продукт успешно загружен', 'success');
            document.getElementById('upload-form').reset();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка загрузки продукта', 'error');
        }
    } catch (error) {
        showMessage('Ошибка соединения с сервером', 'error');
    }
}

// Симуляция
async function startSimulation(productId) {
    if (!currentUser) {
        showMessage('Необходимо войти в систему', 'error');
        return;
    }

    try {
        // Получаем информацию о продукте
        const productResponse = await fetch(`${API_BASE}/products/${productId}`);
        if (!productResponse.ok) {
            showMessage('Ошибка загрузки продукта', 'error');
            return;
        }
        currentProduct = await productResponse.json();

        // Создаем сеанс
        // #region agent log
        const requestData = {
            user_id: currentUser.id,
            product_id: productId,
            scenario_id: currentProduct.scenarios && currentProduct.scenarios.length > 0 
                ? currentProduct.scenarios[0].id 
                : null
        };
        fetch('http://127.0.0.1:7242/ingest/5e0f57cb-de49-42b6-9ad8-36f797dc9728',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:startSimulation',message:'Before create-session request',data:{currentUser:currentUser,productId:productId,requestData:requestData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
        // #endregion
        const sessionResponse = await fetch(`${API_BASE}/simulation/create-session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/5e0f57cb-de49-42b6-9ad8-36f797dc9728',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:startSimulation',message:'After create-session request',data:{status:sessionResponse.status,ok:sessionResponse.ok},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
        // #endregion

        if (sessionResponse.ok) {
            const sessionData = await sessionResponse.json();
            currentSessionId = sessionData.session_id;

            // Инициализируем симуляцию
            const initResponse = await fetch(`${API_BASE}/simulation/${currentSessionId}/initialize`, {
                method: 'POST'
            });

        if (initResponse.ok) {
            const initData = await initResponse.json();
            // Обновляем информацию о продукте с URL модели если есть
            if (initData.environment && initData.environment.product && initData.environment.product.model_file_url) {
                currentProduct.model_file_url = initData.environment.product.model_file_url;
            }
            hideAllSections();
            document.getElementById('simulation-page').style.display = 'block';
            displaySimulationPage();
            addLog('Сеанс симуляции создан и инициализирован', 'success');
        } else {
            showMessage('Ошибка инициализации симуляции', 'error');
        }
        } else {
            showMessage('Ошибка создания сеанса', 'error');
        }
    } catch (error) {
        showMessage('Ошибка соединения с сервером', 'error');
    }
}

function displaySimulationPage() {
    const productInfo = document.getElementById('product-info');
    productInfo.innerHTML = `
        <h3>${currentProduct.name}</h3>
        <p>${currentProduct.description || 'Нет описания'}</p>
        <p><strong>ID продукта:</strong> ${currentProduct.id}</p>
    `;

    // Отображение информации о модели
    const modelFilePath = document.getElementById('model-file-path');
    const modelPlaceholder = document.getElementById('model-placeholder');
    const modelCanvas = document.getElementById('model-canvas');
    
    if (currentProduct.model_file_path) {
        const fileName = currentProduct.model_file_path.split('/').pop() || currentProduct.model_file_path.split('\\').pop();
        if (modelFilePath) {
            modelFilePath.textContent = fileName;
        }
        
        // Преобразуем абсолютный путь в относительный URL
        const modelUrl = getModelUrl(currentProduct.model_file_path);
        
        if (modelPlaceholder) {
            modelPlaceholder.innerHTML = `
                <p><strong>Модель:</strong> ${fileName}</p>
                <p><a href="${modelUrl}" target="_blank" download="${fileName}">Скачать модель</a></p>
                <p class="model-info">Для просмотра 3D модели используйте внешний просмотрщик или загрузите файл</p>
            `;
            modelPlaceholder.style.display = 'block';
        }
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/5e0f57cb-de49-42b6-9ad8-36f797dc9728',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:displaySimulationPage',message:'Model file path processed',data:{originalPath:currentProduct.model_file_path,fileName:fileName,modelUrl:modelUrl},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
        // #endregion
        
        addLog(`Модель загружена: ${fileName}`, 'info');
        addLog(`URL модели: ${modelUrl}`, 'info');
    } else {
        if (modelPlaceholder) {
            modelPlaceholder.innerHTML = '<p>Модель не загружена</p>';
        }
    }

    const log = document.getElementById('simulation-log');
    log.innerHTML = '';
}

function getModelUrl(filePath) {
    // Используем model_file_url если он есть (передан с сервера)
    if (currentProduct && currentProduct.model_file_url) {
        return currentProduct.model_file_url;
    }
    
    // Иначе преобразуем абсолютный путь сервера в относительный URL
    if (!filePath) return '';
    
    // Извлекаем имя файла
    const fileName = filePath.split('/').pop() || filePath.split('\\').pop();
    
    // Возвращаем URL для доступа через статические файлы
    return `/uploads/models/${fileName}`;
}

function addLog(message, type = 'info') {
    const log = document.getElementById('simulation-log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

async function simulateClick() {
    await processInteraction('click', { x: 100, y: 100 });
}

async function simulateRotate() {
    await processInteraction('rotate', { angle: 45 });
}

async function simulateZoom() {
    await processInteraction('zoom', { level: 1.5 });
}

async function runTesting() {
    if (!currentSessionId) {
        addLog('Сеанс не создан', 'error');
        return;
    }

    addLog('Запуск автоматического тестирования...', 'info');
    
    // Последовательность тестовых взаимодействий
    const tests = [
        { type: 'click', data: { x: 100, y: 100 }, delay: 500 },
        { type: 'click', data: { x: 200, y: 200 }, delay: 500 },
        { type: 'rotate', data: { angle: 90 }, delay: 500 },
        { type: 'rotate', data: { angle: 180 }, delay: 500 },
        { type: 'zoom', data: { level: 2.0 }, delay: 500 },
        { type: 'zoom', data: { level: 1.0 }, delay: 500 },
    ];

    for (let i = 0; i < tests.length; i++) {
        const test = tests[i];
        addLog(`Тест ${i + 1}/${tests.length}: ${test.type}`, 'info');
        await processInteraction(test.type, test.data);
        
        if (i < tests.length - 1) {
            await new Promise(resolve => setTimeout(resolve, test.delay));
        }
    }

    addLog('Автоматическое тестирование завершено', 'success');
}

async function processInteraction(type, data) {
    if (!currentSessionId) {
        addLog('Сеанс не создан', 'error');
        return;
    }

    try {
        // #region agent log
        const requestData = {
            interaction_type: type,
            interaction_data: data
        };
        fetch('http://127.0.0.1:7242/ingest/5e0f57cb-de49-42b6-9ad8-36f797dc9728',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:processInteraction',message:'Before interact request',data:{sessionId:currentSessionId,requestData:requestData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
        // #endregion
        const response = await fetch(`${API_BASE}/simulation/${currentSessionId}/interact`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/5e0f57cb-de49-42b6-9ad8-36f797dc9728',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:processInteraction',message:'After interact request',data:{status:response.status,ok:response.ok},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
        // #endregion

        if (response.ok) {
            const result = await response.json();
            addLog(`Взаимодействие "${type}" обработано: ${result.result.response}`, 'success');
        } else {
            const error = await response.json();
            addLog(`Ошибка: ${error.detail}`, 'error');
        }
    } catch (error) {
        addLog('Ошибка соединения с сервером', 'error');
    }
}

async function finalizeSimulation() {
    if (!currentSessionId) {
        showMessage('Сеанс не создан', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/simulation/${currentSessionId}/finalize`, {
            method: 'POST'
        });

        if (response.ok) {
            const result = await response.json();
            addLog(`Сеанс завершен. Всего взаимодействий: ${result.total_interactions}`, 'success');
            showMessage('Сеанс тестирования завершен', 'success');
            setTimeout(() => {
                showProductsMenu();
            }, 2000);
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка завершения сеанса', 'error');
        }
    } catch (error) {
        showMessage('Ошибка соединения с сервером', 'error');
    }
}

// Управление продуктами для владельца
async function deleteProduct(productId) {
    if (!currentUser || currentUser.user_type !== 'owner') {
        showMessage('Только владельцы могут удалять продукты', 'error');
        return;
    }
    
    if (!confirm('Вы уверены, что хотите удалить этот продукт?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/products/${productId}?owner_id=${currentUser.id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showMessage('Продукт успешно удален', 'success');
            showProductsMenu(); // Обновляем список
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка удаления продукта', 'error');
        }
    } catch (error) {
        showMessage('Ошибка соединения с сервером', 'error');
    }
}

async function editProduct(productId) {
    if (!currentUser || currentUser.user_type !== 'owner') {
        showMessage('Только владельцы могут редактировать продукты', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`);
        if (!response.ok) {
            showMessage('Ошибка загрузки продукта', 'error');
            return;
        }
        
        const product = await response.json();
        
        // Заполняем форму загрузки данными продукта
        document.getElementById('product-name').value = product.name;
        document.getElementById('product-description').value = product.description || '';
        
        // Сохраняем ID продукта для обновления
        document.getElementById('upload-form').dataset.editId = productId;
        
        // Переходим на форму загрузки
        showUploadMenu();
        
        // Меняем заголовок и кнопку
        document.querySelector('#upload-menu h2').textContent = 'Редактирование продукта';
        const submitBtn = document.querySelector('#upload-form button[type="submit"]');
        submitBtn.textContent = 'Сохранить изменения';
        submitBtn.onclick = (e) => {
            e.preventDefault();
            handleUpdateProduct(productId);
        };
    } catch (error) {
        showMessage('Ошибка соединения с сервером', 'error');
    }
}

async function handleUpdateProduct(productId) {
    if (!currentUser || currentUser.user_type !== 'owner') {
        showMessage('Только владельцы могут редактировать продукты', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('name', document.getElementById('product-name').value);
    formData.append('description', document.getElementById('product-description').value);
    formData.append('owner_id', currentUser.id);
    
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`, {
            method: 'PUT',
            body: formData
        });
        
        if (response.ok) {
            showMessage('Продукт успешно обновлен', 'success');
            // Сбрасываем форму
            document.getElementById('upload-form').reset();
            delete document.getElementById('upload-form').dataset.editId;
            document.querySelector('#upload-menu h2').textContent = 'Загрузка моделей';
            const submitBtn = document.querySelector('#upload-form button[type="submit"]');
            submitBtn.textContent = 'Загрузить продукт';
            submitBtn.onclick = null;
            // Возвращаемся к списку продуктов
            showProductsMenu();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка обновления продукта', 'error');
        }
    } catch (error) {
        showMessage('Ошибка соединения с сервером', 'error');
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    showLogin();
});

