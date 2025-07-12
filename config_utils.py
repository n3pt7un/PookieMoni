"""
Configuration utilities for the Personal Finance Tracker.

This module provides functions to load and use the TOML configuration file
for managing categories and store names.
"""

import toml
import os
from typing import Dict, List, Optional
import re


class ConfigManager:
    """Manages the configuration for the Personal Finance Tracker."""
    
    def __init__(self, config_file: str = "config.toml"):
        """
        Initialize the ConfigManager with a configuration file.
        
        Args:
            config_file: Path to the TOML configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load the configuration from the TOML file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return toml.load(f)
            else:
                # Return default configuration if file doesn't exist
                return self._get_default_config()
        except Exception as e:
            print(f"Error loading config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return a default configuration if the file is missing."""
        return {
            "settings": {
                "default_category": "Other",
                "auto_categorize": True
            },
            "categories": {
                "Food": {
                    "stores": ["Supermarket", "Restaurant", "Café"],
                    "keywords": ["food", "restaurant", "cafe"]
                },
                "Transport": {
                    "stores": ["Gas Station", "Uber", "Taxi"],
                    "keywords": ["fuel", "taxi", "transport"]
                },
                "Shopping": {
                    "stores": ["Amazon", "Clothing Store"],
                    "keywords": ["shopping", "clothes"]
                },
                "Bills": {
                    "stores": ["Electricity Company", "Bank"],
                    "keywords": ["bill", "utility"]
                },
                "Fun": {
                    "stores": ["Cinema", "Gym"],
                    "keywords": ["entertainment", "gym"]
                },
                "Health": {
                    "stores": ["Pharmacy", "Hospital"],
                    "keywords": ["health", "medical"]
                },
                "Other": {
                    "stores": ["Post Office", "Miscellaneous"],
                    "keywords": ["other", "misc"]
                }
            }
        }
    
    def get_categories(self) -> List[str]:
        """Get a list of all available categories."""
        return list(self.config.get("categories", {}).keys())
    
    def get_stores_for_category(self, category: str) -> List[str]:
        """
        Get all stores for a specific category.
        
        Args:
            category: The category name
            
        Returns:
            List of store names for the category
        """
        categories = self.config.get("categories", {})
        if category in categories:
            return categories[category].get("stores", [])
        return []
    
    def get_all_stores(self) -> List[str]:
        """Get all store names from all categories."""
        all_stores = []
        for category in self.get_categories():
            all_stores.extend(self.get_stores_for_category(category))
        return sorted(list(set(all_stores)))  # Remove duplicates and sort
    
    def auto_categorize_store(self, store_name: str) -> str:
        """
        Automatically categorize a store based on its name.
        
        Args:
            store_name: The name of the store
            
        Returns:
            The predicted category name
        """
        if not self.config.get("settings", {}).get("auto_categorize", True):
            return self.config.get("settings", {}).get("default_category", "Other")
        
        store_name_lower = store_name.lower()
        
        # First, try exact match with store names
        for category, data in self.config.get("categories", {}).items():
            stores = [store.lower() for store in data.get("stores", [])]
            if store_name_lower in stores:
                return category
        
        # Then, try keyword matching
        for category, data in self.config.get("categories", {}).items():
            keywords = data.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in store_name_lower:
                    return category
        
        # Return default category if no match found
        return self.config.get("settings", {}).get("default_category", "Other")
    
    def add_store_to_category(self, category: str, store_name: str) -> bool:
        """
        Add a new store to a category and save the configuration.
        
        Args:
            category: The category to add the store to
            store_name: The name of the store to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if category not in self.config.get("categories", {}):
                return False
            
            if store_name not in self.config["categories"][category]["stores"]:
                self.config["categories"][category]["stores"].append(store_name)
                self.config["categories"][category]["stores"].sort()
                self._save_config()
                return True
            return False
        except Exception as e:
            print(f"Error adding store to category: {e}")
            return False
    
    def remove_store_from_category(self, category: str, store_name: str) -> bool:
        """
        Remove a store from a category and save the configuration.
        
        Args:
            category: The category to remove the store from
            store_name: The name of the store to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if category in self.config.get("categories", {}):
                if store_name in self.config["categories"][category]["stores"]:
                    self.config["categories"][category]["stores"].remove(store_name)
                    self._save_config()
                    return True
            return False
        except Exception as e:
            print(f"Error removing store from category: {e}")
            return False
    
    def _save_config(self) -> None:
        """Save the current configuration to the TOML file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                toml.dump(self.config, f)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def get_default_category(self) -> str:
        """Get the default category."""
        return self.config.get("settings", {}).get("default_category", "Other")
    
    def is_auto_categorize_enabled(self) -> bool:
        """Check if auto-categorization is enabled."""
        return self.config.get("settings", {}).get("auto_categorize", True)
    
    def add_category(self, category_name: str) -> bool:
        """
        Add a new category to the configuration.
        
        Args:
            category_name: Name of the new category
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if category_name not in self.config.get("categories", {}):
                self.config["categories"][category_name] = {
                    "stores": [],
                    "keywords": []
                }
                self._save_config()
                return True
            return False
        except Exception as e:
            print(f"Error adding category: {e}")
            return False
    
    def remove_category(self, category_name: str) -> bool:
        """
        Remove a category from the configuration.
        
        Args:
            category_name: Name of the category to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if category_name in self.config.get("categories", {}):
                del self.config["categories"][category_name]
                self._save_config()
                return True
            return False
        except Exception as e:
            print(f"Error removing category: {e}")
            return False
    
    def get_keywords_for_category(self, category: str) -> List[str]:
        """
        Get all keywords for a specific category.
        
        Args:
            category: The category name
            
        Returns:
            List of keywords for the category
        """
        categories = self.config.get("categories", {})
        if category in categories:
            return categories[category].get("keywords", [])
        return []
    
    def add_keyword_to_category(self, category: str, keyword: str) -> bool:
        """
        Add a keyword to a category.
        
        Args:
            category: The category to add the keyword to
            keyword: The keyword to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if category not in self.config.get("categories", {}):
                return False
            
            if keyword.lower() not in [k.lower() for k in self.config["categories"][category]["keywords"]]:
                self.config["categories"][category]["keywords"].append(keyword.lower())
                self.config["categories"][category]["keywords"].sort()
                self._save_config()
                return True
            return False
        except Exception as e:
            print(f"Error adding keyword to category: {e}")
            return False
    
    def remove_keyword_from_category(self, category: str, keyword: str) -> bool:
        """
        Remove a keyword from a category.
        
        Args:
            category: The category to remove the keyword from
            keyword: The keyword to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if category in self.config.get("categories", {}):
                keywords = self.config["categories"][category]["keywords"]
                # Case-insensitive removal
                keywords_lower = [k.lower() for k in keywords]
                if keyword.lower() in keywords_lower:
                    # Find the actual keyword with original case
                    for k in keywords:
                        if k.lower() == keyword.lower():
                            keywords.remove(k)
                            break
                    self._save_config()
                    return True
            return False
        except Exception as e:
            print(f"Error removing keyword from category: {e}")
            return False
    
    def update_settings(self, default_category: str = None, auto_categorize: bool = None) -> bool:
        """
        Update configuration settings.
        
        Args:
            default_category: New default category
            auto_categorize: Enable/disable auto-categorization
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if "settings" not in self.config:
                self.config["settings"] = {}
            
            if default_category is not None:
                self.config["settings"]["default_category"] = default_category
            
            if auto_categorize is not None:
                self.config["settings"]["auto_categorize"] = auto_categorize
            
            self._save_config()
            return True
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False
    
    def rename_category(self, old_name: str, new_name: str) -> bool:
        """
        Rename a category.
        
        Args:
            old_name: Current name of the category
            new_name: New name for the category
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if old_name in self.config.get("categories", {}) and new_name not in self.config.get("categories", {}):
                self.config["categories"][new_name] = self.config["categories"][old_name]
                del self.config["categories"][old_name]
                
                # Update default category if it was the renamed one
                if self.config.get("settings", {}).get("default_category") == old_name:
                    self.config["settings"]["default_category"] = new_name
                
                self._save_config()
                return True
            return False
        except Exception as e:
            print(f"Error renaming category: {e}")
            return False


# Create a global instance for easy access
config_manager = ConfigManager()


# Convenience functions for backward compatibility
def get_categories() -> List[str]:
    """Get a list of all available categories."""
    return config_manager.get_categories()


def get_stores_for_category(category: str) -> List[str]:
    """Get all stores for a specific category."""
    return config_manager.get_stores_for_category(category)


def get_all_stores() -> List[str]:
    """Get all store names from all categories."""
    return config_manager.get_all_stores()


def auto_categorize_store(store_name: str) -> str:
    """Automatically categorize a store based on its name."""
    return config_manager.auto_categorize_store(store_name)


def add_store_to_category(category: str, store_name: str) -> bool:
    """Add a new store to a category."""
    return config_manager.add_store_to_category(category, store_name)


def remove_store_from_category(category: str, store_name: str) -> bool:
    """Remove a store from a category."""
    return config_manager.remove_store_from_category(category, store_name)


def add_category(category_name: str) -> bool:
    """Add a new category to the configuration."""
    return config_manager.add_category(category_name)


def remove_category(category_name: str) -> bool:
    """Remove a category from the configuration."""
    return config_manager.remove_category(category_name)


def get_keywords_for_category(category: str) -> List[str]:
    """Get all keywords for a specific category."""
    return config_manager.get_keywords_for_category(category)


def add_keyword_to_category(category: str, keyword: str) -> bool:
    """Add a keyword to a category."""
    return config_manager.add_keyword_to_category(category, keyword)


def remove_keyword_from_category(category: str, keyword: str) -> bool:
    """Remove a keyword from a category."""
    return config_manager.remove_keyword_from_category(category, keyword)


def update_settings(default_category: str = None, auto_categorize: bool = None) -> bool:
    """Update configuration settings."""
    return config_manager.update_settings(default_category, auto_categorize)


def rename_category(old_name: str, new_name: str) -> bool:
    """Rename a category."""
    return config_manager.rename_category(old_name, new_name) 