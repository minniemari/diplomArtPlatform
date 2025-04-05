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
        premium: row.querySelector('td:nth-child(4)')
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

            // Включить все поля
            rowGroups.forEach(group => {
                group.basic.style.display = '';
                group.standard.style.display = '';
                group.premium.style.display = '';
                enableFields(group.basic);
                enableFields(group.standard);
                enableFields(group.premium);
            });
            switchLabel.textContent = '3 пакета';
        } else {
            // Показать только стандартный пакет
            basicColumn.style.display = 'none';
            standardColumn.style.display = '';
            premiumColumn.style.display = 'none';

            // Отключить базовый и премиум пакеты
            rowGroups.forEach(group => {
                group.basic.style.display = 'none';
                group.standard.style.display = '';
                group.premium.style.display = 'none';
                disableFields(group.basic);
                disableFields(group.premium);
            });
            switchLabel.textContent = '1 пакет (Стандартный)';
        }
    }

    // Функция для включения полей
    function enableFields(cell) {
        const inputs = cell.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.disabled = false;
            input.required = true;
        });
    }

    // Функция для отключения полей
    function disableFields(cell) {
        const inputs = cell.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.disabled = true;
            input.required = false;
        });
    }

    // Добавление дополнительных опций
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