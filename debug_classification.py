from Backend.Model import FirstLayerDMM

test_queries = [
    "hello",
    "open youtube",
]

with open("debug_class_log.txt", "w", encoding="utf-8") as f:
    f.write("Testing Classification Logic with 'command-r-08-2024'...\n")
    for q in test_queries:
        try:
            f.write(f"Query: '{q}'\n")
            print(f"Query: '{q}'")
            result = FirstLayerDMM(q)
            f.write(f"Result: {result}\n")
            f.write("-" * 20 + "\n")
        except Exception as e:
            f.write(f"Error processing '{q}': {e}\n")
