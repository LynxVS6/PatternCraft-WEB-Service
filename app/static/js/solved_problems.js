const toggleProblem = (problemId) => {
    const card = document.querySelector(`.problem-card[data-id="${problemId}"]`);
    const details = card.querySelector('.problem-details');
    const toggle = card.querySelector('.problem-toggle');
    const isHidden = details.style.display === 'none';
    
    details.style.display = isHidden ? 'block' : 'none';
    toggle.classList.toggle('active', isHidden);
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
        .then(solutions => {
            const solutionsDiv = document.getElementById(`solutions-${problemId}`);
            solutions.forEach(solution => {
                const solutionCard = createSolutionCard(solution);
                solutionsDiv.insertBefore(solutionCard, solutionsDiv.lastElementChild);
            });
        })
        .catch(error => console.error('Error loading more solutions:', error));
};

const createSolutionCard = (solution) => {
    const card = document.createElement('div');
    card.className = 'solution-card';
    card.innerHTML = `
        <div class="solution-content">
            ${solution.solution}
        </div>
        <div class="solution-actions">
            <button class="btn btn-like" onclick="toggleLike(${solution.id})">
                <i class="far fa-heart"></i>
                <span class="likes-count">${solution.likes}</span>
            </button>
            <button class="btn btn-comment" onclick="showComments(${solution.id})">
                <i class="far fa-comment"></i>
                <span class="comments-count">0</span>
            </button>
        </div>
        <div class="comments-section" id="comments-${solution.id}" style="display: none;">
            <div class="comments-list"></div>
            <form class="comment-form" onsubmit="submitComment(event, ${solution.id})">
                <textarea class="form-control" placeholder="Add a comment..."></textarea>
                <button type="submit" class="btn btn-primary mt-2">Send</button>
            </form>
        </div>
    `;
    return card;
};

const createCommentElement = (comment) => {
    const commentDiv = document.createElement('div');
    commentDiv.className = 'comment';
    commentDiv.id = `comment-${comment.id}`;
    commentDiv.innerHTML = `
        <div class="comment-header">
            <strong>${comment.username}</strong>
            <div class="comment-actions">
                <button class="btn btn-sm btn-edit" onclick="startEditComment(${comment.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-delete" onclick="deleteComment(${comment.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
        <p class="comment-text">${comment.comment}</p>
        <div class="comment-edit-form" style="display: none;">
            <textarea class="form-control">${comment.comment}</textarea>
            <div class="mt-2">
                <button class="btn btn-sm btn-primary" onclick="saveEditComment(${comment.id})">Save</button>
                <button class="btn btn-sm btn-secondary" onclick="cancelEditComment(${comment.id})">Cancel</button>
            </div>
        </div>
    `;
    return commentDiv;
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
        commentsList.appendChild(createCommentElement(data));
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

// Custom select functionality
const initializeCustomSelects = () => {
    const selects = document.querySelectorAll('.filter-select');
    selects.forEach(select => {
        const container = select.closest('.select-container');
        const label = container.querySelector('label');
        const isMultiple = select.hasAttribute('multiple');
        
        // Create custom select wrapper
        const customSelect = document.createElement('div');
        customSelect.className = 'custom-select';
        
        // Get selected items
        const selectedItems = Array.from(select.selectedOptions).map(option => ({
            value: option.value,
            text: option.text
        }));
        
        // Create custom select HTML
        customSelect.innerHTML = `
            <div class="select-selected">
                <div class="selected-items">
                    ${isMultiple ? 
                        selectedItems.map(item => `
                            <span class="selected-tag" data-value="${item.value}">
                                ${item.text}
                                <button type="button" class="remove-tag" onclick="removeTag('${item.value}')">
                                    <i class="fas fa-times"></i>
                                </button>
                            </span>
                        `).join('') :
                        selectedItems.length > 0 ? 
                            `<span class="selected-text">${selectedItems[0].text}</span>` :
                            `<span class="selected-text">${select.options[0].text}</span>`
                    }
                </div>
                <div class="select-arrow"></div>
            </div>
            <div class="select-items select-hide">
                ${Array.from(select.options).map(option => `
                    <div class="select-item ${option.selected ? 'selected' : ''}" data-value="${option.value}">
                        ${option.text}
                    </div>
                `).join('')}
            </div>
        `;
        
        // Replace original select with custom one
        container.appendChild(customSelect);
        select.style.display = 'none';
        
        // Handle click on custom select
        customSelect.querySelector('.select-selected').addEventListener('click', function(e) {
            if (e.target.closest('.remove-tag')) return; // Don't toggle if clicking remove button
            e.stopPropagation();
            const items = this.nextElementSibling;
            items.classList.toggle('select-hide');
            this.classList.toggle('select-arrow-active');
        });
        
        // Handle item selection
        customSelect.querySelectorAll('.select-item').forEach(item => {
            item.addEventListener('click', function(e) {
                const value = this.getAttribute('data-value');
                const text = this.textContent;
                const option = select.querySelector(`option[value="${value}"]`);
                
                if (isMultiple) {
                    // Toggle selection for multiple select
                    option.selected = !option.selected;
                    this.classList.toggle('selected');
                    
                    // Update selected items display
                    const selectedItems = customSelect.querySelector('.selected-items');
                    if (option.selected) {
                        const tag = document.createElement('span');
                        tag.className = 'selected-tag';
                        tag.setAttribute('data-value', value);
                        tag.innerHTML = `
                            ${text}
                            <button type="button" class="remove-tag" onclick="removeTag('${value}')">
                                <i class="fas fa-times"></i>
                            </button>
                        `;
                        selectedItems.appendChild(tag);
                    } else {
                        const tag = selectedItems.querySelector(`[data-value="${value}"]`);
                        if (tag) tag.remove();
                    }
                } else {
                    // Single select behavior
                    select.value = value;
                    const selectedItems = customSelect.querySelector('.selected-items');
                    selectedItems.innerHTML = `<span class="selected-text">${text}</span>`;
                    
                    // Update selected state in dropdown
                    customSelect.querySelectorAll('.select-item').forEach(item => {
                        item.classList.remove('selected');
                    });
                    this.classList.add('selected');
                    
                    // Close dropdown
                    customSelect.querySelector('.select-items').classList.add('select-hide');
                    customSelect.querySelector('.select-selected').classList.remove('select-arrow-active');
                }
                
                // Trigger change event
                select.dispatchEvent(new Event('change'));
            });
        });
    });
    
    // Close custom selects when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.custom-select')) {
            document.querySelectorAll('.select-items').forEach(items => {
                items.classList.add('select-hide');
            });
            document.querySelectorAll('.select-selected').forEach(selected => {
                selected.classList.remove('select-arrow-active');
            });
        }
    });
};

const removeTag = (value) => {
    const select = document.querySelector(`.filter-select option[value="${value}"]`).parentElement;
    const option = select.querySelector(`option[value="${value}"]`);
    option.selected = false;
    
    // Update the custom select display
    const customSelect = select.nextElementSibling;
    const selectedItems = customSelect.querySelector('.selected-items');
    const tag = selectedItems.querySelector(`[data-value="${value}"]`);
    if (tag) tag.remove();
    
    // Update selected state in dropdown
    const item = customSelect.querySelector(`.select-item[data-value="${value}"]`);
    if (item) item.classList.remove('selected');
    
    // Trigger change event
    select.dispatchEvent(new Event('change'));
};

// Custom search functionality
const initializeSearch = () => {
    const searchInput = document.getElementById('search_input');
    const searchButton = document.getElementById('search');
    let searchTimeout;
    
    const performSearch = () => {
        const query = searchInput.value.trim();
        if (query) {
            // Add your search logic here
            console.log('Searching for:', query);
        }
    };
    
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(performSearch, 300);
    });
    
    searchButton.addEventListener('click', performSearch);
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });
};

// Initialize all custom functionality
document.addEventListener('DOMContentLoaded', () => {
    initializeCustomSelects();
    initializeSearch();
    
    // Initialize bookmark counts from sessionStorage
    document.querySelectorAll('.bookmark-count').forEach(countElement => {
        const problemId = countElement.dataset.problemId;
        const storedCount = sessionStorage.getItem(`bookmark_count_${problemId}`);
        if (storedCount !== null) {
            countElement.textContent = storedCount;
        }
    });
    
    // Add click handler to problem cards
    document.querySelectorAll('.problem-card').forEach(card => {
        card.addEventListener('click', (e) => {
            // Don't navigate if clicking on interactive elements
            if (e.target.closest('.btn') || 
                e.target.closest('a') || 
                e.target.closest('textarea') || 
                e.target.closest('input') ||
                e.target.closest('.select-items') ||
                e.target.closest('.select-selected')) {
                return;
            }
            
            const problemId = card.dataset.id;
            window.location.href = `/problem/${problemId}`;
        });
    });
});

// Listen for bookmark updates from problem card
document.addEventListener('bookmarkUpdated', (event) => {
    const { problemId, bookmarkCount } = event.detail;
    
    // Store the updated count in sessionStorage
    sessionStorage.setItem(`bookmark_count_${problemId}`, bookmarkCount);
    
    // Find the problem card in solved problems view
    const problemCard = document.querySelector(`.problem-card[data-id="${problemId}"]`);
    if (problemCard) {
        // Update the bookmark count
        const bookmarkCountElement = problemCard.querySelector('.stat-item i.fa-star').nextElementSibling;
        if (bookmarkCountElement) {
            bookmarkCountElement.textContent = bookmarkCount;
            
            // Add a subtle animation
            bookmarkCountElement.style.transform = 'scale(1.2)';
            bookmarkCountElement.style.color = '#6a34c7';
            setTimeout(() => {
                bookmarkCountElement.style.transform = 'scale(1)';
                bookmarkCountElement.style.color = '';
            }, 300);
        }
    }
}); 