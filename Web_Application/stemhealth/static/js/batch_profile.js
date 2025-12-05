// Function to switch between the tab panes in the batch profile page
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.batch-tab-button');
    const tabPanes = document.querySelectorAll('.batch-tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            // Add active class to the clicked button and the corresponding pane
            button.classList.add('active');
            document.getElementById(button.dataset.tab).classList.add('active');
        });
    });
});

const spinnerText = document.getElementById('spinner-text');

// Function to perform measurement on a batch
async function measureBatch(batchId) {
    try {
        // Hide the measurement message and show the spinner
        const measurementMessage = document.getElementById('measurement-message');
        const spinnerContainer = document.getElementById('spinner-container');
        const completionContainer = document.getElementById('completion-container');
        const predictButton = document.getElementById('predict-button');
        const spinnerText = document.getElementById('spinner-text');

        // Hide the measurement message and show the spinnner loading effect
        measurementMessage.style.display = 'none';
        spinnerContainer.style.display = 'flex';
        completionContainer.style.display = 'none';
        predictButton.textContent = 'Measuring...';
        predictButton.disabled = true;    

        // Perform the measurement by sending a request to the server
        const response = await axios.get('/predict', { params: { batch_id: batchId } });

        if (response) {

            // Hide the spinner and show the completion message
            if (spinnerContainer) spinnerContainer.style.display = 'none';
            if (completionContainer) completionContainer.style.display = 'flex';

            // Change the button text to "View Results"
            if (predictButton) {
                predictButton.textContent = 'View Results';
                predictButton.disabled = false;
                predictButton.onclick = function() {
                    window.location.href = `/batch/${batchId}`;
                };
            }

        } else {
            console.error('Error:', response.data.error);
            if (spinnerText) spinnerText.textContent = 'Error during measurement.';
        }
    } catch (error) {
        console.error('Error performing measurement:', error);
        if (spinnerText) spinnerText.textContent = 'Error performing measurement.';
    }
}

// Function to show the details modal for each image
function showDetails(originalImagePath, predictedImagePath, temperature, humidity, predictedSeedlings, averageHeight) {
    const modal = document.getElementById('details-modal');

    // Check if averageHeight is None or null and set it to 0 if it is
    if (!averageHeight || averageHeight === 'None') {
        averageHeight = 0;
    }

    if (!predictedSeedlings || predictedSeedlings === 'None') {
        predictedSeedlings = 0;
    }
    
    // Set the image paths and other details in the modal
    document.getElementById('modal-original-image').src = originalImagePath;
    document.getElementById('modal-original-link').href = originalImagePath;
    document.getElementById('modal-predicted-image').src = predictedImagePath;
    document.getElementById('modal-predicted-link').href = predictedImagePath;
    document.getElementById('modal-temperature').textContent = temperature;
    document.getElementById('modal-humidity').textContent = humidity;
    document.getElementById('modal-seedlings').textContent = predictedSeedlings;
    document.getElementById('modal-height').textContent = averageHeight;
    modal.style.display = 'block';
}

// Function to close the details modal
function closeModal() {
    const modal = document.getElementById('details-modal');
    modal.style.display = 'none';
}

// Function to download the CSV files for a batch
function downloadCSV(batchId) {
    // Send a request to the server to retrieve the CSV file paths
    axios.get(`/download_csv?batch_id=${batchId}`)
        .then(response => {
            const data = response.data;
            if (data.success) {
                downloadFile(`/static/${data.csv_batch_file_path}`);
                downloadFile(`/static/${data.csv_entries_file_path}`);
                downloadFile(`/static/${data.csv_individual_heights_file_path}`);
            } else {
                alert('Failed to download CSV files');
            }
        })
        .catch(error => {
            console.error('Error downloading CSV files:', error);
            alert('An error occurred while downloading CSV files');
        });
}

// Function to download a file
function downloadFile(filePath) {
    const link = document.createElement('a');
    link.href = filePath;
    link.download = filePath.split('/').pop();
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
