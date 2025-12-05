// Function to check if the name already exists in the database
async function checkName() {
    const name = document.getElementById('name').value;
    if (name) {
        try {
            // Send a request to the server to check if the name already exists
            const response = await axios.get('/check_name', { params: { name: name } });
            return response.data.exists;
        } catch (error) {
            console.error("There was an error checking the name!", error);
            return false;  // Handle error as necessary
        }
    }
    return false;
}

// Function to validate the form before submission
async function validateForm(event) {
    event.preventDefault();  // Prevent default form submission to handle it manually

    var fileInput = document.getElementById('file');
    var envDataInput = document.getElementById('environmental-data');
    var fileWarning = document.getElementById('file-warning');
    var envDataWarning = document.getElementById('environmental-data-warning');
    var nameWarning = document.getElementById('name-warning');
    var allowedExtensions = ['png', 'jpg', 'jpeg'];
    var invalidFiles = [];
    var invalidEnvData = false;

    // Clear previous warnings
    envDataWarning.style.display = 'none';
    fileWarning.style.display = 'none';
    nameWarning.style.display = 'none';

    // Validate environmental data
    var envFile = envDataInput.files[0];
    if (!envFile) {
        envDataWarning.style.display = 'block';
        envDataWarning.textContent = 'Please upload an environmental data JSON file.';
        return false; // Prevent form submission
    }
    if (envFile.name.split('.').pop().toLowerCase() !== 'json') {
        invalidEnvData = true;
    }

    // Validate image files
    if (fileInput.files.length === 0) {
        fileWarning.style.display = 'block';
        fileWarning.textContent = 'Please attach files before submitting.';
        return false; // Prevent form submission
    }
    for (var i = 0; i < fileInput.files.length; i++) {
        var file = fileInput.files[i];
        var fileExtension = file.name.split('.').pop().toLowerCase();
        if (!allowedExtensions.includes(fileExtension)) {
            invalidFiles.push(file.name);
        }
    }

    // Display warnings and prevent form submission if there are invalid files
    if (invalidEnvData) {
        envDataWarning.style.display = 'block';
        envDataWarning.textContent = 'Please upload a valid JSON file.';
        envDataInput.value = ''; // Clear the environmental data input
        document.getElementById('environmental-data-list').innerHTML = ''; // Clear the environmental data list
        return false; // Prevent form submission
    }

    if (invalidFiles.length > 0) {
        fileWarning.style.display = 'block';
        fileWarning.textContent = 'Invalid file types: ' + invalidFiles.join(', ') + '. Please upload only PNG, JPG, or JPEG files.';
        fileInput.value = ''; // Clear the file input
        document.getElementById('file-list').innerHTML = ''; // Clear the file list
        return false; // Prevent form submission
    }

    // Check if the name already exists
    const nameExists = await checkName();
    if (nameExists) {
        nameWarning.style.display = 'block';
        return false; // Prevent form submission
    } else {
        nameWarning.style.display = 'none';
    }

    envDataWarning.style.display = 'none';
    fileWarning.style.display = 'none';

    const spinnerContainer = document.getElementById('spinner-container');
    spinnerContainer.style.display = 'flex';

    document.getElementById('submit-button').disabled = true;
    // If all validations pass, submit the form programmatically
    document.getElementById('upload-form').submit();
}

// Add thumbnail preview of the uploaded images
document.getElementById('file').addEventListener('change', function() {
    var fileList = document.getElementById('file-list');
    fileList.innerHTML = '';
    for (var i = 0; i < this.files.length; i++) {
        var file = this.files[i];
        var listItem = document.createElement('div');
        listItem.classList.add('file-item');

        var fileName = document.createElement('div');
        fileName.textContent = file.name;
        fileName.classList.add('file-name');

        if (file.type.startsWith('image/')) {
            var thumbnail = document.createElement('img');
            thumbnail.classList.add('thumbnail');
            thumbnail.src = URL.createObjectURL(file);
            listItem.appendChild(thumbnail);
        }

        listItem.appendChild(fileName);
        fileList.appendChild(listItem);
    }

    // Remove the warning message
    var fileWarning = document.getElementById('file-warning');
    fileWarning.style.display = 'none';
});

// Add preview of the uploaded environmental data
document.getElementById('environmental-data').addEventListener('change', function() {
    var envDataList = document.getElementById('environmental-data-list');
    envDataList.innerHTML = '';

    var file = this.files[0];
    if (file) {
        var listItem = document.createElement('div');
        listItem.classList.add('file-item');

        var fileName = document.createElement('div');
        fileName.textContent = file.name;
        fileName.classList.add('file-name');

        listItem.appendChild(fileName);
        envDataList.appendChild(listItem);
        
        // Remove the warning message
        var envDataWarning = document.getElementById('environmental-data-warning');
        envDataWarning.style.display = 'none';
    }
});

// Check if the name already exists when the user types in the input field
document.getElementById('name').addEventListener('input', async () => {
    const nameWarning = document.getElementById('name-warning');
    const nameExists = await checkName();
    if (nameExists) {
        nameWarning.style.display = 'block';
    } else {
        nameWarning.style.display = 'none';
    }
});
