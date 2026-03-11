import streamlit as st
from groq import Groq

# ── Page Setup ─────────────────────────────────────────────
st.set_page_config(page_title="AI Recipe Generator", page_icon="🍳", layout="centered")
st.title("🍳 AI Recipe Generator")
st.markdown("Enter your ingredients and get a **complete recipe** with nutrition info instantly!")

# ── Sidebar: API Key + Preferences ────────────────────────
with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_xxx")
    st.markdown("---")
    st.header("⚙️ Preferences")
    servings  = st.number_input("👥 Servings", min_value=1, max_value=10, value=2)
    cook_time = st.selectbox("⏱️ Max Cooking Time", ["15 mins", "30 mins", "45 mins", "1 hour", "No limit"])
    difficulty = st.selectbox("📊 Difficulty Level", ["Beginner", "Intermediate", "Chef Level"])

# ── Main Inputs ────────────────────────────────────────────
st.markdown("---")
ingredients = st.text_input("🥗 Enter Ingredients (comma separated)", placeholder="e.g. tomato, egg, onion, curry leaf")
cuisine     = st.selectbox("🌍 Cuisine Type", ["Indian", "Italian", "Chinese", "Mexican", "Continental", "Any"])
meal_type   = st.selectbox("🍽️ Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack", "Dessert"])

# ── Show current selections as summary ─────────────────────
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Servings",   servings)
c2.metric("⏱️ Cook Time",  cook_time)
c3.metric("📊 Difficulty", difficulty)
c4.metric("🌍 Cuisine",    cuisine)
st.markdown("---")

# ── Session State: store last 3 recipes without database ──
# st.session_state works like a temporary memory during the app session
if "recipe_history" not in st.session_state:
    st.session_state.recipe_history = []   # Empty list to store past recipes

# ── Generate Button ────────────────────────────────────────
if st.button("✨ Generate Recipe", use_container_width=True):

    # Validation checks
    if not api_key.strip():
        st.error("❌ Please enter your Groq API key in the sidebar.")
    elif not ingredients.strip():
        st.warning("⚠️ Please enter at least one ingredient.")
    else:
        # Build a rich prompt with all user preferences
        prompt = f"""You are a professional chef. Create a {difficulty} level {cuisine} {meal_type} recipe for {servings} servings.
Ingredients available: {ingredients}
Maximum cooking time: {cook_time}

Provide:
1. Recipe Name
2. Prep Time and Cook Time
3. Ingredients with exact quantities for {servings} servings
4. Step by Step Instructions
5. Nutrition Info (calories, protein, carbs per serving)
6. One Pro Chef Tip

Be practical and beginner friendly."""

        with st.spinner("🤖 Chef AI is preparing your recipe..."):
            try:
                client   = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model    = "llama-3.3-70b-versatile",
                    messages = [
                        {"role": "system", "content": "You are an expert chef who gives clear, practical recipes with nutrition information."},
                        {"role": "user",   "content": prompt}
                    ],
                    max_tokens  = 700,
                    temperature = 0.7
                )
                recipe = response.choices[0].message.content

                # Save to session history (keep last 3 only)
                st.session_state.recipe_history.insert(0, {
                    "title":      f"{cuisine} {meal_type} with {ingredients[:30]}",
                    "recipe":     recipe,
                    "servings":   servings,
                    "difficulty": difficulty
                })
                st.session_state.recipe_history = st.session_state.recipe_history[:3]

                # Show the recipe
                st.success("✅ Recipe ready!")
                st.markdown("---")
                st.markdown(recipe)

                # Download button to save recipe as text file
                st.download_button(
                    label     = "⬇️ Download Recipe",
                    data      = recipe,
                    file_name = f"{cuisine}_{meal_type}_recipe.txt",
                    mime      = "text/plain"
                )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ── Recipe History (last 3 recipes this session) ──────────
if st.session_state.recipe_history:
    st.markdown("---")
    st.subheader("🕐 Recent Recipes This Session")
    for i, item in enumerate(st.session_state.recipe_history):
        with st.expander(f"Recipe {i+1}: {item['title']} | {item['difficulty']} | {item['servings']} servings"):
            st.markdown(item["recipe"])
