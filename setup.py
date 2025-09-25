#!/usr/bin/env python3

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def run_command(command, check=True):
    """Run a command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error output: {result.stderr}")
        sys.exit(1)
        
    return result

def check_requirements():
    """Check if required software is installed"""
    requirements = {
        'python3': 'python3 --version',
        'pip': 'pip --version',
        'google-chrome': 'google-chrome --version || chromium --version'
    }
    
    print("Checking requirements...")
    
    for name, command in requirements.items():
        try:
            result = run_command(command, check=False)
            if result.returncode == 0:
                print(f"✓ {name} is installed")
            else:
                print(f"✗ {name} is not installed or not in PATH")
                if name == 'google-chrome':
                    print("  Please install Google Chrome or Chromium browser")
                    return False
        except Exception as e:
            print(f"✗ Error checking {name}: {e}")
            return False
            
    return True

def setup_virtual_environment():
    """Setup Python virtual environment"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        run_command("python3 -m venv venv")
    else:
        print("Virtual environment already exists")
        
    # Activate virtual environment and install requirements
    if sys.platform == "win32":
        activate_script = "venv\\Scripts\\activate"
        pip_path = "venv\\Scripts\\pip"
    else:
        activate_script = "source venv/bin/activate"
        pip_path = "venv/bin/pip"
        
    print("Installing Python packages...")
    run_command(f"{pip_path} install --upgrade pip")
    run_command(f"{pip_path} install -r requirements.txt")
    
    return activate_script

def setup_environment_file():
    """Setup environment configuration file"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from example...")
        with open(env_example, 'r') as example:
            content = example.read()
            
        with open(env_file, 'w') as env:
            env.write(content)
            
        print("✓ .env file created")
        print("⚠️  Please edit .env file with your API keys and database credentials")
        return False
    elif env_file.exists():
        print("✓ .env file already exists")
        return True
    else:
        print("✗ No .env.example file found")
        return False

def verify_env_configuration():
    """Verify environment configuration"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("✗ .env file not found")
        return False
        
    required_vars = [
        'DATABASE_URL',
        'COMPANIES_HOUSE_API_KEY'
    ]
    
    missing_vars = []
    
    with open(env_file, 'r') as f:
        content = f.read()
        
    for var in required_vars:
        if f"{var}=" not in content or f"{var}=your_" in content:
            missing_vars.append(var)
            
    if missing_vars:
        print(f"✗ Missing or incomplete environment variables: {', '.join(missing_vars)}")
        print("Please edit .env file with proper values")
        return False
    else:
        print("✓ Environment variables configured")
        return True

async def test_database_connection():
    """Test database connection"""
    try:
        from database import DatabaseManager
        
        print("Testing database connection...")
        db = DatabaseManager()
        await db.connect()
        await db.close()
        print("✓ Database connection successful")
        return True
        
    except ImportError:
        print("✗ Cannot import database module")
        return False
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Please check your DATABASE_URL in .env file")
        return False

def create_run_script():
    """Create convenience run script"""
    if sys.platform == "win32":
        script_content = """@echo off
call venv\\Scripts\\activate
python main.py %*
"""
        script_name = "run.bat"
    else:
        script_content = """#!/bin/bash
source venv/bin/activate
python main.py "$@"
"""
        script_name = "run.sh"
        
    with open(script_name, 'w') as f:
        f.write(script_content)
        
    if sys.platform != "win32":
        run_command(f"chmod +x {script_name}")
        
    print(f"✓ Created {script_name} convenience script")

def main():
    """Main setup function"""
    print("Google Maps Business Scraper Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\nSetup failed: Missing requirements")
        sys.exit(1)
        
    # Setup virtual environment
    activate_script = setup_virtual_environment()
    
    # Setup environment file
    env_configured = setup_environment_file()
    
    if not env_configured:
        print("\nSetup completed with warnings:")
        print("1. Edit .env file with your API keys and database credentials")
        print("2. Run setup again to verify configuration")
        return
        
    # Verify environment configuration
    if not verify_env_configuration():
        print("\nSetup failed: Environment configuration incomplete")
        return
        
    # Test database connection
    try:
        loop = asyncio.get_event_loop()
        db_success = loop.run_until_complete(test_database_connection())
    except Exception as e:
        print(f"Database test failed: {e}")
        db_success = False
        
    # Create run script
    create_run_script()
    
    print("\n" + "=" * 40)
    
    if db_success:
        print("✓ Setup completed successfully!")
        print("\nYou can now use the scraper:")
        
        if sys.platform == "win32":
            print("  run.bat scrape restaurants")
            print("  run.bat verify")
            print("  run.bat report")
        else:
            print("  ./run.sh scrape restaurants")
            print("  ./run.sh verify")
            print("  ./run.sh report")
            
        print("\nOr activate the virtual environment manually:")
        print(f"  {activate_script}")
        print("  python main.py scrape restaurants")
        
    else:
        print("⚠️  Setup completed with database connection issues")
        print("Please check your DATABASE_URL and try again")

if __name__ == "__main__":
    main()
