document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('input[name="additional_options"]');
    const totalPriceElement = document.getElementById('totalPrice');
    const totalDeadlineElement = document.getElementById('totalDeadline');

    let basePrice = parseFloat(totalPriceElement.textContent);
    let baseDeadline = parseInt(totalDeadlineElement.textContent);

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            let totalPrice = basePrice;
            let totalDeadline = baseDeadline;

            checkboxes.forEach(cb => {
                if (cb.checked) {
                    const price = parseFloat(cb.dataset.price);
                    const deadline = parseInt(cb.dataset.deadline);
                    totalPrice += price;
                    totalDeadline += deadline;
                }
            });

            totalPriceElement.textContent = `${totalPrice} ₽`;
            totalDeadlineElement.textContent = `${totalDeadline} дней`;
        });
    });
});