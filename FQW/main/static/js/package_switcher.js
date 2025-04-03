// switch_package.js
document.addEventListener('DOMContentLoaded', function () {
    const packageSwitch = document.getElementById('packageSwitch');
    const optionTables = document.querySelectorAll('.option-table');

    // Обработчик переключения пакетов
    packageSwitch.addEventListener('change', function () {
        optionTables.forEach(table => {
            table.style.display = this.checked ? 'none' : 'table';
        });
    });

    // Добавление дополнительных опций
    const addOptionButton = document.getElementById('addOptionButton');
    const additionalOptionsContainer = document.querySelector('.additional-options-container');

    addOptionButton.addEventListener('click', function () {
        const newOption = `
            <div class="additional-option mb-3">
                <div class="input-group">
                    <input type="text" class="form-control" placeholder="Название опции">
                    <input type="number" class="form-control" placeholder="80 ₽">
                    <input type="number" class="form-control" placeholder="0 дней">
                </div>
                <textarea class="form-control mt-2" rows="3" placeholder="Подсказка для покупателя (очень краткое описание опции)"></textarea>
            </div>
        `;
        additionalOptionsContainer.insertAdjacentHTML('beforeend', newOption);
    });
});