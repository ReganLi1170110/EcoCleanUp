"""
Password Hash Generator for EcoCleanUp Hub
Run this script locally to generate bcrypt hashes for database population
"""

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def generate_hash(password):
    """Generate bcrypt hash for a password"""
    hash = bcrypt.generate_password_hash(password).decode('utf-8')
    return hash

if __name__ == '__main__':
    # Generate hashes for common test passwords
    passwords = ['Password123!', 'Test123!', 'Admin123!', 'Leader123!']
    
    print("Password Hash Generator")
    print("=" * 50)
    
    for password in passwords:
        hash = generate_hash(password)
        print(f"Password: {password}")
        print(f"Hash: {hash}")
        print("-" * 50)
    
    print("\nTo generate a hash for a specific password:")
    print("1. Import this module")
    print("2. Call generate_hash('your_password')")