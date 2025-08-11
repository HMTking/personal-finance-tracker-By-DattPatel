"""
Test script to create a user and verify authentication system
"""
from models.user import User
from models.transaction import Transaction

def test_user_creation():
    try:
        # Try to create a test user (might already exist)
        try:
            user_id = User.create_user("testuser", "test@example.com", "password123")
            print(f"✅ User created successfully with ID: {user_id}")
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                print("ℹ️  Test user already exists, continuing with login test...")
            else:
                raise e
        
        # Verify user login
        user = User.verify_user("testuser", "password123")
        if user:
            print(f"✅ User login verified: {user['username']} (ID: {user['id']})")
            user_id = user['id']
        else:
            print("❌ User login failed")
            return
            
        # Test transaction creation for this user
        transaction_id = Transaction.create(
            user_id=user_id,
            amount=1000.0,
            category="Salary",
            type_="income",
            date="2025-08-12",
            description="Test salary"
        )
        print(f"✅ Transaction created successfully with ID: {transaction_id}")
        
        # Test getting user transactions
        transactions = Transaction.get_all(user_id)
        print(f"✅ Found {len(transactions)} transactions for user")
        
        # Test summary
        summary = Transaction.summary(user_id)
        print(f"✅ Summary: Income=₹{summary['total_income']}, Expenses=₹{summary['total_expenses']}")
        
        print("\n🎉 All tests passed! The system is working correctly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_creation()
