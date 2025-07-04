// Initialize API client
const api = new ApiClient('https://api.example.com', {
  'Authorization': 'Bearer your-token-here'
});

// ================================
// 1. GET REQUEST EXAMPLES
// ================================

// Simple GET - fetch all users
async function getAllUsers() {
  try {
    const users = await api.get('/users');
    console.log('Users:', users);
    return users;
  } catch (error) {
    console.error('Error fetching users:', error.message);
  }
}

// GET with query parameters
async function getUserById(userId) {
  try {
    const user = await api.get(`/users/${userId}`); 
    console.log('User details:', user);
    return user;
  } catch (error) {
    console.error('Error fetching user:', error.message);
  }
}

// GET with custom headers
async function getProtectedData() {
  try {
    const data = await api.get('/protected-data', {
      headers: {
        'X-Custom-Header': 'custom-value'
      }
    });
    return data;
  } catch (error) {
    console.error('Error fetching protected data:', error.message);
  }
}

// ================================
// 2. POST REQUEST EXAMPLES
// ================================

// Simple POST - create user
async function createUser(userData) {
  try {
    const newUser = await api.post('/users', {
      name: userData.name,
      email: userData.email,
      age: userData.age
    });
    console.log('User created successfully:', newUser);
    return newUser;
  } catch (error) {
    console.error('Error creating user:', error.message);
  }
}

// POST with custom options
async function loginUser(credentials) {
  try {
    const loginResponse = await api.post('/auth/login', credentials, {
      timeout: 5000, // 5 second timeout
      retries: 2     // retry twice on failure
    });
    console.log('Login successful:', loginResponse);
    return loginResponse;
  } catch (error) {
    console.error('Login failed:', error.message);
  }
}

// ================================
// 3. FILE UPLOAD EXAMPLES
// ================================

// Simple file upload
async function uploadProfilePicture(file, userId) {
  try {
    const result = await api.uploadFile('/users/profile-picture', file, {
      userId: userId,
      category: 'profile'
    });
    console.log('Profile picture uploaded:', result);
    return result;
  } catch (error) {
    console.error('Upload failed:', error.message);
  }
}

// Multiple file upload with additional data
async function uploadDocuments(files, documentType) {
  try {
    const formData = new FormData();
    
    // Add multiple files
    files.forEach((file, index) => {
      formData.append(`document_${index}`, file);
    });
    
    // Add additional data
    formData.append('type', documentType);
    formData.append('timestamp', new Date().toISOString());
    
    const result = await api.request('/documents/upload', {
      method: 'POST',
      body: formData,
      isFormData: true
    });
    
    console.log('Documents uploaded:', result);
    return result;
  } catch (error) {
    console.error('Document upload failed:', error.message);
  }
}

// ================================
// 4. FORM SUBMISSION EXAMPLES
// ================================

// Submit HTML form data
async function submitContactForm(formElement) {
  try {
    const formData = new FormData(formElement);
    
    const response = await api.request('/contact/submit', {
      method: 'POST',
      body: formData,
      isFormData: true
    });
    
    console.log('Form submitted successfully:', response);
    return response;
  } catch (error) {
    console.error('Form submission failed:', error.message);
  }
}

// Submit form with mixed data types
async function submitUserProfile(profileData, avatarFile) {
  try {
    const formData = new FormData();
    
    // Add text fields
    formData.append('name', profileData.name);
    formData.append('email', profileData.email);
    formData.append('bio', profileData.bio);
    
    // Add file
    if (avatarFile) {
      formData.append('avatar', avatarFile);
    }
    
    // Add JSON data as string
    formData.append('preferences', JSON.stringify(profileData.preferences));
    
    const result = await api.request('/profile/update', {
      method: 'PUT',
      body: formData,
      isFormData: true
    });
    
    console.log('Profile updated:', result);
    return result;
  } catch (error) {
    console.error('Profile update failed:', error.message);
  }
}

// ================================
// 5. PRACTICAL USAGE EXAMPLES
// ================================

// Example: User registration with avatar
async function registerUserWithAvatar(userData, avatarFile) {
  try {
    // First create the user
    const newUser = await api.post('/users/register', {
      name: userData.name,
      email: userData.email,
      password: userData.password
    });
    
    // Then upload avatar if provided
    if (avatarFile) {
      await api.uploadFile('/users/avatar', avatarFile, {
        userId: newUser.id
      });
    }
    
    console.log('User registered successfully with avatar');
    return newUser;
  } catch (error) {
    console.error('Registration failed:', error.message);
  }
}

// Example: Handle file input change
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (file) {
    uploadProfilePicture(file, 'user123');
  }
}

// Example: Handle form submission
function handleFormSubmit(event) {
  event.preventDefault();
  const formElement = event.target;
  submitContactForm(formElement);
}

// ================================
// 6. HTML INTEGRATION EXAMPLES
// ================================

// HTML form that works with the API
const htmlFormExample = `
<!-- Contact Form -->
<form id="contactForm" onsubmit="handleFormSubmit(event)">
  <input type="text" name="name" placeholder="Your Name" required>
  <input type="email" name="email" placeholder="Your Email" required>
  <textarea name="message" placeholder="Your Message" required></textarea>
  <input type="file" name="attachment" accept=".pdf,.doc,.docx">
  <button type="submit">Send Message</button>
</form>

<!-- File Upload -->
<input type="file" id="avatarUpload" onchange="handleFileUpload(event)" accept="image/*">

<!-- Multiple File Upload -->
<input type="file" id="documentUpload" multiple onchange="handleMultipleFileUpload(event)">
`;

// Handle multiple file upload
function handleMultipleFileUpload(event) {
  const files = Array.from(event.target.files);
  if (files.length > 0) {
    uploadDocuments(files, 'user-documents');
  }
}

// ================================
// 7. ERROR HANDLING EXAMPLES
// ================================

// Advanced error handling
async function handleApiCall() {
  try {
    const data = await api.get('/users');
    return data;
  } catch (error) {
    if (error.status === 401) {
      console.log('Unauthorized - redirect to login');
      // Redirect to login page
    } else if (error.status === 403) {
      console.log('Forbidden - show access denied message');
    } else if (error.status >= 500) {
      console.log('Server error - show retry option');
    } else {
      console.log('Other error:', error.message);
    }
  }
}

// Usage with async/await in event handlers
document.addEventListener('DOMContentLoaded', async () => {
  // Load initial data
  await getAllUsers();
  
  // Set up event listeners
  document.getElementById('contactForm')?.addEventListener('submit', handleFormSubmit);
  document.getElementById('avatarUpload')?.addEventListener('change', handleFileUpload);
});