import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

st.set_page_config(page_title="Iris Species Predictor", layout="wide")
st.title("🌸 Iris Flower Classification Dashboard")
st.markdown("This app uses Machine Learning to predict Iris species and visualize flower data.")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv('Iris.csv')
    return df

df = load_data()
X = df.drop(['Id', 'Species'], axis=1)
y = df['Species']

# --- TRAIN MODEL ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# --- NAVIGATION TABS  ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dataset View", "📈 Visualizations", "🧠 Model Performance", "🔮 Species Predictor"])

with tab1:
    st.header("Raw Dataset")
    st.write(df.head(10))
    st.write("Statistics:", df.describe())

with tab2:
    st.header("Exploratory Data Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Petal Length vs Width")
        fig1, ax1 = plt.subplots()
        sns.scatterplot(data=df, x='PetalLengthCm', y='PetalWidthCm', hue='Species', ax=ax1)
        st.pyplot(fig1)
        
    with col2:
        st.subheader("Feature Distributions")
        fig2, ax2 = plt.subplots()
        sns.boxplot(data=df, x='Species', y='SepalLengthCm', ax=ax2)
        st.pyplot(fig2)

with tab3:
    st.header("Model Evaluation")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    st.success(f"Model Accuracy: {acc*100:.2f}%")
    
    st.subheader("Confusion Matrix")
    cm = confusion_matrix(y_test, y_pred)
    fig3, ax3 = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=model.classes_, yticklabels=model.classes_, ax=ax3)
    st.pyplot(fig3)

with tab4:
    st.header("Predict Species from Measurements")
    st.info("Adjust the sliders below to see the prediction change in real-time!")
    
    c1, c2 = st.columns(2)
    sl = c1.slider("Sepal Length (cm)", 4.0, 8.0, 5.8)
    sw = c1.slider("Sepal Width (cm)", 2.0, 4.5, 3.0)
    pl = c2.slider("Petal Length (cm)", 1.0, 7.0, 4.3)
    pw = c2.slider("Petal Width (cm)", 0.1, 2.5, 1.3)
    
    input_data = pd.DataFrame([[sl, sw, pl, pw]], 
                              columns=['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'])
    
    prediction = model.predict(input_data)
    
    # 
    st.subheader("Prediction Result:")
    st.success(f"The flower is likely an **{prediction[0]}**")