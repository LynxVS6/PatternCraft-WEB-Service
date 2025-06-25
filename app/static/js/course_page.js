const getCsrfToken = () => {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
};

async function downloadCourse(courseId, labUrl) {
    console.log('downloadCourse called with courseId:', courseId);
    
    try {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }

        // Отправляем запрос для получения данных курса
        const response = await fetch(`/courses/api/${courseId}/download`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include'
        });

        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error(`Failed to get course data: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        console.log('Course data received:', result);

        const courseLabUrl = `${labUrl}/course/${courseId}`;
        console.log('Redirecting to lab:', courseLabUrl);

        window.open(courseLabUrl, '_blank');

        alert('Курс открыт в лаборатории!');

       

    } catch (error) {
        console.error('Error downloading course:', error);
        alert('Failed to download course. Please try again.');
    } finally {
        setTimeout(() => {
            const downloadBtn = document.querySelector(`.download-btn[data-course-id="${courseId}"]`);
            if (downloadBtn) {
                downloadBtn.disabled = false;
            }
        }, 500);
    }
}
