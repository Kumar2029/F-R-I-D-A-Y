from Backend.Model import FirstLayerDMM

def test_decomposition():
    queries = [
        "send a message to dad on whatsapp that i am coming home",
        "send message to brother",
        "search for python on chrome"
    ]
    
    print("Testing Decision Model Decomposition...\n")
    
    for q in queries:
        print(f"Query: {q}")
        response = FirstLayerDMM(q)
        print(f"Response: {response}\n")

if __name__ == "__main__":
    test_decomposition()
