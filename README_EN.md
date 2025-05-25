Okay, here's the English translation of your README file:

-----

# MeetSpot (聚点) - Intelligent Meeting Point Recommendation System

\<p align="center"\>
\<img src="docs/images/logo.png" alt="MeetSpot Logo" width="600"\>
\</p\>

MeetSpot (聚点) is an intelligent meeting point recommendation system designed to help users quickly find the most suitable meeting places based on the locations of multiple participants and their specific needs. Whether you're looking for a quiet café for a business meeting, a lively restaurant for a friends' gathering, or a library suitable for studying, MeetSpot can provide you with intelligent recommendations.

## 🔍 Project Showcase

\<p align="center"\>
\<a href="docs/videos/bandicam 2025-05-25 12-07-09-174.mp4"\>
\<strong\>📹 Click to watch the project demo video\</strong\>
\</a\>
\</p\>

\<p align="center"\>
\<em\>Project Demo - Intelligent recommendation process for multi-location meeting places\</em\>
\</p\>

> Note: GitHub does not support direct video playback. Please download and watch locally, or clone the repository to view.

\<p align="center"\>
\<img src="docs/images/show1.png" alt="MeetSpot Showcase 1" width="600"\>
\</p\>

\<p align="center"\>
\<img src="docs/images/show2.png" alt="MeetSpot Showcase 2" width="600"\>
\</p\>

\<p align="center"\>
\<img src="docs/images/show3.png" alt="MeetSpot Showcase 3" width="600"\>
\</p\>

\<p align="center"\>
\<img src="docs/images/show4.png" alt="MeetSpot Showcase 4" width="600"\>
\</p\>

## ✨ Main Features

  - **Intelligent Center Point Calculation**: Automatically calculates the fairest and most convenient meeting center area based on the locations of all participants.
  - **Diverse Venue Recommendations**: Supports recommendations for various types of venues, including but not limited to:
      - Cafés ☕
      - Restaurants 🍜
      - Libraries 📚
      - Shopping Malls 🛍️
      - Parks 🌳
      - Cinemas 🎬
      - Basketball Courts 🏀
      - And more custom venue types\!
  - **Personalized Needs Fulfillment**: Users can input special requirements such as "easy parking," "quiet environment," "suitable for business," "has Wi-Fi," etc., and the system will prioritize these factors in its recommendations.
  - **Dynamic Themed Results Page**: The results page automatically changes its theme color and icons to match the selected venue type, providing a more immersive experience.
  - **Interactive Map Display**:
      - Clearly marks all participant locations, the calculated optimal meeting center point, and recommended venues on the map.
      - Provides navigation links to recommended venues (via Amap/Gaode Maps).
  - **Detailed Venue Information**: Displays the name, address, rating, opening hours, contact number, tags, and distance from the center point for recommended venues.
  - **AI Search Process Simulation**: Animates the "thinking" process of the AI assistant analyzing needs, searching for locations, and ranking them, adding an element of fun.
  - **Web User Interface**: Provides a simple and easy-to-use web interface (`meetspot_finder.html`) for location input and needs selection.
  - **API Interface**: Offers a `/api/find_meetspot` endpoint for easy integration with other systems.

## 🚀 How it Works

1.  **User Input**: Users input the location descriptions of at least two participants, select desired venue types (multiple selections or custom keywords allowed), and any special requirements through the frontend interface.
2.  **Backend Reception**: The FastAPI-built backend server receives the request.
3.  **Geocoding**: Calls the Amap (Gaode Maps) API to convert user-input location descriptions into precise latitude and longitude coordinates.
4.  **Center Point Calculation**: Calculates the geometric center point based on the latitude and longitude of all participants as the initial center of the meeting area.
5.  **POI Search**: Using the center point as the origin, searches for relevant Points of Interest (POI) within a certain radius (e.g., 5 km), based on user-selected venue types (keywords) and Amap's category codes.
6.  **Intelligent Sorting and Filtering**:
      - Comprehensively considers factors like venue ratings, distance from the center point, and whether special user needs are met.
      - Scores and ranks the searched venues.
7.  **Dynamic Result Generation**:
      - Selects the top-rated venues as recommendations.
      - Generates an HTML page containing detailed recommendation information and an interactive map.
8.  **Frontend Display**: Returns the URL of the generated HTML page to the frontend, and the user views the recommendation results in a new tab.

## 🛠️ Tech Stack

  - **Backend**: Python, FastAPI, Uvicorn
  - **Core Recommendation Logic**: `app.tool.meetspot_recommender.CafeRecommender` (Although named CafeRecommender, it has general venue recommendation capabilities)
  - **Intelligent Agent Framework**: OpenManus (Project structure includes related modules like `app.agent` and `app.flow`)
  - **Geo Services**: Amap (Gaode Maps) Open Platform API (Geocoding, POI Search, Map Display)
  - **Frontend**: HTML, CSS, JavaScript (Boxicons icon library)
  - **Data Handling**: Pydantic (Data validation and model definition)
  - **Asynchronous Processing**: `asyncio`, `aiohttp`

## ⚙️ Installation and Configuration

1.  **Clone the repository**:

    ```
    git clone https://github.com/JasonRobertDestiny/MeetSpot.git
    cd MeetSpot
    ```

2.  **Create and activate a virtual environment**:

    ```
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies**:

    ```
    pip install -r requirements.txt
    ```

4.  **Configure API Keys**:

      - Find the `config` folder in the project root directory.
      - Inside the `config` folder, copy `config.toml.example` to `config.toml`.
      - Edit `config.toml` and add your Amap API Key and Security JS Code:
        ```toml
        # config/config.toml
        [amap]
        api_key = "YOUR_AMAP_API_KEY"          # Replace with your Amap Web Service API Key
        security_js_code = "YOUR_AMAP_SECURITY_JS_CODE" # Replace with your Amap JS API Security Key

        # If using OpenAI or other LLM services, configure them here as well
        # [openai]
        # api_key = "sk-YOUR_OPENAI_API_KEY"
        # base_url = "YOUR_OPENAI_API_BASE_URL_IF_NEEDED"
        ```
      - **Important**: `api_key` is used for backend calls to Amap Web Service APIs (like geocoding, POI search), and `security_js_code` is for security verification when loading the map via the frontend JS API. Ensure you obtain both credentials from the Amap Open Platform.

## ▶️ Running the Project

Run the following command in the project root directory to start the web server:

```
python web_server.py
```

The server will start by default at `http://127.0.0.1:8000` (or `http://0.0.0.0:8000`).

## 💡 How to Use

1.  Open your browser and navigate to `http://localhost:8000`.
      - (If the server is bound to `0.0.0.0`, you can also access it via your local network IP address).
2.  In the "Participant Locations" section, enter the starting locations for at least two meeting participants. You can click the "Add more locations" button to add more input fields.
3.  In the "Select Scene Type" section, check the venue types you are interested in (e.g., café, library, restaurant). You can also enter more specific custom keywords in the input box below.
4.  In the "Special Requirements" input box, enter your additional needs, such as "quiet," "has projector," "kid-friendly," etc.
5.  Click the "Find Best MeetSpot" button.
6.  The system will perform calculations and searches, and upon completion, will automatically redirect to a new page containing the recommended results and map.

## 📂 Project Structure (Overview)

```
MeetSpot/
├── app/                      # Core application logic
│   ├── agent/                # OpenManus intelligent agent related implementation
│   ├── flow/                 # Task flow definitions
│   ├── prompt/               # Prompt engineering related templates
│   ├── tool/                 # Tool definitions, core is meetspot_recommender.py
│   ├── config.py             # Application configuration loading
│   ├── logger.py             # Logging configuration
│   └── ...
├── config/                   # Configuration files directory
│   └── config.toml.example   # Configuration file example
├── docs/                     # Documentation and resources
│   ├── images/               # Image resources
│   │   ├── logo.png
│   │   ├── show1.png
│   │   ├── show2.png
│   │   ├── show3.png
│   │   └── show4.png
│   └── videos/               # Video resources
├── logs/                     # Log file storage directory
├── workspace/                # Frontend static files and user-generated content
│   ├── js_src/               # Backend-generated HTML recommendation result pages are stored here
│   ├── meetspot_finder.html  # Main frontend input page
│   └── index.html            # (Optional) Project homepage or old entry point
├── tests/                    # Test code
├── .venv/                    # Python virtual environment
├── main.py                   # Command-line interaction entry point (if retained)
├── web_server.py             # FastAPI Web server main program
├── requirements.txt          # Python dependency package list
└── README.md                 # This file
```

## 🔮 Future Prospects

  - **User Accounts & History**: Allow users to save frequently used locations and query history.
  - **Finer-grained Filtering Conditions**: E.g., filter by average cost, business status (like "Open Now").
  - **Multilingual Support**: Provide an English or other language interface.
  - **Route Planning Integration**: Directly display multi-participant route plans to recommended locations on the results page.
  - **Real-time Traffic Information**: Optimize recommendations by incorporating real-time traffic conditions.
  - **Mobile Optimization**: Further optimize display and interaction experience on mobile devices.

## 🤝 Contributing

Contributions to the MeetSpot (聚点) project are welcome\! If you have any suggestions, find bugs, or want to add new features, please feel free to participate by:

1.  Forking this repository.
2.  Creating your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Committing your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Pushing your changes to the branch (`git push origin feature/AmazingFeature`).
5.  Opening a Pull Request.

## 📜 License

This project is licensed under the [MIT License](https://www.google.com/search?q=LICENSE).

We hope this README helps you better understand and use MeetSpot (聚点)\!

-----