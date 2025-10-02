import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os
import xml.etree.ElementTree as ET
from datetime import datetime

def load_data_from_excel(file_path):
    """
    Load training data from Excel file
    """
    try:
        print(f"📖 Loading data from Excel: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Check required columns
        required_columns = ['description', 'category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}. Required columns: {required_columns}")
        
        # Remove rows with missing values
        original_len = len(df)
        df = df.dropna(subset=required_columns)
        removed_rows = original_len - len(df)
        
        if removed_rows > 0:
            print(f"⚠️  Removed {removed_rows} rows with missing values")
        
        if len(df) == 0:
            raise ValueError("No valid data found in Excel file")
        
        print(f"✅ Successfully loaded {len(df)} records from Excel")
        print(f"📊 Categories found: {sorted(df['category'].unique())}")
        print(f"📈 Category distribution:")
        print(df['category'].value_counts().to_string())
        print()
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return None

def load_data_from_xml(file_path):
    """
    Load training data from XML file
    """
    try:
        print(f"📖 Loading data from XML: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"XML file not found: {file_path}")
        
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        data = []
        for record in root.findall('record'):
            desc_elem = record.find('description')
            cat_elem = record.find('category')
            
            if desc_elem is not None and cat_elem is not None:
                desc = desc_elem.text
                cat = cat_elem.text
                if desc and desc.strip() and cat and cat.strip():
                    data.append((desc.strip(), cat.strip()))
        
        if not data:
            raise ValueError("No valid data found in XML file")
        
        df = pd.DataFrame(data, columns=['description', 'category'])
        
        print(f"✅ Successfully loaded {len(df)} records from XML")
        print(f"📊 Categories found: {sorted(df['category'].unique())}")
        print(f"📈 Category distribution:")
        print(df['category'].value_counts().to_string())
        print()
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading XML file: {e}")
        return None

def load_training_data(data_source='excel'):
    """
    Load training data from external file
    
    Parameters:
    data_source (str): 'excel' or 'xml'
    """
    data_dir = 'data'
    
    if data_source.lower() == 'excel':
        file_path = os.path.join(data_dir, 'training_data.xlsx')
        return load_data_from_excel(file_path)
    elif data_source.lower() == 'xml':
        file_path = os.path.join(data_dir, 'training_data.xml')
        return load_data_from_xml(file_path)
    else:
        print(f"❌ Unsupported data source: {data_source}")
        print("Supported sources: 'excel', 'xml'")
        return None

def preprocess_text(text):
    """
    Simple text preprocessing
    """
    if pd.isna(text):
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text

def validate_data(df):
    """
    Validate the loaded data
    """
    print("🔍 Validating dataset...")
    
    # Check minimum samples per category
    category_counts = df['category'].value_counts()
    min_samples = 2  # Minimum samples needed for train/test split
    
    insufficient_categories = category_counts[category_counts < min_samples]
    if len(insufficient_categories) > 0:
        print(f"⚠️  Categories with insufficient samples (< {min_samples}):")
        print(insufficient_categories.to_string())
        print("Consider adding more samples for these categories.")
    
    # Check for very long descriptions
    max_length = df['description'].str.len().max()
    if max_length > 200:
        long_descriptions = df[df['description'].str.len() > 200]
        print(f"⚠️  Found {len(long_descriptions)} descriptions longer than 200 characters")
        print("Consider shortening very long descriptions for better performance.")
    
    # Check for duplicate descriptions
    duplicates = df[df.duplicated(subset=['description'], keep=False)]
    if len(duplicates) > 0:
        print(f"⚠️  Found {len(duplicates)} duplicate descriptions")
        print("Consider removing or modifying duplicate entries.")
    
    print("✅ Data validation completed")
    print()

def train_model(data_source='excel'):
    """
    Train the transaction categorization model using external data
    
    Parameters:
    data_source (str): 'excel' or 'xml'
    """
    print("🚀 Starting model training...")
    print("=" * 60)
    
    # Load training data from external file
    df = load_training_data(data_source)
    if df is None:
        print("❌ Failed to load training data. Training aborted.")
        return False
    
    # Validate data
    validate_data(df)
    
    # Preprocess text
    print("🔤 Preprocessing text data...")
    df['description_clean'] = df['description'].apply(preprocess_text)
    
    # Prepare features and labels
    X = df['description_clean']
    y = df['category']
    
    # Check if we have enough samples for splitting
    if len(df) < 4:
        print("❌ Not enough samples for train/test split (minimum 4 required)")
        return False
    
    # Split data with stratification (if possible)
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print("✅ Used stratified split")
    except ValueError:
        # Fallback to regular split if stratification is not possible
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        print("⚠️  Used regular split (stratification not possible)")
    
    print(f"📊 Training samples: {len(X_train)}")
    print(f"📊 Testing samples: {len(X_test)}")
    print()
    
    # Create TF-IDF Vectorizer
    print("🔍 Creating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=min(1000, len(df) * 10),  # Adjust max_features based on dataset size
        ngram_range=(1, 2),  # Use unigrams and bigrams
        lowercase=True,
        stop_words=None,  # Keep all words for Indonesian
        min_df=1,
        max_df=0.95
    )
    
    # Fit and transform training data
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    print(f"✅ TF-IDF feature matrix shape: {X_train_tfidf.shape}")
    print()
    
    # Train Logistic Regression model
    print("🤖 Training Logistic Regression model...")
    model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        C=1.0,
        solver='liblinear'
    )
    
    model.fit(X_train_tfidf, y_train)
    print("✅ Model training completed!")
    print()
    
    # Evaluate model
    print("📊 Evaluating model performance...")
    y_pred = model.predict(X_test_tfidf)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"🎯 Accuracy: {accuracy:.4f}")
    print()
    
    if len(X_test) > 0:
        print("📋 Classification Report:")
        print(classification_report(y_test, y_pred))
    
    # Feature importance (top words per category)
    print("🔝 Top features per category:")
    feature_names = vectorizer.get_feature_names_out()
    
    for i, category in enumerate(model.classes_):
        # Get top 5 features for this category
        if len(feature_names) >= 5:
            top_indices = model.coef_[i].argsort()[-5:][::-1]
        else:
            top_indices = model.coef_[i].argsort()[::-1]
        top_features = [feature_names[idx] for idx in top_indices]
        print(f"  {category}: {', '.join(top_features)}")
    print()
    
    # Save model and vectorizer
    print("💾 Saving model and vectorizer...")
    
    # Create models directory if it doesn't exist
    models_dir = 'models'
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    # Save vectorizer
    vectorizer_path = os.path.join(models_dir, 'vectorizer.pkl')
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"✅ Vectorizer saved to: {vectorizer_path}")
    
    # Save model
    model_path = os.path.join(models_dir, 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✅ Model saved to: {model_path}")
    
    # Save metadata
    metadata = {
        'model_type': 'LogisticRegression',
        'vectorizer_type': 'TfidfVectorizer',
        'data_source': data_source,
        'total_samples': len(df),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'accuracy': accuracy,
        'categories': list(model.classes_),
        'feature_count': X_train_tfidf.shape[1],
        'trained_at': datetime.now().isoformat(),
        'version': '1.0.0'
    }
    
    metadata_path = os.path.join(models_dir, 'metadata.pkl')
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✅ Metadata saved to: {metadata_path}")
    print()
    
    # Test predictions on some examples
    print("🧪 Testing predictions on sample data...")
    test_descriptions = [
        "Makan siang di restoran padang",
        "Isi bensin motor",
        "Bayar tagihan internet",
        "Beli laptop baru",
        "Nonton film di bioskop"
    ]
    
    for desc in test_descriptions:
        desc_clean = preprocess_text(desc)
        desc_tfidf = vectorizer.transform([desc_clean])
        prediction = model.predict(desc_tfidf)[0]
        probability = model.predict_proba(desc_tfidf).max()
        print(f"  '{desc}' → {prediction} (confidence: {probability:.3f})")
    
    print()
    print("🎉 Model training completed successfully!")
    print("📁 Files saved in 'models/' directory:")
    print("   - model.pkl (trained model)")
    print("   - vectorizer.pkl (TF-IDF vectorizer)")
    print("   - metadata.pkl (training metadata)")
    print()
    print("💡 To add more training data:")
    print("   1. Edit the training_data.xlsx file in 'data/' directory")
    print("   2. Add more rows with 'description' and 'category' columns")
    print("   3. Run this script again to retrain the model")
    
    return True

def load_and_test_model():
    """
    Load saved model and test it
    """
    try:
        print("\n🔄 Testing saved model...")
        
        models_dir = 'models'
        
        # Check if model files exist
        vectorizer_path = os.path.join(models_dir, 'vectorizer.pkl')
        model_path = os.path.join(models_dir, 'model.pkl')
        metadata_path = os.path.join(models_dir, 'metadata.pkl')
        
        if not all(os.path.exists(path) for path in [vectorizer_path, model_path, metadata_path]):
            print("❌ Model files not found. Please train the model first.")
            return False
        
        # Load vectorizer
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        
        # Load model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        print(f"✅ Loaded model (accuracy: {metadata['accuracy']:.4f})")
        print(f"📊 Categories: {metadata['categories']}")
        print(f"📅 Trained at: {metadata['trained_at']}")
        print(f"📁 Data source: {metadata.get('data_source', 'unknown')}")
        
        # Test prediction function
        def predict_category(description):
            desc_clean = preprocess_text(description)
            desc_tfidf = vectorizer.transform([desc_clean])
            prediction = model.predict(desc_tfidf)[0]
            confidence = model.predict_proba(desc_tfidf).max()
            return prediction, confidence
        
        # Test examples
        test_cases = [
            "Beli es krim",
            "Naik ojek online",
            "Transfer uang ke keluarga",
            "Bayar cicilan kredit",
            "Medical checkup"
        ]
        
        print("\n🧪 Testing with sample predictions:")
        for test_desc in test_cases:
            category, conf = predict_category(test_desc)
            print(f"  '{test_desc}' → {category} (confidence: {conf:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

if __name__ == "__main__":
    print("🏦 Transaction Categorization Model Training")
    print("=" * 60)
    print()
    print("📋 Make sure you have:")
    print("   1. 'data/training_data.xlsx' file with columns: description, category")
    print("   2. pandas, sklearn, openpyxl installed (pip install pandas scikit-learn openpyxl)")
    print()
    
    # Check if data file exists
    data_file = 'data/training_data.xlsx'
    
    if not os.path.exists('data'):
        print("📁 Creating 'data' directory...")
        os.makedirs('data')
    
    if not os.path.exists(data_file):
        print(f"❌ Training data file not found: {data_file}")
        print()
        print("💡 Please create the training data file:")
        print("   1. Create 'data/training_data.xlsx' file")
        print("   2. Add columns: 'description' and 'category'")
        print("   3. Add your training data rows")
        print()
        print("📋 Example Excel format:")
        print("   description               | category")
        print("   --------------------------|------------------")
        print("   Kopi Kenangan            | Makanan & Minuman")
        print("   Naik Gojek               | Transportasi")
        print("   Bayar listrik PLN        | Tagihan")
        print()
        exit(1)
    # Train the model using Excel data
    success = train_model(data_source='excel')
    
    if success:
        # Test the saved model
        load_and_test_model()
    else:
        print("❌ Model training failed. Please check your data and try again.")