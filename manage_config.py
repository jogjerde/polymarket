"""
Utility script for managing wallet configuration.
Use this to easily add/remove wallets and update settings.
"""

import json
import os

def show_current_wallets():
    """Display current tracked wallets."""
    from config import TRACKED_WALLETS, MIN_WALLETS_PER_MARKET, OUTPUT_CSV
    
    print("\n" + "="*70)
    print("CURRENT CONFIGURATION")
    print("="*70)
    print(f"\nTracked Wallets: {len(TRACKED_WALLETS)}")
    for i, wallet in enumerate(TRACKED_WALLETS, 1):
        print(f"  {i}. {wallet}")
    
    print(f"\nMinimum Wallets Per Market: {MIN_WALLETS_PER_MARKET}")
    print(f"Output CSV Filename: {OUTPUT_CSV}")
    print("="*70 + "\n")

def add_wallet():
    """Add a new wallet to config."""
    wallet = input("Enter wallet address (0x...): ").strip()
    
    if not wallet.startswith("0x") or len(wallet) != 42:
        print("❌ Invalid wallet format. Must be 0x followed by 40 hex characters.")
        return
    
    with open("config.py", "r") as f:
        content = f.read()
    
    # Find TRACKED_WALLETS list and add wallet
    if wallet not in content:
        new_wallet = f'    "{wallet}",\n'
        content = content.replace(
            '    "0xda0f4e3f79a50b8601b3cb9d421f48ce11bbf0e7",\n]',
            f'    "0xda0f4e3f79a50b8601b3cb9d421f48ce11bbf0e7",\n{new_wallet}]'
        )
        
        with open("config.py", "w") as f:
            f.write(content)
        
        print(f"✅ Added wallet: {wallet}")
    else:
        print("⚠️  Wallet already in configuration.")

def show_help():
    """Display help information."""
    print("""
Usage: python manage_config.py [command]

Commands:
  show       - Show current configuration
  add        - Add a new wallet
  help       - Show this help message

Examples:
  python manage_config.py show
  python manage_config.py add
    """)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "show":
            show_current_wallets()
        elif command == "add":
            add_wallet()
        elif command == "help":
            show_help()
        else:
            print(f"Unknown command: {command}")
            show_help()
    else:
        show_current_wallets()
