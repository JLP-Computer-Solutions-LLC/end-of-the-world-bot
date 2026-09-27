#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Guided local model (Ollama) setup for offline use.

This script helps users install Ollama and download a model before going offline.
It is designed to run while online, then the model works offline thereafter.
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

RECOMMENDED_MODELS = [
    {
        "name": "llama3.2:3b",
        "size": "2.0 GB",
        "description": "Fast, capable 3B parameter model (recommended for most hardware)",
    },
    {
        "name": "llama3.1:8b",
        "size": "4.7 GB",
        "description": "More capable 8B model, needs ~8 GB RAM",
    },
    {
        "name": "phi3:mini",
        "size": "2.3 GB",
        "description": "Microsoft's Phi-3 mini, good balance of size and quality",
    },
    {
        "name": "gemma2:2b",
        "size": "1.6 GB",
        "description": "Smallest option, works on very limited hardware",
    },
    {
        "name": "qwen2.5:3b",
        "size": "2.0 GB",
        "description": "Strong multilingual 3B model",
    },
]

def run_cmd(cmd, capture=False, check=True):
    """Run a command and return result."""
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=check)
            return ""
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return e.stdout.strip() if capture else ""

def check_ollama_installed():
    """Check if Ollama is installed and accessible."""
    if not shutil.which("ollama"):
        return False, "Ollama not found in PATH"
    try:
        version = run_cmd(["ollama", "version"], capture=True)
        return True, f"Ollama {version}"
    except Exception as e:
        return False, f"Ollama found but error: {e}"

def install_ollama():
    """Install Ollama using the official installer."""
    print("\nInstalling Ollama...")
    print("This downloads and runs the official Ollama installer.")
    print("You may be prompted for your password (sudo).")
    
    try:
        # Use the official install script
        result = subprocess.run(
            ["sh", "-c", "curl -fsSL https://ollama.com/install.sh | sh"],
            check=True
        )
        print("✓ Ollama installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Ollama installation failed")
        print("\nManual installation options:")
        print("  1. Visit https://ollama.com/download and download for your OS")
        print("  2. On Linux: curl -fsSL https://ollama.com/install.sh | sh")
        print("  3. On macOS: brew install ollama")
        print("  4. On Windows: Download from https://ollama.com/download/windows")
        return False

def start_ollama_service():
    """Start Ollama service if not running."""
    print("\nChecking Ollama service...")
    try:
        # Check if service is running
        response = urllib.request.urlopen("http://127.0.0.1:11434/api/version", timeout=2)
        if response.status == 200:
            print("✓ Ollama service is already running")
            return True
    except Exception:
        pass
    
    print("Starting Ollama service...")
    try:
        # Try to start in background
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        start_new_session=True)
        import time
        time.sleep(2)  # Give it time to start
        
        # Verify
        response = urllib.request.urlopen("http://127.0.0.1:11434/api/version", timeout=5)
        if response.status == 200:
            print("✓ Ollama service started")
            return True
    except Exception as e:
        print(f"✗ Could not start Ollama service: {e}")
        print("Try running 'ollama serve' in a separate terminal")
        return False
    return False

def list_local_models():
    """List locally installed models."""
    try:
        output = run_cmd(["ollama", "list"], capture=True)
        return output
    except Exception:
        return ""

def pull_model(model_name):
    """Pull a model from Ollama registry."""
    print(f"\nDownloading model: {model_name}")
    print("This may take several minutes depending on your connection...")
    try:
        # Run with output visible
        subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"✓ Model {model_name} downloaded successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to download {model_name}")
        return False

def test_model(model_name, question="Hello, are you working?"):
    """Test a model with a simple query."""
    print(f"\nTesting model {model_name}...")
    try:
        import model_query
        from types import SimpleNamespace
        
        # We need a mock retrieve function
        def mock_retrieve(_):
            return [{
                'id': 'S1',
                'source': 'test',
                'location': 'test',
                'date': 'test',
                'text': 'This is a test document about offline AI models.'
            }]
        
        model_query.retrieve = mock_retrieve
        model_query.MODEL = model_name
        model_query.HERE = Path(".")
        
        args = SimpleNamespace(
            question=question,
            search=None,
            retrieve_only=False,
            num_gpu=0,
            threads=4,
            ollama_url="http://127.0.0.1:11434/api/chat"
        )
        result = model_query.query(args)
        print(f"✓ Model responded: {result.get('answer', 'No answer')[:100]}")
        return True
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False

def recommend_model():
    """Help user choose a model based on available RAM."""
    print("\n" + "="*60)
    print("RECOMMENDED MODELS FOR OFFLINE USE")
    print("="*60)
    for i, m in enumerate(RECOMMENDED_MODELS, 1):
        print(f"\n  {i}. {m['name']} ({m['size']})")
        print(f"     {m['description']}")
    print("\n  6. Custom model name")
    print("  7. Skip model download (configure later)")
    
    while True:
        try:
            choice = input("\nSelect a model (1-7): ").strip()
            if choice in "12345":
                return RECOMMENDED_MODELS[int(choice)-1]["name"]
            elif choice == "6":
                custom = input("Enter model name (e.g., 'mistral:7b'): ").strip()
                if custom:
                    return custom
            elif choice == "7":
                return None
            else:
                print("Please enter 1-7")
        except (EOFError, KeyboardInterrupt):
            return None

def main():
    parser = argparse.ArgumentParser(
        description="Guided Ollama model setup for offline End of the World Bot use",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script helps you:
  1. Install Ollama if not present
  2. Start the Ollama service
  3. Choose and download a model for offline use
  4. Verify the model works with the bot

Run this ONLINE before going offline. The model will work offline afterward.
        """
    )
    parser.add_argument("--model", help="Skip interactive selection, use this model")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434/api/chat",
                        help="Ollama API URL")
    parser.add_argument("--skip-install", action="store_true",
                        help="Skip Ollama installation check")
    parser.add_argument("--skip-service", action="store_true",
                        help="Skip Ollama service start")
    args = parser.parse_args()
    
    print("="*60)
    print("END OF THE WORLD BOT - LOCAL MODEL SETUP")
    print("="*60)
    print("This guided setup prepares a local AI model for offline use.")
    print("Run this while you have internet access.\n")
    
    # Step 1: Check/install Ollama
    if not args.skip_install:
        installed, msg = check_ollama_installed()
        if installed:
            print(f"✓ {msg}")
        else:
            print(f"✗ {msg}")
            if not install_ollama():
                return 1
            # Re-check
            installed, msg = check_ollama_installed()
            if not installed:
                print("Ollama installation verification failed")
                return 1
            print(f"✓ {msg}")
    else:
        print("Skipping Ollama installation check (--skip-install)")
    
    # Step 2: Start Ollama service
    if not args.skip_service:
        if not start_ollama_service():
            print("Warning: Ollama service may not be running.")
            print("You can start it manually with: ollama serve")
    else:
        print("Skipping Ollama service start (--skip-service)")
    
    # Step 3: Check existing models
    print("\n" + "-"*60)
    existing = list_local_models()
    if existing:
        print("Currently installed models:")
        print(existing)
    else:
        print("No models installed yet.")
    
    # Step 4: Select model
    model_name = args.model
    if not model_name:
        model_name = recommend_model()
    
    if not model_name:
        print("\nSkipping model download. You can run this script again later.")
        print("Or manually: ollama pull <model-name>")
        return 0
    
    # Check if already installed
    if model_name in existing:
        print(f"\nModel {model_name} is already installed.")
        if input("Re-download? (y/N): ").strip().lower() != 'y':
            print("Using existing model.")
        else:
            if not pull_model(model_name):
                return 1
    else:
        if not pull_model(model_name):
            return 1
    
    # Step 5: Test model with bot
    print("\n" + "-"*60)
    print("Testing model with End of the World Bot...")
    
    # Add current directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent))
    
    if test_model(model_name):
        print("\n" + "="*60)
        print("SETUP COMPLETE!")
        print("="*60)
        print(f"\nModel '{model_name}' is ready for offline use.")
        print("\nTo use with the bot:")
        print(f"  sh launch.sh ask 'Your question' --model {model_name}")
        print("\nOr with the chat adapter:")
        print(f"  python3 http_adapter.py --root library --model {model_name}")
        print("\nThe model will work offline after this setup.")
        return 0
    else:
        print("\nModel downloaded but test failed.")
        print("You can still try using it with the bot.")
        return 1

if __name__ == "__main__":
    from pathlib import Path
    sys.exit(main())