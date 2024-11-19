# Website Bot Project

This README provides instructions on how to set up and run the Website Reader project.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## Setup Instructions

1. Create a virtual environment:

   ```
   python -m venv venv
   ```

2. Activate the virtual environment:

   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

3. Install the required packages:

   ```
   pip install -r ./requirements/local.txt
   ```

4. Set up environment variables:
   - Copy the `.env.sample` file to a new file named `.env`
   - Update the values in `.env` with your specific configuration

## Running the Project

To run the Website Bot, use the following command:

```
python ./src/main.py
```

             