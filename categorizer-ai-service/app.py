from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import logging
import pickle
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables for model and vectorizer
model = None
vectorizer = None
model_metadata = None

def load_models():
    """
    Load trained model and vectorizer on startup
    """
    global model, vectorizer, model_metadata
    
    try:
        models_dir = 'models'
        
        # Load vectorizer
        vectorizer_path = os.path.join(models_dir, 'vectorizer.pkl')
        if os.path.exists(vectorizer_path):
            with open(vectorizer_path, 'rb') as f:
                vectorizer = pickle.load(f)
            logger.info("✅ Vectorizer loaded successfully")
        else:
            logger.warning("⚠️ vectorizer.pkl not found, using fallback keyword-based categorization")
        
        # Load model
        model_path = os.path.join(models_dir, 'model.pkl')
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            logger.info("✅ Model loaded successfully")
        else:
            logger.warning("⚠️ model.pkl not found, using fallback keyword-based categorization")
        
        # Load metadata
        metadata_path = os.path.join(models_dir, 'metadata.pkl')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                model_metadata = pickle.load(f)
            logger.info(f"✅ Model metadata loaded - Accuracy: {model_metadata.get('accuracy', 'unknown')}")
        
        # Check if both model and vectorizer are loaded
        if model is not None and vectorizer is not None:
            logger.info("🤖 ML Model categorization enabled")
            return True
        else:
            logger.warning("🔄 Falling back to keyword-based categorization")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")
        logger.warning("🔄 Falling back to keyword-based categorization")
        return False

def preprocess_text(text):
    """
    Simple text preprocessing (same as training)
    """
    if pd.isna(text) or not text:
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text

def predict_with_ml_model(description):
    """
    Predict category using trained ML model
    """
    global model, vectorizer
    
    if model is None or vectorizer is None:
        return None, 0.0
    
    try:
        # Preprocess text
        desc_clean = preprocess_text(description)
        
        # Transform to TF-IDF features
        desc_tfidf = vectorizer.transform([desc_clean])
        
        # Make prediction
        prediction = model.predict(desc_tfidf)[0]
        
        # Get confidence score
        probabilities = model.predict_proba(desc_tfidf)[0]
        confidence = max(probabilities)
        
        return prediction, confidence
        
    except Exception as e:
        logger.error(f"Error in ML prediction: {e}")
        return None, 0.0

# Transaction categories with keywords
CATEGORY_KEYWORDS = {
    "Makanan & Minuman": [
        "alfamart", "ayam", "bakso", "breadtalk", "burger", "cafe", "coffee",
        "dunkin", "drink", "es krim", "food", "gado-gado", "galon", "grocery",
        "ice cream", "indomaret", "j.co", "jajanan", "juice", "katering", "kfc",
        "kopi", "makan", "makan malam", "makan siang", "mcd", "mcdonald", "minum",
        "nasi", "pasar", "pizza", "rendang", "restoran", "restaurant", "sarapan",
        "snack", "soto", "starbucks", "supermarket", "tea", "teh", "warteg", "warung"
    ],
    "Transportasi": [
        "angkot", "angkutan", "ban", "bandara", "BBM", "bengkel", "bensin",
        "blue bird", "booking", "bus", "express", "flight", "gojek", "grab",
        "grab bike", "grab car", "kereta", "KRL", "LRT", "mobil", "motor", "MRT",
        "ojek", "oli", "parkir", "pelabuhan", "pertamax", "pertamina", "pesawat",
        "railway", "service", "shell", "SIM", "solar", "spbu", "stasiun", "STNK",
        "taxi", "tiket", "tol", "train", "transport", "travel", "uber", "e-money", "e-toll"
    ],
    "Tagihan": [
        "air", "angsuran", "asuransi", "bayar", "bill", "bpjs", "cicilan",
        "disney+", "hbo", "indihome", "indosat", "insurance", "internet",
        "iuran", "keamanan", "KPR", "kredit", "listrik", "pam", "pajak",
        "paket data", "pascabayar", "pinjaman", "pln", "pulsa", "RW", "RT", "sampah",
        "smartfren", "tagihan", "tax", "telkom", "telkomsel", "three", "token listrik",
        "vidio", "wifi", "xl", "IPL"
    ],
    "Belanja": [
        "baju", "belanja", "beli", "blibli", "bukalapak", "celana", "charger",
        "detergen", "elektronik", "electronics", "fashion", "furniture", "gadget",
        "handphone", "household", "kabel", "kosmetik", "laptop", "lazada",
        "makeup", "mall", "market", "oleh-oleh", "pakaian", "pakan hewan", "pampers",
        "pecah belah", "perabotan", "pet food", "popok", "sabun", "sepatu", "shampoo",
        "shopee", "shopping", "skincare", "store", "tas", "toko", "tokopedia", "zalora"
    ],
    "Hiburan": [
        "billiard", "bioskop", "bowling", "cinema", "concert", "dufan", "festival",
        "film", "fitness", "game", "gaming", "gym", "hobi", "holiday", "hotel",
        "karaoke", "konser", "ktv", "langganan game", "liburan", "movie", "netflix",
        "olahraga", "ps4", "ps5", "rekreasi", "spotify", "sport", "staycation", "steam",
        "taman bermain", "tiket", "travel", "vacation", "wisata", "xbox", "youtube"
    ],
    "Kesehatan": [
        "apotik", "century", "checkup", "dental", "dokter", "gigi", "guardian",
        "imunisasi", "kacamata", "kandungan", "kehamilan", "kimia farma", "klinik",
        "lab", "laboratorium", "mata", "medical", "medicine", "obat", "pharmacy",
        "psikiater", "psikolog", "rontgen", "rs", "rumah sakit", "suplemen", "terapi",
        "therapy", "usg", "vaksin", "vitamin", "glasses"
    ],
    "Pendidikan": [
        "alat tulis", "bimbel", "bimbingan belajar", "book", "bootcamp", "buku",
        "certification", "course", "exam", "kampus", "kelulusan", "kuliah", "kursus",
        "les", "pendaftaran sekolah", "penelitian", "research", "sekolah", "seminar",
        "semester", "skripsi", "spp", "stationery", "thesis", "training", "uang sekolah",
        "ujian", "universitas", "webinar", "workshop"
    ],
    "Investasi": [
        "ajaib", "asuransi jiwa", "bareksa", "bitcoin", "bond", "broker", "crypto",
        "dana darurat", "deposit", "emergency fund", "emas", "ethereum", "fintech",
        "gold", "indodax", "investasi", "investment", "life insurance", "mutual fund",
        "obligasi", "p2p lending", "pluang", "RDN", "reksadana", "saham", "saving",
        "sekuritas", "stock", "tabungan", "tanamduit", "trading"
    ],
    "Lainnya": [
        "administrasi", "amal", "donasi", "denda", "hadiah", "infaq", "kado", "notaris",
        "patungan", "perbaikan", "renovasi", "sedekah", "servis", "sumbangan",
        "transfer", "uang duka", "zakat", "biaya tak terduga"
    ]
}

def clean_text(text):
    """Clean and normalize text for better matching"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers, keep only letters and spaces
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text

def categorize_transaction(description):
    """
    Categorize transaction based on description
    First tries ML model, then falls back to keyword matching
    """
    if not description:
        return "Lainnya", 0.0
    
    # Try ML model first
    if model is not None and vectorizer is not None:
        ml_category, ml_confidence = predict_with_ml_model(description)
        if ml_category and ml_confidence > 0.3:  # Minimum confidence threshold
            logger.info(f"ML prediction: '{description}' -> {ml_category} ({ml_confidence:.3f})")
            return ml_category, ml_confidence
    
    # Fallback to keyword-based categorization
    cleaned_desc = clean_text(description)
    words = cleaned_desc.split()
    
    category_scores = {}
    
    # Calculate score for each category
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            keyword_clean = clean_text(keyword)
            
            # Exact match gets higher score
            if keyword_clean in cleaned_desc:
                score += 1
                
            # Partial match gets lower score
            elif any(word in keyword_clean or keyword_clean in word for word in words):
                score += 0.5
        
        # Normalize score
        if total_keywords > 0:
            category_scores[category] = score / total_keywords
    
    # Find category with highest score
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[best_category]
        
        # If confidence is too low, return "Lainnya"
        if confidence < 0.1:
            return "Lainnya", confidence
            
        logger.info(f"Keyword prediction: '{description}' -> {best_category} ({confidence:.3f})")
        return best_category, confidence
    
    return "Lainnya", 0.0

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    ml_status = "enabled" if (model is not None and vectorizer is not None) else "disabled"
    
    health_data = {
        'status': 'healthy',
        'service': 'categorizer-ai-service',
        'version': '1.0.0',
        'ml_model_status': ml_status,
        'timestamp': datetime.now().isoformat()
    }
    
    if model_metadata:
        health_data['model_info'] = {
            'accuracy': model_metadata.get('accuracy', 'unknown'),
            'categories': model_metadata.get('categories', []),
            'trained_at': model_metadata.get('trained_at', 'unknown')
        }
    
    return jsonify(health_data)

@app.route('/categorize', methods=['POST'])
def categorize():
    """
    Categorize a single transaction
    Expected JSON: {"description": "transaction description"}
    """
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'error': 'missing_description',
                'message': 'Description field is required'
            }), 400
        
        description = data['description']
        category, confidence = categorize_transaction(description)
        
        response = {
            'description': description,
            'predicted_category': category,
            'confidence': round(confidence, 3),
            'prediction_method': 'ml_model' if (model is not None and vectorizer is not None and confidence > 0.3) else 'keyword_matching',
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Categorized: '{description}' -> {category} (confidence: {confidence:.3f})")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in categorize endpoint: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Internal server error occurred'
        }), 500

@app.route('/categorize/batch', methods=['POST'])
def categorize_batch():
    """
    Categorize multiple transactions
    Expected JSON: {"transactions": [{"description": "desc1"}, {"description": "desc2"}]}
    """
    try:
        data = request.get_json()
        
        if not data or 'transactions' not in data:
            return jsonify({
                'error': 'missing_transactions',
                'message': 'Transactions field is required'
            }), 400
        
        transactions = data['transactions']
        
        if not isinstance(transactions, list):
            return jsonify({
                'error': 'invalid_format',
                'message': 'Transactions must be an array'
            }), 400
        
        results = []
        
        for i, transaction in enumerate(transactions):
            if not isinstance(transaction, dict) or 'description' not in transaction:
                results.append({
                    'index': i,
                    'error': 'invalid_transaction',
                    'message': 'Each transaction must have a description field'
                })
                continue
            
            description = transaction['description']
            category, confidence = categorize_transaction(description)
            
            results.append({
                'index': i,
                'description': description,
                'predicted_category': category,
                'confidence': round(confidence, 3),
                'prediction_method': 'ml_model' if (model is not None and vectorizer is not None and confidence > 0.3) else 'keyword_matching'
            })
        
        response = {
            'results': results,
            'total_processed': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Batch categorized {len(results)} transactions")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in batch categorize endpoint: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Internal server error occurred'
        }), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """
    Get list of available categories
    """
    categories = list(CATEGORY_KEYWORDS.keys()) + ["Lainnya"]
    
    return jsonify({
        'categories': categories,
        'total_categories': len(categories)
    })

@app.route('/keywords/<category>', methods=['GET'])
def get_category_keywords(category):
    """
    Get keywords for a specific category
    """
    if category in CATEGORY_KEYWORDS:
        return jsonify({
            'category': category,
            'keywords': CATEGORY_KEYWORDS[category],
            'total_keywords': len(CATEGORY_KEYWORDS[category])
        })
    else:
        return jsonify({
            'error': 'category_not_found',
            'message': f'Category "{category}" not found',
            'available_categories': list(CATEGORY_KEYWORDS.keys())
        }), 404

if __name__ == '__main__':
    # Load models on startup
    logger.info("🚀 Starting AI Categorizer Service...")
    load_models()
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting AI Categorizer Service on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)