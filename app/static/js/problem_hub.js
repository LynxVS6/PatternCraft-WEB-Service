// Custom select functionality
const initializeCustomSelects = () => {
    const selects = document.querySelectorAll('.filter-select');
    const urlParams = new URLSearchParams(window.location.search);
    
    selects.forEach(select => {
        const container = select.closest('.select-container');
        const label = container.querySelector('label');
        const isMultiple = select.hasAttribute('multiple');
        
        // Create custom select wrapper
        const customSelect = document.createElement('div');
        customSelect.className = 'custom-select';
        
        // Get selected items based on URL parameters
        let selectedItems = [];
        if (isMultiple) {
            const paramName = select.name;
            const values = urlParams.getAll(paramName);
            
            // Update native select options to match URL parameters
            Array.from(select.options).forEach(option => {
                option.selected = values.includes(option.value);
            });
            
            selectedItems = Array.from(select.options)
                .filter(option => option.selected)
                .map(option => ({
                    value: option.value,
                    text: option.text
                }));
        } else {
            const paramName = select.name;
            const value = urlParams.get(paramName);
            const selectedOption = Array.from(select.options).find(option => option.value === value);
            if (selectedOption) {
                selectedOption.selected = true;
                selectedItems = [{
                    value: selectedOption.value,
                    text: selectedOption.text
                }];
            } else if (select.options.length > 0) {
                select.options[0].selected = true;
                selectedItems = [{
                    value: select.options[0].value,
                    text: select.options[0].text
                }];
            }
        }
        
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
                    <div class="select-item ${selectedItems.some(item => item.value === option.value) ? 'selected' : ''}" data-value="${option.value}">
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
    
    // Get all currently selected tags from the custom select UI first
    const customSelect = select.nextElementSibling;
    const selectedItems = customSelect.querySelector('.selected-items');
    const selectedTags = Array.from(selectedItems.querySelectorAll('.selected-tag'))
        .map(tag => tag.getAttribute('data-value'));
    
    // Sync the native select element with the custom UI state
    Array.from(select.options).forEach(opt => {
        opt.selected = selectedTags.includes(opt.value);
    });
    
    // Log state before removal
    console.log('Before removal - Current URL params:', new URLSearchParams(window.location.search).getAll('tags_filter'));
    console.log('Before removal - Currently selected options:', selectedTags);
    
    option.selected = false;
    
    // Update the custom select display
    const tag = selectedItems.querySelector(`[data-value="${value}"]`);
    if (tag) tag.remove();
    
    // Update selected state in dropdown
    const item = customSelect.querySelector(`.select-item[data-value="${value}"]`);
    if (item) item.classList.remove('selected');
    
    // Get updated selected tags after removal
    const updatedSelectedTags = Array.from(selectedItems.querySelectorAll('.selected-tag'))
        .map(tag => tag.getAttribute('data-value'));
    
    // Sync the native select element with the updated custom UI state
    Array.from(select.options).forEach(opt => {
        opt.selected = updatedSelectedTags.includes(opt.value);
    });
    
    // Log state after removal
    console.log('After removal - Selected tags to be added:', updatedSelectedTags);
    console.log('After removal - New URL params:', new URLSearchParams(window.location.search).getAll('tags_filter'));
    
    // If this is the tags filter and no tags are selected, trigger search to show all problems
    if (select.name === 'tags_filter' && updatedSelectedTags.length === 0) {
        performSearch();
    } else {
        // Trigger change event
        select.dispatchEvent(new Event('change'));
    }
};

// Custom search functionality
const performSearch = () => {
    const searchForm = document.getElementById('search_form');
    
    // Sync all custom selects with their native select elements before getting form data
    document.querySelectorAll('.custom-select').forEach(customSelect => {
        const select = customSelect.previousElementSibling;
        if (select.hasAttribute('multiple')) {
            const selectedTags = Array.from(customSelect.querySelectorAll('.selected-tag'))
                .map(tag => tag.getAttribute('data-value'));
            
            // Update native select options
            Array.from(select.options).forEach(option => {
                option.selected = selectedTags.includes(option.value);
            });
        }
    });
    
    const formData = new FormData(searchForm);
    const params = new URLSearchParams();
    
    // Add all form data to params
    for (const [key, value] of formData.entries()) {
        console.log(key, value);
        if (value) {
            if (key === 'tags_filter') {
                // Get all selected tags and remove duplicates using Set
                const selectedTags = new Set();
                formData.getAll(key).forEach(tag => selectedTags.add(tag));
                
                // Only add if not empty
                if (selectedTags.size > 0) {
                    // Clear any existing tags_filter parameters
                    params.delete(key);
                    // Add each unique tag once
                    selectedTags.forEach(tag => params.append(key, tag));
                }
            } else {
                // Only add if not the default "all" value
                if (value !== 'all') {
                    params.append(key, value);
                }
            }
        }
    }
    
    // Update URL with search parameters
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newUrl);
    
    // Reload the page with new parameters
    window.location.reload();
};

const initializeSearch = () => {
    const searchForm = document.getElementById('search_form');
    const searchInput = document.getElementById('search_input');
    const searchButton = document.getElementById('search');
    
    // Handle search button click
    searchButton.addEventListener('click', (e) => {
        e.preventDefault();
        performSearch();
    });
    
    // Handle form submission
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        performSearch();
    });
    
    // Initialize form with URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    searchInput.value = urlParams.get('q') || '';
    
    // Set initial values for selects
    document.querySelectorAll('.filter-select').forEach(select => {
        const paramName = select.name;
        if (paramName === 'tags' || paramName === 'r') {
            // Handle multiple select values
            const values = urlParams.getAll(paramName);
            Array.from(select.options).forEach(option => {
                option.selected = values.includes(option.value);
            });
        } else {
            const value = urlParams.get(paramName);
            if (value) {
                select.value = value;
            }
        }
    });
};

// Initialize all custom functionality
document.addEventListener('DOMContentLoaded', () => {
    initializeCustomSelects();
    initializeSearch();
    
    // Initialize all states from sessionStorage
    document.querySelectorAll('.problem-card').forEach(card => {
        const problemId = card.dataset.id;
        
        // Restore bookmark count
        const bookmarkCount = sessionStorage.getItem(`bookmark_count_${problemId}`);
        if (bookmarkCount !== null) {
            const bookmarkCountElement = card.querySelector(`.bookmark-count[data-problem-id="${problemId}"]`);
            if (bookmarkCountElement) {
                bookmarkCountElement.textContent = bookmarkCount;
            }
        }
        
        // Restore vote state
        const satisfactionPercent = sessionStorage.getItem(`satisfaction_${problemId}`);
        const totalVotes = sessionStorage.getItem(`total_votes_${problemId}`);
        if (satisfactionPercent !== null && totalVotes !== null) {
            const voteElement = card.querySelector('.vote-text');
            if (voteElement) {
                updateVoteText(voteElement, satisfactionPercent, totalVotes);
            }
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

// Add page show event listener to handle back/forward navigation
window.addEventListener('pageshow', (event) => {
    // Check if the page is being shown from the back/forward cache
    if (event.persisted) {
        // Re-initialize all states from sessionStorage
        document.querySelectorAll('.problem-card').forEach(card => {
            const problemId = card.dataset.id;
            
            // Restore bookmark count
            const bookmarkCount = sessionStorage.getItem(`bookmark_count_${problemId}`);
            if (bookmarkCount !== null) {
                const bookmarkCountElement = card.querySelector(`.bookmark-count[data-problem-id="${problemId}"]`);
                if (bookmarkCountElement) {
                    bookmarkCountElement.textContent = bookmarkCount;
                }
            }
            
            // Restore vote state
            const satisfactionPercent = sessionStorage.getItem(`satisfaction_${problemId}`);
            const totalVotes = sessionStorage.getItem(`total_votes_${problemId}`);
            if (satisfactionPercent !== null && totalVotes !== null) {
                const voteElement = card.querySelector('.vote-text');
                if (voteElement) {
                    updateVoteText(voteElement, satisfactionPercent, totalVotes);
                }
            }
        });
    }
});

// Listen for bookmark updates from problem card
document.addEventListener('bookmarkUpdated', (event) => {
    const { problemId, bookmarkCount } = event.detail;
    
    // Store the updated count in sessionStorage
    sessionStorage.setItem(`bookmark_count_${problemId}`, bookmarkCount);
    
    // Find all bookmark count elements for this problem
    document.querySelectorAll(`.bookmark-count[data-problem-id="${problemId}"]`).forEach(countElement => {
        // Update the count
        countElement.textContent = bookmarkCount;
        
        // Add animation
        countElement.style.transform = 'scale(1.2)';
        countElement.style.color = '#6a34c7';
        setTimeout(() => {
            countElement.style.transform = 'scale(1)';
            countElement.style.color = '';
        }, 300);
    });
});

// Listen for vote updates
document.addEventListener('voteUpdated', (event) => {
    const { problemId, satisfactionPercent, totalVotes } = event.detail;
    
    // Store the updated values in sessionStorage
    sessionStorage.setItem(`satisfaction_${problemId}`, satisfactionPercent);
    sessionStorage.setItem(`total_votes_${problemId}`, totalVotes);
    
    // Find all vote count elements for this problem
    document.querySelectorAll(`.problem-card[data-id="${problemId}"] .vote-text`).forEach(voteElement => {
        // Update the vote count using the translation key
        updateVoteText(voteElement, satisfactionPercent, totalVotes);
        
        // Add animation
        voteElement.style.transform = 'scale(1.2)';
        voteElement.style.color = '#6a34c7';
        setTimeout(() => {
            voteElement.style.transform = 'scale(1)';
            voteElement.style.color = '';
        }, 300);
    });
}); 