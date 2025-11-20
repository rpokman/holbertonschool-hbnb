/*
  HBnB Web Client
  Handles authentication, place details, and review functionality
*/

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Get cookie value by name
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

/**
 * Set cookie
 */
function setCookie(name, value, days = 365) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/`;
}

/**
 * Check if user is authenticated
 */
function checkAuthentication() {
    const token = getCookie('token');
    return token;
}

/**
 * Get place ID from URL parameters
 */
function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

// ============================================
// THEME MANAGEMENT
// ============================================

/**
 * Initialize theme system
 */
function initThemeSystem() {
    // Load saved theme or default to red-dark
    const savedTheme = getCookie('theme') || 'red';
    const savedMode = getCookie('mode') || 'dark';
    applyTheme(savedTheme, savedMode);
    
    // Setup theme button
    const themeBtn = document.getElementById('theme-toggle-btn');
    const themeModal = document.getElementById('theme-modal');
    const closeModal = document.querySelector('.close-modal');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    
    if (!themeBtn || !themeModal) return;
    
    // Open modal
    themeBtn.addEventListener('click', () => {
        themeModal.classList.add('active');
        updateThemeSelection();
    });
    
    // Close modal
    closeModal?.addEventListener('click', () => {
        themeModal.classList.remove('active');
    });
    
    // Close on outside click
    themeModal.addEventListener('click', (e) => {
        if (e.target === themeModal) {
            themeModal.classList.remove('active');
        }
    });
    
    // Theme selection
    document.querySelectorAll('.theme-option').forEach(option => {
        option.addEventListener('click', () => {
            const theme = option.dataset.theme;
            const mode = darkModeToggle.checked ? 'dark' : 'light';
            applyTheme(theme, mode);
            updateThemeSelection();
        });
    });
    
    // Dark mode toggle
    darkModeToggle?.addEventListener('change', () => {
        const currentTheme = getCookie('theme') || 'red';
        const mode = darkModeToggle.checked ? 'dark' : 'light';
        applyTheme(currentTheme, mode);
    });
    
    // Set initial toggle state
    darkModeToggle.checked = savedMode === 'dark';
}

/**
 * Apply theme to document
 */
function applyTheme(theme, mode) {
    const themeClass = `${theme}-${mode}`;
    document.documentElement.setAttribute('data-theme', themeClass);
    setCookie('theme', theme);
    setCookie('mode', mode);
    
    // Update logo icon based on theme
    updateLogoIcon(theme);
}

/**
 * Update logo icon based on theme
 */
function updateLogoIcon(theme) {
    const logos = document.querySelectorAll('.logo');
    let iconPath;
    
    // Map theme to icon
    switch(theme) {
        case 'red':
            iconPath = 'images/red_icon.png';
            break;
        case 'forest':
            iconPath = 'images/green_icon.png';
            break;
        case 'ocean':
            iconPath = 'images/blue_icon.png';
            break;
        default:
            iconPath = 'images/icon.png';
    }
    
    // Update all logo images on the page
    logos.forEach(logo => {
        logo.src = iconPath;
    });
}

/**
 * Update theme selection UI
 */
function updateThemeSelection() {
    const currentTheme = getCookie('theme') || 'red';
    document.querySelectorAll('.theme-option').forEach(option => {
        if (option.dataset.theme === currentTheme) {
            option.classList.add('selected');
        } else {
            option.classList.remove('selected');
        }
    });
}

// ============================================
// LOGIN FUNCTIONALITY
// ============================================

/**
 * Toggle password visibility
 */
function togglePassword(show) {
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.type = show ? 'text' : 'password';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            // Get form values
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Call login function
            await loginUser(email, password);
        });
    }
});

/**
 * Login user via API
 */
async function loginUser(email, password) {
    try {
        const response = await fetch('http://localhost:5000/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            // Store token in cookie (expires in 1 hour)
            document.cookie = `token=${data.access_token}; path=/; max-age=3600`;
            // Redirect to main page
            window.location.href = 'index.html';
        } else {
            const errorData = await response.json();
            alert('Login failed: ' + (errorData.error || response.statusText));
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('An error occurred during login. Please try again.');
    }
}

// ============================================
// PLACE DETAILS PAGE
// ============================================

/**
 * Initialize place details page
 */
function initPlaceDetailsPage() {
    // Check user authentication
    const token = checkAuthentication();
    
    // Redirect if not authenticated
    if (!token) {
        alert('Please login to view place details');
        window.location.href = 'index.html';
        return;
    }
    
    // Get place ID from URL
    const placeId = getPlaceIdFromURL();
    
    if (!placeId) {
        alert('No place ID provided');
        window.location.href = 'index.html';
        return;
    }
    
    // Update login button visibility
    updateLoginButton(token);
    
    // Fetch and display place details
    fetchPlaceDetails(token, placeId);
    
    // Setup review form if authenticated
    setupReviewForm(token, placeId);
}

/**
 * Update login button based on authentication status
 */
function updateLoginButton(token) {
    const loginButton = document.querySelector('.login-button');
    if (token && loginButton) {
        loginButton.textContent = 'Logout';
        loginButton.href = '#';
        loginButton.addEventListener('click', (e) => {
            e.preventDefault();
            document.cookie = 'token=; path=/; max-age=0';
            window.location.reload();
        });
    }
}

/**
 * Fetch place details from API
 */
async function fetchPlaceDetails(token, placeId) {
    try {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`http://localhost:5000/api/v1/places/${placeId}`, {
            method: 'GET',
            headers: headers
        });

        if (response.ok) {
            const place = await response.json();
            displayPlaceDetails(place);
        } else {
            console.error('Failed to fetch place details');
            alert('Failed to load place details');
        }
    } catch (error) {
        console.error('Error fetching place details:', error);
        alert('An error occurred while loading place details');
    }
}

/**
 * Get amenity icon
 */
function getAmenityIcon(amenityName) {
    const icons = {
        'wifi': '📶',
        'bath': '🛁',
        'bed': '🛏️',
        'pool': '🏊',
        'swimming pool': '🏊',
        'kitchen': '🍳',
        'parking': '🅿️',
        'air conditioning': '❄️',
        'tv': '📺',
        'gym': '🏋️'
    };
    
    const normalizedName = amenityName.toLowerCase();
    return icons[normalizedName] || '✨';
}

/**
 * Display place details on the page
 */
function displayPlaceDetails(place) {
    // Update title
    const titleElement = document.querySelector('.place-details h1');
    if (titleElement) {
        titleElement.textContent = place.title || place.name || 'Unknown Place';
    }
    
    // Update place info
    const placeInfo = document.querySelector('.place-info');
    if (placeInfo) {
        placeInfo.innerHTML = `
            <p><strong>Host:</strong> ${place.owner?.first_name || 'Unknown'} ${place.owner?.last_name || ''}</p>
            <p><strong>Price:</strong> $<span class="price">${place.price || 0}</span> per night</p>
            <p><strong>Description:</strong> ${place.description || 'No description available.'}</p>
            
            <div class="amenities">
                <h3>Amenities:</h3>
                <ul>
                    ${place.amenities && place.amenities.length > 0 
                        ? place.amenities.map(amenity => {
                            const name = amenity.name || amenity;
                            const icon = getAmenityIcon(name);
                            return `<li>${icon} ${name}</li>`;
                        }).join('') 
                        : '<li>No amenities listed</li>'}
                </ul>
            </div>
        `;
    }
    
    // Display reviews
    displayReviews(place.reviews || []);
}

/**
 * Display reviews on the page
 */
function displayReviews(reviews) {
    const reviewsSection = document.querySelector('.reviews-section');
    
    if (!reviewsSection) return;
    
    // Clear existing reviews (except the title)
    const existingReviews = reviewsSection.querySelectorAll('.review-card');
    existingReviews.forEach(review => review.remove());
    
    if (reviews.length === 0) {
        const noReviews = document.createElement('p');
        noReviews.textContent = 'No reviews yet. Be the first to review!';
        reviewsSection.appendChild(noReviews);
        return;
    }
    
    // Add reviews
    reviews.forEach(review => {
        const reviewCard = document.createElement('div');
        reviewCard.className = 'review-card';
        
        const stars = '⭐'.repeat(review.rating || 0);
        
        reviewCard.innerHTML = `
            <p class="review-comment">"${review.text || review.comment || ''}"</p>
            <p class="review-user"><strong>User:</strong> ${review.user?.first_name || 'Anonymous'} ${review.user?.last_name || ''}</p>
            <p class="review-rating"><strong>Rating:</strong> ${stars} (${review.rating || 0}/5)</p>
        `;
        
        reviewsSection.appendChild(reviewCard);
    });
}

/**
 * Setup review form based on authentication
 */
function setupReviewForm(token, placeId) {
    const addReviewSection = document.querySelector('.add-review');
    const loginMessage = document.querySelector('.login-message');
    const reviewForm = document.getElementById('review-form');
    
    if (!token) {
        // Hide form, show login message
        if (reviewForm) reviewForm.style.display = 'none';
        if (loginMessage) loginMessage.style.display = 'block';
    } else {
        // Show form, hide login message
        if (reviewForm) reviewForm.style.display = 'block';
        if (loginMessage) loginMessage.style.display = 'none';
        
        // Add submit handler
        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            await submitReview(token, placeId);
        });
    }
}

/**
 * Submit review to API
 */
async function submitReview(token, placeId) {
    const reviewText = document.getElementById('review-comment').value;
    const rating = document.getElementById('review-rating').value;
    
    // Validation
    if (!reviewText || !rating) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5000/api/v1/reviews/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                place_id: placeId,
                text: reviewText,  // API uses 'text' not 'comment'
                rating: parseInt(rating)
            })
        });

        if (response.ok) {
            alert('Review submitted successfully!');
            // Clear the form
            document.getElementById('review-comment').value = '';
            document.getElementById('review-rating').value = '';
            // Reload page to show new review
            window.location.reload();
        } else {
            const errorData = await response.json();
            alert('Failed to submit review: ' + (errorData.error || response.statusText));
        }
    } catch (error) {
        console.error('Error submitting review:', error);
        alert('An error occurred while submitting your review');
    }
}

// ============================================
// INDEX PAGE
// ============================================

/**
 * Initialize index page
 */
function initIndexPage() {
    const token = checkAuthentication();
    
    // Update login button based on authentication
    updateLoginButtonOnIndex(token);
    
    // Fetch and display places
    fetchPlaces(token);
    
    // Setup price filter
    setupPriceFilter();
}

/**
 * Setup price filter event listener
 */
function setupPriceFilter() {
    const priceFilter = document.getElementById('price-filter');
    
    if (!priceFilter) return;
    
    // Add event listener for filter changes
    priceFilter.addEventListener('change', (event) => {
        const maxPrice = event.target.value;
        filterPlacesByPrice(maxPrice);
    });
}

/**
 * Filter places by price without reloading the page
 */
function filterPlacesByPrice(maxPrice) {
    const placeCards = document.querySelectorAll('.place-card');
    
    placeCards.forEach(card => {
        const price = parseFloat(card.dataset.price);
        
        if (maxPrice === '' || maxPrice === 'all') {
            // Show all places
            card.style.display = 'block';
        } else {
            // Show only places within the price range
            if (price <= parseFloat(maxPrice)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        }
    });
}

/**
 * Fetch places from API
 */
async function fetchPlaces(token) {
    try {
        // Prepare headers
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Add token to headers if available
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Send GET request to fetch places
        const response = await fetch('http://localhost:5000/api/v1/places/', {
            method: 'GET',
            headers: headers
        });

        if (response.ok) {
            const places = await response.json();
            console.log('Places fetched:', places);
            displayPlaces(places);
        } else {
            console.error('Failed to fetch places:', response.status);
            alert('Failed to load places');
        }
    } catch (error) {
        console.error('Error fetching places:', error);
        alert('An error occurred while loading places');
    }
}

/**
 * Display places on the page
 */
function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    
    if (!placesList) return;
    
    // Clear existing content
    placesList.innerHTML = '';
    
    // Check if there are places
    if (!places || places.length === 0) {
        placesList.innerHTML = '<p>No places available at the moment.</p>';
        return;
    }
    
    // Create a card for each place
    places.forEach(place => {
        const placeCard = document.createElement('div');
        placeCard.className = 'place-card';
        placeCard.dataset.price = place.price || 0; // Store price for filtering
        
        placeCard.innerHTML = `
            <h2>${place.title || place.name || 'Unknown Place'}</h2>
            <p class="place-price">Price: $<span class="price">${place.price || 0}</span> per night</p>
            <button class="details-button" onclick="window.location.href='place.html?id=${place.id}'">View Details</button>
        `;
        
        placesList.appendChild(placeCard);
    });
}

/**
 * Update login button based on authentication status
 */
function updateLoginButtonOnIndex(token) {
    const loginButton = document.querySelector('.login-button');
    
    if (!loginButton) return;
    
    if (token) {
        // User is authenticated - show Logout button
        loginButton.textContent = 'Logout';
        loginButton.href = '#';
        loginButton.addEventListener('click', (e) => {
            e.preventDefault();
            // Remove token cookie
            document.cookie = 'token=; path=/; max-age=0';
            // Reload page
            window.location.reload();
        });
    } else {
        // User is not authenticated - show Login button
        loginButton.textContent = 'Login';
        loginButton.href = 'login.html';
    }
}

// ============================================
// PAGE INITIALIZATION
// ============================================

// Initialize appropriate page functionality
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme system on all pages
    initThemeSystem();
    
    const currentPage = window.location.pathname.split('/').pop();
    
    if (currentPage === 'place.html' || currentPage.includes('place')) {
        initPlaceDetailsPage();
    } else if (currentPage === 'index.html' || currentPage === '' || currentPage === '/') {
        initIndexPage();
    }
});