# 🍽️ Plate Pal
> **Where AI meets your Appetite**

An AI-powered recipe recommendation system built with Streamlit that matches personalised nutritional goals to recipes using cosine similarity — with smart health-aware filtering for medical conditions.

---

## ✨ Features

- 🔍 **Personalised Recommendations** — cosine similarity matching against your daily nutritional targets
- 🩺 **Health-Aware Filtering** — auto-filters recipes for high blood sugar (≥126 mg/dL) or high blood pressure (≥130 mmHg)
- 📂 **CSV Upload** — works with any compatible recipe dataset
- 🏷️ **Nutritional Badges** — displays calories, fat, carbs, protein, and match % per recipe
- ⬇️ **Export Results** — download top recommendations as a CSV
- ⚡ **Cached Loading** — dataset is cached for fast repeated interactions
- 👤 **Session-based Sign In** — persistent user profile across interactions

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | Streamlit |
| Data Processing | Pandas |
| ML / Similarity | scikit-learn |
| Language | Python 3.8+ |

---

## 📁 Project Structure

```
plate_pal/
├── plate_pal_app.py        # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── Recipe Dataset.csv      # Your recipe dataset (user-supplied)
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/plate-pal.git
cd plate-pal
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
streamlit run plate_pal_app.py
```

---

## 📦 Requirements

`requirements.txt`:

```
streamlit>=1.28.0
pandas>=1.5.0
scikit-learn>=1.2.0
```

---

## 📂 Dataset Format

Upload a CSV file with the following required columns:

| Column Name | Description |
|-------------|-------------|
| `Name` | Recipe name |
| `Calories` | Caloric content (kcal) |
| `FatContent` | Fat in grams |
| `CarbohydrateContent` | Carbohydrates in grams |
| `ProteinContent` | Protein in grams |
| `RecipeInstructions` | Step-by-step cooking instructions |

---

## 🚀 Usage

1. **Sign In** — enter your name in the sidebar and click *Sign In*
2. **Health Profile** — set your age, blood sugar level, and blood pressure
3. **Nutritional Goals** — input your daily targets for calories, fat, carbs, and protein
4. **Upload Dataset** — upload your Recipe Dataset CSV
5. **Get Recommendations** — click the button to view your top personalised recipes
6. **Export** — optionally download results as a CSV file

---

## 🧠 How It Works

### Cosine Similarity

Both the user's nutritional targets and the dataset values are normalised using the **dataset's own min/max range** (same scale), then cosine similarity is computed between the user vector and every recipe vector. The top-N closest recipes are returned.

```
user_norm[i] = (user_value[i] - dataset_min[i]) / (dataset_max[i] - dataset_min[i])
```

> ⚠️ This is the critical fix over naive implementations — normalising the user against the dataset scale (not against themselves) ensures meaningful similarity scores.

### Health Filtering

| Condition | Filter Applied |
|-----------|---------------|
| Sugar ≥ 126 mg/dL | Removes recipes above 60th percentile for carbs & calories |
| Blood Pressure ≥ 130 mmHg | Removes recipes above 60th percentile for fat content |

---

## ⚠️ Known Limitations

- Blood sugar and BP thresholds are heuristic — **not a substitute for medical advice**
- Sodium is not used (not in base dataset); fat is used as a proxy for BP filtering
- Best results with large, diverse datasets (1,000+ recipes)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute with attribution.

---

<p align="center">Built with ❤️ using Streamlit & scikit-learn</p>
