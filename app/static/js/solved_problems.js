function toggleProblem(problemId) {
    const content = document.getElementById(`problem-${problemId}`);
    const icon = content.previousElementSibling.querySelector('i');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
    } else {
        content.style.display = 'none';
        icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
    }
}

function showSolutions(problemId) {
    const solutionsDiv = document.getElementById(`solutions-${problemId}`);
    const button = solutionsDiv.previousElementSibling;
    solutionsDiv.style.display = 'block';
    button.style.display = 'none';
}

function showMoreSolutions(problemId) {
    fetch(`/api/problems/${problemId}/solutions?offset=3`)
        .then(response => response.json())
        .then(data => {
            const solutionsDiv = document.getElementById(`solutions-${problemId}`);
            // Add new solutions to the list
            // Hide "Show more" button if all solutions are loaded
        });
}

function toggleLike(solutionId) {
    fetch(`/api/solutions/${solutionId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        const likeButtons = document.querySelectorAll(`.btn-like[onclick*="${solutionId}"]`);
        
        likeButtons.forEach(button => {
            const likesCount = button.querySelector('.likes-count');
            const heartIcon = button.querySelector('i');
            
            likesCount.textContent = data.likes;
            
            if (data.liked) {
                heartIcon.classList.remove('far');
                heartIcon.classList.add('fas');
                heartIcon.style.color = '#E6E6FA';
            } else {
                heartIcon.classList.remove('fas');
                heartIcon.classList.add('far');
                heartIcon.style.color = '';
            }
        });
    })
    .catch(error => {
        console.error('Error toggling like:', error);
    });
}

function showComments(solutionId) {
    const commentsDiv = document.getElementById(`comments-${solutionId}`);
    commentsDiv.style.display = commentsDiv.style.display === 'none' ? 'block' : 'none';
}

function submitComment(event, solutionId) {
    event.preventDefault();
    const form = event.target;
    const textarea = form.querySelector('textarea');
    const comment = textarea.value;
    
    fetch(`/api/solutions/${solutionId}/comments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comment })
    })
    .then(response => response.json())
    .then(data => {
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
        
        // Update comment count
        const commentButtons = document.querySelectorAll(`.btn-comment[onclick*="${solutionId}"]`);
        commentButtons.forEach(button => {
            const countSpan = button.querySelector('.comments-count');
            countSpan.textContent = parseInt(countSpan.textContent) + 1;
        });
    });
}

function startEditComment(commentId) {
    const commentDiv = document.getElementById(`comment-${commentId}`);
    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    const textarea = editForm.querySelector('textarea');
    
    commentText.style.display = 'none';
    editForm.style.display = 'block';
    textarea.value = commentText.textContent;
    textarea.focus();
}

function cancelEditComment(commentId) {
    const commentDiv = document.getElementById(`comment-${commentId}`);
    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    
    commentText.style.display = 'block';
    editForm.style.display = 'none';
}

function saveEditComment(commentId) {
    const commentDiv = document.getElementById(`comment-${commentId}`);
    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    const textarea = editForm.querySelector('textarea');
    const newComment = textarea.value;
    
    fetch(`/api/comments/${commentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comment: newComment })
    })
    .then(response => response.json())
    .then(data => {
        commentText.textContent = data.comment;
        commentText.style.display = 'block';
        editForm.style.display = 'none';
    })
    .catch(error => {
        console.error('Error updating comment:', error);
        alert('Ошибка при обновлении комментария');
    });
}

function deleteComment(commentId) {
    if (!confirm('Вы уверены, что хотите удалить этот комментарий?')) {
        return;
    }
    
    fetch(`/api/comments/${commentId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        const commentDiv = document.getElementById(`comment-${commentId}`);
        const solutionId = commentDiv.closest('.solution-card').querySelector('.btn-comment').getAttribute('onclick').match(/\d+/)[0];
        commentDiv.remove();
        
        // Update comment count
        const commentButtons = document.querySelectorAll(`.btn-comment[onclick*="${solutionId}"]`);
        commentButtons.forEach(button => {
            const countSpan = button.querySelector('.comments-count');
            countSpan.textContent = parseInt(countSpan.textContent) - 1;
        });
    })
    .catch(error => {
        console.error('Error deleting comment:', error);
        alert('Ошибка при удалении комментария');
    });
} 