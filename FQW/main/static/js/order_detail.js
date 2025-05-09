document.addEventListener('DOMContentLoaded', function () {
  const acceptOrderBtn = document.getElementById('accept-order-btn');
  const rejectOrderBtn = document.getElementById('reject-order-btn');
  const actionButtons = document.getElementById('action-buttons');
  const orderStatus = document.getElementById('order-status');
  const chatSection = document.getElementById('chat-section');

  // Обработка нажатия кнопки "Принять заказ"
  if (acceptOrderBtn) {
    acceptOrderBtn.addEventListener('click', function (event) {
      event.preventDefault(); // Предотвращаем отправку формы

      // Отправляем AJAX-запрос на сервер для принятия заказа
      fetch(window.location.href, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') // Получаем CSRF-токен
        },
        body: JSON.stringify({ accept_order: true })
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Обновляем интерфейс
            orderStatus.innerHTML = '<span class="badge bg-primary">Статус: Обсуждение</span>';
            actionButtons.style.display = 'none'; // Скрываем кнопки принятия/отклонения
            chatSection.style.display = 'block'; // Показываем чат
          } else {
            alert('Ошибка при принятии заказа.');
          }
        })
        .catch(error => console.error('Ошибка:', error));
    });
  }

  // Обработка нажатия кнопки "Отклонить заказ"
  if (rejectOrderBtn) {
    rejectOrderBtn.addEventListener('click', function (event) {
      event.preventDefault(); // Предотвращаем отправку формы

      // Отправляем AJAX-запрос на сервер для отклонения заказа
      fetch(window.location.href, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') // Получаем CSRF-токен
        },
        body: JSON.stringify({ reject_order: true })
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            window.location.href = '/my-orders/'; // Перенаправляем на страницу "Мои заказы"
          } else {
            alert('Ошибка при отклонении заказа.');
          }
        })
        .catch(error => console.error('Ошибка:', error));
    });
  }
});

// Функция для получения CSRF-токена из cookies
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