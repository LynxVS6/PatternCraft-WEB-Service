
async function downloadCourse(courseId) {
    console.log('downloadCourse called with courseId:', courseId);
    
    try {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }

        // Отправляем запрос для получения данных курса
        const response = await fetch(`/courses/api/${courseId}/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
            body: JSON.stringify({
                course_id: courseId,
                timestamp: new Date().toISOString(),
            })
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

        const labUrl = `http://localhost:3000/courses/${courseId}`;
        console.log('Redirecting to lab:', labUrl);

        window.open(labUrl, '_blank');

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
