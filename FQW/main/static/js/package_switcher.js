document.addEventListener('DOMContentLoaded', function () {
    const packageTabs = document.querySelectorAll('.nav-link');
    const packagePrice = document.getElementById('package-price');
    const packageDescription = document.getElementById('package-description');
    const packageDetails = document.getElementById('package-details');

    packageTabs.forEach(tab => {
        tab.addEventListener('click', function () {
            packageTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            const packageType = this.getAttribute('data-package');
            const option = document.getElementById(`option-${packageType}`);

            if (option) {
                packagePrice.textContent = option.dataset.price + ' ₽';
                packageDescription.textContent = option.dataset.description;
                packageDetails.innerHTML = option.dataset.details;
            }
        });
    });
});