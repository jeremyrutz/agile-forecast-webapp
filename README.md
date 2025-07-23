# Agile Forecast Web Application

This project is a web application that simulates project completion dates using Monte Carlo methods. Users can input various parameters through a web interface, and the application will run simulations to estimate completion dates based on historical throughput data.

## Project Structure

- **app.py**: The main entry point of the web application. It sets up a Flask web server, handles routing, and processes user input from the web form.
- **requirements.txt**: Lists the dependencies required for the project, including Flask and any other libraries needed for the simulation and web functionality.
- **templates/index.html**: Contains the HTML structure for the web application, including input fields for user parameters and a button to submit the form to run the simulation.
- **static/style.css**: Contains the CSS styles for the web application, defining the layout and appearance of the HTML elements.
- **src/simulation.py**: Contains the logic for the Monte Carlo simulation, defining functions to load throughput data, calculate completion dates, and return results based on user input.

## Setup Instructions

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python app.py
   ```
5. Open your web browser and go to `http://127.0.0.1:5000` to access the application.

## Virtual Environment

To run your app in a virtual environment in Visual Studio Code, follow these steps:

1. Use the **Python: Create Environment** command to create a new virtual environment.
2. Select the environment type (Venv or Conda) from the list.
3. If creating a Venv environment, select the interpreter to use as a base for the new virtual environment.
4. Wait for the environment creation process to complete. A notification will show the progress.
5. Ensure your new environment is selected by using the **Python: Select Interpreter** command.
6. Open a terminal in VS Code and activate the virtual environment (VS Code usually does this automatically when the interpreter is selected).
7. Run your app using the terminal.

To activate the Venv virtual environment, execute the following in your VS Code terminal:

>.venv\Scripts\Activate.ps1

To deactivate and return the terminal to the global Python environment, execute the following:

>deactivate

## Usage Guidelines

- Input the number of items, number of completed items, timeframe in weeks, and any other required parameters in the provided fields.
- Click the "Run Simulation" button to execute the Monte Carlo simulation.
- The application will display the projected completion dates based on the simulation results.

## Overview of Functionality

This web application allows users to easily simulate project completion dates by providing a user-friendly interface. It leverages historical throughput data and Monte Carlo methods to provide estimates with varying levels of certainty. The results are visualized and can help in project planning and management.