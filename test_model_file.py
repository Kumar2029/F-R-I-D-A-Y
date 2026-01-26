from Backend.Model import FirstLayerDMM
import json

def test_decomposition():
    queries = [
        "send a message to dad on whatsapp that i am coming home",
        "send message to brother",
        "search for python on chrome"
    ]
    
    results = {}
    print("Testing Decision Model...")
    
    for q in queries:
        print(f"Query: {q}")
        try:
            response = FirstLayerDMM(q)
            results[q] = response
        except Exception as e:
            results[q] = str(e)

    with open("model_test_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("Results written to model_test_results.json")

if __name__ == "__main__":
    test_decomposition()
