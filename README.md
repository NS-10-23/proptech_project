# AI-Based Nepal Real Estate Property Valuation System

This project is a Django-based property valuation system that uses a machine learning model to estimate real-estate prices in selected locations in Nepal. Users enter property characteristics such as location, land area, floors, road width, road type, rooms, and bathrooms, and the system returns an estimated property value together with rental and five-year forecast information.

## Main Components

- **Django web application** – provides the property valuation dashboard and stores recent valuation records.
- **Machine Learning model** – a Random Forest Regressor implemented as a scikit-learn Pipeline.
- **Dataset** – `dataset/nepal_gharjagga_data.csv` contains 6,000 property records used by the project.
- **Training script** – `train_model.py` generates the project dataset, preprocesses the features, trains the model, evaluates it with R², and saves the trained model.
- **ML notebook** – `ML_Training_Notebook.ipynb` documents dataset loading, preprocessing, training, evaluation, and model export in notebook form.
- **Saved model** – `valuation/ml_models/nepal_gharjagga_model.joblib` is loaded by the Django application for predictions.
- **SQLite database** – `db.sqlite3` stores property valuation records created by the application.

## Machine Learning Workflow

The model uses the following input features:

- `location` – categorical
- `land_aana` – numerical
- `floors` – numerical
- `road_feet` – numerical
- `road_type` – categorical
- `rooms` – numerical
- `bathrooms` – numerical

The target variable is `price_npr`.

Preprocessing is performed with a scikit-learn `ColumnTransformer`:

- Numerical features are standardized with `StandardScaler`.
- Categorical features are converted using `OneHotEncoder(handle_unknown='ignore')`.

The processed features are passed to a `RandomForestRegressor` with 150 trees, maximum depth 20, and random state 42. The data is split into 80% training and 20% testing data using `random_state=42`. Model performance is evaluated using the R² score.

## Project Structure

```text
proptech_project/
├── dataset/
│   └── nepal_gharjagga_data.csv
├── valuation/
│   ├── ml_models/
│   │   ├── nepal_gharjagga_model.joblib
│   │   └── real_estate_model.joblib
│   ├── templates/
│   │   └── valuation/
│   │       └── index.html
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── proptech/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── ML_Training_Notebook.ipynb
├── train_model.py
├── manage.py
├── requirements.txt
├── README.md
└── db.sqlite3
```

## Installation

1. Create and activate a Python virtual environment.

   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Run the Django Application

From the folder containing `manage.py`:

```bash
python manage.py migrate
python manage.py runserver
```

Then open the local Django development server shown in the terminal (normally `http://127.0.0.1:8000/`).

## Train the Model Again

The existing training script can regenerate the dataset and retrain the model:

```bash
python train_model.py
```

This creates/updates:

```text
dataset/nepal_gharjagga_data.csv
valuation/ml_models/nepal_gharjagga_model.joblib
```

Alternatively, use `ML_Training_Notebook.ipynb` to run the documented machine-learning workflow interactively.

## Run the Notebook

Install Jupyter if it is not already available:

```bash
pip install jupyter
```

Then run:

```bash
jupyter notebook ML_Training_Notebook.ipynb
```

The notebook loads the supplied dataset, performs preprocessing, trains the Random Forest model, reports the R² evaluation score, and saves the trained pipeline.

## Notes

The dataset used by this project is generated/synthetic project data rather than a directly collected government or commercial property transaction dataset. The model's predictions should therefore be treated as project estimates and not as certified market valuations.

The included `venv` directory is an environment from the development machine. For a clean setup on another computer, use `requirements.txt` to create a new virtual environment instead of relying on the included environment.
