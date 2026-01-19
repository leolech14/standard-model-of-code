from google import genai
import subprocess

def get_gcloud_project():
    try:
        res = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return None

def get_access_token():
    try:
        res = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return None

def main():
    project_id = get_gcloud_project()
    print(f"Project: {project_id}")
    
    from google.oauth2 import credentials as oauth2_credentials
    token = get_access_token()
    creds = oauth2_credentials.Credentials(token=token)

    regions = ["us-central1", "us-west1", "us-east4", "europe-west4", "europe-west9"]
    
    for loc in regions:
        print(f"\n--- Checking region: {loc} ---")
        try:
            client = genai.Client(vertexai=True, project=project_id, location=loc, credentials=creds)
            
            candidates = ["gemini-1.5-pro-002", "gemini-1.5-pro-001"]
            
            for model in candidates:
                print(f"Testing connectivity to: {model} ... ", end="")
                try:
                    client.models.generate_content(model=model, contents="Hello")
                    print("SUCCESS (Available)")
                    return  # Found one!
                except Exception as e:
                    if "404" in str(e):
                        print("Not Found")
                    else:
                        print(f"Error: {e}")

        except Exception as e:
            print(f"Client Init Error for {loc}: {e}")

if __name__ == "__main__":
    main()
