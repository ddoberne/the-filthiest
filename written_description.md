# The Filthiest ⚾
## Design
The goal of this project was to create an automated feed of the best pitches thrown in MLB games from the previous day. A pipeline is constructed that uses a recurring scraping script to pull the data, deploys a model to grade each pitch, uploads the data to a cloud-based database, then queries the database to visualize the results in a user-facing app. Thanks to MLB's recent advances in video cataloguing, individual results can be easily viewed as video with the right query provided by the app.
## The Model
Scikit-learn's RandomForestClassifier was trained with the 600,000+ pitches from the 2021 major league season, scraped from BaseballSavant. These pitches were divided into the categories Fastball, Slider, Sinker, Curveball, Changeup, Cutter, and Splitter. Each has data for velocity, rpm, vertical break, horizontal break, and outcome. The outcome was used as the target variable with the rest as features. Outcomes were divided in Strikes, Balls, Contact (In Play), and Contact (Foul). The model was trained to soft predict whether the outcome was a Strike vs. Contact. The model's prediction of a pitch's outcome would be a Strike given that it was a Strike or Contact would then be used as FiFaX (**Fi**lth **Fa**ctor e**X**pected).
## Data
Data for the app is scraped on a daily basis. The data has an automated process to clean it, then the model is asked to predict on each pitch. The data, with its prediction (FiFaX) is saved to Google Cloud Storage.
## The App
The Streamlit app reads from a database in Google Cloud Storage, then sorts and displays information based on user inputs.  The data can be filtered by pitch category and by pitcher, and then sorted by FiFaX or one of the feature variables. By default, the app only displays Strikes (times the pitcher wins), but users can opt to sort by Hits (times the batter wins). The app displays a table of the top five given the filter and sort. The user can then choose an entry to focus on, and an iframe will provide the video of the pitch in-app. There is also a display of how the selected pitch fares in comparison to others of its pitch category.
## Tools/Algorithms
- Scikit-learn RandomForestRegressor
- Google Cloud Storage
- Streamlit
- TimeDate, Schedule
- Pandas, Numpy
- Selenium, BeautifulSoup
- Seaborn, Matplotlib

## Communication
The app is available for public access at https://share.streamlit.io/ddoberne/the-filthiest/main/display.py
