from app import get_db_connection
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

def test_direct_connection():
    print("测试1: 直接数据库连接")
    try:
        from connect import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASSWORD
        import psycopg2
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        print(f"✅ 连接成功！用户数: {count}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_app_connection():
    print("\n测试2: 通过app.py连接")
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            count = cur.fetchone()[0]
            print(f"✅ 连接成功！用户数: {count}")
            cur.close()
            conn.close()
        else:
            print("❌ 连接返回None")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

def test_password(username, password):
    print(f"\n测试3: 验证 {username}")
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
            result = cur.fetchone()
            if result:
                if bcrypt.check_password_hash(result[0], password):
                    print(f"✅ {username} 密码正确")
                else:
                    print(f"❌ {username} 密码错误")
            else:
                print(f"❌ {username} 不存在")
            cur.close()
            conn.close()
    except Exception as e:
        print(f"❌ 错误: {e}")

test_direct_connection()
test_app_connection()
test_password("test_volunteer", "Test123!")
test_password("test_leader", "Test123!")
test_password("test_admin", "Test123!")
