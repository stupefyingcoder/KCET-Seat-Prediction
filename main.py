from flask import Flask, request, jsonify, render_template, redirect, url_for
import pandas as pd
import os
import traceback

# Create more robust path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
DATA_FILE = os.path.join(BASE_DIR, 'kcet_cutoff_data_finale.csv')

app = Flask(__name__,
            static_folder=FRONTEND_DIR,
            template_folder=FRONTEND_DIR)

# Load the dataset (defined as global, will reload on upload)
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        print(f"Successfully loaded data with {len(df)} rows")
        print(f"CSV columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Error loading CSV: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()

df = load_data()

# Routes
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin_dashboard():
    global df
    if df.empty:
        df = load_data()

    total_colleges = df['College Code'].nunique()
    total_branches = df['Branch'].nunique()
    total_rows = len(df)
    total_cities = len(df['College Name'].apply(lambda x: x.split(',')[-1].strip() if ',' in x else '').unique())

    grouped = df.sort_values(by='GM', na_position='last').groupby('College Name', as_index=False).first()
    preview_data = grouped[['College Code', 'College Name', 'Branch', 'GM']].head(15).to_dict(orient='records')
    
    return render_template('admin.html',
                           total_colleges=total_colleges,
                           total_branches=total_branches,
                           total_rows=total_rows,
                           total_cities=total_cities,
                           preview_data=preview_data)

@app.route('/upload', methods=['POST'])
def upload_csv():
    global df
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        file.save(DATA_FILE)
        df = load_data()  # reload new data into memory
        print("✅ CSV uploaded and reloaded successfully.")
    else:
        print("❌ Invalid file format or upload error.")
    return redirect(url_for('admin_dashboard'))

@app.route('/predict', methods=['POST'])
def predict():
    global df
    try:
        print(f"Raw request data: {request.data}")
        params = request.json
        print(f"Parsed params: {params}")

        if not params:
            return jsonify({'error': 'No data received'}), 400

        rank = int(params.get('rank', 0))
        category = params.get('category', '')
        branch_filter = params.get('branch', '')

        print(f"Processing request: rank={rank}, category={category}, branch={branch_filter}")

        if df.empty:
            return jsonify({'error': 'Dataset could not be loaded'}), 500

        print(f"First few rows of dataframe: {df.head().to_dict()}")

        # Filter by branch
        branch_df = df
        if branch_filter and branch_filter.lower() != 'all':
            branch_df = df[df['Branch'].str.contains(branch_filter, case=False, na=False)]
            print(f"After branch filter: {len(branch_df)} rows")

        # Category check
        if category not in df.columns:
            print(f"Warning: Category {category} not found in columns!")
            return jsonify({'error': f"Category {category} not found in dataset"}), 400

        # Predict logic
        colleges = []
        for _, row in branch_df.iterrows():
            try:
                cutoff_value = row.get(category, None)
                if pd.notna(cutoff_value) and cutoff_value != '--':
                    cutoff_rank = int(float(str(cutoff_value).replace('--', '0')))
                    if cutoff_rank >= rank:
                        colleges.append({
                            'code': str(row['College Code']),
                            'name': str(row['College Name']),
                            'branch': str(row['Branch']),
                            'cutoff': cutoff_rank
                        })
            except Exception as e:
                print(f"Error processing row: {str(e)}")
                continue

        colleges.sort(key=lambda x: x['cutoff'])

        print(f"Found {len(colleges)} matching colleges")
        return jsonify({'colleges': colleges})

    except Exception as e:
        print(f"Error in predict route: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print(f"Starting Flask server. Frontend dir: {FRONTEND_DIR}")
    print(f"Data file path: {DATA_FILE}")
    print(f"Visit http://127.0.0.1:5000 in your browser")
    app.run(debug=True, port=5000)
