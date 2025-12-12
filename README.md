# StemHealth: Plant Stem Elongation Monitoring and Analysis System (Final Year Project)
This is an end-to-end computer vision system developed in collaboration with Sunway XFarms that automates seedling stem elongation measurement to determine optimal germination condition. 

## Problem Statement
Within the indoor vertical farm industry, advanced agricultural techniques such as hydroponics are employed to optimize plant growth and yield. A critical initial step in these methods involves placing the trays of sowed seeds in a dark environment for the first few days 
to promote germination. During this phase, monitoring and analysing the plant, specifically the 
seedling stem elongation becomes essential for ensuring healthy plant development. However, 
existing monitoring methods rely heavily on manual measurements using measuring tools 
which are prone to errors, time-consuming, and labour-intensive.

## Methodology
- A custom enclosure equipped with a strategically placed 
camera, an Arduino-controlled automated lighting system, and image acquisition scripts was 
designed and implemented to capture images of seedlings autonomously.
- Through data 
collection of the seedling images and its environmental data, a custom dataset was curated and 
manually annotated. Utilizing state-of-the-art instance segmentation models, specifically 
YOLOv8, a custom seedling detection model was trained to detect seedlings within an image 
that demonstrated above-average performance with precision, recall, and mAP50 scores of 
0.615, 0.63, and 0.644 respectively.
-  Subsequently, a measurement algorithm was 
developed using a reference object wall to calculate the predicted height of the seedlings 
detected by the trained model which achieved a Root Mean Square Error (RMSE) of 0.1693 
cm when tested against ground truth values.
- The predicted heights of the seedlings in a tray are 
then averaged to determine the average stem elongation of the seedlings.
- A simple web 
application is developed to simplify the system interaction process for the team at Sunway 
XFarms, allowing them to perform stem elongation monitoring and analysis on the seedlings 
as well as correlating the stem elongation with environmental data.

## Web Application
> Dashboard Page (Before Upload) 
![Dashboard Page (Before Upload)](https://github.com/EugeneSiew/StemHealth/blob/main/images/Batch%20Profile%20Page%20(Before%20Measurement).png)

> Upload Page
![Upload Page](https://github.com/EugeneSiew/StemHealth/blob/main/images/Upload%20Page.png)

> Completed Upload Form
![Completed Upload Form](https://github.com/EugeneSiew/StemHealth/blob/478d54ee9afe7659f49896513d1c8c70d4bb53ba/images/Completed%20Upload%20Form.png)

> Successful Upload
![Successful Upload](https://github.com/EugeneSiew/StemHealth/blob/main/images/Successful%20Upload.png)

> Dashboard Page (After Upload)
![Dashboard Page After Upload](https://github.com/EugeneSiew/StemHealth/blob/main/images/Dashboard%20Page%20(After%20Upload).png)

> Multiple Batches Page
![Multiple Batches Page](https://github.com/EugeneSiew/StemHealth/blob/main/images/Multiple%20Batches.png)

> Batch Profile Page (Before Measurement)
![Batch Profile Page (Before Measurement)](https://github.com/EugeneSiew/StemHealth/blob/main/images/Batch%20Profile%20Page%20(Before%20Measurement).png)

> Batch Profile Page (After Measurement)
![Batch Profile Page (After Measurement)](https://github.com/EugeneSiew/StemHealth/blob/main/images/Batch%20Profile%20Page%20(After%20Measurement).png)

> Popup Pane Displaying Prediction and Measurement Results
![Popup Pane Displaying Prediction and Measurement Results](https://github.com/EugeneSiew/StemHealth/blob/main/images/Popup%20pane%20displaying%20the%20me%20prediction%20and%20measurement%20results.png)

> Batch Profile Page with Height Analysis Tab Active (After Measurement)
![Batch Profile Page with Height Analysis Tab Active (After Measurement)](https://github.com/EugeneSiew/StemHealth/blob/main/images/Batch%20profile%20page%20with%20height%20analysis%20tab%20active%20(after%20measurement).png)

