// Add some interactivity
document.addEventListener('DOMContentLoaded', function() {
    // Load the timetable image
    //loadTimetableImage();
    
    // Modal functionality
    const uploadButton = document.getElementById('uploadButton');
    const uploadModal = document.getElementById('uploadModal');
    const closeModal = document.getElementById('closeModal');
    const cancelButton = document.getElementById('cancelButton');
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileProgress = document.getElementById('fileProgress');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const removeFile = document.getElementById('removeFile');
    const nextButton = document.getElementById('nextButton');

    let selectedFile = null;

    // Open modal
    uploadButton.addEventListener('click', function() {
        uploadModal.classList.add('show');
        document.body.style.overflow = 'hidden';
    });

    // Close modal
    function closeUploadModal() {
        uploadModal.classList.remove('show');
        document.body.style.overflow = '';
        resetUpload();
    }

    closeModal.addEventListener('click', closeUploadModal);
    cancelButton.addEventListener('click', closeUploadModal);

    // Close modal when clicking outside
    uploadModal.addEventListener('click', function(e) {
        if (e.target === uploadModal) {
            closeUploadModal();
        }
    });

    // File upload functionality
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Send file to backend when Next button is clicked
    function sendFile(){
        if (!selectedFile) {
            alert('Please select a file first!');
            return;
        }

        // Disable Next button during upload
        nextButton.disabled = true;
        nextButton.textContent = 'Uploading...';

        // Create FormData and append the file
        const formData = new FormData();
        formData.append("file", selectedFile);

        // Send file to backend
        fetch('http://127.0.0.1:8000/uploadpdf', {
            method: "POST",
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Upload successful:", data);
            alert("File uploaded successfully!");
            closeUploadModal();
        })
        .catch(err => {
            console.error("Upload error:", err);
            alert("Upload failed! Please try again.");
        })
        .finally(() => {
            // Re-enable Next button
            nextButton.disabled = false;
            nextButton.textContent = 'Next';
        });
    }

    // Handle file selection
    function handleFile(file) {
        selectedFile = file;
        
        // Validate file
        const maxSize = 25 * 1024 * 1024; // 25MB
        const allowedTypes = ['application/pdf'];
        
        if (file.size > maxSize) {
            alert('File size exceeds 25MB limit');
            return;
        }
        
        if (!allowedTypes.includes(file.type)) {
            alert('Only PDF files are supported');
            return;
        }

        // Show file progress
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileProgress.classList.remove('hidden');
        nextButton.disabled = false;

        // Simulate upload progress
        simulateProgress();
    }

    // Add event listener to Next button
    nextButton.addEventListener('click', sendFile);

    // Remove file
    removeFile.addEventListener('click', function(e) {
        e.stopPropagation();
        resetUpload();
    });

    // Reset upload state
    function resetUpload() {
        selectedFile = null;
        fileInput.value = '';
        fileProgress.classList.add('hidden');
        progressBar.style.width = '0%';
        progressPercent.textContent = '0%';
        nextButton.disabled = true;
    }

    // Simulate upload progress
    function simulateProgress() {
        let progress = 0;
        const interval = setInterval(function() {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            
            progressBar.style.width = progress + '%';
            progressPercent.textContent = Math.round(progress) + '%';
        }, 200);
    }

    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add click animations
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });

});



/*document.addEventListener("DOMContentLoaded", function () {
const timetableImage = document.getElementById("timetableImage");
console.log("Image element found:", timetableImage); });*/