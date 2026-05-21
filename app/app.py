"""
Streamlit UI for NLP Product Description Generator
"""
import streamlit as st
import pandas as pd
import os
import requests

try:
    from app.data import load_dataset
except ModuleNotFoundError:
    from data import load_dataset

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Product Description Generator",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .generated-text {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_text_api(prompt, max_tokens, temperature, top_k, top_p):
    try:
        response = requests.post(
            f"{API_URL}/generate",
            json={
                "prompt": prompt,
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p
            }
        )
        response.raise_for_status()
        return response.json().get("generated_text", "")
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return "Error generating text."

def evaluate_text_api(generated, reference):
    try:
        response = requests.post(
            f"{API_URL}/evaluate",
            json={
                "generated_text": generated,
                "reference_text": reference
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return {'bleu': 0.0, 'rouge_1': 0.0, 'rouge_2': 0.0, 'rouge_l': 0.0, 'combined': 0.0}

def main():
    st.markdown('<h1 class="main-header">🛍️ Product Description Generator</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.subheader("Generation Parameters")
        max_tokens = st.slider("Max New Tokens", 50, 300, 150, 10)
        temperature = st.slider("Temperature", 0.1, 2.0, 0.7, 0.1)
        top_k = st.slider("Top-K", 1, 100, 50, 5)
        top_p = st.slider("Top-P", 0.1, 1.0, 0.95, 0.05)
        
        st.markdown("---")
        st.subheader("Feedback Loop Settings")
        num_iterations = st.slider("Number of Iterations", 1, 10, 5, 1)
        
        st.markdown("---")
        st.subheader("Dataset")
        # Ensure path compatibility
        dataset_path = st.text_input("Dataset Path", value="amazon.csv.zip")
        load_data = st.button("Load Dataset", type="primary")
        
        if not os.path.exists(dataset_path):
            st.warning(f"⚠️ Dataset file not found: {dataset_path}")
            
        # API Health Check
        st.markdown("---")
        st.subheader("System Status")
        try:
            health = requests.get(f"{API_URL}/health", timeout=2)
            if health.status_code == 200:
                st.success("API: Online 🟢")
            else:
                st.error("API: Error 🔴")
        except:
            st.error("API: Offline 🔴")
    
    tab1, tab2, tab3 = st.tabs(["📝 Single Product", "📊 Batch Processing", "📈 About"])
    
    with tab1:
        st.header("Generate Description for Single Product")
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input(
                "Product Name",
                value="Wayona Nylon Braided USB to Lightning Fast Charging Cable"
            )
        
        with col2:
            product_description = st.text_area(
                "Product Description",
                value="Fast charging and data sync cable compatible with iPhone devices",
                height=100
            )
        
        reference_text = st.text_area(
            "Reference Text (for evaluation)",
            value="Great cable, fast charging, durable build quality",
            height=100
        )
        
        if st.button("Generate Description", type="primary", use_container_width=True):
            if not product_name or not product_description:
                st.error("Please fill in both Product Name and Product Description")
            else:
                prompt = f"Product Name: {product_name}\nDescription: {product_description}\nGenerate a compelling product description:"
                
                with st.spinner("Generating description from API..."):
                    generated_text = generate_text_api(prompt, max_tokens, temperature, top_k, top_p)
                
                st.markdown("### Generated Description")
                st.markdown(f'<div class="generated-text">{generated_text}</div>', unsafe_allow_html=True)
                
                if reference_text:
                    with st.spinner("Calculating evaluation metrics via API..."):
                        reward_scores = evaluate_text_api(generated_text, reference_text)
                    
                    st.markdown("### Evaluation Metrics")
                    metric_cols = st.columns(5)
                    metric_cols[0].metric("BLEU Score", f"{reward_scores.get('bleu', 0):.4f}")
                    metric_cols[1].metric("ROUGE-1", f"{reward_scores.get('rouge_1', 0):.4f}")
                    metric_cols[2].metric("ROUGE-2", f"{reward_scores.get('rouge_2', 0):.4f}")
                    metric_cols[3].metric("ROUGE-L", f"{reward_scores.get('rouge_l', 0):.4f}")
                    metric_cols[4].metric("Combined", f"{reward_scores.get('combined', 0):.4f}")
    
    with tab2:
        st.header("Batch Processing with Iterative Feedback")
        if 'dataset' not in st.session_state:
            st.session_state.dataset = None
        
        if load_data or st.session_state.dataset is not None:
            if st.session_state.dataset is None and os.path.exists(dataset_path):
                with st.spinner("Loading dataset..."):
                    df = load_dataset(dataset_path)
                    if df is not None and not df.empty:
                        st.session_state.dataset = df
                        st.success(f"✅ Dataset loaded successfully! ({len(df)} products)")
                    else:
                        st.error("❌ Failed to load dataset")
            
            if st.session_state.dataset is not None:
                df = st.session_state.dataset
                required_columns = ['product_name', 'about_product', 'review_content']
                if all(col in df.columns for col in required_columns):
                    product_options = df['product_name'].tolist()
                    num_products = min(10, len(df))
                    selected_product_idx = st.selectbox(
                        "Select Product",
                        range(num_products),
                        format_func=lambda x: f"Product {x+1}: {product_options[x][:50]}..."
                    )
                    
                    if st.button("Process Product", type="primary"):
                        row = df.iloc[selected_product_idx]
                        product_name = row.get('product_name', 'N/A')
                        description = row.get('about_product', 'N/A')
                        reference_text = row.get('review_content', 'N/A')
                        
                        prompt = f"Product Name: {product_name}\nDescription: {description}\nGenerate a compelling product description:"
                        
                        st.markdown("### Iterative Feedback Loop")
                        st.markdown(f"**Product:** {product_name}")
                        manual_scores = []
                        results_container = st.container()
                        
                        for i in range(num_iterations):
                            with results_container:
                                st.markdown(f"#### Iteration {i + 1}")
                                with st.spinner(f"Generating text for iteration {i + 1}..."):
                                    generated_text = generate_text_api(prompt, max_tokens, temperature, top_k, top_p)
                                
                                st.markdown(f'<div class="generated-text">{generated_text}</div>', unsafe_allow_html=True)
                                
                                if not pd.isna(reference_text) and reference_text.strip():
                                    reward_scores = evaluate_text_api(generated_text, reference_text)
                                    cols = st.columns(5)
                                    cols[0].metric("BLEU", f"{reward_scores.get('bleu', 0):.4f}")
                                    cols[1].metric("ROUGE-1", f"{reward_scores.get('rouge_1', 0):.4f}")
                                    cols[2].metric("ROUGE-2", f"{reward_scores.get('rouge_2', 0):.4f}")
                                    cols[3].metric("ROUGE-L", f"{reward_scores.get('rouge_l', 0):.4f}")
                                    cols[4].metric("Combined", f"{reward_scores.get('combined', 0):.4f}")
                                else:
                                    reward_scores = {'combined': 0.0}
                                
                                manual_score = st.slider(f"Rate iteration {i + 1} (1-10)", 1, 10, 5, key=f"score_{selected_product_idx}_{i}")
                                manual_scores.append(manual_score)
                                combined_reward = (0.7 * manual_score / 10) + (0.3 * reward_scores.get('combined', 0))
                                st.metric("Combined Reward", f"{combined_reward:.4f}")
                                st.markdown("---")
    
    with tab3:
        st.header("About This Project")
        st.markdown("This application uses a FastAPI backend powered by GPT-2 to generate compelling product descriptions. It monitors API metrics with Prometheus and runs in a cloud-native architecture.")

if __name__ == "__main__":
    main()
