// Функции для dashboard
document.addEventListener('DOMContentLoaded', function() {
    initDashboard();
});

function initDashboard() {
    // Отслеживание просмотров товаров
    trackProductViews();
    
    // Инициализация формы отзывов
    initReviewForm();
    
    // Анимация появления элементов
    animateElements();
    
    // Статистика в реальном времени
    updateStats();
}

function trackProductViews() {
    const productCards = document.querySelectorAll('.product-card');
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const productId = entry.target.dataset.productId;
                if (productId && !entry.target.dataset.viewed) {
                    incrementProductViews(productId);
                    entry.target.dataset.viewed = 'true';
                }
            }
        });
    }, observerOptions);
    
    productCards.forEach(card => {
        observer.observe(card);
    });
}

async function incrementProductViews(productId) {
    try {
        const response = await apiRequest(`/api/track_view/${productId}`);
        
        // Обновляем счетчик просмотров
        const viewsElement = document.querySelector(
            `.product-card[data-product-id="${productId}"] .views-badge`
        );
        
        if (viewsElement) {
            const currentViews = parseInt(viewsElement.textContent.match(/\d+/)[0]);
            viewsElement.innerHTML = `<i class="fas fa-eye"></i> ${response.views}`;
            
            // Анимация обновления
            viewsElement.style.transform = 'scale(1.1)';
            setTimeout(() => {
                viewsElement.style.transform = 'scale(1)';
            }, 300);
        }
    } catch (error) {
        console.error('Failed to track view:', error);
    }
}

function initReviewForm() {
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const reviewData = {
                product_id: parseInt(formData.get('product_id')),
                rating: parseInt(formData.get('rating')),
                content: formData.get('content')
            };
            
            try {
                const response = await apiRequest('/api/add_review', {
                    method: 'POST',
                    body: JSON.stringify(reviewData)
                });
                
                if (response.success) {
                    showNotification('Отзыв успешно добавлен!', 'success');
                    closeModal();
                    // Перезагружаем страницу для обновления отзывов
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showNotification(response.error, 'danger');
                }
            } catch (error) {
                showNotification('Ошибка при отправке отзыва', 'danger');
            }
        });
    }
}

function showReviewModal(productId = null, productName = null) {
    const modal = document.getElementById('reviewModal');
    const productIdInput = document.getElementById('reviewProductId');
    const productNameSpan = document.getElementById('reviewProductName');
    
    if (productId && productName) {
        productIdInput.value = productId;
        productNameSpan.textContent = productName;
    } else {
        productIdInput.value = '';
        productNameSpan.textContent = 'Выберите товар';
    }
    
    // Сброс формы
    const form = document.getElementById('reviewForm');
    if (form) {
        form.reset();
    }
    
    showModal('reviewModal');
}

function animateElements() {
    const animateOnScroll = (elements) => {
        elements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 100 * index);
        });
    };
    
    // Анимация товаров
    const productCards = document.querySelectorAll('.product-card');
    animateOnScroll(Array.from(productCards));
    
    // Анимация отзывов
    const reviewCards = document.querySelectorAll('.review-card');
    animateOnScroll(Array.from(reviewCards));
}

async function updateStats() {
    try {
        const stats = await apiRequest('/api/product_stats');
        
        // Здесь можно обновлять статистику в реальном времени
        console.log('Product stats:', stats);
        
    } catch (error) {
        console.error('Failed to fetch stats:', error);
    }
}

// Глобальные функции для использования в HTML
window.showReviewModal = showReviewModal;
window.closeModal = closeModal;