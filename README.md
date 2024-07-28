# Fabrico: Fabric Defect Detection System

![work3](https://github.com/user-attachments/assets/85ab4dac-7c39-4916-b71e-6d787ad8b32a)


## Overview

Fabrico is an advanced fabric defect detection system designed to identify various defects in fabric materials using state-of-the-art machine learning techniques. This project leverages YOLO (You Only Look Once) for real-time object detection, providing an efficient solution for quality control in the textile industry.

## Features

- **Real-time Detection**: Utilizes YOLO for fast and accurate defect detection.
- **Scalable**: Built with Docker and Flask for easy deployment and scalability.
- **User-Friendly Interface**: Intuitive web interface for uploading and analyzing fabric images.
- **Detailed Reports**: Generates detailed reports on detected defects, aiding in quality control processes.

## Technologies Used

<div>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="40" height="40" alt="Python">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/flask/flask-original.svg" width="40" height="40" alt="Flask">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original.svg" width="40" height="40" alt="Docker">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/github/github-original.svg" width="40" height="40" alt="GitHub">
</div>

## Installation

### Using Docker

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/HuzaifaKhaan/Fabrico.git
    cd Fabrico
    ```

2. **Build the Docker Image**:
    ```bash
    docker-compose build
    ```

3. **Run the Docker Container**:
    ```bash
    docker-compose up
    ```

4. **Open Your Browser and Navigate to**:
    ```
    http://127.0.0.1:5000
    ```

### Without Docker

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/HuzaifaKhaan/Fabrico.git
    cd Fabrico
    ```

2. **Create a Virtual Environment and Activate It**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Flask Application**:
    ```bash
    python run.py
    ```

5. **Open Your Browser and Navigate to**:
    ```
    http://127.0.0.1:5000
    ```

## Usage

1. **Upload a Fabric Image**:
    - Click on the "Upload" button and select a fabric image from your local machine.

2. **Get Defect Detection Results**:
    - The system will analyze the image using the YOLO model and display the detected defects on the screen.

## Project Structure

```plaintext
.
├── app/                 # Application files and folders
├── migrations/          # Database migrations
├── .env                 # Environment variables
├── .gitignore           # Git ignore file
├── README.md            # Project README file
├── bg.png               # Background image
├── config.py            # Configuration file
├── defect_times.txt     # Text file with defect timings
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Dockerfile for building the Docker image
├── imagesaveyolo.py     # Image saving script for YOLO
├── requirements.txt     # Project dependencies
├── run.py               # Main application file
└── .vscode/             # VSCode configuration files
```

Contribution Guidelines
Contributions to Fabrico are welcome! To contribute, please follow these steps:

Fork the repository.
Create a new branch for your feature or bug fix.
Make your changes and commit them.
Push your changes to your fork.
Submit a pull request to the main repository.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Contact
Feel free to reach out if you have any questions or suggestions!

<div>
  <a href="https://www.linkedin.com/in/huzaifa-khaan" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-Huzaifa%20Khan-blue?logo=linkedin" alt="LinkedIn">
  </a>
  <a href="mailto:huzukham14@gmail.com">
    <img src="https://img.shields.io/badge/Email-huzukham14@gmail.com-red?logo=gmail" alt="Email">
  </a>
</div>
