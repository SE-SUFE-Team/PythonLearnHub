# PythonLearnHub
A web-based interactive Python learning platform for beginners and developers.
## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the project**
   ```bash
   cd python_learning_platform
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5555`

## Project Structure

```
python_learning_platform/
├── app.py                 # Main Flask application
├── safe_executor.py       # Safe code execution environment
├── module_content.py      # Learning content and examples
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── module_detail.html # Module detail page
│   ├── code_playground.html # Code playground
│   ├── about.html        # About page
│   └── error.html        # Error pages
└── static/               # Static assets
    ├── css/
    │   └── main.css      # Main stylesheet
    └── js/
        └── main.js       # Main JavaScript
```
