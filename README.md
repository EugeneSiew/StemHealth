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
