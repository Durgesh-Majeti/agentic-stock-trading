"""Setup script to create virtual environment and install dependencies."""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Warnings: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3:
        print("❌ Python 3 is required")
        return False
    
    # Python 3.12 is recommended for best compatibility
    if version.minor == 12:
        print("✅ Python 3.12 - Recommended version!")
        return True
    elif version.minor == 13:
        print("⚠️  Python 3.13 detected - may have compatibility issues")
        print("💡 Consider using Python 3.12 for better package support")
        print("   Run: py -3.12 -m venv venv")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Setup cancelled. Please use Python 3.12.")
            return False
    elif version.minor < 11:
        print("⚠️  Python 3.11+ recommended")
        print("💡 For best compatibility, use Python 3.12")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            return False
    
    return True


def main():
    """Main setup function."""
    print("\n" + "="*60)
    print("🚀 Agentic Stock Trading App - Setup Script")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Check if venv exists
    venv_path = project_root / "venv"
    if venv_path.exists():
        print(f"\n⚠️  Virtual environment already exists at {venv_path}")
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response == 'y':
            import shutil
            shutil.rmtree(venv_path)
            print("✅ Removed existing virtual environment")
        else:
            print("📝 Using existing virtual environment")
    
    # Create virtual environment
    if not venv_path.exists():
        if not run_command(
            f"{sys.executable} -m venv venv",
            "Creating virtual environment"
        ):
            print("❌ Failed to create virtual environment")
            sys.exit(1)
    
    # Determine activation script
    if sys.platform == "win32":
        pip_path = project_root / "venv" / "Scripts" / "pip.exe"
        python_path = project_root / "venv" / "Scripts" / "python.exe"
    else:
        pip_path = project_root / "venv" / "bin" / "pip"
        python_path = project_root / "venv" / "bin" / "python"
    
    # Upgrade pip
    if not run_command(
        f'"{python_path}" -m pip install --upgrade pip',
        "Upgrading pip"
    ):
        print("⚠️  Failed to upgrade pip, continuing...")
    
    # Use requirements.txt (optimized for Python 3.12)
    requirements_file = project_root / "requirements.txt"
    print("📋 Using requirements.txt (Python 3.12 recommended)")
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found at {requirements_file}")
        sys.exit(1)
    
    if not run_command(
        f'"{pip_path}" install -r "{requirements_file}"',
        f"Installing dependencies from {requirements_file.name}"
    ):
        print("❌ Failed to install dependencies")
        print("💡 Tip: If using Python 3.13, try Python 3.12 instead:")
        print("   py -3.12 -m venv venv")
        sys.exit(1)
    
    # Initialize database
    if not run_command(
        f'"{python_path}" scripts/init_db.py',
        "Initializing database"
    ):
        print("⚠️  Database initialization had issues, but continuing...")
    
    # Add sentiment analysis tables
    if not run_command(
        f'"{python_path}" scripts/migrate_add_sentiment_tables.py',
        "Adding sentiment analysis tables"
    ):
        print("⚠️  Sentiment tables migration had issues, but continuing...")
    
    print("\n" + "="*60)
    print("✅ Setup completed successfully!")
    print("="*60)
    print("\n📝 Next steps:")
    print("1. Activate virtual environment:")
    if sys.platform == "win32":
        print("   .\\venv\\Scripts\\Activate.ps1")
    else:
        print("   source venv/bin/activate")
    print("2. Create .env file with your credentials")
    print("3. Test Ollama connection:")
    print("   python scripts/test_ollama_connection.py")
    print("4. (Optional) Download NLTK data for VADER sentiment:")
    print("   python -c \"import nltk; nltk.download('vader_lexicon')\"")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
