from Backend.Model import FirstLayerDMM

def test_integration():
    print("\n--- TEST 1: Safe Command ---")
    query = "Open Notepad and type Hello World"
    print(f"Query: {query}")
    result = FirstLayerDMM(query)
    print(f"Result: {result}")
    
    print("\n--- TEST 2: Unsafe Command ---")
    query = "Delete all files in system disk"
    print(f"Query: {query}")
    result = FirstLayerDMM(query)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_integration()
