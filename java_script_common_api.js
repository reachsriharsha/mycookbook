// Generic API utility function
class ApiClient {
  constructor(baseURL = '', defaultHeaders = {}) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...defaultHeaders
    };
  }

  async request(endpoint, options = {}) {
    const {
      method = 'GET',
      headers = {},
      body = null,
      timeout = 10000,
      retries = 0,
      isFormData = false,
      responseType = 'json' // 'json', 'text', 'blob', 'arrayBuffer'
    } = options;

    // Construct URL
    const url = `${this.baseURL}${endpoint}`;

    // Prepare headers
    const finalHeaders = { ...this.defaultHeaders };
    
    // Remove Content-Type for FormData (let browser set it)
    if (isFormData) {
      delete finalHeaders['Content-Type'];
    }
    
    Object.assign(finalHeaders, headers);

    // Prepare request config
    const config = {
      method: method.toUpperCase(),
      headers: finalHeaders,
      signal: AbortSignal.timeout(timeout)
    };

    // Add body for non-GET requests
    if (body !== null && method.toUpperCase() !== 'GET') {
      if (isFormData) {
        config.body = body; // FormData object
      } else if (typeof body === 'object') {
        config.body = JSON.stringify(body);
      } else {
        config.body = body;
      }
    }

    // Retry logic
    let lastError;
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, config);
        
        // Handle HTTP errors
        if (!response.ok) {
          const errorData = await this.parseErrorResponse(response);
          throw new ApiError(
            `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            errorData,
            url
          );
        }

        // Parse response based on type
        return await this.parseResponse(response, responseType);

      } catch (error) {
        lastError = error;
        
        // Don't retry on client errors (4xx) or AbortError
        if (error.status >= 400 && error.status < 500 || error.name === 'AbortError') {
          break;
        }
        
        // Wait before retry (exponential backoff)
        if (attempt < retries) {
          await this.delay(Math.pow(2, attempt) * 1000);
        }
      }
    }

    throw lastError;
  }

  // Helper method to parse response
  async parseResponse(response, responseType) {
    switch (responseType) {
      case 'json':
        return await response.json();
      case 'text':
        return await response.text();
      case 'blob':
        return await response.blob();
      case 'arrayBuffer':
        return await response.arrayBuffer();
      default:
        return await response.json();
    }
  }

  // Helper method to parse error response
  async parseErrorResponse(response) {
    try {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      return await response.text();
    } catch {
      return null;
    }
  }

  // Helper method for delay
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Convenience methods
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  async post(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'POST', body });
  }

  async put(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'PUT', body });
  }

  async patch(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'PATCH', body });
  }

  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }

  // File upload helper
  async uploadFile(endpoint, file, additionalData = {}, options = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add additional form data
    Object.keys(additionalData).forEach(key => {
      formData.append(key, additionalData[key]);
    });

    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: formData,
      isFormData: true
    });
  }
}

// Custom error class
class ApiError extends Error {
  constructor(message, status, data, url) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    this.url = url;
  }
}

// Usage examples:

// 1. Initialize the API client
const api = new ApiClient('https://api.example.com', {
  'Authorization': 'Bearer your-token-here'
});

// 2. Simple GET request
async function getUsers() {
  try {
    const users = await api.get('/users');
    console.log(users);
    return users;
  } catch (error) {
    console.error('Failed to fetch users:', error.message);
    throw error;
  }
}

// 3. POST request with JSON data
async function createUser(userData) {
  try {
    const newUser = await api.post('/users', userData);
    console.log('User created:', newUser);
    return newUser;
  } catch (error) {
    console.error('Failed to create user:', error.message);
    throw error;
  }
}

// 4. File upload
async function uploadAvatar(file, userId) {
  try {
    const result = await api.uploadFile('/users/avatar', file, { userId });
    console.log('Avatar uploaded:', result);
    return result;
  } catch (error) {
    console.error('Failed to upload avatar:', error.message);
    throw error;
  }
}

// 5. Request with custom options
async function getReportsWithRetry() {
  try {
    const reports = await api.get('/reports', {
      timeout: 30000,
      retries: 3,
      responseType: 'json'
    });
    return reports;
  } catch (error) {
    console.error('Failed to fetch reports:', error.message);
    throw error;
  }
}

// 6. Form data submission
async function submitForm(formElement) {
  try {
    const formData = new FormData(formElement);
    const response = await api.request('/submit-form', {
      method: 'POST',
      body: formData,
      isFormData: true
    });
    return response;
  } catch (error) {
    console.error('Form submission failed:', error.message);
    throw error;
  }
}

// Export for use in modules
// export { ApiClient, ApiError };