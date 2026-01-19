from google.cloud import aiplatform
import sys

def list_models(project_id, location):
    aiplatform.init(project=project_id, location=location)
    try:
        # This is a bit of a hack as SDK doesn't always expose publisher models easily
        # We will try to list via the low-level API if possible, or just print success if init works
        print(f"Initialized aiplatform for {location}")
        
        from google.cloud import aiplatform_v1
        client = aiplatform_v1.ModelGardenServiceClient(
            client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        )
        parent = f"projects/{project_id}/locations/{location}/publishers/google"
        
        print(f"Querying Model Garden in {location}...")
        # Note: listing models can be verbose, we just want to see if we can access the endpoint
        # and maybe find gemini
        request = aiplatform_v1.ListPublisherModelsRequest(parent=parent)
        response = client.list_publisher_models(request=request)
        
        found = []
        for model in response.publisher_models:
            if "gemini" in model.name:
                found.append(model.name)
        
        if found:
            print("Found Gemini Models:")
            for m in found:
                print(f" - {m}")
        else:
            print("No Gemini models found in list (might be filtered or permission issue)")

    except Exception as e:
        print(f"Error listing models in {location}: {e}")

if __name__ == "__main__":
    list_models("elements-archive-2026", "us-central1")
