import hashlib
import pandas as pd
import os


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(username, password, users_df):
    if username in users_df['username'].values:
        stored_password = users_df[users_df['username'] == username]['password'].values[0]
        return hash_password(password) == stored_password
    return False

def load_users():
    if os.path.exists('users.csv'):
        return pd.read_csv('users.csv')
    else:
        return pd.DataFrame(columns=['username', 'password'])

def save_user(username, password):
    users_df = load_users()
    if username not in users_df['username'].values:
        hashed_password = hash_password(password)
        new_user = pd.DataFrame([[username, hashed_password]], columns=['username', 'password'])
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        users_df.to_csv('users.csv', index=False)
        return True
    return False
