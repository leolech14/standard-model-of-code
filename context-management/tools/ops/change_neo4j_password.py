from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "neo4j")
NEW_PASSWORD = "password"

def change_password():
    print(f"Connecting to {URI}...")
    try:
        # We use the driver to connect, but we might fail on verify_connectivity if credentials expired
        # However, we need to run the ALTER command.
        # The driver usually handles password change requirement by raising an error or allowing a specific session?
        # Actually, if credentials are expired, we can still connect to system db to change them?
        # Let's try connecting and running the query.

        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            # Note: We might need to verify connectivity, but it might fail.
            # Let's try to run the query directly.
            # We must run this against the 'system' database usually.

            with driver.session(database="system") as session:
                print("Attempting to change password...")
                session.run(f"ALTER CURRENT USER SET PASSWORD FROM 'neo4j' TO '{NEW_PASSWORD}'")
                print(f"Password changed to '{NEW_PASSWORD}'")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    change_password()
