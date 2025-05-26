document.addEventListener('DOMContentLoaded', () => {
    Prism.highlightAll();

    // Initialize markdown parsing
    const markdownContent = document.querySelector('.markdown-content');
    if (markdownContent) {
        // Configure marked options
        marked.setOptions({
            breaks: true,  // Convert line breaks to <br>
            gfm: true,     // GitHub Flavored Markdown
            headerIds: true,
            mangle: false,
            sanitize: false
        });

        // Parse markdown content
        const content = markdownContent.innerHTML;
        markdownContent.innerHTML = marked.parse(content);

        // Re-initialize Prism for code highlighting
        Prism.highlightAll();
    }

    // Initialize bookmark buttons
    const bookmarkButtons = document.querySelectorAll('.btn-bookmark');
    bookmarkButtons.forEach(button => {
        const problemId = button.dataset.problemId;
        if (problemId) {
            // Set initial state based on the icon class
            const icon = button.querySelector('i');
            if (icon.classList.contains('fas')) {
                button.classList.add('active');
            }
            button.addEventListener('click', () => toggleBookmark(problemId));
        }
    });

    const navButtons = document.querySelectorAll('.nav-btn');
    const contentSections = document.querySelectorAll('.content-section');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            navButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            button.classList.add('active');

            // Hide all content sections
            contentSections.forEach(section => section.style.display = 'none');
            // Show the selected content section
            const view = button.dataset.view;
            document.getElementById(`${view}-section`).style.display = 'block';
        });
    });

    // Restore vote states
    const voteButtons = document.querySelectorAll('.btn-vote-problem');
    voteButtons.forEach(button => {
        const problemId = button.dataset.problemId;
        const voteType = button.dataset.voteType;
        const storedVoteType = sessionStorage.getItem(`vote_${problemId}`);
        
        if (storedVoteType === voteType) {
            button.classList.add('active');
            const icon = button.querySelector('i');
            icon.classList.remove('far');
            icon.classList.add('fas');
        }
    });

    // Restore satisfaction and total votes
    const statItem = document.querySelector('.stat-item:nth-child(2)');
    if (statItem) {
        const problemId = document.querySelector('.problem-card').dataset.id;
        const storedSatisfaction = sessionStorage.getItem(`satisfaction_${problemId}`);
        const storedTotalVotes = sessionStorage.getItem(`total_votes_${problemId}`);
        
        if (storedSatisfaction && storedTotalVotes) {
            const voteText = statItem.querySelector('span');
            if (voteText) {
                voteText.textContent = `${storedSatisfaction}% votes ${storedTotalVotes}`;
            }
        }
    }
});

// Like functionality
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
            heartIcon.style.color = data.liked ? '#ff4d4d' : '';
        });
    } catch (error) {
        console.error('Error toggling like:', error);
    }
};

// Comments functionality
const showComments = (solutionId) => {
    const commentsDiv = document.getElementById(`comments-${solutionId}`);
    commentsDiv.style.display = commentsDiv.style.display === 'none' ? 'block' : 'none';
};

// Shared comment handling functions
const createCommentElement = (data, type) => {
    const commentDiv = document.createElement('div');
    commentDiv.className = 'comment';
    commentDiv.id = `${type}-comment-${data.id}`;
    
    const isDiscourse = type === 'discourse';
    const editFunction = isDiscourse ? 'startEditDiscourseComment' : 'startEditComment';
    const deleteFunction = isDiscourse ? 'deleteDiscourseComment' : 'deleteComment';
    const voteFunction = isDiscourse ? 'voteComment' : 'voteSolutionComment';
    
    commentDiv.innerHTML = `
        <div class="comment-header">
            <strong>${data.username}</strong>
            <div class="comment-actions">
                <button class="btn btn-sm btn-edit" onclick="${editFunction}(${data.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-delete" onclick="${deleteFunction}(${data.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
        <p class="comment-text">${data.comment}</p>
        <div class="comment-actions">
            ${isDiscourse ? `
                <button class="btn btn-sm btn-reply" onclick="mentionUser('${data.username}')">
                    <i class="fas fa-reply"></i>
                    Reply
                </button>
            ` : ''}
            <div class="vote-buttons">
                <button class="btn btn-sm btn-vote" onclick="${voteFunction}(${data.id}, 'up')">
                    <i class="fas fa-arrow-up"></i>
                </button>
                <span class="vote-count">${data.vote_count || 0}</span>
                <button class="btn btn-sm btn-vote" onclick="${voteFunction}(${data.id}, 'down')">
                    <i class="fas fa-arrow-down"></i>
                </button>
            </div>
        </div>
        <div class="comment-edit-form" style="display: none;">
            <textarea class="form-control">${data.comment}</textarea>
            <div class="mt-2">
                <button class="btn btn-sm btn-primary" onclick="saveEdit${type.charAt(0).toUpperCase() + type.slice(1)}Comment(${data.id})">Save</button>
                <button class="btn btn-sm btn-secondary" onclick="cancelEdit${type.charAt(0).toUpperCase() + type.slice(1)}Comment(${data.id})">Cancel</button>
            </div>
        </div>
    `;
    return commentDiv;
};

const handleCommentSubmit = async (event, id, type) => {
    event.preventDefault();
    const form = event.target;
    const textarea = form.querySelector('textarea');
    const comment = textarea.value;
    
    try {
        const endpoint = type === 'discourse' 
            ? `/api/problems/${id}/discourse/comments`
            : `/api/solutions/${id}/comments`;
            
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comment })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit comment');
        }
        
        const data = await response.json();
        const commentsList = form.previousElementSibling;
        const newComment = createCommentElement(data, type);
        commentsList.appendChild(newComment);
        textarea.value = '';
        
        // Update comment count if needed
        if (type !== 'discourse') {
            document.querySelectorAll(`.btn-comment[onclick*="${id}"]`).forEach(button => {
                const countSpan = button.querySelector('.comments-count');
                countSpan.textContent = parseInt(countSpan.textContent) + 1;
            });
        }
    } catch (error) {
        console.error(`Error submitting ${type} comment:`, error);
        alert('Failed to submit comment. Please try again.');
    }
};

// Update existing functions to use shared functionality
const submitComment = (event, solutionId) => handleCommentSubmit(event, solutionId, 'solution');
const submitDiscourseComment = (event, problemId) => handleCommentSubmit(event, problemId, 'discourse');

// Shared edit/delete functionality
const handleEdit = (commentId, type) => {
    const commentDiv = document.getElementById(`${type}-comment-${commentId}`);
    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    const textarea = editForm.querySelector('textarea');
    
    commentText.style.display = 'none';
    editForm.style.display = 'block';
    textarea.value = commentText.textContent;
    textarea.focus();
};

const handleCancelEdit = (commentId, type) => {
    const commentDiv = document.getElementById(`${type}-comment-${commentId}`);
    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    
    commentText.style.display = 'block';
    editForm.style.display = 'none';
};

const handleSaveEdit = async (commentId, type) => {
    const commentDiv = document.getElementById(`${type}-comment-${commentId}`);
    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    const textarea = editForm.querySelector('textarea');
    
    try {
        const endpoint = type === 'discourse' 
            ? `/api/problems/discourse/comments/${commentId}`
            : `/api/comments/${commentId}`;
            
        const response = await fetch(endpoint, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comment: textarea.value })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update comment');
        }
        
        const data = await response.json();
        commentText.textContent = data.comment;
        commentText.style.display = 'block';
        editForm.style.display = 'none';
    } catch (error) {
        console.error(`Error updating ${type} comment:`, error);
        alert('Failed to update comment. Please try again.');
    }
};

const handleDelete = async (commentId, type) => {
    if (!confirm('Are you sure you want to delete this comment?')) return;
    
    try {
        const endpoint = type === 'discourse' 
            ? `/api/problems/discourse/comments/${commentId}`
            : `/api/comments/${commentId}`;
            
        const response = await fetch(endpoint, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete comment');
        }
        
        const commentDiv = document.getElementById(`${type}-comment-${commentId}`);
        commentDiv.remove();
        
        // Update comment count if needed
        if (type !== 'discourse') {
            const solutionId = commentDiv.closest('.solution-card')
                .querySelector('.btn-comment')
                .getAttribute('onclick')
                .match(/\d+/)[0];
            
            document.querySelectorAll(`.btn-comment[onclick*="${solutionId}"]`).forEach(button => {
                const countSpan = button.querySelector('.comments-count');
                countSpan.textContent = parseInt(countSpan.textContent) - 1;
            });
        }
    } catch (error) {
        console.error(`Error deleting ${type} comment:`, error);
        alert('Failed to delete comment. Please try again.');
    }
};

// Update existing functions to use shared functionality
const startEditComment = (commentId) => handleEdit(commentId, 'solution');
const startEditDiscourseComment = (commentId) => handleEdit(commentId, 'discourse');

const cancelEditComment = (commentId) => handleCancelEdit(commentId, 'solution');
const cancelEditDiscourseComment = (commentId) => handleCancelEdit(commentId, 'discourse');

const saveEditComment = (commentId) => handleSaveEdit(commentId, 'solution');
const saveEditDiscourseComment = (commentId) => handleSaveEdit(commentId, 'discourse');

const deleteComment = (commentId) => handleDelete(commentId, 'solution');
const deleteDiscourseComment = (commentId) => handleDelete(commentId, 'discourse');

// Remove all reply-related functions and add new mention function
const mentionUser = (username) => {
    const textarea = document.getElementById('discourse-comment-textarea');
    const mention = `@${username} `;
    
    // If there's already text, add a newline before the mention
    if (textarea.value) {
        textarea.value += '\n' + mention;
    } else {
        textarea.value = mention;
    }
    
    // Focus the textarea and place cursor after the mention
    textarea.focus();
    textarea.setSelectionRange(mention.length, mention.length);
    
    // Scroll to the comment form
    textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
};

// Shared voting functionality
const handleVote = async (id, voteType, type) => {
    console.log('handleVote called with id:', id, 'voteType:', voteType, 'type:', type); // Test log
    try {
        const endpoint = type === 'discourse' 
            ? `/api/problems/discourse/comments/${id}/vote`
            : `/api/solutions/comments/${id}/vote`;
            
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vote_type: voteType })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit vote');
        }
        
        const data = await response.json();
        const commentDiv = document.getElementById(`${type}-comment-${id}`);
        if (commentDiv) {
            const voteCount = commentDiv.querySelector('.vote-count');
            voteCount.textContent = data.vote_count;
            
            // Add animation
            voteCount.style.transform = 'scale(1.2)';
            voteCount.style.color = voteType === 'up' ? '#4CAF50' : '#f44336';
            setTimeout(() => {
                voteCount.style.transform = 'scale(1)';
                voteCount.style.color = '';
            }, 300);
        }
    } catch (error) {
        console.log('Test message111');
        console.error(`Error voting on ${type} comment:`, error);
        alert('Failed to submit vote. Please try again.');
    }
};

// Update existing vote functions to use shared functionality
const voteComment = (commentId, voteType) => handleVote(commentId, voteType, 'discourse');
const voteSolutionComment = (commentId, voteType) => handleVote(commentId, voteType, 'solution');

// Bookmark functionality
async function toggleBookmark(problemId) {
    console.log('toggleBookmark called with problemId:', problemId);
    
    // Get the button and disable it temporarily
    const bookmarkBtn = document.querySelector(`.btn-bookmark[data-problem-id="${problemId}"]`);
    console.log('Found bookmark button:', bookmarkBtn);
    
    if (bookmarkBtn.disabled) {
        console.log('Button is disabled, returning');
        return; // Prevent multiple rapid clicks
    }
    bookmarkBtn.disabled = true;
    
    try {
        console.log('Sending request to /api/problems/${problemId}/bookmark');
        const response = await fetch(`/api/problems/${problemId}/bookmark`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        });

        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Failed to update bookmark: ${errorText}`);
        }

        const data = await response.json();
        console.log('Response data:', data);
        
        const bookmarkCount = document.querySelector(`.bookmark-count[data-problem-id="${problemId}"]`);
        console.log('Found bookmark count element:', bookmarkCount);
        
        if (bookmarkBtn && bookmarkCount) {
            console.log('Updating UI with data:', {
                bookmarked: data.bookmarked,
                bookmark_count: data.bookmark_count
            });
            
            // Update the button state
            bookmarkBtn.classList.toggle('active', data.bookmarked);
            const icon = bookmarkBtn.querySelector('i');
            console.log('Found icon element:', icon);
            icon.classList.toggle('far', !data.bookmarked);
            icon.classList.toggle('fas', data.bookmarked);
            
            // Update the count
            bookmarkCount.textContent = data.bookmark_count;
            
            // Store the updated count
            sessionStorage.setItem(`bookmark_count_${problemId}`, data.bookmark_count);
            
            // Add animation
            bookmarkBtn.style.transform = 'scale(1.2)';
            setTimeout(() => {
                bookmarkBtn.style.transform = 'scale(1)';
                bookmarkBtn.disabled = false;
            }, 200);

            // Dispatch custom event
            document.dispatchEvent(new CustomEvent('bookmarkUpdated', {
                detail: {
                    problemId: problemId,
                    bookmarkCount: data.bookmark_count,
                    isBookmarked: data.bookmarked
                }
            }));
        } else {
            console.error('Missing required elements:', {
                bookmarkBtn: !!bookmarkBtn,
                bookmarkCount: !!bookmarkCount
            });
        }
    } catch (error) {
        console.error('Error in toggleBookmark:', error);
        console.error('Error stack:', error.stack);
        alert('Failed to update bookmark. Please try again.');
        bookmarkBtn.disabled = false;
    }
}

// Training functionality
async function startTraining(problemId) {
    try {
        // Get the button and disable it temporarily
        const trainBtn = document.querySelector(`.btn-train[data-problem-id="${problemId}"]`);
        if (trainBtn.disabled) {
            return; // Prevent multiple rapid clicks
        }
        trainBtn.disabled = true;

        // TODO: Implement actual training functionality
        // This is a dummy function that will be replaced with actual implementation
        const response = await fetch(`http://localhost:5000/api/training/${problemId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                problem_id: problemId,
                timestamp: new Date().toISOString(),
                // Add any other metadata you want to send
            })
        });

        if (!response.ok) {
            throw new Error('Failed to start training');
        }

        // Show success notification
        alert('Training session started! The training application will open shortly.');
        
        // Add animation
        trainBtn.style.transform = 'scale(1.2)';
        setTimeout(() => {
            trainBtn.style.transform = 'scale(1)';
        }, 200);

    } catch (error) {
        console.error('Error starting training:', error);
        alert('Failed to start training. Please try again.');
    } finally {
        // Re-enable the button after a short delay
        setTimeout(() => {
            const trainBtn = document.querySelector(`.btn-train[data-problem-id="${problemId}"]`);
            if (trainBtn) {
                trainBtn.disabled = false;
            }
        }, 500);
    }
}

// Problem voting functionality
async function voteProblem(problemId, voteType) {
    console.log('voteProblem called with problemId:', problemId, 'voteType:', voteType);
    
    // Get all vote buttons for this problem
    const voteButtons = document.querySelectorAll(`.btn-vote-problem[data-problem-id="${problemId}"]`);
    const clickedButton = document.querySelector(`.btn-vote-problem[data-problem-id="${problemId}"][data-vote-type="${voteType}"]`);
    
    if (!clickedButton) {
        console.error('Vote button not found');
        return;
    }

    // Disable all vote buttons temporarily
    if (clickedButton.disabled) {
        console.log('Button is disabled, returning');
        return;
    }
    voteButtons.forEach(btn => btn.disabled = true);

    try {
        // Optimistically update UI
        voteButtons.forEach(btn => {
            const icon = btn.querySelector('i');
            const btnVoteType = btn.dataset.voteType;
            
            if (btnVoteType === voteType) {
                if (btn.classList.contains('active')) {
                    // If already active, remove vote
                    btn.classList.remove('active');
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                } else {
                    // If not active, add vote
                    btn.classList.add('active');
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                }
            } else {
                // Remove vote from other buttons
                btn.classList.remove('active');
                icon.classList.remove('fas');
                icon.classList.add('far');
            }
        });

        console.log('Sending request to /api/problems/${problemId}/vote');
        const response = await fetch(`/api/problems/${problemId}/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({ vote_type: voteType })
        });

        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);

        if (!response.ok) {
            throw new Error('Failed to update vote');
        }

        const data = await response.json();
        console.log('Response data:', data);
        
        // Update UI with server response
        voteButtons.forEach(btn => {
            const icon = btn.querySelector('i');
            const btnVoteType = btn.dataset.voteType;
            
            if (btnVoteType === data.vote_type) {
                btn.classList.add('active');
                icon.classList.remove('far');
                icon.classList.add('fas');
            } else {
                btn.classList.remove('active');
                icon.classList.remove('fas');
                icon.classList.add('far');
            }
        });

        // Update satisfaction percentage and total votes
        const statItem = document.querySelector('.stat-item:nth-child(2)');
        if (statItem) {
            const voteText = statItem.querySelector('span');
            if (voteText) {
                voteText.textContent = `${data.satisfaction_percent}% votes ${data.total_votes}`;
            }
        }

        // Store the updated vote state
        sessionStorage.setItem(`vote_${problemId}`, data.vote_type);
        sessionStorage.setItem(`satisfaction_${problemId}`, data.satisfaction_percent);
        sessionStorage.setItem(`total_votes_${problemId}`, data.total_votes);

        // Add animation
        clickedButton.style.transform = 'scale(1.2)';
        setTimeout(() => {
            clickedButton.style.transform = 'scale(1)';
            voteButtons.forEach(btn => btn.disabled = false);
        }, 200);

        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('voteUpdated', {
            detail: {
                problemId: problemId,
                voteType: data.vote_type,
                satisfactionPercent: data.satisfaction_percent,
                totalVotes: data.total_votes
            }
        }));

    } catch (error) {
        console.error('Error in voteProblem:', error);
        console.error('Error stack:', error.stack);
        
        // Revert optimistic UI update
        voteButtons.forEach(btn => {
            const icon = btn.querySelector('i');
            const btnVoteType = btn.dataset.voteType;
            const storedVoteType = sessionStorage.getItem(`vote_${problemId}`);
            
            if (btnVoteType === storedVoteType) {
                btn.classList.add('active');
                icon.classList.remove('far');
                icon.classList.add('fas');
            } else {
                btn.classList.remove('active');
                icon.classList.remove('fas');
                icon.classList.add('far');
            }
        });

        // Revert satisfaction and total votes
        const statItem = document.querySelector('.stat-item:nth-child(2)');
        if (statItem) {
            const voteText = statItem.querySelector('span');
            if (voteText) {
                const storedSatisfaction = sessionStorage.getItem(`satisfaction_${problemId}`);
                const storedTotalVotes = sessionStorage.getItem(`total_votes_${problemId}`);
                if (storedSatisfaction && storedTotalVotes) {
                    voteText.textContent = `${storedSatisfaction}% votes ${storedTotalVotes}`;
                }
            }
        }
        
        alert('Failed to submit vote. Please try again.');
        voteButtons.forEach(btn => btn.disabled = false);
    }
}