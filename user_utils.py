"""
User management utilities for multi-user finance tracking.

This module provides functions to manage user sessions and data access.
"""

import streamlit as st
from typing import List, Tuple
import pandas as pd
from streamlit_gsheets import GSheetsConnection


def get_user_list() -> List[Tuple[str, str]]:
    """
    Get list of available users.
    
    Returns:
        List of tuples (user_id, user_name)
    """
    try:
        user1_name = st.secrets["users"]["user1_name"]
        user2_name = st.secrets["users"]["user2_name"]
        return [
            ("user1", user1_name),
            ("user2", user2_name),
            ("shared", "Shared")
        ]
    except Exception:
        return [
            ("user1", "User 1"),
            ("user2", "User 2"),
            ("shared", "Shared")
        ]


def get_current_user() -> str:
    """
    Get the currently selected user from session state.
    
    Returns:
        User ID (user1, user2, or shared)
    """
    if "current_user" not in st.session_state:
        st.session_state.current_user = "user1"
    return st.session_state.current_user


def set_current_user(user_id: str) -> None:
    """
    Set the current user in session state.
    
    Args:
        user_id: User ID to set
    """
    st.session_state.current_user = user_id


def get_worksheet_names(user_id: str) -> dict:
    """
    Get worksheet names for a specific user.
    
    Args:
        user_id: User ID (user1, user2, or shared)
        
    Returns:
        Dictionary with worksheet names for expenses, income, recurrings, investments
    """
    try:
        worksheets = st.secrets["connections"]["gsheets"]["worksheets"]
        return {
            "expenses": worksheets[f"expenses_{user_id}"],
            "income": worksheets[f"income_{user_id}"],
            "recurrings": worksheets[f"recurrings_{user_id}"],
            "investments": worksheets[f"investments_{user_id}"]
        }
    except Exception as e:
        # Fallback to default naming
        suffix = user_id if user_id == "shared" else ("taras" if user_id == "user1" else "dana")
        return {
            "expenses": f"expenses_{suffix}",
            "income": f"income_{suffix}",
            "recurrings": f"recurrings_{suffix}",
            "investments": f"investments_{suffix}"
        }


def get_user_and_shared_data(conn: GSheetsConnection, user_id: str, data_type: str) -> pd.DataFrame:
    """
    Get combined data for user and shared worksheets.
    
    Args:
        conn: Google Sheets connection
        user_id: User ID (user1 or user2)
        data_type: Type of data ('expenses', 'income', 'recurrings', 'investments')
        
    Returns:
        Combined DataFrame with user and shared data
    """
    dfs = []
    
    # Get user data
    try:
        user_worksheets = get_worksheet_names(user_id)
        user_df = conn.read(worksheet=user_worksheets[data_type], ttl=0)
        if not user_df.empty:
            user_df['_source'] = 'personal'
            dfs.append(user_df)
    except Exception as e:
        print(f"Could not load {data_type} for {user_id}: {e}")
    
    # Get shared data
    try:
        shared_worksheets = get_worksheet_names("shared")
        shared_df = conn.read(worksheet=shared_worksheets[data_type], ttl=0)
        if not shared_df.empty:
            shared_df['_source'] = 'shared'
            dfs.append(shared_df)
    except Exception as e:
        print(f"Could not load shared {data_type}: {e}")
    
    # Combine dataframes
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()


def get_user_display_name(user_id: str) -> str:
    """
    Get display name for a user ID.
    
    Args:
        user_id: User ID
        
    Returns:
        Display name
    """
    users = dict(get_user_list())
    return users.get(user_id, user_id.capitalize())


def render_user_selector() -> None:
    """
    Render user selection UI in the sidebar.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Active User")
    
    users = get_user_list()
    user_options = {user_id: name for user_id, name in users}
    
    current = get_current_user()
    current_display = user_options.get(current, "User 1")
    
    # Create radio buttons for user selection
    selected_display = st.sidebar.radio(
        "Select user to view:",
        options=list(user_options.values()),
        index=list(user_options.values()).index(current_display),
        label_visibility="collapsed"
    )
    
    # Find user_id from display name
    selected_id = [uid for uid, name in user_options.items() if name == selected_display][0]
    
    if selected_id != current:
        set_current_user(selected_id)
        st.rerun()
    
    # Show what user can see
    if selected_id in ["user1", "user2"]:
        st.sidebar.caption(f"📊 Viewing: Personal + Shared data")
    else:
        st.sidebar.caption(f"📊 Viewing: Shared data only")
    
    st.sidebar.markdown("---")

