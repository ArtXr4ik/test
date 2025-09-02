// Увеличение просмотров при наведении на товар
document.addEventListener('DOMContentLoaded', function() {
    // Отслеживание просмотров товаров
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        const productId = card.dataset.productId;
        if (productId) {
            // Увеличиваем просмотры при первом появлении в viewport
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        incrementProductViews(productId);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(card);
        }
    });

    // Обработка формы отзывов
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const reviewData = {
                content: formData.get('content'),
                rating: formData.get('rating'),
                product_name: formData.get('product_name')
            };
            
            try {
                const response = await fetch('/api/add_review', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(reviewData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Отзыв успешно добавлен!');
                    this.reset();
                    location.reload();
                } else {
                    alert('Ошибка: ' + result.error);
                }
            } catch (error) {
                alert('Ошибка при отправке отзыва');
            }
        });
    }

    // Анимация появления элементов
    animateElements();
});

// Функция увеличения просмотров
async function incrementProductViews(productId) {
    try {
        const response = await fetch(`/api/increment_views/${productId}`);
        const data = await response.json();
        
        // Обновляем счетчик на странице
        const viewsElement = document.querySelector(`.product-card[data-product-id="${productId}"] .views-count`);
        if (viewsElement) {
            viewsElement.textContent = data.views;
        }
    } catch (error) {
        console.error('Ошибка при обновлении просмотров:', error);
    }
}

// Анимация появления элементов
function animateElements() {
    const elements = document.querySelectorAll('.product-card, .review-item');
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

// Проверка доступности email
async function checkEmailAvailability(email) {
    if (!email) return;
    
    const statusElement = document.getElementById('email-status');
    if (!statusElement) return;
    
    try {
        const response = await fetch(`/api/check_email?email=${encodeURIComponent(email)}`);
        const data = await response.json();
        
        if (data.available) {
            statusElement.textContent = 'Email доступен';
            statusElement.className = 'email-available';
        } else {
            statusElement.textContent = 'Email уже занят';
            statusElement.className = 'email-taken';
        }
    } catch (error) {
        statusElement.textContent = 'Ошибка проверки';
        statusElement.className = 'email-taken';
    }
}

// Валидация паролей
function validatePassword() {
    const password = document.getElementById('password');
    const confirmPassword = document.querySelector('input[name="confirm_password"]');
    const matchElement = document.getElementById('password-match');
    
    if (!password || !confirmPassword || !matchElement) return;
    
    if (confirmPassword.value && password.value !== confirmPassword.value) {
        matchElement.textContent = 'Пароли не совпадают';
        matchElement.className = 'password-mismatch';
    } else if (confirmPassword.value) {
        matchElement.textContent = 'Пароли совпадают';
        matchElement.className = 'password-match';
    } else {
        matchElement.textContent = '';
    }
}