# Rootin 
# A Skin Wellbeing App Setup

## Quick Start

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the FastAPI**
```bash
python -m app.main
```

3. **Run web server (in another terminal)**
```bash
cd web/
python -m http.server 3000
```

4. **Open in Browser**
- Visit: http://localhost:8000 for API docs
- Visit: http://localhost:3000 for Web App
- The app works great on mobile browsers too!

## How to Use

### 1. Build Your Routine
- **Add Product to Your Routine**: Select product and add
- **Add Custom Ingredients**: Enter ingredient names like "Niacinamide, Retinol"

### 2. Analyze Your Routine
- **Check Interactions**: Find ingredient clashes, synergies, and cautions
- **Calculate Scores**: See how your routine scores across different categories

### 3. Post-Treatment Analysis
- Select a treatment (Microneedling or Chemical Peel)
- See which products to avoid and for how long

## Features

✅ **Mobile-First Design**: Works perfectly on phones  
✅ **Real-Time Analysis**: Instant feedback on ingredient interactions  
✅ **Treatment Safety**: Post-procedure product recommendations  
✅ **Scoring System**: Quantified routine effectiveness  
✅ **Custom Ingredients**: Add ingredients not in products  

## API Endpoints

- `GET /` - Main web interface
- `POST /{routine_id}/analyze/interactions` - Analyze ingredient interactions
- `POST /{routine_id}/analyze/score` - Calculate routine scores
- `POST /{routine_id}/analyze/post-treatment` - Post-treatment analysis
- `GET /api/products` - List all products
- `GET /api/ingredients` - List all ingredients

## Next Steps for Full App

1. **User Authentication**: Add user accounts and saved routines
2. **Database**: Move from CSV to PostgreSQL/SQLite
3. **AI Chat**: Add OpenAI integration for conversational analysis
4. **Push Notifications**: Treatment reminders and routine suggestions
5. **Data Logging**: Track skin changes over time
6. **Camera Integration**: Skin photo analysis
7. **Native Mobile App**: React Native or Flutter client

## Data Structure

The app uses your existing CSV structure:
- `ingredients.csv` - Ingredient database
- `products.csv` - Product catalog
- `product_ingredients.csv` - Product-ingredient relationships
- `interactions.csv` - Ingredient interaction rules
- `treatments.csv` - Available treatments
- `treatment_rules.csv` - Post-treatment safety rules

## Testing

Try these example routines:
- **Product 1 + 3**: Should show retinol/vitamin C clash
- **Product 1 + 2**: Good synergy between niacinamide and ceramides
- **Custom**: "Salicylic Acid, Niacinamide" for acne routine