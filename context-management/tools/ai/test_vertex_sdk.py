import vertexai
from vertexai.generative_models import GenerativeModel

def test_vertex_sdk():
    project_id = "elements-archive-2026"
    location = "us-central1"
    
    print(f"Init vertexai for {project_id} in {location}")
    vertexai.init(project=project_id, location=location)

    models_to_test = ["gemini-1.5-pro-002", "gemini-1.5-pro-001", "gemini-1.5-pro"]

    for model_name in models_to_test:
        print(f"Testing {model_name}...")
        try:
            model = GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print(f"SUCCESS: {model_name} works!")
            return
        except Exception as e:
            print(f"FAIL {model_name}: {e}")

if __name__ == "__main__":
    test_vertex_sdk()
