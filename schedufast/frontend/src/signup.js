// signup.js - Replace the existing script in your signup.html

import { supabase, signUp } from './supabase.js';

document.addEventListener('DOMContentLoaded', function() {
    
    // Password toggle functionality
    const togglePassword = document.getElementById('togglePassword');
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const password = document.getElementById('password');
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            
            // Toggle eye icon
            this.innerHTML = type === 'text' 
                ? `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                   </svg>`
                : `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
                   </svg>`;
        });
    }

    // Handle signup form submission with Supabase
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }

    //google sign in button listener
    const googleSignInBtn = document.getElementById('google-signin-btn');
    if (googleSignInBtn) {
        googleSignInBtn.addEventListener('click', handleGoogleSignIn);
    }

    // Auth state change listener
    supabase.auth.onAuthStateChange((event, session) => {
        if (event === 'SIGNED_IN') {
            console.log('User signed in:', session.user);
            showSuccessMessage('Welcome! Redirecting to dashboard...');
            setTimeout(() => {
                window.location.href = '/'; 
            }, 2000);
        }
    });
});

async function handleSignup(e) {
    e.preventDefault();
    
    // Get form elements
    const submitButton = e.target.querySelector('button[type="submit"]');
    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const termsAccepted = document.getElementById('terms').checked;
    
    // Validation
    if (!validateForm(fullName, email, password, confirmPassword, termsAccepted)) {
        return;
    }
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.textContent = 'Creating Account...';
    
    try {
        // Sign up user with Supabase - include user metadata
        const { data, error } = await supabase.auth.signUp({
            email: email,
            password: password,
            options: {
                data: {
                    full_name: fullName
                }
            }
        });
        
        if (error) {
            throw error;
        }
        
        if (data.user) {
            // Check if email confirmation is required
            if (!data.session) {
                showSuccessMessage('Please check your email to confirm your account before signing in!');
                // Optionally redirect to a "check email" page
                setTimeout(() => {
                    window.location.href = '/check-email';
                }, 3000);
            } else {
                // User is immediately signed in
                showSuccessMessage('Account created successfully! Welcome to ScheduFast!');
                // Auth state change listener will handle redirect
            }
        }
        
    } catch (error) {
        console.error('Signup error:', error);
        showErrorMessage(getErrorMessage(error.message));
    } finally {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = 'Create Account';
    }
}

function validateForm(fullName, email, password, confirmPassword, termsAccepted) {
    // Check if all fields are filled
    if (!fullName || !email || !password || !confirmPassword) {
        showErrorMessage('Please fill in all fields');
        return false;
    }
    

    if (fullName.length < 2) {
        showErrorMessage('Full name must be at least 2 characters long');
        return false;
    }
    

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showErrorMessage('Please enter a valid email address');
        return false;
    }
    
    if (password.length < 8) {
        showErrorMessage('Password must be at least 8 characters long');
        return false;
    }
    
    if (password !== confirmPassword) {
        showErrorMessage('Passwords do not match');
        return false;
    }
    
    if (!termsAccepted) {
        showErrorMessage('Please accept the Terms of Service and Privacy Policy');
        return false;
    }
    
    return true;
}

async function handleGoogleSignIn() {
    try {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: 'http://localhost:5173/auth/callback',
                scopes: 'https://www.googleapis.com/auth/calendar'
            }
        });

        if (error) {
            throw error;
        }

    } catch (error) {
        console.error('Google Sign-in Error:', error);
        showErrorMessage('Sign in with Google failed. Please try again.');
    }
}

function showSuccessMessage(message) {
    removeExistingAlerts();
    
    const alert = document.createElement('div');
    alert.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 success-alert transform transition-all duration-300 translate-x-0';
    alert.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(alert);
    
    // Animate in
    setTimeout(() => alert.classList.add('translate-x-0'), 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.add('translate-x-full');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 300);
        }
    }, 5000);
}

function showErrorMessage(message) {
    removeExistingAlerts();
    
    const alert = document.createElement('div');
    alert.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 error-alert transform transition-all duration-300 translate-x-full';
    alert.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
            </svg>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(alert);
    
    // Animate in
    setTimeout(() => alert.classList.remove('translate-x-full'), 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.add('translate-x-full');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 300);
        }
    }, 5000);
}

function removeExistingAlerts() {
    const existingAlerts = document.querySelectorAll('.success-alert, .error-alert');
    existingAlerts.forEach(alert => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    });
}

function getErrorMessage(error) {
    const errorMap = {
        'User already registered': 'An account with this email already exists. Try signing in instead.',
        'Invalid email': 'Please enter a valid email address',
        'Password should be at least 6 characters': 'Password must be at least 6 characters long',
        'Email not confirmed': 'Please check your email and confirm your account',
        'Invalid login credentials': 'Invalid email or password',
        'Signup requires a valid password': 'Please enter a valid password',
        'Only an email address is required to invite a user.': 'Please enter a valid email address',
        'Unable to validate email address: invalid format': 'Please enter a valid email address'
    };
    
    return errorMap[error] || `Signup failed: ${error}. Please try again.`;
}