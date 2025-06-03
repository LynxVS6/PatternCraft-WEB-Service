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

    // Initialize EasyMDE for problem description if user is the author
    const problemDescription = document.getElementById('problem-description');

    // Get problem ID from the card
    const problemCard = document.querySelector('.problem-card');
    const problemId = problemCard?.dataset.id;

    // Function to handle description click
    function handleDescriptionClick(event) {
        const problemDescription = event.currentTarget;
        initializeEditor(problemDescription);
    }

    // Function to clean up the editor
    function cleanupEditor(editor, problemDescription) {
        if (editor) {
            editor.cleanup();
            const editorContainer = editor.codemirror.getWrapperElement().parentElement;
            if (editorContainer) {
                editorContainer.remove();
            }
        }
        if (problemDescription) {
            problemDescription.style.display = 'block';
        }
    }

    // Add click handler to problem description
    if (problemDescription && problemId) {
        // Check if user is authorized to edit
        fetch(`/api/problems/${problemId}/description`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'  // Add this to include cookies
        }).then(response => {
            if (response.ok) {
                // If authorized, add hover effect and click handler
                problemDescription.style.cursor = 'pointer';
                problemDescription.addEventListener('mouseenter', () => {
                    problemDescription.style.backgroundColor = 'rgba(106, 52, 199, 0.05)';
                });
                problemDescription.addEventListener('mouseleave', () => {
                    problemDescription.style.backgroundColor = '';
                });
                problemDescription.addEventListener('click', handleDescriptionClick);
            } else if (response.status === 403) {
                // If not authorized, remove hover effect and click handler
                problemDescription.style.cursor = 'default';
                problemDescription.removeEventListener('click', handleDescriptionClick);
                console.log('User is not authorized to edit this description');
            } else {
                console.error('Unexpected response:', response.status);
            }
        }).catch(error => {
            console.error('Error checking authorization:', error);
            // If error, assume not authorized
            problemDescription.style.cursor = 'default';
            problemDescription.removeEventListener('click', handleDescriptionClick);
        });
    }

    // Function to initialize the editor
    function initializeEditor(problemDescription) {
        // Clean up any existing editors first
        const existingEditors = problemDescription.parentNode.querySelectorAll('.EasyMDEContainer');
        existingEditors.forEach(editor => {
            const easyMDE = editor.EasyMDE;
            if (easyMDE) {
                easyMDE.cleanup();
            }
            editor.remove();
        });

        // Clean up any hidden textareas
        const hiddenTextareas = problemDescription.parentNode.querySelectorAll('textarea[style*="display: none"]');
        hiddenTextareas.forEach(textarea => textarea.remove());

        let editor = null;
        // Get the original markdown content from the data attribute
        const originalContent = problemDescription.dataset.markdown;

        // Create a hidden textarea for EasyMDE
        const textarea = document.createElement('textarea');
        textarea.style.display = 'none';
        textarea.value = originalContent;
        problemDescription.parentNode.insertBefore(textarea, problemDescription);

        try {
            // Initialize EasyMDE
            editor = new EasyMDE({
                element: textarea,
                spellChecker: false,
                status: false,
                toolbar: [
                    'bold', 'italic', 'heading', '|',
                    'quote', 'unordered-list', 'ordered-list', '|',
                    'link', 'image', 'code', '|',
                    'preview', 'side-by-side', 'fullscreen', '|',
                    {
                        name: "save",
                        action: async function(editor) {
                            console.log('Save button clicked');
                            const newContent = editor.value();
                            console.log('New content:', newContent);
                            console.log('Original content:', originalContent);
                            if (newContent !== originalContent) {
                                await saveChanges(editor, newContent, originalContent, problemDescription);
                            }
                            // Always close the editor after clicking save
                            cleanupEditor(editor, problemDescription);
                        },
                        className: "fa fa-save",
                        title: "Save Changes",
                    },
                    'guide'
                ],
                theme: 'easymde',
                autofocus: false,
                hideIcons: ['side-by-side'],
                showIcons: ['code', 'table'],
                placeholder: 'Write your problem description here...',
                maxHeight: '500px',
                minHeight: '200px',
                autoDownloadFontAwesome: true,
                previewRender: (text) => {
                    return marked.parse(text);
                }
            });

            // Show editor
            problemDescription.style.display = 'none';
            editor.codemirror.getWrapperElement().style.display = 'block';
            editor.codemirror.refresh();
            editor.codemirror.focus();

            // Handle editor blur
            editor.codemirror.on('blur', async (cm, event) => {
                // Don't hide if clicking on toolbar
                if (event.relatedTarget && event.relatedTarget.closest('.editor-toolbar')) {
                    return;
                }

                const newContent = editor.value();
                if (newContent !== originalContent) {
                    await saveChanges(editor, newContent, originalContent, problemDescription);
                }
            });
        } catch (error) {
            console.error('Error initializing EasyMDE:', error);
        }
    }

    // Function to save changes
    async function saveChanges(editor, newContent, originalContent, problemDescription) {
        try {
            console.log('Saving changes to server');
            const response = await fetch(`/api/problems/${problemId}/description`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ description: newContent })
            });

            if (!response.ok) {
                if (response.status === 403) {
                    // If user is not authorized, remove hover effect and click handler
                    problemDescription.style.cursor = 'default';
                    problemDescription.removeEventListener('click', handleDescriptionClick);
                    throw new Error('You are not authorized to edit this description');
                }
                throw new Error('Failed to update description');
            }

            // Update the rendered content with parsed markdown
            problemDescription.innerHTML = marked.parse(newContent);
            // Store the markdown content in the data attribute
            problemDescription.dataset.markdown = newContent;
            // Re-initialize Prism for code highlighting
            Prism.highlightAll();
            originalContent = newContent;
        } catch (error) {
            console.error('Error updating description:', error);
            alert(error.message || 'Failed to update description. Please try again.');
            // Restore original content
            editor.value(originalContent);
        }
    }

    if (problemId) {
        // Restore bookmark state
        const bookmarkBtn = document.querySelector(`.btn-bookmark[data-problem-id="${problemId}"]`);
        if (bookmarkBtn) {
            const icon = bookmarkBtn.querySelector('i');
            const isBookmarked = icon.classList.contains('fas');
            bookmarkBtn.classList.toggle('active', isBookmarked);
        }

        // Restore bookmark count
        const bookmarkCount = sessionStorage.getItem(`bookmark_count_${problemId}`);
        if (bookmarkCount !== null) {
            const bookmarkCountElement = document.querySelector(`.bookmark-count[data-problem-id="${problemId}"]`);
            if (bookmarkCountElement) {
                bookmarkCountElement.textContent = bookmarkCount;
            }
        }

        // Restore vote state
        const storedVoteType = sessionStorage.getItem(`vote_${problemId}`);
        const satisfactionPercent = sessionStorage.getItem(`satisfaction_${problemId}`);
        const totalVotes = sessionStorage.getItem(`total_votes_${problemId}`);

        if (storedVoteType) {
            const voteButtons = document.querySelectorAll(`.btn-vote-problem[data-problem-id="${problemId}"]`);
            voteButtons.forEach(button => {
                const icon = button.querySelector('i');
                if (button.dataset.voteType === storedVoteType) {
                    button.classList.add('active');
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                } else {
                    button.classList.remove('active');
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                }
            });
        }

        if (satisfactionPercent !== null && totalVotes !== null) {
            const statItem = document.querySelector('.stat-item:nth-child(2)');
            if (statItem) {
                const voteText = statItem.querySelector('span');
                if (voteText) {
                    voteText.textContent = `${satisfactionPercent}% ${ _('stats.votes') } ${totalVotes}`;
                }
            }
        }
    }

    // Initialize bookmark buttons
    const bookmarkButtons = document.querySelectorAll('.btn-bookmark');
    bookmarkButtons.forEach(button => {
        const problemId = button.dataset.problemId;
        if (problemId) {
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
});

// Add page show event listener to handle back/forward navigation
window.addEventListener('pageshow', (event) => {
    // Check if the page is being shown from the back/forward cache
    if (event.persisted) {
        const problemCard = document.querySelector('.problem-card');
        const problemId = problemCard?.dataset.id;

        if (problemId) {
            // Restore bookmark state
            const bookmarkBtn = document.querySelector(`.btn-bookmark[data-problem-id="${problemId}"]`);
            if (bookmarkBtn) {
                const icon = bookmarkBtn.querySelector('i');
                const isBookmarked = icon.classList.contains('fas');
                bookmarkBtn.classList.toggle('active', isBookmarked);
            }

            // Restore bookmark count
            const bookmarkCount = sessionStorage.getItem(`bookmark_count_${problemId}`);
            if (bookmarkCount !== null) {
                const bookmarkCountElement = document.querySelector(`.bookmark-count[data-problem-id="${problemId}"]`);
                if (bookmarkCountElement) {
                    bookmarkCountElement.textContent = bookmarkCount;
                }
            }

            // Restore vote state
            const storedVoteType = sessionStorage.getItem(`vote_${problemId}`);
            const satisfactionPercent = sessionStorage.getItem(`satisfaction_${problemId}`);
            const totalVotes = sessionStorage.getItem(`total_votes_${problemId}`);

            if (storedVoteType) {
                const voteButtons = document.querySelectorAll(`.btn-vote-problem[data-problem-id="${problemId}"]`);
                voteButtons.forEach(button => {
                    const icon = button.querySelector('i');
                    if (button.dataset.voteType === storedVoteType) {
                        button.classList.add('active');
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                    } else {
                        button.classList.remove('active');
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                    }
                });
            }

            if (satisfactionPercent !== null && totalVotes !== null) {
                const statItem = document.querySelector('.stat-item:nth-child(2)');
                if (statItem) {
                    const voteText = statItem.querySelector('span');
                    if (voteText) {
                        voteText.textContent = `${satisfactionPercent}% ${ _('stats.votes') } ${totalVotes}`;
                    }
                }
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
const createCommentElement = (data, type, parentId) => {
    console.log('Creating comment element with data:', data);
    console.log('Type:', type);
    console.log('Parent ID:', parentId);
    
    const commentDiv = document.createElement('div');
    commentDiv.className = 'comment';
    commentDiv.id = `${type}-comment-${data.id}`;
    
    const isDiscourse = type === 'discourse';
    const editFunction = isDiscourse ? 'startEditDiscourseComment' : 'startEditComment';
    const deleteFunction = isDiscourse ? 'deleteDiscourseComment' : 'deleteComment';
    const saveFunction = isDiscourse ? 'saveEditDiscourseComment' : 'saveEditComment';
    const cancelFunction = isDiscourse ? 'cancelEditDiscourseComment' : 'cancelEditComment';
    const voteFunction = 'voteComment';
    
    // Get current user ID from the page
    const currentUserId = document.querySelector('meta[name="user-id"]')?.content;
    console.log('Current user ID:', currentUserId);
    console.log('Comment user ID:', data.user_id);
    const isCurrentUser = currentUserId && data.user_id && parseInt(currentUserId) === data.user_id;
    console.log('Is current user:', isCurrentUser);
    
    commentDiv.innerHTML = `
        <div class="comment-header">
            <strong>${data.username}</strong>
            ${isCurrentUser ? `
            <div class="comment-actions">
                <button class="btn btn-sm btn-edit" onclick="${editFunction}(${data.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-delete" onclick="${deleteFunction}(${data.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            ` : ''}
        </div>
        <p class="comment-text">${data.comment}</p>
        <div class="comment-edit-form" style="display: none;">
            <textarea class="form-control">${data.comment}</textarea>
            <div class="mt-2">
                <button class="btn btn-sm btn-primary" onclick="${saveFunction}(${data.id})">Save</button>
                <button class="btn btn-sm btn-secondary" onclick="${cancelFunction}(${data.id})">Cancel</button>
            </div>
        </div>
        <div class="comment-actions">
            <button class="btn btn-sm btn-reply" onclick="mentionUser('${data.username}', '${type}', ${parentId})">
                <i class="fas fa-reply"></i>
                Reply
            </button>
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
    `;
    console.log('Created comment element:', commentDiv);
    return commentDiv;
};

const handleCommentSubmit = async (event, id, type) => {
    console.log('Handling comment submit:', { event, id, type });
    event.preventDefault();
    const form = event.target;
    const textarea = form.querySelector('textarea');
    const comment = textarea.value;
    
    try {
        const endpoint = type === 'discourse' 
            ? `/api/problems/${id}/discourse/comments`
            : `/api/solutions/${id}/comments`;
            
        console.log('Sending request to:', endpoint);
        console.log('Request data:', { comment });
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comment })
        });
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error('Failed to submit comment');
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        const commentsList = form.previousElementSibling;
        console.log('Comments list element:', commentsList);
        
        const newComment = createCommentElement(data, type, id);
        commentsList.appendChild(newComment);
        textarea.value = '';
        
        // Update comment count
        const commentButton = document.querySelector(`.btn-comment[onclick*="${id}"]`);
        if (commentButton) {
            const countSpan = commentButton.querySelector('.comments-count');
            countSpan.textContent = parseInt(countSpan.textContent) + 1;
        }
    } catch (error) {
        console.error(`Error submitting ${type} comment:`, error);
        console.error('Error stack:', error.stack);
        alert('Failed to submit comment. Please try again.');
    }
};

// Update existing functions to use shared functionality
const submitComment = (event, solutionId) => handleCommentSubmit(event, solutionId, 'solution');
const submitDiscourseComment = (event, problemId) => handleCommentSubmit(event, problemId, 'discourse');

// Shared edit/delete functionality
const handleEdit = (commentId, type) => {
    const commentDiv = document.getElementById(`${type}-comment-${commentId}`);
    if (!commentDiv) {
        console.error(`Comment element not found: ${type}-comment-${commentId}`);
        return;
    }

    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    
    if (!commentText || !editForm) {
        console.error('Required elements not found in comment');
        return;
    }

    const textarea = editForm.querySelector('textarea');
    if (!textarea) {
        console.error('Textarea not found in edit form');
        return;
    }
    
    commentText.style.display = 'none';
    editForm.style.display = 'block';
    textarea.value = commentText.textContent;
    textarea.focus();
};

const handleCancelEdit = (commentId, type) => {
    const commentDiv = document.getElementById(`${type}-comment-${commentId}`);
    if (!commentDiv) {
        console.error(`Comment element not found: ${type}-comment-${commentId}`);
        return;
    }

    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    
    if (!commentText || !editForm) {
        console.error('Required elements not found in comment');
        return;
    }
    
    commentText.style.display = 'block';
    editForm.style.display = 'none';
};

const handleSaveEdit = async (commentId, type) => {
    const commentDiv = document.getElementById(`${type}-comment-${commentId}`);
    if (!commentDiv) {
        console.error(`Comment element not found: ${type}-comment-${commentId}`);
        return;
    }

    const commentText = commentDiv.querySelector('.comment-text');
    const editForm = commentDiv.querySelector('.comment-edit-form');
    const textarea = editForm?.querySelector('textarea');
    
    if (!commentText || !editForm || !textarea) {
        console.error('Required elements not found in comment');
        return;
    }
    
    try {
        const isDiscourse = type === 'discourse';
        const endpoint = isDiscourse 
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
        const isDiscourse = type === 'discourse';
        const endpoint = isDiscourse 
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
        if (commentDiv) {
            // Update the comment count
            const solutionCard = commentDiv.closest('.solution-card');
            if (solutionCard) {
                const commentButton = solutionCard.querySelector('.btn-comment');
                if (commentButton) {
                    const solutionId = commentButton.getAttribute('onclick')?.match(/\d+/)?.[0];
                    if (solutionId) {
                        document.querySelectorAll(`.btn-comment[onclick*="${solutionId}"]`).forEach(button => {
                            const countSpan = button.querySelector('.comments-count');
                            if (countSpan) {
                                const currentCount = parseInt(countSpan.textContent);
                                if (!isNaN(currentCount)) {
                                    countSpan.textContent = currentCount - 1;
                                }
                            }
                        });
                    }
                }
            }
            commentDiv.remove();
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

// Updated mention function to handle both solution and discourse comments
const mentionUser = (username, type, id) => {
    if (!type || !id) {
        console.error('Missing required parameters:', { type, id });
        return;
    }

    const textarea = document.getElementById(`${type}-${id}-comment-textarea`);
    if (!textarea) {
        console.error(`Textarea not found for target: ${type}-${id}`);
        return;
    }
    
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

// Unified voting functionality
async function voteComment(commentId, voteType) {
    console.log("Voting on comment:", { commentId, voteType });
    
    // First determine if this is a discourse comment by checking the comment div
    const discourseCommentDiv = document.getElementById(`discourse-comment-${commentId}`);
    const solutionCommentDiv = document.getElementById(`solution-comment-${commentId}`);
    
    const commentDiv = discourseCommentDiv || solutionCommentDiv;
    if (!commentDiv) {
        console.error("Comment div not found");
        return;
    }

    const isDiscourseComment = !!discourseCommentDiv;
    console.log("Is discourse comment:", isDiscourseComment);

    const endpoint = isDiscourseComment
        ? `/api/problems/discourse/comments/${commentId}/vote`
        : `/api/comments/${commentId}/vote`;

    console.log("Sending request to:", endpoint);
    console.log("Request data:", { vote_type: voteType });

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ vote_type: voteType }),
        });

        console.log("Response status:", response.status);
        console.log("Response ok:", response.ok);

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Error response:", errorText);
            throw new Error("Failed to vote on comment");
        }

        const data = await response.json();
        console.log("Response data:", data);

        const voteCountElement = commentDiv.querySelector(".vote-count");
        if (voteCountElement) {
            console.log("Found vote count element:", voteCountElement);
            voteCountElement.textContent = data.vote_count;
            voteCountElement.style.transform = "scale(1.2)";
            voteCountElement.style.color = voteType === "up" ? "#4CAF50" : "#f44336";
            setTimeout(() => {
                voteCountElement.style.transform = "scale(1)";
            }, 200);
        }
    } catch (error) {
        console.error("Error voting on comment:", error);
        console.error("Error stack:", error.stack);
    }
}

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

    const voteButtons = document.querySelectorAll(`.btn-vote-problem[data-problem-id="${problemId}"]`);
    const clickedButton = document.querySelector(`.btn-vote-problem[data-problem-id="${problemId}"][data-vote-type="${voteType}"]`);

    if (!clickedButton || clickedButton.disabled) {
        return;
    }

    // Disable all vote buttons temporarily
    voteButtons.forEach(btn => btn.disabled = true);

    try {
        const response = await fetch(`/api/problems/${problemId}/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({ vote_type: voteType })
        });

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
                voteText.textContent = `${data.satisfaction_percent}% ${_('stats.votes')} ${data.total_votes}`;
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

        // Dispatch custom event for vote updates
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
        alert('Failed to update vote. Please try again.');
        voteButtons.forEach(btn => btn.disabled = false);
    }
}