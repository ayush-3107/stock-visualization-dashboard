# Stock Dashboard

A web-based stock dashboard application for managing user profiles, tracking favorite stocks, and visualizing stock data. Built with Python and designed for extensibility and ease of use.


---

## Features
- User authentication with secure password storage (bcrypt hashes)
- User profile management with profile pictures
- Favorite stocks tracking per user
- Customizable user settings
- Stock data retrieval and visualization
- Modular code structure for easy maintenance

---

## Project Structure
```
config.yaml                # Application configuration (users, cookies, etc.)
generate_passwords.py      # Utility for generating password hashes
main.py                    # Main application entry point
requirements.txt           # Python dependencies
pages/                     # App pages (Dashboard, Profile, Register)
profile_pics/              # User profile images
services/                  # Service modules (e.g., stock data)
user_favourites/           # User-specific favorite stocks (JSON)
user_settings/             # User-specific settings (JSON)
utils/                     # Utility modules (charts, settings manager)
```

---

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
```bash
git clone https://github.com/yourusername/stock-dashboard.git
cd stock-dashboard
pip install -r requirements.txt
```

### Running the Application
```bash
python main.py
```

---

## Configuration
- User credentials, cookies, and other settings are managed in `config.yaml`.
- Add user profile images to the `profile_pics/` directory.

---

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
