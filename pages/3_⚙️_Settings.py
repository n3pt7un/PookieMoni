import streamlit as st
import pandas as pd
from config_utils import (
    get_categories, 
    get_stores_for_category, 
    get_keywords_for_category,
    add_category,
    remove_category,
    rename_category,
    add_store_to_category,
    remove_store_from_category,
    add_keyword_to_category,
    remove_keyword_from_category,
    update_settings,
    config_manager
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
)

def main():
    st.title("⚙️ Configuration Settings")
    
    if not st.user.is_logged_in:
        st.warning("Please log in from the main page to access settings.")
        return
    
    # Quick overview
    st.markdown("""
    Welcome to the Configuration Settings! Here you can:
    - **Manage categories** for your expenses
    - **Add and remove stores** for each category
    - **Configure keywords** for automatic categorization
    - **Test auto-categorization** with sample store names
    """)
    
    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔧 General", "📂 Categories", "🏪 Stores", "🏷️ Keywords", "❓ Help"])
    
    with tab1:
        general_settings()
    
    with tab2:
        category_management()
    
    with tab3:
        store_management()
    
    with tab4:
        keyword_management()
    
    with tab5:
        help_documentation()

def general_settings():
    """General application settings."""
    st.header("General Settings")
    
    # Current settings
    current_default = config_manager.get_default_category()
    current_auto_categorize = config_manager.is_auto_categorize_enabled()
    
    st.subheader("Current Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Default Category", current_default)
    
    with col2:
        st.metric("Auto-categorization", "Enabled" if current_auto_categorize else "Disabled")
    
    st.subheader("Update Settings")
    
    with st.form("general_settings_form"):
        categories = get_categories()
        
        new_default = st.selectbox(
            "Default Category",
            options=categories,
            index=categories.index(current_default) if current_default in categories else 0,
            help="Category to use when auto-categorization fails"
        )
        
        new_auto_categorize = st.checkbox(
            "Enable Auto-categorization",
            value=current_auto_categorize,
            help="Automatically suggest categories based on store names and keywords"
        )
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.form_submit_button("Update Settings", type="primary"):
                if update_settings(new_default, new_auto_categorize):
                    st.success("Settings updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update settings.")
        
        with col2:
            if st.form_submit_button("Reset to Defaults"):
                if update_settings("Other", True):
                    st.success("Settings reset to defaults!")
                    st.rerun()
                else:
                    st.error("Failed to reset settings.")

def category_management():
    """Manage expense categories."""
    st.header("Category Management")
    
    categories = get_categories()
    
    # Display current categories
    st.subheader("Current Categories")
    if categories:
        # Create a DataFrame for better display
        category_data = []
        for cat in categories:
            stores_count = len(get_stores_for_category(cat))
            keywords_count = len(get_keywords_for_category(cat))
            category_data.append({
                "Category": cat,
                "Stores": stores_count,
                "Keywords": keywords_count
            })
        
        df = pd.DataFrame(category_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No categories found.")
    
    # Add new category
    st.subheader("Add New Category")
    with st.form("add_category_form"):
        new_category = st.text_input("Category Name", placeholder="Enter new category name")
        
        if st.form_submit_button("Add Category", type="primary"):
            if new_category:
                if new_category not in categories:
                    if add_category(new_category):
                        st.success(f"Category '{new_category}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add category.")
                else:
                    st.error("Category already exists.")
            else:
                st.error("Please enter a category name.")
    
    # Remove category
    st.subheader("Remove Category")
    if categories:
        with st.form("remove_category_form"):
            category_to_remove = st.selectbox(
                "Select Category to Remove",
                options=categories,
                help="⚠️ This will permanently delete the category and all its stores/keywords"
            )
            
            confirm_removal = st.checkbox("I confirm I want to delete this category")
            
            if st.form_submit_button("Remove Category", type="secondary"):
                if confirm_removal:
                    if remove_category(category_to_remove):
                        st.success(f"Category '{category_to_remove}' removed successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to remove category.")
                else:
                    st.error("Please confirm the removal by checking the box.")
    
    # Rename category
    st.subheader("Rename Category")
    if categories:
        with st.form("rename_category_form"):
            old_name = st.selectbox("Category to Rename", options=categories)
            new_name = st.text_input("New Name", placeholder="Enter new category name")
            
            if st.form_submit_button("Rename Category"):
                if new_name:
                    if new_name not in categories:
                        if rename_category(old_name, new_name):
                            st.success(f"Category '{old_name}' renamed to '{new_name}' successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to rename category.")
                    else:
                        st.error("A category with this name already exists.")
                else:
                    st.error("Please enter a new category name.")

def store_management():
    """Manage stores for each category."""
    st.header("Store Management")
    
    categories = get_categories()
    
    if not categories:
        st.warning("No categories found. Please add categories first.")
        return
    
    # Select category to manage
    selected_category = st.selectbox("Select Category to Manage", options=categories)
    
    if selected_category:
        stores = get_stores_for_category(selected_category)
        
        st.subheader(f"Stores in '{selected_category}' Category")
        
        if stores:
            # Display stores in a more interactive way
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{len(stores)} stores configured:**")
                
                # Create columns for better layout
                num_cols = 3
                cols = st.columns(num_cols)
                
                for i, store in enumerate(stores):
                    with cols[i % num_cols]:
                        st.write(f"• {store}")
            
            with col2:
                st.write("**Remove Store:**")
                store_to_remove = st.selectbox(
                    "Select store to remove",
                    options=stores,
                    key=f"remove_store_{selected_category}",
                    label_visibility="collapsed"
                )
                
                if st.button("Remove", key=f"remove_btn_{selected_category}"):
                    if remove_store_from_category(selected_category, store_to_remove):
                        st.success(f"Store '{store_to_remove}' removed!")
                        st.rerun()
                    else:
                        st.error("Failed to remove store.")
        else:
            st.info(f"No stores configured for '{selected_category}' category.")
        
        # Add new store
        st.subheader("Add New Store")
        with st.form(f"add_store_form_{selected_category}"):
            new_store = st.text_input("Store Name", placeholder="Enter store name")
            
            if st.form_submit_button("Add Store", type="primary"):
                if new_store:
                    if new_store not in stores:
                        if add_store_to_category(selected_category, new_store):
                            st.success(f"Store '{new_store}' added to '{selected_category}' category!")
                            st.rerun()
                        else:
                            st.error("Failed to add store.")
                    else:
                        st.error("Store already exists in this category.")
                else:
                    st.error("Please enter a store name.")

def keyword_management():
    """Manage keywords for each category."""
    st.header("Keyword Management")
    
    categories = get_categories()
    
    if not categories:
        st.warning("No categories found. Please add categories first.")
        return
    
    # Select category to manage
    selected_category = st.selectbox("Select Category to Manage", options=categories, key="keyword_category")
    
    if selected_category:
        keywords = get_keywords_for_category(selected_category)
        
        st.subheader(f"Keywords for '{selected_category}' Category")
        
        if keywords:
            # Display keywords
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{len(keywords)} keywords configured:**")
                
                # Display keywords as tags
                keyword_tags = " • ".join([f"`{keyword}`" for keyword in keywords])
                st.markdown(keyword_tags)
                
                st.info("💡 These keywords are used to automatically categorize stores. For example, if a store name contains 'pizza', it will be suggested for the Food category.")
            
            with col2:
                st.write("**Remove Keyword:**")
                keyword_to_remove = st.selectbox(
                    "Select keyword to remove",
                    options=keywords,
                    key=f"remove_keyword_{selected_category}",
                    label_visibility="collapsed"
                )
                
                if st.button("Remove", key=f"remove_keyword_btn_{selected_category}"):
                    if remove_keyword_from_category(selected_category, keyword_to_remove):
                        st.success(f"Keyword '{keyword_to_remove}' removed!")
                        st.rerun()
                    else:
                        st.error("Failed to remove keyword.")
        else:
            st.info(f"No keywords configured for '{selected_category}' category.")
        
        # Add new keyword
        st.subheader("Add New Keyword")
        with st.form(f"add_keyword_form_{selected_category}"):
            new_keyword = st.text_input(
                "Keyword", 
                placeholder="Enter keyword (e.g., 'pizza', 'fuel', 'clothes')",
                help="Keywords are used to automatically categorize stores based on their names"
            )
            
            if st.form_submit_button("Add Keyword", type="primary"):
                if new_keyword:
                    if new_keyword.lower() not in [k.lower() for k in keywords]:
                        if add_keyword_to_category(selected_category, new_keyword):
                            st.success(f"Keyword '{new_keyword}' added to '{selected_category}' category!")
                            st.rerun()
                        else:
                            st.error("Failed to add keyword.")
                    else:
                        st.error("Keyword already exists in this category.")
                else:
                    st.error("Please enter a keyword.")
        
        # Test auto-categorization
        st.subheader("Test Auto-categorization")
        with st.form(f"test_categorization_{selected_category}"):
            test_store = st.text_input("Test Store Name", placeholder="Enter a store name to test categorization")
            
            if st.form_submit_button("Test Categorization"):
                if test_store:
                    from config_utils import auto_categorize_store
                    predicted_category = auto_categorize_store(test_store)
                    
                    if predicted_category == selected_category:
                        st.success(f"✅ '{test_store}' would be categorized as '{predicted_category}'")
                    else:
                        st.info(f"ℹ️ '{test_store}' would be categorized as '{predicted_category}'")
                        if predicted_category != selected_category:
                            st.write(f"💡 To make it categorize as '{selected_category}', add relevant keywords.")
                else:
                    st.error("Please enter a store name to test.")

def help_documentation():
    """Help and documentation for the settings interface."""
    st.header("❓ Help & Documentation")
    
    st.markdown("""
    ## How to Use the Settings Interface
    
    This interface allows you to customize how your Personal Finance Tracker categorizes expenses automatically.
    
    ### 🔧 General Settings
    - **Default Category**: Used when auto-categorization can't determine the right category
    - **Auto-categorization**: Enable/disable the automatic suggestion feature
    
    ### 📂 Categories
    Categories help organize your expenses. Each category can have:
    - **Stores**: Specific store names that belong to this category
    - **Keywords**: Words that help identify stores for this category
    
    **Examples of good categories:**
    - `Food` - restaurants, groceries, takeout
    - `Transport` - gas stations, public transport, parking
    - `Shopping` - clothing, electronics, general retail
    - `Bills` - utilities, insurance, subscriptions
    
    ### 🏪 Stores
    Stores are specific business names that you visit regularly. When you add a store:
    - It appears in the dropdown when adding expenses
    - It's automatically categorized correctly in the future
    
    **Examples:**
    - `McDonald's` → Food category
    - `Shell` → Transport category
    - `Amazon` → Shopping category
    
    ### 🏷️ Keywords
    Keywords help the system automatically categorize new stores you haven't seen before.
    
    **How keywords work:**
    - If you enter `Joe's Pizza House`, the keyword `pizza` will suggest `Food` category
    - If you enter `Downtown Parking Garage`, the keyword `parking` will suggest `Transport` category
    
    **Good keyword examples:**
    - Food: `pizza`, `burger`, `coffee`, `restaurant`, `grocery`
    - Transport: `gas`, `fuel`, `parking`, `taxi`, `bus`
    - Shopping: `store`, `mall`, `clothes`, `electronics`
    
    ### 💡 Tips for Best Results
    
    1. **Start with common stores**: Add stores you visit frequently first
    2. **Use descriptive keywords**: Think about words that commonly appear in store names
    3. **Test your setup**: Use the test feature to see how well your keywords work
    4. **Keep it simple**: Don't add too many similar keywords
    5. **Review regularly**: Check if new stores are being categorized correctly
    
    ### 🔄 How Auto-Categorization Works
    
    When you enter a store name, the system:
    1. **Checks exact matches**: Looks for the exact store name in your configured stores
    2. **Checks keywords**: Looks for keywords in the store name
    3. **Suggests category**: Picks the best matching category
    4. **Falls back to default**: Uses your default category if no match is found
    
    ### 📊 Example Workflow
    
    1. **Add a category**: Create "Entertainment" category
    2. **Add stores**: Add "Cinema City", "Netflix", "Spotify"
    3. **Add keywords**: Add "movie", "music", "entertainment"
    4. **Test**: Try "Downtown Movie Theater" - should suggest "Entertainment"
    5. **Use**: Next time you add an expense at "AMC Theaters", it will auto-suggest "Entertainment"
    
    ### 🚨 Troubleshooting
    
    **Store not auto-categorizing correctly?**
    - Check if there are relevant keywords for that store type
    - Add the store manually to the correct category
    - Add more specific keywords
    
    **Too many stores in wrong category?**
    - Review your keywords - they might be too broad
    - Remove or modify overly general keywords
    - Use the test feature to verify changes
    
    **Settings not saving?**
    - Make sure you have write permissions to the config file
    - Check if the config.toml file exists in your project directory
    - Restart the app if changes don't appear
    """)

if __name__ == "__main__":
    main() 