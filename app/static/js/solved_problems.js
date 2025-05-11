const toggleProblem = (problemId) => {
    const content = document.getElementById(`problem-${problemId}`);
    const icon = content.previousElementSibling.querySelector('i');
    const isHidden = content.style.display === 'none';
    
    content.style.display = isHidden ? 'block' : 'none';
    icon.classList.replace(
        isHidden ? 'fa-chevron-down' : 'fa-chevron-up',
        isHidden ? 'fa-chevron-up' : 'fa-chevron-down'
    );
};

const showSolutions = (problemId) => {
    const solutionsDiv = document.getElementById(`solutions-${problemId}`);
    const button = solutionsDiv.previousElementSibling;
    solutionsDiv.style.display = 'block';
    button.style.display = 'none';
};

const showMoreSolutions = (problemId) => {
    fetch(`/api/problems/${problemId}/solutions?offset=3`)
        .then(response => response.json())
        .then(data => {
            const solutionsDiv = document.getElementById(`solutions-${problemId}`);
        });
};

const toggleLike = async (solutionId) => {
    try {
        const response = await fetch(`/api/solutions/${solutionId}/like`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        
        document.querySelectorAll(`.btn-like[onclick*="${solutionId}"]`).forEach(button => {
            const likesCount = button.querySelector('.likes-count');
            const heartIcon = button.querySelector('i');
            
            likesCount.textContent = data.likes;
            heartIcon.classList.toggle('far', !data.liked);
            heartIcon.classList.toggle('fas', data.liked);
            heartIcon.style.color = data.liked ? '#E6E6FA' : '';
        });
    } catch (error) {
        console.error('Error toggling like:', error);
    }
};

const showComments = (solutionId) => {
    const commentsDiv = document.getElementById(`comments-${solutionId}`);
    commentsDiv.style.display = commentsDiv.style.display === 'none' ? 'block' : 'none';
};

const submitComment = async (event, solutionId) => {
    event.preventDefault();
    const form = event.target;
    const textarea = form.querySelector('textarea');
    const comment = textarea.value;
    
    try {
        const response = await fetch(`/api/solutions/${solutionId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comment })
        });
        const data = await response.json();
        
        const commentsList = form.previousElementSibling;
        const newComment = document.createElement('div');
        newComment.className = 'comment';
        newComment.id = `comment-${data.id}`;
        newComment.innerHTML = `
            <div class="comment-header">
                <strong>${data.username}</strong>
                <div class="comment-actions">
                    <button class="btn btn-sm btn-edit" onclick="startEditComment(${data.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-delete" onclick="deleteComment(${data.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <p class="comment-text">${data.comment}</p>
            <div class="comment-edit-form" style="display: none;">
                <textarea class="form-control">${data.comment}</textarea>
                <div class="mt-2">
                    <button class="btn btn-sm btn-primary" onclick="saveEditComment(${data.id})">Сохранить</button>
                    <button class="btn btn-sm btn-secondary" onclick="cancelEditComment(${data.id})">Отмена</button>
                </div>
            </div>
        `;
        commentsList.appendChild(newComment);
        textarea.value = '';
        
        document.querySelectorAll(`.btn-comment[onclick*="${solutionId}"]`).forEach(button => {
            const countSpan = button.querySelector('.comments-count');
            countSpan.textContent = parseInt(countSpan.textContent) + 1;
        });
    } catch (error) {
        console.error('Error submitting comment:', error);
    }
};

const startEditComment = (commentId) => {
    const commentDiv = document.getElementById(`comment-${commentId}`);
    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    const textarea = editForm.querySelector('textarea');
    
    commentText.style.display = 'none';
    editForm.style.display = 'block';
    textarea.value = commentText.textContent;
    textarea.focus();
};

const cancelEditComment = (commentId) => {
    const commentDiv = document.getElementById(`comment-${commentId}`);
    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    
    commentText.style.display = 'block';
    editForm.style.display = 'none';
};

const saveEditComment = async (commentId) => {
    const commentDiv = document.getElementById(`comment-${commentId}`);
    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    const textarea = editForm.querySelector('textarea');
    
    try {
        const response = await fetch(`/api/comments/${commentId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comment: textarea.value })
        });
        const data = await response.json();
        
        commentText.textContent = data.comment;
        commentText.style.display = 'block';
        editForm.style.display = 'none';
    } catch (error) {
        console.error('Error updating comment:', error);
        alert('Ошибка при обновлении комментария');
    }
};

const deleteComment = async (commentId) => {
    if (!confirm('Вы уверены, что хотите удалить этот комментарий?')) return;
    
    try {
        const response = await fetch(`/api/comments/${commentId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        
        const commentDiv = document.getElementById(`comment-${commentId}`);
        const solutionId = commentDiv.closest('.solution-card')
            .querySelector('.btn-comment')
            .getAttribute('onclick')
            .match(/\d+/)[0];
        
        commentDiv.remove();
        
        document.querySelectorAll(`.btn-comment[onclick*="${solutionId}"]`).forEach(button => {
            const countSpan = button.querySelector('.comments-count');
            countSpan.textContent = parseInt(countSpan.textContent) - 1;
        });
    } catch (error) {
        console.error('Error deleting comment:', error);
        alert('Ошибка при удалении комментария');
    }
}; 