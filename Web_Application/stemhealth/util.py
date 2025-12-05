import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend to ensure plots are saved
import matplotlib.pyplot as plt
import os
import datetime as dt
from stemhealth import app

# Methods for routes.py
# Check if the file extension is allowed
def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Method to get the start and end dates of the entries
def get_start_end_dates(entries):
    start_date = entries[0].timestamp.strftime('%A, %d-%m-%Y')
    end_date = entries[-1].timestamp.strftime('%A, %d-%m-%Y')
    return start_date, end_date

# Return a sharpened version of the image, using an unsharp mask
def sharpen_image(filename, kernel_size=(5, 5), sigma=1.0, amount=2.5, threshold=0):
    image = cv2.imread(filename)
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened

# Methods for plotting the graphs and saving them with a filename derived from the plot title
def save_plot_with_title(title, save_folder):
    # Construct the filename from the title
    filename = title.replace(' ', '_') + '.png'
    output_path = os.path.join(save_folder, filename)

    # Save the figure with the constructed filename
    plt.savefig(output_path)
    plt.close()

# Method to plot the average height of seedlings over time
def plot_average_height(batch_data, entry_data, graphs_folder):
    title = 'Average Height of Seedlings Over Time'
    
    # Extract the optimum entry ID from batch_data
    optimum_entry_id = batch_data['optimum_entry_id'].values[0]
    
    # Find the optimum height from entry_data based on the optimum_entry_id
    optimum_row = entry_data[entry_data['id'] == optimum_entry_id]
    if not optimum_row.empty:
        optimum_height = optimum_row['average_height'].values[0]
        optimum_timestamp = optimum_row['timestamp'].values[0]
        optimum_label = f'Optimum Height at {optimum_timestamp}'

    # Create a time series plot
    plt.figure(figsize=(14, 8))
    
    # Plot the average height over time
    plt.plot(entry_data['timestamp'], entry_data['average_height'], marker='o', label='Average Height')
    
    # Add a dashed horizontal line for the optimum height if the optimum height is available
    if optimum_height is not None:
        plt.axhline(y=optimum_height, color='green', linestyle='--', label=optimum_label)
        plt.text(entry_data['timestamp'].iloc[-1], optimum_height, f'Optimum Height: {optimum_height:.2f} cm', 
                 color='green', fontsize=12, ha='right', va='bottom')

    plt.xlabel('Timestamp')
    plt.ylabel('Average Height (cm)')
    plt.title(title)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Add a legend to the plot
    plt.legend()
    save_plot_with_title(title, graphs_folder)


# Method to plot the temperature and humidity over time
def plot_temperature_humidity(entry_data, graphs_folder):
    title = 'Temperature and Humidity Over Time'
    # Create a figure and a primary axis
    fig, ax1 = plt.subplots(figsize=(14, 8))

    # Plot Temperature over Time on the primary y-axis
    line1, = ax1.plot(entry_data['timestamp'], entry_data['temperature'], color='red', label='Temperature (°C)')
    ax1.set_xlabel('Timestamp')
    ax1.set_ylabel('Temperature (°C)', color='red')
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.set_title(title)

    # Create a secondary y-axis for Humidity
    ax2 = ax1.twinx()
    line2, = ax2.plot(entry_data['timestamp'], entry_data['humidity'], color='blue', label='Humidity (%)')
    ax2.set_ylabel('Humidity (%)', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    # Rotate x-axis labels
    fig.autofmt_xdate()

    # Add grid and legends
    ax1.grid(True)

    # Combine legends from both axes
    lines = [line1, line2]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left')

    fig.tight_layout()  # Adjust layout to ensure everything fits without overlap
    save_plot_with_title(title, graphs_folder)
    
# Method to plot the temperature and height over time
def plot_temperature_height(batch_data, entry_data, graphs_folder):
    title = 'Temperature and Average Height Over Time'
    # Create a figure and a primary axis
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # Extract the optimum entry ID from batch_data
    optimum_entry_id = batch_data['optimum_entry_id'].values[0]
    
    # Find the optimum height from entry_data based on the optimum_entry_id
    optimum_row = entry_data[entry_data['id'] == optimum_entry_id]
    if not optimum_row.empty:
        optimum_height = optimum_row['average_height'].values[0]
        optimum_timestamp = optimum_row['timestamp'].values[0]
        optimum_label = f'Optimum Height: {optimum_height:.2f} cm at {optimum_timestamp}'
    else:
        optimum_height = None
        optimum_label = 'Optimum Height (Data Not Found)'

    # Plot Temperature over Time on the primary y-axis
    line1, = ax1.plot(entry_data['timestamp'], entry_data['temperature'], color='red', label='Temperature (°C)')
    ax1.set_xlabel('Timestamp')
    ax1.set_ylabel('Temperature (°C)', color='red')
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.set_title(title)

    # Create a secondary y-axis for Height
    ax2 = ax1.twinx()
    line2, = ax2.plot(entry_data['timestamp'], entry_data['average_height'], color='green', label='Average Height (cm)')
    ax2.set_ylabel('Average Height (cm)', color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    # Rotate x-axis labels
    fig.autofmt_xdate()

    # Add grid and legends
    ax1.grid(True)

    # Combine legends from both axes
    lines = [line1, line2]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left')

    # Add a horizontal dashed line for the optimum height if the optimum height is available
    if optimum_height is not None:
        ax2.axhline(y=optimum_height, color='blue', linestyle='--', label=optimum_label)
        ax2.text(entry_data['timestamp'].iloc[-1], optimum_height, f'Optimum Height: {optimum_height:.2f} cm', 
                 color='blue', fontsize=12, ha='right', va='bottom')

    fig.tight_layout()  # Adjust layout to ensure everything fits without overlap
    
    # Save the plot with the title
    save_plot_with_title(title, graphs_folder)

    
# # Method to plot the humidity and height over time
def plot_humidity_height(batch_data, entry_data, graphs_folder):
    title = 'Humidity and Average Height Over Time'
    # Create a figure and a primary axis
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # Extract the optimum entry ID from batch_data
    optimum_entry_id = batch_data['optimum_entry_id'].values[0]
    
    # Find the optimum height from entry_data based on the optimum_entry_id
    optimum_row = entry_data[entry_data['id'] == optimum_entry_id]
    if not optimum_row.empty:
        optimum_height = optimum_row['average_height'].values[0]
        optimum_timestamp = optimum_row['timestamp'].values[0]
        optimum_label = f'Optimum Height: {optimum_height:.2f} cm at {optimum_timestamp}'
    else:
        optimum_height = None
        optimum_label = 'Optimum Height (Data Not Found)'

    # Plot Humidity over Time on the primary y-axis
    line1, = ax1.plot(entry_data['timestamp'], entry_data['humidity'], color='blue', label='Humidity (%)')
    ax1.set_xlabel('Timestamp')
    ax1.set_ylabel('Humidity (%)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.set_title(title)

    # Create a secondary y-axis for Height
    ax2 = ax1.twinx()
    line2, = ax2.plot(entry_data['timestamp'], entry_data['average_height'], color='green', label='Average Height (cm)')
    ax2.set_ylabel('Average Height (cm)', color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    # Rotate x-axis labels
    fig.autofmt_xdate()

    # Add grid and legends
    ax1.grid(True)

    # Combine legends from both axes
    lines = [line1, line2]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left')

    # Add a horizontal dashed line for the optimum height if the optimum height is available
    if optimum_height is not None:
        ax2.axhline(y=optimum_height, color='purple', linestyle='--', label=optimum_label)
        ax2.text(entry_data['timestamp'].iloc[-1], optimum_height, f'Optimum Height: {optimum_height:.2f} cm', 
                 color='purple', fontsize=12, ha='right', va='bottom')

    fig.tight_layout()  # Adjust layout to ensure everything fits without overlap
    
    # Save the plot with the title
    save_plot_with_title(title, graphs_folder)

# Method to ensure the graphs are generated only if they do not already exist
def ensure_graphs_generated(batch_data, entry_data, graphs_folder):
    # Create the graphs folder 
    os.makedirs(graphs_folder, exist_ok=True)
    
    # Check if the graphs folder is empty
    if not os.listdir(graphs_folder):  
        plot_average_height(batch_data, entry_data, graphs_folder)
        plot_temperature_humidity(entry_data, graphs_folder)
        plot_temperature_height(batch_data, entry_data, graphs_folder)
        plot_humidity_height(batch_data, entry_data, graphs_folder)
    else:
        print("Graphs already exist. Skipping generation.")

# Method to save the batch data and its related entries and individual heights to separate CSV files
def save_batch_data_to_csv(batch):
    # Collect Batch data
    batch_data = [{
        'id': batch.id,
        'name': batch.name,
        'species': batch.species,
        'optimum_duration': batch.optimum_duration,
        'optimum_entry_id': batch.optimum_entry_id
    }]
    
    # Collect Entries data
    entries_data = []
    individual_heights_data = []
    
    # Collect data for each Entry and IndividualHeight
    for entry in batch.entries:
        entries_data.append({
            'id': entry.id,
            'original_image_filepath': entry.original_image_filepath,
            'timestamp': dt.datetime.strftime(entry.timestamp, "%d-%m-%Y_%H-%M-%S"),
            'temperature': entry.temperature,
            'humidity': entry.humidity,
            'predicted_image_filepath': entry.predicted_image_filepath,
            'predicted_seedlings': entry.predicted_seedlings,
            'average_height': entry.average_height,
            'batch_id': entry.batch_id
        })
        
        for individual_height in entry.individual_heights:
            ih_dict = individual_height.to_dict()
            ih_dict['entry_id'] = entry.id
            individual_heights_data.append(ih_dict)

    # Create DataFrames
    df_batch = pd.DataFrame(batch_data)
    df_entries = pd.DataFrame(entries_data)
    df_individual_heights = pd.DataFrame(individual_heights_data)

    # Define file names for each CSV file
    base_filename = f"{batch.name.replace(' ', '_')}"
    csv_batch_filename = f"{base_filename}_batch.csv"
    csv_entries_filename = f"{base_filename}_entry.csv"
    csv_individual_heights_filename = f"{base_filename}_individual_height.csv"

    base_path = os.path.join(app.static_folder, 'seedling_data', batch.name.replace(' ', '_'), 'csv_data')
    
    # Ensure the directory exists
    os.makedirs(base_path, exist_ok=True)
    
    # Define file paths for each CSV file
    csv_batch_file_path = os.path.join(base_path, csv_batch_filename)
    csv_entries_file_path = os.path.join(base_path, csv_entries_filename)
    csv_individual_heights_file_path = os.path.join(base_path, csv_individual_heights_filename)

    # Save DataFrames to CSV files
    df_batch.to_csv(csv_batch_file_path)
    df_entries.to_csv(csv_entries_file_path)
    df_individual_heights.to_csv(csv_individual_heights_file_path)

    return csv_batch_file_path, csv_entries_file_path, csv_individual_heights_file_path

# Method to calculate the optimum duration for a batch of seedlings
def calculate_optimum_duration(batch):
    entries = batch.entries
    target_height = 2.0  # cm
    closest_entry = None
    min_diff = float('inf')
    
    # Assuming entries are sorted by timestamp
    first_entry = entries[0]
    
    # Find the entry with the closest average height to the target height
    for entry in entries:
        diff = abs(entry.average_height - target_height)
        if diff < min_diff:
            min_diff = diff
            closest_entry = entry
    
    # Calculate the duration between the first entry and the closest entry
    if closest_entry:
        duration = closest_entry.timestamp - first_entry.timestamp
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        # minutes = (seconds % 3600) // 60
        batch.optimum_duration = f"{days} days, {hours} hours"
        batch.optimum_entry_id = closest_entry.id

