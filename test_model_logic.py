
import sys
import os

# Ensure root is in path
sys.path.append(os.getcwd())

from Backend.Model import FirstLayerDMM

print("Testing Model Logic...")

print("\n--- TEST 1: Command ---")
res1 = FirstLayerDMM("open notepad")
print(f"Result: {res1}")

print("\n--- TEST 2: Chat ---")
res2 = FirstLayerDMM("how are you today?")
print(f"Result: {res2}")

print("\n--- TEST 3: Time ---")
res3 = FirstLayerDMM("what is the time?")
print(f"Result: {res3}")
