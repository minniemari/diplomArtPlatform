document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('input[name="additional_options"]');
    const totalPriceElement = document.getElementById('totalPrice');
    const totalDeadlineElement = document.getElementById('totalDeadline');

    // Начальные значения
    let totalPrice = parseFloat(totalPriceElement.textContent.replace(/[^0-9.]/g, ''));
    let totalDeadline = parseInt(totalDeadlineElement.textContent.replace(/[^0-9]/g, ''));

    // Обработчик изменения чекбоксов
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const priceChange = parseFloat(this.dataset.price);
            const deadlineChange = parseInt(this.dataset.deadline);

            if (this.checked) {
                totalPrice += priceChange;
                totalDeadline += deadlineChange;
            } else {
                totalPrice -= priceChange;
                totalDeadline -= deadlineChange;
            }

            // Обновляем отображение
            totalPriceElement.textContent = `${totalPrice.toFixed(2)} ₽`;
            totalDeadlineElement.textContent = `${totalDeadline} дней`;
        });
    });

    // Обработчик кнопки "Прикрепить файлы"
    const attachFilesButton = document.getElementById('attachFilesButton');
    const attachedFilesInput = document.getElementById('attachedFiles');

    attachFilesButton.addEventListener('click', function () {
        attachedFilesInput.click();
    });

    attachedFilesInput.addEventListener('change', function () {
        const files = Array.from(this.files);
        console.log(`Прикреплено файлов: ${files.length}`);
    });
});