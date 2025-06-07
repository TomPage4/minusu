/*----------------------------------------------
  CONTACT FORM VALIDATION AND SUBMISSION
----------------------------------------------*/
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("contact-form");
    // Exit if not /contact
    if (!form) return;
    const submitBtn = document.getElementById("contact-submit-button");
    const defaultBtnText = submitBtn.textContent;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const fields = ["name", "email", "message"];
        let valid = true;

        // Clear previous errors
        fields.forEach(field => {
            const input = document.getElementById(field);
            const error = document.getElementById(`${field}-error`);
            input.classList.remove("error", "invalid");
            if (error) error.textContent = "";
        });

        const name = document.getElementById("name");
        const email = document.getElementById("email");
        const message = document.getElementById("message");
        const honeypot = document.getElementById("referral_code");

        // Honeypot check for bots
        if (honeypot && honeypot.value.trim() !== "") {
            return; // Bot detected, silently ignore
        }

        // Validate Name
        if (!name.value.trim()) {
            showError(name, "Name is required");
            valid = false;
        } else if (!/^[a-zA-Z\s'-]+$/.test(name.value.trim())) {
            showError(name, "Name must only contain letters and spaces");
            valid = false;
        }

        // Validate Email
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.value.trim()) {
            showError(email, "Email is required");
            valid = false;
        } else if (!emailPattern.test(email.value.trim())) {
            showError(email, "Please enter a valid email address");
            valid = false;
        }

        // Validate Message
        if (!message.value.trim()) {
            showError(message, "Message cannot be empty");
            valid = false;
        } else if (message.value.length > 999) {
            showError(message, "Message is too long");
            valid = false;
        }

        if (!valid) return;

        // Disable submit button & show loading text
        submitBtn.disabled = true;
        submitBtn.textContent = "Sending...";
        submitBtn.classList.add("submitting");

        try {
        const formData = new FormData(form);
        const response = await fetch("/contact", {
            method: "POST",
            body: formData,
        });

        if (response.status === 429) {
            alert("Too many submissions. Please try again later.");
            return;
        }

        const result = await response.json();

        if (result.success) {
            form.reset();
            alert("Thanks for reaching out!");
        } else {
            alert(result.error || "Something went wrong. Please try again later.");
        }
        } catch (error) {
            console.error("Form submission error:", error);
            alert("Failed to submit form.");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = defaultBtnText;
            submitBtn.classList.remove("submitting");
        }
    });

    function showError(input, message) {
        input.classList.add("error", "invalid");
        const error = document.getElementById(`${input.id}-error`);
        if (error) error.textContent = message;
    }
});








/*----------------------------------------------
  BOOKING SYSTEM
----------------------------------------------*/
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("booking-form");
    if (!form) return;

    const submitBtn = document.getElementById("booking-submit-button");
    const defaultBtnText = submitBtn.textContent;

    const dateInput = document.getElementById("date");
    const timeDropdown = document.getElementById("time");
    const fields = ["name", "email", "date", "time"];

    let slotsByDate = {};

    // Load slots and set up listener
    fetch('/booking/slots')
        .then(response => response.json())
        .then(data => {
            slotsByDate = data;
            timeDropdown.disabled = true;

            dateInput.addEventListener('change', () => {
                const selectedDate = dateInput.value;
                timeDropdown.innerHTML = ''; // Clear existing options

                if (slotsByDate[selectedDate] && slotsByDate[selectedDate].length > 0) {
                    timeDropdown.disabled = false;
                    timeDropdown.innerHTML = '<option value="">Select a time...</option>';
                    slotsByDate[selectedDate].forEach(slot => {
                        const option = document.createElement('option');
                        option.value = slot.start;
                        option.textContent = slot.time;
                        timeDropdown.appendChild(option);
                    });
                } else {
                    timeDropdown.disabled = true;
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'No available times for this date';
                    timeDropdown.appendChild(option);
                }
            });
        })
        .catch(err => {
            console.error("Failed to fetch booking slots:", err);
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'Unable to load times';
            timeDropdown.appendChild(option);
            timeDropdown.disabled = true;
        });

    // Handle form submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        let valid = true;

        // Clear previous errors
        fields.forEach(field => {
            const input = document.getElementById(field);
            const error = document.getElementById(`${field}-error`);
            input.classList.remove("error", "invalid");
            if (error) error.textContent = "";
        });

        const name = document.getElementById("name");
        const email = document.getElementById("email");
        const date = document.getElementById("date");
        const time = document.getElementById("time");
        const honeypot = document.getElementById("referral_code");

        // Honeypot check
        if (honeypot && honeypot.value.trim() !== "") return;

        // Validation
        if (!name.value.trim()) {
            showError(name, "Name is required");
            valid = false;
        } else if (!/^[a-zA-Z\s'-]+$/.test(name.value.trim())) {
            showError(name, "Name must only contain letters and spaces");
            valid = false;
        }

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.value.trim()) {
            showError(email, "Email is required");
            valid = false;
        } else if (!emailPattern.test(email.value.trim())) {
            showError(email, "Please enter a valid email address");
            valid = false;
        }

        if (!date.value) {
            showError(date, "Please select a date");
            valid = false;
        }

        if (!time.value || time.disabled) {
            showError(time, "Please select a valid time");
            valid = false;
        }

        if (!valid) return;

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = "Booking...";
        submitBtn.classList.add("submitting");

        try {
            const formData = new FormData(form);
            const response = await fetch("/booking", {
                method: "POST",
                body: formData,
            });

            if (response.status === 429) {
                alert("Too many submissions. Please try again later.");
                return;
            }

            const result = await response.json();

            if (result.success) {
                form.reset();
                timeDropdown.disabled = true;
                alert("Booking confirmed! Check your email for confirmation.");
            } else {
                alert(result.error || "Something went wrong. Please try again later.");
            }
        } catch (error) {
            console.error("Booking submission error:", error);
            alert("Failed to submit booking.");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = defaultBtnText;
            submitBtn.classList.remove("submitting");
        }
    });

    function showError(input, message) {
        input.classList.add("error", "invalid");
        const error = document.getElementById(`${input.id}-error`);
        if (error) error.textContent = message;
    }
});











/*----------------------------------------------
  COOKIES
----------------------------------------------*/
// Load cookie consent and handle Snipcart activation
window.addEventListener("load", function () {
    if (window.cookieconsent) {
        window.cookieconsent.initialise({
        palette: {
            popup: { background: "#000" },
            button: { background: "#f1d600" }
        },
        type: "opt-in",
        content: {
            message: "We use cookies to provide a shopping cart and improve your experience.",
            dismiss: "Accept",
            deny: "Decline",
            link: "Learn more",
            href: "/privacy-policy" // Change to your actual page
        },
        onInitialise: function (status) {
            if (status === cookieconsent.status.allow) {
            enableSnipcart();
            }
        },
        onStatusChange: function (status) {
            if (status === cookieconsent.status.allow) {
            enableSnipcart();
            }
        }
        });
    }
});

function enableSnipcart() {
    const snipcartScript = document.createElement("script");
    snipcartScript.src = "https://cdn.snipcart.com/themes/v3.3.0/default/snipcart.js";
    snipcartScript.async = true;
    document.body.appendChild(snipcartScript);
}

/*----------------------------------------------
  LOGIN FORM VALIDATION
----------------------------------------------*/
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
    // Exit if not on login page
    if (!form) return;
    
    const submitBtn = document.getElementById("login-submit-button");
    const defaultBtnText = submitBtn.textContent;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const fields = ["username", "password"];
        let valid = true;

        // Clear previous errors
        fields.forEach(field => {
            const input = document.getElementById(field);
            const error = document.getElementById(`${field}-error`);
            input.classList.remove("error", "invalid");
            if (error) error.textContent = "";
        });

        const username = document.getElementById("username");
        const password = document.getElementById("password");

        // Validate Username
        if (!username.value.trim()) {
            showError(username, "Username is required");
            valid = false;
        }

        // Validate Password
        if (!password.value.trim()) {
            showError(password, "Password is required");
            valid = false;
        }

        if (!valid) return;

        // Disable submit button & show loading text
        submitBtn.disabled = true;
        submitBtn.textContent = "Logging in...";
        submitBtn.classList.add("submitting");

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
            });

            if (response.status === 429) {
                alert("Too many login attempts. Please try again later.");
                return;
            }

            if (response.ok) {
                window.location.href = response.url; // Redirect to admin dashboard
            } else {
                const result = await response.json();
                if (result.error === "Invalid credentials") {
                    showError(username, "Invalid username or password");
                    showError(password, "Invalid username or password");
                } else {
                    alert(result.error || "Something went wrong. Please try again later.");
                }
            }
        } catch (error) {
            console.error("Login submission error:", error);
            alert("Failed to submit login form.");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = defaultBtnText;
            submitBtn.classList.remove("submitting");
        }
    });

    function showError(input, message) {
        input.classList.add("error", "invalid");
        const error = document.getElementById(`${input.id}-error`);
        if (error) error.textContent = message;
    }
});

/*----------------------------------------------
  CMS FORM HANDLING
----------------------------------------------*/
document.addEventListener('DOMContentLoaded', () => {
    const cmsForm = document.getElementById('cms-form');
    if (!cmsForm) return;

    const submitButton = document.getElementById('cms-submit-button');
    const defaultBtnText = submitButton.textContent;

    // Track deleted and new items
    const deletedItems = new Set();
    const newItems = new Map();

    // Handle "Add Quote" button clicks
    document.querySelectorAll('.cms-add-item-button').forEach(button => {
        button.addEventListener('click', function() {
            const arrayPath = this.dataset.arrayPath;
            const arrayContainer = this.closest('.cms-array-group').querySelector('.cms-array-items');
            const items = arrayContainer.querySelectorAll('.cms-group');
            const newIndex = items.length;

            // Create new quote item
            const newItem = document.createElement('div');
            newItem.className = 'cms-group new';
            newItem.dataset.index = newIndex;
            newItem.dataset.tempId = `new_${Date.now()}`;

            // Add delete button
            const deleteButton = document.createElement('button');
            deleteButton.type = 'button';
            deleteButton.className = 'cms-delete-item-button';
            deleteButton.dataset.arrayPath = arrayPath;
            deleteButton.dataset.index = newIndex;
            deleteButton.textContent = 'Delete';
            newItem.appendChild(deleteButton);

            // Add quote fields with proper structure
            const quoteFields = `
                <div class="cms-field" data-field-path="${arrayPath}[${newIndex}].name">
                    <label class="cms-label">Name</label>
                    <input type="text" 
                           name="${arrayPath}[${newIndex}].name" 
                           value="" 
                           class="cms-text-input"
                           placeholder="Enter name">
                </div>
                <div class="cms-field" data-field-path="${arrayPath}[${newIndex}].quote">
                    <label class="cms-label">Quote</label>
                    <input type="text" 
                           name="${arrayPath}[${newIndex}].quote" 
                           value="" 
                           class="cms-text-input"
                           placeholder="Enter quote">
                </div>
            `;
            newItem.insertAdjacentHTML('beforeend', quoteFields);

            // Add to container
            arrayContainer.appendChild(newItem);

            // Store in newItems map
            newItems.set(newItem.dataset.tempId, {
                path: arrayPath,
                index: newIndex,
                element: newItem
            });

            // Scroll to new item
            newItem.scrollIntoView({ behavior: 'smooth', block: 'center' });

            // Focus the name input
            newItem.querySelector('input[name$="].name"]').focus();
        });
    });

    // Handle delete button clicks
    document.addEventListener('click', function(e) {
        if (e.target.matches('.cms-delete-item-button')) {
            const item = e.target.closest('.cms-group');
            const arrayPath = e.target.dataset.arrayPath;
            const index = parseInt(e.target.dataset.index);
            
            console.log('Delete clicked:', { arrayPath, index, item });

            if (item.dataset.tempId) {
                // Remove new item
                console.log('Removing new item:', item.dataset.tempId);
                newItems.delete(item.dataset.tempId);
                item.remove();
            } else {
                // Mark existing item as deleted
                console.log('Marking item as deleted:', `${arrayPath}[${index}]`);
                item.classList.add('deleted');
                deletedItems.add(`${arrayPath}[${index}]`);
                console.log('Current deletedItems:', Array.from(deletedItems));
            }
        }
    });

    // Handle form submission
    cmsForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        console.log('Form submission - deleted items:', Array.from(deletedItems));

        // Create a FormData object
        const formData = new FormData(this);

        // Add deleted items to form data with a special marker
        deletedItems.forEach(path => {
            console.log('Adding deletion marker for:', path);
            // Add a hidden field to mark this item as deleted
            const deleteField = document.createElement('input');
            deleteField.type = 'hidden';
            deleteField.name = `__deleted__${path}`;
            deleteField.value = '1';
            this.appendChild(deleteField);
            formData.append(deleteField.name, deleteField.value);
        });

        // Log all form data for debugging
        console.log('Form data contents:');
        for (let [key, value] of formData.entries()) {
            console.log(key, ':', value);
        }

        // Disable submit button and show loading state
        submitButton.disabled = true;
        submitButton.textContent = 'Saving...';
        submitButton.classList.add('submitting');

        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Show success message
            alert('Changes saved successfully!');
            
            // Reload the page to show updated content
            window.location.reload();
        } catch (error) {
            console.error('Error saving changes:', error);
            alert('Error saving changes. Please try again.');
        } finally {
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.textContent = defaultBtnText;
            submitButton.classList.remove('submitting');
        }
    });

    // Handle image file inputs
    document.querySelectorAll('.cms-file-input').forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;

            // Validate file type
            const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
            if (!validTypes.includes(file.type)) {
                alert('Please select a valid image file (JPG, PNG, or WebP)');
                this.value = '';
                return;
            }

            // Validate file size (max 5MB)
            const maxSize = 5 * 1024 * 1024; // 5MB in bytes
            if (file.size > maxSize) {
                alert('Image file size must be less than 5MB');
                this.value = '';
                return;
            }

            // Create preview
            const reader = new FileReader();
            const previewContainer = this.closest('.cms-image-field').querySelector('.cms-image-preview');
            const hiddenInput = this.closest('.cms-image-field').querySelector('.cms-image-value');

            reader.onload = function(e) {
                // Create or update preview
                let previewImg = previewContainer.querySelector('img');
                if (!previewImg) {
                    previewImg = document.createElement('img');
                    previewContainer.appendChild(previewImg);
                }
                previewImg.src = e.target.result;
                previewImg.alt = 'Preview';
            };

            reader.readAsDataURL(file);
        });
    });

    // Add validation for text inputs
    document.querySelectorAll('.cms-text-input').forEach(input => {
        input.addEventListener('input', function() {
            // Remove any HTML tags
            this.value = this.value.replace(/<[^>]*>/g, '');
            
            // Trim whitespace
            this.value = this.value.trim();
        });
    });
});

/*----------------------------------------------
  CMS PRODUCTS HANDLING
----------------------------------------------*/
document.addEventListener('DOMContentLoaded', () => {
    // Delete button click with confirm prompt
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.dataset.productId;
            if (confirm('Are you sure you want to delete this product?')) {
                const form = document.getElementById('delete-form');
                form.action = `/admin/products/delete/${id}`;
                form.submit();
            }
        });
    });

    // Show custom category field if "other" is selected
    const categorySelect = document.getElementById('category-select');
    const customCategoryDiv = document.getElementById('custom-category');

    if (categorySelect && customCategoryDiv) {
        categorySelect.addEventListener('change', () => {
            const input = customCategoryDiv.querySelector('input');
            if (categorySelect.value === 'other') {
                customCategoryDiv.style.display = 'block';
                input.name = 'custom_category';
            } else {
                customCategoryDiv.style.display = 'none';
                input.removeAttribute('name');
            }
        });
    }
});

/*----------------------------------------------
  MOBILE MENU HANDLING
----------------------------------------------*/
document.addEventListener('DOMContentLoaded', () => {
    const burgerMenu = document.querySelector('.burger-menu');
    const mobileMenu = document.querySelector('.mobile-menu');
    const menuOverlay = document.querySelector('.menu-overlay');
    const mobileNavLinks = document.querySelectorAll('.mobile-nav a');
    const body = document.body;

    // Toggle menu function
    function toggleMenu() {
        burgerMenu.classList.toggle('active');
        mobileMenu.classList.toggle('active');
        menuOverlay.classList.toggle('active');
        body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
    }

    // Toggle menu on burger click
    burgerMenu.addEventListener('click', toggleMenu);

    // Close menu when clicking overlay
    menuOverlay.addEventListener('click', toggleMenu);

    // Close menu when clicking a link
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (mobileMenu.classList.contains('active')) {
                toggleMenu();
            }
        });
    });

    // Close menu on window resize if open
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && mobileMenu.classList.contains('active')) {
            toggleMenu();
        }
    });
});

// Scroll-triggered animations
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in-up, .fade-in-left, .fade-in-right, .scale-in, .service-card, .carousel-item');
    
    const observerOptions = {
        root: null, // Use viewport as root
        rootMargin: '0px', // No margin
        threshold: 0.15 // Trigger when 15% of the element is visible
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
                // Unobserve after animation is triggered
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all animated elements
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// Initialize scroll animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initScrollAnimations();
    // ... any existing DOMContentLoaded code ...
});
