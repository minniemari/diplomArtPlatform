document.addEventListener('DOMContentLoaded', function () {
    const switchCheckbox = document.getElementById('packageSwitch');
    const switchLabel = document.getElementById('switch-label');

    // Заголовки столбцов
    const basicColumn = document.querySelector('table thead th:nth-child(2)');
    const standardColumn = document.querySelector('table thead th:nth-child(3)');
    const premiumColumn = document.querySelector('table thead th:nth-child(4)');

    // Строки таблицы
    const rowGroups = Array.from(document.querySelectorAll('table tbody tr')).map(row => ({
        basic: row.querySelector('td:nth-child(2)'),
        standard: row.querySelector('td:nth-child(3)'),
        premium: row.querySelector('td:nth-child(4)'),
    }));

    // Начальное состояние - показываем только стандартный пакет
    togglePackages(false);

    // Обработчик изменения состояния переключателя
    switchCheckbox.addEventListener('change', function () {
        togglePackages(this.checked);
    });

    function togglePackages(showAll) {
        if (showAll) {
            // Показать все пакеты
            basicColumn.style.display = '';
            standardColumn.style.display = '';
            premiumColumn.style.display = '';
            rowGroups.forEach(group => {
                group.basic.style.display = '';
                group.standard.style.display = '';
                group.premium.style.display = '';
            });
            switchLabel.textContent = '3 пакета';
        } else {
            // Показать только стандартный пакет
            basicColumn.style.display = 'none';
            standardColumn.style.display = '';
            premiumColumn.style.display = 'none';
            rowGroups.forEach(group => {
                group.basic.style.display = 'none';
                group.standard.style.display = '';
                group.premium.style.display = 'none';
            });
            switchLabel.textContent = '1 пакет (Стандартный)';
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const addOptionButton = document.getElementById('addOptionButton');
    const additionalOptionsContainer = document.querySelector('.additional-options-container');

    addOptionButton.addEventListener('click', function () {
        const newOption = `
            <div class="additional-option mb-3">
                <div class="input-group">
                    <input type="text" class="form-control" name="additional_option_name[]" placeholder="Название опции">
                    <input type="number" class="form-control" name="additional_option_price[]" placeholder="80 ₽">
                    <input type="number" class="form-control" name="additional_option_deadline[]" placeholder="0 дней">
                </div>
                <textarea class="form-control mt-2" rows="3" name="additional_option_description[]" placeholder="Подсказка для покупателя (очень краткое описание опции)"></textarea>
            </div>
        `;
        additionalOptionsContainer.insertAdjacentHTML('beforeend', newOption);
    });
});
document.addEventListener('DOMContentLoaded', function () {
    const uploadButton = document.getElementById('uploadButton');
    const imageInput = document.getElementById('imageUpload');
    const modal = document.getElementById('uploadModal');

    let selectedButton = null;

    // Отслеживаем, какая кнопка была нажата
    document.querySelectorAll('.portfolio-button').forEach(button => {
        button.addEventListener('click', function () {
            selectedButton = this;
        });
    });

    // Обработчик загрузки изображения
    uploadButton.addEventListener('click', function () {
        const file = imageInput.files[0];
        if (!file) {
            alert('Выберите файл для загрузки.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload-portfolio/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Устанавливаем изображение на кнопку
                    const img = document.createElement('img');
                    img.src = data.image_url;
                    img.classList.add('portfolio-image');

                    selectedButton.innerHTML = '';
                    selectedButton.appendChild(img);

                    // Закрываем модальное окно
                    const bootstrapModal = bootstrap.Modal.getInstance(modal);
                    bootstrapModal.hide();
                } else {
                    alert('Ошибка при загрузке файла.');
                }
            });
    });

    // Функция для получения CSRF-токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});