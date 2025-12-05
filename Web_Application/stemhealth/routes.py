import json
import os
from flask import jsonify, render_template, url_for, flash, redirect, request
from stemhealth import app, db
from werkzeug.utils import secure_filename
import datetime as dt
from stemhealth.models import Batch, Entry, IndividualHeight
from sqlalchemy import func
from ultralytics import YOLO
import ultralytics
import cv2
from stemhealth import measurement
from stemhealth.util import *
import pandas as pd
from torch.serialization import add_safe_globals
import torch

# Define constants
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_JSON_EXTENSIONS = {'json'} 
REFERENCE_OBJECT = "reference_object.png"
MODEL_PATH = 'model/best.pt'

# Obtain the reference object mask
reference_mask, simplified_reference_mask, simplified_reference_mask_approx = measurement.get_reference_object_mask(os.path.join(app.static_folder, REFERENCE_OBJECT))
# Allowlist YOLO SegmentationModel so torch.load() can unpickle it
add_safe_globals([ultralytics.nn.tasks.SegmentationModel])
add_safe_globals([torch.nn.modules.container.Sequential])

# Upload Page
# Upload page route
@app.route('/upload')
def upload_page():
    batches = Batch.query.all()
    return render_template('upload.html', page_title='Upload', batches=batches)

# Method for checking if a batch name already exists
@app.route('/check_name', methods=['GET'])
def check_name():
    name = request.args.get('name').strip()
    if name:
        # Check if any batch with the given name exists in the database
        existing_batch = Batch.query.filter(func.lower(Batch.name) == name.lower()).first()
        print(name.lower())
        if existing_batch:
            return jsonify({'exists': True})
    return jsonify({'exists': False})

# Post method for uploading data
@app.route('/upload', methods=['POST'])
def upload_data():
    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name').strip()
        species = request.form.get('species').strip()
        env_data_file = request.files.get('environmental_data')
        image_files = request.files.getlist('file')

        # Check if a batch with the given name already exists
        existing_batch = Batch.query.filter(func.lower(Batch.name) == name.lower()).first()
        if existing_batch:
            flash('A batch with this name already exists. Please choose a different name.', 'error')
            return render_template('upload.html', species=species, environmental_data=env_data_file, files=image_files)

        # Validate the uploaded files
        env_data_filename = secure_filename(env_data_file.filename)
        if not env_data_file or not allowed_file(env_data_filename, ALLOWED_JSON_EXTENSIONS): 
            flash("Invalid environmental data file. Please upload a JSON file.")
            return redirect(request.url)
        
        invalid_files = [file for file in image_files if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS)]
        if invalid_files:
            for file in invalid_files:
                file.filename = ''  # Clear the invalid files
            flash('Invalid file type detected. Only PNG, JPG, and JPEG files are allowed.', 'danger')
            return redirect(request.url)
        
        # Create directories for the batch to store the uploaded data
        batch_dir = os.path.join(app.config['UPLOAD_FOLDER'], name.replace(' ', '_'))
        os.makedirs(batch_dir, exist_ok=True)      
        # Create directories for the original and predicted images  
        original_images_dir = os.path.join(batch_dir, 'original_images')
        os.makedirs(original_images_dir, exist_ok=True)
        predicted_images_dir = os.path.join(batch_dir, 'predicted_images')
        os.makedirs(predicted_images_dir, exist_ok=True)
        env_data_filepath = os.path.join(batch_dir, env_data_filename)
        env_data_file.save(env_data_filepath)
        
        # Create a new batch in the database
        batch = Batch(name=name, species=species)
        db.session.add(batch)
        db.session.commit()
        
        # Load the environmental data from the JSON file
        with open(env_data_filepath, 'r') as json_file:
            env_data = json.load(json_file)

        # Sort the environmental data by timestamp (earliest to latest)
        env_data_sorted = sorted(env_data, key=lambda x: dt.datetime.strptime(x['timestamp'], "%d-%m-%Y_%H-%M-%S"))
        
        # Process the uploaded images
        for file in image_files:
            if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                filename = secure_filename(file.filename)
                original_image_filepath = os.path.join(original_images_dir, filename)
                predicted_image_filepath = os.path.join(predicted_images_dir, filename)
                # Read the image
                file.save(original_image_filepath)
                
                # Apply unsharp mask to sharpen the image as a preprocessing step
                sharpened_image = sharpen_image(original_image_filepath)

                # Save the processed image
                cv2.imwrite(original_image_filepath, sharpened_image)
                cv2.imwrite(predicted_image_filepath, sharpened_image)
                
                # Extract the timestamp, temperature, and humidity from the environmental data
                for item in env_data_sorted:
                    if item['filename'] == filename:
                        timestamp = dt.datetime.strptime(item['timestamp'], "%d-%m-%Y_%H-%M-%S")
                        relative_image_path = os.path.relpath(original_image_filepath, app.static_folder)  # Get relative path to static folder
                        temperature = item['temperature']
                        humidity = item['humidity']
                        entry = Entry(original_image_filepath=relative_image_path, 
                                      timestamp=timestamp, 
                                      temperature=temperature, 
                                      humidity=humidity, 
                                      batch_id=batch.id)
                        
                        db.session.add(entry)
                        db.session.commit()
        
        # Flash a success message and redirect to the dashboard 
        flash('Files uploaded successfully.', 'success')
        return redirect(url_for('dashboard'))


# Dashboard Page
# Route for the dashboard (home page)
@app.route('/')
@app.route('/dashboard')
def dashboard():
    batches = Batch.query.all()
    batch_data = []

    # Display the batches in reverse order (latest first)
    for batch in reversed(batches):
        # Get the start and end dates of the batch
        start_date, end_date = get_start_end_dates(batch.entries)

        # Get preview image 
        preview_image = batch.entries[len(batch.entries)//2].original_image_filepath
        print(preview_image)

        # Append the batch data to the list to be displayed
        batch_data.append({
            'id': batch.id,
            'name': batch.name,
            'species': batch.species,
            'preview_image': preview_image,
            'start_date': start_date,
            'end_date': end_date
        })

    # Render the dashboard template based on the presence of batches
    if not batches:
        return render_template('dashboard.html', page_title='Dashboard')
    else:
        return render_template('dashboard.html', page_title='Dashboard', batch_data = batch_data)


# Batch Profile Page
# Route for displaying batch details
@app.route('/batch/<int:batch_id>', methods=['GET'])
def batch_detail(batch_id):
    # Get the batch details from the database based on the batch ID
    batch = Batch.query.filter_by(id=batch_id).first_or_404()    
    entries = batch.entries 
    start_date, end_date = get_start_end_dates(entries)
    num_entries = len(entries)
    # Calculate the average temperature and humidity
    if num_entries > 0:
        avg_temperature = float("{:.2f}".format(sum(entry.temperature for entry in entries) / num_entries))
        avg_humidity = float("{:.2f}".format(sum(entry.humidity for entry in entries) / num_entries))

    # Check if measurements/predictions have been done for the batch
    has_predictions = any(entry.average_height for entry in entries)
    graphs_paths = []
    
    # Check if the CSV data and graphs exist for the batch
    csv_base_path = os.path.join(app.static_folder, 'seedling_data', batch.name.replace(' ', '_'), 'csv_data')
    csv_exists = os.path.exists(os.path.join(csv_base_path, f"{batch.name.replace(' ', '_')}_entries.csv"))

    graphs_folder = os.path.join(app.static_folder, 'seedling_data', batch.name.replace(' ', '_'), 'graphs_folder')
    graphs_exist = os.path.exists(graphs_folder) and os.listdir(graphs_folder)

    # Generate the CSV data and graphs if they do not exist
    if has_predictions:
        if not csv_exists or not graphs_exist:
            if not csv_exists:
                csv_batch_file_path, csv_entries_file_path, _ = save_batch_data_to_csv(batch)
            
            if not graphs_exist:
                batch_data = pd.read_csv(csv_batch_file_path)
                entry_data = pd.read_csv(csv_entries_file_path)
                ensure_graphs_generated(batch_data, entry_data, graphs_folder)
    
    # Determine if the graphs exist again after generation
    graphs_exist = os.path.exists(graphs_folder) and os.listdir(graphs_folder)

    # Get the paths of the graphs to be displayed
    if graphs_exist:
        graphs_paths = [os.path.relpath(os.path.join(graphs_folder, graph), app.static_folder) for graph in os.listdir(graphs_folder)]

    return render_template('batch_profile.html',
                           page_title=batch.name,
                           batch=batch,
                           entries=entries,
                           start_date=start_date,
                           end_date=end_date,
                           num_entries=num_entries,
                           avg_temperature=avg_temperature,
                           avg_humidity=avg_humidity,
                           has_predictions=has_predictions,
                           graphs_paths=graphs_paths)

# Method to perform predictions on a batch
@app.route('/predict', methods=['GET'])
def predict_batch():
    # Get the batch ID from the request
    batch_id = request.args.get('batch_id', type=int)
    # Get the batch details from the database based on the batch ID
    batch = Batch.query.filter_by(id=batch_id).first_or_404()
    entries = batch.entries
    # Get the sponge mask
    sponge_image_path = os.path.join(app.static_folder, entries[0].original_image_filepath)
    _, simplified_sponge_mask, simplified_sponge_mask_approx = measurement.get_sponge_mask(sponge_image_path)
    # Define the model paths and image paths
    model = YOLO(os.path.join(app.static_folder, MODEL_PATH))
    print(model.model.yaml)
    batch_path = os.path.join(app.static_folder, 'seedling_data', batch.name.replace(' ', '_'))
    original_images_path = os.path.join(batch_path, 'original_images')
    predicted_images_path = os.path.join(batch_path, 'predicted_images')
    
    # Perform predictions on the images in the batch
    results = model.predict(original_images_path, show_labels=False, line_width=1, iou=0.65, conf=0.5)    
    
    # Process the predictions and save the individual heights
    for i in range(len(results)):
        result = results[i]
        boxes = result.boxes
        entry = entries[i]
        measurements = []
        # predicted_seedlings = len(boxes) if boxes else 0
        predicted_seedlings = 0

        # Get the filename of the predicted image
        predicted_image_filename = os.path.basename(result.path)
        predicted_image_rel_path = os.path.relpath(os.path.join(predicted_images_path, predicted_image_filename), app.static_folder)
        entry.predicted_image_filepath = predicted_image_rel_path

        # Check if any seedlings were detected
        if boxes:
            original_image = cv2.imread(os.path.join(app.static_folder, entry.original_image_filepath))

            for box in boxes:
                # Get the bounding box coordinates
                xyxy = box.xyxy[0].tolist()
                x1, y1, x2, y2 = map(int, xyxy)
                height = int(y2 - y1)
                width = int(x2 - x1)
                confidence = box.conf[0].item()  # Get the confidence score
                class_id = box.cls[0].item()  # Get the class ID
                class_name = model.names[int(class_id)]  # Get the class name

                # Check if the seedling is within the eligible area and has a height greater than the width
                eligible_area_mask = measurement.find_eligible_seedling_position(simplified_reference_mask, simplified_sponge_mask, simplified_reference_mask_approx, simplified_sponge_mask_approx)
                if measurement.is_within_mask(eligible_area_mask, (x2, y2)) and (height > width):
                    # Calculate the predicted height
                    predicted_height = measurement.process_image(simplified_reference_mask, x1, y1, x2, y2)
                    cv2.rectangle(original_image, (x1, y1), (x2, y2), (248, 4, 8), 1)
                    predicted_seedlings += 1
                    measurements.append(predicted_height)
                    # Save the individual height along with YOLO prediction details
                    individual_height = IndividualHeight(
                        height=predicted_height,
                        label=class_name,
                        confidence=confidence,
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        entry_id=entry.id
                    )
                    db.session.add(individual_height)
            cv2.imwrite(os.path.join(predicted_images_path, predicted_image_filename), original_image)
   
        entry.predicted_seedlings = predicted_seedlings
        # Calculate the average height for the entry
        if measurements:
            average_height = float("{:.2f}".format(sum(measurements) / len(measurements)))
            entry.average_height = average_height
        else: # If no seedlings were detected, set the average height to 0 and predicted seedlings to 0
            entry.average_height = 0.0
            entry.predicted_seedlings = 0
            
    # Commit the individual heights and entry updates
    db.session.commit()
    
    # Calculate and update the optimum duration for the batch
    calculate_optimum_duration(batch)
    db.session.commit()
    
    # Return a success response 
    return jsonify({'success': True})

# Method to obtain the CSV data file path for a batch to be downloaded
@app.route('/download_csv', methods=['GET'])
def download_csv():
    # Get the batch ID from the request and retrieve the batch details based on the ID
    batch_id = request.args.get('batch_id', type=int)
    batch = Batch.query.filter_by(id=batch_id).first_or_404()
    
    # Define the paths for the CSV files
    base_path = os.path.join('seedling_data', batch.name.replace(' ', '_'), 'csv_data')
    csv_batch_file_path = os.path.join(base_path, f"{batch.name.replace(' ', '_')}_batch.csv")
    csv_entries_file_path = os.path.join(base_path, f"{batch.name.replace(' ', '_')}_entry.csv")
    csv_individual_heights_file_path = os.path.join(base_path, f"{batch.name.replace(' ', '_')}_individual_height.csv")
    
    # Return the file paths as a JSON response
    return jsonify({
        'success': True, 
        'csv_batch_file_path': csv_batch_file_path,
        'csv_entries_file_path': csv_entries_file_path,
        'csv_individual_heights_file_path': csv_individual_heights_file_path
    })
