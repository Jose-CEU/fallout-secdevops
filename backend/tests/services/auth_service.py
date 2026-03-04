from werkzeug.security import generate_password_hash, check_password_hash

def register_user(conn, username, password):
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))"
    )

    hashed_password = generate_password_hash(password)

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, hashed_password)
    )

    conn.commit()
    cursor.close()

    return {"message": "User created"}, 201


def login_user(conn, username, password):
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username = %s",
        (username,)
    )

    result = cursor.fetchone()
    cursor.close()

    if not result:
        return {"error": "User not found"}, 404

    stored_password = result[0]

    if check_password_hash(stored_password, password):
        return {"message": "Login successful"}, 200
    else:
        return {"error": "Invalid credentials"}, 401